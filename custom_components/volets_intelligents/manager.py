"""Gestionnaire : relie le moteur de décision à Home Assistant."""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import Callable
from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.components.cover import CoverEntityFeature
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Context, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.sun import get_astral_event_date
from homeassistant.util import dt as dt_util

from .const import (
    ACTION_CLOSE,
    ACTION_OPEN,
    CLOSE_BUTTON,
    CLOSE_POSITION,
    CONFIG_VERSION,
    END_ENTITY,
    END_SUNSET,
    EXPOSURE_ENTITY,
    MODE_AUTO,
    MODES,
    MOTION_GRACE_SECONDS,
    SETTLE_SECONDS,
    SIGNAL_CONFIG_CHANGED,
    SIGNAL_STATUS_UPDATED,
    STORAGE_KEY_CONFIG,
    STORAGE_KEY_RUNTIME,
    STORAGE_VERSION,
)
from .engine import CoverInputs, CoverRuntime, Decision, Env, decide
from .schema import ConfigError, default_config, normalize_config
from .solar import exposure_windows, facade_azimuth, is_exposed, sun_position

_LOGGER = logging.getLogger(__name__)

_TIME_STATE_RE = re.compile(r"(\d{1,2}):(\d{2})(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?")
_MOVING_STATES = ("opening", "closing")

_INVALID = (STATE_UNAVAILABLE, STATE_UNKNOWN, "", None)


def _parse_hhmm(value: str) -> time:
    hours, minutes = value.split(":")[:2]
    return time(int(hours), int(minutes))


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _parse_dt(value: str | None) -> datetime | None:
    return dt_util.parse_datetime(value) if value else None


class VoletsManager:
    """Charge la configuration, évalue périodiquement et pilote les volets."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._config_store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY_CONFIG)
        self._runtime_store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY_RUNTIME)
        self.config: dict[str, Any] = normalize_config(default_config())
        self._covers_by_id: dict[str, dict[str, Any]] = {}
        self._subscription_key: tuple | None = None
        self._saved_runtime: dict[str, Any] | None = None
        self.mode: str = MODE_AUTO
        self.scenario: str = "summer"
        self.runtime: dict[str, CoverRuntime] = {}
        self.status: dict[str, Any] = {}
        self._unsubs: list[Callable[[], None]] = []
        self._debouncer: Debouncer | None = None
        self._lock = asyncio.Lock()
        self._wind_exceeded = False
        self._grace_until: datetime | None = None
        self._last_in_window = False
        self._window_end: datetime | None = None
        self._grace_unsub: Callable[[], None] | None = None
        self._windows_key: tuple | None = None
        self._windows_cache: dict[str, list[dict[str, str]]] = {}
        self._stopped = False

    # --- cycle de vie ---------------------------------------------------------

    async def async_load(self) -> None:
        """Charge la configuration et l'état mémorisé."""
        stored = await self._config_store.async_load()
        if stored:
            try:
                self._apply_config(normalize_config(stored))
            except ConfigError as err:
                _LOGGER.error(
                    "Configuration enregistrée invalide, valeurs par défaut utilisées : %s", err
                )
        runtime = await self._runtime_store.async_load() or {}
        if runtime.get("mode") in MODES:
            self.mode = runtime["mode"]
        if runtime.get("scenario") in self.config["scenarios"]:
            self.scenario = runtime["scenario"]
        for entity_id, data in (runtime.get("covers") or {}).items():
            self.runtime[entity_id] = CoverRuntime(
                shaded_by_us=bool(data.get("shaded_by_us")),
                paused_until=_parse_dt(data.get("paused_until")),
                last_action=data.get("last_action"),
                last_action_at=_parse_dt(data.get("last_action_at")),
            )

    async def async_start(self) -> None:
        """Démarre l'écoute et la première évaluation."""
        self._stopped = False
        grace = self.config["settings"]["startup_grace_seconds"]
        self._grace_until = dt_util.now() + timedelta(seconds=grace)
        self._debouncer = Debouncer(
            self.hass,
            _LOGGER,
            cooldown=5.0,
            immediate=False,
            function=self.async_evaluate,
            background=True,
        )
        self._subscribe()
        if grace:
            self._grace_unsub = async_call_later(self.hass, grace + 1, self._async_grace_over)
        await self.async_evaluate()

    async def async_stop(self) -> None:
        self._stopped = True
        self._unsubscribe()
        if self._grace_unsub:
            self._grace_unsub()
            self._grace_unsub = None
        if self._debouncer:
            self._debouncer.async_shutdown()
            self._debouncer = None
        await self._runtime_store.async_save(self._runtime_data())

    async def _async_grace_over(self, _now: datetime) -> None:
        await self.async_evaluate()

    def _subscribe(self) -> None:
        entities = sorted(self._tracked_entities())
        interval = self.config["settings"]["evaluation_interval_minutes"]
        key = (tuple(entities), interval)
        if key == self._subscription_key and self._unsubs:
            return  # rien n'a changé : inutile de se réabonner (ex. simple bascule d'un volet)
        self._subscription_key = key
        self._unsubscribe()
        if entities:
            self._unsubs.append(
                async_track_state_change_event(self.hass, entities, self._on_state_event)
            )
        self._unsubs.append(
            async_track_time_interval(self.hass, self._on_interval, timedelta(minutes=interval))
        )

    def _unsubscribe(self) -> None:
        while self._unsubs:
            self._unsubs.pop()()

    def _tracked_entities(self) -> set[str]:
        s = self.config["settings"]
        entities: set[str] = set()
        for key in (
            "outdoor_temp_entity",
            "feels_like_entity",
            "weather_entity",
            "wind_entity",
        ):
            if s[key]:
                entities.add(s[key])
        if s["window"]["end_mode"] == END_ENTITY and s["window"]["end_entity"]:
            entities.add(s["window"]["end_entity"])
        for facade in self.config["facades"]:
            if facade["exposure"]["entity"]:
                entities.add(facade["exposure"]["entity"])
        for cover in self.config["covers"]:
            entities.add(cover["entity_id"])
            if cover["room_temp_entity"]:
                entities.add(cover["room_temp_entity"])
            entities.update(cover["window_entities"])
        return entities

    # --- événements -----------------------------------------------------------

    async def _on_interval(self, _now: datetime) -> None:
        await self.async_evaluate()

    @callback
    def _on_state_event(self, event: Event[EventStateChangedData]) -> None:
        entity_id = event.data["entity_id"]
        if entity_id in self._covers_by_id:
            self._detect_manual_override(entity_id, event)
        if self._debouncer:
            self._debouncer.async_schedule_call()

    def runtime_keys(self) -> set[str]:
        return set(self._covers_by_id)

    def _cover_config(self, entity_id: str) -> dict[str, Any] | None:
        return self._covers_by_id.get(entity_id)

    def _apply_config(self, config: dict[str, Any]) -> None:
        """Adopte une configuration validée et reconstruit l'index des volets."""
        self.config = config
        self._covers_by_id = {c["entity_id"]: c for c in config["covers"]}

    def _rt(self, entity_id: str) -> CoverRuntime:
        return self.runtime.setdefault(entity_id, CoverRuntime())

    @callback
    def _detect_manual_override(self, entity_id: str, event: Event[EventStateChangedData]) -> None:
        """Un mouvement qui ne vient pas de nous met le volet en pause."""
        cover = self._cover_config(entity_id)
        old = event.data.get("old_state")
        new = event.data.get("new_state")
        if cover is None or not cover["enabled"] or old is None or new is None:
            return
        if old.state in _INVALID or new.state in _INVALID:
            return
        if (old.state, old.attributes.get("current_position")) == (
            new.state,
            new.attributes.get("current_position"),
        ):
            return
        now = dt_util.now()
        rt = self._rt(entity_id)
        if rt.last_command_at is not None:
            elapsed = (now - rt.last_command_at).total_seconds()
            if elapsed < SETTLE_SECONDS:
                return
            # Volet lent : la suite d'un mouvement que nous avons commandé n'est pas manuelle.
            if old.state in _MOVING_STATES and elapsed < MOTION_GRACE_SECONDS:
                return
        if self.mode != MODE_AUTO:
            return
        if not self._last_in_window and not rt.shaded_by_us:
            return
        self._start_override(entity_id, rt, now)

    def _start_override(self, entity_id: str, rt: CoverRuntime, now: datetime) -> None:
        settings = self.config["settings"]
        rt.shaded_by_us = False
        if settings["override_until_window_end"] and self._window_end and self._window_end > now:
            until = self._window_end
        else:
            until = now + timedelta(minutes=settings["override_pause_minutes"])
        rt.paused_until = until if until > now else None
        _LOGGER.debug(
            "Action manuelle détectée sur %s, pause jusqu'à %s", entity_id, rt.paused_until
        )
        self._save_runtime()

    # --- lecture des capteurs -------------------------------------------------

    def _float_state(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in _INVALID:
            return None
        try:
            return float(state.state)
        except ValueError:
            return None

    def _outdoor(self) -> tuple[float | None, float | None]:
        """(mesure brute, température effective). Sans mesure, aucune donnée : pas d'action."""
        s = self.config["settings"]
        measured = self._float_state(s["outdoor_temp_entity"])
        if measured is None:
            return None, None
        feels = self._float_state(s["feels_like_entity"])
        if feels is not None and s["use_max_feels_like"]:
            return measured, max(measured, feels)
        return measured, measured

    def _update_wind(self) -> tuple[float | None, bool]:
        s = self.config["settings"]
        wind = self._float_state(s["wind_entity"])
        if wind is not None:
            if not self._wind_exceeded and wind >= s["wind_threshold"]:
                self._wind_exceeded = True
            elif self._wind_exceeded and wind < s["wind_threshold"] * s["wind_release_ratio"]:
                self._wind_exceeded = False
        return wind, self._wind_exceeded

    def _is_sunny(self) -> bool:
        s = self.config["settings"]
        if not s["weather_entity"] or not s["sunny_conditions"]:
            return True
        state = self.hass.states.get(s["weather_entity"])
        if state is None or state.state in _INVALID:
            return True  # donnée absente : on ne neutralise pas le soleil
        return state.state in s["sunny_conditions"]

    def facade_azimuth(self, facade: dict[str, Any]) -> float:
        """Azimut vers lequel regarde la façade, orientation de la maison comprise."""
        return facade_azimuth(
            facade["orientation"],
            facade["custom_azimuth"],
            self.config["settings"]["house_orientation"],
        )

    def _sun_now(self, now: datetime) -> tuple[float, float]:
        config = self.hass.config
        return sun_position(config.latitude, config.longitude, config.elevation, now)

    def _facade_exposed(self, facade: dict[str, Any], sun: tuple[float, float]) -> bool | None:
        """True/False, ou None si le capteur d'exposition est indisponible."""
        exposure = facade["exposure"]
        if exposure["mode"] == EXPOSURE_ENTITY:
            if not exposure["entity"]:
                return False
            state = self.hass.states.get(exposure["entity"])
            if state is None or state.state in _INVALID:
                return None
            return state.state == STATE_ON
        return is_exposed(
            sun[0],
            sun[1],
            self.facade_azimuth(facade),
            exposure["half_angle"],
            exposure["elevation_min"],
        )

    def _geometry_signature(self) -> tuple:
        config = self.hass.config
        return (
            config.latitude,
            config.longitude,
            config.elevation,
            self.config["settings"]["house_orientation"],
            tuple(
                (
                    f["id"],
                    f["orientation"],
                    f["custom_azimuth"],
                    f["exposure"]["half_angle"],
                    f["exposure"]["elevation_min"],
                )
                for f in self.config["facades"]
            ),
        )

    def _compute_windows(self, day, tz) -> dict[str, list[dict[str, str]]]:
        config = self.hass.config
        result: dict[str, list[dict[str, str]]] = {}
        for facade in self.config["facades"]:
            windows = exposure_windows(
                config.latitude,
                config.longitude,
                config.elevation,
                day,
                tz,
                self.facade_azimuth(facade),
                facade["exposure"]["half_angle"],
                facade["exposure"]["elevation_min"],
            )
            result[facade["id"]] = [
                {"start": start.strftime("%H:%M"), "end": end.strftime("%H:%M")}
                for start, end in windows
            ]
        return result

    async def _facade_windows(self, now: datetime) -> dict[str, list[dict[str, str]]]:
        """Plages d'ensoleillement théoriques du jour (calculées une fois par jour)."""
        key = (now.date(), self._geometry_signature())
        if self._windows_key != key:
            self._windows_cache = await self.hass.async_add_executor_job(
                self._compute_windows, now.date(), now.tzinfo
            )
            self._windows_key = key
        return self._windows_cache

    def _time_from_entity(self, entity_id: str | None) -> time | None:
        """Heure lue dans un état « HH:MM », « HH:MM:SS[.ffffff][±HH:MM] » ou datetime ISO."""
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in _INVALID:
            return None
        raw = state.state.strip()
        match = _TIME_STATE_RE.fullmatch(raw)
        if match:
            hours, minutes = int(match.group(1)), int(match.group(2))
            return time(hours, minutes) if hours < 24 and minutes < 60 else None
        parsed = dt_util.parse_datetime(raw)
        return dt_util.as_local(parsed).time() if parsed else None

    def _compute_window(self, now: datetime) -> tuple[bool, datetime, datetime | None]:
        """(dans la plage ?, début, fin) ; gère une plage qui passe minuit (ex. 20:00 → 02:00)."""
        w = self.config["settings"]["window"]
        start = _parse_hhmm(w["start"])
        end: time | None = None
        if w["end_mode"] == END_ENTITY:
            end = self._time_from_entity(w["end_entity"])
        elif w["end_mode"] == END_SUNSET:
            sunset = get_astral_event_date(self.hass, "sunset", now.date())
            if sunset is not None:
                shifted = dt_util.as_local(sunset) + timedelta(minutes=w["sunset_offset_minutes"])
                end = shifted.time()
        if end is None:
            end = _parse_hhmm(w["end_time"])  # repli si la source est indisponible

        def at(moment: time, offset_days: int = 0) -> datetime:
            return now.replace(
                hour=moment.hour, minute=moment.minute, second=0, microsecond=0
            ) + timedelta(days=offset_days)

        if end == start:
            return False, at(start), at(end)
        if end > start:
            start_dt, end_dt = at(start), at(end)
        elif now.time() < end:  # après minuit, dans la plage commencée la veille
            start_dt, end_dt = at(start, -1), at(end)
        else:  # avant minuit : la plage se termine demain
            start_dt, end_dt = at(start), at(end, 1)
        return start_dt <= now < end_dt, start_dt, end_dt

    def effective_scenario(self, now: datetime) -> str:
        auto = self.config["settings"]["auto_scenario"]
        if auto["enabled"]:
            return "summer" if now.month in auto["summer_months"] else "winter"
        return self.scenario if self.scenario in self.config["scenarios"] else "summer"

    # --- évaluation -----------------------------------------------------------

    async def async_evaluate(self) -> None:
        """Évalue tous les volets et exécute les actions décidées."""
        if self._stopped:
            return
        async with self._lock:
            await self._evaluate()

    async def _evaluate(self) -> None:
        now = dt_util.now()
        settings = self.config["settings"]
        scenario_key = self.effective_scenario(now)
        scenario = self.config["scenarios"][scenario_key]
        in_window, start_dt, end_dt = self._compute_window(now)
        self._last_in_window = in_window
        self._window_end = end_dt
        outdoor_raw, outdoor = self._outdoor()
        wind, wind_exceeded = self._update_wind()
        sunny = self._is_sunny()
        grace = self._grace_until is not None and now < self._grace_until

        env = Env(
            now=now,
            mode=self.mode,
            scenario=scenario,
            in_window=in_window,
            grace_active=grace,
            outdoor=outdoor,
            wind_exceeded=wind_exceeded,
            tolerance=settings["position_tolerance"],
            min_move=timedelta(minutes=settings["min_move_interval_minutes"]),
        )

        sun = self._sun_now(now)
        windows = await self._facade_windows(now)
        facades = {f["id"]: f for f in self.config["facades"]}
        facade_status: dict[str, Any] = {}
        raw_exposure: dict[str, bool | None] = {}
        for facade in self.config["facades"]:
            raw_exposure[facade["id"]] = self._facade_exposed(facade, sun)
            facade_status[facade["id"]] = {
                "name": facade["name"],
                "orientation": facade["orientation"],
                "exposed": None
                if raw_exposure[facade["id"]] is None
                else raw_exposure[facade["id"]] and sunny,
                "source": facade["exposure"]["mode"],
                "azimuth": round(self.facade_azimuth(facade), 1),
                "windows": windows.get(facade["id"], []),
            }

        covers_status: list[dict[str, Any]] = []
        for cover in self.config["covers"]:
            entity_id = cover["entity_id"]
            rt = self._rt(entity_id)
            facade = facades.get(cover["facade"])
            raw_exposed = raw_exposure[facade["id"]] if facade else False
            inp = self._cover_inputs(cover, facade, raw_exposed, sunny)
            decision = decide(cover, inp, rt, env)
            if decision.action and not self._already_sent(rt, decision.action, now):
                await self._execute(cover, decision, rt, now)
            covers_status.append(self._cover_status(cover, inp, rt, decision))

        self.status = {
            "mode": self.mode,
            "scenario": scenario_key,
            "scenario_label": scenario["label"],
            "scenario_kind": scenario["kind"],
            "scenarios": {k: v["label"] for k, v in self.config["scenarios"].items()},
            "in_window": in_window,
            "window_start": start_dt.strftime("%H:%M"),
            "window_end": end_dt.strftime("%H:%M") if end_dt else None,
            "grace_active": grace,
            "outdoor_temp": outdoor_raw,
            "outdoor_effective": outdoor,
            "wind": wind,
            "wind_exceeded": wind_exceeded,
            "sunny": sunny,
            "sun": {"azimuth": round(sun[0], 1), "elevation": round(sun[1], 1)},
            "house_orientation": settings["house_orientation"],
            "facades": facade_status,
            "covers": covers_status,
            "version": CONFIG_VERSION,
        }
        self._save_runtime()
        async_dispatcher_send(self.hass, SIGNAL_STATUS_UPDATED)

    def _cover_inputs(
        self,
        cover: dict[str, Any],
        facade: dict[str, Any] | None,
        raw_exposed: bool | None,
        sunny: bool,
    ) -> CoverInputs:
        state = self.hass.states.get(cover["entity_id"])
        available = state is not None and state.state not in _INVALID
        position = None
        if state is not None:
            value = state.attributes.get("current_position")
            if value is not None:
                try:
                    position = int(value)
                except (TypeError, ValueError):
                    position = None
        # Un capteur de fenêtre indisponible compte comme « ouvert » : on ne risque pas
        # d'enfermer quelqu'un dehors.
        windows_open = any(
            (s := self.hass.states.get(e)) is None or s.state in _INVALID or s.state == STATE_ON
            for e in cover["window_entities"]
        )
        return CoverInputs(
            available=available,
            state=state.state if state else None,
            position=position,
            room_temp=self._float_state(cover["room_temp_entity"]),
            window_open=windows_open,
            exposed=None if raw_exposed is None else raw_exposed and sunny,
            facade_name=facade["name"] if facade else cover["facade"],
            exposure_note="ciel couvert" if raw_exposed and not sunny else "",
        )

    def _cover_status(
        self,
        cover: dict[str, Any],
        inp: CoverInputs,
        rt: CoverRuntime,
        decision: Decision,
    ) -> dict[str, Any]:
        now = dt_util.now()
        paused = rt.paused_until if rt.paused_until and rt.paused_until > now else None
        return {
            "entity_id": cover["entity_id"],
            "name": cover["name"],
            "facade": cover["facade"],
            "enabled": cover["enabled"],
            "status": decision.status,
            "reason": decision.reason,
            "position": inp.position,
            "state": inp.state,
            "room_temp": inp.room_temp,
            "exposed": inp.exposed,
            "paused_until": _iso(paused),
            "shaded_by_us": rt.shaded_by_us,
            "last_action": rt.last_action,
            "last_action_at": _iso(rt.last_action_at),
        }

    # --- exécution ------------------------------------------------------------

    async def _execute(
        self, cover: dict[str, Any], decision: Decision, rt: CoverRuntime, now: datetime
    ) -> None:
        context = Context()
        rt.last_command_at = now  # avant l'appel : évite une fausse détection manuelle
        try:
            if decision.plain:
                await self._send_plain(cover, decision.action, context)
            elif decision.action == ACTION_CLOSE:
                await self._send_close(cover, context)
            elif decision.action == ACTION_OPEN:
                await self._send_open(cover, context)
        except HomeAssistantError as err:
            _LOGGER.warning(
                "Commande %s refusée pour %s : %s", decision.action, cover["entity_id"], err
            )
            return
        rt.shaded_by_us = decision.action == ACTION_CLOSE and not decision.plain
        rt.last_action = decision.action
        rt.last_action_at = now
        _LOGGER.info("%s : %s (%s)", cover["entity_id"], decision.action, decision.reason)

    @staticmethod
    def _already_sent(rt: CoverRuntime, action: str, now: datetime) -> bool:
        """Même ordre déjà envoyé à l'instant : le volet est probablement en mouvement."""
        return (
            rt.last_action == action
            and rt.last_command_at is not None
            and (now - rt.last_command_at).total_seconds() < SETTLE_SECONDS
        )

    async def _send_plain(
        self, cover: dict[str, Any], action: str | None, context: Context
    ) -> None:
        """Ouverture ou fermeture complète (sécurité vent), sans position intermédiaire."""
        service = "close_cover" if action == ACTION_CLOSE else "open_cover"
        await self.hass.services.async_call(
            "cover",
            service,
            {"entity_id": cover["entity_id"]},
            blocking=False,
            context=context,
        )

    def _supports_position(self, entity_id: str) -> bool:
        state = self.hass.states.get(entity_id)
        features = state.attributes.get("supported_features", 0) if state else 0
        return bool(features & CoverEntityFeature.SET_POSITION)

    async def _send_close(self, cover: dict[str, Any], context: Context) -> None:
        entity_id = cover["entity_id"]
        method = cover["close_method"]
        if method == CLOSE_BUTTON and cover["button_entity"]:
            domain = cover["button_entity"].split(".")[0]
            service = "press"
            await self.hass.services.async_call(
                domain,
                service,
                {"entity_id": cover["button_entity"]},
                blocking=False,
                context=context,
            )
        elif method == CLOSE_POSITION and self._supports_position(entity_id):
            await self.hass.services.async_call(
                "cover",
                "set_cover_position",
                {"entity_id": entity_id, "position": cover["close_position"]},
                blocking=False,
                context=context,
            )
        else:
            await self.hass.services.async_call(
                "cover",
                "close_cover",
                {"entity_id": entity_id},
                blocking=False,
                context=context,
            )

    async def _send_open(self, cover: dict[str, Any], context: Context) -> None:
        entity_id = cover["entity_id"]
        if cover["open_position"] < 100 and self._supports_position(entity_id):
            await self.hass.services.async_call(
                "cover",
                "set_cover_position",
                {"entity_id": entity_id, "position": cover["open_position"]},
                blocking=False,
                context=context,
            )
        else:
            await self.hass.services.async_call(
                "cover",
                "open_cover",
                {"entity_id": entity_id},
                blocking=False,
                context=context,
            )

    # --- commandes publiques --------------------------------------------------

    async def async_set_config(self, raw: Any) -> dict[str, Any]:
        """Valide, enregistre et applique une nouvelle configuration."""
        config = normalize_config(raw)  # lève ConfigError
        self._apply_config(config)
        kept = {c["entity_id"] for c in config["covers"]}
        self.runtime = {k: v for k, v in self.runtime.items() if k in kept}
        if self.scenario not in config["scenarios"]:
            self.scenario = "summer"
        await self._config_store.async_save(config)
        self._subscribe()
        async_dispatcher_send(self.hass, SIGNAL_CONFIG_CHANGED)
        await self.async_evaluate()
        return config

    async def async_set_cover_enabled(self, entity_id: str, enabled: bool) -> None:
        config = {**self.config, "covers": [dict(c) for c in self.config["covers"]]}
        for cover in config["covers"]:
            if cover["entity_id"] == entity_id:
                cover["enabled"] = enabled
        await self.async_set_config(config)

    async def async_set_mode(self, mode: str) -> None:
        if mode not in MODES:
            raise HomeAssistantError(f"Mode inconnu : {mode}")
        self.mode = mode
        self._save_runtime()
        await self.async_evaluate()

    async def async_set_scenario(self, scenario: str) -> None:
        if scenario not in self.config["scenarios"]:
            raise HomeAssistantError(f"Scénario inconnu : {scenario}")
        if self.config["settings"]["auto_scenario"]["enabled"]:
            raise HomeAssistantError(
                "Le scénario automatique est activé : désactivez-le dans les réglages "
                "pour choisir un scénario à la main"
            )
        self.scenario = scenario
        self._save_runtime()
        await self.async_evaluate()

    def _targets(self, entity_ids: list[str] | None) -> list[str]:
        known = self.runtime_keys()
        if not entity_ids:
            return sorted(known)
        unknown = [e for e in entity_ids if e not in known]
        if unknown:
            raise HomeAssistantError(f"Volet(s) non géré(s) : {', '.join(unknown)}")
        return list(entity_ids)

    async def async_pause(self, entity_ids: list[str] | None, minutes: int | None) -> None:
        now = dt_util.now()
        if minutes is None:
            minutes = self.config["settings"]["override_pause_minutes"]
        minutes = max(int(minutes), 1)
        for entity_id in self._targets(entity_ids):
            rt = self._rt(entity_id)
            rt.paused_until = now + timedelta(minutes=minutes)
            rt.shaded_by_us = False
        self._save_runtime()
        await self.async_evaluate()

    async def async_resume(self, entity_ids: list[str] | None) -> None:
        for entity_id in self._targets(entity_ids):
            self._rt(entity_id).paused_until = None
        self._save_runtime()
        await self.async_evaluate()

    # --- persistance ----------------------------------------------------------

    def _runtime_data(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "scenario": self.scenario,
            "covers": {
                entity_id: {
                    "shaded_by_us": rt.shaded_by_us,
                    "paused_until": _iso(rt.paused_until),
                    "last_action": rt.last_action,
                    "last_action_at": _iso(rt.last_action_at),
                }
                for entity_id, rt in self.runtime.items()
            },
        }

    def _save_runtime(self) -> None:
        data = self._runtime_data()
        if data == self._saved_runtime:
            return  # rien à écrire sur le disque
        self._saved_runtime = data
        self._runtime_store.async_delay_save(lambda: data, 5)

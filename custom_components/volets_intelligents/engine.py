"""Moteur de décision : pur, sans Home Assistant, entièrement testable.

Pour chaque volet, `decide()` reçoit la configuration, l'état observé et le
contexte global, et retourne un `Decision` (statut, phrase explicative et
action éventuelle). Le moteur ne fait aucun appel de service et ne modifie
aucun état : c'est le gestionnaire qui exécute les actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .const import (
    ACTION_CLOSE,
    ACTION_OPEN,
    CLOSE_FULL,
    KIND_GAIN,
    KIND_HEAT,
    KIND_HOLD,
    KIND_OFF,
    MODE_AUTO,
    MODE_MANUAL,
    ST_COOLDOWN,
    ST_DISABLED,
    ST_GRACE,
    ST_MODE_MANUAL,
    ST_MODE_OFF,
    ST_NO_DATA,
    ST_OUTSIDE,
    ST_PAUSED,
    ST_SCENARIO_OFF,
    ST_SHADED,
    ST_UNAVAILABLE,
    ST_WATCHING,
    ST_WIND,
    ST_WINDOW_OPEN,
)


@dataclass
class CoverRuntime:
    """État mémorisé par volet (persisté, sauf `last_command_at`)."""

    shaded_by_us: bool = False
    paused_until: datetime | None = None
    last_action: str | None = None
    last_action_at: datetime | None = None
    last_command_at: datetime | None = None


@dataclass
class CoverInputs:
    """Ce que l'on observe d'un volet à l'instant T."""

    available: bool = True
    state: str | None = None
    position: int | None = None
    room_temp: float | None = None
    window_open: bool = False
    exposed: bool | None = False  # None = information d'exposition indisponible
    facade_name: str = ""
    exposure_note: str = ""  # ex. « ciel couvert »


@dataclass
class Env:
    """Contexte global commun à tous les volets."""

    now: datetime
    mode: str = MODE_AUTO
    scenario_key: str = ""
    scenario: dict[str, Any] = field(default_factory=dict)
    in_window: bool = True
    grace_active: bool = False
    outdoor: float | None = None
    wind_exceeded: bool = False
    alarm_armed: bool = False
    tolerance: int = 3
    min_move: timedelta = timedelta(minutes=10)


@dataclass
class Decision:
    status: str
    reason: str
    action: str | None = None
    # Ordre « simple » (ouvrir/fermer complètement), sans position de protection :
    # utilisé pour la protection contre le vent.
    plain: bool = False
    # L'intégration abandonne son rôle sur ce volet (elle ne le remontera plus).
    forget: bool = False


# --- aides --------------------------------------------------------------------


def _fmt(value: float | None) -> str:
    if value is None:
        return "—"
    text = f"{value:.1f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def is_shaded(cover: dict[str, Any], inp: CoverInputs, tolerance: int) -> bool:
    """Le volet est-il à la position de protection (ou plus bas) ?"""
    if inp.position is not None:
        return inp.position <= cover["close_position"] + tolerance
    return inp.state == "closed"


def is_lowered(cover: dict[str, Any], inp: CoverInputs, tolerance: int) -> bool:
    """Le volet est-il nettement abaissé, quelle que soit la position atteinte ?

    Sert à reconnaître un volet que nous avons abaissé même si sa position finale diffère
    de `close_position` (bouton « position favorite », course limitée…).
    """
    if inp.position is not None:
        return inp.position < cover["open_position"] - tolerance
    return inp.state == "closed"


def is_fully_closed(inp: CoverInputs) -> bool:
    """Le volet est-il fermé à 100 % (position 0, ou état « fermé » sans position) ?"""
    if inp.position is not None:
        return inp.position <= 0
    return inp.state == "closed"


def protection_is_full_close(cover: dict[str, Any]) -> bool:
    """La protection de ce volet consiste-t-elle à le fermer complètement ?"""
    return cover["close_method"] == CLOSE_FULL or (
        cover["close_method"] == "position" and cover["close_position"] <= 0
    )


def is_open(cover: dict[str, Any], inp: CoverInputs, tolerance: int) -> bool:
    """Le volet est-il ouvert à la position d'ouverture voulue (ou plus haut) ?"""
    if inp.position is not None:
        return inp.position >= cover["open_position"] - tolerance
    return inp.state == "open"


def _cooldown(rt: CoverRuntime, env: Env) -> bool:
    if rt.last_command_at is None or env.min_move <= timedelta(0):
        return False
    return env.now - rt.last_command_at < env.min_move


def _exposure_text(inp: CoverInputs) -> str:
    if inp.exposed:
        return f"Soleil sur la façade {inp.facade_name}"
    if inp.exposure_note:
        return f"Pas de soleil utile sur la façade {inp.facade_name} ({inp.exposure_note})"
    return f"Pas de soleil sur la façade {inp.facade_name}"


# --- décision -----------------------------------------------------------------


def decide(cover: dict[str, Any], inp: CoverInputs, rt: CoverRuntime, env: Env) -> Decision:
    """Décide de l'action à mener pour un volet, sans jamais remonter un volet fermé à 100 %.

    Un volet fermé à 100 % n'est pas remonté, quelle que soit la façon dont il a été fermé,
    sauf si le scénario actif figure dans `allow_open_closed_in` du volet. Exception : un volet
    que l'intégration a elle-même fermé complètement (sa protection est la fermeture totale)
    est bien remonté, sinon la protection ne se terminerait jamais.
    """
    decision = _decide(cover, inp, rt, env)
    if decision.action == ACTION_OPEN and not decision.plain and env.alarm_armed:
        sc = env.scenario
        if sc.get("block_open_alarm"):
            return Decision(
                decision.status, "Alarme activée : le volet n'est pas ouvert (réglage du scénario)"
            )
        if sc.get("block_open_alarm_window") and inp.window_open:
            return Decision(
                decision.status,
                "Alarme activée et fenêtre ouverte : le volet n'est pas ouvert (réglage du scénario)",
            )
    if (
        decision.action == ACTION_OPEN
        and is_fully_closed(inp)
        and env.scenario_key not in cover.get("allow_open_closed_in", [])
        and not (rt.shaded_by_us and protection_is_full_close(cover))
    ):
        return Decision(
            decision.status,
            "Volet fermé à 100 % : l'intégration ne le remonte pas",
            forget=True,
        )
    return decision


def _decide(cover: dict[str, Any], inp: CoverInputs, rt: CoverRuntime, env: Env) -> Decision:
    if not cover["enabled"]:
        return Decision(ST_DISABLED, "Ce volet n'est pas géré automatiquement")
    if not inp.available:
        return Decision(ST_UNAVAILABLE, "Le volet est indisponible")

    # Sécurité vent : prioritaire sur tout le reste (mode, scénario, pause, démarrage),
    # seul un volet explicitement désactivé y échappe.
    if cover["wind_sensitive"] and env.wind_exceeded:
        return _wind(cover, inp, env)

    if env.mode == MODE_MANUAL:
        return Decision(ST_MODE_MANUAL, "Le mode global est « manuel »")
    if env.mode != MODE_AUTO:
        return Decision(ST_MODE_OFF, "La gestion automatique est arrêtée")

    kind = env.scenario.get("kind", KIND_OFF)
    if kind == KIND_OFF:
        return Decision(ST_SCENARIO_OFF, "Le scénario actif ne commande aucun volet")
    if env.grace_active:
        return Decision(ST_GRACE, "Délai de sécurité après le démarrage")

    shaded_now = is_shaded(cover, inp, env.tolerance)
    # Un drapeau « protégé par nous » n'a de sens que si le volet est réellement abaissé.
    shaded_by_us = rt.shaded_by_us and is_lowered(cover, inp, env.tolerance)

    if rt.paused_until is not None and env.now < rt.paused_until:
        until = rt.paused_until.strftime("%H:%M")
        return Decision(ST_PAUSED, f"Action manuelle détectée : pause jusqu'à {until}")

    if not env.in_window:
        if shaded_by_us:
            return Decision(
                ST_OUTSIDE, "Fin de la plage active : le volet est remonté", ACTION_OPEN
            )
        return Decision(ST_OUTSIDE, "En dehors de la plage active")

    if kind in (KIND_HEAT, KIND_HOLD, KIND_GAIN) and inp.exposed is None:
        return Decision(
            ST_NO_DATA, "Information d'exposition au soleil indisponible : aucune action"
        )
    if kind == KIND_HEAT:
        return _heat(cover, inp, rt, env, shaded_now, shaded_by_us)
    if kind == KIND_HOLD:
        return _hold(cover, inp, rt, env, shaded_now, shaded_by_us)
    if kind == KIND_GAIN:
        return _gain(cover, inp, rt, env)
    return Decision(ST_SCENARIO_OFF, "Scénario inconnu")


def _wind(cover: dict[str, Any], inp: CoverInputs, env: Env) -> Decision:
    """Met le volet en sécurité (rentré) : `wind_action` dit quel ordre le fait."""
    if cover.get("wind_action", ACTION_OPEN) == ACTION_CLOSE:
        safe = inp.state == "closed" or (inp.position is not None and inp.position <= env.tolerance)
        action = ACTION_CLOSE
    else:
        safe = is_open(cover, inp, env.tolerance)
        action = ACTION_OPEN
    if safe:
        return Decision(ST_WIND, "Vent fort : le volet reste en sécurité")
    return Decision(ST_WIND, "Vent fort : le volet est mis en sécurité", action, plain=True)


def _try_close(
    cover: dict[str, Any], inp: CoverInputs, rt: CoverRuntime, env: Env, why: str
) -> Decision:
    """Ferme (abaisse) en respectant fenêtre ouverte et anti-usure."""
    if inp.window_open and cover["block_close_if_open"]:
        return Decision(
            ST_WINDOW_OPEN,
            "Fermeture bloquée : une fenêtre ou une porte est ouverte (ou son capteur est indisponible)",
        )
    if _cooldown(rt, env):
        return Decision(ST_COOLDOWN, "Attente de l'intervalle minimal entre deux mouvements")
    return Decision(ST_SHADED, why, ACTION_CLOSE)


def _try_open(rt: CoverRuntime, env: Env, why: str) -> Decision:
    if _cooldown(rt, env):
        return Decision(ST_COOLDOWN, "Attente de l'intervalle minimal entre deux mouvements")
    return Decision(ST_WATCHING, why, ACTION_OPEN)


def _heat(
    cover: dict[str, Any],
    inp: CoverInputs,
    rt: CoverRuntime,
    env: Env,
    shaded_now: bool,
    shaded_by_us: bool,
) -> Decision:
    sc = env.scenario
    outdoor = env.outdoor
    room = inp.room_temp
    if outdoor is None:
        return Decision(ST_NO_DATA, "Température extérieure indisponible : aucune action")

    if not shaded_by_us:
        hot_out = outdoor > sc["close_outdoor"]
        hot_room = room is not None and room > sc["close_room"]
        if inp.exposed and (hot_out or hot_room):
            if shaded_now:
                return Decision(ST_WATCHING, "Le volet est déjà à la position de protection")
            cause = f"{_fmt(outdoor)} °C dehors" if hot_out else f"{_fmt(room)} °C dans la pièce"
            return _try_close(cover, inp, rt, env, f"{_exposure_text(inp)} et {cause}")
        if not inp.exposed:
            return Decision(ST_WATCHING, _exposure_text(inp))
        return Decision(
            ST_WATCHING,
            f"Soleil présent mais températures sous les seuils ({_fmt(outdoor)} °C dehors)",
        )

    # Volet protégé par nous : faut-il le relâcher ?
    mode = sc["release_mode"]
    if mode == "any":
        cooled = outdoor < sc["open_outdoor"] or (room is not None and room < sc["open_room"])
    elif mode == "room":
        cooled = room is not None and room < sc["open_room"]
    elif mode == "outdoor":
        cooled = outdoor < sc["open_outdoor"]
    else:
        cooled = outdoor < sc["open_outdoor"] and (room is None or room < sc["open_room"])
    if not inp.exposed:
        return _try_open(rt, env, f"{_exposure_text(inp)} : le volet est remonté")
    if cooled:
        return _try_open(
            rt, env, f"Températures redescendues ({_fmt(outdoor)} °C dehors) : volet remonté"
        )
    return Decision(ST_SHADED, f"{_exposure_text(inp)} et {_fmt(outdoor)} °C dehors")


def _hold(
    cover: dict[str, Any],
    inp: CoverInputs,
    rt: CoverRuntime,
    env: Env,
    shaded_now: bool,
    shaded_by_us: bool,
) -> Decision:
    if not shaded_by_us:
        if inp.exposed and not shaded_now:
            return _try_close(cover, inp, rt, env, f"{_exposure_text(inp)} (mode vacances)")
        if inp.exposed:
            return Decision(ST_WATCHING, "Le volet est déjà à la position de protection")
        return Decision(ST_WATCHING, _exposure_text(inp))
    if not inp.exposed:
        return _try_open(rt, env, f"{_exposure_text(inp)} : le volet est remonté")
    return Decision(ST_SHADED, f"{_exposure_text(inp)} (mode vacances)")


def _gain(cover: dict[str, Any], inp: CoverInputs, rt: CoverRuntime, env: Env) -> Decision:
    sc = env.scenario
    outdoor = env.outdoor
    room = inp.room_temp
    condition = sc.get("gain_condition", "both")
    if outdoor is None and condition != "room":
        return Decision(ST_NO_DATA, "Température extérieure indisponible : aucune action")
    if not inp.exposed:
        return Decision(ST_WATCHING, _exposure_text(inp))
    cold_room = room is not None and room < sc["gain_room_below"]
    cold_out = outdoor is not None and outdoor < sc["gain_outdoor_below"]
    if condition == "room":
        wants_open = cold_room
    elif condition == "outdoor":
        wants_open = cold_out
    else:
        wants_open = cold_room and cold_out
    if wants_open and not is_open(cover, inp, env.tolerance):
        if _cooldown(rt, env):
            return Decision(ST_COOLDOWN, "Attente de l'intervalle minimal entre deux mouvements")
        return Decision(
            ST_WATCHING,
            f"{_exposure_text(inp)} et pièce fraîche ({_fmt(room)} °C) : le volet est ouvert "
            "pour profiter du soleil",
            ACTION_OPEN,
        )
    return Decision(ST_WATCHING, f"{_exposure_text(inp)} : rien à faire")

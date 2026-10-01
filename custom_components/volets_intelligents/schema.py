"""Valeurs par défaut et validation de la configuration.

Ce module n'importe pas Home Assistant : il reste testable seul.
"""

from __future__ import annotations

import copy
import re
from typing import Any

import voluptuous as vol

from .const import (
    CLOSE_BUTTON,
    CLOSE_METHODS,
    CLOSE_POSITION,
    CONFIG_VERSION,
    END_ENTITY,
    END_FIXED,
    END_SUNSET,
    EXPOSURE_ENTITY,
    EXPOSURE_SUN,
    KIND_GAIN,
    KIND_HEAT,
    KIND_HOLD,
    KIND_OFF,
)
from .solar import ORIENTATION_SOUTH, ORIENTATIONS

_ENTITY_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
_SLUG_RE = re.compile(r"^[a-z0-9_]+$")


MAX_FACADES = 12
MAX_COVERS = 150


class ConfigError(ValueError):
    """Configuration invalide (message en français)."""


DEFAULT_CONFIG: dict[str, Any] = {
    "version": CONFIG_VERSION,
    "settings": {
        "outdoor_temp_entity": None,
        "feels_like_entity": None,
        "house_orientation": 180,
        "use_max_feels_like": True,
        "weather_entity": None,
        "sunny_conditions": ["sunny", "partlycloudy"],
        "wind_entity": None,
        "wind_threshold": 50,
        "wind_release_ratio": 0.8,
        "evaluation_interval_minutes": 5,
        "startup_grace_seconds": 120,
        "min_move_interval_minutes": 10,
        "position_tolerance": 3,
        "override_pause_minutes": 120,
        "override_until_window_end": False,
        "window": {
            "start": "08:00",
            "end_mode": END_FIXED,
            "end_time": "19:00",
            "end_entity": None,
            "sunset_offset_minutes": -60,
        },
        "auto_scenario": {"enabled": False, "summer_months": [5, 6, 7, 8, 9]},
    },
    "scenarios": {
        "summer": {
            "label": "Été",
            "kind": KIND_HEAT,
            "close_outdoor": 25,
            "close_room": 24,
            "open_outdoor": 22,
            "open_room": 22,
            "release_mode": "all",
        },
        "winter": {
            "label": "Hiver",
            "kind": KIND_GAIN,
            "gain_room_below": 20,
            "gain_outdoor_below": 15,
            "block_when_alarm": False,
            "alarm_entity": None,
        },
        "vacation": {"label": "Vacances", "kind": KIND_HOLD},
        "off": {"label": "Désactivé", "kind": KIND_OFF},
    },
    "facades": [],  # rempli plus bas avec les 4 façades
    "covers": [],
}

DEFAULT_FACADE: dict[str, Any] = {
    "id": "",
    "name": "",
    "orientation": ORIENTATION_SOUTH,
    "custom_azimuth": 180,
    "default_close_position": 10,
    "exposure": {
        "mode": EXPOSURE_SUN,
        "entity": None,
        "half_angle": 80,
        "elevation_min": 10,
    },
}

DEFAULT_COVER: dict[str, Any] = {
    "entity_id": "",
    "name": "",
    "facade": "",
    "enabled": True,
    "close_method": CLOSE_POSITION,
    "close_position": 10,
    "button_entity": None,
    "open_position": 100,
    "room_temp_entity": None,
    "window_entities": [],
    "block_close_if_open": True,
    "wind_sensitive": False,
    "wind_action": "open",
    "allow_open_closed_in": [],
}


def _default_facade(facade_id: str, name: str, orientation: str) -> dict[str, Any]:
    facade = copy.deepcopy(DEFAULT_FACADE)
    facade.update({"id": facade_id, "name": name, "orientation": orientation})
    return facade


# Les quatre façades proposées par défaut : chacune peut être renommée, supprimée ou
# remplacée, et n'importe quel volet peut être affecté à n'importe quelle façade.
DEFAULT_CONFIG["facades"] = [
    _default_facade("nord", "Nord", "north"),
    _default_facade("est", "Est", "east"),
    _default_facade("sud", "Sud", "south"),
    _default_facade("ouest", "Ouest", "west"),
]


# --- validateurs élémentaires -------------------------------------------------


def _entity(*domains: str):
    """Identifiant d'entité optionnel, limité à certains domaines."""

    def check(value: Any) -> str | None:
        if value in (None, ""):
            return None
        if not isinstance(value, str) or not _ENTITY_RE.fullmatch(value):
            raise vol.Invalid(f"« {value} » n'est pas un identifiant d'entité valide")
        if domains and value.split(".")[0] not in domains:
            raise vol.Invalid(f"« {value} » doit appartenir au domaine {' ou '.join(domains)}")
        return value

    return check


def _required_entity(*domains: str):
    base = _entity(*domains)

    def check(value: Any) -> str:
        result = base(value)
        if result is None:
            raise vol.Invalid("entité obligatoire")
        return result

    return check


def _time(value: Any) -> str:
    if not isinstance(value, str) or not _TIME_RE.fullmatch(value):
        raise vol.Invalid("heure attendue au format HH:MM")
    return value


def _num(minimum: float, maximum: float):
    def check(value: Any) -> float | int:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise vol.Invalid("nombre attendu")
        if not minimum <= value <= maximum:
            raise vol.Invalid(f"doit être compris entre {minimum} et {maximum}")
        return value

    return check


def _int(minimum: int, maximum: int):
    num = _num(minimum, maximum)

    def check(value: Any) -> int:
        value = num(value)
        return int(round(value))

    return check


def _slug(value: Any) -> str:
    if not isinstance(value, str) or not _SLUG_RE.fullmatch(value):
        raise vol.Invalid("identifiant attendu : lettres minuscules, chiffres et _")
    return value


def _str(max_len: int = 80):
    def check(value: Any) -> str:
        if not isinstance(value, str):
            raise vol.Invalid("texte attendu")
        value = value.strip()
        if len(value) > max_len:
            raise vol.Invalid(f"{max_len} caractères maximum")
        return value

    return check


def _bool(value: Any) -> bool:
    if not isinstance(value, bool):
        raise vol.Invalid("vrai ou faux attendu")
    return value


def _list_of(item, max_items: int = 50):
    def check(value: Any) -> list:
        if value is None:
            return []
        if isinstance(value, list) and len(value) > max_items:
            raise vol.Invalid(f"{max_items} éléments maximum")
        if not isinstance(value, list):
            raise vol.Invalid("liste attendue")
        return [item(v) for v in value]

    return check


# --- schémas -----------------------------------------------------------------

_WINDOW = vol.Schema(
    {
        vol.Required("start"): _time,
        vol.Required("end_mode"): vol.In((END_ENTITY, END_FIXED, END_SUNSET)),
        vol.Required("end_time"): _time,
        vol.Required("end_entity"): _entity("sensor", "input_datetime", "input_text"),
        vol.Required("sunset_offset_minutes"): _int(-240, 240),
    },
    extra=vol.REMOVE_EXTRA,
)

_AUTO_SCENARIO = vol.Schema(
    {
        vol.Required("enabled"): _bool,
        vol.Required("summer_months"): _list_of(_int(1, 12)),
    },
    extra=vol.REMOVE_EXTRA,
)

_SETTINGS = vol.Schema(
    {
        vol.Required("outdoor_temp_entity"): _entity("sensor", "input_number"),
        vol.Required("feels_like_entity"): _entity("sensor", "input_number"),
        vol.Required("house_orientation"): _num(0, 360),
        vol.Required("use_max_feels_like"): _bool,
        vol.Required("weather_entity"): _entity("weather"),
        vol.Required("sunny_conditions"): _list_of(_str(40)),
        vol.Required("wind_entity"): _entity("sensor", "input_number"),
        vol.Required("wind_threshold"): _num(0, 500),
        vol.Required("wind_release_ratio"): _num(0.1, 1.0),
        vol.Required("evaluation_interval_minutes"): _int(1, 60),
        vol.Required("startup_grace_seconds"): _int(0, 900),
        vol.Required("min_move_interval_minutes"): _int(0, 240),
        vol.Required("position_tolerance"): _int(0, 20),
        vol.Required("override_pause_minutes"): _int(0, 1440),
        vol.Required("override_until_window_end"): _bool,
        vol.Required("window"): _WINDOW,
        vol.Required("auto_scenario"): _AUTO_SCENARIO,
    },
    extra=vol.REMOVE_EXTRA,
)

_FACADE_EXPOSURE = vol.Schema(
    {
        vol.Required("mode"): vol.In((EXPOSURE_ENTITY, EXPOSURE_SUN)),
        vol.Required("entity"): _entity("binary_sensor", "input_boolean", "switch"),
        vol.Required("half_angle"): _num(10, 90),
        vol.Required("elevation_min"): _num(-10, 60),
    },
    extra=vol.REMOVE_EXTRA,
)

_FACADE = vol.Schema(
    {
        vol.Required("id"): _slug,
        vol.Required("name"): _str(),
        vol.Required("orientation"): vol.In(ORIENTATIONS),
        vol.Required("custom_azimuth"): _num(0, 360),
        vol.Required("default_close_position"): _int(0, 100),
        vol.Required("exposure"): _FACADE_EXPOSURE,
    },
    extra=vol.REMOVE_EXTRA,
)

_COVER = vol.Schema(
    {
        vol.Required("entity_id"): _required_entity("cover"),
        vol.Required("name"): _str(),
        vol.Required("facade"): _str(40),
        vol.Required("enabled"): _bool,
        vol.Required("close_method"): vol.In(CLOSE_METHODS),
        vol.Required("close_position"): _int(0, 100),
        vol.Required("button_entity"): _entity("button", "input_button"),
        vol.Required("open_position"): _int(0, 100),
        vol.Required("room_temp_entity"): _entity("sensor", "input_number"),
        vol.Required("window_entities"): _list_of(
            _required_entity("binary_sensor", "input_boolean")
        ),
        vol.Required("block_close_if_open"): _bool,
        vol.Required("wind_sensitive"): _bool,
        vol.Required("wind_action"): vol.In(("open", "close")),
        vol.Required("allow_open_closed_in"): _list_of(vol.In(("summer", "winter", "vacation", "off"))),
    },
    extra=vol.REMOVE_EXTRA,
)

_SCENARIO_FIELDS: dict[str, dict[str, Any]] = {
    KIND_HEAT: {
        "close_outdoor": _num(-30, 60),
        "close_room": _num(-30, 60),
        "open_outdoor": _num(-30, 60),
        "open_room": _num(-30, 60),
        "release_mode": vol.In(("all", "any")),
    },
    KIND_GAIN: {
        "gain_room_below": _num(-30, 60),
        "gain_outdoor_below": _num(-30, 60),
        "block_when_alarm": _bool,
        "alarm_entity": _entity("alarm_control_panel"),
    },
    KIND_HOLD: {},
    KIND_OFF: {},
}

SCENARIO_KEYS = tuple(DEFAULT_CONFIG["scenarios"])


# --- normalisation ------------------------------------------------------------


def _merge(defaults: dict[str, Any], raw: Any) -> dict[str, Any]:
    """Fusionne récursivement `raw` par-dessus `defaults` (dictionnaires seulement)."""
    result = copy.deepcopy(defaults)
    if not isinstance(raw, dict):
        return result
    for key, value in raw.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def _validate(schema: vol.Schema, data: dict[str, Any], where: str) -> dict[str, Any]:
    try:
        return schema(data)
    except vol.MultipleInvalid as err:
        first = err.errors[0]
        path = ".".join(str(p) for p in first.path)
        raise ConfigError(f"{where} : {path} — {first.msg}") from err
    except vol.Invalid as err:
        path = ".".join(str(p) for p in err.path)
        raise ConfigError(f"{where} : {path} — {err.msg}") from err


def normalize_config(raw: Any) -> dict[str, Any]:
    """Complète, valide et retourne une configuration propre.

    Lève ConfigError avec un message français si la configuration est invalide.
    """
    if not isinstance(raw, dict):
        raise ConfigError("La configuration doit être un objet")

    merged = _merge(
        DEFAULT_CONFIG, {k: v for k, v in raw.items() if k != "facades" and k != "covers"}
    )
    config: dict[str, Any] = {"version": CONFIG_VERSION}

    config["settings"] = _validate(_SETTINGS, merged["settings"], "Réglages")
    window = config["settings"]["window"]
    if window["end_mode"] == END_ENTITY and not window["end_entity"]:
        raise ConfigError(
            "Réglages : choisissez l'entité qui donne l'heure de fin de plage "
            "ou un autre mode de fin"
        )

    # Scénarios : clés fixes, `kind` non modifiable.
    scenarios: dict[str, Any] = {}
    raw_scenarios: dict[str, Any] = (
        raw["scenarios"] if isinstance(raw.get("scenarios"), dict) else {}
    )
    for key, default in DEFAULT_CONFIG["scenarios"].items():
        entry = _merge(default, raw_scenarios.get(key))
        entry["kind"] = default["kind"]
        fields = {
            vol.Required("label"): _str(30),
            vol.Required("kind"): str,
            **{vol.Required(k): v for k, v in _SCENARIO_FIELDS[default["kind"]].items()},
        }
        entry = _validate(vol.Schema(fields, extra=vol.REMOVE_EXTRA), entry, f"Scénario {key}")
        if default["kind"] == KIND_HEAT:
            if entry["close_outdoor"] < entry["open_outdoor"]:
                raise ConfigError(
                    f"Scénario {key} : le seuil de fermeture extérieur doit être "
                    "supérieur ou égal au seuil d'ouverture"
                )
            if entry["close_room"] < entry["open_room"]:
                raise ConfigError(
                    f"Scénario {key} : le seuil de fermeture de la pièce doit être "
                    "supérieur ou égal au seuil d'ouverture"
                )
        scenarios[key] = entry
    config["scenarios"] = scenarios

    # Façades
    facades: list[dict[str, Any]] = []
    raw_facades = raw["facades"] if "facades" in raw else DEFAULT_CONFIG["facades"]
    raw_facades = raw_facades or []
    if not isinstance(raw_facades, list):
        raise ConfigError("Façades : liste attendue")
    if len(raw_facades) > MAX_FACADES:
        raise ConfigError(f"Façades : {MAX_FACADES} au maximum")
    seen_facades: set[str] = set()
    for index, item in enumerate(raw_facades, start=1):
        facade = _validate(_FACADE, _merge(DEFAULT_FACADE, item), f"Façade n°{index}")
        if facade["id"] in seen_facades:
            raise ConfigError(f"Façade « {facade['id']} » en double")
        seen_facades.add(facade["id"])
        if not facade["name"]:
            facade["name"] = facade["id"].replace("_", " ").title()
        exposure = facade["exposure"]
        if exposure["mode"] == EXPOSURE_ENTITY and not exposure["entity"]:
            raise ConfigError(
                f"Façade « {facade['name']} » : choisissez une entité d'exposition "
                "ou passez en mode « position du soleil »"
            )
        facades.append(facade)
    config["facades"] = facades

    # Volets
    covers: list[dict[str, Any]] = []
    raw_covers = raw.get("covers") or []
    if not isinstance(raw_covers, list):
        raise ConfigError("Volets : liste attendue")
    if len(raw_covers) > MAX_COVERS:
        raise ConfigError(f"Volets : {MAX_COVERS} au maximum")
    seen_covers: set[str] = set()
    for index, item in enumerate(raw_covers, start=1):
        cover = _validate(_COVER, _merge(DEFAULT_COVER, item), f"Volet n°{index}")
        if cover["entity_id"] in seen_covers:
            raise ConfigError(f"Volet « {cover['entity_id']} » en double")
        seen_covers.add(cover["entity_id"])
        if not cover["name"]:
            cover["name"] = cover["entity_id"].split(".", 1)[1].replace("_", " ").title()
        if cover["facade"] not in seen_facades:
            raise ConfigError(
                f"Volet « {cover['name']} » : la façade « {cover['facade']} » n'existe pas"
            )
        if cover["close_position"] > cover["open_position"]:
            raise ConfigError(
                f"Volet « {cover['name']} » : la position de protection ne peut pas être "
                "supérieure à la position d'ouverture"
            )
        if cover["close_method"] == CLOSE_BUTTON and not cover["button_entity"]:
            raise ConfigError(
                f"Volet « {cover['name']} » : choisissez le bouton à presser "
                "ou une autre méthode de fermeture"
            )
        covers.append(cover)
    config["covers"] = covers

    return config


def default_config() -> dict[str, Any]:
    """Copie indépendante de la configuration par défaut."""
    return copy.deepcopy(DEFAULT_CONFIG)

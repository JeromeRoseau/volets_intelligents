"""Tests de la validation de configuration."""

import pytest

from custom_components.volets_intelligents.schema import (
    ConfigError,
    default_config,
    normalize_config,
)


def base():
    cfg = default_config()
    cfg["facades"] = [
        {
            "id": "est",
            "name": "Est",
            "exposure": {"mode": "entity", "entity": "binary_sensor.volets_exposition_est"},
        }
    ]
    cfg["covers"] = [{"entity_id": "cover.bureau", "name": "Bureau", "facade": "est"}]
    return cfg


def test_default_config_is_valid():
    cfg = normalize_config(default_config())
    assert cfg["covers"] == []
    assert [f["id"] for f in cfg["facades"]] == ["nord", "est", "sud", "ouest"]
    assert cfg["settings"]["house_orientation"] == 180
    assert set(cfg["scenarios"]) == {"summer", "winter", "vacation", "off"}


def test_defaults_are_filled_in():
    cfg = normalize_config(base())
    cover = cfg["covers"][0]
    assert cover["close_position"] == 10 and cover["enabled"] is True
    assert cfg["facades"][0]["default_close_position"] == 10


def test_normalize_is_idempotent():
    once = normalize_config(base())
    assert normalize_config(once) == once


def test_scenario_kind_cannot_be_changed():
    raw = base()
    raw["scenarios"] = {"off": {"kind": "heat_protection", "label": "Ok"}}
    assert normalize_config(raw)["scenarios"]["off"]["kind"] == "off"


def test_unknown_facade_rejected():
    raw = base()
    raw["covers"][0]["facade"] = "nord"
    with pytest.raises(ConfigError, match="nord"):
        normalize_config(raw)


def test_duplicate_cover_rejected():
    raw = base()
    raw["covers"].append(dict(raw["covers"][0]))
    with pytest.raises(ConfigError, match="double"):
        normalize_config(raw)


def test_wrong_domain_rejected():
    raw = base()
    raw["covers"][0]["entity_id"] = "light.bureau"
    with pytest.raises(ConfigError, match="cover"):
        normalize_config(raw)


def test_hysteresis_must_be_positive():
    raw = base()
    raw["scenarios"] = {"summer": {"close_outdoor": 20, "open_outdoor": 22}}
    with pytest.raises(ConfigError, match="extérieur"):
        normalize_config(raw)


def test_position_out_of_range_rejected():
    raw = base()
    raw["covers"][0]["close_position"] = 140
    with pytest.raises(ConfigError, match="close_position"):
        normalize_config(raw)


def test_button_method_requires_button():
    raw = base()
    raw["covers"][0]["close_method"] = "button"
    with pytest.raises(ConfigError, match="bouton"):
        normalize_config(raw)


def test_entity_facade_requires_entity():
    raw = base()
    raw["facades"][0]["exposure"]["entity"] = None
    with pytest.raises(ConfigError, match="exposition"):
        normalize_config(raw)


def test_bad_time_rejected():
    raw = base()
    raw["settings"] = {"window": {"start": "8h"}}
    with pytest.raises(ConfigError, match="HH:MM"):
        normalize_config(raw)


def test_not_a_dict_rejected():
    with pytest.raises(ConfigError):
        normalize_config([])


def test_four_facades_by_default_and_any_cover_can_use_any_facade():
    raw = default_config()
    raw["covers"] = [
        {"entity_id": "cover.a", "facade": "nord"},
        {"entity_id": "cover.b", "facade": "nord"},
        {"entity_id": "cover.c", "facade": "ouest"},
    ]
    cfg = normalize_config(raw)
    assert [c["facade"] for c in cfg["covers"]] == ["nord", "nord", "ouest"]


def test_facades_can_be_removed_and_added():
    raw = base()
    raw["facades"].append(
        {
            "id": "velux",
            "name": "Velux",
            "orientation": "custom",
            "custom_azimuth": 225,
            "exposure": {"mode": "sun"},
        }
    )
    cfg = normalize_config(raw)
    assert [f["id"] for f in cfg["facades"]] == ["est", "velux"]
    assert cfg["facades"][1]["custom_azimuth"] == 225


def test_house_orientation_validated():
    raw = base()
    raw["settings"] = {"house_orientation": 400}
    with pytest.raises(ConfigError, match="house_orientation"):
        normalize_config(raw)


def test_half_angle_validated():
    raw = base()
    raw["facades"][0]["exposure"]["half_angle"] = 120
    with pytest.raises(ConfigError, match="half_angle"):
        normalize_config(raw)

"""Constantes et configuration d'exemple partagées par les tests."""

from homeassistant.components.cover import CoverEntityFeature

from custom_components.volets_intelligents.schema import default_config

COVER = "cover.bureau"
FEATURES = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.SET_POSITION


def make_config():
    cfg = default_config()
    cfg["settings"].update(
        {
            "outdoor_temp_entity": "sensor.dehors",
            "startup_grace_seconds": 0,
            "min_move_interval_minutes": 0,
            "window": {"start": "08:00", "end_mode": "fixed", "end_time": "19:00"},
        }
    )
    cfg["facades"] = [
        {
            "id": "est",
            "name": "Est",
            "exposure": {"mode": "entity", "entity": "binary_sensor.expo_est"},
        }
    ]
    cfg["covers"] = [
        {
            "entity_id": COVER,
            "name": "Bureau",
            "facade": "est",
            "room_temp_entity": "sensor.piece",
            "window_entities": ["binary_sensor.fenetre"],
        }
    ]
    return cfg

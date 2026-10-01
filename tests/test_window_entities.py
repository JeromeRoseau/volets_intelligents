"""Entités de la plage active et des façades (exposition, heures de début et de fin)."""

import copy

import pytest
from homeassistant.exceptions import HomeAssistantError


async def _refresh(hass, manager):
    await manager.async_evaluate()
    await hass.async_block_till_done()


async def test_window_read_only_entities(hass, setup):
    manager, _, _, _ = setup
    await _refresh(hass, manager)
    assert hass.states.get("binary_sensor.volets_plage_active").state == "on"
    # 08:00 → 19:00 heure de Paris (UTC+2 en juillet)
    assert hass.states.get("sensor.volets_plage_debut").state.startswith("2026-07-15T06:00")
    assert hass.states.get("sensor.volets_plage_fin").state.startswith("2026-07-15T17:00")


async def test_window_settings_are_editable_from_entities(hass, setup):
    manager, _, _, _ = setup
    await _refresh(hass, manager)
    assert hass.states.get("time.volets_reglage_plage_debut").state == "08:00:00"
    await hass.services.async_call(
        "time", "set_value",
        {"entity_id": "time.volets_reglage_plage_debut", "time": "09:30:00"}, blocking=True,
    )
    await hass.services.async_call(
        "time", "set_value",
        {"entity_id": "time.volets_reglage_plage_fin", "time": "20:15:00"}, blocking=True,
    )
    window = manager.config["settings"]["window"]
    assert window["start"] == "09:30" and window["end_time"] == "20:15"
    assert hass.states.get("time.volets_reglage_plage_debut").state == "09:30:00"

    await hass.services.async_call(
        "select", "select_option",
        {"entity_id": "select.volets_reglage_plage_mode_fin", "option": "sunset"}, blocking=True,
    )
    await hass.services.async_call(
        "number", "set_value",
        {"entity_id": "number.volets_reglage_plage_decalage_coucher", "value": -30}, blocking=True,
    )
    assert manager.config["settings"]["window"]["end_mode"] == "sunset"
    assert manager.config["settings"]["window"]["sunset_offset_minutes"] == -30


async def test_invalid_window_setting_is_refused(hass, setup):
    manager, _, _, _ = setup
    # Le mode « entité » exige une entité de fin : la configuration est refusée, rien ne change.
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "select", "select_option",
            {"entity_id": "select.volets_reglage_plage_mode_fin", "option": "entity"},
            blocking=True,
        )
    assert manager.config["settings"]["window"]["end_mode"] == "fixed"


async def test_facade_entities_follow_config(hass, setup):
    manager, _, _, _ = setup
    config = copy.deepcopy(manager.config)
    config["facades"].append(
        {"id": "sud", "name": "Sud", "orientation": "south", "exposure": {"mode": "sun"}}
    )
    await manager.async_set_config(config)
    await hass.async_block_till_done()
    exposed = hass.states.get("binary_sensor.volets_facade_sud_exposee")
    assert exposed is not None and exposed.state == "on"
    assert exposed.attributes["windows"]
    assert hass.states.get("sensor.volets_facade_sud_debut").state.startswith("2026-07-15T")
    assert hass.states.get("sensor.volets_facade_sud_fin").state.startswith("2026-07-15T")

    config = copy.deepcopy(manager.config)
    config["facades"] = [f for f in config["facades"] if f["id"] != "sud"]
    await manager.async_set_config(config)
    await hass.async_block_till_done()
    assert hass.states.get("binary_sensor.volets_facade_sud_exposee") is None
    assert hass.states.get("sensor.volets_facade_sud_debut") is None


async def test_summer_thresholds_are_editable_from_entities(hass, setup):
    manager, _, _, _ = setup
    await _refresh(hass, manager)
    state = hass.states.get("number.volets_seuil_ete_fermeture_exterieur")
    assert state is not None and float(state.state) == manager.config["scenarios"]["summer"]["close_outdoor"]
    await hass.services.async_call(
        "number", "set_value",
        {"entity_id": "number.volets_seuil_ete_fermeture_exterieur", "value": 28}, blocking=True,
    )
    assert manager.config["scenarios"]["summer"]["close_outdoor"] == 28
    assert float(hass.states.get("number.volets_seuil_ete_fermeture_exterieur").state) == 28


def test_facade_window_stays_visible_after_the_last_window():
    from datetime import datetime, timezone

    from custom_components.volets_intelligents.manager import VoletsManager

    windows = [{"start": "08:00", "end": "12:00"}, {"start": "14:00", "end": "16:00"}]
    nxt = VoletsManager._next_window
    tz = timezone.utc
    assert nxt(datetime(2026, 7, 1, 7, 0, tzinfo=tz), windows)["next_start"].startswith("2026-07-01T08:00")
    assert nxt(datetime(2026, 7, 1, 13, 0, tzinfo=tz), windows)["next_start"].startswith("2026-07-01T14:00")
    after = nxt(datetime(2026, 7, 1, 20, 0, tzinfo=tz), windows)
    assert after["next_start"].startswith("2026-07-01T14:00") and after["next_end"].startswith("2026-07-01T16:00")
    assert nxt(datetime(2026, 7, 1, 20, 0, tzinfo=tz), []) == {"next_start": None, "next_end": None}

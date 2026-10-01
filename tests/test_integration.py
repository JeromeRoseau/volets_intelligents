"""Tests d'intégration avec un vrai Home Assistant de test."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.volets_intelligents.const import DOMAIN
from custom_components.volets_intelligents.schema import ConfigError

from .common import COVER, FEATURES, make_config


async def test_entities_created(hass, setup):
    assert hass.states.get("select.volets_mode").state == "auto"
    assert hass.states.get("select.volets_scenario").state == "summer"
    assert hass.states.get("switch.volets_bureau_auto").state == "on"
    assert hass.states.get("sensor.volets_bureau_statut") is not None
    assert hass.states.get("sensor.volets_temperature_exterieure_effective").state == "27.0"


async def test_hot_and_exposed_shades_to_target_position(hass, setup):
    manager, calls, _, _ = setup
    await manager.async_evaluate()
    assert len(calls) == 1
    assert calls[0].data == {"entity_id": COVER, "position": 10}
    assert hass.states.get("sensor.volets_bureau_statut").state == "shaded"
    assert (
        "Soleil sur la façade Est"
        in hass.states.get("sensor.volets_bureau_statut").attributes["reason"]
    )


async def test_no_second_command_once_shaded(hass, setup):
    manager, calls, _, _ = setup
    await manager.async_evaluate()
    hass.states.async_set(COVER, "open", {"current_position": 10, "supported_features": FEATURES})
    await manager.async_evaluate()
    assert len(calls) == 1


async def test_sun_leaves_reopens_cover(hass, setup):
    manager, calls, opens, _ = setup
    await manager.async_evaluate()
    hass.states.async_set(COVER, "open", {"current_position": 10, "supported_features": FEATURES})
    hass.states.async_set("binary_sensor.expo_est", "off")
    await manager.async_evaluate()
    assert len(opens) == 1


async def test_manual_move_pauses_management(hass, setup, freezer):
    manager, calls, opens, _ = setup
    await manager.async_evaluate()
    hass.states.async_set(COVER, "open", {"current_position": 10, "supported_features": FEATURES})
    freezer.tick(timedelta(minutes=5))
    # L'utilisateur rouvre le volet à la main.
    hass.states.async_set(COVER, "open", {"current_position": 100, "supported_features": FEATURES})
    await hass.async_block_till_done()
    await manager.async_evaluate()
    assert hass.states.get("sensor.volets_bureau_statut").state == "paused"
    assert len(calls) == 1  # pas de nouvelle fermeture


async def test_our_own_movement_is_not_a_manual_override(hass, setup, freezer):
    manager, calls, _, _ = setup
    await manager.async_evaluate()
    freezer.tick(timedelta(seconds=10))
    hass.states.async_set(
        COVER, "closing", {"current_position": 60, "supported_features": FEATURES}
    )
    hass.states.async_set(COVER, "open", {"current_position": 10, "supported_features": FEATURES})
    await hass.async_block_till_done()
    await manager.async_evaluate()
    assert hass.states.get("sensor.volets_bureau_statut").state == "shaded"


async def test_pause_and_resume_services(hass, setup):
    manager, calls, _, _ = setup
    await hass.services.async_call(
        DOMAIN, "pause", {"entity_id": COVER, "minutes": 30}, blocking=True
    )
    assert hass.states.get("sensor.volets_bureau_statut").state == "paused"
    assert not calls
    await hass.services.async_call(DOMAIN, "resume", {"entity_id": COVER}, blocking=True)
    assert len(calls) == 1


async def test_switch_disables_cover(hass, setup):
    manager, calls, _, _ = setup
    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": "switch.volets_bureau_auto"}, blocking=True
    )
    await hass.async_block_till_done()
    assert hass.states.get("sensor.volets_bureau_statut").state == "disabled"
    assert not calls


async def test_manual_mode_blocks_everything(hass, setup):
    manager, calls, _, _ = setup
    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": "select.volets_mode", "option": "manual"},
        blocking=True,
    )
    assert hass.states.get("sensor.volets_bureau_statut").state == "mode_manual"
    assert not calls


async def test_outdoor_sensor_unavailable_does_nothing(hass, setup):
    manager, calls, opens, _ = setup
    hass.states.async_set("sensor.dehors", "unavailable")
    await manager.async_evaluate()
    assert hass.states.get("sensor.volets_bureau_statut").state == "no_data"
    assert not calls and not opens


async def test_window_open_blocks_closing(hass, setup):
    manager, calls, _, _ = setup
    hass.states.async_set("binary_sensor.fenetre", "on")
    await manager.async_evaluate()
    assert hass.states.get("sensor.volets_bureau_statut").state == "window_open"
    assert not calls


async def test_outside_window_no_action(hass, setup, freezer):
    manager, calls, _, _ = setup
    freezer.move_to("2026-07-15 21:00:00+02:00")
    await manager.async_evaluate()
    assert hass.states.get("sensor.volets_bureau_statut").state == "outside_window"
    assert not calls


async def test_entity_end_time_with_fallback(hass, setup, freezer):
    manager, calls, _, _ = setup
    cfg = make_config()
    cfg["settings"]["window"].update(
        {"end_mode": "entity", "end_entity": "sensor.remontee", "end_time": "19:00"}
    )
    await manager.async_set_config(cfg)
    hass.states.async_set("sensor.remontee", "13:30")
    await manager.async_evaluate()
    assert manager.status["in_window"] is False
    hass.states.async_set("sensor.remontee", "unavailable")  # repli sur 19:00
    await manager.async_evaluate()
    assert manager.status["in_window"] is True


async def test_sun_based_exposure_uses_house_orientation(hass, setup):
    manager, _, _, _ = setup
    cfg = make_config()
    cfg["facades"] = [
        {"id": "sud", "name": "Sud", "orientation": "south", "exposure": {"mode": "sun"}},
        {"id": "est", "name": "Est", "orientation": "east", "exposure": {"mode": "sun"}},
    ]
    cfg["covers"][0]["facade"] = "sud"
    await manager.async_set_config(cfg)
    await manager.async_evaluate()
    # 15 juillet, 14 h locale : le soleil est au sud-ouest, haut dans le ciel.
    facades = manager.status["facades"]
    assert facades["sud"]["exposed"] is True
    assert facades["est"]["exposed"] is False
    assert facades["sud"]["azimuth"] == 180
    assert 160 < manager.status["sun"]["azimuth"] < 230
    assert "09:30" < facades["sud"]["windows"][0]["start"] < "11:00"

    # La maison tourne : sa façade « Sud » regarde maintenant vers l'est (90°).
    cfg["settings"]["house_orientation"] = 90
    await manager.async_set_config(cfg)
    await manager.async_evaluate()
    facades = manager.status["facades"]
    assert facades["sud"]["azimuth"] == 90
    assert facades["sud"]["exposed"] is False
    assert facades["est"]["azimuth"] == 0


async def test_cloudy_weather_neutralises_sun(hass, setup):
    manager, calls, _, _ = setup
    cfg = make_config()
    cfg["settings"]["weather_entity"] = "weather.maison"
    hass.states.async_set("weather.maison", "cloudy")
    await manager.async_set_config(cfg)
    await manager.async_evaluate()
    assert not calls
    assert manager.status["sunny"] is False


async def test_invalid_config_is_rejected_and_keeps_previous(hass, setup):
    manager, _, _, _ = setup
    bad = make_config()
    bad["covers"][0]["facade"] = "inconnue"
    with pytest.raises(ConfigError):
        await manager.async_set_config(bad)
    assert manager.config["covers"][0]["facade"] == "est"


async def test_scenario_change_refused_when_auto_scenario(hass, setup):
    manager, _, _, _ = setup
    cfg = make_config()
    cfg["settings"]["auto_scenario"]["enabled"] = True
    await manager.async_set_config(cfg)
    with pytest.raises(HomeAssistantError):
        await manager.async_set_scenario("vacation")


async def test_removing_a_cover_removes_its_entities(hass, setup):
    manager, _, _, _ = setup
    cfg = make_config()
    cfg["covers"] = []
    await manager.async_set_config(cfg)
    await hass.async_block_till_done()
    assert hass.states.get("switch.volets_bureau_auto") is None
    assert hass.states.get("sensor.volets_bureau_statut") is None


async def test_unload_and_reload(hass, setup):
    _, _, _, entry = setup
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_toggling_a_cover_does_not_resubscribe(hass, setup):
    manager, _, _, _ = setup
    before = list(manager._unsubs)
    await manager.async_set_cover_enabled(COVER, False)
    assert manager._unsubs == before
    # Ajouter une entité suivie force en revanche un nouvel abonnement.
    cfg = make_config()
    cfg["settings"]["wind_entity"] = "sensor.vent"
    await manager.async_set_config(cfg)
    assert manager._unsubs != before


async def test_runtime_not_rewritten_when_unchanged(hass, setup):
    manager, _, _, _ = setup
    manager._save_runtime()
    with patch.object(manager._runtime_store, "async_delay_save") as save:
        manager._save_runtime()
        manager._save_runtime()
        assert save.call_count == 0
        manager.mode = "manual"
        manager._save_runtime()
        assert save.call_count == 1

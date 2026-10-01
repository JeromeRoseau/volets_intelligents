"""Régressions issues de la relecture indépendante (chaque test correspond à un bogue corrigé)."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.volets_intelligents.const import DOMAIN
from custom_components.volets_intelligents.schema import (
    ConfigError,
    default_config,
    normalize_config,
)

from .common import COVER, FEATURES, make_config

STATUS = "sensor.volets_bureau_statut"


def state(hass, position, name="open"):
    hass.states.async_set(
        COVER, name, {"current_position": position, "supported_features": FEATURES}
    )


# --- sécurité fenêtre / capteurs -------------------------------------------------


async def test_unavailable_window_sensor_blocks_closing(hass, setup):
    manager, calls, _, _ = setup
    hass.states.async_set("binary_sensor.fenetre", "unavailable")
    await manager.async_evaluate()
    assert hass.states.get(STATUS).state == "window_open"
    assert not calls


async def test_exposure_sensor_unavailable_does_nothing(hass, setup):
    manager, calls, opens, _ = setup
    await manager.async_evaluate()
    assert len(calls) == 1
    state(hass, 10)
    hass.states.async_set("binary_sensor.expo_est", "unavailable")
    await manager.async_evaluate()
    assert hass.states.get(STATUS).state == "no_data"
    assert not opens  # le volet protégé n'est pas rouvert à cause d'une panne de capteur


async def test_missing_outdoor_measure_means_no_action_even_with_feels_like(hass, setup):
    manager, calls, _, _ = setup
    cfg = make_config()
    cfg["settings"]["feels_like_entity"] = "sensor.ressentie"
    hass.states.async_set("sensor.ressentie", "33")
    hass.states.async_set("sensor.dehors", "unavailable")
    await manager.async_set_config(cfg)
    await manager.async_evaluate()
    assert hass.states.get(STATUS).state == "no_data"
    assert not calls


# --- position atteinte différente de close_position -------------------------------


async def test_favorite_button_position_does_not_cause_repeated_closing(hass, setup, freezer):
    manager, calls, opens, _ = setup
    await manager.async_evaluate()
    assert len(calls) == 1
    # Le volet s'arrête à 35 % (position favorite) au lieu des 10 % demandés.
    freezer.tick(timedelta(minutes=30))
    state(hass, 35)
    await manager.async_evaluate()
    await manager.async_evaluate()
    assert len(calls) == 1
    assert hass.states.get(STATUS).state == "shaded"
    # Quand le soleil part, le volet est bien remonté.
    hass.states.async_set("binary_sensor.expo_est", "off")
    await manager.async_evaluate()
    assert len(opens) == 1


# --- volets lents ---------------------------------------------------------------


async def test_slow_cover_is_not_mistaken_for_manual_override(hass, setup, freezer):
    manager, calls, _, _ = setup
    await manager.async_evaluate()
    freezer.tick(timedelta(seconds=10))
    state(hass, 80, "closing")
    await hass.async_block_till_done()
    freezer.tick(timedelta(seconds=110))  # 2 min après l'ordre : fin du délai fixe
    state(hass, 40, "closing")
    await hass.async_block_till_done()
    freezer.tick(timedelta(seconds=90))
    state(hass, 10, "open")
    await hass.async_block_till_done()
    await manager.async_evaluate()
    assert hass.states.get(STATUS).state == "shaded"
    assert manager.runtime[COVER].shaded_by_us is True


# --- plage active qui passe minuit ----------------------------------------------


async def test_window_crossing_midnight(hass, setup, freezer):
    manager, _, _, _ = setup
    cfg = make_config()
    cfg["settings"]["window"] = {"start": "20:00", "end_mode": "fixed", "end_time": "02:00"}
    await manager.async_set_config(cfg)
    for moment, expected in (
        ("2026-07-15 19:00:00+02:00", False),
        ("2026-07-15 22:00:00+02:00", True),
        ("2026-07-16 01:00:00+02:00", True),
        ("2026-07-16 03:00:00+02:00", False),
    ):
        freezer.move_to(moment)
        await manager.async_evaluate()
        assert manager.status["in_window"] is expected, moment


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("13:30", True),
        ("13:30:00", True),
        ("13:30:00.123", True),
        ("13:30:00+02:00", True),
        ("2026-07-15T13:30:00+02:00", True),
        ("not a time", None),
        ("25:00", None),
    ],
)
async def test_end_entity_formats(hass, setup, raw, expected):
    manager, _, _, _ = setup
    cfg = make_config()
    cfg["settings"]["window"].update(
        {"end_mode": "entity", "end_entity": "sensor.fin", "end_time": "19:00"}
    )
    await manager.async_set_config(cfg)
    hass.states.async_set("sensor.fin", raw)
    await manager.async_evaluate()
    # 14:00 locale : une fin à 13:30 la ferme, le repli 19:00 la laisse ouverte.
    assert manager.status["in_window"] is (False if expected else True)


# --- vent ----------------------------------------------------------------------


async def test_wind_protection_overrides_manual_mode_and_uses_plain_commands(hass, setup):
    manager, calls, opens, _ = setup
    cfg = make_config()
    cfg["settings"]["wind_entity"] = "sensor.vent"
    cfg["settings"]["wind_threshold"] = 40
    cfg["covers"][0].update({"wind_sensitive": True, "wind_action": "open"})
    hass.states.async_set("sensor.vent", "10")
    await manager.async_set_config(cfg)
    await manager.async_set_mode("manual")
    state(hass, 10)
    calls.clear()
    hass.states.async_set("sensor.vent", "55")
    await manager.async_evaluate()
    assert hass.states.get(STATUS).state == "wind_protected"
    assert len(opens) == 1 and not calls  # ouverture complète, pas de position intermédiaire


async def test_wind_action_close_retracts_an_awning(hass, setup):
    manager, _, _, _ = setup
    from pytest_homeassistant_custom_component.common import async_mock_service

    closes = async_mock_service(hass, "cover", "close_cover")
    cfg = make_config()
    cfg["settings"]["wind_entity"] = "sensor.vent"
    cfg["settings"]["wind_threshold"] = 40
    cfg["covers"][0].update({"wind_sensitive": True, "wind_action": "close"})
    hass.states.async_set("sensor.vent", "55")
    await manager.async_set_config(cfg)
    await manager.async_evaluate()
    assert len(closes) == 1


async def test_disabled_cover_ignores_wind(hass, setup):
    manager, _, opens, _ = setup
    cfg = make_config()
    cfg["settings"]["wind_entity"] = "sensor.vent"
    cfg["settings"]["wind_threshold"] = 40
    cfg["covers"][0].update({"wind_sensitive": True, "enabled": False})
    hass.states.async_set("sensor.vent", "55")
    await manager.async_set_config(cfg)
    await manager.async_evaluate()
    assert not opens


# --- redémarrage : l'état mémorisé est conservé ------------------------------------


async def test_restart_keeps_shaded_flag_and_lifts_at_end_of_window(hass, hass_storage, freezer):
    from pytest_homeassistant_custom_component.common import async_mock_service

    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.latitude, hass.config.longitude, hass.config.elevation = 45.58, 4.81, 200
    freezer.move_to("2026-07-15 20:00:00+02:00")  # après la fin de plage (19:00)
    hass.config.components.update({"frontend", "panel_custom", "http", "websocket_api"})
    opens = async_mock_service(hass, "cover", "open_cover")
    hass_storage["volets_intelligents.config"] = {
        "version": 1,
        "minor_version": 1,
        "key": "volets_intelligents.config",
        "data": make_config(),
    }
    hass_storage["volets_intelligents.runtime"] = {
        "version": 1,
        "minor_version": 1,
        "key": "volets_intelligents.runtime",
        "data": {
            "mode": "auto",
            "scenario": "summer",
            "covers": {COVER: {"shaded_by_us": True, "paused_until": None}},
        },
    }
    state(hass, 10)
    hass.states.async_set("sensor.dehors", "27")
    hass.states.async_set("binary_sensor.expo_est", "off")
    hass.states.async_set("binary_sensor.fenetre", "off")
    entry = MockConfigEntry(domain=DOMAIN, title="Volets Intelligents")
    entry.add_to_hass(hass)
    with patch("custom_components.volets_intelligents._async_register_frontend"):
        assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert len(opens) == 1  # l'état mémorisé survit au redémarrage : le volet est remonté
    await hass.config_entries.async_unload(entry.entry_id)


# --- permissions WebSocket -------------------------------------------------------


@pytest.mark.real_http
async def test_read_only_user_cannot_change_mode_or_pause(
    hass: HomeAssistant, setup, hass_ws_client, hass_read_only_access_token
):
    manager, _, _, _ = setup
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    msg_id = 10
    for payload in (
        {"command": "set_mode", "value": "off"},
        {"command": "pause"},
        {"command": "pause", "entity_id": COVER},
    ):
        msg_id += 1
        await ws.send_json({"id": msg_id, "type": "volets_intelligents/command", **payload})
        res = await ws.receive_json()
        assert not res["success"] and res["error"]["code"] == "unauthorized", payload
    assert manager.mode == "auto"
    # La lecture du statut reste permise.
    await ws.send_json({"id": msg_id + 1, "type": "volets_intelligents/get_status"})
    assert (await ws.receive_json())["success"]


@pytest.mark.real_http
async def test_admin_can_change_mode_over_websocket(hass, setup, hass_ws_client):
    manager, _, _, _ = setup
    ws = await hass_ws_client(hass)
    await ws.send_json(
        {"id": 1, "type": "volets_intelligents/command", "command": "set_mode", "value": "manual"}
    )
    assert (await ws.receive_json())["success"]
    assert manager.mode == "manual"


# --- validation ---------------------------------------------------------------------


def _cfg():
    cfg = default_config()
    cfg["covers"] = [{"entity_id": "cover.a", "facade": "sud"}]
    return cfg


@pytest.mark.parametrize(
    "mutation",
    [
        lambda c: c["covers"][0].update(entity_id="cover.a\n"),
        lambda c: c["settings"]["window"].update(start="08:00\n"),
        lambda c: c["facades"][0].update(id="nord\n"),
        lambda c: c["settings"]["window"].update(end_mode="entity", end_entity=None),
        lambda c: c["covers"][0].update(close_position=80, open_position=20),
        lambda c: c["covers"][0].update(wind_action="sideways"),
        lambda c: c["settings"].update(sunny_conditions=["sunny"] * 500),
        lambda c: c.update(facades=c["facades"] * 10),
        lambda c: c.update(
            covers=[{"entity_id": f"cover.c{i}", "facade": "sud"} for i in range(200)]
        ),
    ],
)
def test_hostile_or_inconsistent_configs_are_rejected(mutation):
    cfg = _cfg()
    mutation(cfg)
    with pytest.raises(ConfigError):
        normalize_config(cfg)


# --- état des capteurs d'ouverture dans le statut -----------------------------------


@pytest.mark.parametrize(
    ("sensor_state", "expected"),
    [("on", "open"), ("off", "closed"), ("unavailable", "unknown")],
)
async def test_status_exposes_window_state(hass, setup, sensor_state, expected):
    manager, _, _, _ = setup
    hass.states.async_set("binary_sensor.fenetre", sensor_state)
    await manager.async_evaluate()
    cover = manager.status["covers"][0]
    assert cover["window_state"] == expected
    assert cover["window_sensors"] == [{"entity_id": "binary_sensor.fenetre", "state": expected}]


@pytest.mark.real_http
async def test_get_entities_returns_real_entity_ids(hass, setup, hass_ws_client):
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "volets_intelligents/get_entities"})
    res = await ws.receive_json()
    assert res["success"], res
    data = res["result"]
    assert data["mode"] == "select.volets_mode"
    assert data["scenario"] == "select.volets_scenario"
    assert data["outdoor"] == "sensor.volets_temperature_exterieure_effective"
    assert data["covers"][0]["cover"] == COVER
    assert data["covers"][0]["status"] == STATUS
    assert data["covers"][0]["switch"].startswith("switch.")


@pytest.mark.real_http
async def test_get_entities_is_admin_only(hass, setup, hass_ws_client, hass_read_only_access_token):
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json({"id": 1, "type": "volets_intelligents/get_entities"})
    res = await ws.receive_json()
    assert not res["success"] and res["error"]["code"] == "unauthorized"


async def test_status_sensor_exposes_window_state_attribute(hass, setup):
    manager, _, _, _ = setup
    hass.states.async_set("binary_sensor.fenetre", "on")
    await manager.async_evaluate()
    await hass.async_block_till_done()
    assert hass.states.get(STATUS).attributes["window_state"] == "open"


# --- volet fermé à 100 % : jamais remonté --------------------------------------------


async def test_closed_cover_is_not_opened_and_flag_is_cleared(hass, setup):
    manager, calls, opens, _ = setup
    hass.states.async_set("binary_sensor.expo_est", "off")
    state(hass, 0, "closed")
    manager._rt(COVER).shaded_by_us = True  # noqa: SLF001
    await manager.async_evaluate()
    assert not opens and not calls
    assert manager._rt(COVER).shaded_by_us is False  # noqa: SLF001
    assert "100 %" in hass.states.get(STATUS).attributes["reason"]


async def test_lowered_cover_is_still_opened_when_sun_leaves(hass, setup):
    manager, _, opens, _ = setup
    hass.states.async_set("binary_sensor.expo_est", "off")
    state(hass, 10)
    manager._rt(COVER).shaded_by_us = True  # noqa: SLF001
    await manager.async_evaluate()
    assert len(opens) == 1


def test_allow_open_closed_in_defaults_and_validation():
    cfg = default_config()
    cfg["covers"] = [{"entity_id": "cover.a", "facade": "sud"}]
    assert normalize_config(cfg)["covers"][0]["allow_open_closed_in"] == []
    cfg["covers"][0]["allow_open_closed_in"] = ["winter"]
    assert normalize_config(cfg)["covers"][0]["allow_open_closed_in"] == ["winter"]
    cfg["covers"][0]["allow_open_closed_in"] = ["printemps"]
    with pytest.raises(ConfigError):
        normalize_config(cfg)

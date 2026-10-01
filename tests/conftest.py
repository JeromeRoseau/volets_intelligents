"""Fixtures communes."""

from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.volets_intelligents.const import DOMAIN

from .common import COVER, FEATURES, make_config


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Autorise le chargement de custom_components/ dans les tests."""
    yield


@pytest.fixture
async def setup(hass: HomeAssistant, freezer, hass_storage, request):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.latitude = 45.58
    hass.config.longitude = 4.81
    hass.config.elevation = 200
    freezer.move_to("2026-07-15 14:00:00+02:00")
    fake = {"frontend", "panel_custom"}
    if request.node.get_closest_marker("real_http"):
        # Vrai serveur HTTP et vrai WebSocket pour les tests de l'API.
        assert await async_setup_component(hass, "http", {})
        assert await async_setup_component(hass, "websocket_api", {})
    else:
        fake.update({"http", "websocket_api"})
    hass.config.components.update(fake)
    calls = async_mock_service(hass, "cover", "set_cover_position")
    opens = async_mock_service(hass, "cover", "open_cover")

    # Configuration déjà enregistrée (sans délai de sécurité) : le démarrage ne fait rien
    # tant que le soleil n'est pas sur la façade.
    hass_storage["volets_intelligents.config"] = {
        "version": 1,
        "minor_version": 1,
        "key": "volets_intelligents.config",
        "data": make_config(),
    }
    hass.states.async_set(COVER, "open", {"current_position": 100, "supported_features": FEATURES})
    hass.states.async_set("sensor.dehors", "27")
    hass.states.async_set("sensor.piece", "23")
    hass.states.async_set("binary_sensor.expo_est", "off")
    hass.states.async_set("binary_sensor.fenetre", "off")

    entry = MockConfigEntry(domain=DOMAIN, title="Volets Intelligents")
    entry.add_to_hass(hass)
    with patch("custom_components.volets_intelligents._async_register_frontend"):
        assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    manager = entry.runtime_data
    assert not calls
    hass.states.async_set("binary_sensor.expo_est", "on")
    await hass.async_block_till_done()
    yield manager, calls, opens, entry
    if entry.state is ConfigEntryState.LOADED:
        await hass.config_entries.async_unload(entry.entry_id)

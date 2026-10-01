"""Volets Intelligents : protection thermique et solaire des volets, avec panneau de gestion."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol
from homeassistant.components import frontend as ha_frontend
from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    CARD_JS,
    CONF_SHOW_SIDEBAR,
    DOMAIN,
    PANEL_ELEMENT,
    PANEL_JS,
    PANEL_URL_PATH,
    URL_BASE,
    VERSION,
)
from .manager import VoletsManager
from .websocket_api import async_register_websocket_api

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["binary_sensor", "number", "select", "sensor", "switch", "time"]
_FRONTEND_DIR = Path(__file__).parent / "frontend"
_STATIC_KEY = f"{DOMAIN}_static_registered"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_PAUSE = "pause"
SERVICE_RESUME = "resume"
SERVICE_EVALUATE = "evaluate"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Enregistre l'API WebSocket et les services (une seule fois)."""
    async_register_websocket_api(hass)

    def manager() -> VoletsManager:
        entries = hass.config_entries.async_entries(DOMAIN)
        manager = getattr(entries[0], "runtime_data", None) if entries else None
        if manager is None:
            raise HomeAssistantError("Volets Intelligents n'est pas démarré")
        return manager

    async def pause(call: ServiceCall) -> None:
        await manager().async_pause(call.data.get("entity_id"), call.data.get("minutes"))

    async def resume(call: ServiceCall) -> None:
        await manager().async_resume(call.data.get("entity_id"))

    async def evaluate(call: ServiceCall) -> None:
        await manager().async_evaluate()

    entity_ids = vol.All(cv.ensure_list, [cv.entity_id])
    hass.services.async_register(
        DOMAIN,
        SERVICE_PAUSE,
        pause,
        schema=vol.Schema(
            {
                vol.Optional("entity_id"): entity_ids,
                vol.Optional("minutes"): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RESUME, resume, schema=vol.Schema({vol.Optional("entity_id"): entity_ids})
    )
    hass.services.async_register(DOMAIN, SERVICE_EVALUATE, evaluate, schema=vol.Schema({}))
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Charge la configuration, enregistre le panneau et démarre le gestionnaire."""
    manager = VoletsManager(hass)
    await manager.async_load()
    entry.runtime_data = manager

    await _async_register_frontend(hass, entry.options.get(CONF_SHOW_SIDEBAR, True))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await manager.async_start()
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Une option a changé (menu latéral) : recharge l'intégration pour réenregistrer le panneau."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.async_stop()
        ha_frontend.async_remove_panel(hass, PANEL_URL_PATH)
        try:
            ha_frontend.remove_extra_js_url(hass, f"{URL_BASE}/{CARD_JS}?v={VERSION}")
        except (KeyError, ValueError):  # déjà retiré
            _LOGGER.debug("Script de la carte déjà retiré")
    return unloaded


async def _async_register_frontend(hass: HomeAssistant, show_sidebar: bool = True) -> None:
    """Sert les fichiers JS, ajoute le panneau latéral et la carte Lovelace."""
    if not hass.data.get(_STATIC_KEY):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL_BASE, str(_FRONTEND_DIR), cache_headers=False)]
        )
        hass.data[_STATIC_KEY] = True

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_ELEMENT,
        frontend_url_path=PANEL_URL_PATH,
        sidebar_title="Volets" if show_sidebar else None,
        sidebar_icon="mdi:blinds-horizontal" if show_sidebar else None,
        module_url=f"{URL_BASE}/{PANEL_JS}?v={VERSION}",
        require_admin=True,
        config={},
    )
    ha_frontend.add_extra_js_url(hass, f"{URL_BASE}/{CARD_JS}?v={VERSION}")

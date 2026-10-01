"""API WebSocket utilisée par le panneau et la carte Lovelace."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.auth.permissions.const import POLICY_CONTROL
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, Unauthorized
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_STATUS_UPDATED
from .manager import VoletsManager
from .schema import ConfigError, default_config


def _manager(hass: HomeAssistant) -> VoletsManager | None:
    for entry in hass.config_entries.async_entries(DOMAIN):
        manager = getattr(entry, "runtime_data", None)
        if manager is not None:
            return manager
    return None


def _require_manager(hass: HomeAssistant, connection, msg_id: int) -> VoletsManager | None:
    manager = _manager(hass)
    if manager is None:
        connection.send_error(msg_id, "not_loaded", "Volets Intelligents n'est pas démarré")
    return manager


def _select_entity_id(hass: HomeAssistant, manager: VoletsManager, suffix: str) -> str | None:
    """Identifiant de l'entité select (mode ou scénario) d'après son unique_id."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if getattr(entry, "runtime_data", None) is manager:
            return er.async_get(hass).async_get_entity_id(
                "select", DOMAIN, f"{entry.entry_id}_{suffix}"
            )
    return None


def _check_control(connection, entity_ids: list[str | None]) -> None:
    """Exige le droit de contrôle sur chaque entité, comme pour un appel de service HA."""
    user = connection.user
    for entity_id in entity_ids:
        if entity_id and not user.permissions.check_entity(entity_id, POLICY_CONTROL):
            raise Unauthorized(entity_id=entity_id)


@callback
def async_register_websocket_api(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_get_config)
    websocket_api.async_register_command(hass, ws_set_config)
    websocket_api.async_register_command(hass, ws_get_entities)
    websocket_api.async_register_command(hass, ws_get_status)
    websocket_api.async_register_command(hass, ws_subscribe_status)
    websocket_api.async_register_command(hass, ws_command)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_config"})
@websocket_api.require_admin
@callback
def ws_get_config(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    manager = _require_manager(hass, connection, msg["id"])
    if manager:
        connection.send_result(msg["id"], {"config": manager.config, "defaults": default_config()})


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/set_config", vol.Required("config"): dict}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_set_config(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    manager = _require_manager(hass, connection, msg["id"])
    if not manager:
        return
    try:
        config = await manager.async_set_config(msg["config"])
    except ConfigError as err:
        connection.send_error(msg["id"], "invalid_config", str(err))
        return
    connection.send_result(msg["id"], {"config": config})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_entities"})
@websocket_api.require_admin
@callback
def ws_get_entities(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    """Identifiants réels des entités créées (d'après leur unique_id, donc même renommées)."""
    manager = _require_manager(hass, connection, msg["id"])
    if not manager:
        return
    entry_id = next(
        (
            entry.entry_id
            for entry in hass.config_entries.async_entries(DOMAIN)
            if getattr(entry, "runtime_data", None) is manager
        ),
        None,
    )
    registry = er.async_get(hass)

    def find(domain: str, unique_id: str) -> str | None:
        return registry.async_get_entity_id(domain, DOMAIN, f"{entry_id}_{unique_id}")

    connection.send_result(
        msg["id"],
        {
            "mode": find("select", "mode"),
            "scenario": find("select", "scenario"),
            "outdoor": find("sensor", "outdoor_effective"),
            "covers": [
                {
                    "cover": cover["entity_id"],
                    "name": cover["name"],
                    "facade": cover["facade"],
                    "switch": find("switch", f"{cover['entity_id']}_auto"),
                    "status": find("sensor", f"{cover['entity_id']}_status"),
                }
                for cover in manager.config["covers"]
            ],
        },
    )


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_status"})
@callback
def ws_get_status(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    manager = _require_manager(hass, connection, msg["id"])
    if manager:
        connection.send_result(msg["id"], {"status": manager.status})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/subscribe_status"})
@callback
def ws_subscribe_status(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    manager = _require_manager(hass, connection, msg["id"])
    if not manager:
        return

    @callback
    def forward() -> None:
        connection.send_message(websocket_api.event_message(msg["id"], manager.status))

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, SIGNAL_STATUS_UPDATED, forward
    )
    connection.send_result(msg["id"])
    if manager.status:
        forward()


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/command",
        vol.Required("command"): vol.In(
            ("set_mode", "set_scenario", "pause", "resume", "evaluate")
        ),
        vol.Optional("value"): str,
        vol.Optional("entity_id"): str,
        vol.Optional("minutes"): vol.All(int, vol.Range(min=1, max=1440)),
    }
)
@websocket_api.async_response
async def ws_command(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    manager = _require_manager(hass, connection, msg["id"])
    if not manager:
        return
    command = msg["command"]
    targets = [msg["entity_id"]] if msg.get("entity_id") else None
    # Les droits suivent ceux de Home Assistant : modifier le mode ou le scénario demande
    # le contrôle de l'entité select correspondante, pause/reprise celui des volets visés.
    if command == "set_mode":
        _check_control(connection, [_select_entity_id(hass, manager, "mode")])
    elif command == "set_scenario":
        _check_control(connection, [_select_entity_id(hass, manager, "scenario")])
    elif command in ("pause", "resume"):
        _check_control(connection, targets or sorted(manager.runtime_keys()))
    try:
        if command == "set_mode":
            await manager.async_set_mode(msg.get("value", ""))
        elif command == "set_scenario":
            await manager.async_set_scenario(msg.get("value", ""))
        elif command == "pause":
            await manager.async_pause(targets, msg.get("minutes"))
        elif command == "resume":
            await manager.async_resume(targets)
        else:
            await manager.async_evaluate()
    except HomeAssistantError as err:
        connection.send_error(msg["id"], "command_failed", str(err))
        return
    connection.send_result(msg["id"], {"ok": True})

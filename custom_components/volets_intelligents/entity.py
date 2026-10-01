"""Briques communes aux entités : abonnement et gestion dynamique des volets."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN,
    NAME,
    PANEL_URL_PATH,
    SIGNAL_CONFIG_CHANGED,
    SIGNAL_STATUS_UPDATED,
    VERSION,
)
from .manager import VoletsManager


def device_info(entry_id: str) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name=NAME,
        manufacturer="Volets Intelligents",
        model="Gestion thermique des volets",
        sw_version=VERSION,
        configuration_url=f"homeassistant://{PANEL_URL_PATH}",
    )


class VoletsEntity(Entity):
    """Entité qui se met à jour à chaque évaluation du gestionnaire."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, manager: VoletsManager, entry_id: str) -> None:
        self.manager = manager
        self._entry_id = entry_id
        self._attr_device_info = device_info(entry_id)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_STATUS_UPDATED, self.async_write_ha_state)
        )


class ManagedCoverEntity(VoletsEntity):
    """Entité liée à un volet géré (identifié par son entity_id)."""

    def __init__(self, manager: VoletsManager, entry_id: str, cover_id: str) -> None:
        super().__init__(manager, entry_id)
        self.cover_id = cover_id

    def cover_config(self) -> dict[str, Any] | None:
        return self.manager._cover_config(self.cover_id)  # noqa: SLF001

    def cover_status(self) -> dict[str, Any] | None:
        for item in self.manager.status.get("covers", []):
            if item["entity_id"] == self.cover_id:
                return item
        return None

    @property
    def available(self) -> bool:
        return self.cover_config() is not None


@callback
def async_setup_dynamic_covers(
    hass: HomeAssistant,
    manager: VoletsManager,
    entry_id: str,
    platform_domain: str,
    unique_suffix: str,
    factory: Callable[[VoletsManager, str, str], Entity],
    async_add_entities: Callable[[list[Entity]], None],
) -> Callable[[], None]:
    """Crée une entité par volet et suit les ajouts/suppressions de volets."""
    known: set[str] = set()

    @callback
    def sync() -> None:
        wanted = {c["entity_id"] for c in manager.config["covers"]}
        new = sorted(wanted - known)
        if new:
            async_add_entities([factory(manager, entry_id, cover_id) for cover_id in new])
            known.update(new)
        removed = known - wanted
        if removed:
            registry = er.async_get(hass)
            for cover_id in removed:
                unique_id = f"{entry_id}_{cover_id}_{unique_suffix}"
                entity_id = registry.async_get_entity_id(platform_domain, DOMAIN, unique_id)
                if entity_id:
                    registry.async_remove(entity_id)
            known.difference_update(removed)

    sync()
    return async_dispatcher_connect(hass, SIGNAL_CONFIG_CHANGED, sync)


class FacadeEntity(VoletsEntity):
    """Entité liée à une façade (identifiée par son id)."""

    def __init__(self, manager: VoletsManager, entry_id: str, facade_id: str) -> None:
        super().__init__(manager, entry_id)
        self.facade_id = facade_id

    def facade_config(self) -> dict[str, Any] | None:
        for facade in self.manager.config["facades"]:
            if facade["id"] == self.facade_id:
                return facade
        return None

    def facade_status(self) -> dict[str, Any] | None:
        return self.manager.status.get("facades", {}).get(self.facade_id)

    @property
    def available(self) -> bool:
        return self.facade_config() is not None

    @property
    def facade_name(self) -> str:
        facade = self.facade_config()
        return facade["name"] if facade else self.facade_id


@callback
def async_setup_dynamic_facades(
    hass: HomeAssistant,
    manager: VoletsManager,
    entry_id: str,
    platform_domain: str,
    unique_suffix: str,
    factory: Callable[[VoletsManager, str, str], Entity],
    async_add_entities: Callable[[list[Entity]], None],
) -> Callable[[], None]:
    """Crée une entité par façade et suit les ajouts/suppressions de façades."""
    known: set[str] = set()

    @callback
    def sync() -> None:
        wanted = {f["id"] for f in manager.config["facades"]}
        new = sorted(wanted - known)
        if new:
            async_add_entities([factory(manager, entry_id, facade_id) for facade_id in new])
            known.update(new)
        removed = known - wanted
        if removed:
            registry = er.async_get(hass)
            for facade_id in removed:
                unique_id = f"{entry_id}_facade_{facade_id}_{unique_suffix}"
                entity_id = registry.async_get_entity_id(platform_domain, DOMAIN, unique_id)
                if entity_id:
                    registry.async_remove(entity_id)
            known.difference_update(removed)

    sync()
    return async_dispatcher_connect(hass, SIGNAL_CONFIG_CHANGED, sync)

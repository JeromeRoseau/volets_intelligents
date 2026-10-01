"""Interrupteur « géré automatiquement » pour chaque volet."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import ManagedCoverEntity, async_setup_dynamic_covers
from .manager import VoletsManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    manager: VoletsManager = entry.runtime_data
    entry.async_on_unload(
        async_setup_dynamic_covers(
            hass, manager, entry.entry_id, "switch", "auto", CoverAutoSwitch, async_add_entities
        )
    )


class CoverAutoSwitch(ManagedCoverEntity, SwitchEntity):
    """Active ou désactive la gestion automatique d'un volet."""

    _attr_icon = "mdi:blinds-horizontal"

    def __init__(self, manager: VoletsManager, entry_id: str, cover_id: str) -> None:
        super().__init__(manager, entry_id, cover_id)
        self._attr_unique_id = f"{entry_id}_{cover_id}_auto"

    @property
    def name(self) -> str:
        cover = self.cover_config()
        return f"Volets {cover['name'] if cover else self.cover_id} auto"

    @property
    def is_on(self) -> bool:
        cover = self.cover_config()
        return bool(cover and cover["enabled"])

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.manager.async_set_cover_enabled(self.cover_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.manager.async_set_cover_enabled(self.cover_id, False)

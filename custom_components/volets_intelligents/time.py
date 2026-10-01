"""Heures réglables de la plage active (début, fin fixe)."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import VoletsEntity
from .manager import VoletsManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    manager: VoletsManager = entry.runtime_data
    async_add_entities(
        [
            WindowTime(manager, entry.entry_id, "start", "Volets réglage plage début"),
            WindowTime(manager, entry.entry_id, "end_time", "Volets réglage plage fin"),
        ]
    )


class WindowTime(VoletsEntity, TimeEntity):
    """Réglage `settings.window.<key>` (début, ou fin fixe / repli de la fin)."""

    _attr_icon = "mdi:clock-edit-outline"

    def __init__(self, manager: VoletsManager, entry_id: str, key: str, name: str) -> None:
        super().__init__(manager, entry_id)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_window_{key}"

    @property
    def native_value(self) -> time | None:
        raw = self.manager.config["settings"]["window"].get(self._key)
        try:
            hours, minutes = str(raw).split(":")[:2]
            return time(int(hours), int(minutes))
        except (TypeError, ValueError):
            return None

    async def async_set_value(self, value: time) -> None:
        await self.manager.async_set_window_setting(self._key, value.strftime("%H:%M"))

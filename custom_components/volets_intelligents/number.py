"""Décalage par rapport au coucher du soleil (fin de plage en mode « coucher du soleil »)."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import VoletsEntity
from .manager import VoletsManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([SunsetOffsetNumber(entry.runtime_data, entry.entry_id)])


class SunsetOffsetNumber(VoletsEntity, NumberEntity):
    """Minutes avant (négatif) ou après (positif) le coucher du soleil."""

    _attr_name = "Volets réglage plage décalage coucher"
    _attr_icon = "mdi:weather-sunset"
    _attr_native_min_value = -240
    _attr_native_max_value = 240
    _attr_native_step = 5
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(self, manager: VoletsManager, entry_id: str) -> None:
        super().__init__(manager, entry_id)
        self._attr_unique_id = f"{entry_id}_window_sunset_offset"

    @property
    def native_value(self) -> float:
        return self.manager.config["settings"]["window"]["sunset_offset_minutes"]

    async def async_set_native_value(self, value: float) -> None:
        await self.manager.async_set_window_setting("sunset_offset_minutes", int(value))

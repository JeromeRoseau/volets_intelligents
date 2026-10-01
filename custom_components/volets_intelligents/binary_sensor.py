"""Capteurs binaires : façades exposées au soleil et plage active."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import FacadeEntity, VoletsEntity, async_setup_dynamic_facades
from .manager import VoletsManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    manager: VoletsManager = entry.runtime_data
    async_add_entities([WindowActiveBinarySensor(manager, entry.entry_id)])
    entry.async_on_unload(
        async_setup_dynamic_facades(
            hass, manager, entry.entry_id, "binary_sensor", "exposed",
            FacadeExposedBinarySensor, async_add_entities,
        )
    )


class WindowActiveBinarySensor(VoletsEntity, BinarySensorEntity):
    """Vrai quand l'heure courante est dans la plage active."""

    _attr_name = "Volets plage active"
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, manager: VoletsManager, entry_id: str) -> None:
        super().__init__(manager, entry_id)
        self._attr_unique_id = f"{entry_id}_window_active"

    @property
    def is_on(self) -> bool | None:
        return self.manager.status.get("in_window")


class FacadeExposedBinarySensor(FacadeEntity, BinarySensorEntity):
    """Vrai quand la façade reçoit le soleil (météo comprise) ; inconnu si la donnée manque."""

    _attr_icon = "mdi:white-balance-sunny"

    def __init__(self, manager: VoletsManager, entry_id: str, facade_id: str) -> None:
        super().__init__(manager, entry_id, facade_id)
        self._attr_unique_id = f"{entry_id}_facade_{facade_id}_exposed"

    @property
    def name(self) -> str:
        return f"Volets façade {self.facade_name} exposée"

    @property
    def is_on(self) -> bool | None:
        status = self.facade_status()
        return status["exposed"] if status else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        status = self.facade_status() or {}
        return {
            "facade": self.facade_id,
            "orientation": status.get("orientation"),
            "azimuth": status.get("azimuth"),
            "source": status.get("source"),
            "windows": [f"{w['start']} – {w['end']}" for w in status.get("windows", [])],
        }

"""Capteurs : statut de chaque volet et température extérieure effective."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import STATUSES
from .entity import ManagedCoverEntity, VoletsEntity, async_setup_dynamic_covers
from .manager import VoletsManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    manager: VoletsManager = entry.runtime_data
    async_add_entities([OutdoorEffectiveSensor(manager, entry.entry_id)])
    entry.async_on_unload(
        async_setup_dynamic_covers(
            hass, manager, entry.entry_id, "sensor", "status", CoverStatusSensor, async_add_entities
        )
    )


class OutdoorEffectiveSensor(VoletsEntity, SensorEntity):
    """Température extérieure réellement utilisée par les règles."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1
    _attr_name = "Volets température extérieure effective"

    def __init__(self, manager: VoletsManager, entry_id: str) -> None:
        super().__init__(manager, entry_id)
        self._attr_unique_id = f"{entry_id}_outdoor_effective"

    @property
    def native_value(self) -> float | None:
        return self.manager.status.get("outdoor_effective")


class CoverStatusSensor(ManagedCoverEntity, SensorEntity):
    """Statut de gestion d'un volet (protégé, en pause, fenêtre ouverte…)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(STATUSES)
    _attr_translation_key = "cover_status"

    def __init__(self, manager: VoletsManager, entry_id: str, cover_id: str) -> None:
        super().__init__(manager, entry_id, cover_id)
        self._attr_unique_id = f"{entry_id}_{cover_id}_status"

    @property
    def name(self) -> str:
        cover = self.cover_config()
        return f"Volets {cover['name'] if cover else self.cover_id} statut"

    @property
    def native_value(self) -> str | None:
        status = self.cover_status()
        return status["status"] if status else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        status = self.cover_status() or {}
        return {
            "volets_intelligents": True,
            "cover": self.cover_id,
            "reason": status.get("reason"),
            "position": status.get("position"),
            "room_temp": status.get("room_temp"),
            "exposed": status.get("exposed"),
            "paused_until": status.get("paused_until"),
            "shaded_by_us": status.get("shaded_by_us"),
            "last_action": status.get("last_action"),
            "last_action_at": status.get("last_action_at"),
            "window_state": status.get("window_state"),
        }

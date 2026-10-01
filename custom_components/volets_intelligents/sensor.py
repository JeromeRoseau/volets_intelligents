"""Capteurs : statut de chaque volet et température extérieure effective."""

from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import STATUSES
from .entity import (
    FacadeEntity,
    ManagedCoverEntity,
    VoletsEntity,
    async_setup_dynamic_covers,
    async_setup_dynamic_facades,
)
from .manager import VoletsManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    manager: VoletsManager = entry.runtime_data
    async_add_entities(
        [
            OutdoorEffectiveSensor(manager, entry.entry_id),
            WindowTimeSensor(manager, entry.entry_id, "start", "Volets plage début"),
            WindowTimeSensor(manager, entry.entry_id, "end", "Volets plage fin"),
        ]
    )
    for kind, label in (("start", "début"), ("end", "fin")):
        entry.async_on_unload(
            async_setup_dynamic_facades(
                hass, manager, entry.entry_id, "sensor", kind,
                partial(FacadeTimeSensor, kind=kind, label=label),
                async_add_entities,
            )
        )
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


class WindowTimeSensor(VoletsEntity, SensorEntity):
    """Début ou fin de la plage active du moment (horodatage)."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, manager: VoletsManager, entry_id: str, kind: str, name: str) -> None:
        super().__init__(manager, entry_id)
        self._kind = kind
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_window_{kind}_at"

    @property
    def native_value(self) -> datetime | None:
        raw = self.manager.status.get(f"window_{self._kind}_at")
        return dt_util.parse_datetime(raw) if raw else None


class FacadeTimeSensor(FacadeEntity, SensorEntity):
    """Début ou fin de la plage d'ensoleillement en cours, sinon de la prochaine du jour."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:weather-sunny-alert"

    def __init__(
        self, manager: VoletsManager, entry_id: str, facade_id: str, *, kind: str, label: str
    ) -> None:
        super().__init__(manager, entry_id, facade_id)
        self._kind = kind
        self._label = label
        self._attr_unique_id = f"{entry_id}_facade_{facade_id}_{kind}"

    @property
    def name(self) -> str:
        return f"Volets façade {self.facade_name} {self._label}"

    @property
    def native_value(self) -> datetime | None:
        status = self.facade_status() or {}
        raw = status.get(f"next_{self._kind}")
        return dt_util.parse_datetime(raw) if raw else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        status = self.facade_status() or {}
        return {
            "facade": self.facade_id,
            "windows": [f"{w['start']} – {w['end']}" for w in status.get("windows", [])],
        }

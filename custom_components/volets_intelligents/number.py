"""Décalage par rapport au coucher du soleil (fin de plage en mode « coucher du soleil »)."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import VoletsEntity
from .manager import VoletsManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    manager = entry.runtime_data
    async_add_entities(
        [
            SunsetOffsetNumber(manager, entry.entry_id),
            *(
                SummerThresholdNumber(manager, entry.entry_id, key, label)
                for key, label in SUMMER_THRESHOLDS
            ),
        ]
    )


SUMMER_SCENARIO = "summer"
SUMMER_THRESHOLDS = (
    ("close_outdoor", "fermeture extérieur"),
    ("close_room", "fermeture pièce"),
    ("open_outdoor", "réouverture extérieur"),
    ("open_room", "réouverture pièce"),
)


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


class SummerThresholdNumber(VoletsEntity, NumberEntity):
    """Seuil de température du scénario « summer » (protection contre la chaleur)."""

    _attr_icon = "mdi:thermometer"
    _attr_native_min_value = 0
    _attr_native_max_value = 45
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX

    def __init__(self, manager: VoletsManager, entry_id: str, key: str, label: str) -> None:
        super().__init__(manager, entry_id)
        self._key = key
        self._attr_name = f"Volets seuil été {label}"
        self._attr_unique_id = f"{entry_id}_summer_{key}"

    @property
    def available(self) -> bool:
        scenario = self.manager.config["scenarios"].get(SUMMER_SCENARIO)
        return bool(scenario and self._key in scenario)

    @property
    def native_value(self) -> float | None:
        scenario = self.manager.config["scenarios"].get(SUMMER_SCENARIO) or {}
        return scenario.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        await self.manager.async_set_scenario_setting(SUMMER_SCENARIO, self._key, float(value))

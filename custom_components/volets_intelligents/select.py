"""Sélecteurs du mode global et du scénario."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import MODES
from .entity import VoletsEntity
from .manager import VoletsManager
from .schema import SCENARIO_KEYS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    manager: VoletsManager = entry.runtime_data
    async_add_entities(
        [ModeSelect(manager, entry.entry_id), ScenarioSelect(manager, entry.entry_id)]
    )


class ModeSelect(VoletsEntity, SelectEntity):
    """Mode global : automatique, manuel ou arrêté."""

    _attr_translation_key = "mode"
    _attr_options = list(MODES)
    _attr_icon = "mdi:auto-mode"
    _attr_name = "Volets mode"

    def __init__(self, manager: VoletsManager, entry_id: str) -> None:
        super().__init__(manager, entry_id)
        self._attr_unique_id = f"{entry_id}_mode"

    @property
    def current_option(self) -> str:
        return self.manager.mode

    async def async_select_option(self, option: str) -> None:
        await self.manager.async_set_mode(option)


class ScenarioSelect(VoletsEntity, SelectEntity):
    """Scénario actif (été, hiver, vacances, désactivé)."""

    _attr_translation_key = "scenario"
    _attr_options = list(SCENARIO_KEYS)
    _attr_icon = "mdi:weather-sunny"
    _attr_name = "Volets scénario"

    def __init__(self, manager: VoletsManager, entry_id: str) -> None:
        super().__init__(manager, entry_id)
        self._attr_unique_id = f"{entry_id}_scenario"

    @property
    def current_option(self) -> str:
        return self.manager.status.get("scenario", self.manager.scenario)

    async def async_select_option(self, option: str) -> None:
        await self.manager.async_set_scenario(option)

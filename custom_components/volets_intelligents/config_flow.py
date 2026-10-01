"""Configuration : une seule instance, tout se règle ensuite dans le panneau."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback

from .const import CONF_SHOW_SIDEBAR, DOMAIN, NAME, PANEL_URL_PATH


class VoletsIntelligentsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ajout de l'intégration."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return VoletsIntelligentsOptionsFlow()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(title=NAME, data={})
        return self.async_show_form(step_id="user")


class VoletsIntelligentsOptionsFlow(OptionsFlow):
    """Options : afficher ou masquer « Volets » dans le menu latéral, et lien vers le panneau."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(CONF_SHOW_SIDEBAR, True)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required(CONF_SHOW_SIDEBAR, default=current): bool}),
            description_placeholders={"panel_url": f"/{PANEL_URL_PATH}"},
        )

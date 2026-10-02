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
from homeassistant.helpers import selector

from .const import CONF_ALLOWED_USERS, CONF_SHOW_SIDEBAR, DOMAIN, NAME, PANEL_URL_PATH


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
        users = await self.hass.auth.async_get_users()
        choices = [
            selector.SelectOptionDict(value=user.id, label=user.name or user.id)
            for user in users
            if user.is_active and not user.system_generated and not user.is_owner and not user.is_admin
        ]
        known = {choice["value"] for choice in choices}
        designated = [
            uid for uid in (self.config_entry.options.get(CONF_ALLOWED_USERS) or []) if uid in known
        ]
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SHOW_SIDEBAR, default=current): bool,
                    vol.Optional(
                        CONF_ALLOWED_USERS, default=designated
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=choices, multiple=True, mode=selector.SelectSelectorMode.DROPDOWN
                        )
                    ),
                }
            ),
            description_placeholders={"panel_url": f"/{PANEL_URL_PATH}"},
        )

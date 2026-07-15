"""Config flow for a direct-Bluetooth C5500XK collector."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import aiohttp_client

from .api import CollectorApi, CollectorApiError
from .const import (
    CONF_ADDRESS,
    CONF_API_TOKEN,
    CONF_ENABLE_WRITES,
    CONF_HOST,
    CONF_PING_HOST,
    CONF_PING_REPETITIONS,
    CONF_PING_SIZE,
    CONF_PORT,
    CONF_SERIAL,
    DEFAULT_PORT,
    DOMAIN,
)

SERIAL_RE = re.compile(r"^(C5500XK\d+)$")
ADDRESS_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class C5500XKConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            user_input[CONF_ADDRESS] = user_input[CONF_ADDRESS].upper()
            if not ADDRESS_RE.fullmatch(user_input[CONF_ADDRESS]):
                errors["base"] = "invalid_address"
            elif not SERIAL_RE.fullmatch(user_input[CONF_SERIAL]):
                errors["base"] = "invalid_serial"
            else:
                api = CollectorApi(
                    aiohttp_client.async_get_clientsession(self.hass),
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_API_TOKEN],
                )
                try:
                    status = await api.async_status()
                    device = status.get("device", {})
                    if device.get("address", "").upper() != user_input[CONF_ADDRESS]:
                        errors["base"] = "device_mismatch"
                    elif device.get("serial") != user_input[CONF_SERIAL]:
                        errors["base"] = "device_mismatch"
                except CollectorApiError:
                    errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id(user_input[CONF_ADDRESS])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Quantum Fiber C5500XK",
                    data=user_input,
                    options={CONF_ENABLE_WRITES: False},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=(user_input or {}).get(CONF_HOST, "")): str,
                vol.Required(
                    CONF_PORT, default=(user_input or {}).get(CONF_PORT, DEFAULT_PORT)
                ): vol.Coerce(int),
                vol.Required(CONF_API_TOKEN): str,
                vol.Required(CONF_ADDRESS): str,
                vol.Required(CONF_SERIAL): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return C5500XKOptionsFlow()


class C5500XKOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_ENABLE_WRITES,
                    default=options.get(CONF_ENABLE_WRITES, False),
                ): bool,
                vol.Optional(CONF_PING_HOST, default=options.get(CONF_PING_HOST, "1.1.1.1")): str,
                vol.Optional(CONF_PING_SIZE, default=options.get(CONF_PING_SIZE, 56)): vol.All(
                    int, vol.Range(min=1, max=65500)
                ),
                vol.Optional(
                    CONF_PING_REPETITIONS,
                    default=options.get(CONF_PING_REPETITIONS, 4),
                ): vol.All(int, vol.Range(min=1, max=100)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

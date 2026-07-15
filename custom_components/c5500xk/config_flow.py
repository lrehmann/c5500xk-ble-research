"""Config flow for Quantum Fiber ONT Bluetooth."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

from .const import (
    CONF_ADDRESS,
    CONF_ENABLE_WRITES,
    CONF_PING_HOST,
    CONF_PING_REPETITIONS,
    CONF_PING_SIZE,
    CONF_SERIAL,
    DOMAIN,
)

SERIAL_RE = re.compile(r"^C5500XK\d+$")
ADDRESS_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class C5500XKConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle discovered or manually identified C5500XK devices."""

    VERSION = 3

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> config_entries.ConfigFlowResult:
        serial = discovery_info.name
        if not SERIAL_RE.fullmatch(serial):
            return self.async_abort(reason="not_supported")
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": "C5500XK"}
        self._discovery = discovery_info
        self._serial = serial
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="Quantum Fiber C5500XK",
                data={CONF_ADDRESS: self._discovery.address, CONF_SERIAL: self._serial},
                options={CONF_ENABLE_WRITES: False},
            )
        return self.async_show_form(step_id="confirm")

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            address = user_input[CONF_ADDRESS].upper()
            serial = user_input[CONF_SERIAL]
            if not ADDRESS_RE.fullmatch(address):
                errors["base"] = "invalid_address"
            elif not SERIAL_RE.fullmatch(serial):
                errors["base"] = "invalid_serial"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Quantum Fiber C5500XK",
                    data={CONF_ADDRESS: address, CONF_SERIAL: serial},
                    options={CONF_ENABLE_WRITES: False},
                )
        schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS, default=(user_input or {}).get(CONF_ADDRESS, "")): str,
                vol.Required(CONF_SERIAL, default=(user_input or {}).get(CONF_SERIAL, "")): str,
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

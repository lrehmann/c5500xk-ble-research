"""Config flow for Quantum Fiber ONT Bluetooth."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)

from .const import (
    CONF_ENABLE_WRITES,
    CONF_PING_HOST,
    CONF_PING_REPETITIONS,
    CONF_PING_SIZE,
    DOMAIN,
)

SERIAL_RE = re.compile(r"^(C5500XK\d+)$")


class C5500XKConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle discovered C5500XK devices."""

    VERSION = 1

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
                data={"address": self._discovery.address, "serial": self._serial},
                options={CONF_ENABLE_WRITES: False},
            )
        return self.async_show_form(step_id="confirm")

    async def async_step_user(self, user_input=None):
        discovered = {
            info.address: info
            for info in async_discovered_service_info(self.hass, connectable=True)
            if SERIAL_RE.fullmatch(info.name)
        }
        if not discovered:
            return self.async_abort(reason="no_devices_found")
        if user_input is not None:
            info = discovered[user_input["address"]]
            await self.async_set_unique_id(info.address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Quantum Fiber C5500XK",
                data={"address": info.address, "serial": info.name},
                options={CONF_ENABLE_WRITES: False},
            )
        labels = {address: "C5500XK" for address in discovered}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("address"): vol.In(labels)}),
        )

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

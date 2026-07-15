"""Opt-in operational write buttons for Quantum Fiber ONT Bluetooth."""

from dataclasses import dataclass

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity, ButtonEntityDescription
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_ENABLE_WRITES,
    CONF_PING_HOST,
    CONF_PING_REPETITIONS,
    CONF_PING_SIZE,
    DOMAIN,
)
from .entity import C5500XKEntity


@dataclass(frozen=True, kw_only=True)
class C5500XKButtonDescription(ButtonEntityDescription):
    destructive: bool = False


DESCRIPTIONS = (
    C5500XKButtonDescription(key="wan_release_renew", name="Release and renew WAN address"),
    C5500XKButtonDescription(key="run_ping", name="Run ping diagnostic"),
    C5500XKButtonDescription(key="reboot", name="Reboot", device_class=ButtonDeviceClass.RESTART),
    C5500XKButtonDescription(key="reset_ppp", name="Reset PPP credentials", destructive=True),
    C5500XKButtonDescription(key="factory_reset", name="Factory reset", destructive=True),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(C5500XKButton(coordinator, entry, item) for item in DESCRIPTIONS)


class C5500XKButton(C5500XKEntity, ButtonEntity):
    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator, description.key)
        self.entry = entry
        self.entity_description = description
        self._attr_entity_registry_enabled_default = False

    @property
    def available(self):
        return self.coordinator.last_update_success and self.entry.options.get(
            CONF_ENABLE_WRITES, False
        )

    async def async_press(self) -> None:
        if not self.entry.options.get(CONF_ENABLE_WRITES, False):
            raise HomeAssistantError("Write actions are disabled in integration options")
        if self.entity_key == "run_ping":
            options = self.entry.options
            parameters = {
                "host": options.get(CONF_PING_HOST, "1.1.1.1"),
                "size": options.get(CONF_PING_SIZE, 56),
                "repetitions": options.get(CONF_PING_REPETITIONS, 4),
            }
        else:
            parameters = {}
        await self.coordinator.async_action(self.entity_key, parameters)
        await self.coordinator.async_request_refresh()

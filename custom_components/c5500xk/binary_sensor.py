"""Binary sensors for Quantum Fiber ONT Bluetooth."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .entity import C5500XKEntity

DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="authenticated",
        name="Application authenticated",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="ethernet_wan_up",
        name="Ethernet WAN",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(C5500XKBinarySensor(coordinator, item) for item in DESCRIPTIONS)


class C5500XKBinarySensor(C5500XKEntity, BinarySensorEntity):
    def __init__(self, coordinator, description):
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self):
        value = self.coordinator.data.get(self.entity_key)
        return value if isinstance(value, bool) else str(value).lower() in {"1", "true", "up"}

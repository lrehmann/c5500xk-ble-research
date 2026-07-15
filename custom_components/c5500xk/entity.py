"""Base entity for Quantum Fiber ONT Bluetooth."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class C5500XKEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, key: str) -> None:
        super().__init__(coordinator)
        self.entity_key = key
        self._attr_unique_id = f"{coordinator.address}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
            name="Quantum Fiber C5500XK",
            manufacturer="Gemtek Technology Co., Ltd.",
            model="C5500XK",
            sw_version=(coordinator.data or {}).get("software_version"),
            hw_version=(coordinator.data or {}).get("hardware_version"),
        )

    @property
    def available(self) -> bool:
        return super().available and self.entity_key in self.coordinator.data

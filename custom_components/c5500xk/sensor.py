"""Sensors for Quantum Fiber ONT Bluetooth."""

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfInformation, UnitOfTime

from .const import DOMAIN
from .entity import C5500XKEntity


@dataclass(frozen=True, kw_only=True)
class C5500XKSensorDescription(SensorEntityDescription):
    pass


DESCRIPTIONS = (
    C5500XKSensorDescription(key="wan_status", name="WAN status"),
    C5500XKSensorDescription(key="pon_status", name="PON status"),
    C5500XKSensorDescription(
        key="rx_optical",
        name="Receive optical power",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    C5500XKSensorDescription(
        key="rx_lower", name="Receive optical lower threshold", native_unit_of_measurement="dBm"
    ),
    C5500XKSensorDescription(
        key="rx_upper", name="Receive optical upper threshold", native_unit_of_measurement="dBm"
    ),
    C5500XKSensorDescription(
        key="tx_optical",
        name="Transmit optical power",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    C5500XKSensorDescription(
        key="tx_lower", name="Transmit optical lower threshold", native_unit_of_measurement="dBm"
    ),
    C5500XKSensorDescription(
        key="tx_upper", name="Transmit optical upper threshold", native_unit_of_measurement="dBm"
    ),
    C5500XKSensorDescription(
        key="link_uptime",
        name="WAN link uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    C5500XKSensorDescription(
        key="pon_last_change",
        name="PON status age",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
    ),
    C5500XKSensorDescription(
        key="packets_sent", name="IPv4 packets sent", state_class=SensorStateClass.TOTAL_INCREASING
    ),
    C5500XKSensorDescription(
        key="packets_received",
        name="IPv4 packets received",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    C5500XKSensorDescription(
        key="bytes_sent",
        name="PON bytes sent",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    C5500XKSensorDescription(
        key="bytes_received",
        name="PON bytes received",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    C5500XKSensorDescription(
        key="bip_errors", name="PON BIP errors", state_class=SensorStateClass.TOTAL_INCREASING
    ),
    C5500XKSensorDescription(
        key="errors_sent", name="PON errors sent", state_class=SensorStateClass.TOTAL_INCREASING
    ),
    C5500XKSensorDescription(
        key="errors_received",
        name="PON errors received",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    C5500XKSensorDescription(
        key="discards_sent",
        name="PON discarded packets sent",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    C5500XKSensorDescription(
        key="discards_received",
        name="PON discarded packets received",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    C5500XKSensorDescription(key="ping_state", name="Ping diagnostic state"),
    C5500XKSensorDescription(key="ping_success", name="Ping success count"),
    C5500XKSensorDescription(key="ping_failure", name="Ping failure count"),
    C5500XKSensorDescription(
        key="ping_average",
        name="Ping average response time",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
    ),
    C5500XKSensorDescription(
        key="ping_maximum",
        name="Ping maximum response time",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
    ),
    C5500XKSensorDescription(
        key="ping_minimum",
        name="Ping minimum response time",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
    ),
    C5500XKSensorDescription(
        key="rssi",
        name="Bluetooth signal",
        native_unit_of_measurement="dBm",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    C5500XKSensorDescription(key="collector", name="Collector state"),
    C5500XKSensorDescription(key="adapter", name="Bluetooth adapter"),
    C5500XKSensorDescription(key="last_error", name="Last collector error"),
    C5500XKSensorDescription(
        key="last_success", name="Last successful update", device_class=SensorDeviceClass.TIMESTAMP
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(C5500XKSensor(coordinator, description) for description in DESCRIPTIONS)


class C5500XKSensor(C5500XKEntity, SensorEntity):
    def __init__(self, coordinator, description):
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_key)

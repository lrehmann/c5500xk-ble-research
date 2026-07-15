"""Constants for the Quantum Fiber ONT Bluetooth integration."""

from datetime import timedelta

DOMAIN = "c5500xk"
PLATFORMS = ["binary_sensor", "button", "sensor"]
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

CONF_ADDRESS = "address"
CONF_SERIAL = "serial"
AUTH_PREFIX = b"J6rV^ntpNGFpk^ruk7FXhPKh5ak@3A6P"
STRING_KEYS = {
    "serial",
    "hardware_version",
    "software_version",
    "wan_status",
    "pon_fsan",
    "pon_status",
    "ping_state",
}
SIGNED_MILLI_KEYS = {"rx_optical", "rx_lower", "rx_upper", "tx_optical", "tx_lower", "tx_upper"}

AUTH_UUID = "b5ef5c81-e7ec-412d-8d3b-a22bfd5f0bf1"

UUIDS = {
    "serial": "b5ee5c81-e7ec-412d-8d3b-a22bfd5f0bf1",
    "hardware_version": "b5ee5c82-e7ec-412d-8d3b-a22bfd5f0bf1",
    "software_version": "b5ee5c83-e7ec-412d-8d3b-a22bfd5f0bf1",
    "wan_status": "b5ee5c85-e7ec-412d-8d3b-a22bfd5f0bf1",
    "ethernet_wan_up": "b5f05c84-e7ec-412d-8d3b-a22bfd5f0bf1",
    "packets_sent": "b5f15c83-e7ec-412d-8d3b-a22bfd5f0bf1",
    "packets_received": "b5f15c84-e7ec-412d-8d3b-a22bfd5f0bf1",
    "link_uptime": "b5f15c85-e7ec-412d-8d3b-a22bfd5f0bf1",
    "pon_fsan": "4d86d957-7fc1-43ac-8fab-a6a7f03b9b58",
    "pon_status": "4d84d951-7fc1-43ac-8fab-a6a7f03b9b58",
    "pon_last_change": "4d85d950-7fc1-43ac-8fab-a6a7f03b9b58",
    "rx_optical": "4d85d951-7fc1-43ac-8fab-a6a7f03b9b58",
    "rx_lower": "4d85d952-7fc1-43ac-8fab-a6a7f03b9b58",
    "rx_upper": "4d85d953-7fc1-43ac-8fab-a6a7f03b9b58",
    "tx_optical": "4d85d954-7fc1-43ac-8fab-a6a7f03b9b58",
    "tx_lower": "4d85d955-7fc1-43ac-8fab-a6a7f03b9b58",
    "tx_upper": "4d85d956-7fc1-43ac-8fab-a6a7f03b9b58",
    "bip_errors": "4d86d950-7fc1-43ac-8fab-a6a7f03b9b58",
    "bytes_sent": "4d86d951-7fc1-43ac-8fab-a6a7f03b9b58",
    "bytes_received": "4d86d952-7fc1-43ac-8fab-a6a7f03b9b58",
    "errors_sent": "4d86d953-7fc1-43ac-8fab-a6a7f03b9b58",
    "errors_received": "4d86d954-7fc1-43ac-8fab-a6a7f03b9b58",
    "discards_sent": "4d86d955-7fc1-43ac-8fab-a6a7f03b9b58",
    "discards_received": "4d86d956-7fc1-43ac-8fab-a6a7f03b9b58",
    "ping_state": "5544cede-014f-4118-9bc4-f47747172711",
    "ping_success": "5544cedf-014f-4118-9bc4-f47747172711",
    "ping_failure": "5544cee0-014f-4118-9bc4-f47747172711",
    "ping_average": "5544cee1-014f-4118-9bc4-f47747172711",
    "ping_maximum": "5544cee2-014f-4118-9bc4-f47747172711",
    "ping_minimum": "5544cee3-014f-4118-9bc4-f47747172711",
}

WRITE_UUIDS = {
    "reboot": "5541ceda-014f-4118-9bc4-f47747172711",
    "factory_reset": "5542ceda-014f-4118-9bc4-f47747172711",
    "wan_release_renew": "5543ceda-014f-4118-9bc4-f47747172711",
    "reset_ppp": "5543cedb-014f-4118-9bc4-f47747172711",
    "ping_host": "5544ceda-014f-4118-9bc4-f47747172711",
    "ping_size": "5544cedb-014f-4118-9bc4-f47747172711",
    "ping_repetitions": "5544cedc-014f-4118-9bc4-f47747172711",
    "ping_state": UUIDS["ping_state"],
}

CONF_ENABLE_WRITES = "enable_write_actions"
CONF_PING_HOST = "ping_host"
CONF_PING_SIZE = "ping_size"
CONF_PING_REPETITIONS = "ping_repetitions"

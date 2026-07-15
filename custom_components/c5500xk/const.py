"""Constants for the Quantum Fiber ONT collector integration."""

from datetime import timedelta

DOMAIN = "c5500xk"
PLATFORMS = ["binary_sensor", "button", "sensor"]
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

CONF_HOST = "host"
CONF_PORT = "port"
CONF_API_TOKEN = "api_token"
CONF_ADDRESS = "address"
CONF_SERIAL = "serial"
DEFAULT_PORT = 8755
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

CONF_ENABLE_WRITES = "enable_write_actions"
CONF_PING_HOST = "ping_host"
CONF_PING_SIZE = "ping_size"
CONF_PING_REPETITIONS = "ping_repetitions"

"""Quantum Fiber ONT Bluetooth integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF_ADDRESS, CONF_SERIAL, DOMAIN, PLATFORMS
from .coordinator import C5500XKCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = C5500XKCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _remove_collector_entities(hass, coordinator.address)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    hass.async_create_task(
        coordinator.async_refresh(),
        f"Initial C5500XK Bluetooth refresh {coordinator.address}",
    )
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove the retired collector API settings while preserving device identity."""
    if entry.version > 3:
        return False
    if entry.version < 3:
        if CONF_ADDRESS not in entry.data or CONF_SERIAL not in entry.data:
            return False
        hass.config_entries.async_update_entry(
            entry,
            data={CONF_ADDRESS: entry.data[CONF_ADDRESS], CONF_SERIAL: entry.data[CONF_SERIAL]},
            version=3,
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _remove_collector_entities(hass: HomeAssistant, address: str) -> None:
    """Remove entities that existed only for the retired external collector."""
    registry = er.async_get(hass)
    for platform, key in (
        ("sensor", "collector"),
        ("sensor", "adapter"),
        ("sensor", "last_error"),
        ("binary_sensor", "writes_allowed"),
    ):
        if entity_id := registry.async_get_entity_id(platform, DOMAIN, f"{address}_{key}"):
            registry.async_remove(entity_id)

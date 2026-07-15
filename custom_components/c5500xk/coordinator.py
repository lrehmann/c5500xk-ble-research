"""Polling coordinator for the direct-Bluetooth collector API."""

from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CollectorApi, CollectorApiError
from .const import (
    CONF_ADDRESS,
    CONF_API_TOKEN,
    CONF_HOST,
    CONF_PORT,
    CONF_SERIAL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class C5500XKCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"C5500XK collector {entry.data[CONF_HOST]}",
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )
        self.entry = entry
        self.address = entry.data[CONF_ADDRESS]
        self.serial = entry.data[CONF_SERIAL]
        self.api = CollectorApi(
            aiohttp_client.async_get_clientsession(hass),
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
            entry.data[CONF_API_TOKEN],
        )

    async def _async_update_data(self) -> dict:
        try:
            status = await self.api.async_status()
        except CollectorApiError as err:
            raise UpdateFailed(str(err)) from err

        device = status.get("device", {})
        if device.get("address", "").upper() != self.address.upper():
            raise UpdateFailed("Collector returned a different Bluetooth address")
        if device.get("serial") != self.serial:
            raise UpdateFailed("Collector returned a different device serial")

        data = dict(device.get("data") or {})
        collector = status.get("collector", {})
        data.update(
            collector=entry
            if isinstance((entry := collector.get("state")), str)
            else "unknown",
            adapter=collector.get("adapter"),
            last_attempt=_parse_datetime(collector.get("last_attempt")),
            last_success=_parse_datetime(collector.get("last_success")),
            last_error=collector.get("last_error"),
            authenticated=bool(collector.get("authenticated")),
        )
        return data

    async def async_action(self, action: str, parameters: dict | None = None) -> None:
        try:
            await self.api.async_action(action, parameters or {})
        except CollectorApiError as err:
            raise HomeAssistantError(str(err)) from err


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None

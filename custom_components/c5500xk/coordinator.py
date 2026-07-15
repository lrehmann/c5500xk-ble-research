"""Bluetooth coordinator for Quantum Fiber ONTs."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime

from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothScanningMode,
    async_last_service_info,
    async_register_callback,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import AUTH_UUID, CONF_ADDRESS, CONF_SERIAL, DEFAULT_SCAN_INTERVAL, UUIDS
from .protocol import build_auth_payload, decode_value, parse_advertisement_token

_LOGGER = logging.getLogger(__name__)
_CRITICAL_READS = ("pon_status", "rx_optical")


class C5500XKCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"C5500XK {entry.data[CONF_ADDRESS]}",
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )
        self.entry = entry
        self.address = entry.data[CONF_ADDRESS]
        self.serial = entry.data[CONF_SERIAL]
        self.data = {"authenticated": False}
        self._operation_lock = asyncio.Lock()
        self._advertisement_event = asyncio.Event()
        self._advertisement_refresh_task: asyncio.Task | None = None
        self._service_info = async_last_service_info(hass, self.address, connectable=True)
        entry.async_on_unload(
            async_register_callback(
                hass,
                self._async_advertisement,
                BluetoothCallbackMatcher(address=self.address),
                BluetoothScanningMode.PASSIVE,
            )
        )

    def _async_advertisement(self, service_info, change) -> None:
        """Keep the current raw token and retry on each available connection window."""
        self._service_info = service_info
        self._advertisement_event.set()
        if self._operation_lock.locked():
            return
        if (
            self._advertisement_refresh_task is not None
            and not self._advertisement_refresh_task.done()
        ):
            return
        self._advertisement_refresh_task = self.hass.async_create_task(
            self._async_refresh_from_advertisement(),
            f"C5500XK advertisement refresh {self.address}",
        )

    async def _async_refresh_from_advertisement(self) -> None:
        """Request a coordinator refresh without blocking the Bluetooth callback."""
        await self.async_request_refresh()

    async def _connection_inputs(self):
        service_info = self._service_info
        if (
            service_info is None
            or service_info.raw is None
            or time.monotonic() - service_info.time > 5
        ):
            self._advertisement_event.clear()
            try:
                async with asyncio.timeout(20):
                    await self._advertisement_event.wait()
            except TimeoutError as err:
                raise UpdateFailed("No fresh connectable advertisement received") from err
            service_info = self._service_info
        if service_info is None or service_info.raw is None:
            raise UpdateFailed("Fresh advertisement did not include raw data")
        token = parse_advertisement_token(service_info.raw)
        if (device := service_info.device) is None:
            raise UpdateFailed("Device is not currently available through a Bluetooth proxy")
        return device, token, service_info.rssi, service_info.source

    async def _connect_authenticated(self):
        device, token, rssi, source = await self._connection_inputs()
        client = await establish_connection(
            BleakClientWithServiceCache,
            device,
            self.serial,
            max_attempts=1,
            pair=True,
            use_services_cache=True,
        )
        try:
            await client.write_gatt_char(
                AUTH_UUID,
                build_auth_payload(self.serial, token),
                response=False,
            )
        except Exception:
            await client.disconnect()
            raise
        return client, rssi, source

    async def _async_update_data(self) -> dict:
        async with self._operation_lock:
            try:
                client, rssi, source = await self._connect_authenticated()
                try:
                    data, read_errors = {}, {}
                    read_order = (
                        *_CRITICAL_READS,
                        *(key for key in UUIDS if key not in _CRITICAL_READS),
                    )
                    for key in read_order:
                        try:
                            data[key] = decode_value(
                                key, await client.read_gatt_char(UUIDS[key])
                            )
                        except Exception as err:
                            read_errors[key] = str(err)
                            _LOGGER.debug("Unable to read %s: %s", key, err)
                    if not all(key in data for key in _CRITICAL_READS):
                        first_error = next(iter(read_errors.values()), "no protected values")
                        raise UpdateFailed(
                            "Application authentication did not yield protected PON data: "
                            f"{first_error}"
                        )
                    data.update(
                        rssi=rssi,
                        proxy=source,
                        last_success=datetime.now().astimezone(),
                        authenticated=True,
                    )
                    return data
                finally:
                    await client.disconnect()
            except UpdateFailed:
                raise
            except Exception as err:
                raise UpdateFailed(f"Bluetooth update failed: {err}") from err

    async def async_write(self, writes: list[tuple[str, bytes]]) -> None:
        """Authenticate and perform an explicitly requested write sequence."""
        async with self._operation_lock:
            try:
                client, _, _ = await self._connect_authenticated()
                try:
                    for uuid, payload in writes:
                        await client.write_gatt_char(uuid, payload, response=False)
                finally:
                    await client.disconnect()
            except Exception as err:
                raise HomeAssistantError(f"Bluetooth write failed: {err}") from err

#!/usr/bin/env python3
"""Direct-BlueZ C5500XK collector and authenticated local HTTP API."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import signal
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from bleak import BleakClient, BleakScanner

VERSION = "0.1.0"
AUTH_PREFIX = b"J6rV^ntpNGFpk^ruk7FXhPKh5ak@3A6P"
AUTH_UUID = "b5ef5c81-e7ec-412d-8d3b-a22bfd5f0bf1"
SERIAL_RE = re.compile(r"^C5500XK\d+$")

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
ACTIONS = {"wan_release_renew", "run_ping", "reboot", "reset_ppp", "factory_reset"}


def now() -> str:
    return datetime.now(UTC).isoformat()


def token_from_manufacturer_data(data: dict[int, bytes]) -> bytes:
    for company_id, value in data.items():
        token = int(company_id).to_bytes(2, "little") + bytes(value)
        if len(token) == 8 and token.endswith(b"01"):
            return token
    raise ValueError("current eight-byte manufacturer token not found")


def build_auth_payload(serial: str, token: bytes, nonce: bytes | None = None) -> bytes:
    if len(token) != 8:
        raise ValueError("advertisement token must be eight bytes")
    nonce = nonce or os.urandom(32)
    if len(nonce) != 32:
        raise ValueError("nonce must be 32 bytes")
    return hashlib.sha256(AUTH_PREFIX + serial.encode("ascii") + token).digest() + nonce


def decode_value(key: str, value: bytes) -> Any:
    if key in STRING_KEYS:
        return value.rstrip(b"\x00").decode("utf-8", errors="replace")
    if key in SIGNED_MILLI_KEYS:
        return int.from_bytes(value, "little", signed=True) / 1000
    return int.from_bytes(value, "little", signed=False)


@dataclass(frozen=True)
class Config:
    address: str
    serial: str
    api_token: str
    adapter: str = "hci1"
    listen_host: str = "0.0.0.0"
    listen_port: int = 8755
    poll_interval: int = 300
    scan_timeout: int = 30
    allow_writes: bool = False

    @classmethod
    def load(cls, path: Path) -> Config:
        raw = json.loads(path.read_text())
        config = cls(**raw)
        if not SERIAL_RE.fullmatch(config.serial):
            raise ValueError("serial must be a C5500XK serial")
        if not config.api_token:
            raise ValueError("api_token must not be empty")
        return config


@dataclass
class State:
    state: str = "starting"
    authenticated: bool = False
    last_attempt: str | None = None
    last_success: str | None = None
    last_error: str | None = None
    rssi: int | None = None
    data: dict[str, Any] = field(default_factory=dict)
    lock: threading.RLock = field(default_factory=threading.RLock)


class Collector:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.state = State()
        self._operation_lock = asyncio.Lock()

    def snapshot(self) -> dict[str, Any]:
        with self.state.lock:
            device_data = dict(self.state.data)
            if self.state.rssi is not None:
                device_data["rssi"] = self.state.rssi
            return {
                "ok": True,
                "collector": {
                    "version": VERSION,
                    "adapter": self.config.adapter,
                    "state": self.state.state,
                    "authenticated": self.state.authenticated,
                    "last_attempt": self.state.last_attempt,
                    "last_success": self.state.last_success,
                    "last_error": self.state.last_error,
                    "writes_allowed": self.config.allow_writes,
                },
                "device": {
                    "model": "C5500XK",
                    "address": self.config.address,
                    "serial": self.config.serial,
                    "data": device_data,
                },
            }

    async def poll_forever(self) -> None:
        while True:
            try:
                await self.refresh()
            except Exception as err:
                logging.warning("Bluetooth refresh did not complete: %s", err)
            await asyncio.sleep(self.config.poll_interval)

    async def refresh(self) -> None:
        async with self._operation_lock:
            self._mark_attempt("scanning")
            try:
                device, token, rssi = await self._find_device()
                async with BleakClient(
                    device,
                    adapter=self.config.adapter,
                    pair=True,
                    timeout=30,
                ) as client:
                    await client.write_gatt_char(
                        AUTH_UUID,
                        build_auth_payload(self.config.serial, token),
                        response=False,
                    )
                    data, errors = {}, {}
                    for key, uuid in UUIDS.items():
                        try:
                            data[key] = decode_value(key, await client.read_gatt_char(uuid))
                        # One unsupported value must not erase all readings.
                        except Exception as err:
                            errors[key] = str(err)
                    if "pon_status" not in data or "rx_optical" not in data:
                        detail = next(iter(errors.values()), "protected values unavailable")
                        raise RuntimeError(f"application authentication failed: {detail}")
                with self.state.lock:
                    self.state.state = "ready"
                    self.state.authenticated = True
                    self.state.last_success = now()
                    self.state.last_error = None
                    self.state.rssi = rssi
                    self.state.data = data
            except Exception as err:
                with self.state.lock:
                    self.state.state = "waiting_for_advertisement"
                    self.state.authenticated = False
                    self.state.last_error = str(err)
                raise

    async def action(self, name: str, parameters: dict[str, Any]) -> None:
        if name not in ACTIONS:
            raise ValueError("unknown action")
        if not self.config.allow_writes:
            raise PermissionError("operational writes are disabled in collector configuration")
        writes = self._action_writes(name, parameters)
        async with self._operation_lock:
            device, token, _ = await self._find_device()
            async with BleakClient(
                device,
                adapter=self.config.adapter,
                pair=True,
                timeout=30,
            ) as client:
                await client.write_gatt_char(
                    AUTH_UUID,
                    build_auth_payload(self.config.serial, token),
                    response=False,
                )
                for uuid, payload in writes:
                    await client.write_gatt_char(uuid, payload, response=False)

    def _action_writes(self, name: str, parameters: dict[str, Any]) -> list[tuple[str, bytes]]:
        if name != "run_ping":
            return [(WRITE_UUIDS[name], b"\x01")]
        host = str(parameters.get("host", "1.1.1.1"))
        size = int(parameters.get("size", 56))
        repetitions = int(parameters.get("repetitions", 4))
        if not host or len(host.encode()) > 255:
            raise ValueError("invalid ping host")
        if not 1 <= size <= 65500 or not 1 <= repetitions <= 100:
            raise ValueError("invalid ping parameters")
        return [
            (WRITE_UUIDS["ping_host"], host.encode()),
            (WRITE_UUIDS["ping_size"], size.to_bytes(4, "little")),
            (WRITE_UUIDS["ping_repetitions"], repetitions.to_bytes(4, "little")),
            (WRITE_UUIDS["ping_state"], b"Requested"),
        ]

    async def _find_device(self):
        found: asyncio.Future = asyncio.get_running_loop().create_future()

        def callback(device, advertisement) -> None:
            name = advertisement.local_name or device.name or ""
            if device.address.upper() != self.config.address.upper() and name != self.config.serial:
                return
            try:
                token = token_from_manufacturer_data(advertisement.manufacturer_data)
            except ValueError:
                return
            if not found.done():
                found.set_result((device, token, advertisement.rssi))

        scanner = BleakScanner(callback, adapter=self.config.adapter)
        try:
            async with scanner:
                async with asyncio.timeout(self.config.scan_timeout):
                    return await found
        except TimeoutError as err:
            raise RuntimeError("no current advertisement from configured ONT") from err

    def _mark_attempt(self, state: str) -> None:
        with self.state.lock:
            self.state.state = state
            self.state.last_attempt = now()
            self.state.last_error = None


class ApiHandler(BaseHTTPRequestHandler):
    server: ApiServer

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(HTTPStatus.OK, {"ok": True, "version": VERSION})
            return
        if not self._authorized():
            return
        if self.path == "/v1/status":
            self._json(HTTPStatus.OK, self.server.collector.snapshot())
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:
        if not self._authorized():
            return
        prefix = "/v1/actions/"
        if not self.path.startswith(prefix):
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            parameters = json.loads(self.rfile.read(length) or b"{}")
            future = asyncio.run_coroutine_threadsafe(
                self.server.collector.action(self.path[len(prefix) :], parameters),
                self.server.loop,
            )
            future.result(timeout=75)
            self._json(HTTPStatus.ACCEPTED, {"ok": True})
        except PermissionError as err:
            self._json(HTTPStatus.FORBIDDEN, {"error": str(err)})
        except (ValueError, json.JSONDecodeError) as err:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(err)})
        except Exception as err:
            self._json(HTTPStatus.CONFLICT, {"error": str(err)})

    def log_message(self, message: str, *args) -> None:
        logging.info("API %s - %s", self.address_string(), message % args)

    def _authorized(self) -> bool:
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {self.server.collector.config.api_token}"
        if hmac.compare_digest(supplied, expected):
            return True
        self._json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
        return False

    def _json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class ApiServer(ThreadingHTTPServer):
    def __init__(self, collector: Collector, loop: asyncio.AbstractEventLoop) -> None:
        self.collector = collector
        self.loop = loop
        super().__init__((collector.config.listen_host, collector.config.listen_port), ApiHandler)


async def async_main(config_path: Path) -> None:
    config = Config.load(config_path)
    collector = Collector(config)
    loop = asyncio.get_running_loop()
    server = ApiServer(collector, loop)
    api_thread = threading.Thread(target=server.serve_forever, name="collector-api", daemon=True)
    api_thread.start()
    logging.info("Collector API listening on %s:%d", config.listen_host, config.listen_port)
    try:
        await collector.poll_forever()
    finally:
        server.shutdown()
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt))
    try:
        asyncio.run(async_main(args.config))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

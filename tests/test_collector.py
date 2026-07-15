"""Unit tests for the standalone BlueZ collector's pure logic."""

import asyncio
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

fake_bleak = ModuleType("bleak")
fake_bleak.BleakClient = object
fake_bleak.BleakScanner = object
sys.modules.setdefault("bleak", fake_bleak)

path = Path(__file__).parents[1] / "collector" / "c5500xk_collector.py"
spec = importlib.util.spec_from_file_location("c5500xk_collector", path)
collector = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = collector
spec.loader.exec_module(collector)


def test_reconstructs_full_manufacturer_token() -> None:
    assert collector.token_from_manufacturer_data({0x453B: bytes.fromhex("372930733031")}) == (
        bytes.fromhex("3b45372930733031")
    )


def test_auth_payload_matches_protocol_vector() -> None:
    serial = "C5500XK0000000000"
    token = bytes.fromhex("3b45372930733031")
    nonce = bytes(range(32))
    payload = collector.build_auth_payload(serial, token, nonce)
    assert payload.hex() == (
        "930f808f2b3680bd32cd22c87cbbbbcc737fa45621930231e0325146de0e0b99"
        "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
    )


def test_writes_are_disabled_in_sample_config() -> None:
    config = collector.Config.load(
        Path(__file__).parents[1] / "collector" / "config.example.json"
    )
    assert config.allow_writes is False
    assert config.retry_interval == 2
    assert collector.Collector(config).snapshot()["collector"]["writes_allowed"] is False


def test_ping_write_encoding() -> None:
    config = collector.Config(
        address="00:11:22:33:44:55",
        serial="C5500XK0000000000",
        api_token="test",
    )
    instance = collector.Collector(config)
    writes = instance._action_writes(
        "run_ping", {"host": "1.1.1.1", "size": 56, "repetitions": 4}
    )
    assert writes[0][1] == b"1.1.1.1"
    assert writes[1][1] == b"\x38\x00\x00\x00"
    assert writes[2][1] == b"\x04\x00\x00\x00"
    assert writes[3][1] == b"Requested"


def test_failed_scan_uses_short_retry_interval() -> None:
    config = collector.Config(
        address="00:11:22:33:44:55",
        serial="C5500XK0000000000",
        api_token="test",
        poll_interval=300,
        retry_interval=2,
    )
    instance = collector.Collector(config)
    delays = []

    async def failed_refresh() -> None:
        raise RuntimeError("no advertisement")

    async def capture_delay(delay: int) -> None:
        delays.append(delay)
        raise StopAsyncIteration

    instance.refresh = failed_refresh
    instance._sleep = capture_delay

    async def run_once() -> None:
        try:
            await instance.poll_forever()
        except StopAsyncIteration:
            return
        raise AssertionError("collector loop did not stop after captured delay")

    asyncio.run(run_once())
    assert delays == [2]

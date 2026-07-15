"""Protocol regression tests using anonymized, synthetic values."""

import hashlib
import sys
from pathlib import Path
from types import ModuleType

import pytest

# Load the pure protocol modules without importing Home Assistant-dependent
# integration setup code.
package = ModuleType("custom_components.c5500xk")
package.__path__ = [str(Path(__file__).parents[1] / "custom_components" / "c5500xk")]
sys.modules.setdefault("custom_components.c5500xk", package)

from custom_components.c5500xk.const import AUTH_PREFIX
from custom_components.c5500xk.protocol import (
    build_auth_payload,
    decode_value,
    encode_bool,
    encode_u32,
    parse_advertisement_token,
)


def test_parse_current_raw_advertisement_token() -> None:
    raw = bytes.fromhex("12094335353030584b3030303030303030303009ff4142434445463031")
    assert parse_advertisement_token(raw) == b"ABCDEF01"


def test_parse_rejects_aggregated_or_truncated_data() -> None:
    with pytest.raises(ValueError):
        parse_advertisement_token(bytes.fromhex("09ff414243"))
    with pytest.raises(ValueError):
        parse_advertisement_token(bytes.fromhex("09ff4142434445463032"))


def test_build_auth_payload() -> None:
    serial = "C5500XK0000000000"
    token = b"ABCDEF01"
    nonce = bytes(range(32))
    payload = build_auth_payload(serial, token, nonce)
    expected = hashlib.sha256(AUTH_PREFIX + serial.encode() + token).digest()
    assert payload == expected + nonce
    assert len(payload) == 64


@pytest.mark.parametrize(
    ("key", "raw", "expected"),
    [
        ("pon_status", b"Up\x00", "Up"),
        ("packets_sent", b"\x78\x56\x34\x12", 0x12345678),
        ("rx_optical", (-18326).to_bytes(4, "little", signed=True), -18.326),
    ],
)
def test_decode_value(key, raw, expected) -> None:
    assert decode_value(key, raw) == expected


def test_write_encodings() -> None:
    assert encode_bool() == b"\x01"
    assert encode_u32(4) == b"\x04\x00\x00\x00"
    with pytest.raises(ValueError):
        encode_u32(-1)

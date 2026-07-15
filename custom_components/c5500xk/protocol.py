"""Pure protocol helpers for C5500XK-family Bluetooth data."""

from __future__ import annotations

import hashlib
import os

from .const import AUTH_PREFIX, SIGNED_MILLI_KEYS, STRING_KEYS


def parse_advertisement_token(raw: bytes) -> bytes:
    """Return the current eight-byte manufacturer token from raw AD structures."""
    offset = 0
    while offset < len(raw):
        length = raw[offset]
        if length == 0:
            break
        end = offset + length + 1
        if end > len(raw):
            raise ValueError("truncated Bluetooth advertisement")
        if length >= 2 and raw[offset + 1] == 0xFF:
            token = raw[offset + 2 : end]
            if len(token) == 8 and token.endswith(b"01"):
                return token
        offset = end
    raise ValueError("current eight-byte manufacturer token not found")


def build_auth_payload(serial: str, token: bytes, nonce: bytes | None = None) -> bytes:
    """Build the verified 64-byte application-authentication payload."""
    if len(token) != 8:
        raise ValueError("advertisement token must be eight bytes")
    nonce = nonce if nonce is not None else os.urandom(32)
    if len(nonce) != 32:
        raise ValueError("nonce must be 32 bytes")
    digest = hashlib.sha256(AUTH_PREFIX + serial.encode("ascii") + token).digest()
    return digest + nonce


def decode_value(key: str, value: bytes):
    """Decode a characteristic according to the recovered firmware table."""
    if key in STRING_KEYS:
        return value.rstrip(b"\x00").decode("utf-8", errors="replace")
    if key in SIGNED_MILLI_KEYS:
        return int.from_bytes(value, "little", signed=True) / 1000
    return int.from_bytes(value, "little", signed=False)


def encode_bool(value: bool = True) -> bytes:
    """Encode the daemon's one-byte boolean command value."""
    return bytes((int(value),))


def encode_u32(value: int) -> bytes:
    """Encode the daemon's four-byte unsigned integer value."""
    if not 0 <= value <= 0xFFFFFFFF:
        raise ValueError("unsigned 32-bit value out of range")
    return value.to_bytes(4, "little")

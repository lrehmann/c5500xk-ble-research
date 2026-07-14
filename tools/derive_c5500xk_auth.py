#!/usr/bin/env python3
"""Derive a C5500XK BLE application-authentication payload.

This tool performs no Bluetooth operation. It accepts a freshly observed
eight-byte advertisement token, or reconstructs it from BlueZ's split
manufacturer-data representation, then prints the digest and 64-byte payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets


# Recovered and validated against firmware CKX002-02.01.19.00.
AUTH_PREFIX = bytes.fromhex(
    "4a3672565e6e74704e4746706b5e72756b37465868504b6835616b4033413650"
)


def parse_hex(value: str) -> bytes:
    return bytes.fromhex(value.replace(":", "").replace(" ", ""))


def token_from_bluez(company_id: int, manufacturer_value: bytes) -> bytes:
    if not 0 <= company_id <= 0xFFFF:
        raise ValueError("company ID must fit in 16 bits")
    if len(manufacturer_value) != 6:
        raise ValueError("BlueZ manufacturer value must be exactly 6 bytes")
    return company_id.to_bytes(2, "little") + manufacturer_value


def derive(serial: str, token: bytes, nonce: bytes) -> tuple[bytes, bytes]:
    if len(token) != 8:
        raise ValueError("advertised token must be exactly 8 bytes")
    if len(nonce) != 32:
        raise ValueError("nonce must be exactly 32 bytes")
    digest = hashlib.sha256(AUTH_PREFIX + serial.encode("ascii") + token).digest()
    return digest, digest + nonce


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    token_group = parser.add_mutually_exclusive_group(required=True)
    token_group.add_argument("--token-hex")
    token_group.add_argument("--company-id", type=lambda value: int(value, 0))
    parser.add_argument(
        "--manufacturer-value-hex",
        help="required with --company-id; the six bytes BlueZ prints as Value",
    )
    parser.add_argument("--nonce-hex", help="optional 32-byte nonce; random by default")
    args = parser.parse_args()

    if args.token_hex is not None:
        if args.manufacturer_value_hex is not None:
            parser.error("--manufacturer-value-hex is only valid with --company-id")
        token = parse_hex(args.token_hex)
    else:
        if args.manufacturer_value_hex is None:
            parser.error("--manufacturer-value-hex is required with --company-id")
        token = token_from_bluez(args.company_id, parse_hex(args.manufacturer_value_hex))

    nonce = parse_hex(args.nonce_hex) if args.nonce_hex else secrets.token_bytes(32)
    digest, payload = derive(args.serial, token, nonce)
    print(
        json.dumps(
            {
                "token_hex": token.hex(),
                "digest_hex": digest.hex(),
                "nonce_hex": nonce.hex(),
                "payload_hex": payload.hex(),
                "payload_decimal": list(payload),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

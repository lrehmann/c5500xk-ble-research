# Application authentication

This document records the authentication construction verified in firmware
`CKX002-02.01.19.00` and against one live C5500XK. Device-specific values are
redacted.

This construction has not been verified on a C6500XK. See
[`c6500xk-compatibility.md`](c6500xk-compatibility.md) for the separate evidence
and validation boundary.

## Advertisement token

`axon_platform_manager` function `0x00c8daf4` constructs an eight-byte public
passcode:

1. Select six characters from this 88-character alphabet:

   ```text
   ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789~!@#$%^&*()-+`_=:;{}[]|,.?
   ```

2. Append the static suffix `01`.

The complete eight bytes are transmitted in manufacturer-specific advertising
data. BlueZ displays the first two packet-order bytes as a little-endian
`ManufacturerData` key and the last six bytes as its value:

```python
token = company_id.to_bytes(2, "little") + manufacturer_value
```

On the tested unit, the advertised BLE local name was identical to the device
serial used by the authentication calculation. The identifier is represented
here as `<REDACTED_DEVICE_SERIAL>`.

## Static prefix recovery

The firmware contains this Base64 ciphertext in its
`BlePasskeyGenerator` data:

```text
OzwfL027wkYxf7JelRpRf1kVT0d2ykN8g9vepC0jtB5cdfbPkxolCu0ISjnfMT+H
```

The password passed by the platform manager's decrypt helper is the firmware
string:

```text
thinkgreen
```

Function `0x00c8eb74` performs the following operations:

- PBKDF2-HMAC-SHA256;
- 10,000 iterations;
- no salt;
- 48 derived bytes;
- bytes 0 through 31 as the AES key;
- bytes 32 through 47 as the IV; and
- AES-256-CBC decryption with PKCS padding.

The resulting 32-byte prefix is:

```text
ASCII: J6rV^ntpNGFpk^ruk7FXhPKh5ak@3A6P
HEX:   4a3672565e6e74704e4746706b5e72756b37465868504b6835616b4033413650
```

## Digest construction

`axon_platform_manager` function `0x00c8dce8` assembles the SHA-256 input in
this order:

1. the decrypted 32-byte prefix;
2. the device serial; and
3. the current eight-byte advertised token.

Function `0x00c8eaac` passes that concatenation directly to `SHA256`. The digest
is used as 32 raw bytes, not as a 64-character hexadecimal string.

```python
digest = sha256(prefix + serial.encode("ascii") + token).digest()
```

## GATT authentication payload

The application-authentication characteristic is:

| Property            | Value                                  |
| ------------------- | -------------------------------------- |
| Service UUID        | `b5ee5c80-e7ec-412d-8d3b-a22bfd5f0bf1` |
| Characteristic UUID | `b5ef5c81-e7ec-412d-8d3b-a22bfd5f0bf1` |
| Value handle        | `0x0005`                               |
| Live properties     | Read, Write Without Response           |
| Payload length      | 64 bytes                               |

The payload accepted by the tested unit was:

```text
digest_32_bytes || random_nonce_32_bytes
```

In `gtk_ble_daemon`, function `0x004042d4` parses the 64-byte value. Function
`0x00403458` compares the first 32 bytes against the expected digest and sets
the authentication flag on equality.

## Live timing result

One captured attempt transmitted the authentication write about 10.15 seconds
after link encryption and was disconnected. A later attempt pre-armed the write
and sent it immediately when BlueZ reported the connection and GATT service
resolution. That attempt remained connected and returned protected RG and PON
values.

The successfully validated sequence was:

1. observe a fresh manufacturer advertisement;
2. reconstruct all eight token bytes;
3. derive the 32-byte digest;
4. generate a 32-byte nonce;
5. begin encrypted BLE pairing;
6. when both `Connected` and `ServicesResolved` become true, send the 64-byte
   value as a write command to handle `0x0005`; and
7. read protected values immediately.

The helper in [`../tools/derive_c5500xk_auth.py`](../tools/derive_c5500xk_auth.py)
implements steps 2 through 4. It performs no Bluetooth operation.

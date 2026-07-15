# C6500XK compatibility assessment

## Result

The Home Assistant integration now contains a bounded experimental C6500XK
compatibility profile, but it cannot yet be called verified. The integration
recognizes full `C6500XK...` advertised serials and routes them through the
existing pairing, application-authentication, and protected-read sequence. It
reports a successful authenticated update only if protected PON telemetry is
returned. Operational writes are blocked for C6500XK devices.

No C6500XK device, firmware image, Bluetooth advertisement, GATT enumeration,
or packet capture was available for this assessment.

## Primary-source evidence

| Fact | Source | What it establishes |
| --- | --- | --- |
| The C6500XK is a Quantum Fiber SmartNID combining modem and ONT functions. | [Quantum Fiber C6500XK guide](https://www.quantumfiber.com/support/equipment/user-guides/c6500xk-smartnid.html) | Product family and role |
| The C6500XK is an XGS-PON SmartNID with two LAN ports. | [Quantum Fiber C6500XK data sheet](https://www.quantumfiber.com/content/dam/quantumfiber/equipment/downloads/C6500XK_DataSheet_110122_Final.pdf) | Access technology and hardware role |
| FCC ID `MXF-C6500XK` was filed by Gemtek Technology Co., Ltd. | [FCC equipment filing](https://fccid.io/MXF-C6500XK) | Manufacturer and model identity |
| The tested radio supports Bluetooth 5.1 Low Energy at 1 Mbps and 2 Mbps across 40 channels. | [FCC Bluetooth LE test report](https://fcc.report/FCC-ID/MXF-C6500XK/5707219.pdf) | Presence and version of BLE radio support |
| The public user manual describes the physical interfaces and XGS-PON role. | [FCC-hosted C6500XK user manual](https://fccid.io/MXF-C6500XK/User-Manual/Users-Manual-5707230.pdf) | Public product behavior, but no proprietary BLE protocol details |

The public documents do not specify the BLE local name, manufacturer-specific
advertisement format, proprietary GATT service or characteristic UUIDs,
application-authentication prefix, digest construction, or protected telemetry
layout.

## Compatibility implementation

The separate
[Home Assistant integration](https://github.com/lrehmann/c5500xk-home-assistant)
uses the following bounded C6500XK profile:

1. Home Assistant Bluetooth discovery matches connectable local names beginning
   with `C6500XK`.
2. The remaining serial suffix must contain only decimal digits. The complete
   advertised name is retained as the device identity.
3. The complete serial is passed to Home Assistant's selected connectable BLE
   source with encrypted pairing enabled.
4. The current eight-byte manufacturer token is reconstructed from the raw
   advertisement using the C5500XK format.
5. The C5500XK application-authentication digest construction is attempted with
   the C6500XK serial and current token.
6. The C5500XK proprietary characteristic map is read.
7. The update is accepted as authenticated only when both protected PON status
   and receive-optical characteristics return values.

Steps 4 through 6 are compatibility assumptions, not C6500XK findings. Keeping
step 7 prevents a successful BLE link or GATT write from being mislabeled as
working application authentication.

## Required real-device validation

Verified support requires a redacted capture from a real C6500XK that records:

1. its complete local-name shape and raw manufacturer-specific advertisement;
2. successful encrypted pairing through a connectable Home Assistant Bluetooth
   source;
3. enumerated service and characteristic UUIDs and their properties;
4. the result of the experimental application-authentication write using a
   freshly observed token; and
5. protected identity, WAN, and optical reads after authentication.

The first validation pass should remain read-only. Reboot, factory reset, WAN,
PPP, and diagnostic write characteristics must not be exercised merely to test
model compatibility.

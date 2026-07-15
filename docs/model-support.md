# Model support evidence

## Verified model

`C5500XK` is the only enabled discovery pattern and the only model claimed as
supported. Its firmware, advertisement format, authentication construction,
GATT database, value encodings, and protected reads were all checked directly.

## Evidence-bearing candidates

The tested `CKX002-02.01.19.00` platform-manager binary contains explicit model
strings for `C5500XK`, `C6500XK`, and `Q1000K`. The same binary also contains the
generic `BlePasskeyGenerator` implementation and the
`Device.X_CTL_BluetoothLowEnergy` data model. The bundled web application has
model-specific branches and assets for all three names.

That is evidence that the firmware codebase covers these related products, but
it is not evidence that a retail C6500XK or Q1000K advertises the same three
services, uses the same authentication prefix, or accepts the same GATT value
encodings. No live C6500XK or Q1000K GATT database was enumerated in this work.

Accordingly:

| Model | Evidence | Integration discovery |
| --- | --- | --- |
| C5500XK | Firmware plus live authenticated GATT reads | Enabled |
| C6500XK | Named in the shared platform binary and web UI | Disabled pending live GATT/auth verification |
| Q1000K | Named in the shared platform binary and web UI | Disabled pending live GATT/auth verification |

Adding either candidate requires a captured raw advertisement, complete GATT
enumeration, and successful protected read using a freshly derived application
payload. A model name alone is not accepted as compatibility proof.

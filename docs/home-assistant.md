# Home Assistant integration

## Architecture

The integration uses Home Assistant's Bluetooth manager. A connection may be
served by a local adapter or by any connectable ESPHome Bluetooth proxy that
reports the C5500XK advertisement. No direct socket connection to the proxy is
made by the integration.

The advertisement callback retains the packet's raw AD structures because Home
Assistant's aggregated `manufacturer_data` can contain tokens from many older
advertisements. The current token is taken only from AD type `0xff` in the raw
packet, and must be eight bytes ending in `01`.

Each poll then performs this sequence:

1. wait for a fresh connectable advertisement;
2. use the exact proxy-backed `BLEDevice` associated with that packet;
3. establish an encrypted connection with pairing requested;
4. write the 64-byte application-authentication value without response;
5. read protected WAN and PON characteristics; and
6. disconnect.

A poll is successful only if protected PON status and receive-optical values are
returned. A completed link or authentication write alone is not treated as a
successful monitoring update.

## Entities

The default monitoring surface includes:

- application-authentication connectivity;
- WAN and PON state;
- receive/transmit optical power and firmware thresholds;
- WAN uptime and PON state age;
- IPv4 packet counters;
- PON byte, BIP-error, packet-error, and discard counters;
- ping state and result counters/timings;
- Bluetooth RSSI and serving proxy; and
- last successful protected read.

## Operational writes

All write entities are disabled in the entity registry by default and remain
unavailable until `enable_write_actions` is explicitly turned on in the
integration options. This is intentional defense in depth; merely installing
or configuring the integration cannot invoke one of these operations.

| Button | Characteristic | Static payload evidence | Live execution |
| --- | --- | --- | --- |
| Release/renew WAN | `5543ceda-014f-4118-9bc4-f47747172711` | Boolean, 1 byte; mapped to `ReleaseWANIP` | Not executed |
| Run ping | four `5544...` characteristics | ASCII host, LE `uint32` size/count, state `Requested` | Not executed |
| Reboot | `5541ceda-014f-4118-9bc4-f47747172711` | Boolean, 1 byte; mapped to `ble_reboot` | Not executed |
| Reset PPP credentials | `5543cedb-014f-4118-9bc4-f47747172711` | Boolean, 1 byte; mapped to `PPPCredReset` | Not executed |
| Factory reset | `5542ceda-014f-4118-9bc4-f47747172711` | Boolean, 1 byte; mapped to `ble_factory_reset` | Not executed |

The daemon's characteristic table encodes strings as raw bytes, booleans as one
byte, and unsigned diagnostic integers as four little-endian bytes. The bundled
web UI independently sets `Device.IP.Diagnostics.IPPing.DiagnosticsState` to
`Requested` when starting a ping test.

PPP username/password and upload/download diagnostic parameters are writable in
the firmware, but the integration does not expose them. They are multi-field
configuration operations involving credentials or high-bandwidth diagnostics,
not safe one-click controls.

## Live validation boundary

The integration was installed into Home Assistant `2026.2.3`. Five connectable
ESPHome proxies were enumerated; the tested C5500XK was observed through those
proxies and added through the integration config flow. Pairing and the required
application-authentication write were allowed. No operational button was
enabled or pressed.

The first proxy session showed the same short authentication timing constraint
seen during direct BlueZ research: initial pairing and service discovery can
consume the authentication window. The implementation therefore waits for a
fresh raw advertisement and semantically requires protected PON reads before a
poll can be marked successful.

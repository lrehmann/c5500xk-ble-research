# Home Assistant integration

## Architecture

The HACS integration uses Home Assistant's Bluetooth manager. Connections are
served by a connectable ESPHome Bluetooth proxy that reports the current
C5500XK advertisement. The Home Assistant container does not need a local
Bluetooth adapter, and no separate Raspberry Pi collector is used.

The advertisement callback retains the packet's raw AD structures because Home
Assistant's aggregated `manufacturer_data` can contain tokens from older
advertisements. The current token is taken only from AD type `0xff` in the raw
packet and must be eight bytes ending in `01`.

Each connection attempt performs this sequence:

1. receive a fresh connectable advertisement through Home Assistant;
2. bind to the exact proxy-backed `BLEDevice` that reported the packet;
3. request encrypted pairing, reusing an existing bond and service cache;
4. immediately write the 64-byte application-authentication value;
5. read protected PON status and receive-optical power first;
6. read the remaining WAN, PON, counter, and diagnostic values; and
7. disconnect.

A poll is successful only if protected PON status and receive-optical values are
returned. A completed connection or authentication write alone is not treated
as successful monitoring.

## Short advertising window

Initial pairing and GATT discovery can consume most of the ONT's short
authentication window. The integration therefore makes one connection attempt
per fresh advertisement instead of retrying the same token. Later packets
automatically trigger another attempt, and the established Bluetooth bond plus
service cache can make those later connections faster.

Scheduled five-minute refreshes remain as a fallback. Advertisement-triggered
refreshes are the primary path while the ONT is in its physical Bluetooth
window.

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
unavailable until **Enable operational write actions** is explicitly turned on
in integration options. A successful authenticated monitoring update is also
required before the buttons become available.

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
ESPHome proxies were enumerated, and the tested C5500XK was observed through
them. The first proxy session completed pairing and sent the required
application-authentication write, but initial service discovery consumed the
short timing window and protected values were not returned. No operational
button was enabled or pressed.

The current implementation adds service-cache reuse, one attempt per current
token, automatic advertisement-triggered retries, and protected-first reads.
A protected refresh still requires the ONT to enter its physical Bluetooth
advertising window.

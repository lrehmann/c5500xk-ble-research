# Home Assistant integration

## Architecture

The HACS integration does not use Home Assistant Bluetooth or ESPHome
Bluetooth proxies. Bluetooth scanning, encrypted pairing, application
authentication, GATT reads, and any explicitly requested GATT write all happen
on the standalone Linux collector through its physical BlueZ adapter.

Home Assistant communicates with that collector through a local HTTP API. Every
status and action request requires a bearer token. The API is plain HTTP and is
intended only for a trusted LAN; it must not be exposed to the Internet.

Each collector poll performs this sequence:

1. wait for a current advertisement from the configured address or serial;
2. reconstruct the eight-byte token from BlueZ manufacturer data;
3. connect and request encrypted pairing directly through BlueZ;
4. immediately write the 64-byte application-authentication value;
5. read protected WAN and PON characteristics; and
6. disconnect.

A poll is successful only if protected PON status and receive-optical values are
returned. A completed link or authentication write alone is not treated as a
successful monitoring update. The collector keeps the last successful data
available while reporting the current scan/error state separately.

## Collector installation

The collector requires Linux, BlueZ, Python 3.11 or newer, and a physical
Bluetooth adapter that can hear the ONT.

1. Copy `collector/c5500xk_collector.py` to
   `/opt/c5500xk-collector/c5500xk_collector.py`.
2. Create a virtual environment in `/opt/c5500xk-collector/venv` and install
   `bleak`.
3. Copy `collector/config.example.json` to
   `/etc/c5500xk-collector/config.json`, replace its placeholders, and restrict
   the file to root.
4. Copy `collector/c5500xk-collector.service` into `/etc/systemd/system/`, then
   enable and start it.

`allow_writes` is `false` in the example and should remain false for monitoring.
The unauthenticated `/health` route reveals only collector health and version.
`/v1/status` and all `/v1/actions/*` routes require the configured API token.

## Entities

The default monitoring surface includes:

- application-authentication connectivity;
- WAN and PON state;
- receive/transmit optical power and firmware thresholds;
- WAN uptime and PON state age;
- IPv4 packet counters;
- PON byte, BIP-error, packet-error, and discard counters;
- ping state and result counters/timings;
- direct Bluetooth RSSI, collector state, and adapter;
- the last collector error; and
- the last successful protected read.

## Operational writes

Operational writes have three independent gates:

1. `allow_writes` must be explicitly changed to `true` in the collector config;
2. **Enable operational write actions** must be enabled in integration options;
3. each button entity must be manually enabled in Home Assistant.

Installing or configuring either component cannot invoke an operation.

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

The collector API and HACS integration can be tested without enabling or
executing operational writes. A protected data refresh still requires the ONT
to be in its short-lived Bluetooth advertising window. When it is not
advertising, the collector reports `waiting_for_advertisement` and retains the
last successful values, if any.

# Proprietary GATT map

This map combines live GATT enumeration with names recovered from the tested
C5500XK firmware's BLE daemon string table and TR-181 mapping.

Rights use `R` for read, `WNR` for write without response, `N` for notify, and
`B` for broadcast.

## RG data service

Service UUID: `b5ee5c80-e7ec-412d-8d3b-a22bfd5f0bf1`

| Value handle | Characteristic UUID                    | Firmware-mapped meaning              | Rights |
| -----------: | -------------------------------------- | ------------------------------------ | ------ |
|     `0x0003` | `b5ee5c81-e7ec-412d-8d3b-a22bfd5f0bf1` | Device serial number                 | R, B   |
|     `0x0005` | `b5ef5c81-e7ec-412d-8d3b-a22bfd5f0bf1` | User ID / application authentication | R, WNR |
|     `0x0007` | `b5ee5c82-e7ec-412d-8d3b-a22bfd5f0bf1` | Hardware version                     | R      |
|     `0x0009` | `b5ee5c83-e7ec-412d-8d3b-a22bfd5f0bf1` | Software version                     | R      |
|     `0x000b` | `b5ee5c84-e7ec-412d-8d3b-a22bfd5f0bf1` | Device MAC address                   | R      |
|     `0x000d` | `b5ee5c85-e7ec-412d-8d3b-a22bfd5f0bf1` | WAN detection status                 | R, N   |
|     `0x0010` | `b5ee5c86-e7ec-412d-8d3b-a22bfd5f0bf1` | SFP present                          | R, N   |
|     `0x0013` | `b5f05c81-e7ec-412d-8d3b-a22bfd5f0bf1` | DSL interface up                     | R, N   |
|     `0x0016` | `b5f05c82-e7ec-412d-8d3b-a22bfd5f0bf1` | ATM interface up                     | R, N   |
|     `0x0019` | `b5f05c83-e7ec-412d-8d3b-a22bfd5f0bf1` | PTM interface up                     | R, N   |
|     `0x001c` | `b5f05c84-e7ec-412d-8d3b-a22bfd5f0bf1` | Ethernet WAN up                      | R, N   |
|     `0x001f` | `b5f15c81-e7ec-412d-8d3b-a22bfd5f0bf1` | Ethernet interface 1 status          | R, N   |
|     `0x0022` | `b5f15c82-e7ec-412d-8d3b-a22bfd5f0bf1` | Ethernet interface 2 status          | R, N   |
|     `0x0025` | `b5f25c81-e7ec-412d-8d3b-a22bfd5f0bf1` | Downstream train rate                | R, N   |
|     `0x0028` | `b5f25c82-e7ec-412d-8d3b-a22bfd5f0bf1` | Upstream train rate                  | R, N   |
|     `0x002b` | `b5f05c85-e7ec-412d-8d3b-a22bfd5f0bf1` | WAN IPv4 address                     | R, N   |
|     `0x002e` | `b5f15c83-e7ec-412d-8d3b-a22bfd5f0bf1` | IPv4 packets sent                    | R      |
|     `0x0030` | `b5f15c84-e7ec-412d-8d3b-a22bfd5f0bf1` | IPv4 packets received                | R      |
|     `0x0032` | `b5f15c85-e7ec-412d-8d3b-a22bfd5f0bf1` | IPv4 link uptime                     | R      |
|     `0x0034` | `b5f25c88-e7ec-412d-8d3b-a22bfd5f0bf1` | Walled-garden/captive-portal state   | R, N   |
|     `0x0037` | `b5f05c86-e7ec-412d-8d3b-a22bfd5f0bf1` | PPP username                         | R, WNR |
|     `0x0039` | `b5f05c87-e7ec-412d-8d3b-a22bfd5f0bf1` | PPP password                         | WNR    |

## RG diagnostics service

Service UUID: `5540ced9-014f-4118-9bc4-f47747172711`

| Value handle | Characteristic UUID                    | Firmware-mapped meaning                       | Rights    |
| -----------: | -------------------------------------- | --------------------------------------------- | --------- |
|     `0x003c` | `5540ceda-014f-4118-9bc4-f47747172711` | Device serial number                          | R, B      |
|     `0x003e` | `5541ceda-014f-4118-9bc4-f47747172711` | Reboot command                                | WNR       |
|     `0x0040` | `5542ceda-014f-4118-9bc4-f47747172711` | Factory-reset command                         | WNR       |
|     `0x0042` | `5543ceda-014f-4118-9bc4-f47747172711` | Release/renew WAN IP command                  | WNR       |
|     `0x0044` | `5543cedb-014f-4118-9bc4-f47747172711` | Reset PPP credentials command                 | WNR       |
|     `0x0046` | `5544ceda-014f-4118-9bc4-f47747172711` | Ping host                                     | R, WNR    |
|     `0x0048` | `5544cedb-014f-4118-9bc4-f47747172711` | Ping payload/DataBlockSize                    | R, WNR    |
|     `0x004a` | `5544cedc-014f-4118-9bc4-f47747172711` | Ping repetitions                              | R, WNR    |
|     `0x004c` | `5544cede-014f-4118-9bc4-f47747172711` | Ping diagnostic state/start                   | R, WNR, N |
|     `0x004f` | `5544cedf-014f-4118-9bc4-f47747172711` | Ping success count                            | R         |
|     `0x0051` | `5544cee0-014f-4118-9bc4-f47747172711` | Ping failure count                            | R         |
|     `0x0053` | `5544cee1-014f-4118-9bc4-f47747172711` | Ping average response time                    | R         |
|     `0x0055` | `5544cee2-014f-4118-9bc4-f47747172711` | Ping maximum response time                    | R         |
|     `0x0057` | `5544cee3-014f-4118-9bc4-f47747172711` | Ping minimum response time                    | R         |
|     `0x0059` | `5545ceda-014f-4118-9bc4-f47747172711` | Upload-test URL                               | R, WNR    |
|     `0x005b` | `5545cedb-014f-4118-9bc4-f47747172711` | Upload file length                            | R, WNR    |
|     `0x005d` | `5545cedc-014f-4118-9bc4-f47747172711` | Upload duration                               | R, WNR    |
|     `0x005f` | `5545cede-014f-4118-9bc4-f47747172711` | Upload connection count                       | R, WNR    |
|     `0x0061` | `5545cedf-014f-4118-9bc4-f47747172711` | Upload diagnostic state/start                 | R, WNR, N |
|     `0x0064` | `5545cee0-014f-4118-9bc4-f47747172711` | Upload maximum connections                    | R         |
|     `0x0066` | `5545cee1-014f-4118-9bc4-f47747172711` | Upload test bytes sent under full load        | R         |
|     `0x0068` | `5545cee2-014f-4118-9bc4-f47747172711` | Upload total bytes sent under full load       | R         |
|     `0x006a` | `5545cee3-014f-4118-9bc4-f47747172711` | Upload full-load period                       | R         |
|     `0x006c` | `5545cee4-014f-4118-9bc4-f47747172711` | Upload TCP-open latency                       | R         |
|     `0x006e` | `5546ceda-014f-4118-9bc4-f47747172711` | Download-test URL                             | R, WNR    |
|     `0x0070` | `5546cedb-014f-4118-9bc4-f47747172711` | Download file length                          | R, WNR    |
|     `0x0072` | `5546cedc-014f-4118-9bc4-f47747172711` | Download duration                             | R, WNR    |
|     `0x0074` | `5546cede-014f-4118-9bc4-f47747172711` | Download connection count                     | R, WNR    |
|     `0x0076` | `5546cedf-014f-4118-9bc4-f47747172711` | Download diagnostic state/start               | R, WNR, N |
|     `0x0079` | `5546cee0-014f-4118-9bc4-f47747172711` | Download maximum connections                  | R         |
|     `0x007b` | `5546cee1-014f-4118-9bc4-f47747172711` | Download test bytes received under full load  | R         |
|     `0x007d` | `5546cee2-014f-4118-9bc4-f47747172711` | Download total bytes received under full load | R         |
|     `0x007f` | `5546cee3-014f-4118-9bc4-f47747172711` | Download full-load period                     | R         |
|     `0x0081` | `5546cee4-014f-4118-9bc4-f47747172711` | Download TCP-open latency                     | R         |

## PON data service

Service UUID: `4d84d94f-7fc1-43ac-8fab-a6a7f03b9b58`

| Value handle | Characteristic UUID                    | Firmware-mapped meaning        | Rights |
| -----------: | -------------------------------------- | ------------------------------ | ------ |
|     `0x0084` | `4d84d950-7fc1-43ac-8fab-a6a7f03b9b58` | Device serial number           | R, B   |
|     `0x0086` | `4d86d957-7fc1-43ac-8fab-a6a7f03b9b58` | PON FSAN ID                    | R      |
|     `0x0088` | `4d84d951-7fc1-43ac-8fab-a6a7f03b9b58` | PON status                     | R, N   |
|     `0x008b` | `4d85d950-7fc1-43ac-8fab-a6a7f03b9b58` | PON last-change time           | R, N   |
|     `0x008e` | `4d85d951-7fc1-43ac-8fab-a6a7f03b9b58` | Receive optical signal level   | R, N   |
|     `0x0091` | `4d85d952-7fc1-43ac-8fab-a6a7f03b9b58` | Lower RX optical threshold     | R      |
|     `0x0093` | `4d85d953-7fc1-43ac-8fab-a6a7f03b9b58` | Upper RX optical threshold     | R      |
|     `0x0095` | `4d85d954-7fc1-43ac-8fab-a6a7f03b9b58` | Transmit optical level         | R, N   |
|     `0x0098` | `4d85d955-7fc1-43ac-8fab-a6a7f03b9b58` | Lower TX optical threshold     | R      |
|     `0x009a` | `4d85d956-7fc1-43ac-8fab-a6a7f03b9b58` | Upper TX optical threshold     | R      |
|     `0x009c` | `4d86d950-7fc1-43ac-8fab-a6a7f03b9b58` | BIP errors received            | R, N   |
|     `0x009f` | `4d86d951-7fc1-43ac-8fab-a6a7f03b9b58` | PON bytes sent                 | R, N   |
|     `0x00a2` | `4d86d952-7fc1-43ac-8fab-a6a7f03b9b58` | PON bytes received             | R, N   |
|     `0x00a5` | `4d86d953-7fc1-43ac-8fab-a6a7f03b9b58` | PON errors sent                | R, N   |
|     `0x00a8` | `4d86d954-7fc1-43ac-8fab-a6a7f03b9b58` | PON errors received            | R, N   |
|     `0x00ab` | `4d86d955-7fc1-43ac-8fab-a6a7f03b9b58` | PON discarded packets sent     | R, N   |
|     `0x00ae` | `4d86d956-7fc1-43ac-8fab-a6a7f03b9b58` | PON discarded packets received | R, N   |

## Write validation boundary

Only the application-authentication characteristic at handle `0x0005` was
written. No reboot, reset, WAN, PPP, ping, upload, or download characteristic
was exercised. The table reports live GATT rights and firmware-mapped meanings;
it does not claim live execution of untested command values.

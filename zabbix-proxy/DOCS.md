# Home Assistant App: Zabbix Proxy

## About

This app runs an official Zabbix proxy with SQLite3 storage inside Home
Assistant. It is intended for sites where Home Assistant can reach the Zabbix
server and should buffer monitoring data locally if the server is unavailable.

The app defaults to active proxy mode. In active mode, the proxy connects out to
the Zabbix server, so no inbound port needs to be exposed on the Home Assistant
host.

## Setup

1. In Zabbix, create a proxy under **Administration -> Proxies**.
2. Set the Zabbix proxy name to exactly the same value you will enter in
   `proxy_hostname`.
3. Choose active proxy mode unless your Zabbix server must connect to the proxy.
4. Install this app in Home Assistant and configure:
   - `server_host`: your Zabbix server DNS name or IP address, optionally with a port.
   - `proxy_hostname`: the proxy name configured in Zabbix.
5. Start the app and check the logs for the Zabbix proxy startup messages.

## Local development

When installing this app from Home Assistant's local apps directory, temporarily
comment out the `image` key in `config.yaml`. Home Assistant Supervisor will
then build the app from the local `Dockerfile`.

Restore the `image` key before opening a pull request or publishing a release so
repository installs pull the prebuilt GHCR image.

## Passive mode

Passive mode requires the Zabbix server to connect to this proxy. Set
`proxy_mode` to `passive` and enable the `10051/tcp` port mapping in Home
Assistant if the server is outside the Home Assistant host network.

## TLS

For PSK mode, set:

- `tls_connect`: `psk`
- `tls_accept`: `psk`
- `tls_psk_identity`
- `tls_psk`

For certificate mode, place certificate files in this app's configuration
folder and set `tls_ca_file`, `tls_cert_file`, and `tls_key_file` to those file
names. For a local install, this folder is `/addon_configs/local_zabbix_proxy`.
For a repository install, Home Assistant creates the same folder with the
repository identifier instead of `local`.

## Storage

The proxy SQLite database is stored in `/data/db_data`, which is managed by Home
Assistant as persistent app data. Do not configure this app to use the Zabbix
server database; a Zabbix proxy has its own local database.

## Limitations

- ICMP ping checks may require the `NET_RAW` capability. This app intentionally
  does not request that capability in v1.
- The app targets Zabbix 7.4 using the official SQLite proxy image.
- Zabbix 7.4 and the upstream proxy image are licensed under AGPLv3. This
  repository's app wrapper is licensed separately under Apache-2.0.
- The app icon and logo use the Zabbix logo asset from Wikimedia Commons.

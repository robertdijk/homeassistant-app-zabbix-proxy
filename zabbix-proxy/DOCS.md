# Home Assistant App: Zabbix Proxy

## About

This app runs an official Zabbix proxy with SQLite3 storage inside Home
Assistant. It is intended for sites where Home Assistant can reach the Zabbix
server and should buffer monitoring data locally if the server is unavailable.

The app defaults to active proxy mode. In active mode, the proxy connects out to
the Zabbix server, so server communication needs no inbound port. Enable the
`10051/tcp` port mapping if active agents or Zabbix senders need to connect to
the proxy through the Home Assistant host's IP address.

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
Assistant. Configure the server to connect to the Home Assistant host's IP
address and mapped port, even when both are on the same LAN.

## TLS

For PSK mode, set:

- `tls_connect`: `psk`
- `tls_accept`: `psk`
- `tls_psk_identity`
- `tls_psk`

For certificate mode, place certificate files in this app's configuration
folder and set `tls_ca_file`, `tls_cert_file`, and `tls_key_file` to those file
names. Set `tls_connect` to `cert` for outgoing connections and `tls_accept` to
`cert` for incoming connections that should use certificates; both default to
`unencrypted`.

For a local install, this folder is `/addon_configs/local_zabbix_proxy`.
For a repository install, Home Assistant creates the same folder with the
repository identifier instead of `local`.

## Storage

The proxy SQLite database is stored in `/data/db_data`, which is managed by Home
Assistant as persistent app data. Do not configure this app to use the Zabbix
server database; a Zabbix proxy has its own local database.

### Buffering

The default is `proxy_buffer_mode: hybrid`, with a 64 MiB memory buffer and a
10-minute age limit. This keeps normal data collection in RAM to reduce disk
writes, while falling back to SQLite when the buffer fills or unsent data reaches
the age limit. A normal shutdown also saves unsent data to SQLite; a crash or
power loss can still lose data held in RAM.

To use only RAM for collected data, set `proxy_buffer_mode: memory`. Unsent data
is lost on shutdown, and the oldest data is dropped when the buffer fills.
SQLite is still required for proxy configuration. Use `disk` to always buffer
collected data in SQLite.

- `proxy_memory_buffer_size`: buffer size in MiB, default `64`. Increase it if
  needed and RAM is available; this is additional to the proxy's other memory.
- `proxy_memory_buffer_age`: age limit in seconds for hybrid mode, default `600`.
  Use `0` to disable the age limit, or at least `600`. It must not exceed
  `proxy_offline_buffer` converted from hours to seconds.
- `proxy_offline_buffer`: retention during server outages, default `1` hour.
  It does not protect memory mode against shutdown or a full buffer.

`ProxyLocalBuffer` is fixed at `0`, so already-sent history is not retained.
Home Assistant allows up to 60 seconds for the app to shut down and flush its
hybrid buffer. This is separate from the `timeout` option for monitoring checks.

Restart the app after changing these options. Existing installations also use
the hybrid defaults when the new options have not been set.

See [Zabbix's buffer documentation](https://www.zabbix.com/documentation/7.4/en/manual/concepts/proxy#proxy-memory-buffer)
for details.

## Limitations

- ICMP ping checks may require the `NET_RAW` capability. This app intentionally
  does not request that capability.
- The app targets Zabbix 7.4 using the official SQLite proxy image.
- Zabbix 7.4 and the upstream proxy image are licensed under AGPLv3. This
  repository's app wrapper is licensed separately under Apache-2.0.
- The app icon and logo use the Zabbix logo asset from Wikimedia Commons.

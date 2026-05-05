# Zabbix Proxy Home Assistant app repository

Run an official Zabbix proxy with SQLite3 storage from Home Assistant.

Apps documentation: <https://developers.home-assistant.io/docs/apps>

[![Builder](https://github.com/robertdijk/homeassistant-app-zabbix-proxy/actions/workflows/builder.yaml/badge.svg)](https://github.com/robertdijk/homeassistant-app-zabbix-proxy/actions/workflows/builder.yaml)
[![Lint](https://github.com/robertdijk/homeassistant-app-zabbix-proxy/actions/workflows/lint.yaml/badge.svg)](https://github.com/robertdijk/homeassistant-app-zabbix-proxy/actions/workflows/lint.yaml)

[![Open your Home Assistant instance and show the app store with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_store.svg)](https://my.home-assistant.io/redirect/supervisor_store/?repository_url=https%3A%2F%2Fgithub.com%2Frobertdijk%2Fhomeassistant-app-zabbix-proxy)

## Apps

This repository contains the following app.

### [Zabbix Proxy](./zabbix-proxy)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

_Zabbix proxy with SQLite3 storage for Home Assistant._

The app uses the official `zabbix/zabbix-proxy-sqlite3:alpine-7.4-latest`
container image and translates Home Assistant app options into the upstream
`ZBX_*` environment variables.

## Publishing

Images are built with the Home Assistant builder GitHub Actions. Pull requests
and pushes to `main` build for validation. Version tags such as `v0.1.0`
publish the multi-architecture image to GHCR.

See [RELEASING.md](./RELEASING.md) for the release checklist.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg

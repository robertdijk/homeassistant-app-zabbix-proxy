<!-- https://developers.home-assistant.io/docs/apps/presentation#keeping-a-changelog -->

## 7.4.11-3

- Bumps [home-assistant/builder](https://github.com/home-assistant/builder) from 2026.03.2 to 2026.06.0.


## 7.4.11-2

- Bumps [actions/checkout](https://github.com/actions/checkout) from 6.0.2 to 7.0.0.


## 7.4.11-1

- Update to Zabbix 7.4.11.

## 7.4.10-2

- Automate releases: Dependabot opens PRs for new Zabbix versions, merging
  publishes the image automatically. App-only releases via Actions → Release.

## 7.4.10-1

- Update to Zabbix 7.4.10.

## 7.4.9-1

- Switch to Zabbix-version-based versioning: `{zabbix-version}-{release}`.
- Pin base image to `zabbix/zabbix-proxy-sqlite3:alpine-7.4.9`.

## 0.1.2

- Avoid runtime ownership changes on Home Assistant OS app data mounts.
- Explicitly allow the Zabbix proxy to run as root inside the protected app
  container.

## 0.1.1

- Remove the default `startup` configuration key to satisfy the Home Assistant
  app linter.

## 0.1.0

- Initial release.
- Run the official Zabbix proxy SQLite3 image for Zabbix 7.4.
- Add Home Assistant app options for active/passive mode, proxy identity,
  runtime tuning, and TLS.
- Persist the SQLite proxy database in app data.

# Releasing

This repository publishes pre-built Home Assistant app images to GHCR.

## Versioning

Versions use the format `{zabbix-version}-{release}`, e.g. `7.4.9-1`.

- The first three parts track the upstream Zabbix release.
- The trailing `-N` counter resets to `1` on every Zabbix bump and increments
  for app-only fixes within the same Zabbix version (e.g. `7.4.9-2`).

## Automated Zabbix version bumps (Dependabot)

Dependabot checks Docker Hub daily for new `zabbix/zabbix-proxy-sqlite3`
releases. When one is found it opens a PR that updates the `FROM` line in
[zabbix-proxy/Dockerfile](zabbix-proxy/Dockerfile).

The **Prepare release** workflow automatically commits matching updates to
`zabbix-proxy/config.yaml` (version → `{new-zabbix-version}-1`) and
`zabbix-proxy/CHANGELOG.md` onto the same PR branch so CI passes without any
manual edits.

Review the PR, make any extra changes if needed, then merge. The **Release**
workflow fires automatically on merge, creates the tag, builds, and publishes
the image to GHCR — no further action needed.

## App-only releases (no Zabbix bump)

When you fix something in the app itself without changing the Zabbix version:

1. Increment the `-N` counter in `version` in `zabbix-proxy/config.yaml`
   (e.g. `7.4.9-1` → `7.4.9-2`).
2. Add a matching `## 7.4.9-2` section to `zabbix-proxy/CHANGELOG.md`.
3. Merge to `main`.
4. Go to **Actions → Release → Run workflow** and click **Run workflow**.

The workflow reads the current version from `config.yaml`, creates the tag,
builds, and publishes the image to GHCR.

## Upgrading to a new minor or major Zabbix version

Dependabot will open PRs for any new Zabbix version — patch, minor, or major.
Review and merge as usual; the **Prepare release** workflow handles all version
bumps the same way.

## First GHCR Release

Before the first public install works:

1. Confirm the repository has GitHub Actions workflow permissions set to
   **Read and write permissions**.
2. Run the **Release** workflow and wait for it to finish.
3. In GitHub Packages, make the
   `homeassistant-app-zabbix-proxy` container package public.
4. Confirm the package has these tags:
   - `7.4.9-2` or the release version
   - `latest`
   - per-architecture tags created by the Home Assistant builder

## Local Development

For local Supervisor installs from `/addons/local`, temporarily comment out the
`image` key in `zabbix-proxy/config.yaml`, then reload the store and rebuild:

```bash
ha store reload
ha apps rebuild --force "local_zabbix_proxy"
```

Restore the `image` key before opening a pull request or triggering a release.

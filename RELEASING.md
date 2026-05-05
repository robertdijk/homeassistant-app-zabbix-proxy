# Releasing

This repository publishes pre-built Home Assistant app images to GHCR.

## Versioning

Use semantic versions in `zabbix-proxy/config.yaml`.

For every release:

1. Update `version` in `zabbix-proxy/config.yaml`.
2. Add a matching `## X.Y.Z` section to `zabbix-proxy/CHANGELOG.md`.
3. Keep `image` set to:

   ```yaml
   image: "ghcr.io/robertdijk/homeassistant-app-zabbix-proxy"
   ```

4. Merge the change to `main`.
5. Create and push a matching tag:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

The GitHub Actions builder publishes only from `vX.Y.Z` tags. Pull requests and
pushes to `main` build for validation but do not publish images.

## First GHCR Release

Before the first public install works:

1. Confirm the repository has GitHub Actions workflow permissions set to
   **Read and write permissions**.
2. Push the first version tag and wait for the **Builder** workflow to finish.
3. In GitHub Packages, make the
   `homeassistant-app-zabbix-proxy` container package public.
4. Confirm the package has these tags:
   - `0.1.0` or the release version
   - `latest`
   - per-architecture tags created by the Home Assistant builder

## Local Development

For local Supervisor installs from `/addons/local`, temporarily comment out the
`image` key in `zabbix-proxy/config.yaml`, then reload the store and rebuild:

```bash
ha store reload
ha apps rebuild --force "local_zabbix_proxy"
```

Restore the `image` key before opening a pull request or tagging a release.

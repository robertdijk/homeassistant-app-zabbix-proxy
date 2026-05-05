# https://developers.home-assistant.io/docs/apps/configuration#app-dockerfile
FROM zabbix/zabbix-proxy-sqlite3:alpine-7.4-latest

USER root

RUN \
    apk add --no-cache jq su-exec \
    && mv /usr/bin/docker-entrypoint.sh /usr/bin/zabbix-docker-entrypoint.sh \
    && rm -rf /var/lib/zabbix/db_data \
    && ln -s /data/db_data /var/lib/zabbix/db_data

COPY rootfs /

RUN \
    chmod 0755 /usr/local/bin/ha-zabbix-proxy-entrypoint \
    && chown -h zabbix:0 /var/lib/zabbix/db_data

ENTRYPOINT ["/usr/local/bin/ha-zabbix-proxy-entrypoint"]

CMD ["/usr/sbin/zabbix_proxy", "--foreground", "-c", "/etc/zabbix/zabbix_proxy.conf"]

LABEL \
    org.opencontainers.image.title="Home Assistant App: Zabbix Proxy" \
    org.opencontainers.image.description="Zabbix proxy with SQLite3 storage for Home Assistant." \
    org.opencontainers.image.source="https://github.com/robertdijk/homeassistant-app-zabbix-proxy" \
    org.opencontainers.image.licenses="Apache-2.0 AND AGPL-3.0-only"

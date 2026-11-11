"""Build first, then run: python3 tests/smoke_container.py IMAGE [PLATFORM]."""

import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid


IMAGE = sys.argv[1]


def docker(*args, check=True):
    result = subprocess.run(
        ["docker", *args], capture_output=True, text=True, timeout=90
    )
    if check and result.returncode:
        raise AssertionError(f"docker {args}:\n{result.stdout}\n{result.stderr}")
    return result.stdout


def wait_for_startup(name):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        logs = docker("logs", name)
        state = json.loads(docker("inspect", "--format", "{{json .State}}", name))
        if not state["Running"]:
            raise AssertionError(f"Container exited: {state}\n{logs}")
        if "started [" in logs:
            return
        time.sleep(0.5)
    raise AssertionError(f"Startup timed out:\n{logs}")


PLATFORM = sys.argv[2] if len(sys.argv) > 2 else docker(
    "image", "inspect", IMAGE, "--format", "{{.Os}}/{{.Architecture}}"
).strip()


for mode, proxy_mode, tls in (
    ("disk", "passive", "unencrypted"), ("memory", "passive", "unencrypted"),
    ("hybrid", "passive", "unencrypted"), ("hybrid", "active", "unencrypted"),
    ("hybrid", "passive", "psk"), ("hybrid", "active", "psk"),
    ("hybrid", "passive", "cert"), ("hybrid", "active", "cert"),
):
    name = f"zabbix8-smoke-{uuid.uuid4().hex[:10]}"
    with tempfile.TemporaryDirectory(prefix="zabbix8-smoke-") as directory:
        options = {
            "server_host": "127.0.0.1:10052", "proxy_hostname": name,
            "proxy_mode": proxy_mode, "debug_level": 3,
            "proxy_buffer_mode": mode, "proxy_memory_buffer_size": 32,
            "proxy_memory_buffer_age": 600, "proxy_offline_buffer": 2,
            "proxy_config_frequency": 15, "data_sender_frequency": 2,
            "timeout": 8, "tls_connect": tls, "tls_accept": tls,
        }
        if tls == "psk":
            options.update(tls_psk_identity="smoke-test", tls_psk="ab" * 32)
        cert_directory = Path(directory, "certificates")
        cert_directory.mkdir()
        if tls == "cert":
            subprocess.run(
                ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                 "-keyout", str(cert_directory / "key.pem"),
                 "-out", str(cert_directory / "cert.pem"),
                 "-days", "1", "-subj", "/CN=smoke-test"],
                check=True, capture_output=True, timeout=30,
            )
            prefix = "/config/" if proxy_mode == "passive" else ""
            options.update(tls_ca_file=prefix + "cert.pem",
                           tls_cert_file=prefix + "cert.pem", tls_key_file=prefix + "key.pem")
        Path(directory, "options.json").write_text(json.dumps(options))
        try:
            security_options = []
            if profile := os.environ.get("SMOKE_APPARMOR"):
                security_options = ["--security-opt", f"apparmor={profile}"]
            # Exercise an existing data directory on the normal hybrid setup.
            # A previous release can be supplied to test a version upgrade too.
            if (mode, proxy_mode, tls) == ("hybrid", "passive", "unencrypted"):
                previous_name = name + "-previous"
                previous_image = os.environ.get("SMOKE_PREVIOUS_IMAGE", IMAGE)
                try:
                    docker("run", "-d", "--name", previous_name, "--platform", PLATFORM,
                           "--network", "none", "--mount",
                           f"type=bind,src={directory},dst=/data", *security_options, previous_image)
                    wait_for_startup(previous_name)
                    docker("stop", "--time", "60", previous_name)
                    assert list(Path(directory, "db_data").glob("*.sqlite"))
                finally:
                    docker("rm", "-fv", previous_name, check=False)
            docker("run", "-d", "--name", name, "--platform", PLATFORM,
                   "--network", "none", "--mount",
                   f"type=bind,src={directory},dst=/data", "--mount",
                   f"type=bind,src={cert_directory},dst=/config,readonly",
                   *security_options, IMAGE)
            wait_for_startup(name)

            config = docker("exec", name, "sh", "-c", "cat /etc/zabbix/zabbix_proxy*.conf")
            # Zabbix 8 resolves ${ENV_VAR} placeholders in its configuration.
            process_env = dict(
                item.split("=", 1) for item in
                docker("exec", name, "cat", "/proc/1/environ").split("\0")
                if "=" in item
            )
            config = re.sub(r"\$\{([^}]+)\}",
                            lambda match: process_env.get(match[1], ""), config)
            configured = {}
            for line in config.splitlines():
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    configured[key.strip()] = value.strip()
            expected = {
                "Hostname": name, "ProxyMode": "1" if proxy_mode == "passive" else "0",
                "DebugLevel": "3", "ProxyBufferMode": mode,
                "ProxyMemoryBufferSize": "0" if mode == "disk" else "32M",
                "ProxyMemoryBufferAge": "600" if mode == "hybrid" else "0",
                "ProxyLocalBuffer": "0", "ProxyOfflineBuffer": "2",
                "DataSenderFrequency": "2", "Timeout": "8", "AllowRoot": "1",
            }
            for key, value in expected.items():
                assert configured.get(key) == value, (key, value, configured.get(key), config)
            assert "127.0.0.1" in configured["Server"], configured
            if proxy_mode == "active":
                assert "10052" in configured["Server"], configured
                assert configured.get("ProxyConfigFrequency") == "15", configured
                assert configured.get("TLSConnect") == tls, configured
            else:
                assert configured.get("TLSAccept") == tls, configured
            if tls == "psk":
                assert configured.get("TLSPSKIdentity") == "smoke-test", configured
                assert docker("exec", name, "cat", configured["TLSPSKFile"]).strip() == "ab" * 32
            if tls == "cert":
                for key, filename in (("TLSCAFile", "cert.pem"),
                                      ("TLSCertFile", "cert.pem"), ("TLSKeyFile", "key.pem")):
                    assert docker("exec", name, "cat", configured[key]) == (cert_directory / filename).read_text()

            validation = docker("exec", name, "/usr/local/bin/ha-zabbix-proxy-entrypoint",
                                "/usr/sbin/zabbix_proxy", "-T",
                                "-c", "/etc/zabbix/zabbix_proxy.conf")
            assert "successful" in validation.lower(), validation
            database_path = configured["DBName"]
            assert database_path.startswith("/var/lib/zabbix/db_data/"), database_path
            database_file = Path(directory, "db_data", Path(database_path).name)
            assert database_file.stat().st_size > 0
            docker("exec", name, "sh", "-c", "test -L /var/lib/zabbix/db_data")

            docker("stop", "--time", "60", name)
            state = json.loads(docker("inspect", "--format", "{{json .State}}", name))
            logs = docker("logs", name)
            assert state["ExitCode"] == 0, (state, logs)
            assert "Zabbix Proxy stopped" in logs, logs
            print(f"PASS {PLATFORM} {mode}/{proxy_mode}/{tls}: options, config validation, "
                  "startup, persistent SQLite, graceful shutdown", flush=True)
        finally:
            docker("rm", "-fv", name, check=False)

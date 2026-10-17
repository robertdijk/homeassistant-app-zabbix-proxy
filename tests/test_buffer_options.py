"""Check option mapping without starting Zabbix or writing container directories."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ENTRYPOINT = (
    Path(__file__).resolve().parents[1]
    / "zabbix-proxy/rootfs/usr/local/bin/ha-zabbix-proxy-entrypoint"
)


class BufferOptionsTest(unittest.TestCase):
    def run_wrapper(self, **options):
        config = {"server_host": "zabbix.example.com", "proxy_hostname": "test"}
        config.update(options)
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "options.json"
            config_path.write_text(json.dumps(config))
            return subprocess.run(
                [
                    "bash", "-c",
                    'mkdir() { :; }; exec() { env; }; source "$1"',
                    "test", str(ENTRYPOINT),
                ],
                env={**os.environ, "CONFIG_PATH": str(config_path)},
                capture_output=True,
                text=True,
            )

    def test_existing_options_get_defaults(self):
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        exported = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
        self.assertEqual(exported["ZBX_PROXYBUFFERMODE"], "hybrid")
        self.assertEqual(exported["ZBX_PROXYMEMORYBUFFERSIZE"], "64M")
        self.assertEqual(exported["ZBX_PROXYMEMORYBUFFERAGE"], "600")
        self.assertEqual(exported["ZBX_PROXYLOCALBUFFER"], "0")

    def test_switching_modes_only_applies_age_to_hybrid(self):
        for mode in ("disk", "memory", "hybrid"):
            with self.subTest(mode=mode):
                result = self.run_wrapper(
                    proxy_buffer_mode=mode,
                    proxy_memory_buffer_size=32,
                    proxy_memory_buffer_age=600,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"ZBX_PROXYBUFFERMODE={mode}\n", result.stdout)
                size = "0" if mode == "disk" else "32M"
                self.assertIn(f"ZBX_PROXYMEMORYBUFFERSIZE={size}\n", result.stdout)
                age = 600 if mode == "hybrid" else 0
                self.assertIn(f"ZBX_PROXYMEMORYBUFFERAGE={age}\n", result.stdout)

    def test_disabled_age_limit(self):
        result = self.run_wrapper(proxy_memory_buffer_age=0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ZBX_PROXYMEMORYBUFFERAGE=0\n", result.stdout)

    def test_invalid_settings_fail_before_startup(self):
        for options in (
            {"proxy_buffer_mode": "invalid"},
            {"proxy_memory_buffer_size": 0},
            {"proxy_memory_buffer_size": 2049},
            {"proxy_memory_buffer_size": "16M"},
            {"proxy_memory_buffer_age": -1},
            {"proxy_memory_buffer_age": 599},
            {"proxy_memory_buffer_age": 864001},
            {"proxy_memory_buffer_age": 3601, "proxy_offline_buffer": 1},
        ):
            with self.subTest(options=options):
                result = self.run_wrapper(**options)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("[zabbix-proxy]", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_age_limit_uses_hours_for_offline_buffer(self):
        result = self.run_wrapper(proxy_memory_buffer_age=7200, proxy_offline_buffer=2)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

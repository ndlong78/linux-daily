from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import interoperability_lab  # noqa: E402


def _manifest() -> dict:
    return {
        "version": 1,
        "name": "test",
        "roles": {
            "linux-peer": {
                "platform": "linux",
                "distros": ["ubuntu", "xubuntu", "debian", "fedora"],
                "package_managers": ["apt", "dnf"],
                "service_manager": "systemd",
                "config_root": "/etc/nginx",
                "firewalls": ["ufw", "nftables", "firewalld"],
                "script": "labs/p9-linux-freebsd-interoperability/linux-peer.sh",
            },
            "freebsd-peer": {
                "platform": "freebsd",
                "package_managers": ["pkg", "ports"],
                "service_manager": "rc.d",
                "config_root": "/usr/local/etc/nginx",
                "firewalls": ["pf", "ipfw"],
                "script": "labs/p9-linux-freebsd-interoperability/freebsd-peer.sh",
            },
        },
        "workflow": {
            "application": "nginx",
            "protocol": "http",
            "port": 8088,
            "directions": ["linux-to-freebsd", "freebsd-to-linux"],
            "evidence": ["functional", "negative", "recovery", "observability"],
            "negative_test": "stop-service",
            "recovery": "start-service",
        },
        "differences": ["package", "service", "firewall", "path"],
        "safety": {
            "private_network_only": True,
            "dedicated_lab_hosts": True,
            "rollback_required": True,
            "cleanup_required": True,
        },
        "sources": ["https://example.test/one", "https://example.test/two"],
    }


def _write_scripts(root: Path, *, freebsd_line: str = "service nginx status") -> None:
    lab = root / "labs" / "p9-linux-freebsd-interoperability"
    lab.mkdir(parents=True)
    (lab / "linux-peer.sh").write_text("systemctl is-active nginx\n", encoding="utf-8")
    (lab / "freebsd-peer.sh").write_text(freebsd_line + "\n", encoding="utf-8")


def test_real_interoperability_lab_passes():
    manifest = interoperability_lab.load_manifest()
    assert interoperability_lab.validate_manifest(manifest) == []


def test_manifest_requires_both_directions_and_evidence(tmp_path):
    manifest = _manifest()
    _write_scripts(tmp_path)
    manifest["workflow"]["directions"] = ["linux-to-freebsd"]
    manifest["workflow"]["evidence"] = ["functional", "negative"]
    errors = interoperability_lab.validate_manifest(manifest, root=tmp_path)
    assert any("freebsd-to-linux" in error for error in errors)
    assert any("recovery" in error and "observability" in error for error in errors)


def test_freebsd_script_rejects_linux_only_commands(tmp_path):
    manifest = _manifest()
    _write_scripts(tmp_path, freebsd_line="systemctl restart nginx")
    errors = interoperability_lab.validate_manifest(manifest, root=tmp_path)
    assert any("command semantics sai platform" in error for error in errors)


def test_manifest_requires_safety_and_all_difference_classes(tmp_path):
    manifest = copy.deepcopy(_manifest())
    _write_scripts(tmp_path)
    manifest["differences"] = ["package", "service"]
    manifest["safety"]["private_network_only"] = False
    errors = interoperability_lab.validate_manifest(manifest, root=tmp_path)
    assert any("firewall" in error and "path" in error for error in errors)
    assert any("private_network_only" in error for error in errors)

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "platform-baseline.json"
STYLE_PATH = ROOT / "STYLE.md"

EXPECTED_DISPLAYS = [
    "Ubuntu/Xubuntu 26.04 LTS",
    "Debian 13 stable",
    "Fedora 44",
    "FreeBSD 15.1-RELEASE",
]


def _baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def test_current_platform_baseline_is_explicit_and_current():
    data = _baseline()

    assert data["schema_version"] == 1
    assert data["last_verified"] == "2026-09-07"
    assert data["applies_from_issue"] == 70
    assert data["historical_evidence_policy"] == "preserve-until-reverified"
    assert [item["display"] for item in data["platforms"]] == EXPECTED_DISPLAYS

    debian = next(item for item in data["platforms"] if item["id"] == "debian")
    assert debian["latest_point_release"] == "13.6"
    assert debian["codename"] == "trixie"


def test_platform_baseline_keeps_linux_and_freebsd_semantics_separate():
    data = _baseline()
    by_id = {item["id"]: item for item in data["platforms"]}

    assert by_id["ubuntu_xubuntu"]["package_manager"] == "APT"
    assert by_id["ubuntu_xubuntu"]["service_manager"] == "systemd"
    assert by_id["debian"]["package_manager"] == "APT"
    assert by_id["fedora"]["package_manager"] == "DNF"
    assert by_id["fedora"]["security_model"] == "SELinux"
    assert by_id["freebsd"]["package_manager"] == "pkg/ports"
    assert by_id["freebsd"]["service_manager"] == "rc.d"
    assert by_id["freebsd"]["firewall"] == "pf/ipfw"


def test_platform_baseline_sources_are_official_https_urls():
    data = _baseline()

    for item in data["platforms"]:
        assert item["official_source"].startswith("https://")
    ubuntu = next(item for item in data["platforms"] if item["id"] == "ubuntu_xubuntu")
    assert ubuntu["flavor_source"].startswith("https://")


def test_style_uses_current_platform_baseline_and_preserves_history():
    style = STYLE_PATH.read_text(encoding="utf-8")

    assert "platform-baseline.json" in style
    for display in EXPECTED_DISPLAYS:
        assert display in style
    assert "Không đổi #001–#069 thành release mới nếu chưa re-verify" in style

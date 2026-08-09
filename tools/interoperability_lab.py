#!/usr/bin/env python3
"""Validate the P9.5 Linux <-> FreeBSD interoperability lab artifact."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "labs" / "p9-linux-freebsd-interoperability" / "lab.json"
REQUIRED_PLATFORMS = {"linux", "freebsd"}
REQUIRED_DIFFERENCES = {"package", "service", "firewall", "path"}
REQUIRED_DIRECTIONS = {"linux-to-freebsd", "freebsd-to-linux"}
REQUIRED_EVIDENCE = {"functional", "negative", "recovery", "observability"}
LINUX_ONLY_FREEBSD = re.compile(
    r"(^|\s)(systemctl|journalctl|apt|apt-get|dnf|yum|ufw|firewall-cmd|nft)(\s|$)"
)
FREEBSD_ONLY_LINUX = re.compile(r"(^|\s)(sysrc|pkg|pfctl|ipfw)(\s|$)")


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _nonempty_list(value, *, label: str, errors: list[str]) -> list:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} phải là list không rỗng")
        return []
    return value


def validate_manifest(manifest: dict, *, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if manifest.get("version") != 1:
        errors.append("version phải bằng 1")

    roles = manifest.get("roles")
    if not isinstance(roles, dict) or len(roles) < 2:
        errors.append("roles phải có ít nhất linux-peer và freebsd-peer")
        roles = {}

    platforms = {
        role.get("platform")
        for role in roles.values()
        if isinstance(role, dict) and isinstance(role.get("platform"), str)
    }
    if platforms != REQUIRED_PLATFORMS:
        errors.append("roles phải chứa đúng platform linux và freebsd")

    linux = roles.get("linux-peer", {}) if isinstance(roles, dict) else {}
    freebsd = roles.get("freebsd-peer", {}) if isinstance(roles, dict) else {}

    linux_distros = set(_nonempty_list(linux.get("distros"), label="linux-peer.distros", errors=errors))
    if not {"ubuntu", "xubuntu", "debian", "fedora"}.issubset(linux_distros):
        errors.append("linux-peer.distros phải bao quát Ubuntu/Xubuntu, Debian và Fedora")
    if linux.get("service_manager") != "systemd":
        errors.append("linux-peer.service_manager phải là systemd")
    if linux.get("config_root") != "/etc/nginx":
        errors.append("linux-peer.config_root phải là /etc/nginx")
    linux_package_managers = set(
        _nonempty_list(linux.get("package_managers"), label="linux-peer.package_managers", errors=errors)
    )
    if not {"apt", "dnf"}.issubset(linux_package_managers):
        errors.append("linux-peer.package_managers phải có apt và dnf")

    freebsd_package_managers = set(
        _nonempty_list(
            freebsd.get("package_managers"), label="freebsd-peer.package_managers", errors=errors
        )
    )
    if not {"pkg", "ports"}.issubset(freebsd_package_managers):
        errors.append("freebsd-peer.package_managers phải có pkg và ports")
    if freebsd.get("service_manager") != "rc.d":
        errors.append("freebsd-peer.service_manager phải là rc.d")
    if freebsd.get("config_root") != "/usr/local/etc/nginx":
        errors.append("freebsd-peer.config_root phải là /usr/local/etc/nginx")

    differences = set(_nonempty_list(manifest.get("differences"), label="differences", errors=errors))
    missing_differences = sorted(REQUIRED_DIFFERENCES - differences)
    if missing_differences:
        errors.append("differences thiếu: " + ", ".join(missing_differences))

    workflow = manifest.get("workflow")
    if not isinstance(workflow, dict):
        errors.append("workflow phải là object")
        workflow = {}
    if workflow.get("protocol") != "http":
        errors.append("workflow.protocol phải là http")
    if workflow.get("application") != "nginx":
        errors.append("workflow.application phải là nginx")
    port = workflow.get("port")
    if not isinstance(port, int) or not (1024 <= port <= 65535):
        errors.append("workflow.port phải là unprivileged TCP port 1024..65535")
    directions = set(
        _nonempty_list(workflow.get("directions"), label="workflow.directions", errors=errors)
    )
    missing_directions = sorted(REQUIRED_DIRECTIONS - directions)
    if missing_directions:
        errors.append("workflow.directions thiếu: " + ", ".join(missing_directions))
    evidence = set(
        _nonempty_list(workflow.get("evidence"), label="workflow.evidence", errors=errors)
    )
    missing_evidence = sorted(REQUIRED_EVIDENCE - evidence)
    if missing_evidence:
        errors.append("workflow.evidence thiếu: " + ", ".join(missing_evidence))
    if not workflow.get("negative_test"):
        errors.append("workflow.negative_test bắt buộc")
    if not workflow.get("recovery"):
        errors.append("workflow.recovery bắt buộc")

    safety = manifest.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety phải là object")
        safety = {}
    for key in (
        "private_network_only",
        "dedicated_lab_hosts",
        "rollback_required",
        "cleanup_required",
    ):
        if safety.get(key) is not True:
            errors.append(f"safety.{key} phải true")

    for role_name, role, forbidden in (
        ("linux-peer", linux, FREEBSD_ONLY_LINUX),
        ("freebsd-peer", freebsd, LINUX_ONLY_FREEBSD),
    ):
        script = role.get("script") if isinstance(role, dict) else None
        if not isinstance(script, str) or not script:
            errors.append(f"{role_name}.script bắt buộc")
            continue
        path = root / script
        if not path.is_file():
            errors.append(f"{role_name}.script không tồn tại: {script}")
            continue
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if forbidden.search(stripped):
                errors.append(
                    f"{script}:{line_number}: command semantics sai platform: {stripped}"
                )

    sources = _nonempty_list(manifest.get("sources"), label="sources", errors=errors)
    if len(sources) < 2:
        errors.append("sources cần ít nhất 2 official/upstream URL")
    for source in sources:
        if not isinstance(source, str) or not source.startswith("https://"):
            errors.append("sources chỉ được chứa HTTPS URL")

    return errors


def run(*, json_output: bool = False) -> int:
    try:
        manifest = load_manifest()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"LỖI: không đọc được interoperability lab manifest: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(manifest)
    if json_output:
        print(
            json.dumps(
                {
                    "name": manifest.get("name"),
                    "platforms": sorted(REQUIRED_PLATFORMS),
                    "directions": manifest.get("workflow", {}).get("directions", []),
                    "differences": manifest.get("differences", []),
                    "errors": errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif errors:
        print(f"LỖI: interoperability lab có {len(errors)} vấn đề")
        for error in errors:
            print(f"- {error}")
    else:
        print("OK: Linux <-> FreeBSD interoperability lab contract pass.")
    return 1 if errors else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return run(json_output=args.json)


if __name__ == "__main__":
    raise SystemExit(main())

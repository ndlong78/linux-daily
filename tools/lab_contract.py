#!/usr/bin/env python3
"""Validate the machine-readable contract for Linux Daily lab posts."""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postmeta  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST_GLOB = os.path.join(ROOT, "posts", "post-*.html")
EFFECTIVE_FROM_ISSUE = 20
LAB_VERSION = 1
PROFILES = {"standard", "advanced"}
RISK_CLASSES = {
    "none",
    "lockout",
    "network-isolation",
    "downtime",
    "destructive-storage",
    "credential-exposure",
    "resource-pressure",
}
VERIFICATION_CLASSES = {
    "functional",
    "negative",
    "persistence",
    "recovery",
    "restore",
    "observability",
}
BASE_SECTIONS = {"scenario", "topology", "safety", "execution", "verification", "cleanup"}


@dataclass
class LabReport:
    total_labs: int = 0
    legacy_labs: int = 0
    enforced_labs: int = 0
    advanced_labs: int = 0
    risk_counts: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class LabSectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag != "section":
            return
        value = dict(attrs).get("data-lab-section", "").strip()
        if value:
            self.sections.append(value)


def _read_sections(path: str) -> list[str]:
    parser = LabSectionParser()
    with open(path, encoding="utf-8") as f:
        parser.feed(f.read())
    return parser.sections


def _is_lab(meta: dict) -> bool:
    eyebrow = str(meta.get("eyebrow", "")).casefold()
    return str(meta.get("axis", "")) == "Ôn tập" or "lab" in eyebrow or "lab" in meta


def _nonempty_string_list(value, *, label: str, rel: str, report: LabReport) -> list[str]:
    if not isinstance(value, list) or not value:
        report.errors.append(f"{rel}: {label} phải là list không rỗng")
        return []
    cleaned: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            report.errors.append(f"{rel}: {label} chỉ được chứa string không rỗng")
            continue
        cleaned.append(item.strip())
    if len(cleaned) != len(set(cleaned)):
        report.errors.append(f"{rel}: {label} có giá trị trùng")
    return cleaned


def _validate_lab(path: str, meta: dict, report: LabReport) -> None:
    rel = os.path.relpath(path, ROOT)
    issue = int(meta["issue"])
    lab = meta.get("lab")
    if not isinstance(lab, dict):
        report.errors.append(
            f"{rel}: lab từ #{EFFECTIVE_FROM_ISSUE:03d} phải có object ld-meta.lab"
        )
        return

    if lab.get("version") != LAB_VERSION:
        report.errors.append(f"{rel}: lab.version phải bằng {LAB_VERSION}")

    profile = lab.get("profile")
    if profile not in PROFILES:
        report.errors.append(f"{rel}: lab.profile phải thuộc {sorted(PROFILES)}")

    topology = _nonempty_string_list(
        lab.get("topology"), label="lab.topology", rel=rel, report=report
    )
    if profile == "advanced" and len(topology) < 2:
        report.errors.append(f"{rel}: advanced lab cần ít nhất 2 topology roles")

    risks = _nonempty_string_list(lab.get("risks"), label="lab.risks", rel=rel, report=report)
    unknown_risks = sorted(set(risks) - RISK_CLASSES)
    if unknown_risks:
        report.errors.append(f"{rel}: risk class không hợp lệ: {', '.join(unknown_risks)}")
    if "none" in risks and len(risks) > 1:
        report.errors.append(f"{rel}: risk 'none' không được đi cùng risk khác")
    for risk in risks:
        if risk in RISK_CLASSES:
            report.risk_counts[risk] = report.risk_counts.get(risk, 0) + 1

    verification = _nonempty_string_list(
        lab.get("verification"), label="lab.verification", rel=rel, report=report
    )
    unknown_verification = sorted(set(verification) - VERIFICATION_CLASSES)
    if unknown_verification:
        report.errors.append(
            f"{rel}: verification class không hợp lệ: {', '.join(unknown_verification)}"
        )
    if profile == "advanced" and len(verification) < 2:
        report.errors.append(f"{rel}: advanced lab cần ít nhất 2 verification classes")

    rollback_required = lab.get("rollback_required")
    cleanup_required = lab.get("cleanup_required")
    failure_injection = lab.get("failure_injection")
    for key, value in (
        ("rollback_required", rollback_required),
        ("cleanup_required", cleanup_required),
        ("failure_injection", failure_injection),
    ):
        if not isinstance(value, bool):
            report.errors.append(f"{rel}: lab.{key} phải là boolean")

    material_risk = bool(set(risks) - {"none"})
    if material_risk and rollback_required is not True:
        report.errors.append(f"{rel}: lab có risk thực tế nên rollback_required phải true")
    if profile == "advanced" and rollback_required is not True:
        report.errors.append(f"{rel}: advanced lab bắt buộc rollback_required=true")
    if cleanup_required is not True:
        report.errors.append(f"{rel}: lab bắt buộc cleanup_required=true")
    if failure_injection is True and "recovery" not in verification:
        report.errors.append(
            f"{rel}: failure_injection=true yêu cầu verification chứa 'recovery'"
        )
    if "destructive-storage" in risks and "restore" not in verification:
        report.errors.append(
            f"{rel}: destructive-storage yêu cầu verification chứa 'restore'"
        )
    if "resource-pressure" in risks:
        if failure_injection is not True:
            report.errors.append(
                f"{rel}: resource-pressure yêu cầu failure_injection=true để failure có scope/evidence rõ ràng"
            )
        if "observability" not in verification:
            report.errors.append(
                f"{rel}: resource-pressure yêu cầu verification chứa 'observability'"
            )
        if "recovery" not in verification:
            report.errors.append(
                f"{rel}: resource-pressure yêu cầu verification chứa 'recovery'"
            )

    sections = _read_sections(path)
    if len(sections) != len(set(sections)):
        report.errors.append(f"{rel}: data-lab-section không được lặp")
    required_sections = set(BASE_SECTIONS)
    if rollback_required is True:
        required_sections.add("rollback")
    if failure_injection is True:
        required_sections.add("failure-injection")
    missing_sections = sorted(required_sections - set(sections))
    if missing_sections:
        report.errors.append(
            f"{rel}: thiếu data-lab-section: {', '.join(missing_sections)}"
        )

    if issue >= EFFECTIVE_FROM_ISSUE:
        report.enforced_labs += 1
    if profile == "advanced":
        report.advanced_labs += 1


def review(post_paths: list[str] | None = None) -> LabReport:
    report = LabReport()
    paths = post_paths if post_paths is not None else sorted(glob.glob(POST_GLOB))
    for path in paths:
        try:
            meta = postmeta.read_meta(path)
        except (OSError, postmeta.MetaError) as exc:
            report.errors.append(str(exc))
            continue
        if not _is_lab(meta):
            continue
        report.total_labs += 1
        rel = os.path.relpath(path, ROOT)
        try:
            issue = int(meta.get("issue"))
        except (TypeError, ValueError):
            report.errors.append(f"{rel}: issue của lab phải là integer dương")
            continue
        if issue <= 0:
            report.errors.append(f"{rel}: issue của lab phải là integer dương")
            continue
        if issue < EFFECTIVE_FROM_ISSUE and "lab" not in meta:
            report.legacy_labs += 1
            continue
        _validate_lab(path, meta, report)
    return report


def structured(report: LabReport) -> dict:
    return {
        "effective_from_issue": EFFECTIVE_FROM_ISSUE,
        "total_labs": report.total_labs,
        "legacy_labs": report.legacy_labs,
        "enforced_labs": report.enforced_labs,
        "advanced_labs": report.advanced_labs,
        "risk_counts": dict(sorted(report.risk_counts.items())),
        "errors": report.errors,
    }


def run(*, json_output: bool = False) -> int:
    report = review()
    if json_output:
        print(json.dumps(structured(report), ensure_ascii=False, indent=2))
    else:
        print("Linux Daily — Advanced Lab Contract")
        print("=" * 35)
        print(f"effective_from_issue    #{EFFECTIVE_FROM_ISSUE:03d}")
        print(f"lab_posts               {report.total_labs}")
        print(f"legacy_labs             {report.legacy_labs}")
        print(f"enforced_labs           {report.enforced_labs}")
        print(f"advanced_labs           {report.advanced_labs}")
        print(f"errors                  {len(report.errors)}")
        for error in report.errors:
            print(f"LỖI: {error}", file=sys.stderr)
    return 1 if report.errors else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Xuất structured lab evidence.")
    args = parser.parse_args(argv)
    return run(json_output=args.json)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Contributor onboarding helper for Linux Daily."""
from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    "CONTRIBUTING.md",
    "docs/contributor-quickstart.md",
    "tools/publish.py",
    "taxonomy.json",
    "templates/post.template.html",
)


@dataclass
class DoctorReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def doctor(root: Path = ROOT) -> DoctorReport:
    report = DoctorReport()
    if sys.version_info < (3, 11):
        report.errors.append("Python 3.11+ is required")
    if shutil.which("git") is None:
        report.errors.append("git is required")
    if not (root / ".git").exists():
        report.warnings.append(".git directory not found; run this from a cloned repository")
    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            report.errors.append(f"required repository path is missing: {relative}")
    return report


def print_report(report: DoctorReport) -> None:
    if report.ok:
        print("OK: contributor environment baseline is ready.")
    else:
        print(f"FAIL: contributor doctor found {len(report.errors)} blocking issue(s).")
    for error in report.errors:
        print(f"- ERROR: {error}")
    for warning in report.warnings:
        print(f"- WARN: {warning}")
    if report.ok:
        print("Next: python3 -m pip install -e '.[dev]' && python3 tools/publish.py check")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("doctor",), nargs="?", default="doctor")
    parser.parse_args(argv)
    report = doctor()
    print_report(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

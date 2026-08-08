#!/usr/bin/env python3
"""Validate GitHub Actions workflows against Linux Daily safety boundaries."""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
RELEASE_WORKFLOW = "release.yml"
WRITE_PERMISSION_RE = re.compile(r"^\s{2}(contents|actions|pull-requests|issues|packages|deployments):\s*write\s*$", re.MULTILINE)


@dataclass
class Report:
    checked: int = 0
    errors: list[str] = field(default_factory=list)


def _event_block(text: str) -> str:
    match = re.search(r"(?ms)^on:\s*\n(.*?)(?=^[A-Za-z_-]+:\s*(?:\n|$))", text)
    return match.group(1) if match else ""


def _permissions_block(text: str) -> str:
    match = re.search(r"(?ms)^permissions:\s*\n(.*?)(?=^[A-Za-z_-]+:\s*(?:\n|$))", text)
    return match.group(1) if match else ""


def validate_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    errors: list[str] = []
    events = _event_block(text)
    permissions = _permissions_block(text)

    if "pull_request_target:" in text:
        errors.append(f"{rel}: pull_request_target is forbidden")
    if not permissions:
        errors.append(f"{rel}: top-level permissions block is required")

    writes = WRITE_PERMISSION_RE.findall(permissions)
    if path.name != RELEASE_WORKFLOW and writes:
        errors.append(f"{rel}: write permissions are forbidden outside {RELEASE_WORKFLOW}: {', '.join(writes)}")

    for banned in ("actions", "pull-requests", "issues", "packages", "deployments"):
        if re.search(rf"^\s{{2}}{re.escape(banned)}:\s*write\s*$", permissions, re.MULTILINE):
            errors.append(f"{rel}: {banned}: write is not allowed")

    if path.name == RELEASE_WORKFLOW:
        if "workflow_dispatch:" not in events:
            errors.append(f"{rel}: release must use workflow_dispatch")
        for forbidden_event in ("push:", "pull_request:", "schedule:", "workflow_run:"):
            if forbidden_event in events:
                errors.append(f"{rel}: release must not trigger on {forbidden_event[:-1]}")
        if not re.search(r"^\s{2}contents:\s*write\s*$", permissions, re.MULTILINE):
            errors.append(f"{rel}: release requires contents: write")
        if "Require explicit human confirmation" not in text:
            errors.append(f"{rel}: release explicit confirmation gate is missing")
        if "Block release unless CI and Production Smoke are green on this main SHA" not in text:
            errors.append(f"{rel}: exact-main-SHA release gate is missing")
        if "ref: main" not in text:
            errors.append(f"{rel}: release checkout must pin main")

    if re.search(r"\bgh\s+pr\s+merge\b", text) or "enable-auto-merge" in text:
        errors.append(f"{rel}: automatic PR merge commands are forbidden")
    if "--admin" in text and ("gh pr" in text or "branch protection" in text.lower()):
        errors.append(f"{rel}: branch-protection bypass/admin merge is forbidden")

    return errors


def run() -> Report:
    report = Report()
    paths = sorted([*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")])
    for path in paths:
        report.checked += 1
        report.errors.extend(validate_file(path))
    if not paths:
        report.errors.append("no GitHub Actions workflows found")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = run()
    if report.errors:
        print(f"FAIL: workflow safety found {len(report.errors)} issue(s)")
        for error in report.errors:
            print(f"- {error}")
        return 1
    print(f"OK: workflow safety policy passed for {report.checked} workflow(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

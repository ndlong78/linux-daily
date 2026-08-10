#!/usr/bin/env python3
"""Reject noisy PR history and temporary tracked artifacts."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUBJECTS = {
    "x",
    "tmp",
    "temp",
    "test",
    "wip",
    "placeholder",
    "fix",
    "update",
    "changes",
}
FORBIDDEN_SUBJECT_PREFIXES = ("wip:", "tmp:", "temp:", "placeholder:")
FORBIDDEN_PATH_RULES = (
    (
        re.compile(r"(^|/)[^/]+\.(?:tmp|bak|orig|rej)$", re.IGNORECASE),
        "temporary editor/migration artifact",
    ),
    (
        re.compile(
            r"^\.github/workflows/.*(?:finalize|finalizer).*\.ya?ml$",
            re.IGNORECASE,
        ),
        "self-mutating finalizer workflow",
    ),
    (
        re.compile(r"^tools/pr\d+_.*\.(?:py|sh)$", re.IGNORECASE),
        "PR-specific migration helper",
    ),
)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)


def validate_subjects(subjects: list[str]) -> list[str]:
    errors: list[str] = []
    for subject in subjects:
        normalized = " ".join(subject.split()).strip()
        lowered = normalized.lower()
        if not normalized:
            errors.append("commit subject must not be empty")
            continue
        if lowered in FORBIDDEN_SUBJECTS or lowered.startswith(
            FORBIDDEN_SUBJECT_PREFIXES
        ):
            errors.append(f"non-descriptive commit subject is forbidden: {normalized!r}")
    return errors


def validate_paths(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        normalized = path.strip().replace("\\", "/")
        if not normalized:
            continue
        for pattern, reason in FORBIDDEN_PATH_RULES:
            if pattern.search(normalized):
                errors.append(f"forbidden tracked path ({reason}): {normalized}")
                break
    return errors


def validate_branch(branch: str) -> list[str]:
    normalized = branch.strip()
    if not normalized:
        return ["PR preflight requires a named feature branch, not detached HEAD"]
    if normalized in {"main", "master"}:
        return [f"PR preflight must not run from protected branch {normalized!r}"]
    return []


def _git_lines(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def run(*, base: str | None = None, head: str | None = None) -> Report:
    report = Report()
    if bool(base) != bool(head):
        report.errors.append("--base and --head must be provided together")
        return report

    try:
        if base and head:
            subjects = _git_lines(["log", "--format=%s", f"{base}..{head}"])
            paths = _git_lines(["diff", "--name-only", f"{base}...{head}"])
            report.errors.extend(validate_subjects(subjects))
            report.errors.extend(validate_paths(paths))
        else:
            branch = (_git_lines(["branch", "--show-current"]) or [""])[0]
            report.errors.extend(validate_branch(branch))
            report.errors.extend(validate_paths(_git_lines(["ls-files"])))
    except RuntimeError as exc:
        report.errors.append(str(exc))
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base")
    parser.add_argument("--head")
    args = parser.parse_args(argv)
    report = run(base=args.base, head=args.head)
    if report.errors:
        print(f"FAIL: PR hygiene found {len(report.errors)} issue(s)")
        for error in report.errors:
            print(f"- {error}")
        return 1
    print("OK: PR commit/path hygiene passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

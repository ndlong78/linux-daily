#!/usr/bin/env python3
"""Reject noisy PR history, temporary artifacts and stale daily branches."""
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY_BRANCH_RE = re.compile(r"^chatgpt/linux-daily-[0-9]{3}-[0-9]{8}$")
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


def validate_daily_base(branch: str, *, base_is_ancestor: bool) -> list[str]:
    """Daily PRs must contain the current base commit in their own history.

    Maintenance branches may intentionally live across several main commits, but a
    daily article is deterministic output from the current contract. If current
    main is not an ancestor of the daily head, the branch was materialized from an
    older contract and must be updated/regenerated before merge.
    """
    normalized = branch.strip()
    if not DAILY_BRANCH_RE.fullmatch(normalized):
        return []
    if base_is_ancestor:
        return []
    return [
        f"daily branch {normalized!r} is stale relative to the current PR base; "
        "update it from current main and rematerialize artifacts before merge"
    ]


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


def _git_is_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    detail = result.stderr.strip() or result.stdout.strip() or "unknown git error"
    raise RuntimeError(
        f"git merge-base --is-ancestor {ancestor} {descendant} failed: {detail}"
    )


def run(
    *, base: str | None = None, head: str | None = None, branch: str | None = None
) -> Report:
    report = Report()
    if bool(base) != bool(head):
        report.errors.append("--base and --head must be provided together")
        return report
    if base and head and not branch:
        report.errors.append("--branch is required with --base/--head")
        return report

    try:
        if base and head:
            subjects = _git_lines(["log", "--format=%s", f"{base}..{head}"])
            paths = _git_lines(["diff", "--name-only", f"{base}...{head}"])
            report.errors.extend(validate_subjects(subjects))
            report.errors.extend(validate_paths(paths))
            report.errors.extend(
                validate_daily_base(
                    branch or "",
                    base_is_ancestor=_git_is_ancestor(base, head),
                )
            )
        else:
            current_branch = (_git_lines(["branch", "--show-current"]) or [""])[0]
            report.errors.extend(validate_branch(current_branch))
            report.errors.extend(validate_paths(_git_lines(["ls-files"])))
    except RuntimeError as exc:
        report.errors.append(str(exc))
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--branch")
    args = parser.parse_args(argv)
    report = run(base=args.base, head=args.head, branch=args.branch)
    if report.errors:
        print(f"FAIL: PR hygiene found {len(report.errors)} issue(s)")
        for error in report.errors:
            print(f"- {error}")
        return 1
    print("OK: PR commit/path hygiene passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

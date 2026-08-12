#!/usr/bin/env python3
"""Materialize publish artifacts and run all local checks before opening/updating a PR.

The preflight intentionally starts with ``publish.py prepare`` so a new article
cannot reach commit/push with stale generated pages, reports, navigation or site
metadata. Semantic source metadata (learning metadata/path and curriculum queue)
must already be valid; ``prepare`` fails early when that contract is incomplete.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def command_plan() -> list[list[str]]:
    return [
        [PYTHON, "tools/publish.py", "prepare"],
        [PYTHON, "tools/pr_hygiene.py"],
        ["ruff", "check", "tools/", "tests/"],
        [PYTHON, "-m", "pytest"],
        [PYTHON, "tools/workflow_safety.py"],
        [PYTHON, "tools/publish.py", "check"],
    ]


def run(*, runner=subprocess.run) -> int:
    commands = command_plan()
    print("Linux Daily PR preflight")
    print("=" * 24)
    for index, command in enumerate(commands, start=1):
        print(f"[{index}/{len(commands)}] {' '.join(command)}")
        result = runner(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            print(
                f"FAIL: preflight step {index} trả về exit code {result.returncode}.",
                file=sys.stderr,
            )
            return result.returncode or 1
    print("OK: PR preflight pass. Commit toàn bộ source + generated artifacts rồi mới push/mở PR.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

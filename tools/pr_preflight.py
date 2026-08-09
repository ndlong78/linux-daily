#!/usr/bin/env python3
"""Run the local checks that must pass before opening or updating a PR."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def command_plan() -> list[list[str]]:
    return [
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
    print("OK: PR preflight pass. Có thể mở/cập nhật PR và theo dõi GitHub Actions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

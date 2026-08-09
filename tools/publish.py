#!/usr/bin/env python3
"""One-command local publish orchestration for Linux Daily.

Modes:
  prepare  Regenerate deterministic site/report artifacts after editing a post.
  check    Run all deterministic local publish gates without modifying files.

External HTTP checks intentionally remain in CI so local publishing does not depend on network state.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def command_plan(mode: str) -> list[list[str]]:
    if mode == "prepare":
        return [
            [PYTHON, "tools/build.py"],
            [PYTHON, "tools/learning_dashboard.py"],
            [PYTHON, "tools/content_mix.py"],
            [PYTHON, "tools/taxonomy.py"],
            [PYTHON, "tools/distro_coverage.py"],
            [PYTHON, "tools/quality_dashboard.py"],
        ]
    if mode == "check":
        return [
            [PYTHON, "tools/build.py", "--check"],
            [PYTHON, "tools/taxonomy.py"],
            [PYTHON, "tools/content_mix.py", "--check"],
            [PYTHON, "tools/curriculum_planner.py"],
            [PYTHON, "tools/publication_readiness.py"],
            [PYTHON, "tools/coverage_intelligence.py", "--check"],
            [PYTHON, "tools/distro_coverage.py", "--check"],
            [PYTHON, "tools/command_quality.py"],
            [PYTHON, "tools/content_freshness.py"],
            [PYTHON, "tools/content_lifecycle.py"],
            [PYTHON, "tools/quality_dashboard.py", "--check"],
            [PYTHON, "tools/learning_metadata.py"],
            [PYTHON, "tools/topic_progression.py"],
            [PYTHON, "tools/learning_dashboard.py", "--check"],
            [PYTHON, "tools/lab_contract.py"],
            [PYTHON, "tools/interoperability_lab.py"],
            [PYTHON, "tools/release.py", "validate"],
            [PYTHON, "tools/performance_budget.py"],
            [PYTHON, "tools/repo_health.py"],
        ]
    raise ValueError(f"unsupported publish mode: {mode}")


def run(mode: str, *, runner=subprocess.run) -> int:
    commands = command_plan(mode)
    print(f"Linux Daily publish pipeline — {mode}")
    print("=" * 39)
    for index, command in enumerate(commands, start=1):
        printable = " ".join(command)
        print(f"[{index}/{len(commands)}] {printable}")
        result = runner(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            print(f"FAIL: bước {index} trả về exit code {result.returncode}.", file=sys.stderr)
            return result.returncode or 1
    print(f"OK: publish pipeline `{mode}` hoàn tất.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "check"))
    args = parser.parse_args(argv)
    return run(args.mode)


if __name__ == "__main__":
    raise SystemExit(main())

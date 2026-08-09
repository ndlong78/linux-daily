#!/usr/bin/env python3
"""Temporary PR83 source-link repair wrapper; restores canonical tool before verification."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parent.parent
TMP = HERE.with_name(".pr83_backfill_site_metadata_original.py")
POST = ROOT / "posts" / "post-038-smart-nvme-health-disk-degradation.html"
OLD_URL = "https://www.smartmontools.org/wiki/SmartctlNvmeAttrs"
NEW_URL = "https://www.smartmontools.org/static/doxygen/structsmartmontools_1_1nvme__smart__log.html"


def load_original() -> bytes:
    result = subprocess.run(
        ["git", "show", "origin/main:tools/backfill_site_metadata.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    original = result.stdout
    TMP.write_bytes(original)
    return original


def repair_source_link() -> None:
    text = POST.read_text(encoding="utf-8")
    if OLD_URL not in text:
        return
    POST.write_text(text.replace(OLD_URL, NEW_URL), encoding="utf-8")


def main() -> int:
    original = load_original()
    try:
        proc = subprocess.run([sys.executable, str(TMP), *sys.argv[1:]], cwd=ROOT)
        if proc.returncode == 0 and "--check" not in sys.argv:
            repair_source_link()
        return proc.returncode
    finally:
        HERE.write_bytes(original)
        TMP.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())

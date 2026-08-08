from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "pr68-prepared.tgz"


def test_pr68_dump_deterministic_prepare_outputs():
    subprocess.run([sys.executable, "tools/publish.py", "prepare"], cwd=ROOT, check=True)
    changed = subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=ROOT, text=True
    ).splitlines()
    assert changed

    with tarfile.open(ARCHIVE, mode="w:gz") as archive:
        for relative in changed:
            path = ROOT / relative
            if path.is_file():
                archive.add(path, arcname=relative)

    print("PR68_PREPARE_FILES=" + ",".join(changed))
    raise AssertionError("intentional diagnostic dump; remove after syncing artifacts")

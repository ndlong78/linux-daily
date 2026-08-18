#!/usr/bin/env python3
"""Guard cho workflow materialize-artifacts.

Workflow dispatch chạy `tools/publish.py prepare` trên feature branch rồi commit
artifact dẫn xuất. Guard này giữ nó đúng phạm vi:

  1. branch phải là branch bài hằng ngày, không bao giờ là `main`;
  2. thay đổi do generator sinh ra không được đụng vào source of truth, tooling
     hay cấu hình CI.

Dùng deny-list chứ không allow-list: danh sách output của generator thay đổi theo
thời gian, còn tập file "generator tuyệt đối không được ghi" thì ổn định. Nếu một
generator nào đó bắt đầu ghi vào `topics.md` hay `tools/`, workflow phải dừng chứ
không im lặng commit.

Dùng:
  python3 tools/materialize_guard.py --branch <ref>
  python3 tools/materialize_guard.py --branch <ref> --changed-from-git
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DAILY_BRANCH_RE = re.compile(r"^chatgpt/linux-daily-[0-9]{3}-[0-9]{8}$")

# Source of truth do agent/người viết. Generator chỉ đọc, không bao giờ ghi.
PROTECTED_FILES = frozenset({
    "topics.md",
    "state.json",
    "site.json",
    "AGENTS.md",
    "STYLE.md",
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "VERSION",
    "pyproject.toml",
})

# Tooling và cấu hình CI. Một workflow có contents:write không được tự sửa
# chính bộ kiểm định đang gác nó.
PROTECTED_DIRS = ("tools/", "tests/", ".github/", "templates/", "assets/", "labs/")


def validate_branch(branch: str) -> list[str]:
    ref = branch.strip().removeprefix("refs/heads/")
    if not ref:
        return ["materialize cần tên branch cụ thể"]
    if ref in {"main", "master"}:
        return [f"materialize không được chạy trên branch được bảo vệ: {ref!r}"]
    if not DAILY_BRANCH_RE.match(ref):
        return [f"branch {ref!r} không khớp ^chatgpt/linux-daily-NNN-YYYYMMDD$"]
    return []


def validate_changed_paths(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for raw in paths:
        path = raw.strip().replace("\\", "/")
        if not path:
            continue
        if path in PROTECTED_FILES:
            errors.append(f"generator không được sửa source of truth: {path}")
            continue
        for prefix in PROTECTED_DIRS:
            if path.startswith(prefix):
                errors.append(f"generator không được sửa tooling/CI: {path}")
                break
    return errors


def _changed_from_git() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown git error"
        raise RuntimeError(f"git status failed: {detail}")
    # Dòng porcelain dạng "XY <path>"; đổi tên hiếm gặp ở đây nhưng vẫn xử lý.
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        entry = line[3:]
        paths.append(entry.split(" -> ", 1)[-1] if " -> " in entry else entry)
    return paths


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Guard phạm vi cho materialize-artifacts.")
    ap.add_argument("--branch", required=True, help="Branch mà workflow đang chạy trên đó.")
    ap.add_argument(
        "--changed-from-git",
        action="store_true",
        help="Đọc danh sách file thay đổi từ `git status --porcelain`.",
    )
    args = ap.parse_args(argv)

    errors = validate_branch(args.branch)
    if args.changed_from_git:
        errors.extend(validate_changed_paths(_changed_from_git()))

    if errors:
        print(f"✗ materialize guard: {len(errors)} lỗi", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK: materialize guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

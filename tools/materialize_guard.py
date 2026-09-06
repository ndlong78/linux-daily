#!/usr/bin/env python3
"""Guard cho workflow materialize-artifacts.

Workflow dispatch chạy `tools/publish.py prepare` trên feature branch rồi commit
artifact dẫn xuất. Guard này giữ nó đúng phạm vi:

  1. branch phải là branch bài hằng ngày, không bao giờ là `main`;
  2. thay đổi do generator sinh ra không được đụng vào source of truth, tooling
     hay cấu hình CI.

Chỉ cho phép artifact mà publish.py prepare đang sinh. Metadata nguồn, tooling,
config và đường dẫn mới chưa được review đều bị từ chối; thêm output mới phải
cập nhật contract này cùng generator trong maintenance PR.

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
    "curriculum-plan.json",
    "coverage-catalog.json",
    "freshness.json",
    "learning-metadata.json",
    "learning-paths.json",
    "taxonomy.json",
})

# Tooling và cấu hình CI. Một workflow có contents:write không được tự sửa
# chính bộ kiểm định đang gác nó.
PROTECTED_DIRS = ("tools/", "tests/", ".github/", "templates/", "assets/", "labs/")

GENERATED_FILES = frozenset({
    "index.html", "archive.html", "feed.xml", "sitemap.xml", "robots.txt",
    "search-index.json", "learning-paths.html", "learning-dashboard.html",
    "docs/content-mix-report.md", "docs/distro-coverage-report.md", "docs/quality-dashboard.md",
})
GENERATED_PATH_RE = re.compile(r"(?:trang-[2-9][0-9]*\.html|trang-1[0-9]+\.html|posts/post-[0-9]{3}-[a-z0-9-]+\.html)\Z")


def is_generated_path(path: str) -> bool:
    return path in GENERATED_FILES or GENERATED_PATH_RE.fullmatch(path) is not None


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
        path = raw
        if not path:
            continue
        if path in PROTECTED_FILES:
            errors.append(f"generator không được sửa source of truth: {path}")
            continue
        if path.startswith(PROTECTED_DIRS):
            errors.append(f"generator không được sửa tooling/CI: {path}")
        elif not is_generated_path(path):
            errors.append(f"generator không được sửa đường dẫn ngoài artifact contract: {path}")
    return errors


def _changed_from_git() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "-z", "--untracked-files=all"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown git error"
        raise RuntimeError(f"git status failed: {detail}")
    # -z giữ nguyên tên có Unicode/khoảng trắng. Rename ghi destination trước,
    # source sau; phải kiểm cả hai để không lọt việc chuyển metadata sang output.
    paths: list[str] = []
    entries = iter(result.stdout.split("\0"))
    for entry in entries:
        if not entry:
            continue
        paths.append(entry[3:])
        if "R" in entry[:2] or "C" in entry[:2]:
            source = next(entries, "")
            if not source:
                raise RuntimeError("git status returned an incomplete rename/copy")
            paths.append(source)
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
        changed = _changed_from_git()
        errors.extend(validate_changed_paths(changed))
        errors.extend(f"artifact không được là symlink: {path}" for path in changed if (ROOT / path).is_symlink())

    if errors:
        print(f"✗ materialize guard: {len(errors)} lỗi", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK: materialize guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

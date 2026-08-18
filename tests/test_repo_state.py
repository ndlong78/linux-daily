"""Kiểm tra trạng thái repo thật: quality gate đạt và index.html đã đồng bộ.

Đây là "meta test" — bảo đảm mọi lần chạy CI đều xác nhận repo hiện tại sạch,
độc lập với các unit test dùng dữ liệu giả bên dưới.
"""
import os
import subprocess
from pathlib import Path

import build_index
import validate_repo

ROOT = Path(__file__).resolve().parents[1]


def test_quality_gate_passes_on_real_repo():
    report = validate_repo.run()
    assert report.errors == [], "Quality gate còn lỗi:\n" + "\n".join(report.errors)


def test_index_html_in_sync():
    out, _ = build_index.render_index()
    with open(build_index.INDEX_PATH, encoding="utf-8") as f:
        current = f.read()
    assert current == out, "index.html chưa được dựng lại; chạy tools/build_index.py."


# --- Regression: tên file chỉ khác nhau ở hoa/thường ---


def _tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def test_exactly_one_pull_request_template():
    """Repo từng có cả PULL_REQUEST_TEMPLATE.md lẫn pull_request_template.md với
    nội dung khác nhau, nên GitHub chọn bản nào là không xác định."""
    templates = [
        path for path in _tracked_paths()
        if os.path.basename(path).lower() == "pull_request_template.md"
    ]
    assert len(templates) == 1, f"cần đúng một PR template, đang có: {templates}"


def test_no_tracked_paths_collide_when_lowercased():
    """Hai path chỉ khác nhau ở hoa/thường sẽ đụng nhau khi checkout trên
    filesystem không phân biệt hoa thường (macOS, Windows)."""
    buckets: dict[str, list[str]] = {}
    for path in _tracked_paths():
        buckets.setdefault(path.lower(), []).append(path)
    collisions = {key: paths for key, paths in buckets.items() if len(paths) > 1}
    assert not collisions, f"path đụng nhau khi lowercase: {collisions}"

"""Test hành vi cho assets/search.js (chạy qua Node với DOM giả).

Chỉ mục tìm kiếm phải được chuẩn hóa MỘT lần cho mỗi bài lúc tải, thay vì tính lại
theo từng term × từng bài × từng keystroke. Site tăng 1 bài/ngày nên chi phí cũ tăng
tuyến tính theo số bài trên mỗi phím gõ.

Node không phải dependency bắt buộc của repo (pipeline là Python thuần), nên test tự
skip khi không có node.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "js" / "search_harness.mjs"
SEARCH_JS = ROOT / "assets" / "search.js"

POST_COUNT = 200
KEYSTROKES = 5


def _run_harness(
    post_count: int = POST_COUNT,
    keystrokes: int = KEYSTROKES,
    query: str = "tường",
    title: str = "Cấu hình tường lửa",
    initial_query: str = "",
) -> dict:
    node = shutil.which("node")
    if node is None:  # pragma: no cover - phụ thuộc môi trường
        pytest.skip("cần Node để chạy harness cho search.js")
    result = subprocess.run(
        [node, str(HARNESS), str(SEARCH_JS), str(post_count), str(keystrokes),
         query, title, initial_query],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"harness lỗi: {result.stderr.strip()}"
    return json.loads(result.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def harness() -> dict:
    return _run_harness()


def test_search_index_is_normalized_once_per_post_at_load(harness):
    """Chuẩn hóa chạy đúng một lần cho mỗi bài khi tải chỉ mục."""
    assert harness["afterLoad"] == POST_COUNT


def test_typing_does_not_renormalize_every_post(harness):
    """Gõ phím không được kéo theo chi phí O(số bài).

    Bản cũ gọi haystack(post) bên trong filter: 5 keystroke × 200 bài = 1005 lần
    chuẩn hóa. Bản mới chỉ chuẩn hóa thêm chuỗi truy vấn.
    """
    extra = harness["total"] - harness["afterLoad"]
    assert extra <= KEYSTROKES, f"gõ {KEYSTROKES} phím tốn thêm {extra} lần chuẩn hóa"
    assert harness["total"] < POST_COUNT + KEYSTROKES + 5


def test_search_still_returns_correct_matches(harness):
    """Tối ưu không được đổi kết quả: chỉ 1 bài khớp 'tường'."""
    assert harness["rendered"] == 1
    assert "1 kết quả" in harness["statusText"]


@pytest.mark.parametrize("query", ["điều hướng", "dieu huong", "ĐIỀU HƯỚNG", "DIEU HUONG", "huong dieu"])
def test_search_matches_are_diacritic_insensitive(query):
    """Cùng bài phải tìm được với đ/d, dấu tiếng Việt và nhiều từ đảo thứ tự."""
    out = _run_harness(10, len(query), query, "Điều hướng thư mục")
    assert out["rendered"] == 1
    assert out["groupsHidden"] is True


def test_search_without_stroked_d_keeps_other_vietnamese_accents():
    out = _run_harness(10, 10, "tuong lua")
    assert out["rendered"] == 1


def test_no_match_has_empty_results_and_keeps_query_status():
    out = _run_harness(10, 7, "xyznone")
    assert out["rendered"] == 0
    assert "0 kết quả" in out["statusText"]


def test_clearing_query_restores_archive():
    out = _run_harness(10, 1, "", initial_query="tường")
    assert out["rendered"] == 0
    assert out["groupsHidden"] is False
    assert out["resultsHidden"] is True
    assert "10 bài" in out["statusText"]


def test_query_entered_before_index_load_is_applied():
    out = _run_harness(10, 0, title="Điều hướng thư mục", initial_query="dieu huong")
    assert out["rendered"] == 1
    assert "dieu huong" in out["statusText"]

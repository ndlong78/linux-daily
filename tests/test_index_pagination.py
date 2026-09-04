"""Phân trang trang chủ: không được đánh rơi bài, không được để trang mồ côi.

index.html trước đây liệt kê MỌI bài và tăng 0.570 KiB/bài (đo trên 5 mốc git từ
#044 tới #065). Ngân sách `homepage_html` 256 KiB nằm trong `publish.py check`,
nên ở khoảng bài #435 nó sẽ chặn cứng việc ra bài. Phân trang gỡ trần đó, nhưng
đổi lại đưa vào hai rủi ro mới mà bộ test này gác:

  1. một bài rơi khỏi mọi trang → độc giả và crawler không tới được;
  2. chuỗi trang đứt mắt → các bài phía sau thành mồ côi.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_index  # noqa: E402


def _pages() -> dict[str, str]:
    pages, _ = build_index.render_pages()
    return pages


def test_moi_bai_xuat_hien_dung_mot_lan_tren_toan_chuoi():
    """Bất biến quan trọng nhất: phân trang là chia lại, không phải làm mất."""
    posts = build_index.collect_posts()
    gop = "".join(_pages().values())

    thieu = [p["href"] for p in posts if gop.count(f'href="{p["href"]}"') != 1]
    assert not thieu, f"bài rơi khỏi chuỗi trang hoặc bị lặp: {thieu}"


def test_trang_dau_van_la_index_html():
    """URL trang chủ đã publish; đổi nó là làm hỏng mọi link trỏ tới site."""
    assert build_index.page_name(1) == "index.html"
    assert "index.html" in _pages()


def test_khong_trang_nao_vuot_so_bai_moi_trang():
    for name, content in _pages().items():
        n = content.count('class="card" href="posts/')
        assert n <= build_index.POSTS_PER_PAGE, f"{name} có {n} bài"


def test_chuoi_trang_di_duoc_tu_dau_toi_cuoi():
    """Đứt một mắt là các bài phía sau thành mồ côi mà file vẫn còn đủ."""
    pages = _pages()
    ten = [build_index.page_name(i) for i in range(1, len(pages) + 1)]
    for hien_tai, ke_tiep in zip(ten, ten[1:], strict=False):
        assert f'href="{ke_tiep}"' in pages[hien_tai], f"{hien_tai} không trỏ tới {ke_tiep}"
    assert 'rel="next"' not in pages[ten[-1]], "trang cuối không được có next"
    assert 'rel="prev"' not in pages[ten[0]], "trang đầu không được có prev"


def test_canonical_cua_moi_trang_la_rieng():
    """Trùng canonical giữa các trang là tự báo với search engine rằng chúng là một."""
    import re

    found = [
        re.search(r'<link rel="canonical" href="([^"]+)"', c).group(1)
        for c in _pages().values()
    ]
    assert len(set(found)) == len(found), f"canonical trùng nhau: {found}"


def test_kho_rong_van_cho_dung_mot_trang(tmp_path):
    """Kho rỗng không được sinh 0 trang — index.html phải luôn tồn tại."""
    trong = tmp_path / "posts"
    trong.mkdir()
    pages, count = build_index.render_pages(posts_dir=str(trong))
    assert count == 0
    assert list(pages) == ["index.html"]
    assert "pagination" not in pages["index.html"]


def test_phat_hien_trang_thua_khi_series_ngan_lai(tmp_path):
    """Bỏ bài đi mà không dọn trang-N.html thì còn lại trang mồ côi."""
    for name in ("trang-2.html", "trang-9.html"):
        (tmp_path / name).write_text("x", encoding="utf-8")

    thua = build_index.stale_pages({"index.html": "", "trang-2.html": ""}, root=str(tmp_path))
    assert thua == ["trang-9.html"]

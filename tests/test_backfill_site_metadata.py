"""Cổng metadata/social: phải đỏ khi lệch, và phải nói LỆCH GÌ.

Bài #055 lên production với og/twitter:description khác meta.lede. Hai lý do,
bộ test này canh cả hai:

1. `backfill_site_metadata.py` — tool duy nhất sinh og/twitter từ meta.lede —
   không nằm trong `publish.py prepare`, nên materialize không bao giờ tự sửa.
   Canh ở `tests/test_publish.py`.
2. Khi nó có đỏ thì cũng chỉ in tên file, nên người đọc log đi chẩn đoán nhầm.
   Canh ở đây.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import backfill_site_metadata as backfill  # noqa: E402


def test_khong_lech_thi_khong_bao_gi():
    assert backfill.describe_drift("a\nb\n", "a\nb\n") == []


def test_bao_dung_dong_og_description_lech():
    """Đúng hình dạng lỗi của #055: og:description giữ bản cũ, meta.lede đã đổi."""
    current = '<meta property="og:description" content="câu cũ">\n<p>thân bài</p>'
    expected = '<meta property="og:description" content="câu mới">\n<p>thân bài</p>'

    drift = backfill.describe_drift(current, expected)

    assert any(line.startswith("-") and "câu cũ" in line for line in drift)
    assert any(line.startswith("+") and "câu mới" in line for line in drift)
    assert all("thân bài" not in line for line in drift), "dòng không lệch thì đừng in"


def test_cat_bot_dong_qua_dai():
    """og:description dài hơn 200 ký tự là chuyện thường; log CI không nên bị ngập."""
    current = "x" * 400
    expected = "y" * 400

    for line in backfill.describe_drift(current, expected):
        assert len(line) <= backfill.MAX_DRIFT_WIDTH + 2


def test_gioi_han_so_dong_va_noi_ro_con_bao_nhieu():
    current = "\n".join(f"cũ {i}" for i in range(40))
    expected = "\n".join(f"mới {i}" for i in range(40))

    drift = backfill.describe_drift(current, expected)

    assert len(drift) == backfill.MAX_DRIFT_LINES + 1
    assert "còn" in drift[-1] and "dòng lệch nữa" in drift[-1]


def test_kho_hien_tai_dang_dong_bo():
    """Nếu test này đỏ, đừng sửa test — chạy `python tools/backfill_site_metadata.py`."""
    assert backfill.run(check=True) == 0

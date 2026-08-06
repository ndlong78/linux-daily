"""Kiểm tra trạng thái repo thật: quality gate đạt và index.html đã đồng bộ.

Đây là "meta test" — bảo đảm mọi lần chạy CI đều xác nhận repo hiện tại sạch,
độc lập với các unit test dùng dữ liệu giả bên dưới.
"""
import build_index
import validate_repo


def test_quality_gate_passes_on_real_repo():
    report = validate_repo.run()
    assert report.errors == [], "Quality gate còn lỗi:\n" + "\n".join(report.errors)


def test_index_html_in_sync():
    out, _ = build_index.render_index()
    with open(build_index.INDEX_PATH, encoding="utf-8") as f:
        current = f.read()
    assert current == out, "index.html chưa được dựng lại; chạy tools/build_index.py."

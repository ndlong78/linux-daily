from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import backfill_fonts  # noqa: E402
import validate_fonts  # noqa: E402


def test_font_backfill_removes_google_and_is_idempotent():
    source = """<head>\n<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n<link href=\"https://fonts.googleapis.com/css2?family=Example\" rel=\"stylesheet\">\n<link rel=\"stylesheet\" href=\"../assets/style.css\">\n</head>\n"""
    expected = backfill_fonts.transform(source)
    assert "fonts.googleapis.com" not in expected
    assert "fonts.gstatic.com" not in expected
    assert '../assets/fonts.css' in expected
    assert '../assets/fonts/be-vietnam-pro-800.woff2' in expected
    assert backfill_fonts.transform(expected) == expected


def test_self_host_font_gate_passes_repository():
    report = validate_fonts.run()
    assert report.errors == []


def test_templates_do_not_reference_google_fonts():
    for path in (ROOT / "templates" / "index.template.html", ROOT / "templates" / "post.template.html"):
        text = path.read_text(encoding="utf-8")
        assert "fonts.googleapis.com" not in text
        assert "fonts.gstatic.com" not in text


def test_transform_is_idempotent_for_a_post_without_preload():
    """Bài chỉ có fonts.css (chưa có preload) không được nhận link thứ hai.

    Hình dạng này đã làm hỏng #084: transform() cũ chỉ xoá được khối byte-exact
    preload+fonts.css, nên fonts.css đứng một mình sống sót và bài nhận thêm một
    khối nữa — rồi validate_fonts chặn chính artifact mà generator vừa tạo.
    """
    import backfill_fonts

    source = (
        '<head><link rel="stylesheet" href="../assets/fonts.css">'
        '<link rel="stylesheet" href="../assets/style.css"></head>'
    )
    once = backfill_fonts.transform(source)
    assert once.count('href="../assets/fonts.css"') == 1
    assert once.count('be-vietnam-pro-800.woff2') == 1
    assert backfill_fonts.transform(once) == once


def test_transform_survives_a_minified_head():
    """<head> nén một dòng vẫn phải ra đúng một khối font."""
    import backfill_fonts

    source = (
        '<head><title>x</title><link rel="preload" '
        'href="../assets/fonts/be-vietnam-pro-800.woff2" as="font" type="font/woff2" '
        'crossorigin><link rel="stylesheet" href="../assets/fonts.css">'
        '<link rel="stylesheet" href="../assets/style.css"></head>'
    )
    out = backfill_fonts.transform(source)
    assert out.count('href="../assets/fonts.css"') == 1
    assert out.count('be-vietnam-pro-800.woff2') == 1
    assert backfill_fonts.transform(out) == out

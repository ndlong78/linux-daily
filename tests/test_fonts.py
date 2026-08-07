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

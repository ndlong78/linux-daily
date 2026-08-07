from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import backfill_accessibility  # noqa: E402
import validate_accessibility  # noqa: E402


def test_backfill_transform_is_idempotent():
    source = '<body class="post">\n<div class="wrap">x</div>\n</body>'
    once = backfill_accessibility.transform(source)
    twice = backfill_accessibility.transform(once)
    assert once == twice
    assert once.count('class="skip-link"') == 1
    assert once.count('<main id="main-content">') == 1


def test_accessibility_gate_passes_on_real_repo():
    report = validate_accessibility.run()
    assert report.errors == [], "Accessibility gate còn lỗi:\n" + "\n".join(report.errors)


def test_post_template_contains_accessibility_baseline():
    template = (ROOT / "templates" / "post.template.html").read_text(encoding="utf-8")
    assert 'class="skip-link" href="#main-content"' in template
    assert '<main id="main-content">' in template


def test_index_template_contains_accessibility_baseline():
    template = (ROOT / "templates" / "index.template.html").read_text(encoding="utf-8")
    assert 'class="skip-link" href="#main-content"' in template
    assert 'id="main-content"' in template


def test_skip_link_has_keyboard_visible_css():
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    assert ".skip-link" in css
    assert ".skip-link:focus" in css
    assert ":focus-visible" in css

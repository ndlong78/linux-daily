from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import backfill_navigation  # noqa: E402


def test_shared_navigation_has_four_destinations_and_current_state():
    home = backfill_navigation._env().get_template("_global-nav.template.html").render(
        nav_prefix="", nav_current="home"
    )
    for href in (
        "index.html",
        "learning-paths.html",
        "learning-dashboard.html",
        "archive.html",
    ):
        assert f'href="{href}"' in home
    assert home.count('aria-current="page"') == 1
    assert 'href="index.html" aria-current="page"' in home


def test_post_navigation_uses_parent_prefix_and_is_idempotent():
    source = '<body class="post">\n<div class="wrap">\n<header class="post"></header>\n</div>'
    first = backfill_navigation.transform(source)
    second = backfill_navigation.transform(first)
    assert first == second
    assert 'href="../index.html"' in first
    assert 'href="../learning-paths.html"' in first
    assert 'href="../learning-dashboard.html"' in first
    assert 'href="../archive.html"' in first
    assert 'aria-current="page"' not in first


def test_back_to_top_control_is_shared_accessible_and_progressive():
    home = backfill_navigation._env().get_template("_global-nav.template.html").render(
        nav_prefix="", nav_current="home"
    )
    assert 'id="page-top"' in home
    assert home.count('class="back-to-top"') == 1
    assert 'href="#page-top"' in home
    assert 'aria-label="Lên đầu trang"' in home
    assert 'aria-hidden="true">↑</span>' in home
    assert 'src="assets/back-to-top.js"' in home

    post = backfill_navigation.render_navigation(prefix="../")
    assert 'src="../assets/back-to-top.js"' in post

    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    assert ".back-to-top{" in css
    assert ".back-to-top-enhanced .back-to-top.is-visible" in css
    assert "scroll-behavior:smooth" in css

    script = (ROOT / "assets" / "back-to-top.js").read_text(encoding="utf-8")
    assert "window.scrollY > 480" in script
    assert 'classList.toggle("is-visible"' in script

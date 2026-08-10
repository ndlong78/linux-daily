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


def test_global_nav_is_the_single_visible_top_brand():
    for path in (ROOT / "index.html", ROOT / "archive.html", ROOT / "learning-dashboard.html"):
        html = path.read_text(encoding="utf-8")
        assert html.count('class="global-nav-brand"') == 1
        assert 'class="site-brand"' not in html

    learning_html = (ROOT / "learning-paths.html").read_text(encoding="utf-8")
    learning_css = (ROOT / "assets" / "learning-paths.css").read_text(encoding="utf-8")
    assert learning_html.count('class="global-nav-brand"') == 1
    assert 'body.learning .site-brand{display:none}' in learning_css

    post_template = (ROOT / "templates" / "post.template.html").read_text(
        encoding="utf-8"
    )
    assert '>← Linux Daily</a>' not in post_template
    assert 'aria-label="Về trang chủ Linux Daily">←</a>' in post_template

    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    assert 'body.post .brand-home{font-size:0;letter-spacing:0}' in css
    assert 'body.post .brand-home::before{content:"←";font-size:13px;letter-spacing:0}' in css

#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise RuntimeError(f"{path}: không tìm thấy marker cần thay")
    write(path, text.replace(old, new, 1))


NAV_PARTIAL = '''<nav class="global-nav" aria-label="Điều hướng chính">
  <a class="global-nav-brand" href="{{ nav_prefix }}index.html"{% if nav_current == "home" %} aria-current="page"{% endif %}>Linux Daily</a>
  <div class="global-nav-links">
    <a href="{{ nav_prefix }}learning-paths.html"{% if nav_current == "paths" %} aria-current="page"{% endif %}>Lộ trình học</a>
    <a href="{{ nav_prefix }}learning-dashboard.html"{% if nav_current == "dashboard" %} aria-current="page"{% endif %}>Tổng quan</a>
    <a href="{{ nav_prefix }}archive.html"{% if nav_current == "archive" %} aria-current="page"{% endif %}>Tìm kiếm</a>
  </div>
</nav>
'''

BACKFILL = '''#!/usr/bin/env python3
"""Deterministically backfill the shared global navigation into post HTML."""
from __future__ import annotations

import argparse
import glob
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "templates"
NAV_TEMPLATE = "_global-nav.template.html"
POST_TEMPLATE = ROOT / "templates" / "post.template.html"
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
NAV_RE = re.compile(r'<nav class="global-nav"\\b.*?</nav>\\n?', re.DOTALL)


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def render_navigation(prefix: str = "../", current: str = "") -> str:
    return _env().get_template(NAV_TEMPLATE).render(
        nav_prefix=prefix,
        nav_current=current,
    ).strip()


def transform(text: str) -> str:
    marker = '<div class="wrap">'
    if marker not in text:
        raise ValueError('thiếu <div class="wrap">')
    clean = NAV_RE.sub("", text)
    nav = render_navigation()
    return clean.replace(marker, marker + "\\n" + nav, 1)


def run(check: bool = False) -> int:
    paths = [POST_TEMPLATE, *[Path(p) for p in sorted(glob.glob(POSTS_GLOB))]]
    drift: list[str] = []
    changed = 0
    for path in paths:
        current = path.read_text(encoding="utf-8")
        try:
            expected = transform(current)
        except ValueError as exc:
            print(f"LỖI: {path.relative_to(ROOT)}: {exc}")
            return 1
        if current == expected:
            continue
        if check:
            drift.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(expected, encoding="utf-8")
            changed += 1
    if drift:
        print("LỖI: global navigation chưa đồng bộ: " + ", ".join(drift))
        print("Chạy `python3 tools/build.py` rồi commit lại.")
        return 1
    print(
        "OK: global navigation đã đồng bộ."
        if check
        else f"Đã backfill global navigation cho {changed} artifact."
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
'''

TEST_NAV = '''from __future__ import annotations

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
    source = '<body class="post">\\n<div class="wrap">\\n<header class="post"></header>\\n</div>'
    first = backfill_navigation.transform(source)
    second = backfill_navigation.transform(first)
    assert first == second
    assert 'href="../index.html"' in first
    assert 'href="../learning-paths.html"' in first
    assert 'href="../learning-dashboard.html"' in first
    assert 'href="../archive.html"' in first
    assert 'aria-current="page"' not in first
'''

STYLE_BLOCK = '''

/* Global navigation: one compact information-architecture contract site-wide. */
.global-nav{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-top:28px;padding:0 0 11px;border-bottom:1px solid var(--line);font-family:"JetBrains Mono",monospace;font-size:11px;line-height:1.45;letter-spacing:.04em}
.global-nav a{color:var(--muted);text-decoration:none}
.global-nav a:hover{color:var(--accent-deep);text-decoration:underline}
.global-nav .global-nav-brand{color:var(--accent-deep);font-weight:700;letter-spacing:.14em;text-transform:uppercase}
.global-nav-links{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.global-nav a[aria-current="page"]{color:var(--ink);font-weight:700;text-decoration-thickness:2px;text-underline-offset:4px}
body.home .global-nav + header.site,body.learning .global-nav + header.site,body.learning-dashboard .global-nav + header.site{margin-top:20px}
body.post .global-nav + .masthead{margin-top:20px}
@media (max-width:520px){.global-nav{align-items:flex-start;gap:8px;margin-top:20px}.global-nav-links{width:100%;gap:8px 14px}.global-nav-links a{white-space:nowrap}}
'''


def patch_templates() -> None:
    write("templates/_global-nav.template.html", NAV_PARTIAL)

    replace_once(
        "templates/index.template.html",
        '  <div class="wrap">\n    <header class="site">',
        '  <div class="wrap">\n{% set nav_prefix = "" %}\n{% set nav_current = "home" %}\n{% include "_global-nav.template.html" %}\n    <header class="site">',
    )
    replace_once(
        "templates/index.template.html",
        '      <div class="count">{{ count }} BÀI · <a href="archive.html">SEARCH &amp; ARCHIVE</a></div>',
        '      <div class="count">{{ count }} BÀI</div>',
    )

    replace_once(
        "templates/archive.template.html",
        '<div class="wrap">\n<header class="site">',
        '<div class="wrap">\n{% set nav_prefix = "" %}\n{% set nav_current = "archive" %}\n{% include "_global-nav.template.html" %}\n<header class="site">',
    )
    replace_once(
        "templates/archive.template.html",
        '  <div class="site-brand"><a class="brand-home" href="index.html">← Linux Daily</a></div>',
        '  <div class="site-brand">Linux Daily</div>',
    )

    replace_once(
        "templates/learning-paths.template.html",
        '  <div class="wrap">\n    <header class="site">',
        '  <div class="wrap">\n{% set nav_prefix = "" %}\n{% set nav_current = "paths" %}\n{% include "_global-nav.template.html" %}\n    <header class="site">',
    )
    replace_once(
        "templates/learning-paths.template.html",
        '      <div class="learning-nav"><a href="index.html">← TẤT CẢ BÀI</a> · <a href="archive.html">SEARCH &amp; ARCHIVE</a></div>\n',
        '',
    )


def patch_dashboard() -> None:
    path = "tools/learning_dashboard.py"
    replace_once(
        path,
        'from urllib.parse import urljoin\n\nsys.path.insert',
        'from urllib.parse import urljoin\n\nfrom jinja2 import Environment, FileSystemLoader, select_autoescape\n\nsys.path.insert',
    )
    replace_once(
        path,
        'SITE_CONFIG = ROOT / "site.json"\n',
        'SITE_CONFIG = ROOT / "site.json"\nTEMPLATES_DIR = ROOT / "templates"\nNAV_TEMPLATE = "_global-nav.template.html"\n',
    )
    marker = '\n\ndef collect(\n'
    text = read(path)
    if marker not in text:
        raise RuntimeError(f"{path}: thiếu marker collect")
    nav_fn = '''\n\ndef _navigation() -> str:\n    env = Environment(\n        loader=FileSystemLoader(TEMPLATES_DIR),\n        autoescape=select_autoescape(("html", "xml")),\n        trim_blocks=True,\n        lstrip_blocks=True,\n        keep_trailing_newline=True,\n    )\n    return env.get_template(NAV_TEMPLATE).render(\n        nav_prefix="", nav_current="dashboard"\n    ).strip()\n'''
    write(path, text.replace(marker, nav_fn + marker, 1))
    replace_once(
        path,
        '    counts = result["difficulty_counts"]\n    missing_labels = [',
        '    counts = result["difficulty_counts"]\n    nav_lines = ["    " + line for line in _navigation().splitlines()]\n    missing_labels = [',
    )
    replace_once(
        path,
        "        '  <div class=\"wrap\">',\n        '    <header class=\"site\">',",
        "        '  <div class=\"wrap\">',\n        *nav_lines,\n        '    <header class=\"site\">',",
    )
    replace_once(
        path,
        '        \'      <nav class="dashboard-nav" aria-label="Learning navigation"><a href="index.html">TẤT CẢ BÀI</a> · <a href="learning-paths.html">LEARNING PATHS</a> · <a href="archive.html">SEARCH &amp; ARCHIVE</a></nav>\',\n',
        '',
    )


def patch_build() -> None:
    path = "tools/build.py"
    replace_once(
        path,
        'import backfill_accessibility  # noqa: E402\n',
        'import backfill_accessibility  # noqa: E402\nimport backfill_navigation  # noqa: E402\n',
    )
    replace_once(
        path,
        'import learning_paths  # noqa: E402\n',
        'import learning_dashboard  # noqa: E402\nimport learning_paths  # noqa: E402\n',
    )
    replace_once(
        path,
        '        if learning_paths.run(check=True) != 0:\n            return 1\n        if backfill_site_metadata.run(check=True) != 0:',
        '        if learning_paths.run(check=True) != 0:\n            return 1\n        if learning_dashboard.run(check=True) != 0:\n            return 1\n        if backfill_site_metadata.run(check=True) != 0:',
    )
    replace_once(
        path,
        '        if backfill_fonts.run(check=True) != 0:\n            return 1\n        if related_content.run(check=True) != 0:',
        '        if backfill_fonts.run(check=True) != 0:\n            return 1\n        if backfill_navigation.run(check=True) != 0:\n            return 1\n        if related_content.run(check=True) != 0:',
    )
    replace_once(
        path,
        '        if learning_paths.run(check=False) != 0:\n            return 1\n        if backfill_site_metadata.run(check=False) != 0:',
        '        if learning_paths.run(check=False) != 0:\n            return 1\n        if learning_dashboard.run(check=False) != 0:\n            return 1\n        if backfill_site_metadata.run(check=False) != 0:',
    )
    replace_once(
        path,
        '        if backfill_fonts.run(check=False) != 0:\n            return 1\n        if related_content.run(check=False) != 0:',
        '        if backfill_fonts.run(check=False) != 0:\n            return 1\n        if backfill_navigation.run(check=False) != 0:\n            return 1\n        if related_content.run(check=False) != 0:',
    )


def patch_validate_site() -> None:
    path = "tools/validate_site.py"
    replace_once(
        path,
        '        self._in_title = False\n',
        '        self._in_title = False\n        self.global_nav_count = 0\n        self.global_nav_labels: list[str] = []\n        self.global_nav_links: list[dict[str, str]] = []\n        self._in_global_nav = False\n',
    )
    old_start = '''    def handle_starttag(self, tag, attrs):\n        data = dict(attrs)\n        if tag == "link":\n            self.links.append(data)\n        elif tag == "meta":\n            self.meta.append(data)\n        elif tag == "title":\n            self._in_title = True\n\n    def handle_endtag(self, tag):\n        if tag == "title":\n            self._in_title = False\n'''
    new_start = '''    def handle_starttag(self, tag, attrs):\n        data = dict(attrs)\n        if tag == "nav" and "global-nav" in data.get("class", "").split():\n            self.global_nav_count += 1\n            self.global_nav_labels.append(data.get("aria-label", ""))\n            self._in_global_nav = True\n        elif tag == "a" and self._in_global_nav:\n            self.global_nav_links.append(data)\n        elif tag == "link":\n            self.links.append(data)\n        elif tag == "meta":\n            self.meta.append(data)\n        elif tag == "title":\n            self._in_title = True\n\n    def handle_endtag(self, tag):\n        if tag == "nav" and self._in_global_nav:\n            self._in_global_nav = False\n        elif tag == "title":\n            self._in_title = False\n'''
    replace_once(path, old_start, new_start)

    marker = '\n\ndef _sitemap_urls(report: Report) -> set[str]:\n'
    text = read(path)
    if marker not in text:
        raise RuntimeError(f"{path}: thiếu marker sitemap")
    nav_check = '''\n\ndef _check_global_navigation(\n    path: str, prefix: str, current: str | None, report: Report\n) -> None:\n    parser = _parse_page(path)\n    page = os.path.relpath(path, ROOT)\n    if parser.global_nav_count != 1:\n        report.errors.append(\n            f"{page}: cần đúng 1 global navigation, hiện có {parser.global_nav_count}"\n        )\n        return\n    if parser.global_nav_labels != ["Điều hướng chính"]:\n        report.errors.append(f"{page}: global navigation thiếu aria-label chuẩn")\n\n    expected = [\n        prefix + "index.html",\n        prefix + "learning-paths.html",\n        prefix + "learning-dashboard.html",\n        prefix + "archive.html",\n    ]\n    actual = [link.get("href", "") for link in parser.global_nav_links]\n    if actual != expected:\n        report.errors.append(\n            f"{page}: global navigation phải có đúng 4 destination theo thứ tự; "\n            f"đang là {actual}"\n        )\n\n    invalid_current = [\n        link.get("href", "")\n        for link in parser.global_nav_links\n        if link.get("aria-current") not in (None, "", "page")\n    ]\n    if invalid_current:\n        report.errors.append(f"{page}: aria-current không hợp lệ: {invalid_current}")\n\n    current_links = [\n        link.get("href", "")\n        for link in parser.global_nav_links\n        if link.get("aria-current") == "page"\n    ]\n    expected_current = [] if current is None else [prefix + current]\n    if current_links != expected_current:\n        report.errors.append(\n            f"{page}: aria-current phải là {expected_current}, đang là {current_links}"\n        )\n'''
    write(path, text.replace(marker, nav_check + marker, 1))

    replace_once(
        path,
        '    expected_pages = set(canonicals)\n',
        '    _check_global_navigation(INDEX_PATH, "", "index.html", report)\n    _check_global_navigation(ARCHIVE_PATH, "", "archive.html", report)\n    _check_global_navigation(LEARNING_PATHS_PATH, "", "learning-paths.html", report)\n    _check_global_navigation(LEARNING_DASHBOARD_PATH, "", "learning-dashboard.html", report)\n    for path in posts:\n        _check_global_navigation(path, "../", None, report)\n\n    expected_pages = set(canonicals)\n',
    )
    old_dashboard = '''    with open(LEARNING_DASHBOARD_PATH, encoding="utf-8") as f:\n        dashboard_text = f.read()\n    for href in ("index.html", "learning-paths.html", "archive.html"):\n        if href not in dashboard_text:\n            report.errors.append(f"learning-dashboard.html thiếu navigation tới {href}")\n\n'''
    replace_once(path, old_dashboard, '')


def patch_accessibility() -> None:
    path = "tools/validate_accessibility.py"
    replace_once(
        path,
        'INDEX_PATH = os.path.join(ROOT, "index.html")\n',
        'INDEX_PATH = os.path.join(ROOT, "index.html")\nARCHIVE_PATH = os.path.join(ROOT, "archive.html")\n',
    )
    replace_once(
        path,
        '        INDEX_PATH,\n        LEARNING_DASHBOARD_PATH,',
        '        INDEX_PATH,\n        ARCHIVE_PATH,\n        LEARNING_DASHBOARD_PATH,',
    )


def patch_css() -> None:
    css = read("assets/style.css")
    if ".global-nav{" not in css:
        write("assets/style.css", css.rstrip() + STYLE_BLOCK)


def create_durable_files() -> None:
    write("tools/backfill_navigation.py", BACKFILL)
    write("tests/test_navigation.py", TEST_NAV)


def main() -> int:
    patch_templates()
    patch_dashboard()
    patch_build()
    patch_validate_site()
    patch_accessibility()
    patch_css()
    create_durable_files()

    subprocess.run([sys.executable, "tools/build.py"], cwd=ROOT, check=True)
    subprocess.run(
        ["ruff", "check", "tools/backfill_navigation.py", "tools/build.py", "tools/learning_dashboard.py", "tools/validate_site.py", "tools/validate_accessibility.py", "tests/test_navigation.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        ["pytest", "-q", "tests/test_navigation.py", "tests/test_validate_site.py", "tests/test_build_index.py", "tests/test_build_archive.py", "tests/test_learning_paths.py", "tests/test_learning_dashboard.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run([sys.executable, "tools/publish.py", "check"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

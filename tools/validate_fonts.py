#!/usr/bin/env python3
"""Self-hosted web-font quality gate for Linux Daily."""
from __future__ import annotations

import glob
import os
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_CSS = os.path.join(ROOT, "assets", "fonts.css")
INDEX_PATH = os.path.join(ROOT, "index.html")
LEARNING_DASHBOARD_PATH = os.path.join(ROOT, "learning-dashboard.html")
LEARNING_PATHS_PATH = os.path.join(ROOT, "learning-paths.html")
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")
TEMPLATES = [
    os.path.join(ROOT, "templates", "index.template.html"),
    os.path.join(ROOT, "templates", "post.template.html"),
    os.path.join(ROOT, "templates", "learning-paths.template.html"),
]
EXTERNAL_FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")
FONT_FILES = (
    "be-vietnam-pro-400.woff2",
    "be-vietnam-pro-500.woff2",
    "be-vietnam-pro-600.woff2",
    "be-vietnam-pro-700.woff2",
    "be-vietnam-pro-800.woff2",
    "jetbrains-mono.woff2",
    "noto-serif.woff2",
    "noto-serif-italic.woff2",
)
LICENSE_FILES = (
    "Be-Vietnam-Pro-OFL.txt",
    "JetBrains-Mono-OFL.txt",
    "Noto-Serif-OFL.txt",
)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str | None]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "link":
            self.links.append(dict(attrs))


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _check_external_hosts(path: str, report: Report) -> None:
    text = _read(path)
    rel = os.path.relpath(path, ROOT)
    for host in EXTERNAL_FONT_HOSTS:
        if host in text:
            report.errors.append(f"{rel}: còn runtime dependency {host}")


def _check_page(path: str, report: Report) -> None:
    rel = os.path.relpath(path, ROOT)
    parser = LinkParser()
    parser.feed(_read(path))
    is_post = rel.startswith("posts/")
    expected_css = "../assets/fonts.css" if is_post else "assets/fonts.css"
    expected_font = (
        "../assets/fonts/be-vietnam-pro-800.woff2"
        if is_post
        else "assets/fonts/be-vietnam-pro-800.woff2"
    )

    font_css = [x for x in parser.links if x.get("rel") == "stylesheet" and x.get("href") == expected_css]
    if len(font_css) != 1:
        report.errors.append(f"{rel}: cần đúng 1 local fonts.css link")

    preloads = [
        x
        for x in parser.links
        if x.get("rel") == "preload" and x.get("as") == "font"
    ]
    if len(preloads) != 1:
        report.errors.append(f"{rel}: cần đúng 1 font preload, hiện có {len(preloads)}")
    else:
        preload = preloads[0]
        if preload.get("href") != expected_font:
            report.errors.append(f"{rel}: font preload không đúng critical local font")
        if preload.get("type") != "font/woff2":
            report.errors.append(f"{rel}: font preload phải dùng type=font/woff2")
        if "crossorigin" not in preload:
            report.errors.append(f"{rel}: font preload phải có crossorigin")


def run() -> Report:
    report = Report()
    pages = [
        INDEX_PATH,
        LEARNING_DASHBOARD_PATH,
        LEARNING_PATHS_PATH,
        *sorted(glob.glob(POSTS_GLOB)),
    ]

    for path in [*pages, *TEMPLATES, FONT_CSS]:
        _check_external_hosts(path, report)
    for path in pages:
        _check_page(path, report)

    try:
        css = _read(FONT_CSS)
    except OSError as exc:
        report.errors.append(f"assets/fonts.css không đọc được: {exc}")
        return report

    if css.count("@font-face") != 8:
        report.errors.append("assets/fonts.css phải khai báo đúng 8 @font-face")
    if css.count("font-display: swap") != 8:
        report.errors.append("mọi @font-face phải dùng font-display: swap")

    font_dir = os.path.join(ROOT, "assets", "fonts")
    for name in FONT_FILES:
        path = os.path.join(font_dir, name)
        if not os.path.isfile(path) or os.path.getsize(path) <= 0:
            report.errors.append(f"thiếu hoặc rỗng font asset: assets/fonts/{name}")
        if f'fonts/{name}' not in css:
            report.errors.append(f"assets/fonts.css chưa tham chiếu {name}")

    license_dir = os.path.join(font_dir, "licenses")
    for name in LICENSE_FILES:
        path = os.path.join(license_dir, name)
        if not os.path.isfile(path):
            report.errors.append(f"thiếu font license: assets/fonts/licenses/{name}")
            continue
        text = _read(path)
        if "SIL OPEN FONT LICENSE Version 1.1" not in text:
            report.errors.append(f"font license không hợp lệ: assets/fonts/licenses/{name}")
    return report


def main() -> int:
    report = run()
    if report.errors:
        print(f"✗ Self-host font gate: {len(report.errors)} lỗi", file=sys.stderr)
        for error in report.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("✓ Self-host font gate: local WOFF2, OFL, preload và runtime dependency đều hợp lệ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

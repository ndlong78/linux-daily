#!/usr/bin/env python3
"""Accessibility baseline validator for Linux Daily public HTML."""
from __future__ import annotations

import glob
import os
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT, "index.html")
LEARNING_PATHS_PATH = os.path.join(ROOT, "learning-paths.html")
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")
STYLE_PATH = os.path.join(ROOT, "assets", "style.css")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)


class A11yParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang: str | None = None
        self.skip_links: list[dict[str, str]] = []
        self.main_landmarks: list[dict[str, str]] = []
        self.svgs: list[dict[str, str]] = []
        self.h1_count = 0
        self.headings: list[int] = []
        self.positive_tabindex: list[str] = []
        self._order = 0
        self.skip_order: int | None = None
        self.main_order: int | None = None

    def handle_starttag(self, tag, attrs):
        self._order += 1
        data = dict(attrs)
        if tag == "html":
            self.html_lang = data.get("lang")
        elif tag == "a" and "skip-link" in data.get("class", "").split():
            self.skip_links.append(data)
            if self.skip_order is None:
                self.skip_order = self._order
        elif tag == "main":
            self.main_landmarks.append(data)
            if self.main_order is None:
                self.main_order = self._order
        elif tag == "svg":
            self.svgs.append(data)
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.headings.append(level)
            if tag == "h1":
                self.h1_count += 1

        tabindex = data.get("tabindex")
        if tabindex:
            try:
                if int(tabindex) > 0:
                    self.positive_tabindex.append(f"<{tag} tabindex={tabindex}>")
            except ValueError:
                pass


def _validate_page(path: str, report: Report) -> None:
    rel = os.path.relpath(path, ROOT)
    parser = A11yParser()
    with open(path, encoding="utf-8") as f:
        parser.feed(f.read())

    if parser.html_lang != "vi":
        report.errors.append(f"{rel}: html lang phải là vi")
    if len(parser.skip_links) != 1:
        report.errors.append(f"{rel}: cần đúng 1 skip link, hiện có {len(parser.skip_links)}")
    elif parser.skip_links[0].get("href") != "#main-content":
        report.errors.append(f"{rel}: skip link phải trỏ #main-content")
    if len(parser.main_landmarks) != 1:
        report.errors.append(f"{rel}: cần đúng 1 <main>, hiện có {len(parser.main_landmarks)}")
    elif parser.main_landmarks[0].get("id") != "main-content":
        report.errors.append(f"{rel}: main phải có id=main-content")
    if parser.skip_order and parser.main_order and parser.skip_order > parser.main_order:
        report.errors.append(f"{rel}: skip link phải đứng trước main")
    if parser.h1_count != 1:
        report.errors.append(f"{rel}: cần đúng 1 h1, hiện có {parser.h1_count}")
    for prev, current in zip(parser.headings, parser.headings[1:], strict=False):
        if current > prev + 1:
            report.errors.append(f"{rel}: heading nhảy cấp h{prev} → h{current}")
            break
    for attrs in parser.svgs:
        if attrs.get("role") != "img" or not attrs.get("aria-label", "").strip():
            report.errors.append(f"{rel}: mọi SVG phải có role=img và aria-label không rỗng")
            break
    for item in parser.positive_tabindex:
        report.errors.append(f"{rel}: cấm positive tabindex: {item}")


def run() -> Report:
    report = Report()
    for path in [INDEX_PATH, LEARNING_PATHS_PATH, *sorted(glob.glob(POSTS_GLOB))]:
        _validate_page(path, report)

    try:
        with open(STYLE_PATH, encoding="utf-8") as f:
            css = f.read()
    except OSError as exc:
        report.errors.append(f"assets/style.css không đọc được: {exc}")
        return report

    if ":focus-visible" not in css:
        report.errors.append("assets/style.css: thiếu keyboard focus-visible style")
    if ".skip-link" not in css or ".skip-link:focus" not in css:
        report.errors.append("assets/style.css: thiếu visible-on-focus style cho skip link")
    return report


def main() -> int:
    report = run()
    if report.errors:
        print(f"✗ Accessibility gate: {len(report.errors)} lỗi", file=sys.stderr)
        for error in report.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("✓ Accessibility gate: landmarks, skip link, headings, SVG labels và keyboard focus đều hợp lệ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

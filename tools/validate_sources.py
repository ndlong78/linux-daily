#!/usr/bin/env python3
"""Source-backed technical quality gate cho Linux Daily.

Từ bài #019, mỗi bài bắt buộc khai nguồn kỹ thuật có cấu trúc trong ``ld-meta``
và hiển thị cùng danh sách nguồn trong ``<section class="sources">``.

Bài lịch sử #001–#018 vẫn được grandfather nếu chưa backfill. Tuy nhiên, ngay khi
một bài lịch sử khai ``review_status`` hoặc ``sources``, bài đó được xem là đã
opt-in vào source-backed review và phải vượt toàn bộ gate giống bài mới. Cách này
cho phép backfill dần mà không để bài đã sửa bị regression âm thầm.
"""
from __future__ import annotations

import glob
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postmeta  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
SOURCE_REQUIRED_FROM_ISSUE = 19
MIN_PRIMARY_SOURCES = 2
PRIMARY_KINDS = {"official", "upstream"}
ALLOWED_REVIEW_STATUSES = {"draft", "reviewed", "published"}
MERGEABLE_REVIEW_STATUSES = {"reviewed", "published"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def fail(self, message: str) -> None:
        self.errors.append(message)


class _SourceSectionParser(HTMLParser):
    """Lấy các link trong ``section.sources`` theo đúng thứ tự hiển thị."""

    def __init__(self) -> None:
        super().__init__()
        self.in_sources = False
        self.section_depth = 0
        self.found_section = False
        self.active_href: str | None = None
        self.active_text: list[str] = []
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        classes = attrs_d.get("class", "").split()
        if tag == "section" and not self.in_sources and "sources" in classes:
            self.in_sources = True
            self.found_section = True
            self.section_depth = 1
            return
        if not self.in_sources:
            return
        if tag == "section":
            self.section_depth += 1
        if tag == "a":
            self.active_href = attrs_d.get("href", "")
            self.active_text = []

    def handle_endtag(self, tag):
        if not self.in_sources:
            return
        if tag == "a" and self.active_href is not None:
            self.links.append({
                "title": "".join(self.active_text).strip(),
                "url": self.active_href.strip(),
            })
            self.active_href = None
            self.active_text = []
        if tag == "section":
            self.section_depth -= 1
            if self.section_depth == 0:
                self.in_sources = False

    def handle_data(self, data):
        if self.in_sources and self.active_href is not None:
            self.active_text.append(data)


def read_visible_sources(path: str) -> tuple[bool, list[dict[str, str]]]:
    parser = _SourceSectionParser()
    with open(path, encoding="utf-8") as f:
        parser.feed(f.read())
    return parser.found_section, parser.links


def _issue_from_filename(path: str) -> int | None:
    m = re.match(r"post-(\d+)-[a-z0-9-]+\.html$", os.path.basename(path))
    return int(m.group(1)) if m else None


def _valid_https_url(url: object) -> bool:
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _historical_opted_in(meta: dict) -> bool:
    """Bài cũ có một dấu hiệu source-review thì phải hoàn tất toàn bộ contract."""
    return "review_status" in meta or "sources" in meta


def validate_post_sources(path: str, report: Report) -> None:
    name = os.path.basename(path)
    issue = _issue_from_filename(path)
    if issue is None:
        return

    # Bài #019+ luôn bắt buộc source metadata. Bài cũ chỉ được kiểm khi đã opt-in.
    try:
        meta = postmeta.read_meta(path)
    except postmeta.MetaError as exc:
        if issue >= SOURCE_REQUIRED_FROM_ISSUE:
            report.fail(f"{name}: không thể kiểm tra nguồn vì metadata lỗi ({exc}).")
        return

    if issue < SOURCE_REQUIRED_FROM_ISSUE and not _historical_opted_in(meta):
        return

    status = meta.get("review_status")
    report.check(
        status in ALLOWED_REVIEW_STATUSES,
        f"{name}: meta.review_status phải là draft/reviewed/published, đang là {status!r}.",
    )
    if status in ALLOWED_REVIEW_STATUSES:
        report.check(
            status in MERGEABLE_REVIEW_STATUSES,
            f"{name}: review_status={status!r}; bài có nguồn phải được technical review trước khi merge (reviewed/published).",
        )

    sources = meta.get("sources")
    if not isinstance(sources, list):
        report.fail(f"{name}: meta.sources phải là một JSON array.")
        return

    report.check(
        len(sources) >= MIN_PRIMARY_SOURCES,
        f"{name}: cần ít nhất {MIN_PRIMARY_SOURCES} nguồn kỹ thuật, đang có {len(sources)}.",
    )

    pairs: list[dict[str, str]] = []
    primary_count = 0
    seen_urls: set[str] = set()
    for idx, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            report.fail(f"{name}: sources[{idx}] phải là object JSON.")
            continue
        title = source.get("title")
        url = source.get("url")
        kind = source.get("kind")
        report.check(
            isinstance(title, str) and bool(title.strip()),
            f"{name}: sources[{idx}].title bị thiếu/rỗng.",
        )
        report.check(
            _valid_https_url(url),
            f"{name}: sources[{idx}].url phải là URL HTTPS đầy đủ, đang là {url!r}.",
        )
        report.check(
            kind in PRIMARY_KINDS,
            f"{name}: sources[{idx}].kind phải là official hoặc upstream, đang là {kind!r}.",
        )
        if kind in PRIMARY_KINDS:
            primary_count += 1
        if isinstance(url, str) and url:
            report.check(url not in seen_urls, f"{name}: URL nguồn bị lặp: {url}")
            seen_urls.add(url)
        if isinstance(title, str) and isinstance(url, str):
            pairs.append({"title": title.strip(), "url": url.strip()})

    report.check(
        primary_count >= MIN_PRIMARY_SOURCES,
        f"{name}: cần ít nhất {MIN_PRIMARY_SOURCES} nguồn official/upstream, đang có {primary_count}.",
    )

    found_section, visible = read_visible_sources(path)
    report.check(found_section, f"{name}: thiếu <section class=\"sources\"> Nguồn kỹ thuật.")
    if found_section:
        report.check(
            visible == pairs,
            f"{name}: nguồn hiển thị không khớp meta.sources (title/URL/thứ tự phải giống nhau).",
        )


def run(posts_dir: str | None = None) -> Report:
    report = Report()
    root = posts_dir or POSTS_DIR
    for path in sorted(glob.glob(os.path.join(root, "post-*.html"))):
        validate_post_sources(path, report)
    return report


def main() -> int:
    report = run()
    if report.errors:
        print(f"✗ Source-backed gate: {len(report.errors)} lỗi", file=sys.stderr)
        for error in report.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(
        f"✓ Source-backed gate: bài #{SOURCE_REQUIRED_FROM_ISSUE:03d}+ và historical opt-in có nguồn hợp lệ."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

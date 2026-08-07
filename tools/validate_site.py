#!/usr/bin/env python3
"""Cross-artifact website/SEO quality gate for Linux Daily."""
from __future__ import annotations

import glob
import json
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_CONFIG = os.path.join(ROOT, "site.json")
INDEX_PATH = os.path.join(ROOT, "index.html")
FEED_PATH = os.path.join(ROOT, "feed.xml")
SITEMAP_PATH = os.path.join(ROOT, "sitemap.xml")
ROBOTS_PATH = os.path.join(ROOT, "robots.txt")
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")
STALE_PUBLIC_HOSTS = {"ndlong78.github.io"}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self.meta: list[dict[str, str]] = []
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "link":
            self.links.append(data)
        elif tag == "meta":
            self.meta.append(data)
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)


def _site() -> dict:
    with open(SITE_CONFIG, encoding="utf-8") as f:
        site = json.load(f)
    site["url"] = site["url"].rstrip("/") + "/"
    return site


def _parse_page(path: str) -> PageParser:
    parser = PageParser()
    with open(path, encoding="utf-8") as f:
        parser.feed(f.read())
    return parser


def _one(items: list[str], label: str, page: str, report: Report) -> str | None:
    if len(items) != 1:
        report.errors.append(f"{page}: cần đúng 1 {label}, hiện có {len(items)}")
        return None
    return items[0]


def _page_urls(path: str, site: dict, report: Report) -> tuple[str | None, set[str]]:
    parser = _parse_page(path)
    page = os.path.relpath(path, ROOT)
    canonicals = [x.get("href", "") for x in parser.links if x.get("rel") == "canonical"]
    canonical = _one(canonicals, "canonical", page, report)
    props = {x.get("property"): x.get("content", "") for x in parser.meta if x.get("property")}
    names = {x.get("name"): x.get("content", "") for x in parser.meta if x.get("name")}
    descriptions = [x.get("content", "") for x in parser.meta if x.get("name") == "description"]
    description = _one(descriptions, "meta description", page, report)
    title = "".join(parser.title_parts).strip()

    if not title:
        report.errors.append(f"{page}: thiếu <title>")
    if not description:
        report.errors.append(f"{page}: meta description rỗng")

    if canonical:
        parsed = urlparse(canonical)
        if parsed.scheme != "https" or parsed.netloc != urlparse(site["url"]).netloc:
            report.errors.append(f"{page}: canonical ngoài public origin: {canonical}")
        if props.get("og:url") != canonical:
            report.errors.append(f"{page}: og:url không khớp canonical")

    for key in ("og:type", "og:title", "og:description", "og:url", "og:site_name", "og:image", "og:image:alt"):
        if not props.get(key):
            report.errors.append(f"{page}: thiếu {key}")
    for key in ("twitter:card", "twitter:title", "twitter:description", "twitter:image", "twitter:image:alt"):
        if not names.get(key):
            report.errors.append(f"{page}: thiếu {key}")
    if names.get("twitter:card") != "summary_large_image":
        report.errors.append(f"{page}: twitter:card phải là summary_large_image")
    if props.get("og:image") and names.get("twitter:image") != props.get("og:image"):
        report.errors.append(f"{page}: twitter:image không khớp og:image")
    if props.get("og:image:alt") and names.get("twitter:image:alt") != props.get("og:image:alt"):
        report.errors.append(f"{page}: twitter:image:alt không khớp og:image:alt")
    if props.get("og:description") and description != props.get("og:description"):
        report.errors.append(f"{page}: og:description không khớp meta description")
    if names.get("twitter:description") and description != names.get("twitter:description"):
        report.errors.append(f"{page}: twitter:description không khớp meta description")

    internal_hrefs: set[str] = set()
    origin = urlparse(site["url"]).netloc
    for link in parser.links:
        href = link.get("href", "")
        if href and urlparse(urljoin(canonical or site["url"], href)).netloc == origin:
            internal_hrefs.add(urljoin(canonical or site["url"], href))
    return canonical, internal_hrefs


def _sitemap_urls(report: Report) -> set[str]:
    try:
        root = ET.parse(SITEMAP_PATH).getroot()
    except (ET.ParseError, OSError) as exc:
        report.errors.append(f"sitemap.xml không parse được: {exc}")
        return set()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text or "" for node in root.findall("s:url/s:loc", ns)]
    if len(urls) != len(set(urls)):
        report.errors.append("sitemap.xml có URL trùng")
    return set(urls)


def _feed_urls(report: Report) -> set[str]:
    try:
        root = ET.parse(FEED_PATH).getroot()
    except (ET.ParseError, OSError) as exc:
        report.errors.append(f"feed.xml không parse được: {exc}")
        return set()
    urls = [(node.text or "").strip() for node in root.findall("./channel/item/link")]
    guids = [(node.text or "").strip() for node in root.findall("./channel/item/guid")]
    if urls != guids:
        report.errors.append("feed.xml: item link và guid không đồng bộ")
    if len(urls) != len(set(urls)):
        report.errors.append("feed.xml có item URL trùng")
    return set(urls)


def _check_stale_hosts(paths: list[str], report: Report) -> None:
    for path in paths:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for host in STALE_PUBLIC_HOSTS:
            if host in text:
                report.errors.append(f"{os.path.relpath(path, ROOT)}: còn public host cũ {host}")


def run() -> Report:
    report = Report()
    site = _site()
    posts = sorted(glob.glob(POSTS_GLOB))
    html_paths = [INDEX_PATH, *posts]
    canonicals: dict[str, str] = {}

    index_canonical, _ = _page_urls(INDEX_PATH, site, report)
    for path in posts:
        canonical, _ = _page_urls(path, site, report)
        if canonical:
            if canonical in canonicals:
                report.errors.append(
                    f"duplicate canonical: {canonical} ở {canonicals[canonical]} và {os.path.relpath(path, ROOT)}"
                )
            canonicals[canonical] = os.path.relpath(path, ROOT)

    if index_canonical:
        if index_canonical in canonicals:
            report.errors.append(f"duplicate canonical homepage: {index_canonical}")
        canonicals[index_canonical] = "index.html"

    expected_pages = set(canonicals)
    sitemap_urls = _sitemap_urls(report)
    if sitemap_urls != expected_pages:
        missing = sorted(expected_pages - sitemap_urls)
        extra = sorted(sitemap_urls - expected_pages)
        if missing:
            report.errors.append(f"sitemap thiếu canonical: {', '.join(missing)}")
        if extra:
            report.errors.append(f"sitemap có URL không phải page canonical: {', '.join(extra)}")

    feed_urls = _feed_urls(report)
    post_urls = {url for url, path in canonicals.items() if path.startswith("posts/")}
    if not feed_urls <= post_urls:
        report.errors.append("feed.xml chứa URL không phải canonical post")

    index_text = open(INDEX_PATH, encoding="utf-8").read()
    for path in posts:
        href = "posts/" + os.path.basename(path)
        if href not in index_text:
            report.errors.append(f"orphan post: {href} không được homepage liên kết")

    with open(ROBOTS_PATH, encoding="utf-8") as f:
        robots = f.read()
    expected_sitemap = urljoin(site["url"], site["sitemap_path"])
    if f"Sitemap: {expected_sitemap}" not in robots:
        report.errors.append("robots.txt không trỏ đúng sitemap public")

    _check_stale_hosts([SITE_CONFIG, INDEX_PATH, FEED_PATH, SITEMAP_PATH, ROBOTS_PATH, *posts], report)
    return report


def main() -> int:
    report = run()
    if report.errors:
        print(f"✗ Website/SEO gate: {len(report.errors)} lỗi", file=sys.stderr)
        for error in report.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("✓ Website/SEO gate: canonical, OG/social, feed, sitemap, robots và page inventory đều hợp lệ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

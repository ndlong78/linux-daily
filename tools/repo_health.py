#!/usr/bin/env python3
"""Print a deterministic health snapshot for the Linux Daily repository."""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST_GLOB = os.path.join(ROOT, "posts", "post-*.html")
SOCIAL_GLOB = os.path.join(ROOT, "posts", "social", "post-*-code.png")
FONT_GLOB = os.path.join(ROOT, "assets", "fonts", "*.woff2")
META_RE = re.compile(
    r'<script\s+type="application/json"\s+id="ld-meta">\s*(\{.*?\})\s*</script>',
    re.DOTALL,
)

REQUIRED = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "PROJECT_STATUS.md",
    "CHANGELOG.md",
    "index.html",
    "archive.html",
    "learning-dashboard.html",
    "learning-paths.html",
    "learning-paths.json",
    "learning-metadata.json",
    "search-index.json",
    "feed.xml",
    "sitemap.xml",
    "robots.txt",
    "docs/ROADMAP.md",
    "docs/architecture.md",
    "docs/release-checklist.md",
)


@dataclass
class Health:
    metrics: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def _post_sources(path: str, health: Health) -> int:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    match = META_RE.search(text)
    if not match:
        health.errors.append(f"{os.path.relpath(path, ROOT)}: thiếu ld-meta")
        return 0
    try:
        meta = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        health.errors.append(f"{os.path.relpath(path, ROOT)}: ld-meta JSON lỗi: {exc}")
        return 0
    sources = meta.get("sources", [])
    if not isinstance(sources, list):
        health.errors.append(f"{os.path.relpath(path, ROOT)}: sources không phải list")
        return 0
    return len(sources)


def collect() -> Health:
    health = Health()
    for rel in REQUIRED:
        if not os.path.isfile(os.path.join(ROOT, rel)):
            health.errors.append(f"thiếu required file: {rel}")

    posts = sorted(glob.glob(POST_GLOB))
    health.metrics["posts"] = len(posts)
    static_pages = sum(
        1
        for name in (
            "index.html",
            "archive.html",
            "learning-dashboard.html",
            "learning-paths.html",
        )
        if os.path.isfile(os.path.join(ROOT, name))
    )
    health.metrics["generated_pages"] = len(posts) + static_pages
    health.metrics["technical_sources"] = sum(_post_sources(path, health) for path in posts)
    health.metrics["social_code_images"] = len(glob.glob(SOCIAL_GLOB))
    health.metrics["woff2_fonts"] = len(glob.glob(FONT_GLOB))

    try:
        feed_root = ET.parse(os.path.join(ROOT, "feed.xml")).getroot()
        health.metrics["rss_items"] = len(feed_root.findall("./channel/item"))
    except (OSError, ET.ParseError) as exc:
        health.metrics["rss_items"] = 0
        health.errors.append(f"feed.xml không parse được: {exc}")

    try:
        sitemap_root = ET.parse(os.path.join(ROOT, "sitemap.xml")).getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        health.metrics["sitemap_urls"] = len(sitemap_root.findall("s:url", ns))
    except (OSError, ET.ParseError) as exc:
        health.metrics["sitemap_urls"] = 0
        health.errors.append(f"sitemap.xml không parse được: {exc}")

    if health.metrics["social_code_images"] < health.metrics["posts"]:
        health.errors.append("social code images ít hơn số bài")
    if health.metrics["sitemap_urls"] != health.metrics["generated_pages"]:
        health.errors.append("sitemap URL count không khớp generated page inventory")
    if health.metrics["rss_items"] > health.metrics["posts"]:
        health.errors.append("RSS item count lớn hơn post inventory")
    if health.metrics["woff2_fonts"] < 1:
        health.errors.append("không tìm thấy self-hosted WOFF2 fonts")
    return health


def main() -> int:
    health = collect()
    print("Linux Daily — Repository Health")
    print("=" * 31)
    for key in (
        "posts",
        "generated_pages",
        "technical_sources",
        "social_code_images",
        "woff2_fonts",
        "rss_items",
        "sitemap_urls",
    ):
        print(f"{key:20} {health.metrics.get(key, 0)}")
    if health.errors:
        print(f"\nFAIL: {len(health.errors)} vấn đề", file=sys.stderr)
        for error in health.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("\nOK: repository health baseline đạt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

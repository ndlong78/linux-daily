#!/usr/bin/env python3
"""Build/check the deterministic RSS 2.0 feed from ld-meta post metadata."""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import postmeta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
SITE_CONFIG = os.path.join(ROOT, "site.json")
FEED_PATH = os.path.join(ROOT, "feed.xml")
MAX_ITEMS = 10
VN_TZ = timezone(timedelta(hours=7))


def _xml(value: object) -> str:
    return html.escape(str(value), quote=False)


def _load_site(path: str = SITE_CONFIG) -> dict:
    with open(path, encoding="utf-8") as f:
        site = json.load(f)
    required = ("title", "description", "language", "url", "feed_path")
    missing = [key for key in required if not site.get(key)]
    if missing:
        raise ValueError(f"site.json thiếu trường bắt buộc: {', '.join(missing)}")
    site["url"] = site["url"].rstrip("/") + "/"
    return site


def _pub_date(iso_date: str) -> str:
    dt = datetime.strptime(iso_date, "%Y-%m-%d").replace(tzinfo=VN_TZ)
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def collect_items(posts_dir: str = POSTS_DIR, limit: int = MAX_ITEMS) -> list[dict]:
    items = []
    for path in glob.glob(os.path.join(posts_dir, "post-*.html")):
        meta = postmeta.read_meta(path)
        items.append({
            "issue": int(meta["issue"]),
            "date": meta["date"],
            "title": meta["title"],
            "lede": meta["lede"],
            "href": "posts/" + os.path.basename(path),
        })
    items.sort(key=lambda item: item["issue"], reverse=True)
    return items[:limit]


def render_feed(posts_dir: str = POSTS_DIR, site_config: str = SITE_CONFIG) -> tuple[str, int]:
    site = _load_site(site_config)
    items = collect_items(posts_dir)
    feed_url = urljoin(site["url"], site["feed_path"])
    last_build = _pub_date(items[0]["date"]) if items else _pub_date("2026-01-01")

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{_xml(site['title'])}</title>",
        f"    <link>{_xml(site['url'])}</link>",
        f"    <description>{_xml(site['description'])}</description>",
        f"    <language>{_xml(site['language'])}</language>",
        f"    <lastBuildDate>{last_build}</lastBuildDate>",
        f'    <atom:link href="{_xml(feed_url)}" rel="self" type="application/rss+xml" />',
    ]

    for item in items:
        url = urljoin(site["url"], item["href"])
        lines.extend([
            "    <item>",
            f"      <title>{_xml(item['title'])}</title>",
            f"      <link>{_xml(url)}</link>",
            f'      <guid isPermaLink="true">{_xml(url)}</guid>',
            f"      <pubDate>{_pub_date(item['date'])}</pubDate>",
            f"      <description>{_xml(item['lede'])}</description>",
            "    </item>",
        ])

    lines.extend(["  </channel>", "</rss>", ""])
    return "\n".join(lines), len(items)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Dựng hoặc kiểm tra feed.xml.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rendered, count = render_feed()

    if args.check:
        current = ""
        if os.path.exists(FEED_PATH):
            with open(FEED_PATH, encoding="utf-8") as f:
                current = f.read()
        if current != rendered:
            print("LỖI: feed.xml chưa đồng bộ. Chạy `python3 tools/build.py` rồi commit lại.")
            return 1
        print(f"OK: feed.xml đã đồng bộ ({count} bài mới nhất).")
        return 0

    with open(FEED_PATH, "w", encoding="utf-8") as f:
        f.write(rendered)
    print(f"Đã dựng feed.xml với {count} bài mới nhất.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

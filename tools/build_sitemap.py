#!/usr/bin/env python3
"""Build/check sitemap.xml and robots.txt from post metadata + site.json."""
from __future__ import annotations

import argparse
import glob
import json
import os
from urllib.parse import urljoin
from xml.sax.saxutils import escape

import build_index
import postmeta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
SITE_CONFIG = os.path.join(ROOT, "site.json")
SITEMAP_PATH = os.path.join(ROOT, "sitemap.xml")
ROBOTS_PATH = os.path.join(ROOT, "robots.txt")


def _load_site(path: str = SITE_CONFIG) -> dict:
    with open(path, encoding="utf-8") as f:
        site = json.load(f)
    required = ("url", "sitemap_path")
    missing = [key for key in required if not site.get(key)]
    if missing:
        raise ValueError(f"site.json thiếu trường bắt buộc: {', '.join(missing)}")
    site["url"] = site["url"].rstrip("/") + "/"
    return site


def collect_urls(posts_dir: str = POSTS_DIR, site_config: str = SITE_CONFIG) -> list[dict]:
    site = _load_site(site_config)
    posts = []
    for path in glob.glob(os.path.join(posts_dir, "post-*.html")):
        meta = postmeta.read_meta(path)
        posts.append({
            "issue": int(meta["issue"]),
            "date": meta["date"],
            "loc": urljoin(site["url"], "posts/" + os.path.basename(path)),
        })
    posts.sort(key=lambda item: item["issue"], reverse=True)
    newest = posts[0]["date"] if posts else "2026-01-01"
    # Trang danh sách đã phân trang. Bài vốn đã có mục riêng trong sitemap, nhưng
    # khai cả chuỗi trang giúp crawler hiểu đây là một danh sách liên tục.
    #
    # Lấy tên trang từ chính build_index chứ KHÔNG glob trên đĩa: khi series ngắn
    # lại, build.py dựng sitemap trước rồi mới xoá trang thừa, nên bản glob sẽ
    # khai một trang vừa bị xoá và làm gate đỏ ở lần chạy sau.
    total_pages = len(build_index.paginate(build_index.collect_posts(posts_dir)))
    listing = [
        {"loc": urljoin(site["url"], build_index.page_name(page)), "date": newest}
        for page in range(2, total_pages + 1)
    ]
    return [
        {"loc": site["url"], "date": newest},
        *listing,
        {"loc": urljoin(site["url"], "archive.html"), "date": newest},
        {"loc": urljoin(site["url"], "learning-dashboard.html"), "date": newest},
        {"loc": urljoin(site["url"], "learning-paths.html"), "date": newest},
        *posts,
    ]


def render_sitemap(posts_dir: str = POSTS_DIR, site_config: str = SITE_CONFIG) -> tuple[str, int]:
    urls = collect_urls(posts_dir, site_config)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for item in urls:
        lines.extend([
            "  <url>",
            f"    <loc>{escape(item['loc'])}</loc>",
            f"    <lastmod>{item['date']}</lastmod>",
            "  </url>",
        ])
    lines.extend(["</urlset>", ""])
    return "\n".join(lines), len(urls)


def render_robots(site_config: str = SITE_CONFIG) -> str:
    site = _load_site(site_config)
    sitemap_url = urljoin(site["url"], site["sitemap_path"])
    return f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Dựng hoặc kiểm tra sitemap.xml + robots.txt.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    sitemap, count = render_sitemap()
    robots = render_robots()

    if args.check:
        ok = True
        for path, expected, label in (
            (SITEMAP_PATH, sitemap, "sitemap.xml"),
            (ROBOTS_PATH, robots, "robots.txt"),
        ):
            current = ""
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    current = f.read()
            if current != expected:
                print(f"LỖI: {label} chưa đồng bộ. Chạy `python3 tools/build.py` rồi commit lại.")
                ok = False
        if not ok:
            return 1
        print(f"OK: sitemap.xml + robots.txt đã đồng bộ ({count} URL).")
        return 0

    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(sitemap)
    with open(ROBOTS_PATH, "w", encoding="utf-8") as f:
        f.write(robots)
    print(f"Đã dựng sitemap.xml ({count} URL) và robots.txt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

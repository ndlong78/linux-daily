#!/usr/bin/env python3
"""Build/check archive.html and search-index.json from ld-meta + taxonomy."""
from __future__ import annotations

import argparse
import glob
import html
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import postmeta
import taxonomy

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
ARCHIVE_PATH = ROOT / "archive.html"
SEARCH_INDEX_PATH = ROOT / "search-index.json"
TEMPLATES_DIR = ROOT / "templates"
TEMPLATE = "archive.template.html"


def collect_posts() -> list[dict]:
    items: list[dict] = []
    axes = taxonomy.load_taxonomy()["axes"]
    for raw in glob.glob(POSTS_GLOB):
        path = Path(raw)
        meta = postmeta.read_meta(str(path))
        axis = str(meta["axis"]).strip()
        eyebrow = str(meta["eyebrow"]).strip()
        parts = [part.strip() for part in eyebrow.split("·") if part.strip()]
        items.append({
            "issue": int(meta["issue"]),
            "date": str(meta["date"]),
            "axis": axis,
            "axis_label": axes[axis]["label"],
            "axis_slug": axes[axis]["slug"],
            "tags": parts[1:],
            "title": str(meta["title"]).strip(),
            "lede": str(meta["lede"]).strip(),
            "href": "posts/" + path.name,
        })
    items.sort(key=lambda item: item["issue"], reverse=True)
    return items


def render_search_index(posts: list[dict] | None = None) -> str:
    posts = posts if posts is not None else collect_posts()
    payload = {
        "schema": 1,
        "count": len(posts),
        "posts": [
            {key: item[key] for key in ("issue", "date", "axis", "axis_label", "axis_slug", "tags", "title", "lede", "href")}
            for item in posts
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_archive(posts: list[dict] | None = None) -> str:
    posts = posts if posts is not None else collect_posts()
    axes = taxonomy.load_taxonomy()["axes"]
    groups = []
    for axis, cfg in axes.items():
        members = [item for item in posts if item["axis"] == axis]
        groups.append({"axis": axis, "label": cfg["label"], "slug": cfg["slug"], "posts": members})
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    return env.get_template(TEMPLATE).render(groups=groups, count=len(posts))


def run(*, check: bool) -> int:
    posts = collect_posts()
    expected = ((ARCHIVE_PATH, render_archive(posts), "archive.html"), (SEARCH_INDEX_PATH, render_search_index(posts), "search-index.json"))
    stale = []
    for path, content, label in expected:
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current == content:
            continue
        if check:
            stale.append(label)
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        print("LỖI: discovery artifacts chưa đồng bộ: " + ", ".join(stale))
        return 1
    print(("OK: " if check else "Đã dựng ") + f"archive/search cho {len(posts)} bài.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

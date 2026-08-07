#!/usr/bin/env python3
"""Backfill discovery metadata and repair small historical HTML drift.

The transformation is deterministic and idempotent: public URLs come from site.json,
post title/description come from ld-meta, legacy broken source URLs are replaced with
verified live official equivalents, and old HTML fragments missing the common document
shell are normalized back to the shared site structure.
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import sys
from urllib.parse import urljoin

import postmeta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_CONFIG = os.path.join(ROOT, "site.json")
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")

LEGACY_LINK_REPLACEMENTS = {
    "https://docs.fedoraproject.org/en-US/fedora/f30/system-administrators-guide/basic-system-configuration/Gaining_Privileges/":
        "https://docs.fedoraproject.org/ko/fedora/f30/system-administrators-guide/basic-system-configuration/Gaining_Privileges/",
    "https://docs.fedoraproject.org/nn/fedora/f32/system-administrators-guide/infrastructure-services/OpenSSH/":
        "https://docs.fedoraproject.org/cs/fedora/f30/system-administrators-guide/infrastructure-services/OpenSSH/",
    "https://manpages.debian.org/bookworm/libc-bin/getent.1.en.html":
        "https://manpages.debian.org/bookworm/manpages/getent.1.en.html",
}


def _load_site() -> dict:
    with open(SITE_CONFIG, encoding="utf-8") as f:
        return json.load(f)


def _ensure_document_shell(text: str, meta: dict) -> str:
    """Repair historical fragments that have </head>/<body> but no opening document shell."""
    prefix_probe = text[:1000].lower()
    if "<html" in prefix_probe:
        return text

    issue = int(meta["issue"])
    title = html.escape(str(meta["title"]), quote=True)
    lede = html.escape(str(meta["lede"]), quote=True)
    shell = "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="vi">',
            "<head>",
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"<title>{title} — Linux Daily #{issue:03d}</title>",
            f'<meta name="description" content="{lede}">',
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&amp;family=JetBrains+Mono:wght@400;500;700&amp;family=Noto+Serif:ital,wght@0,400;0,600;1,400&amp;display=swap" rel="stylesheet">',
            '<link rel="stylesheet" href="../assets/style.css">',
        ]
    )
    return shell + "\n" + text


def _strip_discovery_lines(text: str) -> str:
    kept: list[str] = []
    for line in text.splitlines():
        if 'rel="canonical"' in line:
            continue
        if 'type="application/rss+xml"' in line:
            continue
        if 'property="og:' in line:
            continue
        kept.append(line)
    return "\n".join(kept) + ("\n" if text.endswith("\n") else "")


def render_post(path: str) -> str:
    site = _load_site()
    meta = postmeta.read_meta(path)
    with open(path, encoding="utf-8") as f:
        text = f.read()

    for old, new in LEGACY_LINK_REPLACEMENTS.items():
        text = text.replace(old, new)

    text = _ensure_document_shell(text, meta)
    text = _strip_discovery_lines(text)
    basename = os.path.basename(path)
    canonical = urljoin(site["url"], f"posts/{basename}")
    feed_url = urljoin(site["url"], site["feed_path"])
    title = html.escape(str(meta["title"]), quote=True)
    lede = html.escape(str(meta["lede"]), quote=True)
    site_title = html.escape(str(site["title"]), quote=True)

    block = "\n".join(
        [
            f'<link rel="canonical" href="{canonical}">',
            f'<link rel="alternate" type="application/rss+xml" title="Linux Daily RSS" href="{feed_url}">',
            '<meta property="og:type" content="article">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{lede}">',
            f'<meta property="og:url" content="{canonical}">',
            f'<meta property="og:site_name" content="{site_title}">',
            '<meta property="og:locale" content="vi_VN">',
        ]
    )

    marker = '<script type="application/json" id="ld-meta">'
    if marker not in text:
        raise ValueError(f"{path}: thiếu ld-meta marker")
    return text.replace(marker, block + "\n" + marker, 1)


def run(check: bool = False) -> int:
    changed: list[str] = []
    for path in sorted(glob.glob(POSTS_GLOB)):
        expected = render_post(path)
        with open(path, encoding="utf-8") as f:
            current = f.read()
        if current == expected:
            continue
        changed.append(os.path.relpath(path, ROOT))
        if not check:
            with open(path, "w", encoding="utf-8") as f:
                f.write(expected)

    if check and changed:
        for path in changed:
            print(f"LỖI: metadata/link backfill chưa đồng bộ: {path}", file=sys.stderr)
        return 1
    print(
        f"OK: historical metadata/link backfill "
        f"{'đồng bộ' if check else 'đã cập nhật'} ({len(changed)} file thay đổi)."
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

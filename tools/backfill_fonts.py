#!/usr/bin/env python3
"""Normalize historical post font loading to self-hosted WOFF2 assets."""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")

GOOGLE_FONT_TAG = re.compile(
    r'<link\b[^>]*(?:fonts\.googleapis\.com|fonts\.gstatic\.com)[^>]*>\s*',
    re.IGNORECASE,
)
LOCAL_BLOCK = (
    '<link rel="preload" href="../assets/fonts/be-vietnam-pro-800.woff2" '
    'as="font" type="font/woff2" crossorigin>\n'
    '<link rel="stylesheet" href="../assets/fonts.css">\n'
)
STYLE_LINK = '<link rel="stylesheet" href="../assets/style.css">'


def transform(text: str) -> str:
    """Return post HTML using only local web-font resources."""
    text = GOOGLE_FONT_TAG.sub("", text)
    text = text.replace(LOCAL_BLOCK, "")
    if STYLE_LINK not in text:
        raise ValueError("post thiếu shared stylesheet link")
    return text.replace(STYLE_LINK, LOCAL_BLOCK + STYLE_LINK, 1)


def run(check: bool = False) -> int:
    changed: list[str] = []
    for path in sorted(glob.glob(POSTS_GLOB)):
        with open(path, encoding="utf-8") as f:
            current = f.read()
        expected = transform(current)
        if expected == current:
            continue
        changed.append(os.path.relpath(path, ROOT))
        if not check:
            with open(path, "w", encoding="utf-8") as f:
                f.write(expected)

    if check and changed:
        print(
            "LỖI: font loading chưa được self-host đồng bộ: " + ", ".join(changed),
            file=sys.stderr,
        )
        return 1
    if not check and changed:
        print(f"Đã chuẩn hóa self-host font cho {len(changed)} bài lịch sử.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

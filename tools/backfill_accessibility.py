#!/usr/bin/env python3
"""Deterministically backfill skip-link/main landmarks into historical post HTML."""
from __future__ import annotations

import argparse
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")
SKIP_LINK = '<a class="skip-link" href="#main-content">Đi tới nội dung chính</a>'
MAIN_OPEN = '<main id="main-content">'
MAIN_CLOSE = "</main>"


def transform(text: str) -> str:
    if SKIP_LINK not in text:
        marker = '<body class="post">'
        if marker not in text:
            raise ValueError("thiếu <body class=\"post\">")
        text = text.replace(marker, marker + "\n" + SKIP_LINK, 1)

    if MAIN_OPEN not in text:
        marker = SKIP_LINK
        text = text.replace(marker, marker + "\n" + MAIN_OPEN, 1)
        if "</body>" not in text:
            raise ValueError("thiếu </body>")
        text = text.replace("</body>", MAIN_CLOSE + "\n</body>", 1)

    return text


def run(check: bool = False) -> int:
    drift: list[str] = []
    changed = 0
    for path in sorted(glob.glob(POSTS_GLOB)):
        with open(path, encoding="utf-8") as f:
            current = f.read()
        try:
            expected = transform(current)
        except ValueError as exc:
            print(f"LỖI: {os.path.relpath(path, ROOT)}: {exc}")
            return 1
        if current == expected:
            continue
        if check:
            drift.append(os.path.relpath(path, ROOT))
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(expected)
            changed += 1

    if drift:
        print("LỖI: accessibility landmark chưa được backfill: " + ", ".join(drift))
        print("Chạy `python3 tools/build.py` rồi commit lại.")
        return 1
    if check:
        print("OK: historical accessibility landmarks đã đồng bộ.")
    else:
        print(f"Đã backfill accessibility landmark cho {changed} bài.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Backfill accessibility landmarks cho post lịch sử.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

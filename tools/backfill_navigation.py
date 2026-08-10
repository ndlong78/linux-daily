#!/usr/bin/env python3
"""Deterministically backfill the shared global navigation into post HTML."""
from __future__ import annotations

import argparse
import glob
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "templates"
NAV_TEMPLATE = "_global-nav.template.html"
POST_TEMPLATE = ROOT / "templates" / "post.template.html"
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
NAV_RE = re.compile(r'<nav class="global-nav"[^>]*>.*?</nav>\n?', re.DOTALL)


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def render_navigation(prefix: str = "../", current: str = "") -> str:
    return _env().get_template(NAV_TEMPLATE).render(
        nav_prefix=prefix,
        nav_current=current,
    ).strip()


def transform(text: str) -> str:
    marker = '<div class="wrap">'
    if marker not in text:
        raise ValueError('thiếu <div class="wrap">')
    clean = NAV_RE.sub("", text)
    before, after = clean.split(marker, 1)
    after = after.lstrip("\r\n")
    nav = render_navigation()
    return before + marker + "\n" + nav + "\n" + after


def run(check: bool = False) -> int:
    paths = [POST_TEMPLATE, *[Path(p) for p in sorted(glob.glob(POSTS_GLOB))]]
    drift: list[str] = []
    changed = 0
    for path in paths:
        current = path.read_text(encoding="utf-8")
        try:
            expected = transform(current)
        except ValueError as exc:
            print(f"LỖI: {path.relative_to(ROOT)}: {exc}")
            return 1
        if current == expected:
            continue
        if check:
            drift.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(expected, encoding="utf-8")
            changed += 1
    if drift:
        print("LỖI: global navigation chưa đồng bộ: " + ", ".join(drift))
        print("Chạy `python3 tools/build.py` rồi commit lại.")
        return 1
    print(
        "OK: global navigation đã đồng bộ."
        if check
        else f"Đã backfill global navigation cho {changed} artifact."
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

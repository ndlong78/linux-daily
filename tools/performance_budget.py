#!/usr/bin/env python3
"""Deterministic artifact-size performance budget for Linux Daily."""
from __future__ import annotations

import argparse
import glob
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUDGETS = {
    "homepage_html": 256 * 1024,
    "post_html_each": 512 * 1024,
    "css_each": 128 * 1024,
    "font_each": 1280 * 1024,
    "fonts_total": 2560 * 1024,
    "social_image_each": 2 * 1024 * 1024,
    "social_images_total": 32 * 1024 * 1024,
}


@dataclass(frozen=True)
class Finding:
    label: str
    size: int
    limit: int
    path: str


def _size(path: Path) -> int:
    return path.stat().st_size


def _over(label: str, path: Path, limit: int) -> Finding | None:
    size = _size(path)
    return Finding(label, size, limit, str(path.relative_to(ROOT))) if size > limit else None


def collect() -> tuple[list[Finding], dict[str, int]]:
    failures: list[Finding] = []
    metrics: dict[str, int] = {}

    homepage = ROOT / "index.html"
    metrics["homepage_html"] = _size(homepage)
    f = _over("homepage_html", homepage, BUDGETS["homepage_html"])
    if f:
        failures.append(f)

    posts = [Path(p) for p in glob.glob(str(ROOT / "posts" / "post-*.html"))]
    metrics["post_html_max"] = max((_size(p) for p in posts), default=0)
    for p in posts:
        f = _over("post_html_each", p, BUDGETS["post_html_each"])
        if f:
            failures.append(f)

    css = [ROOT / "assets" / "style.css", ROOT / "assets" / "fonts.css"]
    metrics["css_total"] = sum(_size(p) for p in css if p.exists())
    for p in css:
        if p.exists():
            f = _over("css_each", p, BUDGETS["css_each"])
            if f:
                failures.append(f)

    fonts = [Path(p) for p in glob.glob(str(ROOT / "assets" / "fonts" / "*.woff2"))]
    metrics["fonts_total"] = sum(_size(p) for p in fonts)
    if metrics["fonts_total"] > BUDGETS["fonts_total"]:
        failures.append(
            Finding(
                "fonts_total",
                metrics["fonts_total"],
                BUDGETS["fonts_total"],
                "assets/fonts/*.woff2",
            )
        )
    for p in fonts:
        f = _over("font_each", p, BUDGETS["font_each"])
        if f:
            failures.append(f)

    social = [Path(p) for p in glob.glob(str(ROOT / "posts" / "social" / "post-*-code.png"))]
    metrics["social_images_total"] = sum(_size(p) for p in social)
    if metrics["social_images_total"] > BUDGETS["social_images_total"]:
        failures.append(
            Finding(
                "social_images_total",
                metrics["social_images_total"],
                BUDGETS["social_images_total"],
                "posts/social/*.png",
            )
        )
    for p in social:
        f = _over("social_image_each", p, BUDGETS["social_image_each"])
        if f:
            failures.append(f)

    return failures, metrics


def _fmt(n: int) -> str:
    return f"{n / 1024:.1f} KiB"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    failures, metrics = collect()
    print("Linux Daily — Performance Budget")
    for key, value in sorted(metrics.items()):
        print(f"{key:22} {_fmt(value)}")
    if failures:
        print("\nFAIL: performance budget exceeded")
        for f in failures:
            print(f"- {f.path}: {_fmt(f.size)} > {_fmt(f.limit)} ({f.label})")
        return 1
    print("\nOK: deterministic artifact-size budgets passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

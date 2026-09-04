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
    # Ba artifact khám phá dưới đây tăng TUYẾN TÍNH theo số bài và trước PR này
    # không có cổng nào canh. Hồi quy trên 7 điểm lịch sử (#34 → #66):
    #
    #     archive.html          479 B/bài   → 474 KiB ở 1000 bài, chạm 256 KiB ở #533
    #     search-index.json     575 B/bài   → 565 KiB ở 1000 bài, chạm 256 KiB ở #449
    #     learning-paths.html  1037 B/bài   → 1006 KiB ở 1000 bài, chạm 256 KiB ở #259
    #
    # `learning-paths.html` mới là chỗ đau, không phải archive: nó tăng gấp đôi
    # archive và chạm trần chỉ sau ~193 bài nữa. Đặt cùng trần 256 KiB với
    # homepage để khi cái nào chạm thì xử lý giống nhau — phân trang hoặc tách
    # file — chứ không phải nới trần.
    "archive_html": 256 * 1024,
    "search_index_json": 256 * 1024,
    "learning_paths_html": 256 * 1024,
    "post_html_each": 512 * 1024,
    "css_each": 128 * 1024,
    "font_each": 1280 * 1024,
    "fonts_total": 2560 * 1024,
    "social_image_each": 2 * 1024 * 1024,
    "social_images_total": 32 * 1024 * 1024,
}


# Metric nào soi được vào trần nào. Không phải metric nào cũng có trần
# (css_total chỉ để tham khảo, trần đặt theo từng file), nên tra bằng .get().
METRIC_LIMIT = {
    "homepage_html": "homepage_html",
    "archive_html": "archive_html",
    "search_index_json": "search_index_json",
    "learning_paths_html": "learning_paths_html",
    "post_html_max": "post_html_each",
    "fonts_total": "fonts_total",
    "social_images_total": "social_images_total",
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

    # Gác mọi trang danh sách chứ không riêng index.html: phân trang giữ từng
    # trang nhỏ, nhưng nếu thẻ bài phình ra thì trang nào cũng có thể vượt.
    listing_pages = [ROOT / "index.html", *sorted(ROOT.glob("trang-*.html"))]
    metrics["homepage_html"] = max(_size(page) for page in listing_pages)
    for page in listing_pages:
        f = _over("homepage_html", page, BUDGETS["homepage_html"])
        if f:
            failures.append(f)

    # Artifact khám phá: mỗi cái một file duy nhất, phình theo số bài.
    for label, name in (
        ("archive_html", "archive.html"),
        ("search_index_json", "search-index.json"),
        ("learning_paths_html", "learning-paths.html"),
    ):
        path = ROOT / name
        if not path.exists():
            continue
        metrics[label] = _size(path)
        f = _over(label, path, BUDGETS[label])
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
        # In cả % đã dùng: một cổng chỉ báo lúc đã vượt thì luôn báo quá muộn.
        # Artifact khám phá tăng tuyến tính theo số bài, nên % chính là dư địa
        # còn lại tính bằng bài viết.
        limit = BUDGETS.get(METRIC_LIMIT.get(key, ""))
        pct = f"{value / limit * 100:5.1f}% ngân sách" if limit else ""
        print(f"{key:22} {_fmt(value):>10}  {pct}".rstrip())
    if failures:
        print("\nFAIL: performance budget exceeded")
        for f in failures:
            print(f"- {f.path}: {_fmt(f.size)} > {_fmt(f.limit)} ({f.label})")
        return 1
    print("\nOK: deterministic artifact-size budgets passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

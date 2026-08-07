#!/usr/bin/env python3
"""
build.py — Một lệnh duy nhất: dựng index.html + feed.xml + sitemap/robots rồi chạy quality gate.

  python3 tools/build.py            # dựng output + kiểm định (exit != 0 nếu có lỗi)
  python3 tools/build.py --check     # không ghi; chỉ kiểm tra output đồng bộ + quality gate

Gộp build_index, build_feed, build_sitemap, validate_repo và source-backed technical gate
vào một luồng, để người dùng và CI chỉ cần nhớ một lệnh.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_feed  # noqa: E402
import build_index  # noqa: E402
import build_sitemap  # noqa: E402
import validate_repo  # noqa: E402
import validate_sources  # noqa: E402


def _print_errors(title: str, errors: list[str]) -> None:
    print(f"✗ {title}: {len(errors)} lỗi", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)


def _check_file(path: str, expected: str, label: str) -> bool:
    current = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            current = f.read()
    if current != expected:
        print(
            f"LỖI: {label} chưa đồng bộ. Chạy `python3 tools/build.py` rồi commit lại.",
            file=sys.stderr,
        )
        return False
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dựng website output rồi chạy quality gate.")
    ap.add_argument(
        "--check",
        action="store_true",
        help="Không ghi; chỉ kiểm tra index/feed/sitemap/robots đồng bộ + quality gate.",
    )
    args = ap.parse_args(argv)

    index_out, post_count = build_index.render_index()
    feed_out, feed_count = build_feed.render_feed()
    sitemap_out, sitemap_count = build_sitemap.render_sitemap()
    robots_out = build_sitemap.render_robots()

    if args.check:
        ok_index = _check_file(build_index.INDEX_PATH, index_out, "index.html")
        ok_feed = _check_file(build_feed.FEED_PATH, feed_out, "feed.xml")
        ok_sitemap = _check_file(build_sitemap.SITEMAP_PATH, sitemap_out, "sitemap.xml")
        ok_robots = _check_file(build_sitemap.ROBOTS_PATH, robots_out, "robots.txt")
        if not (ok_index and ok_feed and ok_sitemap and ok_robots):
            return 1
        print(f"OK: index.html đã đồng bộ ({post_count} bài).")
        print(f"OK: feed.xml đã đồng bộ ({feed_count} bài mới nhất).")
        print(f"OK: sitemap.xml đã đồng bộ ({sitemap_count} URL).")
        print("OK: robots.txt đã đồng bộ.")
    else:
        with open(build_index.INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(index_out)
        with open(build_feed.FEED_PATH, "w", encoding="utf-8") as f:
            f.write(feed_out)
        with open(build_sitemap.SITEMAP_PATH, "w", encoding="utf-8") as f:
            f.write(sitemap_out)
        with open(build_sitemap.ROBOTS_PATH, "w", encoding="utf-8") as f:
            f.write(robots_out)
        print(f"Đã dựng index.html với {post_count} bài.")
        print(f"Đã dựng feed.xml với {feed_count} bài mới nhất.")
        print(f"Đã dựng sitemap.xml với {sitemap_count} URL.")
        print("Đã dựng robots.txt.")

    repo_report = validate_repo.run()
    if repo_report.errors:
        _print_errors("Quality gate", repo_report.errors)
        return 1

    source_report = validate_sources.run()
    if source_report.errors:
        _print_errors("Source-backed gate", source_report.errors)
        return 1

    print("✓ Build + RSS + sitemap/robots + quality gate + source-backed review: tất cả kiểm tra đều đạt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

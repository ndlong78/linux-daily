#!/usr/bin/env python3
"""
build.py — Một lệnh duy nhất: dựng website output rồi chạy quality gate.

  python3 tools/build.py            # dựng output + chuẩn hóa post metadata + kiểm định
  python3 tools/build.py --check    # không ghi; chỉ kiểm tra mọi artifact/post đã đồng bộ

Gộp index, archive/search, learning paths, RSS, sitemap/robots, historical discovery + social preview metadata,
related-content navigation, self-hosted font loading, accessibility landmarks,
structural/source-backed validation, website/SEO consistency và deterministic internal-link
gate vào một luồng. External HTTP checks chạy riêng trong CI để lỗi mạng/website bên thứ ba
không che mất quality gate local.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backfill_accessibility  # noqa: E402
import backfill_fonts  # noqa: E402
import backfill_site_metadata  # noqa: E402
import build_archive  # noqa: E402
import build_feed  # noqa: E402
import build_index  # noqa: E402
import build_sitemap  # noqa: E402
import check_links  # noqa: E402
import learning_paths  # noqa: E402
import related_content  # noqa: E402
import validate_accessibility  # noqa: E402
import validate_fonts  # noqa: E402
import validate_repo  # noqa: E402
import validate_site  # noqa: E402
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
        help="Không ghi; chỉ kiểm tra website artifacts + historical post metadata đồng bộ.",
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
        if build_archive.run(check=True) != 0:
            return 1
        if learning_paths.run(check=True) != 0:
            return 1
        if backfill_site_metadata.run(check=True) != 0:
            return 1
        if backfill_accessibility.run(check=True) != 0:
            return 1
        if backfill_fonts.run(check=True) != 0:
            return 1
        if related_content.run(check=True) != 0:
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
        if build_archive.run(check=False) != 0:
            return 1
        if learning_paths.run(check=False) != 0:
            return 1
        if backfill_site_metadata.run(check=False) != 0:
            return 1
        if backfill_accessibility.run(check=False) != 0:
            return 1
        if backfill_fonts.run(check=False) != 0:
            return 1
        if related_content.run(check=False) != 0:
            return 1
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

    site_report = validate_site.run()
    if site_report.errors:
        _print_errors("Website/SEO gate", site_report.errors)
        return 1

    font_report = validate_fonts.run()
    if font_report.errors:
        _print_errors("Self-host font gate", font_report.errors)
        return 1

    accessibility_report = validate_accessibility.run()
    if accessibility_report.errors:
        _print_errors("Accessibility gate", accessibility_report.errors)
        return 1

    link_errors = check_links.check_internal()
    if link_errors:
        _print_errors("Internal-link gate", link_errors)
        return 1

    print(
        "✓ Build + archive/search + learning paths + RSS + sitemap/robots + canonical/OG/social + related navigation + "
        "self-host fonts + website/SEO + accessibility + source-backed review + internal links: "
        "tất cả kiểm tra đều đạt."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
build.py — Một lệnh duy nhất: dựng lại index.html rồi chạy quality gate.

  python3 tools/build.py            # dựng index.html + kiểm định (exit != 0 nếu có lỗi)
  python3 tools/build.py --check     # không ghi; chỉ kiểm tra index đồng bộ + quality gate

Gộp build_index, validate_repo và source-backed technical gate vào một luồng, để
người dùng và CI chỉ cần nhớ một lệnh.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_index  # noqa: E402
import validate_repo  # noqa: E402
import validate_sources  # noqa: E402


def _print_errors(title: str, errors: list[str]) -> None:
    print(f"✗ {title}: {len(errors)} lỗi", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dựng index.html rồi chạy quality gate.")
    ap.add_argument(
        "--check",
        action="store_true",
        help="Không ghi; chỉ kiểm tra index đồng bộ + quality gate.",
    )
    args = ap.parse_args(argv)

    out, n = build_index.render_index()

    if args.check:
        current = ""
        if os.path.exists(build_index.INDEX_PATH):
            with open(build_index.INDEX_PATH, encoding="utf-8") as f:
                current = f.read()
        if current != out:
            print(
                "LỖI: index.html chưa đồng bộ với posts/. "
                "Chạy `python3 tools/build.py` rồi commit lại.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: index.html đã đồng bộ ({n} bài).")
    else:
        with open(build_index.INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Đã dựng index.html với {n} bài.")

    repo_report = validate_repo.run()
    if repo_report.errors:
        _print_errors("Quality gate", repo_report.errors)
        return 1

    source_report = validate_sources.run()
    if source_report.errors:
        _print_errors("Source-backed gate", source_report.errors)
        return 1

    print("✓ Build + quality gate + source-backed review: tất cả kiểm tra đều đạt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

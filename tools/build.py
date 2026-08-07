#!/usr/bin/env python3
"""
build.py — Một lệnh duy nhất: dựng lại index.html rồi chạy quality gate.

  python3 tools/build.py            # dựng index.html + kiểm định (exit != 0 nếu có lỗi)
  python3 tools/build.py --check     # không ghi; chỉ kiểm tra index đồng bộ + quality gate

Gộp build_index (render từ metadata + Jinja2) và validate_repo vào một luồng, để
người dùng và CI chỉ cần nhớ một lệnh.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_index  # noqa: E402
import validate_repo  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dựng index.html rồi chạy quality gate.")
    ap.add_argument("--check", action="store_true",
                    help="Không ghi; chỉ kiểm tra index đồng bộ + quality gate.")
    args = ap.parse_args(argv)

    out, n = build_index.render_index()

    if args.check:
        current = ""
        if os.path.exists(build_index.INDEX_PATH):
            with open(build_index.INDEX_PATH, encoding="utf-8") as f:
                current = f.read()
        if current != out:
            print("LỖI: index.html chưa đồng bộ với posts/. "
                  "Chạy `python3 tools/build.py` rồi commit lại.", file=sys.stderr)
            return 1
        print(f"OK: index.html đã đồng bộ ({n} bài).")
    else:
        with open(build_index.INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Đã dựng index.html với {n} bài.")

    report = validate_repo.run()
    if report.errors:
        print(f"✗ Quality gate: {len(report.errors)} lỗi", file=sys.stderr)
        for e in report.errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("✓ Build + quality gate: tất cả kiểm tra đều đạt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

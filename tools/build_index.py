#!/usr/bin/env python3
"""
build_index.py — Quét posts/post-*.html và dựng trang chủ index.html liệt kê bài,
mới nhất lên đầu. Đọc **metadata có cấu trúc** (khối <script id="ld-meta">) qua
tools/postmeta.py — KHÔNG bới HTML bằng regex — rồi render qua template Jinja2
templates/index.template.html. CSS chung ở assets/style.css.

Dùng:
  python3 tools/build_index.py            # dựng lại index.html
  python3 tools/build_index.py --check     # chỉ kiểm tra index.html đã đồng bộ chưa
"""
import argparse
import glob
import html
import os
import sys

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postmeta  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
INDEX_PATH = os.path.join(ROOT, "index.html")
TEMPLATES_DIR = os.path.join(ROOT, "templates")
INDEX_TEMPLATE = "index.template.html"


def _fmt_date(iso: str) -> str:
    """2026-08-07 -> 07·08·2026 (định dạng hiển thị trên thẻ)."""
    y, m, d = iso.split("-")
    return f"{int(d):02d}·{int(m):02d}·{int(y):04d}"


def collect_posts(posts_dir=POSTS_DIR):
    """Đọc metadata mọi bài, trả danh sách đã sắp mới→cũ (theo số bài giảm dần)."""
    posts = []
    for path in glob.glob(os.path.join(posts_dir, "post-*.html")):
        meta = postmeta.read_meta(path)
        n = int(meta["issue"])
        posts.append({
            "n": n,
            "href": "posts/" + os.path.basename(path),
            "num": f"#{n:03d}",
            "date": _fmt_date(meta["date"]),
            "axis": meta["eyebrow"],  # thẻ dùng eyebrow (trục · phụ đề)
            "title": meta["title"],
            "lede": meta["lede"],
        })
    posts.sort(key=lambda p: p["n"], reverse=True)
    return posts


def _env() -> Environment:
    # autoescape=False: tự html.escape trong Python để khớp byte với bản cũ
    # (html.escape dùng &#x27;/&quot;, khác markupsafe của Jinja).
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def render_index(posts_dir=POSTS_DIR):
    """Dựng nội dung HTML của trang chủ (không ghi ra đĩa) — dùng chung cho build và --check."""
    posts = collect_posts(posts_dir)
    ctx = [{
        "href": html.escape(p["href"]),
        "num": html.escape(p["num"]),
        "axis": html.escape(p["axis"]),
        "date": html.escape(p["date"]),
        "title": html.escape(p["title"]),
        "lede": html.escape(p["lede"]),
    } for p in posts]
    out = _env().get_template(INDEX_TEMPLATE).render(posts=ctx, count=len(posts))
    return out, len(posts)


def main():
    ap = argparse.ArgumentParser(description="Dựng hoặc kiểm tra index.html.")
    ap.add_argument("--check", action="store_true",
                    help="Không ghi; báo lỗi nếu index.html chưa được dựng lại từ posts/ hiện tại.")
    args = ap.parse_args()

    out, n = render_index()

    if args.check:
        current = ""
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, encoding="utf-8") as f:
                current = f.read()
        if current != out:
            print("LỖI: index.html chưa đồng bộ với posts/. "
                  "Chạy `python3 tools/build_index.py` rồi commit lại.", file=sys.stderr)
            return 1
        print(f"OK: index.html đã đồng bộ ({n} bài).")
        return 0

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Đã dựng index.html với {n} bài.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

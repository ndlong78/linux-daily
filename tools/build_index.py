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
import json
import os
import sys
from urllib.parse import urljoin

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postmeta  # noqa: E402
import socialmeta  # noqa: E402

# Trang chủ liệt kê bài mới nhất; phần còn lại nằm ở trang-2.html, trang-3.html…
#
# Vì sao phải phân trang: index.html trước đây liệt kê MỌI bài, và đo trên lịch sử
# git cho thấy nó tăng tuyến tính 0.570 KiB mỗi bài (5 mốc, từ #044 tới #065).
# Ngân sách `homepage_html` là 256 KiB và `performance_budget.py` nằm trong
# `publish.py check`, nên ở khoảng bài #435 nó sẽ CHẶN CỨNG việc ra bài hằng ngày.
# 20 bài/trang giữ mỗi trang ở ~19 KiB bất kể series dài bao nhiêu.
POSTS_PER_PAGE = 20

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
INDEX_PATH = os.path.join(ROOT, "index.html")
SITE_CONFIG = os.path.join(ROOT, "site.json")
TEMPLATES_DIR = os.path.join(ROOT, "templates")
INDEX_TEMPLATE = "index.template.html"


def _fmt_date(iso: str) -> str:
    """2026-08-07 -> 07·08·2026 (định dạng hiển thị trên thẻ)."""
    y, m, d = iso.split("-")
    return f"{int(d):02d}·{int(m):02d}·{int(y):04d}"


def _load_site(path=SITE_CONFIG):
    with open(path, encoding="utf-8") as f:
        site = json.load(f)
    site["url"] = site["url"].rstrip("/") + "/"
    return site


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
            "axis": meta["eyebrow"],
            "title": meta["title"],
            "lede": meta["lede"],
        })
    posts.sort(key=lambda p: p["n"], reverse=True)
    return posts


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def page_name(page: int) -> str:
    """Trang 1 là index.html — không đổi URL trang chủ đã publish."""
    return "index.html" if page <= 1 else f"trang-{page}.html"


def paginate(posts: list, per_page: int = POSTS_PER_PAGE) -> list[list]:
    """Chia bài thành các trang. Kho rỗng vẫn cho đúng một trang (index.html)."""
    if not posts:
        return [[]]
    return [posts[i:i + per_page] for i in range(0, len(posts), per_page)]


def render_pages(posts_dir=POSTS_DIR, site_config=SITE_CONFIG) -> tuple[dict[str, str], int]:
    """{tên file: nội dung} cho mọi trang danh sách. Không ghi ra đĩa."""
    posts = collect_posts(posts_dir)
    site = _load_site(site_config)
    pages = paginate(posts)
    total_pages = len(pages)

    social = None
    if posts:
        latest = posts[0]
        social = socialmeta.image_info(latest["n"], latest["title"], site["url"])

    template = _env().get_template(INDEX_TEMPLATE)
    out: dict[str, str] = {}
    for index, page_posts in enumerate(pages, start=1):
        name = page_name(index)
        canonical = site["url"] if index == 1 else urljoin(site["url"], name)
        out[name] = template.render(
            posts=[{
                "href": html.escape(p["href"]),
                "num": html.escape(p["num"]),
                "axis": html.escape(p["axis"]),
                "date": html.escape(p["date"]),
                "title": html.escape(p["title"]),
                "lede": html.escape(p["lede"]),
            } for p in page_posts],
            count=len(posts),
            page=index,
            total_pages=total_pages,
            prev_href=html.escape(page_name(index - 1), quote=True) if index > 1 else "",
            next_href=html.escape(page_name(index + 1), quote=True) if index < total_pages else "",
            canonical_url=html.escape(canonical, quote=True),
            feed_url=html.escape(urljoin(site["url"], site["feed_path"]), quote=True),
            site_title=html.escape(site["title"], quote=True),
            social_image_url=html.escape(str(social["url"]), quote=True) if social else "",
            social_image_width=social["width"] if social else 0,
            social_image_height=social["height"] if social else 0,
            social_image_alt=html.escape(str(social["alt"]), quote=True) if social else "",
            social_image_mime=html.escape(str(social["mime"]), quote=True) if social else "",
        )
    return out, len(posts)


def stale_pages(expected: dict[str, str], root: str = ROOT) -> list[str]:
    """trang-N.html còn sót khi series ngắn lại — không dọn thì chúng thành trang mồ côi."""
    keep = set(expected)
    return sorted(
        os.path.basename(path)
        for path in glob.glob(os.path.join(root, "trang-*.html"))
        if os.path.basename(path) not in keep
    )


def render_index(posts_dir=POSTS_DIR, site_config=SITE_CONFIG):
    """Chỉ trang 1. Giữ lại vì test và công cụ khác đang gọi."""
    pages, count = render_pages(posts_dir, site_config)
    return pages[page_name(1)], count


def main():
    ap = argparse.ArgumentParser(description="Dựng hoặc kiểm tra index.html.")
    ap.add_argument(
        "--check",
        action="store_true",
        help="Không ghi; báo lỗi nếu index.html chưa được dựng lại từ posts/ hiện tại.",
    )
    args = ap.parse_args()

    pages, n = render_pages()
    stale = stale_pages(pages)

    if args.check:
        lech = []
        for name, content in sorted(pages.items()):
            path = os.path.join(ROOT, name)
            current = ""
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    current = f.read()
            if current != content:
                lech.append(name)
        lech.extend(f"{name} (thừa, cần xoá)" for name in stale)
        if lech:
            print(
                "LỖI: trang danh sách chưa đồng bộ với posts/: " + ", ".join(lech)
                + ". Chạy `python3 tools/build_index.py` rồi commit lại.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {len(pages)} trang danh sách đã đồng bộ ({n} bài).")
        return 0

    for name, content in pages.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(content)
    for name in stale:
        os.remove(os.path.join(ROOT, name))
    thua = f", xoá {len(stale)} trang thừa" if stale else ""
    print(f"Đã dựng {len(pages)} trang danh sách với {n} bài{thua}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

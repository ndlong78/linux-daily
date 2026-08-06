#!/usr/bin/env python3
"""
build_index.py — Quét posts/post-*.html và dựng trang chủ index.html liệt kê bài,
mới nhất lên đầu. Dùng CSS chung ở assets/style.css. Chạy sau mỗi lần thêm bài.

Dùng:
  python3 tools/build_index.py            # dựng lại index.html
  python3 tools/build_index.py --check     # chỉ kiểm tra index.html đã đồng bộ chưa
"""
import argparse
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
INDEX_PATH = os.path.join(ROOT, "index.html")


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def grab(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""


def parse_post(path):
    with open(path, encoding="utf-8") as fh:
        t = fh.read()
    issue_raw = grab(r'<span class="issue">(.*?)</span>', t)
    num, date = issue_raw, ""
    if "·" in issue_raw:
        num, date = (x.strip() for x in issue_raw.split("·", 1))
    axis = strip_tags(grab(r'<p class="eyebrow">(.*?)</p>', t))
    title = strip_tags(grab(r"<h1>(.*?)</h1>", t))
    lede = strip_tags(grab(r'<p class="lede">(.*?)</p>', t))
    n = 0
    m = re.search(r"#(\d+)", num)
    if m:
        n = int(m.group(1))
    return {"file": "posts/" + os.path.basename(path), "num": num, "n": n,
            "date": date, "axis": axis, "title": title, "lede": lede}


def card(p):
    return f'''      <a class="card" href="{html.escape(p['file'])}">
        <div class="card-top">
          <span class="c-issue">{html.escape(p['num'])}</span>
          <span class="c-axis">{html.escape(p['axis'])}</span>
          <span class="c-date">{html.escape(p['date'])}</span>
        </div>
        <h2>{html.escape(p['title'])}</h2>
        <p>{html.escape(p['lede'])}</p>
      </a>'''


TEMPLATE = '''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Linux Daily — Học quản trị Linux/Unix mỗi bài một chủ đề</title>
<meta name="description" content="Series bài học Linux/Unix system administration: Ubuntu, Xubuntu, Debian, Fedora và FreeBSD. Mỗi bài một chủ đề, có sơ đồ và lệnh copy-paste.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&family=Noto+Serif:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body class="home">
  <div class="wrap">
    <header class="site">
      <div class="site-brand">Linux Daily</div>
      <h1 class="site">Học quản trị Linux &amp; Unix, mỗi bài một chủ đề</h1>
      <p class="site-lede">Ubuntu · Xubuntu · Debian · Fedora · FreeBSD. Mỗi bài kèm sơ đồ, lệnh copy-paste và cạm bẫy thực tế — luôn tách rõ FreeBSD.</p>
      <div class="count">{{COUNT}} BÀI</div>
    </header>
    <main class="list">
{{CARDS}}
    </main>
    <footer>Linux Daily · #LinuxDaily #SysAdmin</footer>
  </div>
</body>
</html>
'''


def render_index(posts_dir=POSTS_DIR):
    """Dựng nội dung HTML của trang chủ (không ghi ra đĩa) — dùng chung cho build và --check."""
    posts = [parse_post(p) for p in glob.glob(os.path.join(posts_dir, "post-*.html"))]
    posts.sort(key=lambda x: x["n"], reverse=True)
    cards = "\n".join(card(p) for p in posts) or '<p class="empty">Chưa có bài nào.</p>'
    out = TEMPLATE.replace("{{CARDS}}", cards).replace("{{COUNT}}", str(len(posts)))
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

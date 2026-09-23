#!/usr/bin/env python3
"""Normalize historical post font loading to self-hosted WOFF2 assets."""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")

GOOGLE_FONT_TAG = re.compile(
    r'<link\b[^>]*(?:fonts\.googleapis\.com|fonts\.gstatic\.com)[^>]*>\s*',
    re.IGNORECASE,
)
LOCAL_BLOCK = (
    '<link rel="preload" href="../assets/fonts/be-vietnam-pro-800.woff2" '
    'as="font" type="font/woff2" crossorigin>\n'
    '<link rel="stylesheet" href="../assets/fonts.css">\n'
)
# Bắt MỌI link font cục bộ đang có, bất kể thứ tự thuộc tính hay xuống dòng,
# để transform() gỡ sạch trước khi chèn lại đúng một khối. Khớp theo `href` là
# đủ hẹp: chỉ hai tài nguyên font cục bộ mới có đường dẫn này.
LOCAL_FONT_TAG = re.compile(
    r'<link\b[^>]*href="\.\./assets/fonts(?:\.css|/be-vietnam-pro-800\.woff2)"[^>]*>\s*',
    re.IGNORECASE,
)
STYLE_LINK = '<link rel="stylesheet" href="../assets/style.css">'


def transform(text: str) -> str:
    """Return post HTML using only local web-font resources.

    Phải idempotent với MỌI hình dạng đầu vào, không chỉ khối byte-exact.
    Bản cũ chỉ xoá đúng chuỗi `LOCAL_BLOCK` rồi chèn lại một khối mới; một bài
    đã có `fonts.css` nhưng chưa có preload — hình dạng hợp lệ mà validator
    không cấm — thì chẳng có gì bị xoá, và bài nhận thêm link thứ hai. Chính
    `validate_fonts` sau đó chặn artifact do generator vừa tạo ra. Lỗi này đã
    chặn bài #084 trọn một lượt materialize.

    Cách chắc chắn: gỡ HẾT preload/fonts.css đang có (ở đâu, thứ tự nào, có
    xuống dòng hay không), rồi chèn đúng một khối trước STYLE_LINK.
    """
    text = GOOGLE_FONT_TAG.sub("", text)
    text = LOCAL_FONT_TAG.sub("", text)
    if STYLE_LINK not in text:
        raise ValueError("post thiếu shared stylesheet link")
    return text.replace(STYLE_LINK, LOCAL_BLOCK + STYLE_LINK, 1)


def run(check: bool = False) -> int:
    changed: list[str] = []
    for path in sorted(glob.glob(POSTS_GLOB)):
        with open(path, encoding="utf-8") as f:
            current = f.read()
        expected = transform(current)
        if expected == current:
            continue
        changed.append(os.path.relpath(path, ROOT))
        if not check:
            with open(path, "w", encoding="utf-8") as f:
                f.write(expected)

    if check and changed:
        print(
            "LỖI: font loading chưa được self-host đồng bộ: " + ", ".join(changed),
            file=sys.stderr,
        )
        return 1
    if not check and changed:
        print(f"Đã chuẩn hóa self-host font cho {len(changed)} bài lịch sử.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

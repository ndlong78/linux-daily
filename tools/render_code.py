#!/usr/bin/env python3
"""
render_code.py — Biến một đoạn lệnh thành ảnh PNG hợp cho Facebook/X.

Dùng:
  python3 tools/render_code.py --in snippet.txt --out posts/social/post-001-code.png \
      --title "Linux Daily #001 · Đặt IP tĩnh"

Tuỳ chọn:
  --max-cols N   Số ký tự tối đa mỗi dòng trước khi wrap (mặc định 92).
  --max-lines N  Số dòng tối đa (kể cả dòng wrap) trước khi cắt (mặc định 40).

Theme tối khớp với code block trên web (nền #13211E, chữ #E7ECEA, chú thích #8AA39B,
tiêu đề teal #7FD8CB). Ưu tiên font JetBrains Mono trong tools/fonts, không có thì
dùng DejaVu Sans Mono (đều hỗ trợ tiếng Việt).
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

BG      = (0x13, 0x21, 0x1E)
CARD    = (0x16, 0x24, 0x21)
TEXT    = (0xE7, 0xEC, 0xEA)
COMMENT = (0x8A, 0xA3, 0x9B)
TITLE   = (0x7F, 0xD8, 0xCB)
ACCENT  = (0x2E, 0xB6, 0xA3)

SCALE = 2                      # render 2x cho nét
PAD   = 30 * SCALE
FS    = 15 * SCALE             # cỡ chữ code
TFS   = 15 * SCALE             # cỡ chữ tiêu đề
LH    = int(FS * 1.55)

DEFAULT_MAX_COLS = 92
DEFAULT_MAX_LINES = 40

HERE = os.path.dirname(os.path.abspath(__file__))


def load_font(bold=False, size=FS):
    names = ["JetBrainsMono-Bold.ttf"] if bold else ["JetBrainsMono-Regular.ttf"]
    for n in names:
        p = os.path.join(HERE, "fonts", n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    # fallback DejaVu Sans Mono (thường có sẵn trên Linux CI)
    for dv in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono%s.ttf" % ("-Bold" if bold else ""),
        "/usr/share/fonts/dejavu/DejaVuSansMono%s.ttf" % ("-Bold" if bold else ""),
    ):
        if os.path.exists(dv):
            return ImageFont.truetype(dv, size)
    print(
        "LỖI: không tìm thấy font JetBrains Mono trong tools/fonts/ và cũng không có "
        "DejaVu Sans Mono trên hệ thống. Cài `fonts-dejavu` hoặc đặt font vào tools/fonts/.",
        file=sys.stderr,
    )
    raise SystemExit(2)


def split_comment(line):
    """Trả (code, comment). Chỉ tách khi thấy ' #' để không đụng '#' trong URL."""
    s = line.rstrip("\n")
    if s.lstrip().startswith("#"):
        return "", s
    idx = s.find(" #")
    if idx >= 0:
        # Giữ lại khoảng trắng trước '#' để code và comment không dính nhau.
        return s[:idx] + " ", s[idx + 1:]
    return s, None


def wrap_lines(lines, max_cols):
    """Wrap thô theo số ký tự để đầu vào bất thường không tạo ảnh siêu rộng."""
    out = []
    for raw in lines:
        s = raw.rstrip("\n")
        if len(s) <= max_cols:
            out.append(s)
            continue
        while len(s) > max_cols:
            out.append(s[:max_cols])
            s = s[max_cols:]
        out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--max-cols", type=int, default=DEFAULT_MAX_COLS)
    ap.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    args = ap.parse_args()

    with open(args.inp, encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f.readlines()]
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        print(f"LỖI: file đầu vào rỗng: {args.inp}", file=sys.stderr)
        return 2

    lines = wrap_lines(lines, args.max_cols)
    if len(lines) > args.max_lines:
        kept = args.max_lines - 1
        dropped = len(lines) - kept
        lines = lines[:kept] + [f"… (+{dropped} dòng bị cắt, giảm bớt snippet)"]

    fcode = load_font(False, FS)
    fbold = load_font(True, TFS)

    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)

    def w(txt, fnt):
        return d.textlength(txt, font=fnt)

    max_w = max([w(line, fcode) for line in lines] + [w(args.title, fbold) if args.title else 0])
    title_h = (LH + 8 * SCALE) if args.title else 0
    width  = int(max_w + PAD * 2)
    height = int(title_h + len(lines) * LH + PAD * 2)

    img = Image.new("RGB", (width, height), BG)
    dr = ImageDraw.Draw(img)
    r = 16 * SCALE
    dr.rounded_rectangle([0, 0, width - 1, height - 1], radius=r, fill=CARD)
    # thanh accent trái
    dr.rectangle([0, r, 4 * SCALE, height - r], fill=ACCENT)

    y = PAD
    if args.title:
        dr.text((PAD, y), args.title, font=fbold, fill=TITLE)
        y += title_h

    for line in lines:
        code, comment = split_comment(line)
        x = PAD
        if code:
            dr.text((x, y), code, font=fcode, fill=TEXT)
            x += w(code, fcode)
        if comment is not None:
            dr.text((x, y), comment, font=fcode, fill=COMMENT)
        y += LH

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    img.save(args.out)
    print("Đã tạo:", args.out, img.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

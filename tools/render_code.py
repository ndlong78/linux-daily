#!/usr/bin/env python3
"""
render_code.py — Biến một đoạn lệnh thành ảnh PNG hợp cho Facebook/X.

Dùng:
  python3 tools/render_code.py --in snippet.txt --out posts/social/post-001-code.png \
      --title "Linux Daily #001 · Đặt IP tĩnh"

Theme tối khớp với code block trên web (nền #13211E, chữ #E7ECEA, chú thích #8AA39B,
tiêu đề teal #7FD8CB). Ưu tiên font JetBrains Mono trong tools/fonts, không có thì
dùng DejaVu Sans Mono (đều hỗ trợ tiếng Việt).
"""
import argparse, os, sys
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

HERE = os.path.dirname(os.path.abspath(__file__))

def load_font(bold=False, size=FS):
    names = (["JetBrainsMono-Bold.ttf"] if bold else ["JetBrainsMono-Regular.ttf"])
    for n in names:
        p = os.path.join(HERE, "fonts", n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    # fallback DejaVu
    dv = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono%s.ttf" % ("-Bold" if bold else "")
    return ImageFont.truetype(dv, size)

def split_comment(line):
    """Trả (code, comment). Chỉ tách khi thấ ' #' để không đụng '#' trong URL."""
    s = line.rstrip("\n")
    if s.lstrip().startswith("#"):
        return "", s
    idx = s.find(" #")
    if idx >= 0:
        return s[:idx], s[idx+1:]
    return s, None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--title", default="")
    args = ap.parse_args()

    with open(args.inp, encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f.readlines()]
    while lines and not lines[-1].strip():
        lines.pop()

    fcode = load_font(False, FS)
    fbold = load_font(True, TFS)

    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    def w(txt, fnt):
        return d.textlength(txt, font=fnt)

    max_w = max([w(l, fcode) for l in lines] + [w(args.title, fbold) if args.title else 0])
    title_h = (LH + 8*SCALE) if args.title else 0
    width  = int(max_w + PAD*2)
    height = int(title_h + len(lines)*LH + PAD*2)

    img = Image.new("RGB", (width, height), BG)
    dr = ImageDraw.Draw(img)
    r = 16 * SCALE
    dr.rounded_rectangle([0, 0, width-1, height-1], radius=r, fill=CARD)
    # thanh accent trái
    dr.rectangle([0, r, 4*SCALE, height-r], fill=ACCENT)

    y = PAD
    if args.title:
        dr.text((PAD, y), args.title, font=fbold, fill=TITLE)
        y += title_h

    for l in lines:
        code, comment = split_comment(l)
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

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
POST = ROOT / "posts/post-021-storage-backup-restore-recovery-lab.html"
PREVIEW = ROOT / "posts/social/post-021-code.png"
WORKFLOW = ROOT / ".github/workflows/pr69-regenerate.yml"
SELF = Path(__file__).resolve()


def normalize_post() -> None:
    html = POST.read_text(encoding="utf-8")
    if "<svg" not in html:
        figures = """

  <figure>
    <svg viewBox="0 0 760 250" role="img" aria-label="Chuỗi layer của lab storage từ image file tới dữ liệu">
      <rect width="760" height="250" fill="#F7FAF9"/>
      <g font-family="Be Vietnam Pro, sans-serif" text-anchor="middle">
        <rect x="20" y="82" width="110" height="70" rx="8" fill="#F4F8F6" stroke="#0C6E61"/><text x="75" y="110" font-size="12" font-weight="700">IMAGE</text><text x="75" y="134" font-size="10">disk.img</text>
        <rect x="145" y="82" width="110" height="70" rx="8" fill="#F4F8F6" stroke="#0C6E61"/><text x="200" y="110" font-size="12" font-weight="700">PROVIDER</text><text x="200" y="134" font-size="10">loop / md</text>
        <rect x="270" y="82" width="110" height="70" rx="8" fill="#F4F8F6" stroke="#0C6E61"/><text x="325" y="110" font-size="12" font-weight="700">PARTITION</text><text x="325" y="134" font-size="10">GPT</text>
        <rect x="395" y="82" width="110" height="70" rx="8" fill="#F4F8F6" stroke="#0C6E61"/><text x="450" y="110" font-size="12" font-weight="700">FILESYSTEM</text><text x="450" y="134" font-size="10">ext4 / UFS</text>
        <rect x="520" y="82" width="100" height="70" rx="8" fill="#F4F8F6" stroke="#0C6E61"/><text x="570" y="110" font-size="12" font-weight="700">MOUNT</text><text x="570" y="134" font-size="10">mnt</text>
        <rect x="635" y="82" width="105" height="70" rx="8" fill="#14201D"/><text x="687" y="110" fill="#7FE0D2" font-size="12" font-weight="700">DATA</text><text x="687" y="134" fill="#FFFFFF" font-size="10">payload</text>
        <path d="M130 117H145M255 117H270M380 117H395M505 117H520M620 117H635" stroke="#0C6E61" stroke-width="3"/>
      </g>
    </svg>
    <figcaption>Hình 1 — Phân biệt từng layer để failure injection chỉ tác động filesystem disposable, không nhầm sang disk thật.</figcaption>
  </figure>

  <figure>
    <svg viewBox="0 0 760 270" role="img" aria-label="Quy trình recovery từ baseline checksum qua backup failure restore tới verification">
      <rect width="760" height="270" fill="#FFFFFF"/>
      <g font-family="Be Vietnam Pro, sans-serif" text-anchor="middle">
        <rect x="25" y="78" width="125" height="80" rx="8" fill="#F4F8F6" stroke="#0C6E61"/><text x="87" y="108" font-size="12" font-weight="700">BASELINE</text><text x="87" y="133" font-size="10">checksum</text>
        <rect x="175" y="78" width="125" height="80" rx="8" fill="#F4F8F6" stroke="#0C6E61"/><text x="237" y="108" font-size="12" font-weight="700">BACKUP</text><text x="237" y="133" font-size="10">independent</text>
        <rect x="325" y="78" width="125" height="80" rx="8" fill="#FBF1F0" stroke="#B23A2E"/><text x="387" y="108" font-size="12" font-weight="700">FAILURE</text><text x="387" y="133" font-size="10">disposable</text>
        <rect x="475" y="78" width="125" height="80" rx="8" fill="#F4F8F6" stroke="#0C6E61"/><text x="537" y="108" font-size="12" font-weight="700">RESTORE</text><text x="537" y="133" font-size="10">archive</text>
        <rect x="625" y="78" width="110" height="80" rx="8" fill="#14201D"/><text x="680" y="108" fill="#7FE0D2" font-size="12" font-weight="700">VERIFY</text><text x="680" y="133" fill="#FFFFFF" font-size="10">checksum OK</text>
        <path d="M150 118H175M300 118H325M450 118H475M600 118H625" stroke="#0C6E61" stroke-width="3"/>
      </g>
    </svg>
    <figcaption>Hình 2 — Backup chỉ được coi là có giá trị khi restore thành công và checksum quay về đúng baseline.</figcaption>
  </figure>"""
        html = html.replace("  </header>", "  </header>" + figures, 1)
    html = html.replace(
        '<h2><span class="num">08</span> Cleanup</h2>', '<h2>Cleanup</h2>'
    )
    html = html.replace(
        '<h2><span class="num">09</span> Cạm bẫy và bảo mật</h2>',
        '<h2>Cạm bẫy và bảo mật</h2>',
    )
    html = html.replace(
        '  <section>\n    <h2><span class="num">10</span> Bài tập tự luyện</h2>',
        '  <section class="exercise">\n    <h2>Bài tập tự luyện</h2>',
    )
    POST.write_text(html, encoding="utf-8")


def build_preview() -> None:
    image = Image.new("RGB", (948, 642), "#14211e")
    draw = ImageDraw.Draw(image)
    font_dir = Path("/usr/share/fonts/truetype/dejavu")
    regular = ImageFont.truetype(str(font_dir / "DejaVuSansMono.ttf"), 22)
    bold = ImageFont.truetype(str(font_dir / "DejaVuSansMono-Bold.ttf"), 28)
    small = ImageFont.truetype(str(font_dir / "DejaVuSansMono.ttf"), 18)
    draw.rectangle((0, 0, 10, 642), fill="#2eb6a3")
    draw.text((48, 38), "Linux Daily #021", font=bold, fill="#e7ecea")
    draw.text((48, 82), "Storage Backup / Restore Recovery Lab", font=regular, fill="#8aa39b")
    lines = [
        "$ backup-before-change",
        "  source -> independent backup target",
        "$ verify-checksum baseline",
        "  expected: payload OK",
        "$ failure-injection disposable-storage",
        "  expected: payload absent",
        "$ restore-from-backup",
        "  expected: checksum recovered",
        "$ cleanup-and-verify",
        "  loop/md provider detached",
    ]
    y = 150
    for line in lines:
        color = "#e7ecea" if line.startswith("$") else "#8aa39b"
        draw.text((62, y), line, font=regular, fill=color)
        y += 39
    draw.text(
        (48, 596),
        "Ubuntu/Xubuntu · Debian · Fedora · FreeBSD",
        font=small,
        fill="#2eb6a3",
    )
    image.save(PREVIEW, format="PNG", optimize=True)


def main() -> None:
    normalize_post()
    build_preview()
    WORKFLOW.unlink(missing_ok=True)
    SELF.unlink(missing_ok=True)
    subprocess.run(["python", "tools/build.py"], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()

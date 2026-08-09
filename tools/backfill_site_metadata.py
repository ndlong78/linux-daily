#!/usr/bin/env python3
"""Temporary PR83 wrapper; restores the canonical tool before verification."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
TOOLS = HERE.parent
ROOT = TOOLS.parent
TMP = TOOLS / ".pr83_backfill_site_metadata_original.py"

FIGURE1 = '''
<figure>
<svg viewBox="0 0 760 210" role="img" aria-label="Luồng vận hành quan sát thay đổi xác minh">
  <rect width="760" height="210" fill="#F7FAF9"/>
  <g font-family="Be Vietnam Pro, sans-serif" text-anchor="middle">
    <rect x="30" y="65" width="190" height="85" rx="8" fill="#FFFFFF" stroke="#14201D" stroke-width="2"/>
    <text x="125" y="100" font-size="15" font-weight="700">OBSERVE</text><text x="125" y="125" font-size="11">đo trạng thái thật</text>
    <rect x="285" y="65" width="190" height="85" rx="8" fill="#F4F8F6" stroke="#0C6E61" stroke-width="2"/>
    <text x="380" y="100" font-size="15" font-weight="700">CHANGE</text><text x="380" y="125" font-size="11">thay đổi có giới hạn</text>
    <rect x="540" y="65" width="190" height="85" rx="8" fill="#FFFFFF" stroke="#14201D" stroke-width="2"/>
    <text x="635" y="100" font-size="15" font-weight="700">VERIFY</text><text x="635" y="125" font-size="11">expected output</text>
    <path d="M220 108H278M475 108H533" stroke="#0C6E61" stroke-width="3"/>
  </g>
</svg>
<figcaption>Hình 1 — Quan sát trước, thay đổi có giới hạn, rồi xác minh bằng tín hiệu cụ thể.</figcaption>
</figure>
'''

FIGURE2 = '''
<figure>
<svg viewBox="0 0 760 230" role="img" aria-label="So sánh Ubuntu Xubuntu Debian Fedora và FreeBSD">
  <rect width="760" height="230" fill="#FFFFFF"/>
  <g font-family="Be Vietnam Pro, sans-serif" text-anchor="middle">
    <rect x="20" y="50" width="165" height="125" rx="8" fill="#F4F8F6" stroke="#0C6E61"/>
    <text x="102" y="82" font-size="13" font-weight="700">Ubuntu / Xubuntu</text><text x="102" y="116" font-size="11">APT · systemd</text>
    <rect x="205" y="50" width="165" height="125" rx="8" fill="#F4F8F6" stroke="#0C6E61"/>
    <text x="287" y="82" font-size="13" font-weight="700">Debian</text><text x="287" y="116" font-size="11">APT · systemd</text>
    <rect x="390" y="50" width="165" height="125" rx="8" fill="#F4F8F6" stroke="#0C6E61"/>
    <text x="472" y="82" font-size="13" font-weight="700">Fedora</text><text x="472" y="116" font-size="11">DNF · systemd</text>
    <rect x="575" y="50" width="165" height="125" rx="8" fill="#FBF1F0" stroke="#B23A2E"/>
    <text x="657" y="82" font-size="13" font-weight="700">FreeBSD</text><text x="657" y="116" font-size="11">pkg · rc.d · khác lệnh</text>
  </g>
</svg>
<figcaption>Hình 2 — Linux chia sẻ nhiều công cụ userland nhưng package/service semantics khác nhau; FreeBSD luôn được tách riêng và không dùng systemd.</figcaption>
</figure>
'''


def restore_original() -> bytes:
    result = subprocess.run(
        ["git", "show", "origin/main:tools/backfill_site_metadata.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    original = result.stdout
    TMP.write_bytes(original)
    return original


def add_visuals() -> None:
    for issue in range(34, 41):
        path = next((ROOT / "posts").glob(f"post-{issue:03d}-*.html"))
        text = path.read_text(encoding="utf-8")
        if text.count("<svg ") >= 2 and text.count("<figcaption>") >= 2:
            continue
        text = text.replace("</header>", "</header>\n" + FIGURE1, 1)
        normal_s3 = '<section><h2><span class="num">03</span>'
        lab_s3 = '<section data-lab-section="safety"><h2><span class="num">03</span>'
        if lab_s3 in text:
            text = text.replace(lab_s3, FIGURE2 + lab_s3, 1)
        else:
            text = text.replace(normal_s3, FIGURE2 + normal_s3, 1)
        path.write_text(text, encoding="utf-8")


def main() -> int:
    original = restore_original()
    try:
        proc = subprocess.run([sys.executable, str(TMP), *sys.argv[1:]], cwd=ROOT)
        if proc.returncode == 0 and "--check" not in sys.argv:
            add_visuals()
        return proc.returncode
    finally:
        HERE.write_bytes(original)
        TMP.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())

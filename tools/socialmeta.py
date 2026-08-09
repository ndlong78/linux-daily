#!/usr/bin/env python3
"""Shared social-preview metadata helpers for Linux Daily.

Historical lessons may have a dedicated ``post-NNN-code.png`` preview. New lessons do
not generate per-post social artifacts while social output is paused, so they reuse
the newest existing historical preview as a deterministic site-level fallback.
"""
from __future__ import annotations

import glob
import os
import re
from urllib.parse import urljoin

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOCIAL_DIR = os.path.join(ROOT, "posts", "social")
SOCIAL_IMAGE_RE = re.compile(r"post-(\d+)-code\.png$")


def dedicated_image_relpath(issue: int) -> str:
    return f"posts/social/post-{int(issue):03d}-code.png"


def _latest_existing_relpath() -> str | None:
    candidates: list[tuple[int, str]] = []
    for fullpath in glob.glob(os.path.join(SOCIAL_DIR, "post-*-code.png")):
        match = SOCIAL_IMAGE_RE.search(os.path.basename(fullpath))
        if match:
            candidates.append((int(match.group(1)), fullpath))
    if not candidates:
        return None
    _, latest = max(candidates, key=lambda item: item[0])
    return os.path.relpath(latest, ROOT).replace(os.sep, "/")


def image_relpath(issue: int) -> str:
    """Return a dedicated preview when present, otherwise the latest shared fallback."""
    dedicated = dedicated_image_relpath(issue)
    if os.path.isfile(os.path.join(ROOT, dedicated)):
        return dedicated
    fallback = _latest_existing_relpath()
    if fallback is None:
        raise FileNotFoundError(
            "Không có social preview image lịch sử để dùng làm fallback trong lúc social output tạm dừng."
        )
    return fallback


def image_info(issue: int, title: str, site_url: str) -> dict[str, str | int]:
    dedicated = dedicated_image_relpath(issue)
    relpath = image_relpath(issue)
    fullpath = os.path.join(ROOT, relpath)
    with Image.open(fullpath) as image:
        width, height = image.size
        fmt = (image.format or "").upper()
    if fmt != "PNG":
        raise ValueError(f"Social preview image phải là PNG: {relpath} ({fmt or 'unknown'})")
    if width <= 0 or height <= 0:
        raise ValueError(f"Social preview image có kích thước không hợp lệ: {relpath}")
    alt = (
        f"Linux Daily #{int(issue):03d} — {title}"
        if relpath == dedicated
        else "Linux Daily — ảnh preview chung trong giai đoạn social output tạm dừng"
    )
    return {
        "path": relpath,
        "url": urljoin(site_url.rstrip("/") + "/", relpath),
        "width": width,
        "height": height,
        "alt": alt,
        "mime": "image/png",
    }

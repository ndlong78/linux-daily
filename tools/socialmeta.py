#!/usr/bin/env python3
"""Shared social-preview metadata helpers for Linux Daily."""
from __future__ import annotations

import os
from urllib.parse import urljoin

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOCIAL_DIR = os.path.join(ROOT, "posts", "social")


def image_relpath(issue: int) -> str:
    return f"posts/social/post-{int(issue):03d}-code.png"


def image_info(issue: int, title: str, site_url: str) -> dict[str, str | int]:
    relpath = image_relpath(issue)
    fullpath = os.path.join(ROOT, relpath)
    if not os.path.isfile(fullpath):
        raise FileNotFoundError(
            f"Thiếu social preview image cho #{int(issue):03d}: {relpath}"
        )
    with Image.open(fullpath) as image:
        width, height = image.size
        fmt = (image.format or "").upper()
    if fmt != "PNG":
        raise ValueError(f"Social preview image phải là PNG: {relpath} ({fmt or 'unknown'})")
    if width <= 0 or height <= 0:
        raise ValueError(f"Social preview image có kích thước không hợp lệ: {relpath}")
    return {
        "path": relpath,
        "url": urljoin(site_url.rstrip("/") + "/", relpath),
        "width": width,
        "height": height,
        "alt": f"Linux Daily #{int(issue):03d} — {title}",
        "mime": "image/png",
    }

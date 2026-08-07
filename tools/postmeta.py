#!/usr/bin/env python3
"""
postmeta.py — Đọc metadata có cấu trúc của một bài (front matter) và text hiển thị.

Mỗi bài nhúng một khối JSON tự mô tả trong <head>:

    <script type="application/json" id="ld-meta">
    {"issue": 18, "date": "2026-08-07", "axis": "Công cụ mới",
     "eyebrow": "Công cụ mới · Cloud sync", "slug": "rclone-cloud-sync",
     "title": "…", "lede": "…"}
    </script>

Nhờ khối này, build_index và validate_repo **đọc metadata có cấu trúc** thay vì bới
HTML bằng regex. read_visible() cũng dùng html.parser (không regex) để lấy text các
phần hiển thị, phục vụ kiểm tra khối meta không lệch với nội dung người đọc thấy.
"""
from __future__ import annotations

import json
from html.parser import HTMLParser

META_SCRIPT_ID = "ld-meta"
REQUIRED_FIELDS = ("issue", "date", "axis", "eyebrow", "slug", "title", "lede")


class MetaError(ValueError):
    """Khối metadata thiếu, sai vị trí, hoặc JSON không hợp lệ."""


class _MetaExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in = False
        self.raw: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == META_SCRIPT_ID:
            self._in = True
            self.raw = ""

    def handle_endtag(self, tag):
        if tag == "script":
            self._in = False

    def handle_data(self, data):
        if self._in:
            self.raw = (self.raw or "") + data


class _VisibleExtractor(HTMLParser):
    """Lấy text (đã bỏ tag con) của <span class=issue>, <p class=eyebrow>,
    <h1>, <p class=lede> — mỗi loại lấy phần tử đầu tiên."""

    def __init__(self) -> None:
        super().__init__()
        self.out: dict[str, str] = {}
        self._active: tuple[str, str] | None = None  # (key, tag)

    @staticmethod
    def _match(tag, attrs) -> str | None:
        cls = dict(attrs).get("class", "").split()
        if tag == "h1":
            return "title"
        if tag == "span" and "issue" in cls:
            return "issue"
        if tag == "p" and "eyebrow" in cls:
            return "eyebrow"
        if tag == "p" and "lede" in cls:
            return "lede"
        return None

    def handle_starttag(self, tag, attrs):
        if self._active is None:
            key = self._match(tag, attrs)
            if key and key not in self.out:
                self._active = (key, tag)
                self.out[key] = ""

    def handle_endtag(self, tag):
        if self._active and tag == self._active[1]:
            self._active = None

    def handle_data(self, data):
        if self._active:
            self.out[self._active[0]] += data


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_meta(path: str) -> dict:
    """Trả metadata (dict) từ khối <script id='ld-meta'>. Ném MetaError nếu lỗi."""
    p = _MetaExtractor()
    p.feed(_read(path))
    if not p.raw or not p.raw.strip():
        raise MetaError(f"{path}: thiếu khối <script id=\"{META_SCRIPT_ID}\"> JSON.")
    try:
        data = json.loads(p.raw)
    except json.JSONDecodeError as exc:
        raise MetaError(f"{path}: JSON trong khối meta không hợp lệ ({exc}).") from exc
    if not isinstance(data, dict):
        raise MetaError(f"{path}: khối meta phải là một object JSON.")
    return data


def read_visible(path: str) -> dict[str, str]:
    """Trả text đã strip của issue/eyebrow/title/lede để đối chiếu với meta."""
    p = _VisibleExtractor()
    p.feed(_read(path))
    return {k: v.strip() for k, v in p.out.items()}

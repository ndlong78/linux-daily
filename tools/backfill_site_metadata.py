#!/usr/bin/env python3
"""Backfill discovery/social metadata and repair small historical HTML drift.

The transformation is deterministic and idempotent: public URLs come from site.json,
post title/description come from ld-meta, social image metadata comes from the existing
post-NNN-code.png assets, legacy broken source URLs are replaced with live stable sources,
and old HTML fragments missing the common document shell are normalized back to the
shared site structure.

From Linux Daily #070 onward the same durable backfill also splits verification evidence:
``tested_on`` contains runtime-lab evidence only, while ``documentation_verified_on``
contains platforms reviewed against official/upstream documentation. The migration is
activated by state.json reaching #070, so merging the contract at #069 does not leave
main with uncommitted deterministic drift; the first #070 materialization performs the
one-time historical normalization under the existing artifact guard.
"""
from __future__ import annotations

import argparse
import difflib
import glob
import html
import json
import os
import re
import sys
from urllib.parse import urljoin

import postmeta
import socialmeta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_CONFIG = os.path.join(ROOT, "site.json")
STATE_CONFIG = os.path.join(ROOT, "state.json")
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")
VERIFICATION_SPLIT_FROM_ISSUE = 70
DOCUMENTATION_SUFFIX = " (documentation-verified)"
STYLE_META_RE = re.compile(
    r'<div class="style-meta"[^>]*>.*?</div>', re.IGNORECASE | re.DOTALL
)
LEGACY_STYLE_CONTRACT_RE = re.compile(
    r'<section class="style-contract"[^>]*>.*?</section>', re.IGNORECASE | re.DOTALL
)
TESTED_FIELD_RE = re.compile(r'"tested_on"\s*:\s*\[[^\]]*\]')
DOC_FIELD_RE = re.compile(r'"documentation_verified_on"\s*:\s*\[[^\]]*\]')

FEDORA_SUDO_URL = "https://fedoramagazine.org/howto-use-sudo/"
FEDORA_OPENSSH_URL = "https://packages.fedoraproject.org/pkgs/openssh/openssh-server/"
DEBIAN_GETENT_URL = "https://manpages.debian.org/bookworm/manpages/getent.1.en.html"

LEGACY_LINK_REPLACEMENTS = {
    "https://docs.fedoraproject.org/en-US/fedora/f30/system-administrators-guide/basic-system-configuration/Gaining_Privileges/": FEDORA_SUDO_URL,
    "https://docs.fedoraproject.org/nn/fedora/f32/system-administrators-guide/infrastructure-services/OpenSSH/": FEDORA_OPENSSH_URL,
    "https://manpages.debian.org/bookworm/libc-bin/getent.1.en.html": DEBIAN_GETENT_URL,
    "https://docs.fedoraproject.org/ko/fedora/f30/system-administrators-guide/basic-system-configuration/Gaining_Privileges/": FEDORA_SUDO_URL,
    "https://docs.fedoraproject.org/cs/fedora/f30/system-administrators-guide/infrastructure-services/OpenSSH/": FEDORA_OPENSSH_URL,
}

LEGACY_TITLE_REPLACEMENTS = {
    "Fedora Docs — Gaining Privileges": "Fedora Magazine — Configure sudo",
    "Fedora Docs — OpenSSH": "Fedora Packages — openssh-server",
}


def _load_site() -> dict:
    with open(SITE_CONFIG, encoding="utf-8") as f:
        return json.load(f)


def _verification_split_active() -> bool:
    with open(STATE_CONFIG, encoding="utf-8") as f:
        state = json.load(f)
    return int(state.get("last_issue", 0)) >= VERIFICATION_SPLIT_FROM_ISSUE


def _clean_verification_value(value: str) -> tuple[str, bool]:
    item = value.strip()
    if item.lower().endswith(DOCUMENTATION_SUFFIX):
        return item[: -len(DOCUMENTATION_SUFFIX)].strip(), True
    return item, False


def split_verification_evidence(meta: dict) -> tuple[list[str], list[str]]:
    """Return (runtime-tested, documentation-verified) without legacy sentinels."""
    runtime: list[str] = []
    documented: list[str] = []

    tested_on = meta.get("tested_on", [])
    if isinstance(tested_on, list):
        for raw in tested_on:
            if not isinstance(raw, str) or not raw.strip():
                continue
            value, was_documented = _clean_verification_value(raw)
            (documented if was_documented else runtime).append(value)

    documentation_verified_on = meta.get("documentation_verified_on", [])
    if isinstance(documentation_verified_on, list):
        for raw in documentation_verified_on:
            if not isinstance(raw, str) or not raw.strip():
                continue
            value, _ = _clean_verification_value(raw)
            documented.append(value)

    return list(dict.fromkeys(runtime)), list(dict.fromkeys(documented))


def _compact_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def normalize_verification_metadata(text: str, meta: dict, *, active: bool) -> str:
    """Migrate legacy verification metadata + visible label when the split is active."""
    if not active:
        return text

    runtime, documented = split_verification_evidence(meta)
    if not runtime and not documented:
        return text

    tested_field = f'"tested_on":{_compact_json(runtime)}'
    documented_field = f'"documentation_verified_on":{_compact_json(documented)}'

    if not TESTED_FIELD_RE.search(text):
        raise ValueError("ld-meta thiếu tested_on nên không thể migrate verification metadata")
    text = TESTED_FIELD_RE.sub(tested_field, text, count=1)

    if DOC_FIELD_RE.search(text):
        text = DOC_FIELD_RE.sub(documented_field, text, count=1)
    else:
        text = text.replace(tested_field, f"{tested_field},{documented_field}", 1)

    runtime_display = " · ".join(runtime) if runtime else "—"
    documented_display = " · ".join(documented) if documented else "—"
    last_verified = str(meta.get("last_verified", "")).strip()
    style_meta = (
        '<div class="style-meta" aria-label="Môi trường kiểm chứng">'
        f'<span><strong>Runtime tested:</strong> {html.escape(runtime_display)}</span>'
        '<span><strong>Documentation verified:</strong> '
        f'{html.escape(documented_display)}</span>'
        f'<span><strong>Last verified:</strong> {html.escape(last_verified)}</span>'
        "</div>"
    )
    if STYLE_META_RE.search(text):
        return STYLE_META_RE.sub(style_meta, text, count=1)
    if LEGACY_STYLE_CONTRACT_RE.search(text):
        return LEGACY_STYLE_CONTRACT_RE.sub(style_meta, text, count=1)
    raise ValueError("thiếu style-meta/style-contract nên không thể migrate verification label")


def _ensure_document_shell(text: str, meta: dict) -> str:
    """Repair historical fragments that have </head>/<body> but no opening document shell."""
    prefix_probe = text[:1000].lower()
    if "<html" in prefix_probe:
        return text

    issue = int(meta["issue"])
    title = html.escape(str(meta["title"]), quote=True)
    lede = html.escape(str(meta["lede"]), quote=True)
    shell = "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="vi">',
            "<head>",
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"<title>{title} — Linux Daily #{issue:03d}</title>",
            f'<meta name="description" content="{lede}">',
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&amp;family=JetBrains+Mono:wght@400;500;700&amp;family=Noto+Serif:ital,wght@0,400;0,600;1,400&amp;display=swap" rel="stylesheet">',
            '<link rel="stylesheet" href="../assets/style.css">',
        ]
    )
    return shell + "\n" + text


def _strip_discovery_lines(text: str) -> str:
    kept: list[str] = []
    for line in text.splitlines():
        if 'rel="canonical"' in line:
            continue
        if 'type="application/rss+xml"' in line:
            continue
        if 'property="og:' in line:
            continue
        if 'name="twitter:' in line:
            continue
        kept.append(line)
    return "\n".join(kept) + ("\n" if text.endswith("\n") else "")


def render_post(path: str) -> str:
    site = _load_site()
    meta = postmeta.read_meta(path)
    with open(path, encoding="utf-8") as f:
        text = f.read()

    for old, new in LEGACY_LINK_REPLACEMENTS.items():
        text = text.replace(old, new)
    for old, new in LEGACY_TITLE_REPLACEMENTS.items():
        text = text.replace(old, new)

    text = _ensure_document_shell(text, meta)
    text = normalize_verification_metadata(
        text, meta, active=_verification_split_active()
    )
    text = _strip_discovery_lines(text)
    basename = os.path.basename(path)
    canonical = urljoin(site["url"], f"posts/{basename}")
    feed_url = urljoin(site["url"], site["feed_path"])
    title = html.escape(str(meta["title"]), quote=True)
    lede = html.escape(str(meta["lede"]), quote=True)
    site_title = html.escape(str(site["title"]), quote=True)
    social = socialmeta.image_info(int(meta["issue"]), str(meta["title"]), site["url"])
    social_url = html.escape(str(social["url"]), quote=True)
    social_alt = html.escape(str(social["alt"]), quote=True)

    block = "\n".join(
        [
            f'<link rel="canonical" href="{canonical}">',
            f'<link rel="alternate" type="application/rss+xml" title="Linux Daily RSS" href="{feed_url}">',
            '<meta property="og:type" content="article">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{lede}">',
            f'<meta property="og:url" content="{canonical}">',
            f'<meta property="og:site_name" content="{site_title}">',
            '<meta property="og:locale" content="vi_VN">',
            f'<meta property="og:image" content="{social_url}">',
            f'<meta property="og:image:type" content="{social["mime"]}">',
            f'<meta property="og:image:width" content="{social["width"]}">',
            f'<meta property="og:image:height" content="{social["height"]}">',
            f'<meta property="og:image:alt" content="{social_alt}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{title}">',
            f'<meta name="twitter:description" content="{lede}">',
            f'<meta name="twitter:image" content="{social_url}">',
            f'<meta name="twitter:image:alt" content="{social_alt}">',
        ]
    )

    marker = '<script type="application/json" id="ld-meta">'
    if marker not in text:
        raise ValueError(f"{path}: thiếu ld-meta marker")
    return text.replace(marker, block + "\n" + marker, 1)


MAX_DRIFT_LINES = 6
MAX_DRIFT_WIDTH = 160


def describe_drift(current: str, expected: str, limit: int = MAX_DRIFT_LINES) -> list[str]:
    """Những dòng lệch giữa file hiện tại và bản dựng lại."""
    diff = difflib.unified_diff(
        current.splitlines(), expected.splitlines(),
        fromfile="hiện tại", tofile="mong đợi", lineterm="", n=0,
    )
    lines = [
        item for item in diff
        if item[:1] in {"+", "-"} and not item.startswith(("+++", "---"))
    ]
    shown = [
        item if len(item) <= MAX_DRIFT_WIDTH else item[:MAX_DRIFT_WIDTH] + " …"
        for item in lines[:limit]
    ]
    if len(lines) > limit:
        shown.append(f"… còn {len(lines) - limit} dòng lệch nữa")
    return shown


def run(check: bool = False) -> int:
    changed: list[tuple[str, list[str]]] = []
    for path in sorted(glob.glob(POSTS_GLOB)):
        expected = render_post(path)
        with open(path, encoding="utf-8") as f:
            current = f.read()
        if current == expected:
            continue
        drift = describe_drift(current, expected) if check else []
        changed.append((os.path.relpath(path, ROOT), drift))
        if not check:
            with open(path, "w", encoding="utf-8") as f:
                f.write(expected)

    if check and changed:
        for path, drift in changed:
            print(f"LỖI: metadata/social backfill chưa đồng bộ: {path}", file=sys.stderr)
            for line in drift:
                print(f"    {line}", file=sys.stderr)
        print(
            "  Sinh lại bằng `python tools/backfill_site_metadata.py` "
            "(hoặc `python tools/publish.py prepare`); đừng sửa tay từng dòng meta.",
            file=sys.stderr,
        )
        return 1
    print(
        f"OK: historical metadata/social backfill "
        f"{'đồng bộ' if check else 'đã cập nhật'} ({len(changed)} file thay đổi)."
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

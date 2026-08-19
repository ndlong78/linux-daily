#!/usr/bin/env python3
"""Build a deterministic fingerprint of the files Linux Daily serves publicly."""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import socialmeta

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
VERSION_PATH = ROOT / "site-version.json"

# Cloudflare AI Crawl Control chèn một khối "Cloudflare Managed content" lên
# trước /robots.txt rồi nối nguyên bản của repo phía sau. Đó là biến đổi hợp lệ
# ở edge, không phải deploy hỏng — nên file này không so được theo byte và cũng
# không được nằm trong hash tổng, nếu không hash tổng sẽ luôn lệch và che mất
# drift thật của 5 file còn lại. check_production đổi sang kiểm containment:
# nguyên bản repo phải xuất hiện nguyên vẹn trong body mà production trả về.
EDGE_MANAGED_PATHS = frozenset({"/robots.txt"})


@dataclass(frozen=True)
class FingerprintedFile:
    public_path: str
    repository_path: str
    sha256: str
    size: int


def latest_post_path() -> Path:
    posts = glob.glob(POSTS_GLOB)
    if not posts:
        raise RuntimeError("repository không có post HTML")
    return Path(max(posts, key=lambda p: int(Path(p).name.split("-")[1])))


def served_files() -> list[tuple[str, Path]]:
    latest = latest_post_path()
    issue = int(latest.name.split("-")[1])
    social_relpath = socialmeta.image_relpath(issue)
    return [
        ("/", ROOT / "index.html"),
        ("/feed.xml", ROOT / "feed.xml"),
        ("/sitemap.xml", ROOT / "sitemap.xml"),
        ("/robots.txt", ROOT / "robots.txt"),
        (f"/posts/{latest.name}", latest),
        (f"/{social_relpath}", ROOT / social_relpath),
    ]


def fingerprinted_files() -> list[tuple[str, Path]]:
    """Tập file so được theo byte — served_files() trừ đi phần edge tự viết lại."""
    return [item for item in served_files() if item[0] not in EDGE_MANAGED_PATHS]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect() -> tuple[str, list[FingerprintedFile]]:
    files: list[FingerprintedFile] = []
    aggregate = hashlib.sha256()
    for public_path, path in served_files():
        data = path.read_bytes()
        digest = sha256_bytes(data)
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        # File edge-managed vẫn nằm trong manifest để checker có bytes mà đối
        # chiếu containment, nhưng không góp vào hash tổng.
        files.append(FingerprintedFile(public_path, rel, digest, len(data)))
        if public_path in EDGE_MANAGED_PATHS:
            continue
        aggregate.update(public_path.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(data)
        aggregate.update(b"\0")
    return aggregate.hexdigest(), files


def manifest() -> dict:
    fingerprint, files = collect()
    latest = latest_post_path()
    return {
        "schema": 1,
        "fingerprint": fingerprint,
        "latest_issue": int(latest.name.split("-")[1]),
        "files": [asdict(item) for item in files],
    }


def render_manifest() -> str:
    return json.dumps(manifest(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable manifest.")
    args = parser.parse_args(argv)
    data = manifest()
    if args.json:
        print(render_manifest(), end="")
    else:
        print(f"site fingerprint: {data['fingerprint']}")
        for item in data["files"]:
            print(f"{item['sha256']}  {item['public_path']}  ({item['size']} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

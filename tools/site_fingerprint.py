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

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
VERSION_PATH = ROOT / "site-version.json"


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
    return [
        ("/", ROOT / "index.html"),
        ("/feed.xml", ROOT / "feed.xml"),
        ("/sitemap.xml", ROOT / "sitemap.xml"),
        ("/robots.txt", ROOT / "robots.txt"),
        (f"/posts/{latest.name}", latest),
        (f"/posts/social/post-{issue:03d}-code.png", ROOT / "posts" / "social" / f"post-{issue:03d}-code.png"),
    ]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect() -> tuple[str, list[FingerprintedFile]]:
    files: list[FingerprintedFile] = []
    aggregate = hashlib.sha256()
    for public_path, path in served_files():
        data = path.read_bytes()
        digest = sha256_bytes(data)
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        files.append(FingerprintedFile(public_path, rel, digest, len(data)))
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

#!/usr/bin/env python3
"""Validate and report Linux Daily taxonomy derived from post ld-meta."""
from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from pathlib import Path

import postmeta

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
TAXONOMY_PATH = ROOT / "taxonomy.json"


def load_taxonomy(path: Path = TAXONOMY_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1 or not isinstance(data.get("axes"), dict):
        raise ValueError("taxonomy.json phải có schema=1 và object axes")
    return data


def collect() -> tuple[list[str], Counter[str], Counter[str]]:
    taxonomy = load_taxonomy()
    allowed = taxonomy["axes"]
    errors: list[str] = []
    axes: Counter[str] = Counter()
    tags: Counter[str] = Counter()
    seen_issues: set[int] = set()

    for raw in glob.glob(POSTS_GLOB):
        path = Path(raw)
        meta = postmeta.read_meta(str(path))
        issue = int(meta["issue"])
        axis = str(meta.get("axis", "")).strip()
        eyebrow = str(meta.get("eyebrow", "")).strip()
        if issue in seen_issues:
            errors.append(f"duplicate issue #{issue:03d}")
        seen_issues.add(issue)
        if axis not in allowed:
            errors.append(f"{path.name}: axis {axis!r} không có trong taxonomy.json")
        else:
            axes[axis] += 1
        if not eyebrow:
            errors.append(f"{path.name}: thiếu eyebrow để derive tag")
            continue
        parts = [part.strip() for part in eyebrow.split("·") if part.strip()]
        for tag in parts[1:]:
            tags[tag] += 1

    if not seen_issues:
        errors.append("repository không có post HTML")
    return errors, axes, tags


def report() -> str:
    taxonomy = load_taxonomy()
    errors, axes, tags = collect()
    lines = ["Linux Daily — Taxonomy & Topic Discovery", ""]
    for key, cfg in taxonomy["axes"].items():
        lines.append(f"- {cfg['label']}: {axes.get(key, 0)} bài (`{cfg['slug']}`)")
    if tags:
        lines.extend(["", "Secondary tags:"])
        for tag, count in sorted(tags.items(), key=lambda item: (-item[1], item[0].casefold())):
            lines.append(f"- {tag}: {count}")
    if errors:
        lines.extend(["", "Errors:", *[f"- {error}" for error in errors]])
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Xuất counts ở dạng JSON.")
    args = parser.parse_args(argv)
    errors, axes, tags = collect()
    if args.json:
        print(json.dumps({"axes": dict(sorted(axes.items())), "tags": dict(sorted(tags.items())), "errors": errors}, ensure_ascii=False, indent=2))
    else:
        print(report(), end="")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

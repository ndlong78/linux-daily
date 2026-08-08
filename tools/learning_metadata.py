#!/usr/bin/env python3
"""Validate normalized difficulty and prerequisite metadata for Linux Daily."""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postmeta  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
CONFIG_PATH = ROOT / "learning-metadata.json"
DIFFICULTY_LABELS = {
    "basic": "Cơ bản",
    "intermediate": "Trung cấp",
    "advanced": "Nâng cao",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_posts() -> dict[int, dict]:
    posts: dict[int, dict] = {}
    for raw_path in glob.glob(POSTS_GLOB):
        path = Path(raw_path)
        meta = postmeta.read_meta(str(path))
        issue = int(meta["issue"])
        posts[issue] = {
            "issue": issue,
            "title": str(meta["title"]).strip(),
            "href": f"posts/{path.name}",
        }
    return dict(sorted(posts.items()))


def _find_cycle(graph: dict[int, list[int]]) -> list[int]:
    visiting: set[int] = set()
    visited: set[int] = set()
    stack: list[int] = []

    def visit(node: int) -> list[int]:
        if node in visiting:
            start = stack.index(node)
            return [*stack[start:], node]
        if node in visited:
            return []
        visiting.add(node)
        stack.append(node)
        for dependency in graph.get(node, []):
            cycle = visit(dependency)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return []

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return []


def review(config: dict | None = None, posts: dict[int, dict] | None = None) -> dict:
    config = config if config is not None else _load_json(CONFIG_PATH)
    posts = posts if posts is not None else collect_posts()
    errors: list[str] = []

    if config.get("version") != 1:
        errors.append("learning-metadata.json: version phải là 1")

    raw_entries = config.get("posts")
    if not isinstance(raw_entries, list) or not raw_entries:
        return {
            "metadata": {},
            "posts": posts,
            "difficulty_counts": {},
            "prerequisite_edges": 0,
            "root_issues": sorted(posts),
            "errors": [*errors, "learning-metadata.json: posts phải là array không rỗng"],
        }

    metadata: dict[int, dict] = {}
    for index, raw_entry in enumerate(raw_entries, start=1):
        label = f"posts[{index}]"
        if not isinstance(raw_entry, dict):
            errors.append(f"{label}: phải là object")
            continue

        issue = raw_entry.get("issue")
        difficulty = raw_entry.get("difficulty")
        prerequisites = raw_entry.get("prerequisites")

        if not isinstance(issue, int) or issue <= 0:
            errors.append(f"{label}.issue phải là số dương")
            continue
        if issue in metadata:
            errors.append(f"{label}: issue #{issue:03d} bị khai báo trùng")
            continue
        if issue not in posts:
            errors.append(f"{label}: issue không tồn tại #{issue:03d}")

        if difficulty not in DIFFICULTY_LABELS:
            errors.append(
                f"{label}.difficulty phải thuộc {', '.join(DIFFICULTY_LABELS)}, đang là {difficulty!r}"
            )

        if not isinstance(prerequisites, list):
            errors.append(f"{label}.prerequisites phải là array")
            prerequisites = []

        seen_prerequisites: set[int] = set()
        clean_prerequisites: list[int] = []
        for position, prerequisite in enumerate(prerequisites, start=1):
            if not isinstance(prerequisite, int) or prerequisite <= 0:
                errors.append(f"{label}.prerequisites[{position}] phải là issue number dương")
                continue
            if prerequisite == issue:
                errors.append(f"{label}: issue #{issue:03d} không thể phụ thuộc chính nó")
                continue
            if prerequisite in seen_prerequisites:
                errors.append(f"{label}: prerequisite #{prerequisite:03d} bị lặp")
                continue
            seen_prerequisites.add(prerequisite)
            clean_prerequisites.append(prerequisite)
            if prerequisite not in posts:
                errors.append(
                    f"{label}: prerequisite tham chiếu issue không tồn tại #{prerequisite:03d}"
                )

        metadata[issue] = {
            "issue": issue,
            "difficulty": difficulty,
            "difficulty_label": DIFFICULTY_LABELS.get(str(difficulty), "Không hợp lệ"),
            "prerequisites": clean_prerequisites,
        }

    missing = sorted(set(posts) - set(metadata))
    if missing:
        errors.append(
            "learning metadata chưa phủ mọi bài: "
            + ", ".join(f"#{issue:03d}" for issue in missing)
        )

    graph = {
        issue: [dependency for dependency in item["prerequisites"] if dependency in posts]
        for issue, item in metadata.items()
        if issue in posts
    }
    cycle = _find_cycle(graph)
    if cycle:
        errors.append(
            "prerequisite graph có cycle: "
            + " -> ".join(f"#{issue:03d}" for issue in cycle)
        )

    difficulty_counts = Counter(
        item["difficulty"] for issue, item in metadata.items()
        if issue in posts and item["difficulty"] in DIFFICULTY_LABELS
    )
    roots = sorted(issue for issue, dependencies in graph.items() if not dependencies)
    edges = sum(len(dependencies) for dependencies in graph.values())

    return {
        "metadata": dict(sorted(metadata.items())),
        "posts": posts,
        "difficulty_counts": dict(difficulty_counts),
        "prerequisite_edges": edges,
        "root_issues": roots,
        "errors": errors,
    }


def structured(result: dict) -> dict:
    entries = []
    for issue, item in result["metadata"].items():
        post = result["posts"].get(issue, {})
        entries.append(
            {
                **item,
                "title": post.get("title", ""),
                "href": post.get("href", ""),
            }
        )
    return {
        "post_count": len(result["posts"]),
        "metadata_count": len(result["metadata"]),
        "difficulty_counts": result["difficulty_counts"],
        "prerequisite_edges": result["prerequisite_edges"],
        "root_issues": result["root_issues"],
        "posts": entries,
        "errors": result["errors"],
    }


def run(*, json_output: bool = False) -> int:
    result = review()
    if json_output:
        print(json.dumps(structured(result), ensure_ascii=False, indent=2))
    else:
        counts = result["difficulty_counts"]
        print(
            "Learning metadata: "
            f"posts={len(result['posts'])}, "
            f"basic={counts.get('basic', 0)}, "
            f"intermediate={counts.get('intermediate', 0)}, "
            f"advanced={counts.get('advanced', 0)}, "
            f"prerequisite_edges={result['prerequisite_edges']}."
        )
        for problem in result["errors"]:
            print(f"LỖI: {problem}", file=sys.stderr)
    return 1 if result["errors"] else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Xuất structured learning metadata.")
    args = parser.parse_args(argv)
    return run(json_output=args.json)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build and validate goal-oriented Linux Daily learning paths."""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

from jinja2 import Environment, FileSystemLoader, select_autoescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postmeta  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
CONFIG_PATH = ROOT / "learning-paths.json"
SITE_CONFIG = ROOT / "site.json"
TEMPLATES_DIR = ROOT / "templates"
TEMPLATE_NAME = "learning-paths.template.html"
OUTPUT_PATH = ROOT / "learning-paths.html"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MIN_STEPS = 3


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


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
            "date": str(meta["date"]),
            "axis": str(meta["axis"]).strip(),
            "eyebrow": str(meta["eyebrow"]).strip(),
            "href": f"posts/{path.name}",
        }
    return dict(sorted(posts.items()))


def review(config: dict | None = None, posts: dict[int, dict] | None = None) -> dict:
    config = config if config is not None else _load_json(CONFIG_PATH)
    posts = posts if posts is not None else collect_posts()
    errors: list[str] = []

    if config.get("version") != 1:
        errors.append("learning-paths.json: version phải là 1")

    raw_paths = config.get("paths")
    if not isinstance(raw_paths, list) or not raw_paths:
        return {
            "paths": [],
            "posts": posts,
            "assigned_issues": set(),
            "unassigned_issues": sorted(posts),
            "assignment_counts": {},
            "errors": [*errors, "learning-paths.json: paths phải là array không rỗng"],
        }

    seen_slugs: set[str] = set()
    enriched_paths: list[dict] = []
    assignments: Counter[int] = Counter()

    for index, raw_path in enumerate(raw_paths, start=1):
        label = f"paths[{index}]"
        if not isinstance(raw_path, dict):
            errors.append(f"{label}: phải là object")
            continue

        slug = raw_path.get("slug")
        title = raw_path.get("title")
        goal = raw_path.get("goal")
        audience = raw_path.get("audience")
        steps = raw_path.get("steps")

        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            errors.append(f"{label}.slug phải là kebab-case, đang là {slug!r}")
            slug = f"invalid-{index}"
        if slug in seen_slugs:
            errors.append(f"{label}.slug bị trùng: {slug}")
        seen_slugs.add(slug)

        for key, value in (("title", title), ("goal", goal), ("audience", audience)):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}.{key} phải là chuỗi không rỗng")

        if not isinstance(steps, list) or len(steps) < MIN_STEPS:
            errors.append(f"{label}.steps cần ít nhất {MIN_STEPS} issue")
            steps = steps if isinstance(steps, list) else []

        seen_steps: set[int] = set()
        resolved_steps: list[dict] = []
        for position, raw_issue in enumerate(steps, start=1):
            if not isinstance(raw_issue, int) or raw_issue <= 0:
                errors.append(f"{label}.steps[{position}] phải là issue number dương")
                continue
            if raw_issue in seen_steps:
                errors.append(f"{label}: issue #{raw_issue:03d} bị lặp trong cùng path")
                continue
            seen_steps.add(raw_issue)
            post = posts.get(raw_issue)
            if post is None:
                errors.append(f"{label}: tham chiếu issue không tồn tại #{raw_issue:03d}")
                continue
            assignments[raw_issue] += 1
            resolved_steps.append({**post, "position": position})

        enriched_paths.append(
            {
                "slug": slug,
                "title": title.strip() if isinstance(title, str) else "",
                "goal": goal.strip() if isinstance(goal, str) else "",
                "audience": audience.strip() if isinstance(audience, str) else "",
                "steps": resolved_steps,
            }
        )

    unassigned = sorted(set(posts) - set(assignments))
    if unassigned:
        errors.append(
            "learning paths chưa phủ mọi bài: "
            + ", ".join(f"#{issue:03d}" for issue in unassigned)
        )

    return {
        "paths": enriched_paths,
        "posts": posts,
        "assigned_issues": set(assignments),
        "unassigned_issues": unassigned,
        "assignment_counts": dict(assignments),
        "errors": errors,
    }


def render_page(result: dict | None = None) -> str:
    result = result if result is not None else review()
    if result["errors"]:
        raise ValueError("không thể render learning paths khi config không hợp lệ")
    site = _load_json(SITE_CONFIG)
    base_url = str(site["url"]).rstrip("/") + "/"
    return _env().get_template(TEMPLATE_NAME).render(
        paths=result["paths"],
        path_count=len(result["paths"]),
        post_count=len(result["posts"]),
        canonical_url=urljoin(base_url, "learning-paths.html"),
        site_title=str(site["title"]),
    )


def structured(result: dict) -> dict:
    return {
        "paths": result["paths"],
        "path_count": len(result["paths"]),
        "post_count": len(result["posts"]),
        "assigned_post_count": len(result["assigned_issues"]),
        "unassigned_issues": result["unassigned_issues"],
        "assignment_counts": result["assignment_counts"],
        "errors": result["errors"],
    }


def run(*, check: bool, json_output: bool = False) -> int:
    result = review()
    if result["errors"]:
        print(f"LỖI: learning paths có {len(result['errors'])} vấn đề")
        for problem in result["errors"]:
            print(f"- {problem}")
        return 1

    if json_output:
        print(json.dumps(structured(result), ensure_ascii=False, indent=2))
        return 0

    expected = render_page(result)
    if check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != expected:
            print(
                "LỖI: learning-paths.html chưa đồng bộ. "
                "Chạy `python3 tools/learning_paths.py`."
            )
            return 1
        print(
            "OK: learning paths đồng bộ; "
            f"paths={len(result['paths'])}, covered={len(result['assigned_issues'])}/{len(result['posts'])}."
        )
        return 0

    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(
        "Đã cập nhật learning-paths.html; "
        f"paths={len(result['paths'])}, covered={len(result['assigned_issues'])}/{len(result['posts'])}."
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail nếu public learning-path page bị drift.")
    parser.add_argument("--json", action="store_true", help="Xuất structured learning-path inventory.")
    args = parser.parse_args(argv)
    return run(check=args.check, json_output=args.json)


if __name__ == "__main__":
    raise SystemExit(main())

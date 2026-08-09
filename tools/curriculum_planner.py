#!/usr/bin/env python3
"""Validate and inspect the deterministic Linux Daily curriculum queue."""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

import postmeta
import taxonomy

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "curriculum-plan.json"
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
DIFFICULTIES = {"basic", "intermediate", "advanced"}
TOKEN_RE = re.compile(r"[a-z0-9À-ỹ]+", re.IGNORECASE)


def load_plan() -> dict:
    data = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("topics"), list):
        raise ValueError("curriculum-plan.json phải có version=1 và topics là list")
    return data


def published() -> list[dict]:
    items = []
    for raw in glob.glob(POSTS_GLOB):
        meta = postmeta.read_meta(raw)
        items.append({"issue": int(meta["issue"]), "axis": str(meta["axis"]), "title": str(meta["title"])})
    return sorted(items, key=lambda item: item["issue"])


def normalized(value: str) -> str:
    return " ".join(TOKEN_RE.findall(value.casefold()))


def validate(plan: dict | None = None, posts: list[dict] | None = None) -> list[str]:
    plan = plan if plan is not None else load_plan()
    posts = posts if posts is not None else published()
    axes = list(taxonomy.load_taxonomy()["axes"])
    topics = plan["topics"]
    errors: list[str] = []

    horizon = plan.get("policy", {}).get("planning_horizon_days")
    if not isinstance(horizon, int) or horizon < 7:
        errors.append("planning_horizon_days phải là integer >= 7")
    if horizon != len(topics):
        errors.append(f"planning_horizon_days={horizon} nhưng queue có {len(topics)} topic")

    expected_start = len(posts) % len(axes) if axes else 0
    seen: set[str] = set()
    published_titles = {normalized(item["title"]) for item in posts}
    for index, item in enumerate(topics):
        prefix = f"topics[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} phải là object")
            continue
        axis = item.get("axis")
        topic = str(item.get("topic", "")).strip()
        difficulty = item.get("difficulty")
        goal = str(item.get("goal", "")).strip()
        expected_axis = axes[(expected_start + index) % len(axes)] if axes else None
        if axis not in axes:
            errors.append(f"{prefix}.axis không hợp lệ: {axis!r}")
        elif axis != expected_axis:
            errors.append(f"{prefix}.axis expected {expected_axis!r}, found {axis!r}")
        if difficulty not in DIFFICULTIES:
            errors.append(f"{prefix}.difficulty không hợp lệ: {difficulty!r}")
        if len(topic) < 12:
            errors.append(f"{prefix}.topic quá ngắn")
        if len(goal) < 20:
            errors.append(f"{prefix}.goal quá ngắn")
        key = normalized(topic)
        if key in seen:
            errors.append(f"{prefix}.topic trùng trong queue: {topic!r}")
        seen.add(key)
        if key in published_titles:
            errors.append(f"{prefix}.topic trùng title đã publish: {topic!r}")
    return errors


def snapshot(plan: dict | None = None, posts: list[dict] | None = None) -> dict:
    plan = plan if plan is not None else load_plan()
    posts = posts if posts is not None else published()
    next_issue = posts[-1]["issue"] + 1 if posts else 1
    topics = []
    for offset, item in enumerate(plan["topics"]):
        topics.append({"issue": next_issue + offset, **item})
    return {"published": len(posts), "next_issue": next_issue, "horizon": len(topics), "topics": topics}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Xuất queue đã resolve issue number dưới dạng JSON.")
    args = parser.parse_args(argv)
    try:
        plan = load_plan()
        posts = published()
        problems = validate(plan, posts)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"LỖI: {exc}")
        return 1
    if problems:
        print(f"LỖI: curriculum planner có {len(problems)} vấn đề")
        for problem in problems:
            print(f"- {problem}")
        return 1
    result = snapshot(plan, posts)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        first = result["topics"][0]
        print(f"OK: {result['horizon']} topic đã plan; next=#{first['issue']:03d} {first['axis']} — {first['topic']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

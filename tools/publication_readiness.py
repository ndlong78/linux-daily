#!/usr/bin/env python3
"""Validate whether planned Linux Daily topics are ready for authoring."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import curriculum_planner

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PLATFORMS = {"ubuntu", "debian", "fedora", "freebsd"}


def token_set(value: str) -> set[str]:
    return set(curriculum_planner.normalized(value).split())


def similarity(left: str, right: str) -> float:
    a, b = token_set(left), token_set(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def validate(plan: dict | None = None, posts: list[dict] | None = None) -> list[str]:
    plan = plan if plan is not None else curriculum_planner.load_plan()
    posts = posts if posts is not None else curriculum_planner.published()
    problems = curriculum_planner.validate(plan, posts)
    if problems:
        return [f"planner: {problem}" for problem in problems]

    policy = plan.get("policy", {}).get("readiness", {})
    required_platforms = set(policy.get("required_platforms", []))
    minimum_sources = policy.get("minimum_primary_sources")
    threshold = policy.get("semantic_similarity_block_threshold")
    if required_platforms != REQUIRED_PLATFORMS:
        problems.append("readiness.required_platforms phải gồm đúng ubuntu/debian/fedora/freebsd")
    if not isinstance(minimum_sources, int) or minimum_sources < 2:
        problems.append("readiness.minimum_primary_sources phải >= 2")
    if not isinstance(threshold, int | float) or not 0.5 <= float(threshold) <= 0.95:
        problems.append("semantic_similarity_block_threshold phải nằm trong [0.5, 0.95]")
        threshold = 0.72

    published_ids = {int(item["issue"]) for item in posts}
    for index, item in enumerate(plan["topics"]):
        prefix = f"topics[{index}]"
        prereqs = item.get("prerequisites")
        if not isinstance(prereqs, list) or any(not isinstance(value, int) for value in prereqs):
            problems.append(f"{prefix}.prerequisites phải là list issue ID integer")
            continue
        if len(prereqs) != len(set(prereqs)):
            problems.append(f"{prefix}.prerequisites bị trùng")
        unknown = sorted(set(prereqs) - published_ids)
        if unknown:
            problems.append(f"{prefix}.prerequisites chưa publish: {unknown}")
        if item.get("difficulty") == "advanced" and not prereqs:
            problems.append(f"{prefix} advanced topic phải có prerequisite")

        topic = str(item.get("topic", ""))
        for published in posts:
            score = similarity(topic, str(published["title"]))
            if score >= float(threshold):
                problems.append(
                    f"{prefix}.topic quá giống bài #{int(published['issue']):03d} "
                    f"(similarity={score:.2f} >= {float(threshold):.2f})"
                )
    return problems


def report(plan: dict | None = None, posts: list[dict] | None = None) -> dict:
    plan = plan if plan is not None else curriculum_planner.load_plan()
    posts = posts if posts is not None else curriculum_planner.published()
    snapshot = curriculum_planner.snapshot(plan, posts)
    policy = plan["policy"]["readiness"]
    return {
        "ready": not validate(plan, posts),
        "next_issue": snapshot["next_issue"],
        "next_topic": snapshot["topics"][0],
        "required_platforms": policy["required_platforms"],
        "minimum_primary_sources": policy["minimum_primary_sources"],
        "semantic_similarity_block_threshold": policy["semantic_similarity_block_threshold"],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan = curriculum_planner.load_plan()
        posts = curriculum_planner.published()
        problems = validate(plan, posts)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"LỖI: {exc}")
        return 1
    if problems:
        print(f"LỖI: publication readiness có {len(problems)} vấn đề")
        for problem in problems:
            print(f"- {problem}")
        return 1
    result = report(plan, posts)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        topic = result["next_topic"]
        print(
            f"OK: #{result['next_issue']:03d} ready — {topic['topic']}; "
            f"platforms=4, primary_sources>={result['minimum_primary_sources']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

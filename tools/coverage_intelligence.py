#!/usr/bin/env python3
"""Derive explainable curriculum gaps without mutating the planning queue."""
from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from pathlib import Path

import curriculum_planner
import postmeta
import taxonomy

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "coverage-catalog.json"
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
DIFFICULTY_ORDER = {"basic": 0, "intermediate": 1, "advanced": 2}


def load_catalog() -> dict:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("capabilities"), list):
        raise ValueError("coverage-catalog.json phải có version=1 và capabilities là list")
    return data


def corpus() -> list[dict]:
    items = []
    for raw in glob.glob(POSTS_GLOB):
        meta = postmeta.read_meta(raw)
        items.append(
            {
                "issue": int(meta["issue"]),
                "axis": str(meta["axis"]),
                "title": str(meta["title"]),
                "lede": str(meta["lede"]),
            }
        )
    return sorted(items, key=lambda item: item["issue"])


def validate(catalog: dict | None = None) -> list[str]:
    catalog = catalog if catalog is not None else load_catalog()
    axes = set(taxonomy.load_taxonomy()["axes"])
    policy = catalog.get("policy", {})
    minimum_hits = policy.get("minimum_keyword_hits")
    limit = policy.get("recommendation_limit")
    errors: list[str] = []
    if not isinstance(minimum_hits, int) or minimum_hits < 1:
        errors.append("policy.minimum_keyword_hits phải là integer >= 1")
    if not isinstance(limit, int) or limit < 1:
        errors.append("policy.recommendation_limit phải là integer >= 1")

    seen: set[str] = set()
    for index, item in enumerate(catalog["capabilities"]):
        prefix = f"capabilities[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} phải là object")
            continue
        capability_id = str(item.get("id", "")).strip()
        if not capability_id or capability_id in seen:
            errors.append(f"{prefix}.id thiếu hoặc trùng: {capability_id!r}")
        seen.add(capability_id)
        if item.get("axis") not in axes:
            errors.append(f"{prefix}.axis không hợp lệ: {item.get('axis')!r}")
        if item.get("difficulty") not in DIFFICULTY_ORDER:
            errors.append(f"{prefix}.difficulty không hợp lệ")
        keywords = item.get("keywords")
        if not isinstance(keywords, list) or len(keywords) < 2 or any(not str(value).strip() for value in keywords):
            errors.append(f"{prefix}.keywords phải có ít nhất 2 keyword")
        elif isinstance(minimum_hits, int) and minimum_hits > len(keywords):
            errors.append(f"{prefix}.keywords ít hơn minimum_keyword_hits")
        if len(str(item.get("rationale", "")).strip()) < 20:
            errors.append(f"{prefix}.rationale quá ngắn")
    return errors


def _tokens(value: str) -> set[str]:
    return set(curriculum_planner.normalized(value).split())


def analyze(
    catalog: dict | None = None,
    posts: list[dict] | None = None,
    plan: dict | None = None,
) -> dict:
    catalog = catalog if catalog is not None else load_catalog()
    posts = posts if posts is not None else corpus()
    plan = plan if plan is not None else curriculum_planner.load_plan()
    problems = validate(catalog)
    if problems:
        raise ValueError("; ".join(problems))

    minimum_hits = int(catalog["policy"]["minimum_keyword_hits"])
    limit = int(catalog["policy"]["recommendation_limit"])
    axis_counts = Counter(item["axis"] for item in posts)
    planned_text = " ".join(str(item.get("topic", "")) for item in plan.get("topics", []))
    planned_tokens = _tokens(planned_text)

    capabilities = []
    for item in catalog["capabilities"]:
        evidence_tokens: set[str] = set()
        evidence_issues = []
        for post in posts:
            if post["axis"] != item["axis"]:
                continue
            post_tokens = _tokens(f"{post['title']} {post['lede']}")
            hits = sorted(set(item["keywords"]) & post_tokens)
            if hits:
                evidence_tokens.update(hits)
                evidence_issues.append(post["issue"])
        keyword_hits = sorted(evidence_tokens)
        covered = len(keyword_hits) >= minimum_hits
        planned_hits = sorted(set(item["keywords"]) & planned_tokens)
        planned = len(planned_hits) >= minimum_hits
        capabilities.append(
            {
                **item,
                "covered": covered,
                "planned": planned,
                "matched_keywords": keyword_hits,
                "planned_keywords": planned_hits,
                "evidence_issues": sorted(set(evidence_issues)),
                "axis_post_count": axis_counts[item["axis"]],
            }
        )

    gaps = [item for item in capabilities if not item["covered"] and not item["planned"]]
    gaps.sort(
        key=lambda item: (
            item["axis_post_count"],
            DIFFICULTY_ORDER[item["difficulty"]],
            item["id"],
        )
    )
    recommendations = [
        {
            "id": item["id"],
            "axis": item["axis"],
            "topic": item["topic"],
            "difficulty": item["difficulty"],
            "reason": (
                f"gap: {len(item['matched_keywords'])}/{minimum_hits} keyword evidence; "
                f"axis hiện có {item['axis_post_count']} bài; {item['rationale']}"
            ),
        }
        for item in gaps[:limit]
    ]
    return {
        "posts": len(posts),
        "capabilities": len(capabilities),
        "covered": sum(1 for item in capabilities if item["covered"]),
        "planned": sum(1 for item in capabilities if item["planned"] and not item["covered"]),
        "gaps": len(gaps),
        "axis_counts": dict(sorted(axis_counts.items())),
        "recommendations": recommendations,
        "details": capabilities,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Xuất full explainable coverage report.")
    parser.add_argument("--check", action="store_true", help="Validate catalog và chạy derivation read-only.")
    args = parser.parse_args(argv)
    try:
        result = analyze()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"LỖI: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"OK: coverage intelligence; capabilities={result['capabilities']}, "
            f"covered={result['covered']}, planned={result['planned']}, gaps={result['gaps']}."
        )
        for item in result["recommendations"]:
            print(f"- {item['axis']}: {item['topic']} — {item['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

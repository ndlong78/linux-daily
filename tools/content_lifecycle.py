#!/usr/bin/env python3
"""Validate replacement lineage and derive canonical guidance for Linux Daily."""
from __future__ import annotations

import argparse
import json
from datetime import date

import content_freshness

TERMINAL_GUIDANCE_STATES = {"current", "review-due"}


def analyze(
    *,
    as_of: date | None = None,
    posts: list[dict] | None = None,
    policy: dict | None = None,
) -> dict:
    freshness = content_freshness.review(as_of=as_of, posts=posts, policy=policy)
    problems = list(freshness["errors"])
    items = freshness["posts"]
    by_issue = {int(item["issue"]): item for item in items}
    lineages: list[dict] = []

    for item in items:
        replacement = item.get("replacement_issue")
        if replacement is None:
            continue

        source = int(item["issue"])
        chain = [source]
        seen = {source}
        cursor = source
        while True:
            current = by_issue.get(cursor)
            if current is None:
                problems.append(f"#{source:03d}: replacement chain mất issue #{cursor:03d}")
                break
            target = current.get("replacement_issue")
            if target is None:
                terminal = current
                if terminal["state"] not in TERMINAL_GUIDANCE_STATES:
                    problems.append(
                        f"#{source:03d}: replacement chain kết thúc ở #{cursor:03d} "
                        f"với state={terminal['state']!r}, không phải canonical guidance"
                    )
                lineages.append(
                    {
                        "source_issue": source,
                        "chain": chain,
                        "canonical_issue": cursor,
                        "canonical_state": terminal["state"],
                    }
                )
                break
            target = int(target)
            if target in seen:
                chain.append(target)
                problems.append(
                    f"#{source:03d}: replacement cycle phát hiện: "
                    + " -> ".join(f"#{value:03d}" for value in chain)
                )
                break
            seen.add(target)
            chain.append(target)
            cursor = target

    canonical_sources = {item["canonical_issue"] for item in lineages}
    return {
        "as_of": freshness["as_of"],
        "posts": freshness["total"],
        "current": freshness["counts"].get("current", 0),
        "review_due": freshness["counts"].get("review-due", 0),
        "historically_valid": freshness["counts"].get("historically-valid", 0),
        "superseded": freshness["counts"].get("superseded", 0),
        "replacement_lineages": lineages,
        "canonical_replacement_targets": sorted(canonical_sources),
        "errors": problems,
    }


def render_text(result: dict) -> str:
    lines = [
        "Linux Daily — Long-term Content Lifecycle",
        "=" * 41,
        f"as_of                         {result['as_of']}",
        f"posts                         {result['posts']}",
        f"current                       {result['current']}",
        f"review_due                    {result['review_due']}",
        f"historically_valid            {result['historically_valid']}",
        f"superseded                    {result['superseded']}",
        f"replacement_lineages          {len(result['replacement_lineages'])}",
        f"canonical_replacement_targets {len(result['canonical_replacement_targets'])}",
    ]
    if result["replacement_lineages"]:
        lines.extend(["", "Replacement lineage:"])
        for item in result["replacement_lineages"]:
            chain = " -> ".join(f"#{value:03d}" for value in item["chain"])
            lines.append(f"- {chain} ({item['canonical_state']})")
    return "\n".join(lines)


def run(*, as_of: date | None = None, json_output: bool = False) -> int:
    result = analyze(as_of=as_of)
    if result["errors"]:
        print(f"LỖI: content lifecycle có {len(result['errors'])} vấn đề")
        for problem in result["errors"]:
            print(f"- {problem}")
        return 1
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", help="Ngày đánh giá YYYY-MM-DD; mặc định là ngày chạy.")
    parser.add_argument("--json", action="store_true", help="Xuất replacement lineage dạng JSON.")
    args = parser.parse_args(argv)
    as_of = None
    if args.as_of:
        try:
            as_of = date.fromisoformat(args.as_of)
        except ValueError:
            parser.error("--as-of phải là YYYY-MM-DD hợp lệ")
    return run(as_of=as_of, json_output=args.json)


if __name__ == "__main__":
    raise SystemExit(main())

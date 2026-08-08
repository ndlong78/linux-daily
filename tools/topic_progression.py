#!/usr/bin/env python3
"""Analyze learning-path ordering, prerequisite placement, and difficulty progression."""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import learning_metadata  # noqa: E402
import learning_paths  # noqa: E402

DIFFICULTY_ORDER = ("basic", "intermediate", "advanced")
DIFFICULTY_RANK = {name: index for index, name in enumerate(DIFFICULTY_ORDER)}


def _finding(
    *,
    code: str,
    path_slug: str,
    path_title: str,
    issue: int,
    message: str,
) -> dict:
    return {
        "code": code,
        "path": path_slug,
        "path_title": path_title,
        "issue": issue,
        "message": message,
    }


def review(path_result: dict | None = None) -> dict:
    paths_result = path_result if path_result is not None else learning_paths.review()
    upstream_errors = list(paths_result.get("errors", []))
    hard_findings: list[dict] = []
    external_prerequisites: list[dict] = []
    path_summaries: list[dict] = []
    total_prerequisite_references = 0
    local_prerequisite_references = 0

    for path in paths_result.get("paths", []):
        steps = path.get("steps", [])
        positions = {int(step["issue"]): int(step["position"]) for step in steps}
        ordering_violations = 0
        difficulty_jumps = 0
        external_count = 0
        local_count = 0

        previous: dict | None = None
        for step in steps:
            issue = int(step["issue"])
            position = int(step["position"])
            prerequisites = step.get("prerequisites", [])

            for prerequisite in prerequisites:
                prerequisite_issue = int(prerequisite["issue"])
                total_prerequisite_references += 1
                prerequisite_position = positions.get(prerequisite_issue)
                if prerequisite_position is None:
                    external_count += 1
                    external_prerequisites.append(
                        {
                            "path": path["slug"],
                            "path_title": path["title"],
                            "issue": issue,
                            "prerequisite": prerequisite_issue,
                            "message": (
                                f"#{issue:03d} cần #{prerequisite_issue:03d}, "
                                "nhưng prerequisite nằm ngoài learning path này"
                            ),
                        }
                    )
                    continue

                local_count += 1
                local_prerequisite_references += 1
                if prerequisite_position > position:
                    ordering_violations += 1
                    hard_findings.append(
                        _finding(
                            code="prerequisite-after-dependent",
                            path_slug=path["slug"],
                            path_title=path["title"],
                            issue=issue,
                            message=(
                                f"#{issue:03d} đứng ở bước {position} nhưng prerequisite "
                                f"#{prerequisite_issue:03d} chỉ xuất hiện ở bước {prerequisite_position}"
                            ),
                        )
                    )

            if previous is not None:
                previous_difficulty = str(previous.get("difficulty", ""))
                current_difficulty = str(step.get("difficulty", ""))
                previous_rank = DIFFICULTY_RANK.get(previous_difficulty)
                current_rank = DIFFICULTY_RANK.get(current_difficulty)
                if (
                    previous_rank is not None
                    and current_rank is not None
                    and current_rank - previous_rank > 1
                ):
                    difficulty_jumps += 1
                    hard_findings.append(
                        _finding(
                            code="difficulty-jump",
                            path_slug=path["slug"],
                            path_title=path["title"],
                            issue=issue,
                            message=(
                                f"bước {int(previous['position'])} #{int(previous['issue']):03d} "
                                f"({previous_difficulty}) -> bước {position} #{issue:03d} "
                                f"({current_difficulty}) nhảy quá một bậc"
                            ),
                        )
                    )
            previous = step

        difficulties = [
            str(step.get("difficulty", ""))
            for step in steps
            if str(step.get("difficulty", "")) in DIFFICULTY_RANK
        ]
        maximum_difficulty = (
            max(difficulties, key=lambda value: DIFFICULTY_RANK[value])
            if difficulties
            else ""
        )
        path_summaries.append(
            {
                "slug": path["slug"],
                "title": path["title"],
                "steps": len(steps),
                "ordering_violations": ordering_violations,
                "difficulty_jumps": difficulty_jumps,
                "local_prerequisites": local_count,
                "external_prerequisites": external_count,
                "maximum_difficulty": maximum_difficulty,
            }
        )

    difficulty_counts = paths_result.get("learning", {}).get("difficulty_counts", {})
    missing_difficulty_tiers = [
        tier for tier in DIFFICULTY_ORDER if int(difficulty_counts.get(tier, 0)) == 0
    ]

    if upstream_errors or hard_findings:
        status = "FAIL"
    elif missing_difficulty_tiers:
        status = "ATTENTION"
    else:
        status = "PASS"

    return {
        "status": status,
        "path_count": len(path_summaries),
        "post_count": len(paths_result.get("posts", {})),
        "path_summaries": path_summaries,
        "total_prerequisite_references": total_prerequisite_references,
        "local_prerequisite_references": local_prerequisite_references,
        "external_prerequisite_references": len(external_prerequisites),
        "external_prerequisites": external_prerequisites,
        "missing_difficulty_tiers": missing_difficulty_tiers,
        "hard_findings": hard_findings,
        "upstream_errors": upstream_errors,
    }


def structured(result: dict) -> dict:
    return result


def run(*, json_output: bool = False, fail_gaps: bool = False) -> int:
    result = review()
    if json_output:
        print(json.dumps(structured(result), ensure_ascii=False, indent=2))
    else:
        print("Linux Daily — Topic Progression")
        print("=" * 31)
        print(f"status                         {result['status']}")
        print(f"paths                          {result['path_count']}")
        print(f"posts                          {result['post_count']}")
        print(f"prerequisite_references        {result['total_prerequisite_references']}")
        print(f"local_prerequisites            {result['local_prerequisite_references']}")
        print(f"external_prerequisites         {result['external_prerequisite_references']}")
        print(f"hard_findings                  {len(result['hard_findings'])}")
        missing = ", ".join(result["missing_difficulty_tiers"]) or "none"
        print(f"missing_difficulty_tiers       {missing}")

        for problem in result["upstream_errors"]:
            print(f"LỖI upstream: {problem}", file=sys.stderr)
        for finding in result["hard_findings"]:
            print(
                f"LỖI [{finding['code']}] {finding['path_title']}: {finding['message']}",
                file=sys.stderr,
            )
        for tier in result["missing_difficulty_tiers"]:
            print(f"CHÚ Ý: curriculum chưa có bài difficulty={tier}.")

    if result["upstream_errors"] or result["hard_findings"]:
        return 1
    if fail_gaps and result["missing_difficulty_tiers"]:
        return 1
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Xuất structured progression evidence.")
    parser.add_argument(
        "--fail-gaps",
        action="store_true",
        help="Fail nếu curriculum còn thiếu một difficulty tier; không dùng trong publish CI mặc định.",
    )
    args = parser.parse_args(argv)
    return run(json_output=args.json, fail_gaps=args.fail_gaps)


if __name__ == "__main__":
    raise SystemExit(main())

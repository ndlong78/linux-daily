#!/usr/bin/env python3
"""Build/check the P10.5 derived Daily Operations Dashboard."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timezone
from pathlib import Path

import cadence
import content_lifecycle
import coverage_intelligence
import curriculum_planner
import learning_dashboard
import publication_readiness
import quality_dashboard

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state.json"
OUTPUT_PATH = ROOT / "docs" / "daily-operations-dashboard.md"


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _deterministic_as_of(state: dict | None = None) -> date:
    state = state if state is not None else _state()
    raw = state.get("last_published_date")
    if not raw:
        raise ValueError("state.last_published_date bị thiếu")
    return date.fromisoformat(str(raw))


def collect(*, as_of: date | None = None) -> dict:
    state = _state()
    as_of = as_of or _deterministic_as_of(state)
    posts = curriculum_planner.published()
    plan = curriculum_planner.load_plan()
    planner_errors = curriculum_planner.validate(plan, posts)
    plan_snapshot = curriculum_planner.snapshot(plan, posts)
    readiness_errors = publication_readiness.validate(plan, posts)
    readiness = publication_readiness.report(plan, posts)
    quality = quality_dashboard.collect(as_of=as_of)
    learning = learning_dashboard.collect()
    lifecycle = content_lifecycle.analyze(as_of=as_of)
    coverage = coverage_intelligence.analyze(posts=coverage_intelligence.corpus(), plan=plan)

    now = datetime.combine(as_of, time.max, tzinfo=timezone.utc)
    days_since = cadence.days_since(state, now)
    due = cadence.is_due(state, cadence.DEFAULT_INTERVAL_DAYS, now)
    next_topic = plan_snapshot["topics"][0] if plan_snapshot["topics"] else None

    review_queue = []
    review_queue.extend(
        {
            "source": "quality",
            "issue": item.get("issue"),
            "detail": item.get("finding", ""),
        }
        for item in quality.get("remediation_queue", [])
    )
    if lifecycle.get("review_due", 0):
        review_queue.append(
            {
                "source": "lifecycle",
                "issue": None,
                "detail": f"{lifecycle['review_due']} bài đang review-due",
            }
        )
    review_queue.extend(
        {
            "source": "coverage",
            "issue": None,
            "detail": f"{item['axis']}: {item['topic']}",
        }
        for item in coverage.get("recommendations", [])
    )

    errors = [
        *planner_errors,
        *readiness_errors,
        *quality.get("errors", []),
        *learning.get("errors", []),
        *lifecycle.get("errors", []),
    ]
    return {
        "as_of": as_of.isoformat(),
        "last_published_issue": int(state.get("last_issue", 0)),
        "last_published_date": state.get("last_published_date"),
        "last_generated_at": state.get("last_generated_at"),
        "cadence_days": cadence.DEFAULT_INTERVAL_DAYS,
        "days_since_generation": days_since,
        "cadence_due": due,
        "next_issue": plan_snapshot["next_issue"],
        "next_topic": next_topic,
        "readiness_ready": readiness["ready"] and not readiness_errors,
        "required_platforms": readiness["required_platforms"],
        "minimum_primary_sources": readiness["minimum_primary_sources"],
        "quality_status": quality["status"],
        "quality_hard_errors": len(quality.get("errors", [])),
        "quality_remediation": len(quality.get("remediation_queue", [])),
        "learning_status": learning["status"],
        "learning_covered": learning["covered_post_count"],
        "learning_posts": learning["post_count"],
        "learning_paths": learning["path_count"],
        "lifecycle": {
            "current": lifecycle["current"],
            "review_due": lifecycle["review_due"],
            "historically_valid": lifecycle["historically_valid"],
            "superseded": lifecycle["superseded"],
        },
        "coverage": {
            "capabilities": coverage["capabilities"],
            "covered": coverage["covered"],
            "planned": coverage["planned"],
            "gaps": coverage["gaps"],
            "recommendations": coverage["recommendations"],
        },
        "review_queue": review_queue,
        "errors": errors,
    }


def render(result: dict) -> str:
    topic = result.get("next_topic") or {}
    cadence_status = "DUE" if result["cadence_due"] else "WAIT"
    readiness_status = "READY" if result["readiness_ready"] else "BLOCKED"
    overall = "PASS" if not result["errors"] else "FAIL"
    lifecycle = result["lifecycle"]
    coverage = result["coverage"]
    lines = [
        "# Linux Daily — Daily Operations Dashboard",
        "",
        f"Deterministic operational snapshot · **{result['as_of']}**.",
        "",
        "## Executive status",
        "",
        "| Signal | Status | Detail |",
        "|---|---|---|",
        f"| Overall | **{overall}** | hard errors: {len(result['errors'])} |",
        f"| Cadence | **{cadence_status}** | every {result['cadence_days']} day(s) · days since generation: {result['days_since_generation']} |",
        f"| Publication readiness | **{readiness_status}** | next #{result['next_issue']:03d} · 4-platform scope · primary sources >= {result['minimum_primary_sources']} |",
        f"| P7 quality | **{result['quality_status']}** | hard errors {result['quality_hard_errors']} · remediation {result['quality_remediation']} |",
        f"| Learning | **{result['learning_status']}** | covered {result['learning_covered']}/{result['learning_posts']} · paths {result['learning_paths']} |",
        f"| Lifecycle | **PASS** | current {lifecycle['current']} · review-due {lifecycle['review_due']} · historical {lifecycle['historically_valid']} · superseded {lifecycle['superseded']} |",
        f"| Coverage intelligence | **PASS** | capabilities {coverage['capabilities']} · covered {coverage['covered']} · planned {coverage['planned']} · gaps {coverage['gaps']} |",
        "",
        "## Publication clock",
        "",
        f"- Last published: **#{result['last_published_issue']:03d}** · `{result['last_published_date']}`",
        f"- Last generated at: `{result['last_generated_at']}`",
        f"- Next resolved issue: **#{result['next_issue']:03d}**",
        f"- Cadence gate: **{cadence_status}**",
        "",
        "## Next planned topic",
        "",
        f"- Axis: **{topic.get('axis', 'n/a')}**",
        f"- Topic: **{topic.get('topic', 'n/a')}**",
        f"- Difficulty: `{topic.get('difficulty', 'n/a')}`",
        f"- Goal: {topic.get('goal', 'n/a')}",
        f"- Prerequisites: {', '.join(f'#{value:03d}' for value in topic.get('prerequisites', [])) or 'none'}",
        f"- Authoring readiness: **{readiness_status}**",
        "",
        "## Review queue",
        "",
    ]
    if result["review_queue"]:
        for item in result["review_queue"]:
            issue = f"#{int(item['issue']):03d}" if item.get("issue") is not None else "n/a"
            lines.append(f"- **{item['source']}** · {issue} · {item['detail']}")
    else:
        lines.append("- PASS: no quality/lifecycle/coverage review item.")

    lines.extend(["", "## Coverage recommendations", ""])
    if coverage["recommendations"]:
        for item in coverage["recommendations"]:
            lines.append(
                f"- **{item['axis']}** · {item['topic']} · `{item['difficulty']}` — {item['reason']}"
            )
    else:
        lines.append("- PASS: no uncovered capability recommendation.")

    lines.extend(["", "## Hard findings", ""])
    if result["errors"]:
        lines.extend(f"- FAIL: {error}" for error in result["errors"])
    else:
        lines.append("- PASS: all deterministic P10 operational inputs are internally consistent.")

    lines.extend(
        [
            "",
            "> This dashboard is a derived view only. `state.json`, published post metadata, "
            "`curriculum-plan.json`, learning/quality/lifecycle validators and their source files remain authoritative.",
            "",
        ]
    )
    return "\n".join(lines)


def run(*, check: bool = False, json_output: bool = False, as_of: date | None = None) -> int:
    result = collect(as_of=as_of)
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["errors"] else 0
    expected = render(result)
    if check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != expected:
            print(
                "LỖI: docs/daily-operations-dashboard.md chưa đồng bộ. "
                "Chạy `python3 tools/daily_operations_dashboard.py` rồi commit lại."
            )
            return 1
        if result["errors"]:
            for error in result["errors"]:
                print(f"LỖI: {error}")
            return 1
        print(
            "OK: daily operations dashboard đồng bộ; "
            f"next=#{result['next_issue']:03d}, cadence={'DUE' if result['cadence_due'] else 'WAIT'}."
        )
        return 0
    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"Đã cập nhật {OUTPUT_PATH.relative_to(ROOT)}")
    return 1 if result["errors"] else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--as-of", help="Override YYYY-MM-DD; mặc định state.last_published_date để deterministic.")
    args = parser.parse_args(argv)
    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    return run(check=args.check, json_output=args.json, as_of=as_of)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Aggregate P7 content-quality signals without duplicating their validation rules."""
from __future__ import annotations

import argparse
import glob
import json
from datetime import date
from pathlib import Path

import command_quality
import content_freshness
import distro_coverage
import postmeta
import validate_sources

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
STATE_PATH = ROOT / "state.json"
REPORT_PATH = ROOT / "docs" / "quality-dashboard.md"
MERGEABLE_REVIEW_STATUSES = {"reviewed", "published"}
PRIMARY_SOURCE_KINDS = {"official", "upstream"}


def canonical_as_of() -> date:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    value = state.get("last_published_date")
    if not isinstance(value, str):
        raise ValueError("state.json thiếu last_published_date")
    return date.fromisoformat(value)


def collect_source_quality() -> dict:
    posts: list[dict] = []
    total_sources = 0
    primary_sources = 0
    source_backed_posts = 0
    reviewed_source_posts = 0
    missing_source_posts: list[dict] = []

    for raw_path in glob.glob(POSTS_GLOB):
        path = Path(raw_path)
        meta = postmeta.read_meta(str(path))
        issue = int(meta["issue"])
        sources = meta.get("sources")
        backed = isinstance(sources, list) and bool(sources)
        source_count = len(sources) if isinstance(sources, list) else 0
        primary_count = (
            sum(
                isinstance(source, dict) and source.get("kind") in PRIMARY_SOURCE_KINDS
                for source in sources
            )
            if isinstance(sources, list)
            else 0
        )
        if backed:
            source_backed_posts += 1
            total_sources += source_count
            primary_sources += primary_count
            if meta.get("review_status") in MERGEABLE_REVIEW_STATUSES:
                reviewed_source_posts += 1
        else:
            missing_source_posts.append(
                {
                    "issue": issue,
                    "title": str(meta["title"]).strip(),
                    "path": path.relative_to(ROOT).as_posix(),
                }
            )
        posts.append(
            {
                "issue": issue,
                "title": str(meta["title"]).strip(),
                "review_status": meta.get("review_status"),
                "source_count": source_count,
                "primary_source_count": primary_count,
                "source_backed": backed,
            }
        )

    posts.sort(key=lambda item: item["issue"])
    missing_source_posts.sort(key=lambda item: item["issue"])
    source_gate = validate_sources.run()
    return {
        "posts": posts,
        "total_posts": len(posts),
        "source_backed_posts": source_backed_posts,
        "reviewed_source_posts": reviewed_source_posts,
        "total_sources": total_sources,
        "primary_sources": primary_sources,
        "missing_source_posts": missing_source_posts,
        "errors": list(source_gate.errors),
    }


def _signal_status(*, errors: list, attention: list) -> str:
    if errors:
        return "FAIL"
    if attention:
        return "ATTENTION"
    return "PASS"


def _queue_item(
    *,
    signal: str,
    owner: str,
    issue: int | None,
    finding: str,
    remediation: str,
) -> dict:
    return {
        "severity": "ATTENTION",
        "signal": signal,
        "owner": owner,
        "issue": issue,
        "finding": finding,
        "remediation": remediation,
    }


def collect(*, as_of: date | None = None) -> dict:
    as_of = as_of or canonical_as_of()
    distro = distro_coverage.review()
    commands = command_quality.review()
    freshness = content_freshness.review(as_of=as_of)
    sources = collect_source_quality()

    distro_errors = distro_coverage.errors(distro)
    command_errors = command_quality.errors(commands)
    freshness_errors = list(freshness["errors"])
    source_errors = list(sources["errors"])

    distro_attention: list[dict] = []
    queue: list[dict] = []
    for post in distro["posts"]:
        missing = distro_coverage.missing_coverage(post)
        if not missing:
            continue
        finding = f"#{post['issue']:03d} thiếu explicit coverage: {', '.join(missing)}"
        distro_attention.append({"issue": post["issue"], "finding": finding})
        if post["issue"] < distro_coverage.ENFORCE_COMPLETE_FROM_ISSUE:
            queue.append(
                _queue_item(
                    signal="Distro portability",
                    owner="Technical reviewer",
                    issue=int(post["issue"]),
                    finding=finding,
                    remediation="docs/distro-portability.md",
                )
            )

    command_attention = list(commands["review_queue"])
    for finding in command_attention:
        queue.append(
            _queue_item(
                signal="Command/config",
                owner="Technical reviewer",
                issue=int(finding["issue"]),
                finding=f"[{finding['code']}] {finding['message']}",
                remediation="docs/command-config-quality.md",
            )
        )

    freshness_attention = list(freshness["review_due"])
    for item in freshness_attention:
        queue.append(
            _queue_item(
                signal="Freshness",
                owner="Freshness reviewer",
                issue=int(item["issue"]),
                finding=f"review due {item['review_due_on']} ({item['volatility']})",
                remediation="docs/content-freshness.md",
            )
        )

    source_attention = list(sources["missing_source_posts"])
    for item in source_attention:
        queue.append(
            _queue_item(
                signal="Source quality",
                owner="Content author / reviewer",
                issue=int(item["issue"]),
                finding="chưa có structured official/upstream source evidence",
                remediation="docs/technical-review-guide.md",
            )
        )

    queue.sort(key=lambda item: (item["issue"] if item["issue"] is not None else 999999, item["signal"], item["finding"]))

    hard_errors: list[dict] = []
    for signal, problems in (
        ("Distro portability", distro_errors),
        ("Command/config", command_errors),
        ("Freshness", freshness_errors),
        ("Source quality", source_errors),
    ):
        hard_errors.extend({"signal": signal, "message": problem} for problem in problems)

    signals = {
        "distro": {
            "status": _signal_status(errors=distro_errors, attention=distro_attention),
            "complete_posts": distro["complete_posts"],
            "total_posts": distro["total"],
            "freebsd_marked_posts": distro["freebsd_marked_posts"],
            "portability_violations": distro["violation_count"],
            "review_items": len(distro_attention),
        },
        "command": {
            "status": _signal_status(errors=command_errors, attention=command_attention),
            "code_blocks": commands["code_blocks"],
            "command_lines": commands["command_lines"],
            "privileged_lines": commands["privileged_lines"],
            "destructive_lines": commands["destructive_lines"],
            "blockers": len(commands["blockers"]),
            "review_items": len(command_attention),
        },
        "freshness": {
            "status": _signal_status(errors=freshness_errors, attention=freshness_attention),
            "current": freshness["counts"].get("current", 0),
            "review_due": freshness["counts"].get("review-due", 0),
            "historically_valid": freshness["counts"].get("historically-valid", 0),
            "total_posts": freshness["total"],
        },
        "sources": {
            "status": _signal_status(errors=source_errors, attention=source_attention),
            "source_backed_posts": sources["source_backed_posts"],
            "reviewed_source_posts": sources["reviewed_source_posts"],
            "total_posts": sources["total_posts"],
            "technical_sources": sources["total_sources"],
            "primary_sources": sources["primary_sources"],
            "missing_source_posts": len(source_attention),
        },
    }

    if hard_errors:
        overall = "FAIL"
    elif queue:
        overall = "ATTENTION"
    else:
        overall = "PASS"

    return {
        "as_of": as_of.isoformat(),
        "status": overall,
        "total_posts": distro["total"],
        "signals": signals,
        "remediation_queue": queue,
        "errors": hard_errors,
        "historically_valid": list(freshness["historically_valid"]),
    }


def render_markdown(result: dict) -> str:
    signals = result["signals"]
    lines = [
        "# Linux Daily — P7 Audit & Quality Dashboard",
        "",
        f"Derived quality snapshot · as of **{result['as_of']}**.",
        "",
        "## Executive status",
        "",
        f"- P7 quality: **{result['status']}**",
        f"- Published posts: **{result['total_posts']}**",
        f"- Hard errors: **{len(result['errors'])}**",
        f"- Remediation queue: **{len(result['remediation_queue'])}**",
        "",
        "| Signal | Status | Detail |",
        "|---|---|---|",
        f"| Distro coverage & portability | **{signals['distro']['status']}** | {signals['distro']['complete_posts']}/{signals['distro']['total_posts']} complete · FreeBSD blocks {signals['distro']['freebsd_marked_posts']}/{signals['distro']['total_posts']} · violations {signals['distro']['portability_violations']} |",
        f"| Command & configuration | **{signals['command']['status']}** | {signals['command']['code_blocks']} blocks · {signals['command']['command_lines']} lines · blockers {signals['command']['blockers']} · review {signals['command']['review_items']} |",
        f"| Content freshness | **{signals['freshness']['status']}** | current {signals['freshness']['current']} · review-due {signals['freshness']['review_due']} · historically-valid {signals['freshness']['historically_valid']} |",
        f"| Source quality | **{signals['sources']['status']}** | backed {signals['sources']['source_backed_posts']}/{signals['sources']['total_posts']} · reviewed {signals['sources']['reviewed_source_posts']}/{signals['sources']['total_posts']} · sources {signals['sources']['technical_sources']} |",
        "",
        "## Quality evidence",
        "",
        "### Distro portability",
        "",
        f"- Complete four-platform coverage: **{signals['distro']['complete_posts']}/{signals['distro']['total_posts']}**",
        f"- Explicit FreeBSD blocks: **{signals['distro']['freebsd_marked_posts']}/{signals['distro']['total_posts']}**",
        f"- Linux-only semantics inside FreeBSD blocks: **{signals['distro']['portability_violations']}**",
        "",
        "### Command / configuration safety",
        "",
        f"- Code blocks scanned: **{signals['command']['code_blocks']}**",
        f"- Command/config lines scanned: **{signals['command']['command_lines']}**",
        f"- Privileged lines: **{signals['command']['privileged_lines']}**",
        f"- Destructive storage examples: **{signals['command']['destructive_lines']}**",
        f"- Blocking findings: **{signals['command']['blockers']}**",
        "",
        "### Freshness / technical drift",
        "",
        f"- Current: **{signals['freshness']['current']}**",
        f"- Review due: **{signals['freshness']['review_due']}**",
        f"- Historically valid: **{signals['freshness']['historically_valid']}**",
        "",
        "### Source evidence",
        "",
        f"- Posts with structured source evidence: **{signals['sources']['source_backed_posts']}/{signals['sources']['total_posts']}**",
        f"- Source-backed posts with mergeable review status: **{signals['sources']['reviewed_source_posts']}/{signals['sources']['total_posts']}**",
        f"- Official/upstream technical sources: **{signals['sources']['primary_sources']}**",
        "",
        "## Remediation queue",
        "",
    ]

    if result["remediation_queue"]:
        lines.extend(
            [
                "| Severity | Signal | Owner | Issue | Finding | Remediation |",
                "|---|---|---|---:|---|---|",
            ]
        )
        for item in result["remediation_queue"]:
            issue = f"#{item['issue']:03d}" if item["issue"] is not None else "n/a"
            lines.append(
                f"| {item['severity']} | {item['signal']} | {item['owner']} | {issue} | {item['finding']} | `{item['remediation']}` |"
            )
    else:
        lines.append("- PASS: không có non-blocking quality debt cần remediation.")

    lines.extend(["", "## Hard errors", ""])
    if result["errors"]:
        for item in result["errors"]:
            lines.append(f"- FAIL · **{item['signal']}**: {item['message']}")
    else:
        lines.append("- PASS: không có hard-error từ P7 validators/source gate.")

    lines.extend(
        [
            "",
            "## Ownership & remediation",
            "",
            "| Signal | Primary owner | Remediation contract |",
            "|---|---|---|",
            "| Distro coverage / FreeBSD portability | Technical reviewer | `docs/distro-portability.md` |",
            "| Command / configuration safety | Technical reviewer | `docs/command-config-quality.md` |",
            "| Freshness / technical drift | Freshness reviewer | `docs/content-freshness.md` |",
            "| Source quality | Content author / reviewer | `docs/technical-review-guide.md` |",
            "",
            "> This dashboard is derived evidence only. P7.1–P7.3 validators, source metadata, `freshness.json` and post content remain the sources of truth. The dashboard imports those rules; it does not reimplement them.",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    *,
    as_of: date,
    check: bool,
    json_output: bool,
    output: Path | None,
    write_default: bool,
) -> int:
    result = collect(as_of=as_of)
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["errors"] else 0

    report = render_markdown(result)
    if check:
        current = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.exists() else ""
        if current != report:
            print(
                "LỖI: docs/quality-dashboard.md chưa đồng bộ. "
                "Chạy `python tools/quality_dashboard.py`."
            )
            return 1
    elif output is not None:
        output.write_text(report, encoding="utf-8")
        print(f"Wrote quality dashboard: {output}")
    elif write_default:
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"Đã cập nhật quality dashboard cho {result['total_posts']} bài.")
    else:
        print(report)

    if result["errors"]:
        print(f"LỖI: quality dashboard tổng hợp {len(result['errors'])} hard error")
        return 1
    if check:
        print(
            "OK: quality dashboard đồng bộ; "
            f"status={result['status']}, remediation={len(result['remediation_queue'])}."
        )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail nếu committed dashboard bị drift.")
    parser.add_argument("--as-of", help="Dynamic audit date YYYY-MM-DD; mặc định dùng state.last_published_date.")
    parser.add_argument("--json", action="store_true", help="Xuất structured JSON cho audit/tooling.")
    parser.add_argument("--output", help="Write dynamic Markdown dashboard to this path.")
    args = parser.parse_args(argv)
    if args.check and args.as_of:
        parser.error("--check luôn dùng canonical state.last_published_date; không kết hợp --as-of")

    explicit_as_of = bool(args.as_of)
    as_of = date.fromisoformat(args.as_of) if args.as_of else canonical_as_of()
    return run(
        as_of=as_of,
        check=args.check,
        json_output=args.json,
        output=Path(args.output) if args.output else None,
        write_default=not explicit_as_of and not args.output and not args.json and not args.check,
    )


if __name__ == "__main__":
    raise SystemExit(main())

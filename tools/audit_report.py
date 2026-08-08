#!/usr/bin/env python3
"""Aggregate Linux Daily audit evidence without creating a new source of truth."""
from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

import check_production
import content_mix
import operations_dashboard
import quality_dashboard
import repo_health

ROOT = Path(__file__).resolve().parents[1]


def _workflow_badge(state: operations_dashboard.WorkflowState) -> str:
    return operations_dashboard._workflow_badge(state)


def build(*, as_of: date, github: bool = False, production: bool = False) -> tuple[str, int]:
    health = repo_health.collect()
    mix = content_mix.review()
    mix_errors = content_mix.errors(mix)
    quality = quality_dashboard.collect(as_of=as_of)
    publication = operations_dashboard.collect_publication(as_of)
    workflows = (
        operations_dashboard.collect_workflows(
            os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_TOKEN", "")
        )
        if github
        else [
            operations_dashboard._unknown_workflow("CI", "offline mode"),
            operations_dashboard._unknown_workflow("Production Smoke", "offline mode"),
        ]
    )
    production_result = check_production._check_once() if production else None

    workflow_failures = [state.name for state in workflows if _workflow_badge(state) == "FAIL"]
    failures = (
        len(health.errors)
        + len(mix_errors)
        + len(workflow_failures)
        + len(quality["errors"])
    )
    if production_result is not None and not production_result.ok:
        failures += len(production_result.errors) or 1

    lines = [
        "# Linux Daily — Audit Report",
        "",
        f"Derived evidence snapshot · **{as_of.isoformat()}**.",
        "",
        "## Executive status",
        "",
        f"- Overall: **{'PASS' if failures == 0 else 'FAIL'}**",
        f"- Latest publication: **#{publication.issue:03d}** · {publication.published.isoformat()} · **{publication.freshness}**",
        f"- Repository health: **{'PASS' if not health.errors else 'FAIL'}**",
        f"- Content mix: **{'PASS' if not mix_errors else 'FAIL'}** · spread={mix['spread']} · next=#{mix['next_issue']:03d} {mix['next_axis']}",
        f"- P7 content quality: **{quality['status']}** · hard_errors={len(quality['errors'])} · remediation={len(quality['remediation_queue'])}",
        "",
        "## Repository inventory",
        "",
        "| Metric | Count |",
        "|---|---:|",
    ]
    for key in (
        "posts",
        "generated_pages",
        "technical_sources",
        "social_code_images",
        "woff2_fonts",
        "rss_items",
        "sitemap_urls",
    ):
        lines.append(f"| `{key}` | {health.metrics.get(key, 0)} |")

    quality_signals = quality["signals"]
    lines.extend(
        [
            "",
            "## P7 quality evidence",
            "",
            "| Signal | Status | Detail |",
            "|---|---|---|",
            f"| Distro portability | **{quality_signals['distro']['status']}** | complete {quality_signals['distro']['complete_posts']}/{quality_signals['distro']['total_posts']} · review {quality_signals['distro']['review_items']} · violations {quality_signals['distro']['portability_violations']} |",
            f"| Command/config | **{quality_signals['command']['status']}** | blockers {quality_signals['command']['blockers']} · review {quality_signals['command']['review_items']} · destructive {quality_signals['command']['destructive_lines']} |",
            f"| Freshness | **{quality_signals['freshness']['status']}** | current {quality_signals['freshness']['current']} · review-due {quality_signals['freshness']['review_due']} · historical {quality_signals['freshness']['historically_valid']} |",
            f"| Source quality | **{quality_signals['sources']['status']}** | backed {quality_signals['sources']['source_backed_posts']}/{quality_signals['sources']['total_posts']} · sources {quality_signals['sources']['technical_sources']} |",
            "",
            "### Quality remediation queue",
            "",
        ]
    )
    if quality["remediation_queue"]:
        for item in quality["remediation_queue"]:
            issue = f"#{item['issue']:03d}" if item["issue"] is not None else "n/a"
            lines.append(
                f"- **{item['signal']}** · {issue} · owner: {item['owner']} · "
                f"{item['finding']} · `{item['remediation']}`"
            )
    else:
        lines.append("- PASS: no P7 remediation items.")

    lines.extend(["", "## Workflow evidence", "", "| Workflow | Status | SHA |", "|---|---|---|"])
    for state in workflows:
        lines.append(
            f"| {state.name} | **{_workflow_badge(state)}** | "
            f"`{state.head_sha[:8] if state.head_sha else 'n/a'}` |"
        )

    lines.extend(["", "## Production evidence", ""])
    if production_result is None:
        lines.append("- Not requested (offline/local audit mode).")
    else:
        lines.append(f"- Status: **{'PASS' if production_result.ok else 'FAIL'}**")
        lines.append(
            f"- Expected fingerprint: `{production_result.expected_fingerprint or 'n/a'}`"
        )
        lines.append(
            f"- Production fingerprint: `{production_result.production_fingerprint or 'n/a'}`"
        )
        for warning in production_result.warnings:
            lines.append(f"- Warning: {warning}")
        for error in production_result.errors:
            lines.append(f"- FAIL: {error}")

    lines.extend(["", "## Findings", ""])
    findings = [*health.errors, *mix_errors]
    findings.extend(f"workflow {name} latest main run failed" for name in workflow_failures)
    findings.extend(
        f"P7 {item['signal']}: {item['message']}" for item in quality["errors"]
    )
    if production_result is not None:
        findings.extend(production_result.errors)
    if findings:
        lines.extend(f"- FAIL: {item}" for item in findings)
    else:
        lines.append("- PASS: no hard audit findings in the requested evidence set.")

    lines.extend(
        [
            "",
            "> This report is derived evidence only. Repository metadata/artifacts, P7 validators, "
            "GitHub Actions and the production serving state remain the sources of truth.",
            "",
        ]
    )
    return "\n".join(lines), 1 if failures else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--github", action="store_true", help="Include latest main CI/Production Smoke evidence."
    )
    parser.add_argument(
        "--production", action="store_true", help="Run live production observability once."
    )
    parser.add_argument("--as-of", help="Audit date as YYYY-MM-DD.")
    parser.add_argument("--output", help="Write Markdown report to this path.")
    args = parser.parse_args(argv)
    as_of = date.fromisoformat(args.as_of) if args.as_of else operations_dashboard._today()
    report, code = build(as_of=as_of, github=args.github, production=args.production)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Wrote audit report: {args.output}")
    else:
        print(report)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

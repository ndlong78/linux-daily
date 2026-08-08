#!/usr/bin/env python3
"""Build a source-derived operations dashboard for Linux Daily.

Repository metrics are collected locally. When --github is enabled, the script reads
latest GitHub Actions workflow state using GITHUB_TOKEN. The generated report is an
operational view only; repository files and GitHub Actions remain the sources of truth.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postmeta  # noqa: E402
import repo_health  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state.json"
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
EXPECTED_CADENCE_DAYS = 2
WORKFLOWS = (
    ("CI", "ci.yml"),
    ("Production Smoke", "production-smoke.yml"),
)
USER_AGENT = "linux-daily-operations-dashboard/1.0"


@dataclass(frozen=True)
class Publication:
    issue: int
    title: str
    published: date
    age_days: int
    freshness: str


@dataclass(frozen=True)
class WorkflowState:
    name: str
    status: str
    conclusion: str
    head_sha: str
    updated_at: str
    url: str
    note: str = ""


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _load_state() -> dict:
    with STATE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _latest_post() -> tuple[str, dict]:
    posts = glob.glob(POSTS_GLOB)
    if not posts:
        raise RuntimeError("repository không có post HTML")
    path = max(posts, key=lambda p: int(Path(p).name.split("-")[1]))
    return path, postmeta.read_meta(path)


def _freshness(age_days: int) -> str:
    if age_days <= EXPECTED_CADENCE_DAYS:
        return "FRESH"
    if age_days <= EXPECTED_CADENCE_DAYS * 2:
        return "ATTENTION"
    return "STALE"


def collect_publication(as_of: date) -> Publication:
    _, meta = _latest_post()
    published = date.fromisoformat(str(meta["date"]))
    age_days = max(0, (as_of - published).days)
    return Publication(
        issue=int(meta["issue"]),
        title=str(meta["title"]),
        published=published,
        age_days=age_days,
        freshness=_freshness(age_days),
    )


def _unknown_workflow(name: str, note: str) -> WorkflowState:
    return WorkflowState(
        name=name,
        status="unknown",
        conclusion="unknown",
        head_sha="",
        updated_at="",
        url="",
        note=note,
    )


def _github_request(url: str, token: str, timeout: float = 10.0) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_workflow_state(repository: str, workflow_file: str, name: str, token: str) -> WorkflowState:
    repo = urllib.parse.quote(repository, safe="/")
    workflow = urllib.parse.quote(workflow_file, safe="")
    url = (
        f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs"
        "?branch=main&per_page=1&exclude_pull_requests=true"
    )
    try:
        payload = _github_request(url, token)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return _unknown_workflow(name, f"GitHub API unavailable: {exc}")

    runs = payload.get("workflow_runs", [])
    if not runs:
        return _unknown_workflow(name, "no workflow run found on main")
    run = runs[0]
    return WorkflowState(
        name=name,
        status=str(run.get("status") or "unknown"),
        conclusion=str(run.get("conclusion") or "pending"),
        head_sha=str(run.get("head_sha") or ""),
        updated_at=str(run.get("updated_at") or ""),
        url=str(run.get("html_url") or ""),
    )


def collect_workflows(repository: str, token: str) -> list[WorkflowState]:
    if not repository:
        return [_unknown_workflow(name, "GITHUB_REPOSITORY not set") for name, _ in WORKFLOWS]
    if not token:
        return [_unknown_workflow(name, "GITHUB_TOKEN not set") for name, _ in WORKFLOWS]
    return [
        fetch_workflow_state(repository, workflow_file, name, token)
        for name, workflow_file in WORKFLOWS
    ]


def _workflow_badge(state: WorkflowState) -> str:
    conclusion = state.conclusion.lower()
    if conclusion == "success":
        return "PASS"
    if state.status.lower() in {"queued", "in_progress", "pending", "requested", "waiting"}:
        return "RUNNING"
    if conclusion in {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}:
        return "FAIL"
    return "UNKNOWN"


def render_dashboard(
    publication: Publication,
    metrics: dict[str, int],
    health_errors: list[str],
    workflows: list[WorkflowState],
    as_of: date,
    state: dict,
) -> str:
    health_status = "PASS" if not health_errors else "FAIL"
    lines = [
        "# Linux Daily — Operations Dashboard",
        "",
        f"Generated from repository + GitHub Actions data · as of **{as_of.isoformat()}**.",
        "",
        "## Executive status",
        "",
        "| Signal | Status | Detail |",
        "|---|---|---|",
        f"| Publication freshness | **{publication.freshness}** | #{publication.issue:03d} · {publication.published.isoformat()} · {publication.age_days} day(s) old |",
        f"| Repository health | **{health_status}** | {len(health_errors)} error(s) |",
    ]
    for workflow in workflows:
        badge = _workflow_badge(workflow)
        detail = workflow.conclusion
        if workflow.status != "completed":
            detail = f"{workflow.status} / {workflow.conclusion}"
        if workflow.head_sha:
            detail += f" · `{workflow.head_sha[:8]}`"
        if workflow.note:
            detail += f" · {workflow.note}"
        lines.append(f"| {workflow.name} | **{badge}** | {detail} |")

    lines.extend(
        [
            "",
            "## Latest publication",
            "",
            f"- **#{publication.issue:03d} — {publication.title}**",
            f"- Published: `{publication.published.isoformat()}`",
            f"- Expected cadence: every {EXPECTED_CADENCE_DAYS} days",
            f"- State last issue: `{state.get('last_issue', 'n/a')}`",
            f"- State last published date: `{state.get('last_published_date', 'n/a')}`",
            "",
            "## Artifact inventory",
            "",
            "| Metric | Count |",
            "|---|---:|",
        ]
    )
    for key in (
        "posts",
        "generated_pages",
        "technical_sources",
        "social_code_images",
        "woff2_fonts",
        "rss_items",
        "sitemap_urls",
    ):
        lines.append(f"| `{key}` | {metrics.get(key, 0)} |")

    lines.extend(["", "## Workflow evidence", ""])
    for workflow in workflows:
        evidence = workflow.url or "n/a"
        updated = workflow.updated_at or "n/a"
        lines.append(
            f"- **{workflow.name}:** `{workflow.status}` / `{workflow.conclusion}` · updated `{updated}` · {evidence}"
        )

    lines.extend(["", "## Repository health details", ""])
    if health_errors:
        lines.extend(f"- FAIL: {error}" for error in health_errors)
    else:
        lines.append("- PASS: deterministic repository health checks have no errors.")

    lines.extend(
        [
            "",
            "> This dashboard is a derived operational view, not a source of truth. "
            "Publication data comes from posts/state, inventory from repository artifacts, "
            "and CI/smoke status from GitHub Actions.",
            "",
        ]
    )
    return "\n".join(lines)


def build(as_of: date, github: bool = False) -> tuple[str, int]:
    health = repo_health.collect()
    publication = collect_publication(as_of)
    state = _load_state()
    workflows = (
        collect_workflows(
            os.environ.get("GITHUB_REPOSITORY", ""),
            os.environ.get("GITHUB_TOKEN", ""),
        )
        if github
        else [
            _unknown_workflow("CI", "offline mode"),
            _unknown_workflow("Production Smoke", "offline mode"),
        ]
    )
    report = render_dashboard(
        publication,
        health.metrics,
        health.errors,
        workflows,
        as_of,
        state,
    )
    return report, 1 if health.errors else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github", action="store_true", help="Read latest CI and Production Smoke runs from GitHub Actions.")
    parser.add_argument("--as-of", help="Override report date as YYYY-MM-DD (useful for deterministic tests/audits).")
    parser.add_argument("--output", help="Write Markdown report to this path instead of stdout only.")
    args = parser.parse_args(argv)

    as_of = date.fromisoformat(args.as_of) if args.as_of else _today()
    report, exit_code = build(as_of=as_of, github=args.github)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Wrote operations dashboard: {args.output}")
    else:
        print(report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate Linux Daily release metadata, gates and release notes."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATH = ROOT / "VERSION"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SECTION_RE = re.compile(r"^## \[(?P<version>\d+\.\d+\.\d+)\](?: — (?P<date>\d{4}-\d{2}-\d{2}))?\s*$", re.MULTILINE)
WORKFLOWS = (("CI", "ci.yml"), ("Production Smoke", "production-smoke.yml"))
USER_AGENT = "linux-daily-release/1.0"


@dataclass(frozen=True)
class WorkflowGate:
    name: str
    status: str
    conclusion: str
    head_sha: str
    url: str


def canonical_version() -> str:
    version = VERSION_PATH.read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        raise ValueError(f"VERSION must be strict SemVer X.Y.Z, got {version!r}")
    return version


def tag_for(version: str) -> str:
    if not SEMVER_RE.fullmatch(version):
        raise ValueError(f"invalid release version: {version!r}")
    return f"v{version}"


def changelog_section(version: str) -> str:
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    matches = list(SECTION_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group("version") != version:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if not body:
            raise ValueError(f"CHANGELOG section [{version}] is empty")
        return body
    raise ValueError(f"CHANGELOG.md has no release section [{version}]")


def validate(version: str | None = None) -> str:
    canonical = canonical_version()
    requested = version or canonical
    if requested != canonical:
        raise ValueError(f"requested version {requested} does not match VERSION {canonical}")
    changelog_section(canonical)
    return canonical


def _github_json(url: str, token: str, timeout: float = 10.0) -> dict:
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


def workflow_gate(repository: str, workflow_file: str, name: str, sha: str, token: str) -> WorkflowGate:
    repo = urllib.parse.quote(repository, safe="/")
    workflow = urllib.parse.quote(workflow_file, safe="")
    url = (
        f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs"
        f"?branch=main&head_sha={urllib.parse.quote(sha, safe='')}&status=completed&per_page=1"
    )
    payload = _github_json(url, token)
    runs = payload.get("workflow_runs", [])
    if not runs:
        return WorkflowGate(name, "missing", "missing", "", "")
    run = runs[0]
    return WorkflowGate(
        name=name,
        status=str(run.get("status") or "unknown"),
        conclusion=str(run.get("conclusion") or "unknown"),
        head_sha=str(run.get("head_sha") or ""),
        url=str(run.get("html_url") or ""),
    )


def verify_release_gates(repository: str, sha: str, token: str) -> list[WorkflowGate]:
    if not repository or not sha or not token:
        raise ValueError("repository, sha and GitHub token are required for release gate verification")
    gates: list[WorkflowGate] = []
    try:
        for name, workflow_file in WORKFLOWS:
            gates.append(workflow_gate(repository, workflow_file, name, sha, token))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GitHub Actions gate lookup failed: {exc}") from exc

    failures = [
        gate
        for gate in gates
        if gate.status != "completed" or gate.conclusion != "success" or gate.head_sha != sha
    ]
    if failures:
        detail = "; ".join(
            f"{gate.name}={gate.status}/{gate.conclusion} sha={gate.head_sha[:8] or 'n/a'}"
            for gate in failures
        )
        raise RuntimeError(f"release blocked: required workflow gates are not green on {sha[:8]}: {detail}")
    return gates


def render_curated_notes(version: str) -> str:
    body = changelog_section(version)
    return f"# Linux Daily {tag_for(version)}\n\n{body}\n"


def _write_or_print(text: str, output: str | None) -> None:
    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        print(text, end="")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser("validate", help="Validate VERSION and CHANGELOG release metadata.")
    validate_parser.add_argument("--version")

    notes_parser = sub.add_parser("notes", help="Render curated release notes from CHANGELOG.")
    notes_parser.add_argument("--version")
    notes_parser.add_argument("--output")

    gate_parser = sub.add_parser("gate", help="Require CI and Production Smoke success on the exact main SHA.")
    gate_parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    gate_parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA", ""))

    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            version = validate(args.version)
            print(f"OK: release metadata valid for {tag_for(version)}")
        elif args.command == "notes":
            version = validate(args.version)
            _write_or_print(render_curated_notes(version), args.output)
        elif args.command == "gate":
            token = os.environ.get("GITHUB_TOKEN", "")
            gates = verify_release_gates(args.repository, args.sha, token)
            for gate in gates:
                print(f"OK: {gate.name} success on {gate.head_sha[:8]} — {gate.url}")
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

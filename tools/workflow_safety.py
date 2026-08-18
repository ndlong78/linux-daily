#!/usr/bin/env python3
"""Validate GitHub Actions workflows against Linux Daily safety boundaries."""
from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
RELEASE_WORKFLOW = "release.yml"
CI_WORKFLOW = "ci.yml"
AUTO_MERGE_WORKFLOW = "linux-daily-auto-merge.yml"
MATERIALIZE_WORKFLOW = "materialize-artifacts.yml"
WRITE_PERMISSION_RE = re.compile(
    r"^\s{2}(contents|actions|pull-requests|issues|packages|deployments):\s*write\s*$",
    re.MULTILINE,
)
SELF_MUTATION_RE = re.compile(r"\bgit\s+(?:add|commit|push)\b", re.IGNORECASE)
TOOLS_DIR = ROOT / "tools"
RUN_TOOL_RE = re.compile(r"python[0-9.]*\s+tools/([a-z0-9_]+)\.py")
PIP_INSTALL_RE = re.compile(r"\bpip\s+install\b")
TOOL_REFERENCE_RE = re.compile(r"[\"']tools/([a-z0-9_]+)\.py[\"']")
# Import name của dependency khai báo trong pyproject (Pillow, Jinja2).
# tests/test_workflow_safety.py canh pyproject để bộ này không trôi.
THIRD_PARTY_MODULES = frozenset({"PIL", "jinja2"})


@dataclass
class Report:
    checked: int = 0
    errors: list[str] = field(default_factory=list)


def _tool_imports(name: str) -> set[str]:
    """Top-level module mà tools/<name>.py import trực tiếp."""
    path = TOOLS_DIR / f"{name}.py"
    if not path.exists():
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:  # pragma: no cover - defensive
        return set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module.split(".")[0])
    return modules


def _tool_edges(name: str) -> set[str]:
    """Tool khác mà tools/<name>.py phụ thuộc: qua import, hoặc qua subprocess.

    publish.py và pr_preflight.py không import gì của bên thứ ba — chúng spawn
    tool khác bằng subprocess. Chỉ nhìn import sẽ kết luận sai là chúng không cần
    dependency, nên bắt cả tham chiếu dạng chuỗi "tools/<x>.py".
    """
    path = TOOLS_DIR / f"{name}.py"
    edges = {m for m in _tool_imports(name) if (TOOLS_DIR / f"{m}.py").exists()}
    if path.exists():
        edges |= set(TOOL_REFERENCE_RE.findall(path.read_text(encoding="utf-8")))
    return {edge for edge in edges if (TOOLS_DIR / f"{edge}.py").exists()}


def needs_third_party(name: str, _seen: frozenset[str] = frozenset()) -> bool:
    """True nếu tools/<name>.py chạm tới dependency bên thứ ba, kể cả gián tiếp.

    Lỗi thật đã gặp là gián tiếp: check_production -> site_fingerprint -> socialmeta
    -> PIL. Nhìn import trực tiếp của check_production thì không thấy gì, nên phải
    đi hết đồ thị phụ thuộc nội bộ trong tools/.
    """
    if name in _seen:
        return False
    seen = _seen | {name}
    if _tool_imports(name) & THIRD_PARTY_MODULES:
        return True
    return any(needs_third_party(edge, seen) for edge in _tool_edges(name))


def _validate_dependency_install(rel: str, text: str) -> list[str]:
    """Workflow chạy tool cần dependency thì phải cài dependency.

    Thiếu bước này job chết ngay lúc import, và một job đỏ vì ImportError trông
    hệt như một job đỏ vì phát hiện sự cố thật.
    """
    if PIP_INSTALL_RE.search(text):
        return []
    offenders = sorted({
        name for name in RUN_TOOL_RE.findall(text) if needs_third_party(name)
    })
    return [
        f"{rel}: chạy tools/{name}.py (cần dependency bên thứ ba) nhưng không có bước pip install"
        for name in offenders
    ]


def _event_block(text: str) -> str:
    match = re.search(r"(?ms)^on:\s*\n(.*?)(?=^[A-Za-z_-]+:\s*(?:\n|$))", text)
    return match.group(1) if match else ""


def _permissions_block(text: str) -> str:
    match = re.search(r"(?ms)^permissions:\s*\n(.*?)(?=^[A-Za-z_-]+:\s*(?:\n|$))", text)
    return match.group(1) if match else ""


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


def _validate_auto_merge(rel: str, text: str, events: str, permissions: str) -> list[str]:
    errors: list[str] = []

    if "workflow_run:" not in events:
        errors.append(f"{rel}: auto-merge must trigger from workflow_run")
    for forbidden_event in ("pull_request:", "pull_request_target:", "push:", "schedule:"):
        if forbidden_event in events:
            errors.append(f"{rel}: auto-merge must not trigger on {forbidden_event[:-1]}")
    if "- CI" not in events:
        errors.append(f"{rel}: auto-merge must listen only to the CI workflow")

    if not re.search(r"^\s{2}contents:\s*write\s*$", permissions, re.MULTILINE):
        errors.append(f"{rel}: auto-merge requires contents: write")
    if not re.search(r"^\s{2}pull-requests:\s*read\s*$", permissions, re.MULTILINE):
        errors.append(f"{rel}: auto-merge requires pull-requests: read")
    if re.search(
        r"^\s{2}(actions|pull-requests|issues|packages|deployments):\s*write\s*$",
        permissions,
        re.MULTILINE,
    ):
        errors.append(f"{rel}: auto-merge may not request extra write permissions")

    required_markers = (
        "github.event.workflow_run.conclusion == 'success'",
        "github.event.workflow_run.event == 'pull_request'",
        "CI_HEAD_SHA: ${{ github.event.workflow_run.head_sha }}",
        "^chatgpt/linux-daily-[0-9]{3}-[0-9]{8}$",
        'test "${head_sha}" = "${CI_HEAD_SHA}"',
        "reviewDecision",
        "reviewThreads(first:100)",
        'test "${unresolved_threads}" = "0"',
        'test "${review_decision}" != "CHANGES_REQUESTED"',
        '"repos/${GITHUB_REPOSITORY}/pulls/${PR_NUMBER}/merge"',
        "-f merge_method=squash",
        '-f sha="${CI_HEAD_SHA}"',
    )
    for marker in required_markers:
        if marker not in text:
            errors.append(f"{rel}: auto-merge safety marker missing: {marker}")

    if "actions/checkout" in text:
        errors.append(f"{rel}: workflow_run auto-merge must not checkout PR code with a write token")
    if SELF_MUTATION_RE.search(text):
        errors.append(f"{rel}: auto-merge must not stage, commit, or push repository changes")
    if "--admin" in text:
        errors.append(f"{rel}: auto-merge must not bypass branch protection")
    if re.search(r"\bgh\s+pr\s+merge\b", text) or "enable-auto-merge" in text:
        errors.append(f"{rel}: use the exact-SHA REST merge gate, not gh pr merge/auto-merge")

    return errors


def _validate_materialize(rel: str, text: str, events: str, permissions: str) -> list[str]:
    """Workflow duy nhất được ghi lên feature branch.

    Nó tồn tại vì agent API-only không có Python runtime để chạy generator. Đổi lại,
    nó phải giữ đúng khuôn của release.yml: chỉ dispatch tường minh, có chuỗi xác
    nhận, và không bao giờ chạm tới main.
    """
    errors: list[str] = []

    if "workflow_dispatch:" not in events:
        errors.append(f"{rel}: materialize must use workflow_dispatch")
    for forbidden_event in ("push:", "pull_request:", "pull_request_target:", "schedule:", "workflow_run:"):
        if forbidden_event in events:
            errors.append(f"{rel}: materialize must not trigger on {forbidden_event[:-1]}")

    if not re.search(r"^\s{2}contents:\s*write\s*$", permissions, re.MULTILINE):
        errors.append(f"{rel}: materialize requires contents: write")
    if re.search(
        r"^\s{2}(actions|pull-requests|issues|packages|deployments):\s*write\s*$",
        permissions,
        re.MULTILINE,
    ):
        errors.append(f"{rel}: materialize may not request extra write permissions")

    required_markers = (
        # Cổng xác nhận phải là một bước fail được, không phải `if:` mức job:
        # job bị skip vẫn cho workflow run báo thành công.
        'test "${CONFIRM}" = "materialize-artifacts"',
        "^chatgpt/linux-daily-[0-9]{3}-[0-9]{8}$",
        "tools/materialize_guard.py --branch",
        "--changed-from-git",
        "tools/publish.py prepare",
        "tools/publish.py check",
        'git push origin "HEAD:${BRANCH}"',
    )
    for marker in required_markers:
        if marker not in text:
            errors.append(f"{rel}: materialize safety marker missing: {marker}")

    if re.search(r"^\s{4}if:.*inputs\.confirm", text, re.MULTILINE):
        errors.append(
            f"{rel}: confirm gate must be a failing step, not a job-level `if:` "
            "(a skipped job still reports the run as successful)"
        )
    if re.search(r"\bgit\s+add\s+(?:-A\b|--all\b|\.(?:\s|$))", text):
        errors.append(f"{rel}: materialize must stage explicit paths, not whole directories")
    if "ref: main" in text or re.search(r'HEAD:\s*["\']?main', text):
        errors.append(f"{rel}: materialize must never target main")

    return errors


def validate_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    rel = _display_path(path)
    errors: list[str] = []
    events = _event_block(text)
    permissions = _permissions_block(text)
    is_release = path.name == RELEASE_WORKFLOW
    is_auto_merge = path.name == AUTO_MERGE_WORKFLOW
    is_materialize = path.name == MATERIALIZE_WORKFLOW
    may_write = is_release or is_auto_merge or is_materialize

    if "pull_request_target:" in text:
        errors.append(f"{rel}: pull_request_target is forbidden")
    if not permissions:
        errors.append(f"{rel}: top-level permissions block is required")

    writes = WRITE_PERMISSION_RE.findall(permissions)
    if not may_write and writes:
        errors.append(
            f"{rel}: write permissions are forbidden outside {RELEASE_WORKFLOW}, "
            f"{AUTO_MERGE_WORKFLOW} and {MATERIALIZE_WORKFLOW}: {', '.join(writes)}"
        )
    if not may_write and not re.search(
        r"^\s{2}contents:\s*read\s*$", permissions, re.MULTILINE
    ):
        errors.append(f"{rel}: non-write workflow must declare contents: read")
    if not is_release and not is_materialize and SELF_MUTATION_RE.search(text):
        errors.append(f"{rel}: workflow must not stage, commit, or push repository changes")

    for banned in ("actions", "pull-requests", "issues", "packages", "deployments"):
        if re.search(rf"^\s{{2}}{re.escape(banned)}:\s*write\s*$", permissions, re.MULTILINE):
            errors.append(f"{rel}: {banned}: write is not allowed")

    if is_release:
        if "workflow_dispatch:" not in events:
            errors.append(f"{rel}: release must use workflow_dispatch")
        for forbidden_event in ("push:", "pull_request:", "schedule:", "workflow_run:"):
            if forbidden_event in events:
                errors.append(f"{rel}: release must not trigger on {forbidden_event[:-1]}")
        if not re.search(r"^\s{2}contents:\s*write\s*$", permissions, re.MULTILINE):
            errors.append(f"{rel}: release requires contents: write")
        if "Require explicit human confirmation" not in text:
            errors.append(f"{rel}: release explicit confirmation gate is missing")
        if "Block release unless CI and Production Smoke are green on this main SHA" not in text:
            errors.append(f"{rel}: release exact-main-SHA release gate is missing")
        if "ref: main" not in text:
            errors.append(f"{rel}: release checkout must pin main")

    if is_auto_merge:
        errors.extend(_validate_auto_merge(rel, text, events, permissions))

    if is_materialize:
        errors.extend(_validate_materialize(rel, text, events, permissions))

    errors.extend(_validate_dependency_install(rel, text))

    if path.name == CI_WORKFLOW:
        if "fetch-depth: 0" not in text:
            errors.append(f"{rel}: CI must fetch full PR history for hygiene validation")
        if "tools/pr_hygiene.py" not in text:
            errors.append(f"{rel}: CI must run PR commit/path hygiene")

    if not is_auto_merge and (
        re.search(r"\bgh\s+pr\s+merge\b", text) or "enable-auto-merge" in text
    ):
        errors.append(f"{rel}: automatic PR merge commands are forbidden")
    if "--admin" in text and ("gh pr" in text or "branch protection" in text.lower()):
        errors.append(f"{rel}: branch-protection bypass/admin merge is forbidden")

    return errors


def run() -> Report:
    report = Report()
    paths = sorted([*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")])
    for path in paths:
        report.checked += 1
        report.errors.extend(validate_file(path))
    if not paths:
        report.errors.append("no GitHub Actions workflows found")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = run()
    if report.errors:
        print(f"FAIL: workflow safety found {len(report.errors)} issue(s)")
        for error in report.errors:
            print(f"- {error}")
        return 1
    print(f"OK: workflow safety policy passed for {report.checked} workflow(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

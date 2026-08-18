"""Unit test cho materialize_guard: giới hạn phạm vi của workflow có contents: write."""
from __future__ import annotations

import materialize_guard
import pytest

DAILY = "chatgpt/linux-daily-048-20260818"


@pytest.mark.parametrize(
    "branch",
    [DAILY, "refs/heads/" + DAILY, "chatgpt/linux-daily-001-20260101"],
)
def test_daily_branch_is_accepted(branch: str):
    assert materialize_guard.validate_branch(branch) == []


@pytest.mark.parametrize(
    ("branch", "expected"),
    [
        ("main", "branch được bảo vệ"),
        ("master", "branch được bảo vệ"),
        ("refs/heads/main", "branch được bảo vệ"),
        ("", "cần tên branch"),
        ("   ", "cần tên branch"),
        ("chatgpt/linux-daily-48-20260818", "không khớp"),
        ("chatgpt/linux-daily-048-2026818", "không khớp"),
        ("claude/linux-daily-code-review", "không khớp"),
        ("chatgpt/linux-daily-048-20260818-extra", "không khớp"),
    ],
)
def test_unexpected_branch_is_rejected(branch: str, expected: str):
    errors = materialize_guard.validate_branch(branch)
    assert errors and expected in errors[0], errors


def test_generator_output_paths_are_allowed():
    """Đây đúng là 13 file mà publish.py prepare đã sinh cho bài #047."""
    assert materialize_guard.validate_changed_paths([
        "index.html",
        "archive.html",
        "feed.xml",
        "sitemap.xml",
        "search-index.json",
        "learning-paths.html",
        "learning-dashboard.html",
        "posts/post-047-socket-ownership-ss-lsof-sockstat-fstat.html",
        "posts/post-026-vmstat-systat-resource-pressure.html",
        "posts/post-033-process-tree-service-ownership.html",
        "docs/content-mix-report.md",
        "docs/distro-coverage-report.md",
        "docs/quality-dashboard.md",
    ]) == []


@pytest.mark.parametrize(
    "path",
    ["topics.md", "state.json", "site.json", "AGENTS.md", "STYLE.md", "VERSION", "pyproject.toml"],
)
def test_source_of_truth_is_protected(path: str):
    errors = materialize_guard.validate_changed_paths([path])
    assert errors and "source of truth" in errors[0], errors


@pytest.mark.parametrize(
    "path",
    [
        "tools/publish.py",
        "tools/materialize_guard.py",
        "tests/test_validate_repo.py",
        ".github/workflows/ci.yml",
        ".github/workflows/materialize-artifacts.yml",
        "templates/post.template.html",
        "assets/search.js",
        "labs/p9-linux-freebsd-interoperability/lab.json",
    ],
)
def test_tooling_and_ci_are_protected(path: str):
    """Workflow có contents: write không được tự sửa bộ kiểm định đang gác nó."""
    errors = materialize_guard.validate_changed_paths([path])
    assert errors and "tooling/CI" in errors[0], errors


def test_each_offending_path_is_reported_once():
    errors = materialize_guard.validate_changed_paths(
        ["index.html", "topics.md", "tools/publish.py", "feed.xml"]
    )
    assert len(errors) == 2

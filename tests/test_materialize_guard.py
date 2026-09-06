"""Unit test cho materialize_guard: giới hạn phạm vi của workflow có contents: write."""
from __future__ import annotations

import subprocess

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
    ["topics.md", "state.json", "site.json", "AGENTS.md", "STYLE.md", "VERSION", "pyproject.toml",
     "curriculum-plan.json", "coverage-catalog.json", "freshness.json", "learning-metadata.json",
     "learning-paths.json", "taxonomy.json"],
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


@pytest.mark.parametrize("path", ["new-source.json", "docs/CHATGPT-OPERATIONS.md", "setup.py",
                                 "../index.html", "/index.html", " index.html", "posts/new.py"])
def test_unknown_or_noncanonical_outputs_are_rejected(path):
    assert materialize_guard.validate_changed_paths([path])


@pytest.mark.parametrize("path", ["trang-2.html", "trang-10.html", "trang-100.html"])
def test_new_pagination_outputs_are_allowed(path):
    assert materialize_guard.validate_changed_paths([path]) == []


def test_git_rename_cannot_hide_removal_of_source_file(tmp_path, monkeypatch):
    def git(*args):
        return subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                               *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / "state.json").write_text('{"last_issue": 68}\n')
    git("add", "state.json")
    git("commit", "-qm", "Initial state")
    git("mv", "state.json", "search-index.json")
    monkeypatch.setattr(materialize_guard, "ROOT", tmp_path)
    paths = materialize_guard._changed_from_git()
    assert set(paths) == {"state.json", "search-index.json"}
    assert any("state.json" in error for error in materialize_guard.validate_changed_paths(paths))


def test_git_unicode_paths_do_not_escape_tooling_guard(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "kiểm tra.py").write_text("pass\n")
    monkeypatch.setattr(materialize_guard, "ROOT", tmp_path)
    paths = materialize_guard._changed_from_git()
    assert paths == ["tools/kiểm tra.py"]
    assert materialize_guard.validate_changed_paths(paths)


def test_symlink_cannot_be_committed_as_artifact(tmp_path, monkeypatch):
    (tmp_path / "index.html").symlink_to("state.json")
    monkeypatch.setattr(materialize_guard, "ROOT", tmp_path)
    monkeypatch.setattr(materialize_guard, "_changed_from_git", lambda: ["index.html"])
    assert materialize_guard.main(["--branch", DAILY, "--changed-from-git"]) == 1

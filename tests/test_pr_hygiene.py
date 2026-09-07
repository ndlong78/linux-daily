from pathlib import Path

import pr_hygiene

ROOT = Path(__file__).resolve().parents[1]


def test_descriptive_commit_subjects_pass():
    assert pr_hygiene.validate_subjects(
        [
            "Add PR commit and path hygiene guard",
            "Linux Daily #042: Lab service outage",
            "docs: clarify squash merge policy",
        ]
    ) == []


def test_junk_commit_subjects_are_rejected():
    errors = pr_hygiene.validate_subjects(
        ["x", "placeholder", "WIP: try finalizer", "tmp: debug"]
    )
    assert len(errors) == 4
    assert all("non-descriptive commit subject" in error for error in errors)


def test_temporary_and_finalizer_paths_are_rejected():
    errors = pr_hygiene.validate_paths(
        [
            "README.tmp",
            ".github/workflows/pr93-back-to-top-finalizer.yml",
            "tools/pr93_back_to_top.py",
            "notes/recovery.orig",
        ]
    )
    assert len(errors) == 4


def test_durable_repository_paths_are_allowed():
    assert pr_hygiene.validate_paths(
        [
            ".github/workflows/ci.yml",
            "tools/pr_preflight.py",
            "tools/workflow_safety.py",
            "posts/post-041-ansible-handlers-templates-idempotent-restart.html",
        ]
    ) == []


def test_protected_branch_is_rejected_for_local_preflight():
    assert pr_hygiene.validate_branch("main")
    assert pr_hygiene.validate_branch("master")
    assert pr_hygiene.validate_branch("chatgpt/pr94-git-ci-workflow-simplification") == []


def test_daily_branch_requires_current_base_as_ancestor():
    branch = "chatgpt/linux-daily-070-20260908"
    assert pr_hygiene.validate_daily_base(branch, base_is_ancestor=True) == []
    errors = pr_hygiene.validate_daily_base(branch, base_is_ancestor=False)
    assert len(errors) == 1
    assert "stale relative to the current PR base" in errors[0]
    assert "rematerialize" in errors[0]


def test_maintenance_branch_is_not_subject_to_daily_stale_base_gate():
    assert pr_hygiene.validate_daily_base(
        "maintenance/p1-daily-pr-gates-20260907",
        base_is_ancestor=False,
    ) == []


def test_remote_compare_mode_requires_branch_name():
    report = pr_hygiene.run(base="a" * 40, head="b" * 40)
    assert report.errors == ["--branch is required with --base/--head"]


def test_ci_passes_head_branch_to_remote_hygiene_gate():
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert '--branch "${{ github.event.pull_request.head.ref }}"' in text

import pr_hygiene


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

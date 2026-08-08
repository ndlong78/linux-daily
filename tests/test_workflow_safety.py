from pathlib import Path

import workflow_safety


def test_repository_workflows_pass_policy():
    report = workflow_safety.run()
    assert report.errors == []
    assert report.checked >= 1


def test_non_release_write_permission_is_rejected(tmp_path: Path):
    path = tmp_path / "unsafe.yml"
    path.write_text(
        "name: unsafe\non:\n  workflow_dispatch:\npermissions:\n  contents: write\njobs:\n  x:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    errors = workflow_safety.validate_file(path)
    assert any("write permissions are forbidden" in error for error in errors)


def test_pull_request_target_is_rejected(tmp_path: Path):
    path = tmp_path / "unsafe.yml"
    path.write_text(
        "name: unsafe\non:\n  pull_request_target:\npermissions:\n  contents: read\njobs:\n  x:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    errors = workflow_safety.validate_file(path)
    assert any("pull_request_target is forbidden" in error for error in errors)

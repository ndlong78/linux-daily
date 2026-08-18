"""Policy test cho materialize-artifacts.yml.

Đây là workflow duy nhất ngoài release.yml được phép ghi lên repository, nên mỗi
lớp bảo vệ của nó phải có test riêng: bỏ lớp nào ra thì policy phải đỏ.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import workflow_safety

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "materialize-artifacts.yml"


def _mutated(tmp_path: Path, old: str, new: str) -> list[str]:
    """Ghi bản workflow đã bị sửa vào tmp_path rồi trả về lỗi policy."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert old in text, f"không tìm thấy đoạn cần sửa: {old!r}"
    path = tmp_path / WORKFLOW.name
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return workflow_safety.validate_file(path)


def test_real_materialize_workflow_passes_policy():
    assert workflow_safety.validate_file(WORKFLOW) == []


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        pytest.param(
            "  workflow_dispatch:",
            "  pull_request:\n  workflow_dispatch:",
            "must not trigger on pull_request",
            id="tu-chay-theo-pull-request",
        ),
        pytest.param(
            "    if: inputs.confirm == 'materialize-artifacts'",
            "    if: always()",
            "safety marker missing",
            id="bo-cong-xac-nhan",
        ),
        pytest.param(
            'git push origin "HEAD:${BRANCH}"',
            'git push origin "HEAD:main"',
            "must never target main",
            id="push-thang-vao-main",
        ),
        pytest.param(
            "          ref: ${{ inputs.branch }}",
            "          ref: main",
            "must never target main",
            id="checkout-main",
        ),
        pytest.param(
            '--branch "${BRANCH}" --changed-from-git',
            '--branch "${BRANCH}"',
            "safety marker missing",
            id="bo-guard-pham-vi-thay-doi",
        ),
        pytest.param(
            "python tools/publish.py check",
            "echo skip",
            "safety marker missing",
            id="bo-buoc-verify",
        ),
        pytest.param(
            "permissions:\n  contents: write\n",
            "permissions:\n  contents: write\n  pull-requests: write\n",
            "may not request extra write permissions",
            id="xin-them-quyen-ghi",
        ),
        pytest.param(
            'git add -- "${entry:3}"',
            "git add -A",
            "must stage explicit paths",
            id="stage-ca-thu-muc",
        ),
    ],
)
def test_removing_a_safeguard_is_rejected(tmp_path: Path, old: str, new: str, expected: str):
    errors = _mutated(tmp_path, old, new)
    assert any(expected in error for error in errors), errors


def test_materialize_is_the_only_new_write_capable_workflow():
    """Nới quyền ghi phải giới hạn đúng ba workflow đã biết."""
    assert workflow_safety.MATERIALIZE_WORKFLOW == "materialize-artifacts.yml"
    write_capable = {
        workflow_safety.RELEASE_WORKFLOW,
        workflow_safety.AUTO_MERGE_WORKFLOW,
        workflow_safety.MATERIALIZE_WORKFLOW,
    }
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        if path.name in write_capable:
            continue
        text = path.read_text(encoding="utf-8")
        assert "contents: write" not in text, f"{path.name} không được có contents: write"

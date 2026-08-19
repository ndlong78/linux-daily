"""Policy test cho materialize-artifacts.yml.

Đây là workflow duy nhất ngoài release.yml được phép ghi lên repository, nên mỗi
lớp bảo vệ của nó phải có test riêng: bỏ lớp nào ra thì policy phải đỏ.
"""
from __future__ import annotations

import re
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
            '          test "${CONFIRM}" = "materialize-artifacts"',
            "          echo skip",
            "safety marker missing",
            id="bo-cong-xac-nhan",
        ),
        pytest.param(
            "  materialize:\n    runs-on: ubuntu-latest",
            "  materialize:\n    if: inputs.confirm == 'materialize-artifacts'\n    runs-on: ubuntu-latest",
            "confirm gate must be a failing step",
            id="cong-xac-nhan-quay-lai-dang-if-muc-job",
        ),
        pytest.param(
            'git push origin "HEAD:${BRANCH}"',
            'git push origin "HEAD:main"',
            "must never target main",
            id="push-thang-vao-main",
        ),
        pytest.param(
            "          ref: ${{ env.BRANCH }}",
            "          ref: main",
            "must never target main",
            id="checkout-main",
        ),
        pytest.param(
            '[[ "${resolved}" =~ ^chatgpt/linux-daily-[0-9]{3}-[0-9]{8}$ ]]',
            'true',
            "safety marker missing",
            id="bo-rang-buoc-pattern-branch-sau-discovery",
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


def test_branch_input_must_be_optional_so_rerun_works():
    """Connector của agent không expose `workflow_dispatch`, chỉ expose rerun.

    Rerun phát lại đúng inputs của run gốc. Nếu `branch` là input bắt buộc thì mọi
    lần rerun đều dựng lại branch của hôm trước — vô dụng cho nhịp 1 bài/ngày.
    Để trống thì workflow tự tìm branch theo state.json, nên rerun dùng được mọi ngày.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(r"^      branch:\n(?:.*\n)*?        required:\s*(\w+)", text, re.MULTILINE)
    assert match, "workflow phải khai input branch"
    assert match.group(1) == "false"


def test_required_branch_input_is_rejected_by_policy(tmp_path: Path):
    errors = _mutated(
        tmp_path,
        '        description: "Feature branch cụ thể; để trống để tự tìm theo state.json"\n        required: false',
        '        description: "Feature branch"\n        required: true',
    )
    assert any("required: false" in error for error in errors), errors


def test_discovery_reads_last_issue_from_default_branch():
    """Branch đích suy từ state.json, không suy từ 'ahead of main'.

    Squash-merge để lại branch cũ ahead of main vĩnh viễn, nên bộ lọc đó sẽ khớp
    nhầm branch đã merge xong.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert '"repos/${GITHUB_REPOSITORY}/contents/state.json"' in text
    assert "last_issue + 1" in text
    # từ chối khi không có hoặc có nhiều hơn một ứng viên
    assert 'test "${#found[@]}" -eq 0' in text
    assert 'test "${#found[@]}" -gt 1' in text


def test_confirm_gate_is_a_failing_step_not_a_skipped_job():
    """Job bị skip vẫn cho workflow run báo thành công.

    Nếu cổng xác nhận là `if:` mức job thì gõ sai chuỗi sẽ trông như dispatch
    thành công trong khi không có artifact nào được dựng — và bước kiểm bên trong
    không bao giờ chạy tới.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert not re.search(r"^\s{4}if:.*inputs\.confirm", text, re.MULTILINE)
    assert 'test "${CONFIRM}" = "materialize-artifacts"' in text


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

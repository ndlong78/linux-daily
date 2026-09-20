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
            "          ref: ${{ env.TARGET_SHA }}",
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
            # Materialize chỉ được có contents: write; mọi write scope khác bị cấm.
            "permissions:\n  contents: write\n",
            "permissions:\n  contents: write\n  actions: write\n",
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


def _without_comments(text: str) -> str:
    """Bỏ comment YAML trước khi quét quyền.

    Quét raw text bắt được cả `permissions:` mức job — điều mà chỉ parse block
    top-level sẽ bỏ lọt — nên giữ cách quét đó. Nhưng nó cũng bắt cả một dòng
    comment NÓI VỀ quyền, ví dụ "file này không có `contents: write`". Lọc comment
    giữ nguyên độ rộng của phép kiểm mà bỏ được kiểu dương tính giả đó.
    """
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def test_materialize_is_the_only_new_write_capable_workflow():
    """Nới quyền ghi NỘI DUNG phải giới hạn đúng ba workflow đã biết.

    `materialize-dispatch.yml` không nằm trong danh sách này và cũng không được
    có `contents: write`: nó chỉ có `actions: write` để gọi workflow_dispatch.
    Ranh giới cần giữ là workflow nào ghi được vào repository, nên nó vẫn phải
    qua phép kiểm này như mọi workflow read-only khác.
    """
    assert workflow_safety.MATERIALIZE_WORKFLOW == "materialize-artifacts.yml"
    write_capable = {
        workflow_safety.RELEASE_WORKFLOW,
        workflow_safety.AUTO_MERGE_WORKFLOW,
        workflow_safety.MATERIALIZE_WORKFLOW,
    }
    checked = 0
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        if path.name in write_capable:
            continue
        text = _without_comments(path.read_text(encoding="utf-8"))
        assert "contents: write" not in text, f"{path.name} không được có contents: write"
        checked += 1
    assert checked, "không quét được workflow nào — glob hỏng"


def test_comment_filter_still_catches_a_real_job_level_grant(tmp_path):
    """Phép lọc comment không được làm hỏng chính thứ nó phục vụ."""
    assert "contents: write" not in _without_comments("  # nói về contents: write\n")
    assert "contents: write" in _without_comments(
        "jobs:\n  x:\n    permissions:\n      contents: write\n"
    )


@pytest.mark.parametrize(("old", "new"), [
    ('persist-credentials: false', 'persist-credentials: true'),
    ('--trusted-ref "${TRUSTED_SHA}"', ''),
    ('git show "${TRUSTED_SHA}:tools/materialize_guard.py"', 'git show "HEAD:tools/materialize_guard.py"'),
    ('test "${GITHUB_REF}" = "refs/heads/main"', 'true'),
    ('test "$(git rev-parse HEAD)" = "${TARGET_SHA}"', 'true'),
    ('      - name: Cài dependency\n', '      - name: Cài dependency\n        env:\n          GH_TOKEN: ${{ github.token }}\n'),
])
def test_trusted_source_and_credential_boundaries_are_required(tmp_path, old, new):
    assert _mutated(tmp_path, old, new)


def test_source_guard_must_precede_dependency_installation(tmp_path):
    text = WORKFLOW.read_text()
    start = text.index('      - name: Validate source against trusted main')
    end = text.index('      - uses: actions/setup-python', start)
    step = text[start:end]
    text = text[:start] + text[end:]
    position = text.index('      - name: Guard branch')
    text = text[:position] + step + text[position:]
    path = tmp_path / WORKFLOW.name
    path.write_text(text)
    assert any('before dependency' in error for error in workflow_safety.validate_file(path))


# --- ranh giới PR: materialize không mở PR ---

@pytest.mark.parametrize("scope", ["actions", "pull-requests", "issues", "packages", "deployments"])
def test_materialize_rejects_every_extra_write_scope(tmp_path: Path, scope: str):
    """Ngoài contents: write, materialize không được có thêm quyền ghi nào."""
    errors = _mutated(
        tmp_path,
        "permissions:\n  contents: write\n",
        f"permissions:\n  contents: write\n  {scope}: write\n",
    )
    assert any("may not request extra write permissions" in err for err in errors), errors


def test_materialize_does_not_open_pull_requests():
    """PR phải do agent/owner connector mở sau khi materialize xanh."""
    text = WORKFLOW.read_text(encoding="utf-8")
    permissions = workflow_safety._permissions_block(text)
    assert not re.search(r"^\s{2}pull-requests:\s*write\s*$", permissions, re.MULTILINE)
    assert 'repos/${GITHUB_REPOSITORY}/pulls' not in text
    assert "Mở PR bài hằng ngày" not in text

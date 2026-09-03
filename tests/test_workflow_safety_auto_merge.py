from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import workflow_safety  # noqa: E402


def test_real_auto_merge_workflow_passes_safety_contract():
    path = ROOT / ".github" / "workflows" / workflow_safety.AUTO_MERGE_WORKFLOW
    assert workflow_safety.validate_file(path) == []


def test_auto_merge_workflow_is_exact_sha_and_no_checkout():
    path = ROOT / ".github" / "workflows" / workflow_safety.AUTO_MERGE_WORKFLOW
    text = path.read_text(encoding="utf-8")

    assert "actions/checkout" not in text
    assert "github.event.workflow_run.conclusion == 'success'" in text
    assert 'test "${head_sha}" = "${CI_HEAD_SHA}"' in text
    assert "-f merge_method=squash" in text
    assert '-f sha="${CI_HEAD_SHA}"' in text
    assert "--admin" not in text


def test_auto_merge_paginates_all_review_threads_and_fails_closed():
    text = (ROOT / ".github" / "workflows" / workflow_safety.AUTO_MERGE_WORKFLOW).read_text(
        encoding="utf-8"
    )

    assert "reviewThreads(first:100,after:$cursor)" in text
    assert "pageInfo{hasNextPage endCursor}" in text
    assert 'test "${has_next_page}" = "true"' in text
    assert 'test -n "${end_cursor}"' in text
    assert 'test "${end_cursor}" != "${previous_cursor}"' in text
    assert 'unresolved_threads="$(( unresolved_threads + page_unresolved ))"' in text


def test_auto_merge_policy_rejects_checkout_with_write_token(tmp_path):
    source = (
        ROOT / ".github" / "workflows" / workflow_safety.AUTO_MERGE_WORKFLOW
    ).read_text(encoding="utf-8")
    unsafe = source.replace(
        "    steps:\n",
        "    steps:\n      - uses: actions/checkout@v4\n",
        1,
    )
    path = tmp_path / workflow_safety.AUTO_MERGE_WORKFLOW
    path.write_text(unsafe, encoding="utf-8")

    errors = workflow_safety.validate_file(path)
    assert any("must not checkout PR code" in error for error in errors)


def test_auto_merge_policy_rejects_single_page_review_query(tmp_path: Path):
    errors = _mutated(
        tmp_path,
        "reviewThreads(first:100,after:$cursor)",
        "reviewThreads(first:100)",
    )
    assert any("safety marker missing" in error for error in errors), errors


def test_auto_merge_policy_requires_review_pagination_cursor_progress(tmp_path: Path):
    errors = _mutated(
        tmp_path,
        'test "${end_cursor}" != "${previous_cursor}"',
        "true",
    )
    assert any("safety marker missing" in error for error in errors), errors


# --- Dispatch xác thực sau merge ---

WORKFLOW = ROOT / ".github" / "workflows" / workflow_safety.AUTO_MERGE_WORKFLOW


def _mutated(tmp_path: Path, old: str, new: str) -> list[str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert old in text, f"không tìm thấy đoạn cần sửa: {old!r}"
    path = tmp_path / WORKFLOW.name
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return workflow_safety.validate_file(path)


def test_actions_write_is_required_not_merely_tolerated():
    """Gỡ quyền thì bước dispatch fail mỗi ngày — phải chặn ở policy, không chờ runtime."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "\n  actions: write\n" in text


def test_removing_actions_write_is_rejected(tmp_path: Path):
    errors = _mutated(tmp_path, "\n  actions: write\n", "\n")
    assert any("requires actions: write" in error for error in errors), errors


def test_dispatch_step_must_verify_the_run_actually_appeared(tmp_path: Path):
    """Endpoint dispatch trả 204 kể cả khi không có gì chạy.

    Bỏ vòng chờ + `exit 1` thì bước này xanh trong khi main vẫn thiếu CI —
    đúng kiểu hỏng im lặng mà cổng xác nhận của materialize từng mắc phải.
    """
    errors = _mutated(tmp_path, 'if test -z "${found}"; then', "if false; then")
    assert any("safety marker missing" in error for error in errors), errors


def test_dispatch_must_match_the_exact_merged_sha(tmp_path: Path):
    """Khớp 'run mới nhất' thay vì đúng SHA sẽ nhận nhầm run của push khác."""
    errors = _mutated(
        tmp_path,
        "head_sha=${merged_sha}&event=workflow_dispatch",
        "per_page=1",
    )
    assert any("safety marker missing" in error for error in errors), errors


def test_dispatch_step_cannot_be_removed_silently(tmp_path: Path):
    errors = _mutated(
        tmp_path,
        '"repos/${GITHUB_REPOSITORY}/actions/workflows/${wf}/dispatches"',
        '"repos/${GITHUB_REPOSITORY}/actions/workflows/noop"',
    )
    assert any("safety marker missing" in error for error in errors), errors


def test_actions_write_exception_does_not_leak_to_other_workflows(tmp_path: Path):
    """Ngoại lệ chỉ dành cho auto-merge, không mở cho workflow nào khác."""
    for name in ("ci.yml", "production-smoke.yml", workflow_safety.MATERIALIZE_WORKFLOW):
        source = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        assert "\n  actions: write\n" not in source, f"{name} không được có actions: write"

    unsafe = (ROOT / ".github" / "workflows" / workflow_safety.MATERIALIZE_WORKFLOW).read_text(
        encoding="utf-8"
    ).replace("permissions:\n  contents: write\n", "permissions:\n  contents: write\n  actions: write\n", 1)
    path = tmp_path / workflow_safety.MATERIALIZE_WORKFLOW
    path.write_text(unsafe, encoding="utf-8")
    errors = workflow_safety.validate_file(path)
    assert any("actions: write is not allowed" in error for error in errors), errors


def test_other_write_permissions_are_still_banned_on_auto_merge(tmp_path: Path):
    for perm in ("pull-requests", "issues", "packages", "deployments"):
        errors = _mutated(tmp_path, "\n  actions: write\n", f"\n  actions: write\n  {perm}: write\n")
        assert any("extra write permissions" in e or "is not allowed" in e for e in errors), (perm, errors)

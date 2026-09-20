"""Policy test cho materialize-dispatch.yml.

Đây là workflow duy nhất tự chạy theo `push` và là workflow thứ hai được chạm
`actions: write`. Giá trị của nó nằm ở những gì nó KHÔNG làm, nên mỗi ràng buộc
phải có test riêng: gỡ lớp nào ra thì policy phải đỏ.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import workflow_safety

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "materialize-dispatch.yml"
MATERIALIZE = ROOT / ".github" / "workflows" / "materialize-artifacts.yml"


def _mutated(tmp_path: Path, old: str, new: str) -> list[str]:
    """Ghi bản workflow đã bị sửa vào tmp_path rồi trả về lỗi policy."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert old in text, f"không tìm thấy đoạn cần sửa: {old!r}"
    path = tmp_path / WORKFLOW.name
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return workflow_safety.validate_file(path)


def test_real_dispatch_workflow_passes_policy():
    assert workflow_safety.validate_file(WORKFLOW) == []


def test_materialize_itself_still_refuses_push():
    """Tính chất cốt lõi: materialize vẫn chỉ chạy qua dispatch từ main.

    Nếu ai đó "đơn giản hoá" bằng cách thêm `push:` thẳng vào materialize, định
    nghĩa workflow sẽ được lấy từ branch vừa push thay vì từ main — branch tự
    quyết luật chạy của chính nó. Toàn bộ lý do materialize-dispatch.yml tồn tại
    là để điều đó không xảy ra.
    """
    assert workflow_safety.validate_file(MATERIALIZE) == []
    text = MATERIALIZE.read_text(encoding="utf-8")
    assert "push:" not in workflow_safety._event_block(text)


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        pytest.param(
            "    if: github.actor != 'github-actions[bot]'",
            "    # guard removed",
            "thiếu guard bắt buộc",
            id="bo-guard-chong-vong-lap",
        ),
        pytest.param(
            'ref: "main", inputs:',
            'ref: "refs/heads/foo", inputs:',
            "thiếu guard bắt buộc",
            id="dispatch-khong-lay-dinh-nghia-tu-main",
        ),
        pytest.param(
            'confirm: "materialize-artifacts"',
            'confirm: "whatever"',
            "thiếu guard bắt buộc",
            id="bo-chuoi-xac-nhan",
        ),
        pytest.param(
            '^chatgpt/linux-daily-[0-9]{3}-[0-9]{8}$',
            '^chatgpt/.*$',
            "thiếu guard bắt buộc",
            id="noi-long-regex-ten-branch",
        ),
        pytest.param(
            'test "${latest}" -gt "${before}"',
            "true",
            "thiếu guard bắt buộc",
            id="bo-buoc-xac-nhan-run-da-tao",
        ),
        pytest.param(
            '      - "chatgpt/linux-daily-*"',
            '      - "**"',
            "must filter push to daily article branches",
            id="chay-tren-moi-branch",
        ),
        pytest.param(
            "  actions: write",
            "  actions: write\n  contents: write",
            "may not request extra write permissions",
            id="xin-them-quyen-ghi-noi-dung",
        ),
        pytest.param(
            "  push:",
            "  pull_request:\n  push:",
            "must not trigger on pull_request",
            id="tu-chay-theo-pull-request",
        ),
        pytest.param(
            "  push:",
            "  workflow_run:\n  push:",
            "must not trigger on workflow_run",
            id="tu-chay-theo-workflow-run",
        ),
    ],
)
def test_policy_rejects_weakened_dispatch(tmp_path, old, new, expected):
    errors = _mutated(tmp_path, old, new)
    assert any(expected in err for err in errors), errors


def test_policy_rejects_checking_out_the_pushed_branch(tmp_path):
    """Không được chạy một dòng code nào của branch vừa push.

    Checkout là bước đầu tiên của con đường đó: sau khi có code branch trong
    workspace, mọi thứ chạy sau nó đều do branch quyết định.
    """
    errors = _mutated(
        tmp_path,
        "      - name: Dispatch Materialize Artifacts from main",
        "      - uses: actions/checkout@v4\n      - name: Dispatch Materialize Artifacts from main",
    )
    assert any("must not check out the pushed branch" in err for err in errors), errors


def test_policy_rejects_staging_or_pushing(tmp_path):
    """Dispatcher không có contents: write, nên mọi thao tác git là dấu hiệu sai thiết kế."""
    errors = _mutated(tmp_path, "          workflow=\"materialize-artifacts.yml\"", "          git push origin HEAD")
    assert any("must not stage, commit, or push" in err for err in errors), errors

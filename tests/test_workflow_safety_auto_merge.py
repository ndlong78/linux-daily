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

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import lab_contract  # noqa: E402


def _write_lab(
    path: Path,
    *,
    issue: int = 20,
    lab: dict | None = None,
    sections: list[str] | None = None,
) -> Path:
    meta = {
        "issue": issue,
        "date": "2026-08-09",
        "axis": "Ôn tập",
        "eyebrow": "Ôn tập · Advanced Lab",
        "slug": "advanced-lab-test",
        "title": "Advanced lab test",
        "lede": "Test contract",
    }
    if lab is not None:
        meta["lab"] = lab
    section_names = sections or [
        "scenario",
        "topology",
        "safety",
        "execution",
        "verification",
        "rollback",
        "cleanup",
    ]
    body = "".join(f'<section data-lab-section="{name}"></section>' for name in section_names)
    path.write_text(
        '<script type="application/json" id="ld-meta">\n'
        + json.dumps(meta, ensure_ascii=False)
        + "\n</script>\n"
        + body,
        encoding="utf-8",
    )
    return path


def _valid_lab(**overrides) -> dict:
    data = {
        "version": 1,
        "profile": "advanced",
        "topology": ["admin", "target"],
        "risks": ["lockout"],
        "rollback_required": True,
        "cleanup_required": True,
        "failure_injection": False,
        "verification": ["functional", "recovery"],
    }
    data.update(overrides)
    return data


def test_real_repository_keeps_historical_labs_as_legacy():
    report = lab_contract.review()
    assert report.errors == []
    assert report.total_labs == report.legacy_labs + report.enforced_labs
    assert report.legacy_labs == 2
    assert report.enforced_labs >= 1
    assert report.advanced_labs >= 1


def test_valid_advanced_lab_passes(tmp_path):
    path = _write_lab(tmp_path / "post-020-test.html", lab=_valid_lab())
    report = lab_contract.review([str(path)])
    assert report.errors == []
    assert report.enforced_labs == 1
    assert report.advanced_labs == 1
    assert report.risk_counts == {"lockout": 1}


def test_future_lab_without_contract_fails(tmp_path):
    path = _write_lab(tmp_path / "post-020-test.html", lab=None)
    report = lab_contract.review([str(path)])
    assert any("ld-meta.lab" in error for error in report.errors)


def test_failure_injection_requires_recovery_and_section(tmp_path):
    lab = _valid_lab(failure_injection=True, verification=["functional", "negative"])
    path = _write_lab(tmp_path / "post-020-test.html", lab=lab)
    report = lab_contract.review([str(path)])
    assert any("verification chứa 'recovery'" in error for error in report.errors)
    assert any("failure-injection" in error for error in report.errors)


def test_destructive_storage_requires_restore_evidence(tmp_path):
    lab = _valid_lab(risks=["destructive-storage"], verification=["functional", "recovery"])
    path = _write_lab(tmp_path / "post-020-test.html", lab=lab)
    report = lab_contract.review([str(path)])
    assert any("verification chứa 'restore'" in error for error in report.errors)


def test_material_risk_requires_rollback(tmp_path):
    lab = _valid_lab(rollback_required=False)
    path = _write_lab(tmp_path / "post-020-test.html", lab=lab)
    report = lab_contract.review([str(path)])
    assert any("rollback_required" in error for error in report.errors)


def test_advanced_lab_needs_two_topology_roles_and_two_verification_classes(tmp_path):
    lab = _valid_lab(topology=["target"], verification=["functional"])
    path = _write_lab(tmp_path / "post-020-test.html", lab=lab)
    report = lab_contract.review([str(path)])
    assert any("ít nhất 2 topology roles" in error for error in report.errors)
    assert any("ít nhất 2 verification classes" in error for error in report.errors)

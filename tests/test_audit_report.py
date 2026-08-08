from __future__ import annotations

from datetime import date

import audit_report


def test_offline_audit_is_deterministic_and_passes():
    first, code1 = audit_report.build(as_of=date(2026, 8, 8), github=False, production=False)
    second, code2 = audit_report.build(as_of=date(2026, 8, 8), github=False, production=False)
    assert first == second
    assert code1 == code2 == 0
    assert "Linux Daily — Audit Report" in first
    assert "Repository inventory" in first
    assert "P7 quality evidence" in first
    assert "P7 content quality: **ATTENTION**" in first
    assert "Production evidence" in first
    assert "Not requested" in first


def test_offline_audit_keeps_workflow_evidence_unknown():
    report, code = audit_report.build(as_of=date(2026, 8, 8), github=False, production=False)
    assert code == 0
    assert "| CI | **UNKNOWN** | `n/a` |" in report
    assert "| Production Smoke | **UNKNOWN** | `n/a` |" in report

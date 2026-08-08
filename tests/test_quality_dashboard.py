from __future__ import annotations

from datetime import date

import quality_dashboard


def test_repository_quality_dashboard_has_no_hard_errors():
    result = quality_dashboard.collect(as_of=date(2026, 8, 7))
    assert result["total_posts"] == 19
    assert result["errors"] == []
    assert result["status"] == "ATTENTION"
    assert result["signals"]["distro"]["status"] == "ATTENTION"
    assert result["signals"]["command"]["status"] == "PASS"
    assert result["signals"]["freshness"]["status"] == "PASS"
    assert result["signals"]["sources"]["status"] == "PASS"
    assert result["signals"]["sources"]["source_backed_posts"] == 19
    assert result["signals"]["sources"]["reviewed_source_posts"] == 19


def test_repository_quality_dashboard_surfaces_known_legacy_portability_debt():
    result = quality_dashboard.collect(as_of=date(2026, 8, 7))
    issues = {
        item["issue"]
        for item in result["remediation_queue"]
        if item["signal"] == "Distro portability"
    }
    assert issues == {7, 8, 10, 14, 17}
    assert all(item["severity"] == "ATTENTION" for item in result["remediation_queue"])


def test_dynamic_audit_date_can_surface_review_due_without_hard_failure():
    result = quality_dashboard.collect(as_of=date(2027, 2, 1))
    assert result["errors"] == []
    assert result["signals"]["freshness"]["review_due"] > 0
    assert result["signals"]["freshness"]["status"] == "ATTENTION"
    assert result["status"] == "ATTENTION"


def test_committed_dashboard_matches_canonical_snapshot():
    result = quality_dashboard.collect(as_of=quality_dashboard.canonical_as_of())
    expected = quality_dashboard.render_markdown(result)
    assert quality_dashboard.REPORT_PATH.read_text(encoding="utf-8") == expected

from __future__ import annotations

from datetime import date

import daily_operations_dashboard


def test_repository_dashboard_collects_all_p10_signals():
    result = daily_operations_dashboard.collect(as_of=date(2026, 8, 9))
    assert result["last_published_issue"] >= 21
    assert result["next_issue"] == result["last_published_issue"] + 1
    assert result["cadence_days"] == 1
    assert isinstance(result["cadence_due"], bool)
    assert result["next_topic"]["axis"]
    assert result["readiness_ready"] is True
    assert set(result["required_platforms"]) == {"ubuntu", "debian", "fedora", "freebsd"}
    assert result["minimum_primary_sources"] >= 2
    assert result["learning_covered"] == result["learning_posts"]
    assert result["coverage"]["capabilities"] >= result["coverage"]["covered"]
    assert result["errors"] == []


def test_render_exposes_operator_decision_points():
    result = daily_operations_dashboard.collect(as_of=date(2026, 8, 9))
    text = daily_operations_dashboard.render(result)
    assert "## Publication clock" in text
    assert "## Next planned topic" in text
    assert "## Review queue" in text
    assert "## Coverage recommendations" in text
    assert "Publication readiness" in text
    assert "Lifecycle" in text
    assert "derived view only" in text

from datetime import date

import operations_dashboard as dashboard


def test_freshness_thresholds():
    assert dashboard._freshness(0) == "FRESH"
    assert dashboard._freshness(2) == "FRESH"
    assert dashboard._freshness(3) == "ATTENTION"
    assert dashboard._freshness(4) == "ATTENTION"
    assert dashboard._freshness(5) == "STALE"


def test_collect_publication_matches_current_repository():
    publication = dashboard.collect_publication(date(2026, 8, 8))
    assert publication.issue == 19
    assert publication.published == date(2026, 8, 7)
    assert publication.age_days == 1
    assert publication.freshness == "FRESH"
    assert publication.title


def test_workflow_badges():
    success = dashboard.WorkflowState("CI", "completed", "success", "abc", "now", "url")
    running = dashboard.WorkflowState("CI", "in_progress", "pending", "abc", "now", "url")
    failed = dashboard.WorkflowState("CI", "completed", "failure", "abc", "now", "url")
    unknown = dashboard.WorkflowState("CI", "unknown", "unknown", "", "", "")

    assert dashboard._workflow_badge(success) == "PASS"
    assert dashboard._workflow_badge(running) == "RUNNING"
    assert dashboard._workflow_badge(failed) == "FAIL"
    assert dashboard._workflow_badge(unknown) == "UNKNOWN"


def test_render_dashboard_contains_required_operational_signals():
    publication = dashboard.Publication(
        issue=19,
        title="Example",
        published=date(2026, 8, 7),
        age_days=1,
        freshness="FRESH",
    )
    metrics = {
        "posts": 19,
        "generated_pages": 20,
        "technical_sources": 50,
        "social_code_images": 19,
        "woff2_fonts": 2,
        "rss_items": 19,
        "sitemap_urls": 20,
    }
    workflows = [
        dashboard.WorkflowState(
            "CI",
            "completed",
            "success",
            "0123456789abcdef",
            "2026-08-08T01:00:00Z",
            "https://github.example/ci",
        ),
        dashboard.WorkflowState(
            "Production Smoke",
            "completed",
            "success",
            "fedcba9876543210",
            "2026-08-08T01:30:00Z",
            "https://github.example/smoke",
        ),
    ]
    state = {"last_issue": 19, "last_published_date": "2026-08-07"}

    report = dashboard.render_dashboard(
        publication,
        metrics,
        [],
        workflows,
        date(2026, 8, 8),
        state,
    )

    assert "Operations Dashboard" in report
    assert "Publication freshness | **FRESH**" in report
    assert "Repository health | **PASS**" in report
    assert "CI | **PASS**" in report
    assert "Production Smoke | **PASS**" in report
    assert "`posts` | 19" in report
    assert "not a source of truth" in report


def test_offline_build_keeps_workflows_explicitly_unknown():
    report, exit_code = dashboard.build(as_of=date(2026, 8, 8), github=False)

    assert exit_code == 0
    assert "CI | **UNKNOWN**" in report
    assert "Production Smoke | **UNKNOWN**" in report
    assert "offline mode" in report

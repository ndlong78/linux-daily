from __future__ import annotations

import performance_budget


def test_budget_policy_has_explicit_limits():
    assert performance_budget.BUDGETS["homepage_html"] == 256 * 1024
    assert performance_budget.BUDGETS["post_html_each"] == 512 * 1024
    assert performance_budget.BUDGETS["social_image_each"] == 2 * 1024 * 1024


def test_current_repository_is_within_performance_budget():
    failures, metrics = performance_budget.collect()
    assert failures == []
    assert metrics["homepage_html"] > 0
    assert metrics["post_html_max"] > 0
    assert metrics["fonts_total"] > 0
    assert metrics["social_images_total"] > 0

from __future__ import annotations

from datetime import date

import content_freshness


def _policy(overrides=None):
    return {
        "version": 1,
        "effective_from_issue": 20,
        "review_windows_days": {"high": 90, "medium": 180, "low": 365},
        "axis_policy": {
            "Bảo mật": {"volatility": "high", "reason": "test"},
            "Networking": {"volatility": "medium", "reason": "test"},
        },
        "overrides": overrides or {},
    }


def _post(issue=20, published="2026-01-01", axis="Bảo mật", review_status="reviewed"):
    return {
        "issue": issue,
        "date": published,
        "axis": axis,
        "title": "synthetic",
        "review_status": review_status,
        "path": f"posts/post-{issue:03d}-synthetic.html",
    }


def test_real_repository_is_current_at_p7_3_baseline():
    result = content_freshness.review(as_of=date(2026, 8, 8))
    assert result["total"] >= 19
    assert result["errors"] == []
    assert result["counts"].get("review-due", 0) == 0
    assert result["counts"].get("historically-valid", 0) == 0
    assert result["counts"].get("current", 0) == result["total"]


def test_review_due_is_computed_from_clock_but_not_a_policy_error():
    result = content_freshness.review(
        as_of=date(2026, 4, 2), posts=[_post()], policy=_policy()
    )
    assert result["errors"] == []
    assert result["posts"][0]["review_due_on"] == "2026-04-01"
    assert result["posts"][0]["state"] == "review-due"
    assert len(result["review_due"]) == 1


def test_last_reviewed_override_resets_review_window():
    policy = _policy({"20": {"last_reviewed": "2026-03-15"}})
    result = content_freshness.review(
        as_of=date(2026, 4, 2), posts=[_post()], policy=policy
    )
    assert result["errors"] == []
    assert result["posts"][0]["last_reviewed"] == "2026-03-15"
    assert result["posts"][0]["state"] == "current"


def test_historically_valid_requires_explicit_reason():
    policy = _policy({"20": {"state": "historically-valid"}})
    result = content_freshness.review(
        as_of=date(2026, 4, 2), posts=[_post()], policy=policy
    )
    assert any("override.reason" in problem for problem in result["errors"])


def test_historically_valid_preserves_history_with_reason_and_replacement():
    posts = [_post(issue=20), _post(issue=21, published="2026-02-01")]
    policy = _policy(
        {
            "20": {
                "state": "historically-valid",
                "reason": "Giữ để giải thích workflow cũ; guidance mới ở #021.",
                "replacement_issue": 21,
            }
        }
    )
    result = content_freshness.review(as_of=date(2026, 8, 8), posts=posts, policy=policy)
    assert result["errors"] == []
    assert result["posts"][0]["state"] == "historically-valid"
    assert result["posts"][0]["replacement_issue"] == 21


def test_override_for_missing_issue_is_a_hard_policy_error():
    result = content_freshness.review(
        as_of=date(2026, 8, 8),
        posts=[_post()],
        policy=_policy({"999": {"last_reviewed": "2026-08-01"}}),
    )
    assert any("issue không tồn tại" in problem for problem in result["errors"])


def test_new_content_must_be_reviewed_or_published():
    result = content_freshness.review(
        as_of=date(2026, 8, 8), posts=[_post(review_status="draft")], policy=_policy()
    )
    assert any("review_status=reviewed/published" in problem for problem in result["errors"])

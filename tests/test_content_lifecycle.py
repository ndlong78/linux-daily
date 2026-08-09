from __future__ import annotations

from datetime import date

import content_lifecycle


def _post(issue: int) -> dict:
    return {
        "issue": issue,
        "date": f"2026-01-{issue - 19:02d}",
        "axis": "Bảo mật",
        "title": f"synthetic {issue}",
        "review_status": "reviewed",
        "path": f"posts/post-{issue:03d}-synthetic.html",
    }


def _policy(overrides: dict) -> dict:
    return {
        "version": 1,
        "effective_from_issue": 20,
        "review_windows_days": {"high": 90, "medium": 180, "low": 365},
        "axis_policy": {"Bảo mật": {"volatility": "high", "reason": "test"}},
        "overrides": overrides,
    }


def test_repository_lifecycle_baseline_is_valid():
    result = content_lifecycle.analyze(as_of=date(2026, 8, 9))
    assert result["errors"] == []
    assert result["posts"] >= 21


def test_superseded_chain_resolves_to_latest_canonical_issue():
    posts = [_post(20), _post(21), _post(22)]
    policy = _policy(
        {
            "20": {
                "state": "superseded",
                "reason": "Guidance mới hơn ở #021.",
                "replacement_issue": 21,
            },
            "21": {
                "state": "superseded",
                "reason": "Guidance mới hơn ở #022.",
                "replacement_issue": 22,
            },
        }
    )
    result = content_lifecycle.analyze(as_of=date(2026, 2, 1), posts=posts, policy=policy)
    assert result["errors"] == []
    lineage = next(item for item in result["replacement_lineages"] if item["source_issue"] == 20)
    assert lineage["chain"] == [20, 21, 22]
    assert lineage["canonical_issue"] == 22


def test_replacement_cannot_point_backwards():
    posts = [_post(20), _post(21)]
    policy = _policy(
        {
            "21": {
                "state": "superseded",
                "reason": "invalid backward target",
                "replacement_issue": 20,
            }
        }
    )
    result = content_lifecycle.analyze(as_of=date(2026, 2, 1), posts=posts, policy=policy)
    assert any("phải mới hơn issue nguồn" in problem for problem in result["errors"])


def test_replacement_chain_must_end_at_canonical_guidance():
    posts = [_post(20), _post(21)]
    policy = _policy(
        {
            "20": {
                "state": "superseded",
                "reason": "replaced by historical explanation",
                "replacement_issue": 21,
            },
            "21": {
                "state": "historically-valid",
                "reason": "Chỉ giữ để giải thích lịch sử.",
            },
        }
    )
    result = content_lifecycle.analyze(as_of=date(2026, 2, 1), posts=posts, policy=policy)
    assert any("không phải canonical guidance" in problem for problem in result["errors"])

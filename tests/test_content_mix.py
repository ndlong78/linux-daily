from __future__ import annotations

import content_mix


def test_real_repository_mix_is_balanced_and_in_sequence():
    result = content_mix.review()
    assert result["posts"] >= 19
    assert result["spread"] <= 1
    assert result["unknown_axes"] == []
    assert result["sequence_errors"] == []
    assert content_mix.errors(result) == []


def test_next_axis_follows_canonical_rotation():
    result = content_mix.review()
    assert result["next_issue"] == 20
    assert result["next_axis"] == "Automation"
    assert result["complete_cycles"] == 2
    assert result["cycle_remainder"] == 5


def test_report_matches_committed_snapshot():
    expected = content_mix.render_report()
    assert content_mix.REPORT_PATH.read_text(encoding="utf-8") == expected


def test_sequence_drift_is_a_hard_error():
    posts = [
        {"issue": 1, "date": "2026-07-02", "axis": "Networking", "title": "one"},
        {"issue": 2, "date": "2026-07-04", "axis": "Storage", "title": "two"},
    ]
    result = content_mix.review(posts)
    assert result["sequence_errors"]
    assert content_mix.errors(result)

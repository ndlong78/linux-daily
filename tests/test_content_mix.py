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
    posts = content_mix.collect()
    result = content_mix.review(posts)
    axis_order = result["axis_order"]
    assert result["next_issue"] == posts[-1]["issue"] + 1
    assert result["next_axis"] == axis_order[len(posts) % len(axis_order)]
    assert result["complete_cycles"] == len(posts) // len(axis_order)
    assert result["cycle_remainder"] == len(posts) % len(axis_order)


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

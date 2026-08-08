from __future__ import annotations

from pathlib import Path

import learning_paths


def _posts(count: int = 4) -> dict[int, dict]:
    return {
        issue: {
            "issue": issue,
            "title": f"Post {issue}",
            "date": f"2026-07-{issue:02d}",
            "axis": "Networking",
            "eyebrow": "Networking · Test",
            "href": f"posts/post-{issue:03d}-test.html",
        }
        for issue in range(1, count + 1)
    }


def _config(steps: list[int]) -> dict:
    return {
        "version": 1,
        "paths": [
            {
                "slug": "test-path",
                "title": "Test path",
                "goal": "A useful learning goal.",
                "audience": "Sysadmins.",
                "steps": steps,
            }
        ],
    }


def _learning_config(count: int) -> dict:
    return {
        "version": 1,
        "posts": [
            {"issue": issue, "difficulty": "basic", "prerequisites": []}
            for issue in range(1, count + 1)
        ],
    }


def test_real_repo_learning_paths_cover_every_post():
    result = learning_paths.review()
    assert result["errors"] == []
    assert len(result["paths"]) == 4
    assert len(result["posts"]) == 19
    assert len(result["assigned_issues"]) == 19
    assert result["unassigned_issues"] == []
    assert result["learning"]["difficulty_counts"] == {"basic": 8, "intermediate": 11}
    assert result["learning"]["prerequisite_edges"] == 16
    assert {path["slug"] for path in result["paths"]} == {
        "server-foundations",
        "network-security",
        "storage-backup",
        "automation-operations",
    }


def test_committed_page_matches_generator():
    result = learning_paths.review()
    expected = learning_paths.render_page(result)
    current = Path(learning_paths.OUTPUT_PATH).read_text(encoding="utf-8")
    assert current == expected


def test_unknown_issue_is_rejected():
    result = learning_paths.review(
        config=_config([1, 2, 99]),
        posts=_posts(2),
        learning_config=_learning_config(2),
    )
    assert any("issue không tồn tại #099" in error for error in result["errors"])


def test_duplicate_step_is_rejected():
    result = learning_paths.review(
        config=_config([1, 1, 2]),
        posts=_posts(2),
        learning_config=_learning_config(2),
    )
    assert any("#001 bị lặp" in error for error in result["errors"])


def test_unassigned_post_is_rejected():
    result = learning_paths.review(
        config=_config([1, 2, 3]),
        posts=_posts(4),
        learning_config=_learning_config(4),
    )
    assert any("#004" in error and "chưa phủ" in error for error in result["errors"])


def test_structured_inventory_reports_coverage_and_learning_metadata():
    result = learning_paths.review()
    payload = learning_paths.structured(result)
    assert payload["path_count"] == 4
    assert payload["post_count"] == payload["assigned_post_count"] == 19
    assert payload["difficulty_counts"] == {"basic": 8, "intermediate": 11}
    assert payload["prerequisite_edges"] == 16
    assert payload["errors"] == []

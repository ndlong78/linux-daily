from __future__ import annotations

import learning_metadata


def _posts(count: int = 3) -> dict[int, dict]:
    return {
        issue: {
            "issue": issue,
            "title": f"Post {issue}",
            "href": f"posts/post-{issue:03d}-test.html",
        }
        for issue in range(1, count + 1)
    }


def _config(entries: list[dict]) -> dict:
    return {"version": 1, "posts": entries}


def test_real_repo_learning_metadata_is_complete_and_acyclic():
    result = learning_metadata.review()
    assert result["errors"] == []
    assert len(result["posts"]) == len(result["metadata"]) == 19
    assert result["difficulty_counts"] == {"basic": 8, "intermediate": 11}
    assert result["prerequisite_edges"] == 16
    assert 10 in result["metadata"][3]["prerequisites"]


def test_missing_post_metadata_is_rejected():
    config = _config([
        {"issue": 1, "difficulty": "basic", "prerequisites": []},
        {"issue": 2, "difficulty": "basic", "prerequisites": []},
    ])
    result = learning_metadata.review(config=config, posts=_posts(3))
    assert any("#003" in error and "chưa phủ" in error for error in result["errors"])


def test_unknown_prerequisite_is_rejected():
    config = _config([
        {"issue": 1, "difficulty": "basic", "prerequisites": [99]},
        {"issue": 2, "difficulty": "intermediate", "prerequisites": []},
    ])
    result = learning_metadata.review(config=config, posts=_posts(2))
    assert any("prerequisite" in error and "#099" in error for error in result["errors"])


def test_self_and_duplicate_prerequisites_are_rejected():
    config = _config([
        {"issue": 1, "difficulty": "basic", "prerequisites": [1]},
        {"issue": 2, "difficulty": "intermediate", "prerequisites": [1, 1]},
    ])
    result = learning_metadata.review(config=config, posts=_posts(2))
    assert any("không thể phụ thuộc chính nó" in error for error in result["errors"])
    assert any("prerequisite #001 bị lặp" in error for error in result["errors"])


def test_prerequisite_cycle_is_rejected():
    config = _config([
        {"issue": 1, "difficulty": "basic", "prerequisites": [2]},
        {"issue": 2, "difficulty": "intermediate", "prerequisites": [1]},
    ])
    result = learning_metadata.review(config=config, posts=_posts(2))
    assert any("prerequisite graph có cycle" in error for error in result["errors"])


def test_invalid_difficulty_is_rejected():
    config = _config([
        {"issue": 1, "difficulty": "expert", "prerequisites": []},
    ])
    result = learning_metadata.review(config=config, posts=_posts(1))
    assert any("difficulty" in error and "expert" in error for error in result["errors"])

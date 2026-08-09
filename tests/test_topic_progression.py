from __future__ import annotations

import topic_progression


def _result(steps: list[dict], *, difficulty_counts: dict[str, int] | None = None) -> dict:
    return {
        "paths": [
            {
                "slug": "test-path",
                "title": "Test path",
                "steps": steps,
            }
        ],
        "posts": {int(step["issue"]): step for step in steps},
        "learning": {
            "difficulty_counts": difficulty_counts
            or {"basic": 1, "intermediate": 1, "advanced": 1}
        },
        "errors": [],
    }


def _step(
    issue: int,
    position: int,
    difficulty: str,
    prerequisites: list[int] | None = None,
) -> dict:
    return {
        "issue": issue,
        "position": position,
        "difficulty": difficulty,
        "prerequisites": [
            {"issue": prerequisite, "title": f"Post {prerequisite}"}
            for prerequisite in (prerequisites or [])
        ],
    }


def test_real_repo_progression_has_no_hard_findings():
    result = topic_progression.review()
    assert result["status"] == "PASS"
    assert result["path_count"] == 4
    assert result["post_count"] >= 20
    assert result["hard_findings"] == []
    assert result["total_prerequisite_references"] == (
        result["local_prerequisite_references"]
        + result["external_prerequisite_references"]
    )
    assert result["missing_difficulty_tiers"] == []


def test_prerequisite_after_dependent_is_hard_failure():
    path_result = _result(
        [
            _step(1, 1, "basic"),
            _step(2, 2, "intermediate", [3]),
            _step(3, 3, "intermediate"),
        ]
    )
    result = topic_progression.review(path_result)
    assert result["status"] == "FAIL"
    assert any(
        finding["code"] == "prerequisite-after-dependent"
        for finding in result["hard_findings"]
    )


def test_external_prerequisite_is_informational_not_failure():
    path_result = _result(
        [_step(1, 1, "basic"), _step(2, 2, "intermediate", [99])]
    )
    result = topic_progression.review(path_result)
    assert result["status"] == "PASS"
    assert result["hard_findings"] == []
    assert result["external_prerequisite_references"] == 1
    assert result["external_prerequisites"][0]["prerequisite"] == 99


def test_basic_to_advanced_adjacent_jump_is_hard_failure():
    path_result = _result([_step(1, 1, "basic"), _step(2, 2, "advanced")])
    result = topic_progression.review(path_result)
    assert result["status"] == "FAIL"
    assert any(
        finding["code"] == "difficulty-jump"
        for finding in result["hard_findings"]
    )


def test_missing_tier_is_attention_not_hard_failure():
    path_result = _result(
        [_step(1, 1, "basic"), _step(2, 2, "intermediate")],
        difficulty_counts={"basic": 1, "intermediate": 1, "advanced": 0},
    )
    result = topic_progression.review(path_result)
    assert result["status"] == "ATTENTION"
    assert result["missing_difficulty_tiers"] == ["advanced"]
    assert result["hard_findings"] == []

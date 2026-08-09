"""Regression tests cho Publication Readiness Gate."""

import importlib

publication_readiness = importlib.import_module("publication_readiness")


def base_plan(topic: dict) -> dict:
    return {
        "version": 1,
        "policy": {
            "planning_horizon_days": 1,
            "readiness": {
                "required_platforms": ["ubuntu", "debian", "fedora", "freebsd"],
                "minimum_primary_sources": 2,
                "semantic_similarity_block_threshold": 0.72,
            },
        },
        "topics": [topic],
    }


def test_similarity_detects_identical_topic():
    assert publication_readiness.similarity("DNS troubleshooting", "DNS troubleshooting") == 1.0


def test_unknown_prerequisite_is_rejected(monkeypatch):
    monkeypatch.setattr(
        publication_readiness.curriculum_planner,
        "validate",
        lambda plan, posts: [],
    )
    plan = base_plan(
        {
            "axis": "Networking",
            "topic": "DNS troubleshooting nâng cao",
            "difficulty": "intermediate",
            "goal": "Chẩn đoán DNS theo từng lớp resolver.",
            "prerequisites": [99],
        }
    )
    posts = [{"issue": 1, "axis": "Networking", "title": "Static IP"}]
    errors = publication_readiness.validate(plan, posts)
    assert any("chưa publish" in error for error in errors)


def test_advanced_topic_requires_prerequisite(monkeypatch):
    monkeypatch.setattr(
        publication_readiness.curriculum_planner,
        "validate",
        lambda plan, posts: [],
    )
    plan = base_plan(
        {
            "axis": "Ôn tập",
            "topic": "Lab sự cố DNS end to end",
            "difficulty": "advanced",
            "goal": "Khôi phục sự cố DNS có verification và rollback.",
            "prerequisites": [],
        }
    )
    errors = publication_readiness.validate(plan, [])
    assert any("advanced topic phải có prerequisite" in error for error in errors)


def test_repository_readiness_is_clean():
    assert publication_readiness.validate() == []

from __future__ import annotations

import importlib

coverage_intelligence = importlib.import_module("coverage_intelligence")


def capability(capability_id: str = "net-dns") -> dict:
    return {
        "id": capability_id,
        "axis": "Networking",
        "topic": "DNS troubleshooting",
        "difficulty": "intermediate",
        "keywords": ["dns", "dig", "resolver"],
        "rationale": "DNS evidence is required for reliable troubleshooting.",
    }


def test_repository_catalog_is_valid():
    assert coverage_intelligence.validate() == []


def test_uncovered_unplanned_capability_is_recommended(monkeypatch):
    monkeypatch.setattr(
        coverage_intelligence.taxonomy,
        "load_taxonomy",
        lambda: {"axes": {"Networking": {}}},
    )
    catalog = {
        "version": 1,
        "policy": {"minimum_keyword_hits": 2, "recommendation_limit": 3},
        "capabilities": [capability()],
    }
    posts = [{"issue": 1, "axis": "Networking", "title": "ip route basics", "lede": "gateway table"}]
    plan = {"topics": []}
    result = coverage_intelligence.analyze(catalog, posts, plan)
    assert result["gaps"] == 1
    assert result["recommendations"][0]["id"] == "net-dns"
    assert "1 bài" in result["recommendations"][0]["reason"]


def test_planned_capability_is_not_recommended(monkeypatch):
    monkeypatch.setattr(
        coverage_intelligence.taxonomy,
        "load_taxonomy",
        lambda: {"axes": {"Networking": {}}},
    )
    catalog = {
        "version": 1,
        "policy": {"minimum_keyword_hits": 2, "recommendation_limit": 3},
        "capabilities": [capability()],
    }
    plan = {"topics": [{"topic": "DNS với dig và resolver"}]}
    result = coverage_intelligence.analyze(catalog, [], plan)
    assert result["planned"] == 1
    assert result["gaps"] == 0
    assert result["recommendations"] == []


def test_two_keyword_hits_mark_capability_covered(monkeypatch):
    monkeypatch.setattr(
        coverage_intelligence.taxonomy,
        "load_taxonomy",
        lambda: {"axes": {"Networking": {}}},
    )
    catalog = {
        "version": 1,
        "policy": {"minimum_keyword_hits": 2, "recommendation_limit": 3},
        "capabilities": [capability()],
    }
    posts = [{"issue": 2, "axis": "Networking", "title": "DNS resolver triage", "lede": "service failure"}]
    result = coverage_intelligence.analyze(catalog, posts, {"topics": []})
    assert result["covered"] == 1
    assert result["gaps"] == 0

from __future__ import annotations

from pathlib import Path

import learning_dashboard


def test_real_repo_learning_dashboard_baseline():
    result = learning_dashboard.collect()
    assert result["errors"] == []
    assert result["status"] == "PASS"
    assert result["post_count"] == result["covered_post_count"]
    assert result["post_count"] >= 20
    assert result["path_count"] == 4
    assert sum(result["difficulty_counts"].values()) == result["post_count"]
    assert result["difficulty_counts"].get("advanced", 0) >= 1
    assert result["prerequisite_edges"] >= 20
    assert result["path_prerequisite_references"] == (
        result["local_prerequisites"] + result["external_prerequisites"]
    )
    assert result["hard_findings"] == 0
    assert result["missing_difficulty_tiers"] == []
    assert {path["slug"] for path in result["paths"]} == {
        "server-foundations",
        "network-security",
        "storage-backup",
        "automation-operations",
    }


def test_committed_dashboard_matches_renderer():
    result = learning_dashboard.collect()
    expected = learning_dashboard.render_page(result)
    current = Path(learning_dashboard.OUTPUT_PATH).read_text(encoding="utf-8")
    assert current == expected


def test_dashboard_links_to_every_learning_path_anchor():
    result = learning_dashboard.collect()
    page = learning_dashboard.render_page(result)
    for path in result["paths"]:
        assert f'learning-paths.html#{path["slug"]}' in page
    assert 'href="index.html"' in page
    assert 'href="archive.html"' in page

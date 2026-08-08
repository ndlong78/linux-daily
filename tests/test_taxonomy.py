from __future__ import annotations

import taxonomy


def test_taxonomy_has_unique_slugs_and_required_axes():
    data = taxonomy.load_taxonomy()
    axes = data["axes"]
    slugs = [cfg["slug"] for cfg in axes.values()]
    assert len(slugs) == len(set(slugs))
    assert {"Networking", "Bảo mật", "Storage", "Công cụ mới", "Monitoring", "Automation", "Ôn tập"} <= set(axes)


def test_all_current_posts_are_classified():
    errors, axes, tags = taxonomy.collect()
    assert errors == []
    assert sum(axes.values()) >= 19
    assert len(axes) >= 7
    assert tags


def test_report_is_deterministic_and_human_readable():
    first = taxonomy.report()
    second = taxonomy.report()
    assert first == second
    assert "Taxonomy & Topic Discovery" in first
    assert "Networking" in first

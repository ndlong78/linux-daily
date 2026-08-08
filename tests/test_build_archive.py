from __future__ import annotations

import html
import json

import build_archive


def test_search_index_covers_all_posts_and_is_deterministic():
    first = build_archive.render_search_index()
    second = build_archive.render_search_index()
    assert first == second
    payload = json.loads(first)
    assert payload["schema"] == 1
    assert payload["count"] == len(payload["posts"])
    assert payload["count"] >= 19
    assert payload["posts"][0]["issue"] > payload["posts"][-1]["issue"]


def test_search_index_contains_discovery_fields():
    payload = json.loads(build_archive.render_search_index())
    post = payload["posts"][0]
    assert {"issue", "date", "axis", "axis_label", "axis_slug", "tags", "title", "lede", "href"} <= set(post)
    assert post["href"].startswith("posts/post-")


def test_archive_has_search_accessibility_and_all_axes():
    archive = build_archive.render_archive()
    assert 'role="search"' in archive
    assert 'aria-live="polite"' in archive
    assert 'id="archive-search"' in archive
    assert 'search-index.json' not in archive  # loaded by external JS, not duplicated inline
    for group in build_archive.taxonomy.load_taxonomy()["axes"].values():
        assert html.escape(group["label"]) in archive

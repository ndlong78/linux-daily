"""Tests cho source-backed technical quality gate."""
import json

import validate_sources
from validate_sources import Report, validate_post_sources


def _post_html(issue=19, status="reviewed", sources=None, visible_sources=None):
    if sources is None:
        sources = [
            {"title": "Official A", "url": "https://example.com/a", "kind": "official"},
            {"title": "Upstream B", "url": "https://example.org/b", "kind": "upstream"},
        ]
    if visible_sources is None:
        visible_sources = sources
    meta = {
        "issue": issue,
        "date": "2026-08-09",
        "axis": "Monitoring",
        "eyebrow": "Monitoring · Demo",
        "slug": "demo",
        "title": "Demo",
        "lede": "Demo lede",
        "review_status": status,
        "sources": sources,
    }
    links = "\n".join(
        f'<li><a href="{s["url"]}">{s["title"]}</a></li>' for s in visible_sources
    )
    return f"""<!doctype html>
<html><head>
<script type="application/json" id="ld-meta">{json.dumps(meta)}</script>
</head><body>
<section class="sources" aria-labelledby="technical-sources">
<h2 id="technical-sources">Nguồn kỹ thuật</h2><ul>{links}</ul>
</section>
</body></html>"""


def _check(tmp_path, html, issue=19):
    path = tmp_path / f"post-{issue:03d}-demo.html"
    path.write_text(html, encoding="utf-8")
    report = Report()
    validate_post_sources(str(path), report)
    return report.errors


def test_historical_post_without_source_metadata_is_grandfathered(tmp_path):
    assert _check(tmp_path, "<html></html>", issue=18) == []


def test_historical_post_with_valid_source_metadata_is_checked_and_passes(tmp_path):
    assert _check(tmp_path, _post_html(issue=13), issue=13) == []


def test_historical_opt_in_missing_sources_fails(tmp_path):
    html = _post_html(issue=16).replace('"sources": [', '"sources_old": [', 1)
    errors = _check(tmp_path, html, issue=16)
    assert any("meta.sources" in e for e in errors)


def test_historical_opt_in_draft_status_fails(tmp_path):
    errors = _check(tmp_path, _post_html(issue=13, status="draft"), issue=13)
    assert any("technical review" in e for e in errors)


def test_valid_sources_pass(tmp_path):
    assert _check(tmp_path, _post_html()) == []


def test_draft_status_fails_merge_gate(tmp_path):
    errors = _check(tmp_path, _post_html(status="draft"))
    assert any("technical review" in e for e in errors)


def test_missing_sources_array_fails(tmp_path):
    html = _post_html().replace('"sources": [', '"sources_old": [', 1)
    errors = _check(tmp_path, html)
    assert any("meta.sources" in e for e in errors)


def test_requires_two_primary_sources(tmp_path):
    sources = [{"title": "Only", "url": "https://example.com/a", "kind": "official"}]
    errors = _check(tmp_path, _post_html(sources=sources))
    assert any("ít nhất 2" in e for e in errors)


def test_rejects_non_https_source(tmp_path):
    sources = [
        {"title": "A", "url": "http://example.com/a", "kind": "official"},
        {"title": "B", "url": "https://example.org/b", "kind": "upstream"},
    ]
    errors = _check(tmp_path, _post_html(sources=sources))
    assert any("HTTPS" in e for e in errors)


def test_rejects_duplicate_url(tmp_path):
    sources = [
        {"title": "A", "url": "https://example.com/a", "kind": "official"},
        {"title": "B", "url": "https://example.com/a", "kind": "upstream"},
    ]
    errors = _check(tmp_path, _post_html(sources=sources))
    assert any("bị lặp" in e for e in errors)


def test_visible_sources_must_match_metadata(tmp_path):
    sources = [
        {"title": "A", "url": "https://example.com/a", "kind": "official"},
        {"title": "B", "url": "https://example.org/b", "kind": "upstream"},
    ]
    visible = [sources[1], sources[0]]
    errors = _check(tmp_path, _post_html(sources=sources, visible_sources=visible))
    assert any("không khớp" in e for e in errors)


def test_missing_visible_source_section_fails(tmp_path):
    html = _post_html().replace('class="sources"', 'class="references"')
    errors = _check(tmp_path, html)
    assert any("section" in e and "sources" in e for e in errors)


def test_run_checks_new_and_historical_opt_in_posts(tmp_path):
    (tmp_path / "post-018-old.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "post-013-demo.html").write_text(_post_html(issue=13), encoding="utf-8")
    (tmp_path / "post-019-demo.html").write_text(_post_html(), encoding="utf-8")
    assert validate_sources.run(str(tmp_path)).errors == []

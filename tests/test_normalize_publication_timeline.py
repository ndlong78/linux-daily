"""Tests for the bounded #001..#021 historical timeline migration."""
from __future__ import annotations

import json
from datetime import date

import normalize_publication_timeline as timeline


def _post(issue: int, date_s: str) -> str:
    visible = date.fromisoformat(date_s).strftime("%d·%m·%Y")
    return f'''<!doctype html>
<html><head>
<script type="application/json" id="ld-meta">
{{
  "issue": {issue},
  "date": "{date_s}",
  "axis": "Networking",
  "eyebrow": "Networking",
  "slug": "fixture",
  "title": "Fixture",
  "lede": "Fixture"
}}
</script>
</head><body>
<span class="issue">#{issue:03d} · {visible}</span>
</body></html>
'''


def test_target_dates_are_contiguous():
    assert timeline.target_date(1).isoformat() == "2026-07-01"
    assert timeline.target_date(21).isoformat() == "2026-07-21"


def test_render_post_changes_only_metadata_and_visible_date(tmp_path):
    path = tmp_path / "post-001-fixture.html"
    path.write_text(_post(1, "2026-07-02"), encoding="utf-8")
    entry = timeline.TimelineEntry(
        issue=1,
        path=path,
        current_date=date(2026, 7, 2),
        target_date=date(2026, 7, 1),
    )

    rendered = timeline.render_post(entry)

    assert '"date": "2026-07-01"' in rendered
    assert "#001 · 01·07·2026" in rendered
    assert "2026-07-02" not in rendered
    assert "#001 · 02·07·2026" not in rendered


def test_discover_requires_complete_historical_issue_set(tmp_path, monkeypatch):
    posts = tmp_path / "posts"
    posts.mkdir()
    for issue in range(1, 22):
        old_date = date(2026, 7, 1 + min((issue - 1) * 2, 30)).isoformat()
        if issue >= 17:
            old_date = date(2026, 8, min(1 + (issue - 16) * 2, 9)).isoformat()
        (posts / f"post-{issue:03d}-fixture.html").write_text(
            _post(issue, old_date), encoding="utf-8"
        )
    monkeypatch.setattr(timeline, "POST_DIR", posts)

    entries = timeline.discover_entries()

    assert [entry.issue for entry in entries] == list(range(1, 22))
    assert entries[0].target_date.isoformat() == "2026-07-01"
    assert entries[-1].target_date.isoformat() == "2026-07-21"


def test_apply_rewrites_posts_and_state(tmp_path, monkeypatch):
    posts = tmp_path / "posts"
    posts.mkdir()
    for issue in range(1, 22):
        path = posts / f"post-{issue:03d}-fixture.html"
        path.write_text(_post(issue, f"2026-08-{issue:02d}"), encoding="utf-8")

    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps(
            {
                "last_issue": 21,
                "last_published_date": "2026-08-09",
                "last_generated_at": "2026-08-09T01:30:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(timeline, "POST_DIR", posts)
    monkeypatch.setattr(timeline, "STATE_PATH", state_path)

    entries = timeline.discover_entries()
    timeline.apply(entries)

    refreshed = timeline.discover_entries()
    assert timeline.verify(refreshed) == []
    assert '"date": "2026-07-01"' in (posts / "post-001-fixture.html").read_text(
        encoding="utf-8"
    )
    assert '"date": "2026-07-21"' in (posts / "post-021-fixture.html").read_text(
        encoding="utf-8"
    )
    assert json.loads(state_path.read_text(encoding="utf-8")) == {
        "last_issue": 21,
        "last_published_date": "2026-07-21",
        "last_generated_at": "2026-07-21T00:00:00+00:00",
    }

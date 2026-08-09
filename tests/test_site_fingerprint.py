from __future__ import annotations

from pathlib import Path

import site_fingerprint
import socialmeta

ROOT = Path(__file__).resolve().parents[1]


def _latest_issue() -> int:
    return max(
        int(path.name.split("-")[1])
        for path in (ROOT / "posts").glob("post-*.html")
    )


def test_served_files_cover_public_operational_surface():
    paths = [public_path for public_path, _ in site_fingerprint.served_files()]
    latest_issue = _latest_issue()
    expected_preview = f"/{socialmeta.image_relpath(latest_issue)}"
    assert paths[:4] == ["/", "/feed.xml", "/sitemap.xml", "/robots.txt"]
    assert any(path.startswith(f"/posts/post-{latest_issue:03d}-") for path in paths)
    assert expected_preview in paths


def test_fingerprint_is_deterministic_and_complete():
    first, files = site_fingerprint.collect()
    second, files_again = site_fingerprint.collect()

    assert first == second
    assert len(first) == 64
    assert files == files_again
    assert len(files) == 6
    assert all(len(item.sha256) == 64 for item in files)
    assert all(item.size > 0 for item in files)


def test_manifest_exposes_latest_issue_without_commit_sha_coupling():
    data = site_fingerprint.manifest()
    assert data["schema"] == 1
    assert data["latest_issue"] == _latest_issue()
    assert data["fingerprint"]
    assert len(data["files"]) == 6

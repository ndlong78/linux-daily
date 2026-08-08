from __future__ import annotations

import site_fingerprint


def test_served_files_cover_public_operational_surface():
    paths = [public_path for public_path, _ in site_fingerprint.served_files()]
    assert paths[:4] == ["/", "/feed.xml", "/sitemap.xml", "/robots.txt"]
    assert any(path.startswith("/posts/post-019-") for path in paths)
    assert "/posts/social/post-019-code.png" in paths


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
    assert data["latest_issue"] == 19
    assert data["fingerprint"]
    assert len(data["files"]) == 6

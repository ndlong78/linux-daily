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


# --- /robots.txt bị edge viết lại: có trong manifest, ngoài hash tổng ---


def test_robots_is_declared_edge_managed_and_actually_served():
    assert site_fingerprint.EDGE_MANAGED_PATHS == frozenset({"/robots.txt"})
    served = {public_path for public_path, _ in site_fingerprint.served_files()}
    assert site_fingerprint.EDGE_MANAGED_PATHS <= served, (
        "path edge-managed phải là path thật đang phục vụ, nếu không nó không loại được gì"
    )


def test_fingerprinted_files_drops_only_the_edge_managed_paths():
    served = [public_path for public_path, _ in site_fingerprint.served_files()]
    fingerprinted = [public_path for public_path, _ in site_fingerprint.fingerprinted_files()]

    assert fingerprinted == [p for p in served if p not in site_fingerprint.EDGE_MANAGED_PATHS]
    assert "/robots.txt" not in fingerprinted
    assert len(fingerprinted) == len(served) - 1


def test_robots_stays_in_manifest_so_containment_still_has_bytes():
    """Loại khỏi hash tổng, nhưng vẫn phải liệt kê — checker cần bytes để so containment."""
    _, files = site_fingerprint.collect()
    assert "/robots.txt" in {item.public_path for item in files}
    assert len(files) == 6


def test_robots_bytes_really_are_excluded_from_the_aggregate():
    """Dựng lại hash tổng có kèm robots và khẳng định nó KHÁC hash thật.

    Nếu một ngày ai đó bỏ nhánh loại trừ trong collect(), test này đỏ thay vì để
    production-smoke đỏ vĩnh viễn vì một khác biệt hợp lệ ở edge.
    """
    actual, _ = site_fingerprint.collect()

    with_robots = site_fingerprint.hashlib.sha256()
    for public_path, path in site_fingerprint.served_files():
        with_robots.update(public_path.encode("utf-8"))
        with_robots.update(b"\0")
        with_robots.update(path.read_bytes())
        with_robots.update(b"\0")

    assert actual != with_robots.hexdigest()


def test_aggregate_equals_hash_over_fingerprinted_files_only():
    actual, _ = site_fingerprint.collect()

    rebuilt = site_fingerprint.hashlib.sha256()
    for public_path, path in site_fingerprint.fingerprinted_files():
        rebuilt.update(public_path.encode("utf-8"))
        rebuilt.update(b"\0")
        rebuilt.update(path.read_bytes())
        rebuilt.update(b"\0")

    assert actual == rebuilt.hexdigest()

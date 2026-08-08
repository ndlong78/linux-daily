from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import check_production  # noqa: E402


def test_latest_post_path_is_highest_issue():
    path = Path(check_production._latest_post_path())
    assert path.name.startswith("post-019-")


def test_site_origin_is_cloudflare_public_domain():
    site = check_production._load_site()
    assert site["url"] == "https://linux.no.id.vn/"


def test_expected_content_type_policy_is_explicit():
    errors: list[str] = []
    check_production._expect_type("text/html", {"text/html"}, "homepage", errors)
    check_production._expect_type("application/rss+xml", {"application/rss+xml", "application/xml"}, "feed", errors)
    assert errors == []


def test_content_type_strips_charset():
    assert check_production._content_type({"content-type": "text/html; charset=utf-8"}) == "text/html"


def test_wrong_content_type_is_reported():
    errors: list[str] = []
    check_production._expect_type("text/plain", {"text/html"}, "homepage", errors)
    assert len(errors) == 1
    assert "homepage" in errors[0]


def test_public_static_cache_rejects_private_or_no_store():
    errors: list[str] = []
    warnings: list[str] = []
    check_production._cache_observation(
        "homepage",
        {"cache-control": "private, no-store"},
        errors,
        warnings,
    )
    assert len(errors) == 1
    assert "unsafe cache-control" in errors[0]
    assert warnings == []


def test_missing_cache_control_is_observability_warning_not_gate_failure():
    errors: list[str] = []
    warnings: list[str] = []
    check_production._cache_observation("homepage", {}, errors, warnings)
    assert errors == []
    assert warnings == ["homepage: cache-control header missing"]


def test_expected_fingerprint_maps_to_served_paths():
    fingerprint, expected = check_production._expected_by_public_path()
    assert len(fingerprint) == 64
    assert "/" in expected
    assert "/feed.xml" in expected
    assert any(path.startswith("/posts/post-019-") for path in expected)

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import check_production  # noqa: E402
import site_fingerprint  # noqa: E402
import socialmeta  # noqa: E402


def _latest_post() -> Path:
    return max(
        (ROOT / "posts").glob("post-*.html"),
        key=lambda path: int(path.name.split("-")[1]),
    )


def test_latest_post_path_is_highest_issue():
    path = Path(check_production._latest_post_path())
    assert path == _latest_post()


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
    assert f"/posts/{_latest_post().name}" in expected


# --- Regression: social preview khi social output đang tạm dừng ---


def test_social_endpoint_uses_shared_fallback_not_per_issue_guess():
    """Bài mới không có preview riêng — checker phải theo socialmeta, không tự suy ra.

    Trước đây checker hardcode posts/social/post-<issue>-code.png nên với bài #047
    nó đòi một file chưa từng tồn tại và luôn 404, làm production-smoke đỏ vì một
    chính sách dự án đã bỏ ("social output tạm dừng").
    """
    latest = int(Path(check_production._latest_post_path()).name.split("-")[1])
    relpath = socialmeta.image_relpath(latest)

    assert relpath != socialmeta.dedicated_image_relpath(latest)
    assert not (ROOT / socialmeta.dedicated_image_relpath(latest)).exists()
    assert (ROOT / relpath).is_file()


def test_social_url_matches_rendered_og_image_of_latest_post():
    """URL checker yêu cầu phải đúng bằng og:image mà bài thật sự render."""
    latest_path = Path(check_production._latest_post_path())
    latest = int(latest_path.name.split("-")[1])
    site = check_production._load_site()
    expected_url = urljoin(site["url"], socialmeta.image_relpath(latest))

    match = re.search(
        r'<meta property="og:image" content="([^"]+)"',
        latest_path.read_text(encoding="utf-8"),
    )
    assert match, "bài mới nhất phải có og:image"
    assert match.group(1) == expected_url


def test_social_asset_is_covered_by_the_fingerprint_contract():
    """Đường dẫn social phải nằm trong tập file được fingerprint theo dõi,
    nếu không thì nó thoát khỏi kiểm tra content drift."""
    latest = int(Path(check_production._latest_post_path()).name.split("-")[1])
    _, files = site_fingerprint.collect()
    served = {item.public_path for item in files}
    assert f"/{socialmeta.image_relpath(latest)}" in served

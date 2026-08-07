from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import validate_site  # noqa: E402


def test_website_seo_gate_passes_on_real_repo():
    report = validate_site.run()
    assert report.errors == [], "Website/SEO gate còn lỗi:\n" + "\n".join(report.errors)


def test_stale_public_host_policy_is_explicit():
    assert validate_site.STALE_PUBLIC_HOSTS == {"ndlong78.github.io"}


def test_site_inventory_is_homepage_plus_all_posts():
    report = validate_site.Report()
    site = validate_site._site()
    paths = [validate_site.INDEX_PATH, *sorted((ROOT / "posts").glob("post-*.html"))]
    canonicals = [
        validate_site._page_canonical(str(path), site, report)
        for path in paths
    ]
    assert report.errors == []
    assert None not in canonicals
    assert len(canonicals) == len(set(canonicals))

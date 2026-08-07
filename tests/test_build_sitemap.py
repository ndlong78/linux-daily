import json
import xml.etree.ElementTree as ET
from pathlib import Path

from tools import build_sitemap

ROOT = Path(__file__).resolve().parents[1]
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def test_sitemap_matches_generator():
    rendered, count = build_sitemap.render_sitemap()
    assert (ROOT / "sitemap.xml").read_text(encoding="utf-8") == rendered
    assert count == 20


def test_sitemap_uses_custom_domain_and_latest_post():
    root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    urls = root.findall("sm:url", NS)
    locs = [u.findtext("sm:loc", namespaces=NS) for u in urls]
    assert locs[0] == "https://linux.no.id.vn/"
    assert "https://linux.no.id.vn/posts/post-019-triage-hieu-nang-vmstat-iostat.html" in locs
    assert all(loc.startswith("https://linux.no.id.vn/") for loc in locs)


def test_robots_matches_generator_and_sitemap():
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    assert robots == build_sitemap.render_robots()
    assert "Sitemap: https://linux.no.id.vn/sitemap.xml" in robots


def test_site_config_uses_cloudflare_worker_public_url():
    site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    assert site["url"] == "https://linux.no.id.vn/"
    assert not (ROOT / "CNAME").exists()

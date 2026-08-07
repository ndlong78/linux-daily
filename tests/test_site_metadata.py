from __future__ import annotations

import os
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import build_index  # noqa: E402


class HeadMetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.meta = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "link":
            self.links.append(data)
        elif tag == "meta":
            self.meta.append(data)


def _parse(text: str) -> HeadMetaParser:
    parser = HeadMetaParser()
    parser.feed(text)
    return parser


def test_homepage_has_canonical_og_and_rss_autodiscovery():
    rendered, count = build_index.render_index()
    assert count == 19
    parser = _parse(rendered)

    assert {"rel": "canonical", "href": "https://linux.no.id.vn/"} in parser.links
    assert {
        "rel": "alternate",
        "type": "application/rss+xml",
        "title": "Linux Daily RSS",
        "href": "https://linux.no.id.vn/feed.xml",
    } in parser.links

    props = {m.get("property"): m.get("content") for m in parser.meta if m.get("property")}
    assert props["og:type"] == "website"
    assert props["og:url"] == "https://linux.no.id.vn/"
    assert props["og:site_name"] == "Linux Daily"
    assert props["og:locale"] == "vi_VN"
    assert props["og:title"]
    assert props["og:description"]


def test_post_template_requires_discovery_metadata_placeholders():
    template = (ROOT / "templates" / "post.template.html").read_text(encoding="utf-8")
    assert 'rel="canonical" href="{{CANONICAL_URL}}"' in template
    assert 'type="application/rss+xml"' in template
    assert 'href="{{FEED_URL}}"' in template
    assert 'property="og:type" content="article"' in template
    assert 'property="og:url" content="{{CANONICAL_URL}}"' in template
    assert 'property="og:title"' in template
    assert 'property="og:description"' in template


def test_committed_homepage_matches_generator():
    rendered, _ = build_index.render_index()
    assert (ROOT / "index.html").read_text(encoding="utf-8") == rendered

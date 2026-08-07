from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)

import build_feed  # noqa: E402


def test_committed_feed_is_current():
    rendered, count = build_feed.render_feed()
    with open(build_feed.FEED_PATH, encoding="utf-8") as f:
        committed = f.read()

    assert committed == rendered
    assert count == build_feed.MAX_ITEMS


def test_feed_is_valid_rss_with_absolute_permalinks():
    rendered, count = build_feed.render_feed()
    root = ET.fromstring(rendered)

    assert root.tag == "rss"
    channel = root.find("channel")
    assert channel is not None

    items = channel.findall("item")
    assert len(items) == count == 10
    assert channel.findtext("language") == "vi"

    first = items[0]
    assert first.findtext("pubDate") == "Fri, 07 Aug 2026 00:00:00 +0700"
    assert first.findtext("link", "").startswith("https://")
    assert first.findtext("guid") == first.findtext("link")

    for item in items:
        assert item.findtext("link", "").startswith("https://")
        assert item.findtext("guid") == item.findtext("link")
        assert item.findtext("title")
        assert item.findtext("description")

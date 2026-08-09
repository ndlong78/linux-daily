from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import build_index  # noqa: E402
import postmeta  # noqa: E402
import socialmeta  # noqa: E402


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


def _properties(parser: HeadMetaParser) -> dict[str, str | None]:
    return {
        item.get("property"): item.get("content")
        for item in parser.meta
        if item.get("property")
    }


def _named(parser: HeadMetaParser) -> dict[str, str | None]:
    return {
        item.get("name"): item.get("content")
        for item in parser.meta
        if item.get("name")
    }


def _posts() -> list[Path]:
    return sorted(
        (ROOT / "posts").glob("post-*.html"),
        key=lambda path: int(path.name.split("-")[1]),
    )


def test_homepage_has_canonical_og_rss_and_social_preview():
    rendered, count = build_index.render_index()
    posts = _posts()
    assert count == len(posts)
    parser = _parse(rendered)

    assert {"rel": "canonical", "href": "https://linux.no.id.vn/"} in parser.links
    assert {
        "rel": "alternate",
        "type": "application/rss+xml",
        "title": "Linux Daily RSS",
        "href": "https://linux.no.id.vn/feed.xml",
    } in parser.links

    props = _properties(parser)
    assert props["og:type"] == "website"
    assert props["og:url"] == "https://linux.no.id.vn/"
    assert props["og:site_name"] == "Linux Daily"
    assert props["og:locale"] == "vi_VN"
    assert props["og:title"]
    assert props["og:description"]

    latest_path = posts[-1]
    latest = postmeta.read_meta(str(latest_path))
    issue = int(latest["issue"])
    social = socialmeta.image_info(issue, latest["title"], "https://linux.no.id.vn/")
    assert props["og:image"] == social["url"]
    assert props["og:image:type"] == "image/png"
    assert props["og:image:width"] == str(social["width"])
    assert props["og:image:height"] == str(social["height"])
    assert props["og:image:alt"] == social["alt"]

    named = _named(parser)
    assert named["twitter:card"] == "summary_large_image"
    assert named["twitter:image"] == social["url"]
    assert named["twitter:image:alt"] == social["alt"]


def test_all_historical_posts_have_canonical_og_rss_and_social_preview():
    posts = _posts()
    assert posts

    for path in posts:
        text = path.read_text(encoding="utf-8")
        parser = _parse(text)
        meta = postmeta.read_meta(str(path))
        issue = int(meta["issue"])
        canonical = f"https://linux.no.id.vn/posts/{path.name}"
        social = socialmeta.image_info(issue, meta["title"], "https://linux.no.id.vn/")

        canonicals = [link for link in parser.links if link.get("rel") == "canonical"]
        assert canonicals == [{"rel": "canonical", "href": canonical}], path.name

        feeds = [
            link
            for link in parser.links
            if link.get("rel") == "alternate" and link.get("type") == "application/rss+xml"
        ]
        assert feeds == [
            {
                "rel": "alternate",
                "type": "application/rss+xml",
                "title": "Linux Daily RSS",
                "href": "https://linux.no.id.vn/feed.xml",
            }
        ], path.name

        props = _properties(parser)
        assert props["og:type"] == "article", path.name
        assert props["og:url"] == canonical, path.name
        assert props["og:site_name"] == "Linux Daily", path.name
        assert props["og:locale"] == "vi_VN", path.name
        assert props["og:title"] == meta["title"], path.name
        assert props["og:description"] == meta["lede"], path.name
        assert props["og:image"] == social["url"], path.name
        assert props["og:image:type"] == "image/png", path.name
        assert props["og:image:width"] == str(social["width"]), path.name
        assert props["og:image:height"] == str(social["height"]), path.name
        assert props["og:image:alt"] == social["alt"], path.name

        named = _named(parser)
        assert named["twitter:card"] == "summary_large_image", path.name
        assert named["twitter:title"] == meta["title"], path.name
        assert named["twitter:description"] == meta["lede"], path.name
        assert named["twitter:image"] == social["url"], path.name
        assert named["twitter:image:alt"] == social["alt"], path.name


def test_post_template_requires_discovery_and_social_metadata_placeholders():
    template = (ROOT / "templates" / "post.template.html").read_text(encoding="utf-8")
    assert 'rel="canonical" href="{{CANONICAL_URL}}"' in template
    assert 'type="application/rss+xml"' in template
    assert 'href="{{FEED_URL}}"' in template
    assert 'property="og:type" content="article"' in template
    assert 'property="og:url" content="{{CANONICAL_URL}}"' in template
    assert 'property="og:image" content="{{SOCIAL_IMAGE_URL}}"' in template
    assert 'property="og:image:width" content="{{SOCIAL_IMAGE_WIDTH}}"' in template
    assert 'property="og:image:height" content="{{SOCIAL_IMAGE_HEIGHT}}"' in template
    assert 'property="og:image:alt" content="{{SOCIAL_IMAGE_ALT}}"' in template
    assert 'name="twitter:card" content="summary_large_image"' in template
    assert 'name="twitter:image" content="{{SOCIAL_IMAGE_URL}}"' in template


def test_committed_homepage_matches_generator():
    rendered, _ = build_index.render_index()
    assert (ROOT / "index.html").read_text(encoding="utf-8") == rendered

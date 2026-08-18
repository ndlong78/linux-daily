#!/usr/bin/env python3
"""Production observability checks for the Cloudflare-hosted Linux Daily site."""
from __future__ import annotations

import argparse
import glob
import json
import os
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import site_fingerprint
import socialmeta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_CONFIG = os.path.join(ROOT, "site.json")
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")
USER_AGENT = "linux-daily-production-smoke/2.0"


@dataclass
class CheckResult:
    ok: bool
    errors: list[str]
    warnings: list[str]
    expected_fingerprint: str = ""
    production_fingerprint: str = ""


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self.meta: list[dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "link":
            self.links.append(data)
        elif tag == "meta":
            self.meta.append(data)


def _load_site() -> dict:
    with open(SITE_CONFIG, encoding="utf-8") as f:
        site = json.load(f)
    site["url"] = site["url"].rstrip("/") + "/"
    return site


def _latest_post_path() -> str:
    posts = sorted(glob.glob(POSTS_GLOB))
    if not posts:
        raise RuntimeError("repository không có post HTML")
    return max(posts, key=lambda p: int(os.path.basename(p).split("-")[1]))


def _fetch(url: str, timeout: float) -> tuple[int, dict[str, str], bytes, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = int(resp.status)
        headers = {k.lower(): v for k, v in resp.headers.items()}
        body = resp.read()
        final_url = resp.geturl()
    return status, headers, body, final_url


def _content_type(headers: dict[str, str]) -> str:
    return headers.get("content-type", "").split(";", 1)[0].strip().lower()


def _expect_type(actual: str, allowed: set[str], label: str, errors: list[str]) -> None:
    if actual not in allowed:
        errors.append(f"{label}: content-type {actual!r}, expected one of {sorted(allowed)}")


def _parse_html(body: bytes) -> HeadParser:
    parser = HeadParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    return parser


def _cache_observation(label: str, headers: dict[str, str], errors: list[str], warnings: list[str]) -> None:
    """Validate only unsafe cache semantics; keep provider-specific hints observable, not flaky."""
    cache_control = headers.get("cache-control", "").lower()
    directives = {part.strip().split("=", 1)[0] for part in cache_control.split(",") if part.strip()}
    if "private" in directives or "no-store" in directives:
        errors.append(f"{label}: static public response has unsafe cache-control {cache_control!r}")
    if not cache_control:
        warnings.append(f"{label}: cache-control header missing")


def _expected_by_public_path() -> tuple[str, dict[str, tuple[str, bytes]]]:
    fingerprint, files = site_fingerprint.collect()
    expected: dict[str, tuple[str, bytes]] = {}
    for item in files:
        path = os.path.join(ROOT, item.repository_path.replace("/", os.sep))
        expected[item.public_path] = (item.sha256, open(path, "rb").read())
    return fingerprint, expected


def _production_fingerprint(responses_by_path: dict[str, bytes]) -> str:
    aggregate = site_fingerprint.hashlib.sha256()
    for public_path, _ in site_fingerprint.served_files():
        if public_path not in responses_by_path:
            return ""
        aggregate.update(public_path.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(responses_by_path[public_path])
        aggregate.update(b"\0")
    return aggregate.hexdigest()


def _check_once(timeout: float = 12.0) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    site = _load_site()
    base = site["url"]
    origin = urlparse(base).netloc
    latest_local = _latest_post_path()
    latest_name = os.path.basename(latest_local)
    latest_url = urljoin(base, f"posts/{latest_name}")
    latest_issue = int(latest_name.split("-")[1])
    # Social output đang tạm dừng nên bài mới không có preview riêng; socialmeta trả về
    # asset lịch sử mới nhất làm fallback. Dùng đúng helper mà site_fingerprint và
    # build_index dùng, thay vì tự suy ra post-<issue>-code.png — bài #047 sẽ 404.
    social_relpath = socialmeta.image_relpath(latest_issue)
    image_url = urljoin(base, social_relpath)

    expected_fingerprint, expected = _expected_by_public_path()
    endpoints = {
        "homepage": (base, "/", {"text/html"}),
        "feed": (urljoin(base, site["feed_path"]), f"/{site['feed_path'].lstrip('/')}", {"application/rss+xml", "application/xml", "text/xml"}),
        "sitemap": (urljoin(base, site["sitemap_path"]), f"/{site['sitemap_path'].lstrip('/')}", {"application/xml", "text/xml"}),
        "robots": (urljoin(base, "robots.txt"), "/robots.txt", {"text/plain"}),
        "latest post": (latest_url, f"/posts/{latest_name}", {"text/html"}),
        "latest social image": (image_url, f"/{social_relpath}", {"image/png"}),
    }

    responses: dict[str, tuple[dict[str, str], bytes, str]] = {}
    production_by_path: dict[str, bytes] = {}
    for label, (url, public_path, allowed_types) in endpoints.items():
        try:
            status, headers, body, final_url = _fetch(url, timeout)
        except (urllib.error.URLError, TimeoutError) as exc:
            errors.append(f"{label}: request failed: {exc}")
            continue
        if status != 200:
            errors.append(f"{label}: HTTP {status}")
            continue
        if urlparse(final_url).netloc != origin:
            errors.append(f"{label}: redirected outside public origin to {final_url}")
        _expect_type(_content_type(headers), allowed_types, label, errors)
        _cache_observation(label, headers, errors, warnings)
        if not body:
            errors.append(f"{label}: empty response body")
        responses[label] = (headers, body, final_url)
        production_by_path[public_path] = body

        if public_path in expected:
            expected_sha, _ = expected[public_path]
            actual_sha = site_fingerprint.sha256_bytes(body)
            if actual_sha != expected_sha:
                errors.append(
                    f"{label}: production stale/content drift for {public_path} "
                    f"(expected sha256 {expected_sha[:12]}, got {actual_sha[:12]})"
                )

    if "homepage" in responses:
        _, body, _ = responses["homepage"]
        parser = _parse_html(body)
        canonicals = [x.get("href") for x in parser.links if x.get("rel") == "canonical"]
        props = {x.get("property"): x.get("content") for x in parser.meta if x.get("property")}
        feeds = [
            x.get("href")
            for x in parser.links
            if x.get("rel") == "alternate" and x.get("type") == "application/rss+xml"
        ]
        if canonicals != [base]:
            errors.append(f"homepage: canonical mismatch: {canonicals}")
        if props.get("og:url") != base:
            errors.append("homepage: og:url không khớp public URL")
        if props.get("og:image") and urlparse(props["og:image"]).netloc != origin:
            errors.append("homepage: og:image ngoài public origin")
        expected_feed = urljoin(base, site["feed_path"])
        if feeds != [expected_feed]:
            errors.append(f"homepage: RSS autodiscovery mismatch: {feeds}")

    if "latest post" in responses:
        _, body, _ = responses["latest post"]
        parser = _parse_html(body)
        canonicals = [x.get("href") for x in parser.links if x.get("rel") == "canonical"]
        props = {x.get("property"): x.get("content") for x in parser.meta if x.get("property")}
        if canonicals != [latest_url]:
            errors.append(f"latest post: canonical mismatch: {canonicals}")
        if props.get("og:url") != latest_url:
            errors.append("latest post: og:url không khớp canonical")
        if props.get("og:image") != image_url:
            errors.append("latest post: og:image không khớp social asset của issue mới nhất")

    if "feed" in responses:
        _, body, _ = responses["feed"]
        try:
            root = ET.fromstring(body)
            links = [(node.text or "").strip() for node in root.findall("./channel/item/link")]
            if latest_url not in links:
                errors.append("feed: chưa chứa latest post từ main")
        except ET.ParseError as exc:
            errors.append(f"feed: XML parse failed: {exc}")

    if "sitemap" in responses:
        _, body, _ = responses["sitemap"]
        try:
            root = ET.fromstring(body)
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [(node.text or "").strip() for node in root.findall("s:url/s:loc", ns)]
            if base not in locs or latest_url not in locs:
                errors.append("sitemap: thiếu homepage hoặc latest post")
        except ET.ParseError as exc:
            errors.append(f"sitemap: XML parse failed: {exc}")

    if "robots" in responses:
        _, body, _ = responses["robots"]
        text = body.decode("utf-8", errors="replace")
        expected_sitemap = f"Sitemap: {urljoin(base, site['sitemap_path'])}"
        if expected_sitemap not in text:
            errors.append("robots: sitemap directive không đúng public URL")

    production_fingerprint = _production_fingerprint(production_by_path)
    if production_fingerprint and production_fingerprint != expected_fingerprint:
        errors.append(
            "production fingerprint mismatch: serving state differs from repository main artifacts "
            f"({production_fingerprint[:12]} != {expected_fingerprint[:12]})"
        )

    return CheckResult(
        ok=not errors,
        errors=errors,
        warnings=warnings,
        expected_fingerprint=expected_fingerprint,
        production_fingerprint=production_fingerprint,
    )


def run(attempts: int = 12, delay: float = 10.0, timeout: float = 12.0) -> int:
    attempts = max(1, attempts)
    for attempt in range(1, attempts + 1):
        result = _check_once(timeout=timeout)
        if result.ok:
            print(f"✓ Production observability passed on attempt {attempt}/{attempts}.")
            print(f"  expected fingerprint:   {result.expected_fingerprint}")
            print(f"  production fingerprint: {result.production_fingerprint}")
            for warning in result.warnings:
                print(f"  ! {warning}")
            return 0
        print(f"Attempt {attempt}/{attempts} failed:")
        for error in result.errors:
            print(f"  - {error}")
        for warning in result.warnings:
            print(f"  ! {warning}")
        if attempt < attempts:
            time.sleep(delay)
    print("✗ Production observability failed after retries.")
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Observe linux.no.id.vn production endpoints and serving freshness.")
    parser.add_argument("--attempts", type=int, default=12)
    parser.add_argument("--delay", type=float, default=10.0)
    parser.add_argument("--timeout", type=float, default=12.0)
    args = parser.parse_args(argv)
    return run(args.attempts, args.delay, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())

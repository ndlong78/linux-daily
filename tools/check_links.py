#!/usr/bin/env python3
"""Kiểm tra link nội bộ và external URL cho Linux Daily.

Internal links là deterministic và fail cứng. External links dùng retry/timeout;
404/410 và lỗi HTTP client chắc chắn là hard failure, còn rate-limit, bot-block,
5xx và lỗi mạng sau retry chỉ cảnh báo để CI không flaky.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import ssl
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_CONFIG = os.path.join(ROOT, "site.json")
ARCHIVE_PATH = os.path.join(ROOT, "archive.html")
LEARNING_DASHBOARD_PATH = os.path.join(ROOT, "learning-dashboard.html")
LEARNING_PATHS_PATH = os.path.join(ROOT, "learning-paths.html")
POSTS_GLOB = os.path.join(ROOT, "posts", "post-*.html")
USER_AGENT = "LinuxDaily-LinkChecker/1.0 (+https://linux.no.id.vn/)"
TRANSIENT_STATUSES = {408, 425, 429, 500, 502, 503, 504}
BLOCKED_STATUSES = {401, 403, 418}
IGNORED_LINK_RELS = {"preconnect", "dns-prefetch"}


@dataclass(frozen=True)
class LinkRef:
    source: str
    url: str


@dataclass(frozen=True)
class ExternalResult:
    url: str
    status: int | None
    outcome: str  # ok | hard | warning
    detail: str


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        data = dict(attrs)
        element_id = data.get("id")
        if element_id:
            self.ids.add(element_id)
        name = data.get("name")
        if tag == "a" and name:
            self.ids.add(name)

        rel_tokens = set((data.get("rel") or "").lower().split())
        if tag == "link" and rel_tokens & IGNORED_LINK_RELS:
            return

        for attr in ("href", "src"):
            value = data.get(attr)
            if value:
                self.urls.append(value.strip())


def _load_site() -> dict:
    with open(SITE_CONFIG, encoding="utf-8") as f:
        return json.load(f)


def _html_files() -> list[str]:
    return [
        os.path.join(ROOT, "index.html"),
        ARCHIVE_PATH,
        LEARNING_DASHBOARD_PATH,
        LEARNING_PATHS_PATH,
        *sorted(glob.glob(POSTS_GLOB)),
    ]


def _parse_file(path: str) -> LinkParser:
    parser = LinkParser()
    with open(path, encoding="utf-8") as f:
        parser.feed(f.read())
    return parser


def collect_links() -> tuple[list[LinkRef], set[str]]:
    refs: list[LinkRef] = []
    all_ids: set[str] = set()
    for path in _html_files():
        parser = _parse_file(path)
        rel = os.path.relpath(path, ROOT)
        all_ids.update(f"{rel}#{item}" for item in parser.ids)
        refs.extend(LinkRef(rel, url) for url in parser.urls)
    return refs, all_ids


def _is_ignored_scheme(url: str) -> bool:
    scheme = urlsplit(url).scheme.lower()
    return scheme in {"mailto", "tel", "data", "javascript"}


def _site_host() -> str:
    return urlsplit(_load_site()["url"]).netloc.lower()


def escapes_root(target: str) -> bool:
    """True nếu target sau khi resolve nằm ngoài thư mục repo.

    Link như `../../etc/hostname` vẫn là link nội bộ (cùng site) nhưng trỏ ra ngoài
    cây website; nó phải là lỗi cứng chứ không được đem đi kiểm tra os.path.isfile,
    vì file có thể tình cờ tồn tại trên máy build và làm gate xanh giả.
    """
    return os.path.isabs(target) or target == ".." or target.startswith(".." + os.sep)


def _local_target(source: str, url: str, site_host: str) -> tuple[str, str] | None:
    if not url or _is_ignored_scheme(url):
        return None
    parts = urlsplit(url)
    if parts.scheme in {"http", "https"}:
        if parts.netloc.lower() != site_host:
            return None
        raw_path = parts.path.lstrip("/") or "index.html"
    elif parts.scheme or parts.netloc:
        return None
    elif parts.path.startswith("/"):
        raw_path = parts.path.lstrip("/") or "index.html"
    elif parts.path:
        raw_path = os.path.normpath(os.path.join(os.path.dirname(source), parts.path))
    else:
        raw_path = source

    target = os.path.normpath(raw_path)
    if target == ".":
        target = "index.html"
    return target, unquote(parts.fragment)


def check_internal() -> list[str]:
    refs, all_ids = collect_links()
    site_host = _site_host()
    errors: list[str] = []
    for ref in refs:
        resolved = _local_target(ref.source, ref.url, site_host)
        if resolved is None:
            continue
        target, fragment = resolved
        if escapes_root(target):
            errors.append(f"{ref.source}: link nội bộ thoát khỏi thư mục repo: {ref.url} -> {target}")
            continue
        full = os.path.join(ROOT, target)
        if os.path.isdir(full):
            target = os.path.join(target, "index.html")
            full = os.path.join(ROOT, target)
        if not os.path.isfile(full):
            errors.append(f"{ref.source}: link nội bộ không tồn tại: {ref.url} -> {target}")
            continue
        if fragment and target.lower().endswith((".html", ".htm")):
            key = f"{target}#{fragment}"
            if key not in all_ids:
                errors.append(f"{ref.source}: fragment không tồn tại: {ref.url}")
    return errors


def collect_external_urls() -> list[str]:
    refs, _ = collect_links()
    host = _site_host()
    urls = {
        ref.url
        for ref in refs
        if urlsplit(ref.url).scheme in {"http", "https"}
        and urlsplit(ref.url).netloc.lower() != host
    }
    return sorted(urls)


def _request_once(url: str, timeout: float) -> int:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}
    head_req = Request(url, headers=headers, method="HEAD")
    try:
        with urlopen(head_req, timeout=timeout) as response:
            return int(response.status)
    except HTTPError:
        pass

    get_req = Request(url, headers={**headers, "Range": "bytes=0-0"}, method="GET")
    try:
        with urlopen(get_req, timeout=timeout) as response:
            return int(response.status)
    except HTTPError as exc:
        return int(exc.code)


def classify_status(url: str, status: int) -> ExternalResult:
    if 200 <= status < 400:
        return ExternalResult(url, status, "ok", f"HTTP {status}")
    if status in BLOCKED_STATUSES:
        return ExternalResult(url, status, "warning", f"HTTP {status} (auth/bot-block)")
    if status in TRANSIENT_STATUSES:
        return ExternalResult(url, status, "warning", f"HTTP {status} (transient)")
    if 400 <= status < 500:
        return ExternalResult(url, status, "hard", f"HTTP {status}")
    return ExternalResult(url, status, "warning", f"HTTP {status}")


def check_external_url(url: str, timeout: float = 6.0, retries: int = 2) -> ExternalResult:
    last_error = ""
    for attempt in range(retries + 1):
        try:
            status = _request_once(url, timeout)
            result = classify_status(url, status)
            if status not in TRANSIENT_STATUSES or attempt == retries:
                return result
        except (URLError, TimeoutError, ssl.SSLError) as exc:
            last_error = str(exc)
            if attempt == retries:
                break
        if attempt < retries:
            time.sleep(0.5 * (attempt + 1))
    return ExternalResult(url, None, "warning", f"network/timeout sau {retries + 1} lần: {last_error}")


def check_external(max_workers: int = 8) -> tuple[list[ExternalResult], list[ExternalResult]]:
    hard: list[ExternalResult] = []
    warnings: list[ExternalResult] = []
    urls = collect_external_urls()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(check_external_url, url): url for url in urls}
        for future in as_completed(futures):
            result = future.result()
            if result.outcome == "hard":
                hard.append(result)
            elif result.outcome == "warning":
                warnings.append(result)
    return sorted(hard, key=lambda item: item.url), sorted(warnings, key=lambda item: item.url)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Kiểm tra link nội bộ/external của Linux Daily.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--internal", action="store_true", help="Chỉ kiểm tra link nội bộ.")
    mode.add_argument("--external", action="store_true", help="Chỉ kiểm tra external HTTP(S) links.")
    parser.add_argument("--workers", type=int, default=8, help="Số external URL kiểm tra song song.")
    args = parser.parse_args(argv)

    run_internal = not args.external
    run_external = not args.internal
    failed = False

    if run_internal:
        errors = check_internal()
        if errors:
            failed = True
            print(f"✗ Internal links: {len(errors)} lỗi", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print("✓ Internal links: tất cả target/fragment đều hợp lệ.")

    if run_external:
        hard, warnings = check_external(max_workers=max(1, args.workers))
        for item in warnings:
            print(f"⚠ External: {item.url} — {item.detail}")
        if hard:
            failed = True
            print(f"✗ External links: {len(hard)} link lỗi chắc chắn", file=sys.stderr)
            for item in hard:
                print(f"  - {item.url} — {item.detail}", file=sys.stderr)
        else:
            print("✓ External links: không phát hiện HTTP client error chắc chắn.")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

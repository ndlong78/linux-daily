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
import subprocess
import sys
import tempfile
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


# Tập file HTML được quét. Nhận root tuỳ ý để dùng lại nguyên bộ parser cho cây
# baseline lấy từ một git ref — baseline phải đi qua đúng parser này, không phải
# một regex xấp xỉ, nếu không "URL nào là mới" sẽ sai theo cách khó thấy.
HTML_FILE_NAMES = ("index.html", "archive.html", "learning-dashboard.html", "learning-paths.html")


def _html_files(root: str | None = None) -> list[str]:
    base = root or ROOT
    return [
        *(os.path.join(base, name) for name in HTML_FILE_NAMES),
        *sorted(glob.glob(os.path.join(base, "posts", "post-*.html"))),
    ]


def _external_refs_under(root: str) -> set[tuple[str, str]]:
    """Cặp (file, url) — không phải chỉ url.

    Theo dõi theo cặp vì URL không thôi để lọt một lỗ: một link đã chết nằm sẵn
    ở bài cũ, nếu được chép sang bài mới thì tính theo url sẽ coi là "đã có sẵn"
    và không chặn — trong khi bài mới đang thật sự trích một nguồn chết.
    Theo cặp thì (bài mới, url đó) là mới, nên vẫn chặn.

    Dựng lại index/archive không gây nhiễu: nội dung giống nhau thì cặp giống
    nhau. Chỉ khi một trang generated bắt đầu trích URL external theo bài — hiện
    là 0/188 — mới có cặp mới, và khi đó chặn cũng đúng: bài mới đưa URL đó vào.
    """
    host = _site_host()
    refs: set[tuple[str, str]] = set()
    for path in _html_files(root):
        if not os.path.isfile(path):
            continue
        rel = os.path.relpath(path, root)
        for url in _parse_file(path).urls:
            split = urlsplit(url)
            if split.scheme in {"http", "https"} and split.netloc.lower() != host:
                refs.add((rel, url))
    return refs


class BaselineError(RuntimeError):
    """Không dựng được cây baseline — nói rõ nguyên nhân thay vì ném traceback."""


def baseline_external_refs(ref: str) -> set[tuple[str, str]]:
    """Cặp (file, url) đã tồn tại ở `ref` — thường là base SHA của PR."""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            archive = subprocess.run(
                ["git", "archive", ref, "--", *HTML_FILE_NAMES, "posts"],
                cwd=ROOT, capture_output=True, check=True,
            ).stdout
            subprocess.run(["tar", "-x", "-C", tmp], input=archive, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            # Hay gặp nhất: checkout nông nên base SHA không có trong lịch sử.
            # Phải nói thẳng, vì nếu chỉ ném traceback thì người sau dễ "sửa"
            # bằng cách bỏ --baseline — tức là âm thầm gỡ luôn chính sách này.
            raise BaselineError(
                f"không dựng được cây baseline từ ref {ref!r}: {exc}. "
                "Thường do checkout nông — cần fetch-depth: 0 để base SHA có mặt. "
                "KHÔNG gỡ --baseline để né lỗi này."
            ) from exc
        return _external_refs_under(tmp)


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
    # Chỉ 2xx chứng minh URL đã thật sự phục vụ tài liệu. Redirect thường được
    # urllib đi theo tới response cuối; nếu vẫn nhận 3xx thì chưa xác minh được
    # đích cuối và URL mới trên PR phải bị chặn.
    if 200 <= status < 300:
        return ExternalResult(url, status, "ok", f"HTTP {status}")
    if 300 <= status < 400:
        return ExternalResult(url, status, "warning", f"HTTP {status} (redirect unresolved)")
    if status in BLOCKED_STATUSES:
        return ExternalResult(url, status, "warning", f"HTTP {status} (auth/bot-block)")
    if status in TRANSIENT_STATUSES:
        return ExternalResult(url, status, "warning", f"HTTP {status} (transient)")
    if 400 <= status < 500:
        return ExternalResult(url, status, "hard", f"HTTP {status}")
    return ExternalResult(url, status, "warning", f"HTTP {status}")


# Giãn nhịp giữa hai request tới CÙNG một host. Không phải để lịch sự suông:
# kho có 37 URL man.freebsd.org và 15 URL docs.ansible.com, và bắn chúng song
# song làm chính ta lĩnh 429 — đo được trong 4/4 log CI, đúng 15 URL ansible mỗi
# lần. Trước PR #141 đó chỉ là cảnh báo bị bỏ qua; sau #141, một URL nguồn MỚI
# dính 429 sẽ chặn bài. Nghĩa là cổng đúng, còn thứ làm nó nổ lại do chính công
# cụ tự gây ra.
HOST_DELAY_SECONDS = 1.0


def _host_of(url: str) -> str:
    return urlsplit(url).netloc.lower()


def check_external_url(
    url: str, timeout: float = 6.0, retries: int = 2,
    host_delay: float = HOST_DELAY_SECONDS,
) -> ExternalResult:
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
            # Retry cũng gõ vào đúng host vừa từ chối, nên không bao giờ nhanh
            # hơn nhịp ta tự đặt cho host đó.
            time.sleep(max(0.5 * (attempt + 1), host_delay))
    return ExternalResult(url, None, "warning", f"network/timeout sau {retries + 1} lần: {last_error}")


def _check_host_serially(
    urls: list[str], timeout: float, host_delay: float,
) -> list[ExternalResult]:
    """Mọi URL của một host, tuần tự, cách nhau `host_delay` giây."""
    results: list[ExternalResult] = []
    for index, url in enumerate(urls):
        if index:
            time.sleep(host_delay)
        results.append(check_external_url(url, timeout=timeout, host_delay=host_delay))
    return results


def check_external(
    max_workers: int = 8, host_delay: float = HOST_DELAY_SECONDS,
) -> tuple[list[ExternalResult], list[ExternalResult]]:
    """Song song GIỮA các host, tuần tự TRONG mỗi host.

    `max_workers` vì thế là số host chạy đồng thời, không phải số URL — kho có
    ~190 URL trải trên ~60 host, nên mức song song thực tế gần như không đổi.
    Thời gian chạy bị chặn dưới bởi host đông URL nhất (37 × host_delay), không
    phải bởi tổng số URL.
    """
    hard: list[ExternalResult] = []
    warnings: list[ExternalResult] = []

    by_host: dict[str, list[str]] = {}
    for url in collect_external_urls():
        by_host.setdefault(_host_of(url), []).append(url)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(_check_host_serially, host_urls, 6.0, host_delay)
            for host_urls in by_host.values()
        ]
        for future in as_completed(futures):
            for result in future.result():
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
    parser.add_argument(
        "--workers", type=int, default=8,
        help="Số HOST kiểm tra song song (trong mỗi host luôn tuần tự).",
    )
    parser.add_argument(
        "--host-delay", type=float, default=HOST_DELAY_SECONDS, metavar="GIÂY",
        help="Giãn nhịp giữa hai request tới cùng một host. Hạ xuống 0 sẽ làm "
             "công cụ tự chuốc 429 như trước — chỉ dùng khi chạy thử cục bộ.",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        metavar="REF",
        help="Git ref làm mốc (thường là base SHA của PR). Có mốc thì chỉ link MỚI "
             "mới chặn CI; link đã có sẵn bị 404 được báo là nợ bảo trì.",
    )
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
        hard, warnings = check_external(
            max_workers=max(1, args.workers), host_delay=max(0.0, args.host_delay)
        )

        # Không có mốc: mọi link chết đều chặn. Đây là chế độ cho `push: main` và
        # lịch chạy định kỳ — ở đó không có bài nào để chặn, nên siết chặt là đúng.
        introduced, inherited = hard, []
        if args.baseline:
            # Có mốc: chỉ link do nhánh này đưa vào mới chặn. Link đã có sẵn trên
            # main mà hôm nay 404 là nợ bảo trì của kho, không phải lỗi của bài
            # hôm nay — chặn bài vì nó là sai đối tượng, và thực tế đã dẫn tới
            # việc agent đi sửa hai bài cũ rồi làm hỏng một nguồn đang tốt (#063).
            try:
                existing = baseline_external_refs(args.baseline)
            except BaselineError as exc:
                # Fail closed. Không được lặng lẽ quay về "coi mọi link là kế
                # thừa" — đó là gỡ gate mà không ai thấy — cũng không nên ném
                # traceback trần, vì traceback đẩy người sửa tới chỗ bỏ --baseline.
                print(f"✗ External links: {exc}", file=sys.stderr)
                return 1
            current = _external_refs_under(ROOT)
            # URL là "mới" nếu có BẤT KỲ file nào đang trích nó mà cặp (file, url)
            # chưa từng tồn tại ở baseline.
            introduced_urls = {
                url for rel, url in current if (rel, url) not in existing
            }
            # URL mới chỉ pass khi check trả `ok`, tức response cuối là 2xx.
            # 403/bot-block, timeout, lỗi TLS/DNS, 3xx chưa resolve và 5xx đều
            # không chứng minh được nguồn tồn tại, nên phải fail closed trên PR.
            introduced = [
                item for item in [*hard, *warnings] if item.url in introduced_urls
            ]
            inherited = [item for item in hard if item.url not in introduced_urls]
            warnings = [item for item in warnings if item.url not in introduced_urls]

        for item in warnings:
            print(f"⚠ External: {item.url} — {item.detail}")

        if inherited:
            print(
                f"⚠ Link chết trong nội dung đã có ({len(inherited)}) — nợ bảo trì, "
                "KHÔNG do nhánh này gây ra và không chặn PR:"
            )
            for item in inherited:
                print(f"  ~ {item.url} — {item.detail}")
            print("  Sửa ở PR riêng; đừng đổi nguồn trong lúc đang xuất bản bài.")

        if introduced:
            failed = True
            label = (
                "link mới chưa xác minh được HTTP 2xx"
                if args.baseline
                else "link lỗi chắc chắn"
            )
            print(f"✗ External links: {len(introduced)} {label}", file=sys.stderr)
            for item in introduced:
                print(f"  - {item.url} — {item.detail}", file=sys.stderr)
        elif not hard:
            print("✓ External links: không phát hiện HTTP client error chắc chắn.")
        else:
            print("✓ External links: link mới đều sống.")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

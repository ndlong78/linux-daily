#!/usr/bin/env python3
"""Validate Linux Daily posts against STYLE.md.

Historical backfill is complete. Linux Daily #001-#040 and every new post are
enforced by the STYLE.md contract. Verification evidence uses the legacy
``tested_on`` sentinel schema through #069 and the explicit runtime/documentation
split from #070 onward; historical posts become explicit when the deterministic
#070 backfill runs.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
BACKFILLED_THROUGH = 40
ENFORCED_FROM_ISSUE = 41
VERIFICATION_SPLIT_FROM_ISSUE = 70
DOCUMENTATION_SUFFIX = "(documentation-verified)"

SCRIPT_META_RE = re.compile(
    r'<script[^>]+id=["\']ld-meta["\'][^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL
)
TAG_RE = re.compile(r"<[^>]+>")
HEADING_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.IGNORECASE | re.DOTALL)
CODE_RE = re.compile(
    r"<pre(?P<pre_attrs>[^>]*)>\s*<code(?P<code_attrs>[^>]*)>(?P<body>.*?)</code>\s*</pre>",
    re.IGNORECASE | re.DOTALL,
)
ISSUE_FILE_RE = re.compile(r"post-(\d{3})-")
PROMPT_RE = re.compile(
    r"(?m)^\s*(?:\$\s+|#\s+(?:sudo|apt|apt-get|dnf|pkg|systemctl|service|ssh|ip|nmcli|netplan|mount|umount|cp|mv|rm|dd|mkfs|zpool|zfs)\b)"
)
CURL_PIPE_SHELL_RE = re.compile(r"curl\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba)?sh\b", re.IGNORECASE)
LEGACY_PLACEHOLDER_RE = re.compile(r"\bYOUR_[A-Z0-9_]+\b|\[username\]|\[server-ip\]", re.IGNORECASE)
RUN_AS_RE = re.compile(r'data-run-as=["\'](?:user|sudo|root)["\']', re.IGNORECASE)
LANGUAGE_CLASS_RE = re.compile(r'class=["\'][^"\']*\blanguage-[a-z0-9_-]+\b', re.IGNORECASE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CODE_LABEL_RE = re.compile(r'class=["\'][^"\']*\bcode-label\s+([a-z0-9_-]+)', re.IGNORECASE)
CODE_LABEL_TOKENS = frozenset({"bsd", "ubuntu", "debian", "fedora", "linux", "same"})

REQUIRED_HEADINGS = (
    "mục tiêu",
    "yêu cầu tiên quyết",
    "các bước thực hiện",
    "kiểm chứng",
    "lưu ý & khắc phục lỗi",
    "bài tập",
)


@dataclass(frozen=True)
class StyleResult:
    path: Path
    issue: int
    errors: tuple[str, ...]

    @property
    def enforced(self) -> bool:
        return self.issue <= BACKFILLED_THROUGH or self.issue >= ENFORCED_FROM_ISSUE

    @property
    def compliant(self) -> bool:
        return not self.errors


def _plain(fragment: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub(" ", fragment)).split())


def _issue_from_path(path: Path) -> int:
    match = ISSUE_FILE_RE.search(path.name)
    if not match:
        raise ValueError(f"không đọc được issue từ filename: {path.name}")
    return int(match.group(1))


def _load_meta(text: str) -> tuple[dict, str | None]:
    match = SCRIPT_META_RE.search(text)
    if not match:
        return {}, "thiếu <script id=\"ld-meta\">"
    try:
        value = json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError as exc:
        return {}, f"ld-meta JSON không hợp lệ: {exc.msg}"
    if not isinstance(value, dict):
        return {}, "ld-meta phải là JSON object"
    return value, None


def _valid_iso_date(value: object) -> bool:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _valid_string_list(value: object) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _verification_errors(meta: dict, issue: int, lowered: str) -> list[str]:
    errors: list[str] = []
    tested_on = meta.get("tested_on")
    split_schema = "documentation_verified_on" in meta or issue >= VERIFICATION_SPLIT_FROM_ISSUE

    if not split_schema:
        if not _valid_string_list(tested_on) or not tested_on:
            errors.append("ld-meta.tested_on phải là danh sách OS/version đã test")
        if "tested on:" not in lowered:
            errors.append("thiếu metadata hiển thị `Tested on:`")
        return errors

    documentation_verified_on = meta.get("documentation_verified_on")
    if not _valid_string_list(tested_on):
        errors.append("ld-meta.tested_on phải là list runtime-test (có thể rỗng)")
    if not _valid_string_list(documentation_verified_on):
        errors.append(
            "ld-meta.documentation_verified_on phải là list documentation review (có thể rỗng)"
        )

    runtime = tested_on if isinstance(tested_on, list) else []
    documented = documentation_verified_on if isinstance(documentation_verified_on, list) else []
    if not runtime and not documented:
        errors.append("verification metadata phải có ít nhất một bằng chứng runtime hoặc documentation")

    for field_name, values in (
        ("tested_on", runtime),
        ("documentation_verified_on", documented),
    ):
        for item in values:
            if isinstance(item, str) and DOCUMENTATION_SUFFIX in item.lower():
                errors.append(
                    f"ld-meta.{field_name} không được chứa sentinel (documentation-verified)"
                )
                break

    if "runtime tested:" not in lowered:
        errors.append("thiếu metadata hiển thị `Runtime tested:`")
    if "documentation verified:" not in lowered:
        errors.append("thiếu metadata hiển thị `Documentation verified:`")
    if "tested on:" in lowered:
        errors.append("schema verification mới không được hiển thị nhãn legacy `Tested on:`")
    return errors


def audit_post(path: Path) -> StyleResult:
    text = path.read_text(encoding="utf-8")
    issue = _issue_from_path(path)
    errors: list[str] = []
    meta, meta_error = _load_meta(text)
    if meta_error:
        errors.append(meta_error)

    lowered = _plain(text).lower()
    errors.extend(_verification_errors(meta, issue, lowered))

    if not _valid_iso_date(meta.get("last_verified")):
        errors.append("ld-meta.last_verified phải là ngày ISO YYYY-MM-DD")

    changes_system = meta.get("changes_system")
    if not isinstance(changes_system, bool):
        errors.append("ld-meta.changes_system phải là boolean")

    if "last verified:" not in lowered:
        errors.append("thiếu metadata hiển thị `Last verified:`")

    headings = [_plain(item).lower() for item in HEADING_RE.findall(text)]
    for required in REQUIRED_HEADINGS:
        if not any(required in heading for heading in headings):
            errors.append(f"thiếu heading bắt buộc: {required}")

    if changes_system is True and not any("gỡ / hoàn tác" in heading for heading in headings):
        errors.append("changes_system=true nhưng thiếu mục Gỡ / Hoàn tác")

    if not re.search(r'<ol[^>]*class=["\'][^"\']*\bsteps\b', text, re.IGNORECASE):
        errors.append("Các bước thực hiện phải dùng <ol class=\"steps\">")

    verification_present = any("kiểm chứng" in heading for heading in headings)
    if verification_present and not (
        "expected output" in lowered or "kết quả mong đợi" in lowered
    ):
        errors.append("mục Kiểm chứng thiếu Expected Output/Kết quả mong đợi")

    labels = CODE_LABEL_RE.findall(text)
    if not labels:
        errors.append(
            'command block phải gắn nhãn OS: <div class="code-label bsd">…</div> '
            f'(token hợp lệ: {", ".join(sorted(CODE_LABEL_TOKENS))})'
        )
    for token in sorted({item.lower() for item in labels} - CODE_LABEL_TOKENS):
        errors.append(
            f'code-label "{token}" không hợp lệ '
            f'(token hợp lệ: {", ".join(sorted(CODE_LABEL_TOKENS))})'
        )

    for index, match in enumerate(CODE_RE.finditer(text), start=1):
        attrs = match.group("code_attrs")
        body = html.unescape(TAG_RE.sub("", match.group("body")))
        if not LANGUAGE_CLASS_RE.search(attrs):
            errors.append(f"code block #{index} thiếu class language-*")

        if PROMPT_RE.search(body):
            errors.append(f"code block #{index} chứa shell prompt $/#")
        if CURL_PIPE_SHELL_RE.search(body):
            errors.append(f"code block #{index} chứa curl | sh chạy trực tiếp")
        if LEGACY_PLACEHOLDER_RE.search(body):
            errors.append(f"code block #{index} dùng placeholder không theo chuẩn <...>")

        language_match = re.search(r"language-([a-z0-9_-]+)", attrs, re.IGNORECASE)
        language = language_match.group(1).lower() if language_match else ""
        if language in {"bash", "sh", "shell"}:
            context = text[max(0, match.start() - 800) : match.start()]
            if not RUN_AS_RE.search(context):
                errors.append(f"bash block #{index} thiếu data-run-as=user|sudo|root")

    return StyleResult(path=path, issue=issue, errors=tuple(dict.fromkeys(errors)))


def collect_results(posts_dir: Path = POSTS_DIR) -> list[StyleResult]:
    return [audit_post(path) for path in sorted(posts_dir.glob("post-*.html"))]


def print_audit(results: list[StyleResult], *, stream=sys.stdout) -> None:
    compliant = sum(result.compliant for result in results)
    legacy = sum(not result.enforced for result in results)
    enforced = sum(result.enforced for result in results)
    print("Linux Daily STYLE.md audit", file=stream)
    print("=" * 28, file=stream)
    print(
        f"posts={len(results)} compliant={compliant} legacy={legacy} enforced={enforced}",
        file=stream,
    )
    for result in results:
        state = "PASS" if result.compliant else "LEGACY" if not result.enforced else "FAIL"
        print(f"#{result.issue:03d} {state} {result.path.name}", file=stream)
        for error in result.errors:
            print(f"  - {error}", file=stream)


def check(results: list[StyleResult], *, stream=sys.stdout, err_stream=sys.stderr) -> int:
    enforced_failures = [result for result in results if result.enforced and not result.compliant]
    legacy_noncompliant = [result for result in results if not result.enforced and not result.compliant]
    print(
        f"STYLE.md: audited {len(results)} posts; "
        f"legacy_noncompliant={len(legacy_noncompliant)}; enforced_failures={len(enforced_failures)}",
        file=stream,
    )
    if not enforced_failures:
        print(
            "OK: STYLE.md enforced cho toàn bộ Linux Daily series.",
            file=stream,
        )
        return 0
    for result in enforced_failures:
        print(f"FAIL #{result.issue:03d}: {result.path.name}", file=err_stream)
        for error in result.errors:
            print(f"  - {error}", file=err_stream)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit",
        action="store_true",
        help="in báo cáo chi tiết cho toàn bộ lịch sử; không fail vì bài legacy",
    )
    parser.add_argument(
        "--posts-dir",
        type=Path,
        default=POSTS_DIR,
        help="thư mục posts dùng cho test/audit",
    )
    args = parser.parse_args(argv)
    results = collect_results(args.posts_dir)
    if args.audit:
        print_audit(results)
    return check(results)


if __name__ == "__main__":
    raise SystemExit(main())

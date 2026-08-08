#!/usr/bin/env python3
"""Validate distro coverage and obvious FreeBSD portability mistakes."""
from __future__ import annotations

import argparse
import glob
import html
import re
from pathlib import Path

import postmeta

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
REPORT_PATH = ROOT / "docs" / "distro-coverage-report.md"

DISTROS = {
    "ubuntu_xubuntu": {
        "label": "Ubuntu / Xubuntu",
        "patterns": (r"\bUbuntu\b", r"\bXubuntu\b"),
    },
    "debian": {"label": "Debian", "patterns": (r"\bDebian\b",)},
    "fedora": {"label": "Fedora", "patterns": (r"\bFedora\b",)},
    "freebsd": {"label": "FreeBSD", "patterns": (r"\bFreeBSD\b",)},
}

FREEBSD_COMMAND_PATTERNS = (
    re.compile(
        r"^\s*(?:sudo\s+)?(?:apt|apt-get|dnf|yum|systemctl|journalctl|timedatectl|"
        r"hostnamectl|loginctl|nft|ufw|firewall-cmd)\b"
    ),
    re.compile(r"/(?:etc|usr/lib)/systemd(?:/|\b)"),
    re.compile(r"/etc/netplan(?:/|\b)"),
)

_PRE_RE = re.compile(r"<pre\b(?P<attrs>[^>]*)>(?P<body>.*?)</pre>", re.IGNORECASE | re.DOTALL)
_CLASS_RE = re.compile(r"\bclass\s*=\s*([\"'])(?P<value>.*?)\1", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def visible_text(source: str) -> str:
    return html.unescape(_TAG_RE.sub(" ", source))


def has_distro(text: str, key: str) -> bool:
    patterns = DISTROS[key]["patterns"]
    return all(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def freebsd_blocks(source: str) -> list[str]:
    blocks: list[str] = []
    for match in _PRE_RE.finditer(source):
        class_match = _CLASS_RE.search(match.group("attrs"))
        if not class_match:
            continue
        classes = class_match.group("value").split()
        if "bsd" not in classes:
            continue
        blocks.append(visible_text(match.group("body")).strip())
    return blocks


def portability_violations(blocks: list[str]) -> list[str]:
    violations: list[str] = []
    for block_index, block in enumerate(blocks, start=1):
        for line_number, raw_line in enumerate(block.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            for pattern in FREEBSD_COMMAND_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        f"FreeBSD block {block_index}, line {line_number}: {line}"
                    )
                    break
    return violations


def analyze_source(source: str) -> dict:
    text = visible_text(source)
    coverage = {key: has_distro(text, key) for key in DISTROS}
    blocks = freebsd_blocks(source)
    return {
        "coverage": coverage,
        "freebsd_blocks": len(blocks),
        "violations": portability_violations(blocks),
    }


def collect() -> list[dict]:
    posts: list[dict] = []
    for raw_path in glob.glob(POSTS_GLOB):
        path = Path(raw_path)
        source = path.read_text(encoding="utf-8")
        meta = postmeta.read_meta(str(path))
        analysis = analyze_source(source)
        posts.append(
            {
                "issue": int(meta["issue"]),
                "title": str(meta["title"]).strip(),
                "path": path.relative_to(ROOT).as_posix(),
                **analysis,
            }
        )
    posts.sort(key=lambda item: item["issue"])
    return posts


def review(posts: list[dict] | None = None) -> dict:
    posts = posts if posts is not None else collect()
    coverage_counts = {
        key: sum(bool(post["coverage"].get(key)) for post in posts) for key in DISTROS
    }
    complete_posts = sum(all(post["coverage"].get(key) for key in DISTROS) for post in posts)
    freebsd_marked_posts = sum(post["freebsd_blocks"] > 0 for post in posts)
    violation_count = sum(len(post["violations"]) for post in posts)
    return {
        "posts": posts,
        "total": len(posts),
        "coverage_counts": coverage_counts,
        "complete_posts": complete_posts,
        "freebsd_marked_posts": freebsd_marked_posts,
        "violation_count": violation_count,
    }


def errors(result: dict) -> list[str]:
    problems: list[str] = []
    for post in result["posts"]:
        missing = [DISTROS[key]["label"] for key in DISTROS if not post["coverage"].get(key)]
        if missing:
            problems.append(
                f"#{post['issue']:03d} thiếu distro coverage: {', '.join(missing)}"
            )
        if post["freebsd_blocks"] == 0:
            problems.append(f"#{post['issue']:03d} thiếu code block FreeBSD được đánh dấu class=bsd")
        for violation in post["violations"]:
            problems.append(f"#{post['issue']:03d} có Linux-only semantics trong FreeBSD: {violation}")
    return problems


def render_report(result: dict | None = None) -> str:
    result = result if result is not None else review()
    total = result["total"]
    lines = [
        "# Linux Daily — Distro Coverage & Portability Matrix",
        "",
        "> Báo cáo này được sinh deterministic từ nội dung bài viết. Presence coverage là guardrail cấu trúc, không thay thế technical review về tính đúng đắn của từng lệnh.",
        "",
        "## Snapshot",
        "",
        f"- Published posts: **{total}**",
        f"- Complete Ubuntu/Xubuntu + Debian + Fedora + FreeBSD coverage: **{result['complete_posts']}/{total}**",
        f"- Posts with explicit FreeBSD code blocks: **{result['freebsd_marked_posts']}/{total}**",
        f"- Linux-only command/path violations inside FreeBSD blocks: **{result['violation_count']}**",
        "",
        "| Platform | Posts with explicit coverage |",
        "|---|---:|",
    ]
    for key, info in DISTROS.items():
        lines.append(f"| {info['label']} | {result['coverage_counts'][key]}/{total} |")

    problems = errors(result)
    lines.extend(["", "## Review queue", ""])
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("- Không có bài nào vi phạm baseline P7.1 hiện tại.")

    lines.extend(
        [
            "",
            "## Policy boundary",
            "",
            "- Mỗi bài phải nhắc rõ Ubuntu/Xubuntu, Debian, Fedora và FreeBSD.",
            "- Mỗi bài phải có ít nhất một code block FreeBSD được đánh dấu `class=\"bsd\"` để tách semantics khỏi Linux.",
            "- Gate chỉ hard-fail các Linux-only command/path rõ ràng trong block FreeBSD; nó không suy đoán portability từ mọi token CLI.",
            "- Technical reviewer vẫn chịu trách nhiệm kiểm package name, service name, filesystem path, firewall model và behavior thực tế trên từng HĐH.",
            "",
        ]
    )
    return "\n".join(lines)


def run(*, check: bool) -> int:
    result = review()
    problems = errors(result)
    if problems:
        print(f"LỖI: distro portability có {len(problems)} vấn đề")
        for problem in problems:
            print(f"- {problem}")
        return 1

    expected = render_report(result)
    current = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.exists() else ""
    if check and current != expected:
        print(
            "LỖI: docs/distro-coverage-report.md chưa đồng bộ. "
            "Chạy `python tools/distro_coverage.py`."
        )
        return 1
    if not check:
        REPORT_PATH.write_text(expected, encoding="utf-8")
        print(f"Đã cập nhật distro coverage report cho {result['total']} bài.")
    else:
        print(
            "OK: distro coverage/portability pass; "
            f"{result['complete_posts']}/{result['total']} bài đủ 4 platform, "
            f"violations={result['violation_count']}."
        )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail nếu coverage/report bị drift.")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

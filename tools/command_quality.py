#!/usr/bin/env python3
"""Static quality checks for command and configuration examples in Linux Daily posts."""
from __future__ import annotations

import argparse
import glob
import html
import re
from pathlib import Path

import postmeta

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
FUTURE_ENFORCEMENT_ISSUE = 20

_CODE_RE = re.compile(
    r"<pre\b(?P<pre_attrs>[^>]*)>\s*<code\b(?P<code_attrs>[^>]*)>"
    r"(?P<body>.*?)</code>\s*</pre>",
    re.IGNORECASE | re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")
_REMOTE_PIPE_RE = re.compile(
    r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sudo\s+)?(?:sh|bash)\b",
    re.IGNORECASE,
)
_CHMOD_777_RE = re.compile(r"\bchmod\b[^\n#]*\b0?777\b", re.IGNORECASE)
_CATASTROPHIC_RM_RE = re.compile(
    r"\brm\s+-[A-Za-z]*r[A-Za-z]*f[A-Za-z]*\s+"
    r"(?:/|/\*|/(?:etc|usr|var|boot|home)(?:/\*?)?)(?:\s|$)",
    re.IGNORECASE,
)
_RECURSIVE_ROOT_PERM_RE = re.compile(
    r"\b(?:chmod|chown)\s+-R\b[^\n#]*\s"
    r"(?:/|/\*|/(?:etc|usr|var|boot|home)(?:/\*?)?)(?:\s|$)",
    re.IGNORECASE,
)
_PRIVILEGED_REDIRECT_RE = re.compile(
    r"^\s*sudo\s+(?:echo|printf|cat)\b[^\n]*(?:>|>>)\s*/(?:etc|usr|var)(?:/|\b)",
    re.IGNORECASE,
)
_INSECURE_TLS_RE = re.compile(
    r"(?:\bcurl\b[^\n]*(?:\s-k(?:\s|$)|\s--insecure(?:\s|$)))|"
    r"(?:\bwget\b[^\n]*\s--no-check-certificate(?:\s|$))",
    re.IGNORECASE,
)
_LITERAL_SECRET_RE = re.compile(
    r"\b(?:password|passwd|secret|token)\s*[:=]\s*[\"']?"
    r"(?:password|passwd|changeme|change-me|secret|token|123456|admin123)\b",
    re.IGNORECASE,
)

BLOCK_ALWAYS = {
    "remote_pipe_shell",
    "chmod_world_writable",
    "catastrophic_rm",
    "recursive_root_permissions",
}
BLOCK_FROM_020 = {
    "privileged_redirection",
    "insecure_tls",
    "literal_secret_example",
    "destructive_without_context",
}

SAFETY_TERMS = (
    "cảnh báo",
    "mất dữ liệu",
    "sao lưu",
    "backup",
    "snapshot",
    "rollback",
    "phục hồi",
    "restore",
    "kiểm tra",
    "xác nhận",
    "lab",
    "thử nghiệm",
    "test",
)


def visible_text(source: str) -> str:
    return html.unescape(_TAG_RE.sub(" ", source))


def _normalize_line(raw: str) -> str:
    line = html.unescape(raw).strip()
    if line.startswith("$ "):
        return line[2:].lstrip()
    return line


def _has_safety_context(context: str) -> bool:
    lowered = context.casefold()
    return any(term.casefold() in lowered for term in SAFETY_TERMS)


def _is_destructive_storage_command(line: str) -> bool:
    lowered = line.casefold()
    if re.search(r"(?:^|\s)(?:sudo\s+)?mkfs(?:\.[\w-]+)?\b", lowered):
        return True
    if re.search(r"(?:^|\s)(?:sudo\s+)?wipefs\b", lowered) and not re.search(
        r"(?:\s--no-act\b|\s-n(?:\s|$))", lowered
    ):
        return True
    if re.search(r"\bdd\b[^\n]*\bof=/dev/", lowered):
        return True
    if re.search(r"\b(?:zpool|zfs)\s+destroy\b", lowered):
        return True
    if re.search(r"\b(?:lvremove|vgremove|pvremove)\b", lowered):
        return True
    if re.search(r"\bmdadm\b[^\n]*--zero-superblock\b", lowered):
        return True
    if re.search(r"\bparted\b[^\n]*\b(?:mklabel|mkpart|rm)\b", lowered):
        return True
    if re.search(r"\bfdisk\s+/dev/", lowered):
        return True
    return False


def _finding(code: str, block: int, line: int, text: str, message: str) -> dict:
    return {
        "code": code,
        "block": block,
        "line": line,
        "text": text,
        "message": message,
    }


def analyze_source(source: str) -> dict:
    findings: list[dict] = []
    code_blocks = 0
    command_lines = 0
    privileged_lines = 0
    destructive_lines = 0

    for block_index, match in enumerate(_CODE_RE.finditer(source), start=1):
        code_blocks += 1
        body = visible_text(match.group("body"))
        context_raw = source[max(0, match.start() - 1200) : min(len(source), match.end() + 800)]
        context = visible_text(context_raw)
        safety_context = _has_safety_context(context)

        for line_number, raw_line in enumerate(body.splitlines(), start=1):
            line = _normalize_line(raw_line)
            if not line or line.startswith("#"):
                continue
            command_lines += 1
            if re.match(r"^sudo\b", line, re.IGNORECASE):
                privileged_lines += 1

            if _REMOTE_PIPE_RE.search(line):
                findings.append(
                    _finding(
                        "remote_pipe_shell",
                        block_index,
                        line_number,
                        line,
                        "remote download is piped directly into a shell",
                    )
                )
            if _CHMOD_777_RE.search(line):
                findings.append(
                    _finding(
                        "chmod_world_writable",
                        block_index,
                        line_number,
                        line,
                        "world-writable mode 777 is not acceptable as a copy-paste default",
                    )
                )
            if _CATASTROPHIC_RM_RE.search(line):
                findings.append(
                    _finding(
                        "catastrophic_rm",
                        block_index,
                        line_number,
                        line,
                        "recursive forced removal targets a root/system path",
                    )
                )
            if _RECURSIVE_ROOT_PERM_RE.search(line):
                findings.append(
                    _finding(
                        "recursive_root_permissions",
                        block_index,
                        line_number,
                        line,
                        "recursive chmod/chown targets a root/system path",
                    )
                )
            if _PRIVILEGED_REDIRECT_RE.search(line):
                findings.append(
                    _finding(
                        "privileged_redirection",
                        block_index,
                        line_number,
                        line,
                        "sudo does not elevate the shell redirection; use a root-aware writer such as tee",
                    )
                )
            if _INSECURE_TLS_RE.search(line):
                findings.append(
                    _finding(
                        "insecure_tls",
                        block_index,
                        line_number,
                        line,
                        "TLS certificate verification is disabled",
                    )
                )
            if _LITERAL_SECRET_RE.search(line):
                findings.append(
                    _finding(
                        "literal_secret_example",
                        block_index,
                        line_number,
                        line,
                        "example uses a weak literal credential instead of a clear placeholder",
                    )
                )
            if _is_destructive_storage_command(line):
                destructive_lines += 1
                if not safety_context:
                    findings.append(
                        _finding(
                            "destructive_without_context",
                            block_index,
                            line_number,
                            line,
                            "destructive storage command lacks nearby backup/rollback/verification context",
                        )
                    )

    return {
        "code_blocks": code_blocks,
        "command_lines": command_lines,
        "privileged_lines": privileged_lines,
        "destructive_lines": destructive_lines,
        "findings": findings,
    }


def collect() -> list[dict]:
    posts: list[dict] = []
    for raw_path in glob.glob(POSTS_GLOB):
        path = Path(raw_path)
        source = path.read_text(encoding="utf-8")
        meta = postmeta.read_meta(str(path))
        posts.append(
            {
                "issue": int(meta["issue"]),
                "title": str(meta["title"]).strip(),
                "path": path.relative_to(ROOT).as_posix(),
                **analyze_source(source),
            }
        )
    posts.sort(key=lambda item: item["issue"])
    return posts


def _is_blocking(issue: int, code: str) -> bool:
    return code in BLOCK_ALWAYS or (issue >= FUTURE_ENFORCEMENT_ISSUE and code in BLOCK_FROM_020)


def review(posts: list[dict] | None = None) -> dict:
    posts = posts if posts is not None else collect()
    blockers: list[dict] = []
    review_queue: list[dict] = []
    code_blocks = 0
    command_lines = 0
    privileged_lines = 0
    destructive_lines = 0

    for post in posts:
        code_blocks += int(post.get("code_blocks", 0))
        command_lines += int(post.get("command_lines", 0))
        privileged_lines += int(post.get("privileged_lines", 0))
        destructive_lines += int(post.get("destructive_lines", 0))
        issue = int(post["issue"])
        for finding in post.get("findings", []):
            enriched = {"issue": issue, "title": post.get("title", ""), **finding}
            if _is_blocking(issue, str(finding["code"])):
                blockers.append(enriched)
            else:
                review_queue.append(enriched)

    return {
        "posts": posts,
        "total_posts": len(posts),
        "code_blocks": code_blocks,
        "command_lines": command_lines,
        "privileged_lines": privileged_lines,
        "destructive_lines": destructive_lines,
        "blockers": blockers,
        "review_queue": review_queue,
    }


def errors(result: dict) -> list[str]:
    problems: list[str] = []
    for finding in result["blockers"]:
        problems.append(
            f"#{finding['issue']:03d} [{finding['code']}] block {finding['block']} "
            f"line {finding['line']}: {finding['text']}"
        )
    return problems


def run() -> int:
    result = review()
    problems = errors(result)
    if problems:
        print(f"LỖI: command/config quality có {len(problems)} blocker")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print(
        "OK: command/config quality pass; "
        f"posts={result['total_posts']}, code_blocks={result['code_blocks']}, "
        f"command_lines={result['command_lines']}, privileged={result['privileged_lines']}, "
        f"destructive={result['destructive_lines']}, historical_review={len(result['review_queue'])}."
    )
    if result["review_queue"]:
        print("Historical review queue (non-blocking before #020):")
        for finding in result["review_queue"]:
            print(
                f"- #{finding['issue']:03d} [{finding['code']}] "
                f"block {finding['block']} line {finding['line']}: {finding['text']}"
            )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    return run()


if __name__ == "__main__":
    raise SystemExit(main())

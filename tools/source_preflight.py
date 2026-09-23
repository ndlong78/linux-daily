#!/usr/bin/env python3
"""Báo MỌI lỗi source-of-truth trong một lượt, trước khi materialize.

Vì sao tool này tồn tại
-----------------------
`publish.py prepare` là một pipeline vừa sinh vừa kiểm, và nó dừng ở bước hỏng
đầu tiên. Với agent API-only — không chạy được Python, chỉ push rồi chờ workflow
— mỗi thiếu sót vì thế tốn trọn một vòng push → dispatch → materialize → đọc log.

Bài #084 đã trả giá đúng như vậy: bốn lượt chạy đỏ liên tiếp, mỗi lượt lộ ra
đúng MỘT thiếu sót mới (layout ld-meta, learning coverage, dòng topics.md, rồi
lab contract). Không lượt nào sai; cái sai là chúng phải xếp hàng.

Tool này chạy mọi phép kiểm chỉ cần SOURCE — không cần artifact đã dựng — và
luôn chạy hết, kể cả khi một phép kiểm đã đỏ. Một lần chạy cho ra danh sách đầy
đủ việc phải làm.

Read-only: không ghi file, không sinh artifact. Không thay thế `publish.py
check` — cổng đó vẫn kiểm artifact byte-exact sau khi materialize.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
TOPICS_PATH = os.path.join(ROOT, "topics.md")
STATE_PATH = os.path.join(ROOT, "state.json")

TOPIC_LINE_RE = re.compile(r"^#(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$")
POST_FILE_RE = re.compile(r"post-(\d{3})-.*\.html$")
LD_META_RE = re.compile(
    r'<script type="application/json" id="ld-meta">\s*(\{.*?\})\s*</script>', re.S
)

# Validator chỉ đọc source. Cố ý KHÔNG gọi validate_fonts.py hay validate_site.py:
# chúng kiểm artifact đã dựng, nên chạy trước materialize sẽ báo động giả.
SUBPROCESS_CHECKS = (
    ("STYLE.md", "validate_style.py"),
    ("Lab contract", "lab_contract.py"),
    ("Source-backed review", "validate_sources.py"),
    ("Learning metadata", "learning_metadata.py"),
)


def _posts() -> list[str]:
    return sorted(glob.glob(os.path.join(POSTS_DIR, "post-*.html")))


def check_ld_meta() -> list[str]:
    """Mỗi bài phải có khối ld-meta đọc được và khai đúng số hiệu của tên file."""
    errors: list[str] = []
    for path in _posts():
        rel = os.path.relpath(path, ROOT)
        name_match = POST_FILE_RE.search(os.path.basename(path))
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        match = LD_META_RE.search(text)
        if match is None:
            errors.append(f"{rel}: thiếu hoặc sai khuôn khối <script id=\"ld-meta\">")
            continue
        try:
            meta = json.loads(match.group(1))
        except ValueError as exc:
            errors.append(f"{rel}: ld-meta không phải JSON hợp lệ ({exc})")
            continue
        if name_match and meta.get("issue") != int(name_match.group(1)):
            errors.append(
                f"{rel}: ld-meta.issue ({meta.get('issue')}) khác số hiệu trong tên file "
                f"(#{name_match.group(1)})"
            )
    return errors


def _read_topics() -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    entries: list[dict] = []
    if not os.path.exists(TOPICS_PATH):
        return entries, ["topics.md: không tồn tại"]
    with open(TOPICS_PATH, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            match = TOPIC_LINE_RE.match(raw.strip())
            if match:
                entries.append(
                    {
                        "n": int(match.group(1)),
                        "date_s": match.group(2).strip(),
                        "axis": match.group(3).strip(),
                        "title": match.group(4).strip(),
                        "lineno": lineno,
                    }
                )
    entries.sort(key=lambda e: e["n"])
    return entries, errors


def check_source_of_truth() -> list[str]:
    """topics.md ↔ posts/ ↔ state.json phải khớp nhau.

    Đây là phép kiểm đã chặn #084 ở lượt thứ ba: posts/ có #084 nhưng topics.md
    dừng ở #083, nên state.json cũng lệch theo.
    """
    entries, errors = _read_topics()
    if not entries:
        return errors or ["topics.md: không có dòng bài nào hợp lệ"]

    topic_nums = {e["n"] for e in entries}
    file_nums = {
        int(m.group(1))
        for path in _posts()
        if (m := POST_FILE_RE.search(os.path.basename(path)))
    }
    for n in sorted(topic_nums - file_nums):
        errors.append(f"topics.md có #{n:03d} nhưng posts/ không có file tương ứng")
    for n in sorted(file_nums - topic_nums):
        errors.append(
            f"posts/ có #{n:03d} nhưng topics.md thiếu dòng cho bài này "
            "(thêm `#NNN | YYYY-MM-DD | Trục | Tiêu đề`)"
        )

    last = max(entries, key=lambda e: e["n"])
    try:
        with open(STATE_PATH, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError) as exc:
        return errors + [f"state.json: không đọc được ({exc})"]

    if state.get("last_issue") != last["n"]:
        errors.append(
            f"state.json.last_issue ({state.get('last_issue')}) khác bài mới nhất "
            f"trong topics.md (#{last['n']:03d})"
        )
    if state.get("last_published_date") != last["date_s"]:
        errors.append(
            f"state.json.last_published_date ({state.get('last_published_date')}) khác "
            f"ngày của bài mới nhất trong topics.md ({last['date_s']})"
        )

    for entry in entries:
        try:
            dt.date.fromisoformat(entry["date_s"])
        except ValueError:
            errors.append(
                f"topics.md dòng {entry['lineno']}: ngày '{entry['date_s']}' không phải ISO YYYY-MM-DD"
            )
    return errors


# Dòng thật sự là lỗi trong output của validator. Phần còn lại là thống kê —
# giữ lại chỉ làm loãng danh sách việc cần làm.
ERROR_LINE_RE = re.compile(r"^\s*(?:LỖI|ERROR|✗|-\s)", re.IGNORECASE)


def _run_validator(script: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, os.path.join("tools", script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def _error_lines(output: str, script: str, code: int) -> list[str]:
    """Rút dòng lỗi; không nhận ra khuôn nào thì trả nguyên output.

    Thà ồn còn hơn nuốt mất lỗi: một validator đổi định dạng output không được
    phép làm preflight báo xanh.
    """
    picked = [ln.strip() for ln in output.splitlines() if ERROR_LINE_RE.match(ln)]
    if picked:
        return picked
    return [ln for ln in output.splitlines() if ln.strip()] or [
        f"{script} trả exit code {code}"
    ]


def collect() -> list[tuple[str, list[str]]]:
    """Chạy HẾT mọi phép kiểm, kể cả sau khi đã có lỗi. Đó là toàn bộ mục đích."""
    results: list[tuple[str, list[str]]] = [
        ("ld-meta", check_ld_meta()),
        ("Source of truth", check_source_of_truth()),
    ]
    for label, script in SUBPROCESS_CHECKS:
        code, output = _run_validator(script)
        results.append((label, [] if code == 0 else _error_lines(output, script, code)))
    return results


def run(*, json_output: bool = False) -> int:
    results = collect()
    total = sum(len(errs) for _, errs in results)

    if json_output:
        print(json.dumps(
            {"errors": total, "checks": [{"name": n, "errors": e} for n, e in results]},
            ensure_ascii=False,
            indent=2,
        ))
        return 1 if total else 0

    print("Linux Daily — Source Preflight")
    print("==============================")
    for name, errs in results:
        print(f"[{'FAIL' if errs else ' OK '}] {name}")
        for err in errs:
            print(f"       - {err}")
    print()
    if total:
        print(f"FAIL: {total} lỗi source-of-truth. Sửa HẾT rồi mới push lại —")
        print("      danh sách trên là đầy đủ, không phải lỗi đầu tiên trong hàng.")
        return 1
    print("OK: source sẵn sàng để materialize.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="In kết quả dạng JSON.")
    args = parser.parse_args(argv)
    return run(json_output=args.json)


if __name__ == "__main__":
    raise SystemExit(main())

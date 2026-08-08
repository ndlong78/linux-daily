#!/usr/bin/env python3
"""Review Linux Daily content mix and cadence from canonical post metadata."""
from __future__ import annotations

import argparse
import glob
from collections import Counter
from pathlib import Path

import postmeta
import taxonomy

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
REPORT_PATH = ROOT / "docs" / "content-mix-report.md"


def collect() -> list[dict]:
    posts: list[dict] = []
    for raw in glob.glob(POSTS_GLOB):
        path = Path(raw)
        meta = postmeta.read_meta(str(path))
        posts.append(
            {
                "issue": int(meta["issue"]),
                "date": str(meta["date"]),
                "axis": str(meta["axis"]).strip(),
                "title": str(meta["title"]).strip(),
            }
        )
    posts.sort(key=lambda item: item["issue"])
    return posts


def review(posts: list[dict] | None = None) -> dict:
    posts = posts if posts is not None else collect()
    axis_order = list(taxonomy.load_taxonomy()["axes"])
    counts = Counter(item["axis"] for item in posts)
    unknown = sorted(set(counts) - set(axis_order))

    sequence_errors: list[str] = []
    for index, item in enumerate(posts):
        expected = axis_order[index % len(axis_order)]
        if item["axis"] != expected:
            sequence_errors.append(
                f"#{item['issue']:03d}: expected {expected}, found {item['axis']}"
            )

    values = [counts.get(axis, 0) for axis in axis_order]
    spread = max(values) - min(values) if values else 0
    next_axis = axis_order[len(posts) % len(axis_order)] if axis_order else ""

    return {
        "posts": len(posts),
        "axis_order": axis_order,
        "counts": dict(counts),
        "spread": spread,
        "unknown_axes": unknown,
        "sequence_errors": sequence_errors,
        "next_issue": (posts[-1]["issue"] + 1) if posts else 1,
        "next_axis": next_axis,
        "complete_cycles": len(posts) // len(axis_order) if axis_order else 0,
        "cycle_remainder": len(posts) % len(axis_order) if axis_order else 0,
    }


def errors(result: dict) -> list[str]:
    problems: list[str] = []
    if result["unknown_axes"]:
        problems.append("unknown axes: " + ", ".join(result["unknown_axes"]))
    if result["sequence_errors"]:
        problems.extend(result["sequence_errors"])
    if result["spread"] > 1:
        problems.append(f"axis distribution spread is {result['spread']} (> 1)")
    return problems


def render_report(result: dict | None = None) -> str:
    result = result if result is not None else review()
    labels = taxonomy.load_taxonomy()["axes"]
    lines = [
        "# Linux Daily — Content Mix Review",
        "",
        "> Báo cáo này được sinh deterministic từ `ld-meta.axis` của các bài và thứ tự canonical trong `taxonomy.json`.",
        "",
        "## Snapshot",
        "",
        f"- Published posts: **{result['posts']}**",
        f"- Complete 7-axis cycles: **{result['complete_cycles']}**",
        f"- Current-cycle progress: **{result['cycle_remainder']}/7**",
        f"- Distribution spread: **{result['spread']}**",
        f"- Next expected issue: **#{result['next_issue']:03d} — {labels[result['next_axis']]['label']}**",
        "",
        "| Axis | Posts | Share |",
        "|---|---:|---:|",
    ]
    total = result["posts"] or 1
    for axis in result["axis_order"]:
        count = result["counts"].get(axis, 0)
        lines.append(f"| {labels[axis]['label']} | {count} | {count / total:.1%} |")

    lines.extend(
        [
            "",
            "## Findings",
            "",
            "- Mix hiện cân bằng theo cadence 7 trục: chênh lệch giữa axis nhiều nhất và ít nhất không quá 1 bài.",
            "- Phần lệch 3-vs-2 là trạng thái tự nhiên của một chu kỳ chưa hoàn tất, không phải thiếu hụt cần backfill nhân tạo.",
            "- Issue order vẫn đi đúng canonical axis rotation; đây là guardrail phù hợp hơn việc ép mọi axis luôn có số lượng bằng nhau.",
            "",
            "## Recommendation",
            "",
            f"Tiếp tục cadence hiện tại. Bài kế tiếp nên là **#{result['next_issue']:03d} — {labels[result['next_axis']]['label']}**; không cần chèn bài chỉ để làm phẳng thống kê. Review lại mix khi hoàn tất thêm một chu kỳ 7 bài hoặc khi thay đổi taxonomy/cadence.",
            "",
        ]
    )
    return "\n".join(lines)


def run(*, check: bool) -> int:
    result = review()
    problems = errors(result)
    if problems:
        print(f"LỖI: content mix có {len(problems)} vấn đề")
        for problem in problems:
            print(f"- {problem}")
        return 1

    expected = render_report(result)
    current = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.exists() else ""
    if check and current != expected:
        print("LỖI: docs/content-mix-report.md chưa đồng bộ. Chạy `python tools/content_mix.py`.")
        return 1
    if not check:
        REPORT_PATH.write_text(expected, encoding="utf-8")
        print(f"Đã cập nhật content mix report cho {result['posts']} bài.")
    else:
        print(
            f"OK: content mix cân bằng; {result['posts']} bài, spread={result['spread']}, "
            f"next=#{result['next_issue']:03d} {result['next_axis']}."
        )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail nếu report hoặc cadence mix bị drift.")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

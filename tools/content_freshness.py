#!/usr/bin/env python3
"""Track Linux Daily content freshness without rewriting historical posts."""
from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import postmeta

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
POLICY_PATH = ROOT / "freshness.json"
ALLOWED_VOLATILITY = {"high", "medium", "low"}
ALLOWED_DECLARED_STATES = {"current", "historically-valid", "superseded"}
MERGEABLE_REVIEW_STATUSES = {"reviewed", "published"}


def load_policy(path: Path = POLICY_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect() -> list[dict]:
    posts: list[dict] = []
    for raw_path in glob.glob(POSTS_GLOB):
        path = Path(raw_path)
        meta = postmeta.read_meta(str(path))
        posts.append(
            {
                "issue": int(meta["issue"]),
                "date": str(meta["date"]),
                "axis": str(meta["axis"]).strip(),
                "title": str(meta["title"]).strip(),
                "review_status": meta.get("review_status"),
                "path": path.relative_to(ROOT).as_posix(),
            }
        )
    posts.sort(key=lambda item: item["issue"])
    return posts


def _parse_date(value: object, label: str, problems: list[str]) -> date | None:
    if not isinstance(value, str):
        problems.append(f"{label} phải là YYYY-MM-DD, đang là {value!r}")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        problems.append(f"{label} không phải ngày ISO hợp lệ: {value!r}")
        return None


def review(
    *,
    as_of: date | None = None,
    posts: list[dict] | None = None,
    policy: dict | None = None,
) -> dict:
    as_of = as_of or date.today()
    posts = posts if posts is not None else collect()
    policy = policy if policy is not None else load_policy()
    problems: list[str] = []

    windows = policy.get("review_windows_days")
    if not isinstance(windows, dict):
        problems.append("freshness.json: review_windows_days phải là object")
        windows = {}
    normalized_windows: dict[str, int] = {}
    for volatility in ALLOWED_VOLATILITY:
        value = windows.get(volatility)
        if not isinstance(value, int) or value <= 0:
            problems.append(
                f"freshness.json: review_windows_days.{volatility} phải là số nguyên dương"
            )
        else:
            normalized_windows[volatility] = value

    axis_policy = policy.get("axis_policy")
    if not isinstance(axis_policy, dict):
        problems.append("freshness.json: axis_policy phải là object")
        axis_policy = {}

    effective_from = policy.get("effective_from_issue")
    if not isinstance(effective_from, int) or effective_from <= 0:
        problems.append("freshness.json: effective_from_issue phải là số nguyên dương")
        effective_from = 20

    overrides_raw = policy.get("overrides", {})
    if not isinstance(overrides_raw, dict):
        problems.append("freshness.json: overrides phải là object")
        overrides_raw = {}

    posts_by_issue = {int(post["issue"]): post for post in posts}
    overrides: dict[int, dict] = {}
    for raw_issue, raw_override in overrides_raw.items():
        try:
            issue = int(raw_issue)
        except (TypeError, ValueError):
            problems.append(f"freshness.json: override key không phải issue hợp lệ: {raw_issue!r}")
            continue
        if issue not in posts_by_issue:
            problems.append(f"freshness.json: override tham chiếu issue không tồn tại: #{issue:03d}")
            continue
        if not isinstance(raw_override, dict):
            problems.append(f"freshness.json: override #{issue:03d} phải là object")
            continue
        overrides[issue] = raw_override

    items: list[dict] = []
    for post in posts:
        issue = int(post["issue"])
        published = _parse_date(post.get("date"), f"#{issue:03d} date", problems)
        axis = str(post.get("axis", ""))
        axis_rule = axis_policy.get(axis)
        if not isinstance(axis_rule, dict):
            problems.append(f"#{issue:03d}: axis {axis!r} chưa có freshness policy")
            continue

        volatility = axis_rule.get("volatility")
        if volatility not in ALLOWED_VOLATILITY:
            problems.append(
                f"#{issue:03d}: volatility của axis {axis!r} phải là high/medium/low"
            )
            continue
        window_days = normalized_windows.get(volatility)
        if window_days is None or published is None:
            continue

        override = overrides.get(issue, {})
        declared_state = override.get("state", "current")
        if declared_state not in ALLOWED_DECLARED_STATES:
            problems.append(
                f"#{issue:03d}: override.state phải là current, historically-valid hoặc superseded, "
                f"đang là {declared_state!r}"
            )
            declared_state = "current"

        last_reviewed = published
        if "last_reviewed" in override:
            parsed = _parse_date(
                override.get("last_reviewed"), f"#{issue:03d} last_reviewed", problems
            )
            if parsed is not None:
                last_reviewed = parsed
        if published is not None and last_reviewed < published:
            problems.append(
                f"#{issue:03d}: last_reviewed {last_reviewed} không thể trước ngày xuất bản {published}"
            )

        reason = override.get("reason")
        if declared_state in {"historically-valid", "superseded"} and not (
            isinstance(reason, str) and reason.strip()
        ):
            problems.append(
                f"#{issue:03d}: {declared_state} bắt buộc có override.reason giải thích"
            )

        replacement_issue = override.get("replacement_issue")
        if replacement_issue is not None:
            if not isinstance(replacement_issue, int) or replacement_issue not in posts_by_issue:
                problems.append(
                    f"#{issue:03d}: replacement_issue phải tham chiếu một issue đang tồn tại"
                )
            elif replacement_issue <= issue:
                problems.append(
                    f"#{issue:03d}: replacement_issue phải mới hơn issue nguồn, đang là #{replacement_issue:03d}"
                )
        if declared_state == "superseded" and replacement_issue is None:
            problems.append(f"#{issue:03d}: superseded bắt buộc có replacement_issue")

        if issue >= effective_from and post.get("review_status") not in MERGEABLE_REVIEW_STATUSES:
            problems.append(
                f"#{issue:03d}: bài mới phải có review_status=reviewed/published trước khi merge"
            )

        review_due_on = last_reviewed + timedelta(days=window_days)
        if declared_state == "historically-valid":
            effective_state = "historically-valid"
        elif declared_state == "superseded":
            effective_state = "superseded"
        elif as_of > review_due_on:
            effective_state = "review-due"
        else:
            effective_state = "current"

        items.append(
            {
                **post,
                "volatility": volatility,
                "review_window_days": window_days,
                "last_reviewed": last_reviewed.isoformat(),
                "review_due_on": review_due_on.isoformat(),
                "declared_state": declared_state,
                "state": effective_state,
                "reason": reason.strip() if isinstance(reason, str) else "",
                "replacement_issue": replacement_issue,
            }
        )

    counts = Counter(item["state"] for item in items)
    volatility_counts = Counter(item["volatility"] for item in items)
    return {
        "as_of": as_of.isoformat(),
        "effective_from_issue": effective_from,
        "posts": items,
        "total": len(items),
        "counts": dict(counts),
        "volatility_counts": dict(volatility_counts),
        "review_due": [item for item in items if item["state"] == "review-due"],
        "historically_valid": [
            item for item in items if item["state"] == "historically-valid"
        ],
        "superseded": [item for item in items if item["state"] == "superseded"],
        "errors": problems,
    }


def render_text(result: dict) -> str:
    lines = [
        "Linux Daily — Content Freshness & Technical Drift",
        "=" * 49,
        f"as_of                {result['as_of']}",
        f"posts                {result['total']}",
        f"current              {result['counts'].get('current', 0)}",
        f"review_due           {result['counts'].get('review-due', 0)}",
        f"historically_valid   {result['counts'].get('historically-valid', 0)}",
        f"superseded           {result['counts'].get('superseded', 0)}",
    ]
    if result["review_due"]:
        lines.extend(["", "Review queue:"])
        for item in result["review_due"]:
            lines.append(
                f"- #{item['issue']:03d} {item['title']} — due {item['review_due_on']} "
                f"({item['volatility']})"
            )
    if result["historically_valid"]:
        lines.extend(["", "Historically valid:"])
        for item in result["historically_valid"]:
            suffix = (
                f"; replacement #{item['replacement_issue']:03d}"
                if item["replacement_issue"] is not None
                else ""
            )
            lines.append(f"- #{item['issue']:03d} — {item['reason']}{suffix}")
    if result["superseded"]:
        lines.extend(["", "Superseded:"])
        for item in result["superseded"]:
            lines.append(
                f"- #{item['issue']:03d} -> #{item['replacement_issue']:03d} — {item['reason']}"
            )
    return "\n".join(lines)


def run(*, as_of: date | None, json_output: bool, fail_review_due: bool) -> int:
    result = review(as_of=as_of)
    if result["errors"]:
        print(f"LỖI: freshness policy có {len(result['errors'])} vấn đề")
        for problem in result["errors"]:
            print(f"- {problem}")
        return 1

    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))

    if fail_review_due and result["review_due"]:
        print(f"LỖI: có {len(result['review_due'])} bài quá hạn technical freshness review")
        return 1
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--as-of",
        help="Ngày đánh giá YYYY-MM-DD; mặc định là ngày chạy. Dùng để audit/test reproducible.",
    )
    parser.add_argument("--json", action="store_true", help="Xuất structured JSON cho dashboard/audit.")
    parser.add_argument(
        "--fail-review-due",
        action="store_true",
        help="Tùy chọn strict mode cho audit; publish CI không dùng để tránh time-bomb build.",
    )
    args = parser.parse_args(argv)
    as_of = None
    if args.as_of:
        try:
            as_of = date.fromisoformat(args.as_of)
        except ValueError:
            parser.error("--as-of phải là YYYY-MM-DD hợp lệ")
    return run(as_of=as_of, json_output=args.json, fail_review_due=args.fail_review_due)


if __name__ == "__main__":
    raise SystemExit(main())

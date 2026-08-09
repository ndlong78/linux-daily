#!/usr/bin/env python3
"""Normalize the legacy Linux Daily publication timeline to 2026-07-01..2026-07-21.

This is intentionally a bounded migration tool. It never renumbers issues or changes
post URLs/content semantics. For issues #001..#021 it updates only:

- ld-meta.date inside each post;
- the visible masthead date (DD·MM·YYYY);
- state.json publication clock when --apply is used.

Generated public artifacts remain owned by ``python tools/publish.py prepare`` and
must be regenerated after applying the migration.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "posts"
STATE_PATH = ROOT / "state.json"
START_ISSUE = 1
END_ISSUE = 21
START_DATE = date(2026, 7, 1)

META_DATE_RE = re.compile(r'(?P<prefix>"date"\s*:\s*")(?P<date>\d{4}-\d{2}-\d{2})(?P<suffix>")')
VISIBLE_DATE_RE = re.compile(
    r'(?P<prefix><span class="issue">#(?P<issue>\d{3})\s*·\s*)'
    r'(?P<date>\d{2}·\d{2}·\d{4})(?P<suffix></span>)'
)


@dataclass(frozen=True)
class TimelineEntry:
    issue: int
    path: Path
    current_date: date
    target_date: date


def target_date(issue: int) -> date:
    if not START_ISSUE <= issue <= END_ISSUE:
        raise ValueError(f"issue #{issue:03d} outside historical migration range")
    return START_DATE + timedelta(days=issue - START_ISSUE)


def _load_post(path: Path) -> tuple[int, date, str]:
    text = path.read_text(encoding="utf-8")
    meta_match = META_DATE_RE.search(text)
    visible_match = VISIBLE_DATE_RE.search(text)
    if meta_match is None:
        raise ValueError(f"{path}: missing ld-meta date")
    if visible_match is None:
        raise ValueError(f"{path}: missing visible issue/date masthead")

    issue = int(visible_match.group("issue"))
    metadata_date = date.fromisoformat(meta_match.group("date"))
    visible_date = datetime.strptime(visible_match.group("date"), "%d·%m·%Y").date()
    if metadata_date != visible_date:
        raise ValueError(
            f"{path}: metadata date {metadata_date} != visible date {visible_date}"
        )
    return issue, metadata_date, text


def discover_entries() -> list[TimelineEntry]:
    entries: list[TimelineEntry] = []
    seen: set[int] = set()
    for path in sorted(POST_DIR.glob("post-*.html")):
        issue, current_date, _ = _load_post(path)
        if issue > END_ISSUE:
            continue
        if issue in seen:
            raise ValueError(f"duplicate historical issue #{issue:03d}")
        seen.add(issue)
        entries.append(
            TimelineEntry(
                issue=issue,
                path=path,
                current_date=current_date,
                target_date=target_date(issue),
            )
        )

    expected = set(range(START_ISSUE, END_ISSUE + 1))
    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        raise ValueError(f"historical issue set mismatch: missing={missing}, extra={extra}")
    return sorted(entries, key=lambda item: item.issue)


def render_post(entry: TimelineEntry) -> str:
    issue, current_date, text = _load_post(entry.path)
    if issue != entry.issue or current_date != entry.current_date:
        raise ValueError(f"{entry.path}: post changed while migration was running")

    iso_old = entry.current_date.isoformat()
    iso_new = entry.target_date.isoformat()
    visible_old = entry.current_date.strftime("%d·%m·%Y")
    visible_new = entry.target_date.strftime("%d·%m·%Y")

    old_meta = f'"date": "{iso_old}"'
    new_meta = f'"date": "{iso_new}"'
    if text.count(old_meta) != 1:
        raise ValueError(
            f"{entry.path}: expected exactly one metadata date {iso_old}, "
            f"found {text.count(old_meta)}"
        )
    text = text.replace(old_meta, new_meta, 1)

    old_visible = f"#{entry.issue:03d} · {visible_old}"
    new_visible = f"#{entry.issue:03d} · {visible_new}"
    if text.count(old_visible) != 1:
        raise ValueError(
            f"{entry.path}: expected exactly one visible date {old_visible!r}, "
            f"found {text.count(old_visible)}"
        )
    return text.replace(old_visible, new_visible, 1)


def expected_state() -> dict[str, object]:
    last_date = target_date(END_ISSUE)
    # 07:00 Asia/Ho_Chi_Minh == 00:00 UTC in July 2026.
    generated_at = datetime.combine(last_date, time(0, 0), tzinfo=timezone.utc)
    return {
        "last_issue": END_ISSUE,
        "last_published_date": last_date.isoformat(),
        "last_generated_at": generated_at.isoformat(),
    }


def check_state() -> list[str]:
    current = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    expected = expected_state()
    errors: list[str] = []
    for key, value in expected.items():
        if current.get(key) != value:
            errors.append(f"state.{key}: {current.get(key)!r} != {value!r}")
    return errors


def apply(entries: list[TimelineEntry]) -> None:
    for entry in entries:
        entry.path.write_text(render_post(entry), encoding="utf-8")
    STATE_PATH.write_text(
        json.dumps(expected_state(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def verify(entries: list[TimelineEntry]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        if entry.current_date != entry.target_date:
            errors.append(
                f"#{entry.issue:03d} {entry.path.name}: "
                f"{entry.current_date} != {entry.target_date}"
            )
    errors.extend(check_state())
    return errors


def print_plan(entries: list[TimelineEntry]) -> None:
    print("Linux Daily — Historical Publication Timeline")
    print("=============================================")
    for entry in entries:
        marker = "=" if entry.current_date == entry.target_date else "→"
        print(
            f"#{entry.issue:03d}  {entry.current_date.isoformat()} "
            f"{marker} {entry.target_date.isoformat()}  {entry.path.name}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="rewrite posts and state.json")
    mode.add_argument("--check", action="store_true", help="fail unless migration is complete")
    args = parser.parse_args()

    entries = discover_entries()
    print_plan(entries)

    if args.apply:
        apply(entries)
        print("\nApplied source timeline normalization.")
        print("Next: python tools/publish.py prepare")
        return 0

    if args.check:
        errors = verify(entries)
        if errors:
            print("\nTimeline normalization incomplete:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("\nOK: #001..#021 map contiguously to 2026-07-01..2026-07-21.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

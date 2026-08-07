#!/usr/bin/env python3
"""
cadence.py — Quản lý nhịp phát hành Linux Daily qua state.json.

Vì sao cần state.json? Cổng nhịp cũ (Bước 0 của SKILL.md) đọc NGÀY của bài mới
nhất trong topics.md — mà ngày đó do AI tự ghi, có thể sai hoặc backdate. state.json
ghi lại thời điểm THỰC mà routine sinh bài (last_generated_at, mốc UTC do máy đặt),
nên quyết định "đã tới nhịp chưa" đáng tin hơn nhiều.

state.json (ở gốc repo):
  {
    "last_issue": 18,
    "last_published_date": "2026-08-07",
    "last_generated_at": "2026-08-07T00:00:00+00:00"
  }

Lệnh:
  cadence.py status                  # tóm tắt trạng thái + cổng nhịp
  cadence.py next                    # in số bài kế tiếp (last_issue + 1)
  cadence.py gate [--interval N]     # exit 0 nếu ĐÃ tới nhịp (≥ N ngày kể từ
                                     #   last_generated_at); exit 10 nếu CHƯA
  cadence.py init [--force] [--at ISO]   # dựng state.json từ topics.md (bootstrap)
  cadence.py record [--issue N] [--date YYYY-MM-DD] [--at ISO]
                                     # cập nhật state.json sau khi sinh bài xong

Cổng nhịp dùng exit code để SKILL/CI dễ rẽ nhánh:
  0  = tới nhịp, cứ tạo bài
  10 = chưa tới nhịp, bỏ qua hôm nay
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS_PATH = os.path.join(ROOT, "topics.md")
STATE_PATH = os.path.join(ROOT, "state.json")

DEFAULT_INTERVAL_DAYS = 2
GATE_NOT_DUE = 10  # exit code khi chưa tới nhịp

TOPIC_LINE_RE = re.compile(r"^#(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$")


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def read_topics(path: str | None = None) -> list[dict]:
    """Đọc topics.md thành danh sách bài (đã sắp theo số bài). Bỏ qua dòng chú thích."""
    path = path or TOPICS_PATH
    entries: list[dict] = []
    if not os.path.exists(path):
        return entries
    with open(path, encoding="utf-8") as f:
        for raw in f:
            m = TOPIC_LINE_RE.match(raw.strip())
            if m:
                num, date_s, axis, title = m.groups()
                entries.append({
                    "n": int(num),
                    "date_s": date_s.strip(),
                    "axis": axis.strip(),
                    "title": title.strip(),
                })
    entries.sort(key=lambda e: e["n"])
    return entries


def state_from_topics(path: str | None = None, generated_at: str | None = None) -> dict:
    """Suy state.json từ topics.md. generated_at mặc định = bây giờ (UTC)."""
    entries = read_topics(path)
    gen = generated_at or _now().isoformat()
    if not entries:
        return {"last_issue": 0, "last_published_date": None, "last_generated_at": gen}
    last = entries[-1]
    return {
        "last_issue": last["n"],
        "last_published_date": last["date_s"],
        "last_generated_at": gen,
    }


def load_state(path: str | None = None) -> dict | None:
    path = path or STATE_PATH
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict, path: str | None = None) -> None:
    path = path or STATE_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _parse_dt(ts: str) -> dt.datetime | None:
    try:
        d = dt.datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None
    return d.replace(tzinfo=dt.timezone.utc) if d.tzinfo is None else d


def days_since(state: dict | None, now: dt.datetime | None = None) -> int | None:
    """Số ngày (theo lịch UTC) kể từ last_generated_at; None nếu không xác định được.

    Nếu chưa có state.json thì lấy last_published_date của bài mới nhất trong
    topics.md làm mốc thay thế, để cổng nhịp vẫn hoạt động khi bootstrap.
    """
    now = now or _now()
    if state and state.get("last_generated_at"):
        gen = _parse_dt(state["last_generated_at"])
        if gen is not None:
            return (now.date() - gen.astimezone(dt.timezone.utc).date()).days
    entries = read_topics()
    if entries:
        try:
            last_date = dt.date.fromisoformat(entries[-1]["date_s"])
        except ValueError:
            return None
        return (now.date() - last_date).days
    return None


def is_due(state: dict | None, interval: int = DEFAULT_INTERVAL_DAYS,
           now: dt.datetime | None = None) -> bool:
    d = days_since(state, now)
    return d is None or d >= interval


def next_issue(state: dict | None) -> int:
    if state and isinstance(state.get("last_issue"), int):
        return state["last_issue"] + 1
    entries = read_topics()
    return (entries[-1]["n"] + 1) if entries else 1


# --- lệnh ---

def cmd_status(args) -> int:
    state = load_state()
    d = days_since(state)
    due = is_due(state, args.interval)
    print(f"state.json      : {'có' if state else 'CHƯA có (suy từ topics.md)'}")
    if state:
        print(f"last_issue      : {state.get('last_issue')}")
        print(f"last_published  : {state.get('last_published_date')}")
        print(f"last_generated  : {state.get('last_generated_at')}")
    print(f"bài kế tiếp     : #{next_issue(state):03d}")
    print(f"số ngày kể từ đó: {d if d is not None else '?'}")
    print(f"cổng nhịp ({args.interval}n)  : {'TỚI NHỊP → tạo bài' if due else 'CHƯA tới → bỏ qua'}")
    return 0


def cmd_next(args) -> int:
    print(next_issue(load_state()))
    return 0


def cmd_gate(args) -> int:
    state = load_state()
    if is_due(state, args.interval):
        d = days_since(state)
        print(f"Tới nhịp (đã {d if d is not None else '?'} ngày ≥ {args.interval}). Tạo bài #{next_issue(state):03d}.")
        return 0
    d = days_since(state)
    print(f"Chưa tới nhịp (mới {d} ngày < {args.interval}). Bỏ qua hôm nay.")
    return GATE_NOT_DUE


def cmd_init(args) -> int:
    if os.path.exists(STATE_PATH) and not args.force:
        print("state.json đã tồn tại. Dùng --force để ghi đè.", file=sys.stderr)
        return 1
    # Bootstrap: mốc sinh mặc định = 00:00 UTC ngày bài mới nhất (nếu không truyền --at).
    entries = read_topics()
    default_at = f"{entries[-1]['date_s']}T00:00:00+00:00" if entries else _now().isoformat()
    state = state_from_topics(generated_at=args.at or default_at)
    save_state(state)
    print("Đã dựng state.json:", json.dumps(state, ensure_ascii=False))
    return 0


def cmd_record(args) -> int:
    gen = args.at or _now().isoformat()
    state = state_from_topics(generated_at=gen)
    if args.issue is not None:
        state["last_issue"] = args.issue
    if args.date is not None:
        state["last_published_date"] = args.date
    save_state(state)
    print("Đã cập nhật state.json:", json.dumps(state, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Quản lý nhịp phát hành Linux Daily qua state.json.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("status", help="Tóm tắt trạng thái + cổng nhịp.")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_DAYS)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("next", help="In số bài kế tiếp.")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("gate", help="Exit 0 nếu tới nhịp, 10 nếu chưa.")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_DAYS)
    p.set_defaults(func=cmd_gate)

    p = sub.add_parser("init", help="Dựng state.json từ topics.md.")
    p.add_argument("--force", action="store_true", help="Ghi đè nếu đã có.")
    p.add_argument("--at", help="Mốc last_generated_at (ISO 8601).")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("record", help="Cập nhật state.json sau khi sinh bài.")
    p.add_argument("--issue", type=int, help="Số bài (mặc định = bài mới nhất trong topics.md).")
    p.add_argument("--date", help="Ngày xuất bản YYYY-MM-DD (mặc định = topics.md).")
    p.add_argument("--at", help="Mốc last_generated_at (ISO 8601, mặc định = bây giờ UTC).")
    p.set_defaults(func=cmd_record)

    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

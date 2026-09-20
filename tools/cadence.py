#!/usr/bin/env python3
"""
cadence.py — Quản lý nhịp phát hành Linux Daily qua state.json.

state.json ghi lại thời điểm THỰC routine sinh bài (`last_generated_at`) để quyết định
đã tới nhịp chưa. Mặc định Linux Daily phát hành **mỗi ngày một bài**; `--interval`
vẫn được giữ để operator/test có thể kiểm tra một khoảng khác khi cần.

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
  cadence.py backlog [--max-per-run N]   # số bài được phép phát hành lượt này,
                                     #   kèm (số hiệu, ngày) từng bài
  cadence.py init [--force] [--at ISO]   # dựng state.json từ topics.md (bootstrap)
  cadence.py record [--issue N] [--date YYYY-MM-DD] [--at ISO]
                                     # cập nhật state.json sau khi sinh bài xong

Cổng nhịp dùng exit code để SKILL/CI dễ rẽ nhánh:
  0  = tới nhịp, cứ tạo bài
  10 = chưa tới nhịp, bỏ qua hôm nay

Bù bài khi lỡ nhịp
------------------
Cadence mặc định là 1 bài/ngày, nhưng một lượt chạy hỏng làm `last_published_date`
tụt lại sau lịch. Nếu mỗi lượt chỉ ra đúng một bài thì khoảng tụt đó không bao giờ
co lại: ra một bài đẩy ngày lên đúng một ngày, trong khi hôm nay cũng trôi đi một
ngày. `publication_backlog()` đo khoảng tụt đó và `catchup_allowance()` cho phép
ra nhiều bài trong một lượt để bù, tối đa `CATCHUP_MAX_PER_RUN` bài.

Hai thứ giữ cho việc bù không phá contract sẵn có:

- `validate_repo.validate_topics` đã cho phép nhiều bài cùng ngày (ngày chỉ cần
  KHÔNG GIẢM) và cấm ngày ở tương lai (`d <= today_vn()`). Allowance luôn ≤ backlog
  nên ngày của bài cuối cùng trong lượt bù không bao giờ vượt hôm nay.
- Vì cổng ngày tương lai đó tính theo giờ Việt Nam, backlog ở đây cũng phải tính
  theo giờ Việt Nam. Dùng UTC sẽ lệch một ngày trong khoảng 00:00–07:00 giờ VN và
  cho phép một bài mà `validate_repo` sẽ chặn ngay sau đó.

Allowance là số **lượt phát hành**, không phải số bài trong một PR: mỗi bài vẫn đi
một branch/PR riêng và chạy tuần tự, vì `materialize-artifacts.yml` suy branch đích
từ `state.json.last_issue + 1` trên `main`. Xem `AGENTS.md` §2 "Bù bài khi đã lỡ nhịp".
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

DEFAULT_INTERVAL_DAYS = 1
GATE_NOT_DUE = 10  # exit code khi chưa tới nhịp

# Trần số bài được phát hành trong MỘT lượt chạy khi đang bù nhịp. Không có trần thì
# một đợt gián đoạn dài (nghỉ lễ, hỏng CI cả tuần) sẽ đổ hàng chục bài vào một PR,
# vượt quá khả năng review của con người và của chính agent.
CATCHUP_MAX_PER_RUN = 3

# Phải khớp `validate_repo.VN_TZ`: cổng "ngày nằm ở tương lai" của validator tính theo
# giờ Việt Nam, nên phép đo backlog cũng vậy. tests/test_cadence.py ghim hai giá trị
# này bằng nhau để chúng không trôi khỏi nhau.
VN_TZ = dt.timezone(dt.timedelta(hours=7))

TOPIC_LINE_RE = re.compile(r"^#(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$")


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def today_vn(now: dt.datetime | None = None) -> dt.date:
    """Ngày hiện tại theo giờ Việt Nam (UTC+7) — cùng mốc với validate_repo."""
    return (now or _now()).astimezone(VN_TZ).date()


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


def last_published_date(state: dict | None) -> dt.date | None:
    """Ngày của bài mới nhất, ưu tiên state.json rồi mới tới topics.md."""
    raw = (state or {}).get("last_published_date")
    for candidate in (raw, _last_topic_date_s()):
        if not candidate:
            continue
        try:
            return dt.date.fromisoformat(str(candidate))
        except ValueError:
            continue
    return None


def _last_topic_date_s() -> str | None:
    entries = read_topics()
    return entries[-1]["date_s"] if entries else None


def publication_backlog(state: dict | None, now: dt.datetime | None = None) -> int | None:
    """Số ngày bài mới nhất đang tụt sau hôm nay (giờ VN). None nếu không xác định được.

    0 nghĩa là bài mới nhất đã mang ngày hôm nay — đúng nhịp, không có gì để bù.
    Giá trị âm nghĩa là bài mới nhất mang ngày tương lai; đó là lỗi dữ liệu mà
    `validate_repo` sẽ chặn, ở đây chỉ trả về nguyên giá trị để caller thấy.
    """
    last = last_published_date(state)
    if last is None:
        return None
    return (today_vn(now) - last).days


def catchup_allowance(
    state: dict | None,
    interval: int = DEFAULT_INTERVAL_DAYS,
    now: dt.datetime | None = None,
    max_per_run: int = CATCHUP_MAX_PER_RUN,
) -> int:
    """Số bài được phép phát hành trong lượt chạy này (0 = bỏ qua hôm nay)."""
    if not is_due(state, interval, now):
        return 0
    backlog = publication_backlog(state, now)
    if backlog is None:
        # Bootstrap: chưa có mốc ngày nào để đo. Ra đúng một bài, đừng đoán.
        return 1
    return max(0, min(backlog, max_per_run))


def planned_publications(
    state: dict | None,
    interval: int = DEFAULT_INTERVAL_DAYS,
    now: dt.datetime | None = None,
    max_per_run: int = CATCHUP_MAX_PER_RUN,
) -> list[tuple[int, str]]:
    """(số hiệu, ngày YYYY-MM-DD) của từng bài được phép ra trong lượt này.

    Ngày tăng đúng một ngày mỗi bài kể từ `last_published_date`. Vì allowance luôn
    ≤ backlog nên bài cuối cùng nhiều nhất là mang ngày hôm nay, không bao giờ vượt.
    """
    count = catchup_allowance(state, interval, now, max_per_run)
    if count <= 0:
        return []
    first_issue = next_issue(state)
    last = last_published_date(state)
    if last is None:
        return [(first_issue, today_vn(now).isoformat())]
    return [
        (first_issue + offset, (last + dt.timedelta(days=offset + 1)).isoformat())
        for offset in range(count)
    ]


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
    backlog = publication_backlog(state)
    allowance = catchup_allowance(state, args.interval, max_per_run=args.max_per_run)
    print(f"tụt sau lịch    : {backlog if backlog is not None else '?'} ngày")
    print(f"được ra lượt này: {allowance} bài (trần {args.max_per_run})")
    print(f"cổng nhịp ({args.interval}n)  : {'TỚI NHỊP → tạo bài' if due else 'CHƯA tới → bỏ qua'}")
    return 0


def cmd_next(args) -> int:
    print(next_issue(load_state()))
    return 0


def cmd_gate(args) -> int:
    state = load_state()
    d = days_since(state)
    if not is_due(state, args.interval):
        print(f"Chưa tới nhịp (mới {d} ngày < {args.interval}). Bỏ qua hôm nay.")
        return GATE_NOT_DUE

    allowance = catchup_allowance(state, args.interval, max_per_run=args.max_per_run)
    head = f"Tới nhịp (đã {d if d is not None else '?'} ngày ≥ {args.interval})."
    if allowance <= 1:
        print(f"{head} Tạo bài #{next_issue(state):03d}.")
    else:
        planned = planned_publications(state, args.interval, max_per_run=args.max_per_run)
        listing = ", ".join(f"#{n:03d}/{ds}" for n, ds in planned)
        print(f"{head} Đang tụt {publication_backlog(state)} ngày → bù {allowance} bài: {listing}.")
    return 0


def cmd_backlog(args) -> int:
    state = load_state()
    backlog = publication_backlog(state)
    allowance = catchup_allowance(state, args.interval, max_per_run=args.max_per_run)
    planned = planned_publications(state, args.interval, max_per_run=args.max_per_run)

    print(f"tụt sau lịch     : {backlog if backlog is not None else '?'} ngày")
    print(f"trần mỗi lượt    : {args.max_per_run}")
    print(f"được ra lượt này : {allowance}")
    for n, ds in planned:
        print(f"  #{n:03d} | {ds}")
    if not planned:
        print("  (không có bài nào được phép ra trong lượt này)")
    return 0 if allowance >= 1 else GATE_NOT_DUE


def cmd_init(args) -> int:
    if os.path.exists(STATE_PATH) and not args.force:
        print("state.json đã tồn tại. Dùng --force để ghi đè.", file=sys.stderr)
        return 1
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
    p.add_argument("--max-per-run", type=int, default=CATCHUP_MAX_PER_RUN,
                   help=f"Trần số bài mỗi lượt khi bù nhịp (mặc định {CATCHUP_MAX_PER_RUN}).")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("next", help="In số bài kế tiếp.")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("gate", help="Exit 0 nếu tới nhịp, 10 nếu chưa.")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_DAYS)
    p.add_argument("--max-per-run", type=int, default=CATCHUP_MAX_PER_RUN,
                   help=f"Trần số bài mỗi lượt khi bù nhịp (mặc định {CATCHUP_MAX_PER_RUN}).")
    p.set_defaults(func=cmd_gate)

    p = sub.add_parser("backlog", help="Số bài được phép ra lượt này + ngày từng bài.")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_DAYS)
    p.add_argument("--max-per-run", type=int, default=CATCHUP_MAX_PER_RUN,
                   help=f"Trần số bài mỗi lượt khi bù nhịp (mặc định {CATCHUP_MAX_PER_RUN}).")
    p.set_defaults(func=cmd_backlog)

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

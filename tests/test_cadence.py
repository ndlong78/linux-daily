"""Unit test cho cadence.py — cổng nhịp & state.json dùng dữ liệu giả trong tmp_path."""
import datetime as dt
import json

import cadence


def _topics(tmp_path, lines):
    p = tmp_path / "topics.md"
    p.write_text("# chú thích\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


def _point(tmp_path, monkeypatch, topics_lines=None, state=None):
    """Trỏ cadence vào topics.md / state.json trong tmp_path."""
    monkeypatch.setattr(cadence, "TOPICS_PATH", _topics(tmp_path, topics_lines or []))
    sp = tmp_path / "state.json"
    if state is not None:
        sp.write_text(json.dumps(state), encoding="utf-8")
    monkeypatch.setattr(cadence, "STATE_PATH", str(sp))
    return sp


SAMPLE = [
    "#001 | 2026-01-01 | Networking | a",
    "#002 | 2026-01-03 | Bảo mật | b",
]


def test_default_interval_is_daily():
    assert cadence.DEFAULT_INTERVAL_DAYS == 1


def test_read_topics_parses_and_sorts(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=list(reversed(SAMPLE)))
    entries = cadence.read_topics()
    assert [e["n"] for e in entries] == [1, 2]
    assert entries[-1]["date_s"] == "2026-01-03"


def test_next_issue_from_topics(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    assert cadence.next_issue(None) == 3


def test_next_issue_from_state(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    assert cadence.next_issue({"last_issue": 18}) == 19


def test_state_from_topics(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    s = cadence.state_from_topics(generated_at="2026-01-03T00:00:00+00:00")
    assert s["last_issue"] == 2
    assert s["last_published_date"] == "2026-01-03"
    assert s["last_generated_at"] == "2026-01-03T00:00:00+00:00"


NOW = dt.datetime(2026, 1, 10, tzinfo=dt.timezone.utc)


def test_days_since_uses_generated_at(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    state = {"last_generated_at": "2026-01-08T00:00:00+00:00"}
    assert cadence.days_since(state, now=NOW) == 2


def test_days_since_falls_back_to_topics(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    assert cadence.days_since(None, now=NOW) == 7


def test_is_due_true_when_interval_met(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    state = {"last_generated_at": "2026-01-08T00:00:00+00:00"}
    assert cadence.is_due(state, interval=2, now=NOW) is True


def test_is_due_false_when_too_soon(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    state = {"last_generated_at": "2026-01-09T00:00:00+00:00"}
    assert cadence.is_due(state, interval=2, now=NOW) is False


def test_is_due_defaults_to_one_day(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    state = {"last_generated_at": "2026-01-09T00:00:00+00:00"}
    assert cadence.is_due(state, now=NOW) is True


def test_gate_exit_codes(tmp_path, monkeypatch, capsys):
    _point(
        tmp_path,
        monkeypatch,
        topics_lines=SAMPLE,
        state={
            "last_issue": 2,
            "last_published_date": "2026-01-03",
            "last_generated_at": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=5)).isoformat(),
        },
    )
    assert cadence.main(["gate", "--interval", "2"]) == 0

    _point(
        tmp_path,
        monkeypatch,
        topics_lines=SAMPLE,
        state={
            "last_issue": 2,
            "last_published_date": "2026-01-03",
            "last_generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
    )
    assert cadence.main(["gate", "--interval", "2"]) == cadence.GATE_NOT_DUE


def test_init_creates_and_refuses_overwrite(tmp_path, monkeypatch):
    sp = _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    assert cadence.main(["init"]) == 0
    assert sp.exists()
    saved = json.loads(sp.read_text(encoding="utf-8"))
    assert saved["last_issue"] == 2
    assert saved["last_generated_at"].startswith("2026-01-03")
    assert cadence.main(["init"]) == 1
    assert cadence.main(["init", "--force"]) == 0


def test_record_syncs_from_topics(tmp_path, monkeypatch):
    sp = _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    assert cadence.main(["record", "--at", "2026-01-03T09:00:00+00:00"]) == 0
    saved = json.loads(sp.read_text(encoding="utf-8"))
    assert saved["last_issue"] == 2
    assert saved["last_published_date"] == "2026-01-03"
    assert saved["last_generated_at"] == "2026-01-03T09:00:00+00:00"


def test_record_respects_overrides(tmp_path, monkeypatch):
    sp = _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    assert cadence.main(["record", "--issue", "5", "--date", "2026-02-02"]) == 0
    saved = json.loads(sp.read_text(encoding="utf-8"))
    assert saved["last_issue"] == 5
    assert saved["last_published_date"] == "2026-02-02"


# --- bù bài khi lỡ nhịp ---

import validate_repo  # noqa: E402  (đặt cuối để nhóm test bù nhịp tự chứa)


def _behind(days: int, issue: int = 79) -> dict:
    """state.json mô tả bài mới nhất tụt `days` ngày sau 2026-09-20 (giờ VN)."""
    last = dt.date(2026, 9, 20) - dt.timedelta(days=days)
    return {
        "last_issue": issue,
        "last_published_date": last.isoformat(),
        "last_generated_at": f"{last.isoformat()}T00:00:00+00:00",
    }


# 2026-09-20T05:00:00Z == 12:00 giờ VN cùng ngày — giữa ngày ở cả hai múi giờ.
NOON_VN = dt.datetime(2026, 9, 20, 5, 0, tzinfo=dt.timezone.utc)


def test_vn_timezone_matches_validate_repo():
    """Backlog và cổng 'ngày ở tương lai' phải dùng chung một mốc ngày.

    So trên mốc cố định chứ không so hai đồng hồ thực: hai lệnh gọi `now()` liên
    tiếp vắt qua nửa đêm giờ VN sẽ làm test đỏ mà không có lỗi thật nào.
    """
    assert cadence.VN_TZ == validate_repo.VN_TZ
    for instant in (NOON_VN, dt.datetime(2026, 9, 19, 17, 30, tzinfo=dt.timezone.utc)):
        assert cadence.today_vn(instant) == instant.astimezone(validate_repo.VN_TZ).date()


def test_today_vn_uses_vietnam_day_boundary():
    """00:30 giờ VN đã sang ngày mới, trong khi UTC vẫn là hôm trước."""
    just_after_midnight_vn = dt.datetime(2026, 9, 19, 17, 30, tzinfo=dt.timezone.utc)
    assert just_after_midnight_vn.date() == dt.date(2026, 9, 19)
    assert cadence.today_vn(just_after_midnight_vn) == dt.date(2026, 9, 20)


def test_publication_backlog_counts_calendar_lag(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(3))
    assert cadence.publication_backlog(cadence.load_state(), NOON_VN) == 3


def test_publication_backlog_zero_when_caught_up(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(0))
    assert cadence.publication_backlog(cadence.load_state(), NOON_VN) == 0


def test_publication_backlog_falls_back_to_topics(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=["#001 | 2026-09-18 | Networking | a"])
    assert cadence.publication_backlog(None, NOON_VN) == 2


def test_publication_backlog_none_without_any_date(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=[])
    assert cadence.publication_backlog(None, NOON_VN) is None


def test_catchup_allowance_is_one_at_normal_cadence(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(1))
    assert cadence.catchup_allowance(cadence.load_state(), now=NOON_VN) == 1


def test_catchup_allowance_grows_with_backlog(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(3))
    assert cadence.catchup_allowance(cadence.load_state(), now=NOON_VN) == 3


def test_catchup_allowance_capped_by_max_per_run(tmp_path, monkeypatch):
    """Gián đoạn 30 ngày không được đổ 30 bài vào một PR."""
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(30))
    state = cadence.load_state()
    assert cadence.publication_backlog(state, NOON_VN) == 30
    assert cadence.catchup_allowance(state, now=NOON_VN) == cadence.CATCHUP_MAX_PER_RUN
    assert cadence.catchup_allowance(state, now=NOON_VN, max_per_run=5) == 5


def test_catchup_allowance_zero_when_not_due(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(0))
    assert cadence.catchup_allowance(cadence.load_state(), now=NOON_VN) == 0


def test_catchup_allowance_bootstraps_to_single_post(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=[])
    assert cadence.catchup_allowance(None, now=NOON_VN) == 1


def test_planned_publications_never_reach_the_future(tmp_path, monkeypatch):
    """Bất biến quan trọng nhất: validate_repo chặn mọi ngày > today_vn()."""
    for lag in range(1, 12):
        _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(lag))
        planned = cadence.planned_publications(cadence.load_state(), now=NOON_VN)
        assert planned, f"lag={lag} phải ra ít nhất một bài"
        for _, date_s in planned:
            assert dt.date.fromisoformat(date_s) <= cadence.today_vn(NOON_VN)


def test_planned_publications_are_sequential(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(3, issue=79))
    assert cadence.planned_publications(cadence.load_state(), now=NOON_VN) == [
        (80, "2026-09-18"),
        (81, "2026-09-19"),
        (82, "2026-09-20"),
    ]


def test_planned_publications_empty_when_caught_up(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(0))
    assert cadence.planned_publications(cadence.load_state(), now=NOON_VN) == []


def test_backlog_command_exit_codes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cadence, "_now", lambda: NOON_VN)

    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(3))
    assert cadence.main(["backlog"]) == 0
    out = capsys.readouterr().out
    assert "#080 | 2026-09-18" in out
    assert "#082 | 2026-09-20" in out

    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(0))
    assert cadence.main(["backlog"]) == cadence.GATE_NOT_DUE


def test_gate_reports_catchup_plan(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cadence, "_now", lambda: NOON_VN)
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE, state=_behind(3))
    assert cadence.main(["gate"]) == 0
    assert "bù 3 bài" in capsys.readouterr().out

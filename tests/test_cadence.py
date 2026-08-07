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
    # Không có state → lấy ngày bài mới nhất (2026-01-03) làm mốc: 10 - 3 = 7 ngày.
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    assert cadence.days_since(None, now=NOW) == 7


def test_is_due_true_when_interval_met(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    state = {"last_generated_at": "2026-01-08T00:00:00+00:00"}  # 2 ngày
    assert cadence.is_due(state, interval=2, now=NOW) is True


def test_is_due_false_when_too_soon(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    state = {"last_generated_at": "2026-01-09T00:00:00+00:00"}  # 1 ngày
    assert cadence.is_due(state, interval=2, now=NOW) is False


def test_gate_exit_codes(tmp_path, monkeypatch, capsys):
    _point(tmp_path, monkeypatch, topics_lines=SAMPLE,
           state={"last_issue": 2, "last_published_date": "2026-01-03",
                  "last_generated_at": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=5)).isoformat()})
    assert cadence.main(["gate", "--interval", "2"]) == 0  # 5 ngày ≥ 2 → tới nhịp

    _point(tmp_path, monkeypatch, topics_lines=SAMPLE,
           state={"last_issue": 2, "last_published_date": "2026-01-03",
                  "last_generated_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    assert cadence.main(["gate", "--interval", "2"]) == cadence.GATE_NOT_DUE  # 0 ngày → chưa


def test_init_creates_and_refuses_overwrite(tmp_path, monkeypatch):
    sp = _point(tmp_path, monkeypatch, topics_lines=SAMPLE)
    assert cadence.main(["init"]) == 0
    assert sp.exists()
    saved = json.loads(sp.read_text(encoding="utf-8"))
    assert saved["last_issue"] == 2
    # last_generated_at bootstrap = 00:00 UTC ngày bài mới nhất.
    assert saved["last_generated_at"].startswith("2026-01-03")
    # Không --force → từ chối ghi đè.
    assert cadence.main(["init"]) == 1
    # --force → ghi đè được.
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

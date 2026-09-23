"""Test cho source_preflight.py — cổng báo mọi lỗi source cùng lúc.

Tính chất quan trọng nhất không phải "bắt được lỗi X", mà là **chạy hết mọi
phép kiểm dù đã có lỗi**. Mất tính chất đó thì tool thoái hoá thành đúng thứ nó
sinh ra để thay: một lỗi mỗi lượt chạy.
"""
from __future__ import annotations

import json
from pathlib import Path

import source_preflight

ROOT = Path(__file__).resolve().parents[1]


def test_real_repository_passes_preflight():
    assert source_preflight.run() == 0


def test_every_check_runs_even_after_one_fails(monkeypatch):
    """Không được dừng sớm: danh sách phải đủ, không phải lỗi đầu tiên."""
    called: list[str] = []

    def fake_validator(script: str):
        called.append(script)
        return 1, f"LỖI: {script} hỏng"

    monkeypatch.setattr(source_preflight, "check_ld_meta", lambda: ["ld-meta hỏng"])
    monkeypatch.setattr(source_preflight, "check_source_of_truth", lambda: ["state hỏng"])
    monkeypatch.setattr(source_preflight, "_run_validator", fake_validator)

    results = source_preflight.collect()
    assert [script for _, script in source_preflight.SUBPROCESS_CHECKS] == called
    assert len(results) == 2 + len(source_preflight.SUBPROCESS_CHECKS)
    assert all(errs for _, errs in results), results


def test_exit_code_and_json_shape(monkeypatch, capsys):
    monkeypatch.setattr(source_preflight, "collect", lambda: [("A", []), ("B", ["x", "y"])])
    assert source_preflight.run(json_output=True) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["errors"] == 2
    assert payload["checks"][1] == {"name": "B", "errors": ["x", "y"]}


def test_missing_topics_line_is_reported(tmp_path, monkeypatch):
    """Đúng lỗi đã chặn #084 ở lượt thứ ba."""
    _point(tmp_path, monkeypatch, topics=["#001 | 2026-01-01 | Networking | a"],
           posts=["post-001-a.html", "post-002-b.html"],
           state={"last_issue": 2, "last_published_date": "2026-01-02"})
    errors = source_preflight.check_source_of_truth()
    assert any("posts/ có #002 nhưng topics.md thiếu dòng" in e for e in errors), errors
    # và phải kèm luôn hệ quả ở state.json, không bắt người đọc chạy lại mới thấy
    assert any("last_issue" in e for e in errors), errors
    assert any("last_published_date" in e for e in errors), errors


def test_orphan_topics_line_is_reported(tmp_path, monkeypatch):
    _point(tmp_path, monkeypatch,
           topics=["#001 | 2026-01-01 | Networking | a", "#002 | 2026-01-02 | Bảo mật | b"],
           posts=["post-001-a.html"],
           state={"last_issue": 2, "last_published_date": "2026-01-02"})
    errors = source_preflight.check_source_of_truth()
    assert any("topics.md có #002 nhưng posts/ không có file" in e for e in errors), errors


def test_ld_meta_problems_are_reported(tmp_path, monkeypatch):
    posts_dir = tmp_path / "posts"
    posts_dir.mkdir()
    (posts_dir / "post-001-ok.html").write_text(
        '<script type="application/json" id="ld-meta">{"issue": 1}</script>', encoding="utf-8"
    )
    (posts_dir / "post-002-missing.html").write_text("<html></html>", encoding="utf-8")
    (posts_dir / "post-003-broken.html").write_text(
        '<script type="application/json" id="ld-meta">{nope}</script>', encoding="utf-8"
    )
    (posts_dir / "post-004-mismatch.html").write_text(
        '<script type="application/json" id="ld-meta">{"issue": 99}</script>', encoding="utf-8"
    )
    monkeypatch.setattr(source_preflight, "POSTS_DIR", str(posts_dir))
    monkeypatch.setattr(source_preflight, "ROOT", str(tmp_path))

    errors = source_preflight.check_ld_meta()
    joined = "\n".join(errors)
    assert "post-002-missing.html" in joined
    assert "post-003-broken.html" in joined
    assert "post-004-mismatch.html" in joined
    assert "post-001-ok.html" not in joined


def test_unrecognised_validator_output_is_not_swallowed():
    """Validator đổi định dạng output không được làm preflight báo xanh."""
    assert source_preflight._error_lines("something odd", "x.py", 1) == ["something odd"]
    assert source_preflight._error_lines("", "x.py", 3) == ["x.py trả exit code 3"]


def _point(tmp_path, monkeypatch, *, topics, posts, state):
    posts_dir = tmp_path / "posts"
    posts_dir.mkdir()
    for name in posts:
        (posts_dir / name).write_text("x", encoding="utf-8")
    (tmp_path / "topics.md").write_text("\n".join(topics) + "\n", encoding="utf-8")
    (tmp_path / "state.json").write_text(json.dumps(state), encoding="utf-8")
    monkeypatch.setattr(source_preflight, "ROOT", str(tmp_path))
    monkeypatch.setattr(source_preflight, "POSTS_DIR", str(posts_dir))
    monkeypatch.setattr(source_preflight, "TOPICS_PATH", str(tmp_path / "topics.md"))
    monkeypatch.setattr(source_preflight, "STATE_PATH", str(tmp_path / "state.json"))

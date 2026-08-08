from pathlib import Path

import contributor


def test_doctor_accepts_repository_baseline():
    report = contributor.doctor()
    assert report.errors == []


def test_doctor_reports_missing_required_path(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    report = contributor.doctor(tmp_path)
    assert any("CONTRIBUTING.md" in error for error in report.errors)

"""Cổng metadata/social và migration verification evidence."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import backfill_site_metadata as backfill  # noqa: E402


def test_khong_lech_thi_khong_bao_gi():
    assert backfill.describe_drift("a\nb\n", "a\nb\n") == []


def test_bao_dung_dong_og_description_lech():
    current = '<meta property="og:description" content="câu cũ">\n<p>thân bài</p>'
    expected = '<meta property="og:description" content="câu mới">\n<p>thân bài</p>'

    drift = backfill.describe_drift(current, expected)

    assert any(line.startswith("-") and "câu cũ" in line for line in drift)
    assert any(line.startswith("+") and "câu mới" in line for line in drift)
    assert all("thân bài" not in line for line in drift), "dòng không lệch thì đừng in"


def test_cat_bot_dong_qua_dai():
    current = "x" * 400
    expected = "y" * 400

    for line in backfill.describe_drift(current, expected):
        assert len(line) <= backfill.MAX_DRIFT_WIDTH + 2


def test_gioi_han_so_dong_va_noi_ro_con_bao_nhieu():
    current = "\n".join(f"cũ {i}" for i in range(40))
    expected = "\n".join(f"mới {i}" for i in range(40))

    drift = backfill.describe_drift(current, expected)

    assert len(drift) == backfill.MAX_DRIFT_LINES + 1
    assert "còn" in drift[-1] and "dòng lệch nữa" in drift[-1]


def _legacy_verification_html() -> tuple[str, dict]:
    meta = {
        "issue": 69,
        "tested_on": [
            "Ubuntu/Xubuntu 24.04 LTS (documentation-verified)",
            "Debian 13 stable (documentation-verified)",
            "Fedora 42 (documentation-verified)",
            "FreeBSD 14.4-RELEASE (documentation-verified)",
        ],
        "last_verified": "2026-09-07",
    }
    text = '''<script type="application/json" id="ld-meta">
{"issue":69,"tested_on":["Ubuntu/Xubuntu 24.04 LTS (documentation-verified)","Debian 13 stable (documentation-verified)","Fedora 42 (documentation-verified)","FreeBSD 14.4-RELEASE (documentation-verified)"],"last_verified":"2026-09-07"}
</script>
<div class="style-meta" aria-label="Môi trường kiểm chứng"><span><strong>Tested on:</strong> Ubuntu/Xubuntu 24.04 LTS · Debian 13 stable · Fedora 42 · FreeBSD 14.4-RELEASE</span><span><strong>Last verified:</strong> 2026-09-07</span></div>'''
    return text, meta


def test_verification_migration_is_inactive_before_issue_070():
    text, meta = _legacy_verification_html()
    assert backfill.normalize_verification_metadata(text, meta, active=False) == text


def test_verification_migration_splits_legacy_documentation_evidence():
    text, meta = _legacy_verification_html()

    migrated = backfill.normalize_verification_metadata(text, meta, active=True)

    assert '"tested_on":[]' in migrated
    assert (
        '"documentation_verified_on":["Ubuntu/Xubuntu 24.04 LTS","Debian 13 stable",'
        '"Fedora 42","FreeBSD 14.4-RELEASE"]' in migrated
    )
    assert "(documentation-verified)" not in migrated
    assert "Runtime tested:" not in migrated, "empty runtime list should not invent evidence"
    assert "Documentation verified:" in migrated
    assert "Tested on:" not in migrated
    assert "Last verified:</strong> 2026-09-07" in migrated


def test_verification_migration_preserves_real_runtime_evidence():
    meta = {
        "issue": 70,
        "tested_on": [
            "Ubuntu 24.04",
            "FreeBSD 14.4 (documentation-verified)",
        ],
        "last_verified": "2026-09-08",
    }
    text = '''<script type="application/json" id="ld-meta">{"issue":70,"tested_on":["Ubuntu 24.04","FreeBSD 14.4 (documentation-verified)"],"last_verified":"2026-09-08"}</script>
<div class="style-meta"><span><strong>Tested on:</strong> Ubuntu 24.04 · FreeBSD 14.4</span><span><strong>Last verified:</strong> 2026-09-08</span></div>'''

    migrated = backfill.normalize_verification_metadata(text, meta, active=True)

    assert '"tested_on":["Ubuntu 24.04"]' in migrated
    assert '"documentation_verified_on":["FreeBSD 14.4"]' in migrated
    assert "Runtime tested:</strong> Ubuntu 24.04" in migrated
    assert "Documentation verified:</strong> FreeBSD 14.4" in migrated


def test_verification_migration_is_idempotent():
    text, meta = _legacy_verification_html()
    first = backfill.normalize_verification_metadata(text, meta, active=True)
    migrated_meta = {
        "issue": 69,
        "tested_on": [],
        "documentation_verified_on": [
            "Ubuntu/Xubuntu 24.04 LTS",
            "Debian 13 stable",
            "Fedora 42",
            "FreeBSD 14.4-RELEASE",
        ],
        "last_verified": "2026-09-07",
    }
    second = backfill.normalize_verification_metadata(first, migrated_meta, active=True)
    assert second == first


def test_kho_hien_tai_dang_dong_bo():
    """Ở state #069 migration chưa kích hoạt nên main hiện tại phải vẫn deterministic."""
    assert backfill.run(check=True) == 0

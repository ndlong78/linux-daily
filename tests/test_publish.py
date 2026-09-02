from __future__ import annotations

from types import SimpleNamespace

import publish


def test_prepare_sinh_lai_metadata_post_truoc_khi_dung_artifact():
    """backfill ghi lại posts/*.html, build.py dựng artifact TỪ chúng — sai thứ tự là sai kết quả.

    Đây là khoảng trống đã đưa bài #055 tới production với og/twitter:description
    lệch meta.lede: tool sinh chúng không nằm trong `prepare` nên materialize
    không bao giờ tự sửa.
    """
    plan = publish.command_plan("prepare")
    steps = [command[-1] for command in plan]
    assert steps[0] == "tools/backfill_site_metadata.py"
    assert steps.index("tools/backfill_site_metadata.py") < steps.index("tools/build.py")
    assert any(command[-1] == "tools/learning_dashboard.py" for command in plan)
    assert any(command[-1] == "tools/content_mix.py" for command in plan)
    assert any(command[-1] == "tools/taxonomy.py" for command in plan)
    assert any(command[-1] == "tools/distro_coverage.py" for command in plan)
    assert any(command[-1] == "tools/quality_dashboard.py" for command in plan)
    assert all(command[-1] != "tools/daily_operations_dashboard.py" for command in plan)


def test_check_plan_is_read_only_and_covers_local_publish_gates():
    plan = publish.command_plan("check")
    assert len(plan) == 22
    flattened = [" ".join(command) for command in plan]
    # Đứng đầu: lệch metadata post kéo theo nhiều gate khác đỏ, và người đọc log
    # chỉ nhìn lỗi đầu tiên. Xem test_backfill_site_metadata.
    assert flattened[0].endswith("tools/backfill_site_metadata.py --check")
    assert any("tools/build.py --check" in command for command in flattened)
    assert any("tools/validate_style.py" in command for command in flattened)
    assert any("tools/content_mix.py --check" in command for command in flattened)
    assert any("tools/curriculum_planner.py" in command for command in flattened)
    assert any("tools/publication_readiness.py" in command for command in flattened)
    assert any("tools/coverage_intelligence.py --check" in command for command in flattened)
    assert any("tools/distro_coverage.py --check" in command for command in flattened)
    assert any("tools/command_quality.py" in command for command in flattened)
    assert any("tools/content_freshness.py" in command for command in flattened)
    assert any("tools/content_lifecycle.py" in command for command in flattened)
    assert any("tools/quality_dashboard.py --check" in command for command in flattened)
    assert any("tools/learning_metadata.py" in command for command in flattened)
    assert any("tools/topic_progression.py" in command for command in flattened)
    assert any("tools/learning_dashboard.py --check" in command for command in flattened)
    assert any("tools/lab_contract.py" in command for command in flattened)
    assert any("tools/interoperability_lab.py" in command for command in flattened)
    assert any("tools/daily_operations_dashboard.py --check" in command for command in flattened)
    assert any("tools/release.py validate" in command for command in flattened)
    assert any("tools/performance_budget.py" in command for command in flattened)
    assert any("tools/repo_health.py" in command for command in flattened)
    assert all("check_links.py --external" not in command for command in flattened)


def test_pipeline_stops_on_first_failure():
    calls = []

    def fake_runner(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=7 if len(calls) == 2 else 0)

    assert publish.run("check", runner=fake_runner) == 7
    assert len(calls) == 2

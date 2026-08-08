from __future__ import annotations

from types import SimpleNamespace

import publish


def test_prepare_plan_regenerates_before_metadata_checks():
    plan = publish.command_plan("prepare")
    assert plan[0][-1] == "tools/build.py"
    assert any(command[-1] == "tools/content_mix.py" for command in plan)
    assert any(command[-1] == "tools/taxonomy.py" for command in plan)


def test_check_plan_is_read_only_and_covers_local_publish_gates():
    plan = publish.command_plan("check")
    flattened = [" ".join(command) for command in plan]
    assert any("tools/build.py --check" in command for command in flattened)
    assert any("tools/content_mix.py --check" in command for command in flattened)
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

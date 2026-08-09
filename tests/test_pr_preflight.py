from types import SimpleNamespace

import pr_preflight


def test_command_plan_matches_ci_core_gates():
    plan = pr_preflight.command_plan()
    flattened = [" ".join(command) for command in plan]
    assert flattened[0] == "ruff check tools/ tests/"
    assert any("-m pytest" in command for command in flattened)
    assert any("tools/workflow_safety.py" in command for command in flattened)
    assert any("tools/publish.py check" in command for command in flattened)


def test_preflight_stops_on_first_failure():
    calls = []

    def fake_runner(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=3 if len(calls) == 2 else 0)

    assert pr_preflight.run(runner=fake_runner) == 3
    assert len(calls) == 2

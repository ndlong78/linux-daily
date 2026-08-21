from pathlib import Path

import workflow_safety


def test_repository_workflows_pass_policy():
    report = workflow_safety.run()
    assert report.errors == []
    assert report.checked >= 1


def test_non_release_write_permission_is_rejected(tmp_path: Path):
    path = tmp_path / "unsafe.yml"
    path.write_text(
        "name: unsafe\non:\n  workflow_dispatch:\npermissions:\n  contents: write\njobs:\n  x:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    errors = workflow_safety.validate_file(path)
    assert any("write permissions are forbidden" in error for error in errors)


def test_non_release_requires_explicit_contents_read(tmp_path: Path):
    path = tmp_path / "unsafe.yml"
    path.write_text(
        "name: unsafe\non:\n  workflow_dispatch:\npermissions:\n  actions: read\njobs:\n  x:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    errors = workflow_safety.validate_file(path)
    assert any("must declare contents: read" in error for error in errors)


def test_non_release_self_mutation_is_rejected(tmp_path: Path):
    path = tmp_path / "unsafe.yml"
    path.write_text(
        "name: unsafe\non:\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n  x:\n    runs-on: ubuntu-latest\n    steps:\n      - run: git add -A && git commit -m generated && git push\n",
        encoding="utf-8",
    )
    errors = workflow_safety.validate_file(path)
    assert any("must not stage, commit, or push" in error for error in errors)


def test_pull_request_target_is_rejected(tmp_path: Path):
    path = tmp_path / "unsafe.yml"
    path.write_text(
        "name: unsafe\non:\n  pull_request_target:\npermissions:\n  contents: read\njobs:\n  x:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    errors = workflow_safety.validate_file(path)
    assert any("pull_request_target is forbidden" in error for error in errors)


# --- Regression: workflow chạy tool cần dependency phải cài dependency ---

ROOT = Path(__file__).resolve().parents[1]


def _workflow(text: str, tmp_path: Path, name: str = "sample.yml") -> list[str]:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return workflow_safety.validate_file(path)


def test_transitive_third_party_dependency_is_detected():
    """check_production -> site_fingerprint -> socialmeta -> PIL.

    Đây là lỗi thật đã làm production-smoke đỏ nhiều ngày: nhìn import trực tiếp
    của check_production thì không thấy dependency nào.
    """
    assert workflow_safety.needs_third_party("check_production") is True
    assert workflow_safety.needs_third_party("operations_dashboard") is True


def test_subprocess_orchestrator_counts_as_needing_dependencies():
    """publish.py không import gì bên thứ ba — nó spawn tool khác bằng subprocess."""
    assert workflow_safety._tool_imports("publish") & workflow_safety.THIRD_PARTY_MODULES == set()
    assert workflow_safety.needs_third_party("publish") is True
    assert workflow_safety.needs_third_party("pr_preflight") is True


def test_stdlib_only_tool_does_not_require_install():
    assert workflow_safety.needs_third_party("release") is False
    assert workflow_safety.needs_third_party("cadence") is False


def test_missing_dependency_install_is_rejected(tmp_path: Path):
    errors = _workflow(
        "name: x\non:\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n"
        "  x:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - run: python tools/check_production.py\n",
        tmp_path,
    )
    assert any("không có bước pip install" in error for error in errors), errors


def test_dependency_install_satisfies_the_check(tmp_path: Path):
    errors = _workflow(
        "name: x\non:\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n"
        "  x:\n    runs-on: ubuntu-latest\n    steps:\n"
        '      - run: pip install -e "."\n'
        "      - run: python tools/check_production.py\n",
        tmp_path,
    )
    assert not any("pip install" in error for error in errors), errors


def test_stdlib_only_workflow_needs_no_install(tmp_path: Path):
    errors = _workflow(
        "name: x\non:\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n"
        "  x:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - run: python tools/cadence.py status\n",
        tmp_path,
    )
    assert not any("pip install" in error for error in errors), errors


def test_third_party_module_set_matches_pyproject():
    """Thêm dependency vào pyproject mà quên cập nhật bộ này thì check sẽ mù."""
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    block = pyproject.split("dependencies = [", 1)[1].split("]", 1)[0]
    declared = {
        line.strip().strip('",').split("==")[0].strip('"')
        for line in block.splitlines()
        if line.strip().startswith('"')
    }
    assert declared == {"Pillow", "Jinja2"}, (
        f"dependency đã đổi ({declared}); cập nhật THIRD_PARTY_MODULES trong workflow_safety.py"
    )
    assert workflow_safety.THIRD_PARTY_MODULES == {"PIL", "jinja2"}


# --- concurrency của CI không được huỷ run trên main ---

ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_concurrency_never_cancels_main_runs():
    """`tools/release.py` đòi CI xanh trên ĐÚNG SHA của main.

    Nếu `cancel-in-progress` bật vô điều kiện, hai commit vào main liền nhau sẽ
    khiến commit sau huỷ CI của commit trước — SHA đó vĩnh viễn không có CI xanh
    và không release được từ nó nữa. Đây là cái bẫy của phiên bản một dòng, nên
    nó phải có test riêng chứ không chỉ nằm trong comment.
    """
    text = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in text, (
        "cancel-in-progress phải bị giới hạn trong pull_request"
    )
    assert "group: ci-${{ github.event.pull_request.number || github.sha }}" in text, (
        "push vào main phải gom theo github.sha để mỗi commit một nhóm riêng"
    )


def test_release_gate_still_requires_ci_and_production_smoke():
    """Bất biến mà test trên đang bảo vệ — nếu nó đổi thì phải xem lại concurrency."""
    import release

    assert release.WORKFLOWS == (("CI", "ci.yml"), ("Production Smoke", "production-smoke.yml"))

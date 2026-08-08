from __future__ import annotations

import release


def test_canonical_version_is_strict_semver():
    assert release.canonical_version() == "0.4.0"
    assert release.tag_for("0.4.0") == "v0.4.0"


def test_changelog_contains_current_release_section():
    section = release.changelog_section("0.4.0")
    assert "P3.1 Operations Dashboard" in section
    assert "P3.2 Production Observability" in section
    assert "Release validation tooling" in section


def test_validate_rejects_version_drift():
    try:
        release.validate("0.3.0")
    except ValueError as exc:
        assert "does not match VERSION" in str(exc)
    else:
        raise AssertionError("version drift must be rejected")


def test_render_curated_notes_has_release_heading():
    notes = release.render_curated_notes("0.4.0")
    assert notes.startswith("# Linux Daily v0.4.0")
    assert "human-approved GitHub Actions release workflow" in notes


def test_gate_requires_exact_sha_and_success(monkeypatch):
    def fake_gate(repository, workflow_file, name, sha, token):
        return release.WorkflowGate(name, "completed", "success", sha, f"https://example/{workflow_file}")

    monkeypatch.setattr(release, "workflow_gate", fake_gate)
    gates = release.verify_release_gates("owner/repo", "abc123", "token")
    assert [gate.name for gate in gates] == ["CI", "Production Smoke"]


def test_gate_blocks_success_from_wrong_sha(monkeypatch):
    def fake_gate(repository, workflow_file, name, sha, token):
        return release.WorkflowGate(name, "completed", "success", "oldsha", "https://example")

    monkeypatch.setattr(release, "workflow_gate", fake_gate)
    try:
        release.verify_release_gates("owner/repo", "newsha", "token")
    except RuntimeError as exc:
        assert "release blocked" in str(exc)
    else:
        raise AssertionError("gate must reject workflow evidence from another SHA")

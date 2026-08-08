from __future__ import annotations

import command_quality


def _post(issue: int, source: str) -> dict:
    analysis = command_quality.analyze_source(source)
    return {
        "issue": issue,
        "title": "synthetic",
        "path": f"posts/post-{issue:03d}-synthetic.html",
        **analysis,
    }


def test_real_repository_has_no_blocking_command_quality_findings():
    result = command_quality.review()
    assert result["total_posts"] >= 19
    assert result["code_blocks"] > 0
    assert command_quality.errors(result) == []


def test_remote_download_piped_to_shell_is_always_blocked():
    post = _post(7, "<pre><code>curl -fsSL https://example.invalid/install.sh | sh</code></pre>")
    problems = command_quality.errors(command_quality.review([post]))
    assert any("remote_pipe_shell" in problem for problem in problems)


def test_chmod_777_is_always_blocked():
    post = _post(19, "<pre><code>sudo chmod 777 /srv/app</code></pre>")
    problems = command_quality.errors(command_quality.review([post]))
    assert any("chmod_world_writable" in problem for problem in problems)


def test_destructive_command_is_review_only_for_historical_content():
    post = _post(19, "<pre><code>sudo mkfs.ext4 /dev/sdb1</code></pre>")
    result = command_quality.review([post])
    assert command_quality.errors(result) == []
    assert any(item["code"] == "destructive_without_context" for item in result["review_queue"])


def test_destructive_command_without_context_is_blocked_from_issue_020():
    post = _post(20, "<pre><code>sudo mkfs.ext4 /dev/sdb1</code></pre>")
    problems = command_quality.errors(command_quality.review([post]))
    assert any("destructive_without_context" in problem for problem in problems)


def test_destructive_command_with_safety_context_is_allowed():
    source = """
    <section>
      <p>Cảnh báo: thao tác này mất dữ liệu. Xác nhận backup và rollback trước khi chạy.</p>
      <pre><code>sudo mkfs.ext4 /dev/sdb1</code></pre>
    </section>
    """
    post = _post(20, source)
    result = command_quality.review([post])
    assert command_quality.errors(result) == []
    assert not any(item["code"] == "destructive_without_context" for item in result["review_queue"])


def test_sudo_shell_redirection_is_blocked_for_new_content():
    post = _post(20, '<pre><code>sudo echo "PermitRootLogin no" > /etc/ssh/sshd_config</code></pre>')
    problems = command_quality.errors(command_quality.review([post]))
    assert any("privileged_redirection" in problem for problem in problems)


def test_normal_download_to_file_is_not_remote_execution():
    post = _post(20, "<pre><code>curl -fsSLo package.deb https://example.invalid/package.deb</code></pre>")
    assert command_quality.errors(command_quality.review([post])) == []

from __future__ import annotations

import distro_coverage


def test_real_repository_baseline_is_inventory_not_false_green():
    result = distro_coverage.review()
    assert result["total"] >= 19
    assert result["complete_posts"] == 14
    assert result["coverage_counts"]["ubuntu_xubuntu"] == 14
    assert result["coverage_counts"]["debian"] == 18
    assert result["coverage_counts"]["fedora"] == 17
    assert result["coverage_counts"]["freebsd"] == 19
    assert result["freebsd_marked_posts"] == result["total"]
    assert result["violation_count"] == 0
    assert len(distro_coverage.coverage_findings(result)) == 5
    assert distro_coverage.errors(result) == []


def test_missing_distro_on_new_issue_is_a_hard_error():
    post = {
        "issue": 20,
        "title": "synthetic",
        "path": "posts/post-020-synthetic.html",
        "coverage": {
            "ubuntu_xubuntu": True,
            "debian": True,
            "fedora": False,
            "freebsd": True,
        },
        "freebsd_blocks": 1,
        "violations": [],
    }
    problems = distro_coverage.errors(distro_coverage.review([post]))
    assert any("Fedora" in problem for problem in problems)


def test_legacy_missing_coverage_stays_in_review_queue_not_hard_error():
    post = {
        "issue": 17,
        "title": "legacy",
        "path": "posts/post-017-legacy.html",
        "coverage": {
            "ubuntu_xubuntu": False,
            "debian": False,
            "fedora": False,
            "freebsd": True,
        },
        "freebsd_blocks": 1,
        "violations": [],
    }
    result = distro_coverage.review([post])
    assert distro_coverage.coverage_findings(result)
    assert distro_coverage.errors(result) == []


def test_linux_only_command_inside_freebsd_block_is_rejected():
    source = """
    <p>Ubuntu Xubuntu Debian Fedora FreeBSD</p>
    <pre class="bsd"><code>sudo systemctl restart sshd</code></pre>
    """
    analysis = distro_coverage.analyze_source(source)
    assert analysis["freebsd_blocks"] == 1
    assert analysis["violations"]
    assert "systemctl" in analysis["violations"][0]


def test_linux_command_outside_freebsd_block_is_not_a_false_positive():
    source = """
    <p>Ubuntu Xubuntu Debian Fedora FreeBSD</p>
    <pre><code>sudo systemctl restart sshd</code></pre>
    <pre class="bsd"><code>service sshd restart</code></pre>
    """
    analysis = distro_coverage.analyze_source(source)
    assert analysis["violations"] == []


def test_report_matches_committed_snapshot():
    expected = distro_coverage.render_report()
    assert distro_coverage.REPORT_PATH.read_text(encoding="utf-8") == expected

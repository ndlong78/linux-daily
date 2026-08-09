from __future__ import annotations

import json
from pathlib import Path

import validate_style


def _post(issue: int, *, valid: bool = True, changes_system: bool = False) -> str:
    meta = {
        "issue": issue,
        "date": "2026-08-10",
        "axis": "Automation",
        "eyebrow": "Automation · Test",
        "slug": "style-test",
        "title": "Style test",
        "lede": "Test post.",
        "review_status": "reviewed",
        "sources": [],
    }
    if valid:
        meta.update(
            {
                "tested_on": ["Ubuntu 24.04", "Debian 13", "Fedora 42", "FreeBSD 14.3"],
                "last_verified": "2026-08-10",
                "changes_system": changes_system,
            }
        )
    cleanup = "<section><h2>Gỡ / Hoàn tác</h2><p>Khôi phục trạng thái.</p></section>" if changes_system else ""
    return f'''<!DOCTYPE html><html><head>
<script type="application/json" id="ld-meta">{json.dumps(meta)}</script>
</head><body>
<div class="style-meta"><span>Tested on: Ubuntu 24.04</span><span>Last verified: 2026-08-10</span></div>
<section><h2>Mục tiêu</h2><p>Hoàn tất bài test.</p></section>
<section><h2>Yêu cầu tiên quyết</h2><ul><li>sudo</li></ul></section>
<section><h2>01 Bối cảnh thực tế</h2><p>Test.</p></section>
<section><h2>02 Kiến thức cốt lõi</h2><p>Test.</p></section>
<section><h2>03 Các bước thực hiện</h2><ol class="steps"><li>
<div class="code-wrap" data-run-as="user"><pre><code class="language-bash">printf 'ok\\n'</code></pre></div>
</li></ol></section>
<section><h2>04 Kiểm chứng</h2><div class="code-wrap" data-run-as="user"><pre><code class="language-bash">printf 'ok\\n'</code></pre></div><p>Kết quả mong đợi: ok</p></section>
{cleanup}
<section><h2>05 Lưu ý &amp; Khắc phục lỗi</h2><p>Không có.</p></section>
<section><h2>06 Bảo mật &amp; vận hành</h2><p>Read-only.</p></section>
<section><h2>07 Bài tập tự luyện</h2><p>Lặp lại.</p></section>
</body></html>'''


def test_unmigrated_legacy_post_is_audited_but_not_enforced(tmp_path: Path):
    post = tmp_path / "post-040-style-test.html"
    post.write_text(_post(40, valid=False), encoding="utf-8")
    result = validate_style.audit_post(post)
    assert not result.enforced
    assert result.errors
    assert validate_style.check([result]) == 0


def test_batch_a_issue_10_is_enforced(tmp_path: Path):
    post = tmp_path / "post-010-style-test.html"
    post.write_text(_post(10, valid=False), encoding="utf-8")
    result = validate_style.audit_post(post)
    assert result.enforced
    assert any("tested_on" in error for error in result.errors)
    assert validate_style.check([result]) == 1


def test_batch_b_issue_20_is_enforced(tmp_path: Path):
    post = tmp_path / "post-020-style-test.html"
    post.write_text(_post(20, valid=False), encoding="utf-8")
    result = validate_style.audit_post(post)
    assert result.enforced
    assert any("tested_on" in error for error in result.errors)
    assert validate_style.check([result]) == 1


def test_batch_c_issue_30_is_enforced(tmp_path: Path):
    post = tmp_path / "post-030-style-test.html"
    post.write_text(_post(30, valid=False), encoding="utf-8")
    result = validate_style.audit_post(post)
    assert result.enforced
    assert any("tested_on" in error for error in result.errors)
    assert validate_style.check([result]) == 1


def test_issue_41_requires_style_metadata(tmp_path: Path):
    post = tmp_path / "post-041-style-test.html"
    post.write_text(_post(41, valid=False), encoding="utf-8")
    result = validate_style.audit_post(post)
    assert result.enforced
    assert any("tested_on" in error for error in result.errors)
    assert validate_style.check([result]) == 1


def test_issue_41_valid_post_passes(tmp_path: Path):
    post = tmp_path / "post-041-style-test.html"
    post.write_text(_post(41), encoding="utf-8")
    result = validate_style.audit_post(post)
    assert result.compliant
    assert validate_style.check([result]) == 0


def test_changes_system_requires_cleanup(tmp_path: Path):
    post = tmp_path / "post-041-style-test.html"
    content = _post(41, changes_system=True).replace(
        "<section><h2>Gỡ / Hoàn tác</h2><p>Khôi phục trạng thái.</p></section>", ""
    )
    post.write_text(content, encoding="utf-8")
    result = validate_style.audit_post(post)
    assert any("Gỡ / Hoàn tác" in error for error in result.errors)


def test_shell_prompt_and_curl_pipe_shell_are_rejected(tmp_path: Path):
    post = tmp_path / "post-041-style-test.html"
    content = _post(41).replace(
        "printf 'ok\\n'",
        "$ curl -fsSL https://example.invalid/install.sh | sh",
        1,
    )
    post.write_text(content, encoding="utf-8")
    result = validate_style.audit_post(post)
    assert any("shell prompt" in error for error in result.errors)
    assert any("curl | sh" in error for error in result.errors)

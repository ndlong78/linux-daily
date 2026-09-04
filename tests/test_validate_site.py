from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import validate_site  # noqa: E402


def test_website_seo_gate_passes_on_real_repo():
    report = validate_site.run()
    assert report.errors == [], "Website/SEO gate còn lỗi:\n" + "\n".join(report.errors)


def test_stale_public_host_policy_is_explicit():
    assert validate_site.STALE_PUBLIC_HOSTS == {"ndlong78.github.io"}


def test_site_inventory_is_homepage_plus_all_posts():
    report = validate_site.Report()
    site = validate_site._site()
    paths = [validate_site.INDEX_PATH, *sorted((ROOT / "posts").glob("post-*.html"))]
    canonicals = [
        validate_site._page_canonical(str(path), site, report)
        for path in paths
    ]
    assert report.errors == []
    assert None not in canonicals
    assert len(canonicals) == len(set(canonicals))


# --- Regression: lỗi artifact stale phải tự nói cách khắc phục ---


def test_orphan_post_error_tells_operator_how_to_fix(monkeypatch, tmp_path):
    """Tái hiện đúng lỗi đã làm PR #104 đỏ: bài mới có trong posts/ nhưng
    index.html chưa được dựng lại.

    Log CI trước đây chỉ hiện assertion pytest kèm một khối HTML dài, không nói
    phải chạy lệnh gì; người vận hành phải tự suy ra.
    """
    newest = sorted((ROOT / "posts").glob("post-*.html"))[-1].name
    stale_index = tmp_path / "index.html"
    stale_index.write_text(
        (ROOT / "index.html").read_text(encoding="utf-8").replace(
            f"posts/{newest}", "posts/post-000-khong-ton-tai.html"
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_site, "INDEX_PATH", str(stale_index))

    errors = validate_site.run().errors

    orphan = [e for e in errors if e.startswith(f"orphan post: posts/{newest}")]
    assert orphan, f"không tái hiện được lỗi orphan post: {errors}"
    assert "publish.py prepare" in orphan[0]


def test_rebuild_hint_is_attached_to_every_stale_artifact_error():
    """Mọi lỗi cùng nguyên nhân "artifact chưa dựng lại" đều phải mang hướng dẫn.

    Đọc theo AST chứ không theo dòng: bản cũ quét từng dòng nguồn nên chỉ cần
    xuống dòng một lời gọi `append` là test vỡ dù hành vi không đổi — brittle
    theo cách che mất tín hiệu thật.
    """
    import ast

    source = (ROOT / "tools" / "validate_site.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    def literals(node) -> str:
        return " ".join(
            sub.value for sub in ast.walk(node)
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str)
        )

    def names(node) -> set[str]:
        return {sub.id for sub in ast.walk(node) if isinstance(sub, ast.Name)}

    appends = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "append"
    ]

    for message in (
        "sitemap thiếu canonical",
        "sitemap có URL không phải page canonical",
        "orphan post",
        "archive.html không được homepage liên kết",
        "không trỏ tới",
    ):
        khop = [call for call in appends if message in literals(call)]
        assert khop, f"không tìm thấy lời gọi append nào cho: {message}"
        for call in khop:
            assert "REBUILD_HINT" in names(call), f"thiếu hướng dẫn khắc phục cho: {message}"

"""Unit test cho build_index: parse_post và render_index dùng dữ liệu giả."""
import build_index

POST_HTML = """<!DOCTYPE html>
<html lang="vi"><body class="post"><div class="wrap">
  <div class="masthead"><div class="brand">
    <a class="brand-home" href="../index.html">← Linux Daily</a>
    <span class="issue">#012 · 06·08·2026</span>
  </div></div>
  <header class="post">
    <p class="eyebrow">Networking · Kết nối</p>
    <h1>Tiêu đề <em>thử</em></h1>
    <p class="lede">Đây là lede &amp; mô tả.</p>
  </header>
</div></body></html>
"""


def _write_post(posts_dir, name, html):
    p = posts_dir / name
    p.write_text(html, encoding="utf-8")
    return str(p)


def test_parse_post_extracts_fields(tmp_path):
    path = _write_post(tmp_path, "post-012-demo.html", POST_HTML)
    p = build_index.parse_post(path)
    assert p["n"] == 12
    assert p["num"] == "#012"
    assert p["date"] == "06·08·2026"
    assert p["axis"] == "Networking · Kết nối"
    assert p["title"] == "Tiêu đề thử"  # tag <em> bị strip
    assert "lede" in p["lede"]


def test_render_index_sorts_desc_and_counts(tmp_path):
    _write_post(tmp_path, "post-012-demo.html", POST_HTML)
    _write_post(tmp_path, "post-003-demo.html", POST_HTML.replace("#012", "#003"))
    out, n = build_index.render_index(str(tmp_path))
    assert n == 2
    # Bài số lớn hơn (#012) phải đứng trước #003.
    assert out.index("#012") < out.index("#003")
    assert "2 BÀI" in out


def test_render_index_strips_wellformed_tags(tmp_path):
    # Tag đóng đầy đủ bị strip_tags loại bỏ trước khi vào index.
    evil = POST_HTML.replace("Tiêu đề <em>thử</em>", "Tiêu đề<script>alert(1)</script>")
    _write_post(tmp_path, "post-012-demo.html", evil)
    out, _ = build_index.render_index(str(tmp_path))
    assert "<script>" not in out
    assert "alert(1)" in out  # phần văn bản còn lại, nhưng đã trơ (không phải tag)


def test_render_index_escapes_broken_tag(tmp_path):
    # Tag hỏng (thiếu '>') không bị strip; html.escape phải escape dấu '<'.
    evil = POST_HTML.replace("Tiêu đề <em>thử</em>", "<img src=x onerror=alert(1)")
    _write_post(tmp_path, "post-012-demo.html", evil)
    out, _ = build_index.render_index(str(tmp_path))
    assert "<img src=x" not in out
    assert "&lt;img src=x" in out


def test_render_index_empty(tmp_path):
    out, n = build_index.render_index(str(tmp_path))
    assert n == 0
    assert "Chưa có bài nào" in out

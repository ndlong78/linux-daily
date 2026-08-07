"""Unit test cho build_index: đọc metadata có cấu trúc + render Jinja2 (dữ liệu giả)."""
import json

import build_index


def _post(posts_dir, n, slug="demo", eyebrow="Networking · Demo",
          title="Tiêu đề demo", lede="Lede demo.", date="2026-08-06"):
    meta = {"issue": n, "date": date, "axis": "Networking",
            "eyebrow": eyebrow, "slug": slug, "title": title, "lede": lede}
    html = (
        "<!DOCTYPE html>\n<html lang=\"vi\">\n<head>\n"
        '<script type="application/json" id="ld-meta">\n'
        + json.dumps(meta, ensure_ascii=False)
        + "\n</script>\n</head>\n<body class=\"post\"></body></html>\n"
    )
    p = posts_dir / f"post-{n:03d}-{slug}.html"
    p.write_text(html, encoding="utf-8")
    return str(p)


def test_collect_posts_reads_meta_and_sorts(tmp_path):
    _post(tmp_path, 3)
    _post(tmp_path, 12)
    posts = build_index.collect_posts(str(tmp_path))
    assert [p["n"] for p in posts] == [12, 3]  # mới nhất lên đầu
    assert posts[0]["num"] == "#012"
    assert posts[0]["date"] == "06·08·2026"  # ISO -> DD·MM·YYYY


def test_render_index_sorts_desc_and_counts(tmp_path):
    _post(tmp_path, 12)
    _post(tmp_path, 3)
    out, n = build_index.render_index(str(tmp_path))
    assert n == 2
    assert out.index("#012") < out.index("#003")
    assert "2 BÀI" in out


def test_render_index_escapes_meta_title(tmp_path):
    # Tiêu đề trong meta có ký tự đặc biệt (< > &) phải được html.escape khi vào index.
    _post(tmp_path, 5, title="A <b>tag</b> & co")
    out, _ = build_index.render_index(str(tmp_path))
    assert "<b>tag</b>" not in out
    assert "&lt;b&gt;tag&lt;/b&gt; &amp; co" in out


def test_render_index_escapes_quotes_like_htmlescape(tmp_path):
    # Dấu " -> &quot; (html.escape), không phải &#34; (markupsafe) — giữ byte cũ.
    _post(tmp_path, 5, lede='He said "hi"')
    out, _ = build_index.render_index(str(tmp_path))
    assert "&quot;hi&quot;" in out


def test_render_index_empty(tmp_path):
    out, n = build_index.render_index(str(tmp_path))
    assert n == 0
    assert "Chưa có bài nào" in out

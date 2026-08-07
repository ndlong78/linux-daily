"""Unit test cho postmeta: đọc khối meta JSON + text hiển thị (không dùng regex)."""
import json

import postmeta
import pytest


def _write(tmp_path, body):
    p = tmp_path / "post-012-demo.html"
    p.write_text(body, encoding="utf-8")
    return str(p)


META = {"issue": 12, "date": "2026-08-06", "axis": "Networking",
        "eyebrow": "Networking · Demo", "slug": "demo",
        "title": "Tiêu đề", "lede": "Lede."}


def _page(meta=META, eyebrow="Networking · Demo", title="Tiêu đề <em>x</em>",
          lede='Lede có <code>mã</code> và "trích".'):
    return (
        "<!DOCTYPE html>\n<html lang=\"vi\">\n<head>\n"
        '<script type="application/json" id="ld-meta">\n'
        + json.dumps(meta, ensure_ascii=False)
        + "\n</script>\n</head>\n<body class=\"post\"><div class=\"wrap\">\n"
        f'<span class="issue">#012 · 06·08·2026</span>\n'
        f'<p class="eyebrow">{eyebrow}</p>\n<h1>{title}</h1>\n'
        f'<p class="lede">{lede}</p>\n'
        "</div></body></html>\n"
    )


def test_read_meta_ok(tmp_path):
    m = postmeta.read_meta(_write(tmp_path, _page()))
    assert m["issue"] == 12
    assert m["slug"] == "demo"


def test_read_meta_missing_block(tmp_path):
    page = "<!DOCTYPE html>\n<html><head></head><body></body></html>"
    with pytest.raises(postmeta.MetaError):
        postmeta.read_meta(_write(tmp_path, page))


def test_read_meta_bad_json(tmp_path):
    page = ('<head><script type="application/json" id="ld-meta">\n'
            '{ not: valid json </script></head>')
    with pytest.raises(postmeta.MetaError):
        postmeta.read_meta(_write(tmp_path, page))


def test_read_visible_strips_inner_tags(tmp_path):
    v = postmeta.read_visible(_write(tmp_path, _page()))
    assert v["issue"] == "#012 · 06·08·2026"
    assert v["eyebrow"] == "Networking · Demo"
    assert v["title"] == "Tiêu đề x"  # <em> bị bỏ
    assert v["lede"] == 'Lede có mã và "trích".'  # <code> bị bỏ, giữ nguyên "


def test_read_visible_first_of_each(tmp_path):
    # Chỉ lấy <h1> đầu tiên.
    page = _page().replace("</body>", "<h1>Tiêu đề thứ hai</h1></body>")
    v = postmeta.read_visible(_write(tmp_path, page))
    assert v["title"] == "Tiêu đề x"

"""Unit test cho validate_repo: từng quy tắc phải bắt đúng lỗi."""
import validate_repo
from validate_repo import (
    Report,
    parse_tweets,
    tweet_length,
    validate_post_file,
    validate_social,
    validate_topics,
)


def make_entries(rows):
    """rows: list (n, date_s, axis, title) -> list dict như parse_topics trả về."""
    return [
        {"lineno": i + 1, "n": n, "date_s": d, "axis": a, "title": t}
        for i, (n, d, a, t) in enumerate(rows)
    ]


def errs(entries):
    r = Report()
    validate_topics(entries, r)
    return r.errors


def test_topics_valid_cycle_passes():
    rows = [
        (1, "2026-01-01", "Networking", "a"),
        (2, "2026-01-03", "Bảo mật", "b"),
        (3, "2026-01-05", "Storage", "c"),
    ]
    assert errs(make_entries(rows)) == []


def test_topics_non_sequential_number():
    rows = [(1, "2026-01-01", "Networking", "a"), (3, "2026-01-03", "Storage", "b")]
    out = errs(make_entries(rows))
    assert any("không liên tục" in e for e in out)


def test_topics_date_goes_backwards():
    rows = [(1, "2026-01-05", "Networking", "a"), (2, "2026-01-01", "Bảo mật", "b")]
    out = errs(make_entries(rows))
    assert any("nhỏ hơn bài trước" in e for e in out)


def test_topics_wrong_axis():
    rows = [(1, "2026-01-01", "Storage", "a")]  # #001 phải là Networking
    out = errs(make_entries(rows))
    assert any("sai chu kỳ" in e for e in out)


def test_topics_axis_cycles_after_seven():
    # Bài #008 quay lại Networking (index (8-1)%7 = 0).
    rows = [(8, "2026-01-01", "Networking", "x")]
    entries = make_entries(rows)
    r = Report()
    validate_topics(entries, r)
    # Chỉ lỗi số bài không liên tục (bắt đầu từ 8), KHÔNG có lỗi trục.
    assert not any("sai chu kỳ" in e for e in r.errors)


def test_topics_duplicate_title():
    rows = [(1, "2026-01-01", "Networking", "Trùng"), (2, "2026-01-03", "Bảo mật", "trùng")]
    out = errs(make_entries(rows))
    assert any("trùng" in e.lower() for e in out)


def test_topics_bad_date_format():
    rows = [(1, "06-08-2026", "Networking", "a")]
    out = errs(make_entries(rows))
    assert any("không phải ISO" in e for e in out)


def _svg(label):
    return f'<svg viewBox="0 0 10 10" role="img" aria-label="{label}"><rect/></svg>'


def valid_post_html(n=12, date_disp="06·08·2026"):
    nums = "".join(f'<h2><span class="num">{i:02d}</span> Mục</h2>' for i in range(1, 8))
    return f"""<!DOCTYPE html>
<html lang="vi">
<head><link rel="stylesheet" href="../assets/style.css"></head>
<body class="post"><div class="wrap">
  <a class="brand-home" href="../index.html">home</a>
  <span class="issue">#{n:03d} · {date_disp}</span>
  <figure>{_svg("hero")}<figcaption>Hình 1</figcaption></figure>
  {nums}
  <div class="code-label bsd">FreeBSD</div>
  <figure>{_svg("so sánh")}<figcaption>Hình 2</figcaption></figure>
  <div class="exercise">Bài tập</div>
  <a class="foot-home" href="../index.html">về trang chủ</a>
</div></body></html>"""


def check_post(tmp_path, html, n=12, name=None, topic_date="2026-08-06"):
    name = name or f"post-{n:03d}-demo.html"
    p = tmp_path / name
    p.write_text(html, encoding="utf-8")
    r = Report()
    validate_post_file(str(p), n, r, topic_date)
    return r.errors


def test_valid_post_passes(tmp_path):
    assert check_post(tmp_path, valid_post_html()) == []


def test_post_leftover_placeholder(tmp_path):
    html = valid_post_html().replace("Bài tập", "{{TODO}}")
    out = check_post(tmp_path, html)
    assert any("placeholder" in e for e in out)


def test_post_wrong_svg_count(tmp_path):
    html = valid_post_html().replace(_svg("so sánh"), "")
    out = check_post(tmp_path, html)
    assert any("2 ảnh SVG" in e for e in out)


def test_post_svg_missing_aria(tmp_path):
    html = valid_post_html().replace(' aria-label="hero"', "")
    out = check_post(tmp_path, html)
    assert any("aria-label" in e for e in out)


def test_post_missing_freebsd_block(tmp_path):
    html = valid_post_html().replace('<div class="code-label bsd">FreeBSD</div>', "")
    out = check_post(tmp_path, html)
    assert any("FreeBSD" in e for e in out)


def test_post_missing_section(tmp_path):
    html = valid_post_html().replace('<h2><span class="num">07</span> Mục</h2>', "")
    out = check_post(tmp_path, html)
    assert any("7 mục" in e for e in out)


def test_post_issue_number_mismatch(tmp_path):
    out = check_post(tmp_path, valid_post_html(n=12), n=13, name="post-013-demo.html")
    # số trong HTML (#012) khác expected (#013)
    assert any("khác topics.md" in e for e in out)


def test_post_date_mismatch(tmp_path):
    out = check_post(tmp_path, valid_post_html(date_disp="01·01·2026"))
    assert any("ngày trong HTML" in e for e in out)


def test_post_bad_filename(tmp_path):
    out = check_post(tmp_path, valid_post_html(), name="post-12-Demo.html")
    assert any("tên file" in e for e in out)


def test_axis_cycle_constant_length():
    assert len(validate_repo.AXIS_CYCLE) == 7


# --- tweet_length: {{LINK}} phải tính bằng 23 ký tự (t.co), không phải 8 ---

def test_tweet_length_no_link_is_plain_len():
    assert tweet_length("abc") == 3


def test_tweet_length_counts_link_as_23():
    # "x " (2) + {{LINK}} tính 23 = 25, không phải 2 + 8 = 10.
    assert tweet_length("x " + validate_repo.LINK_PLACEHOLDER) == 25


def test_tweet_length_counts_multiple_links():
    two = validate_repo.LINK_PLACEHOLDER * 2
    assert tweet_length(two) == 2 * validate_repo.TWEET_URL_LEN


def thread(bodies, leading=""):
    """Dựng nội dung x.txt: mỗi phần tử bodies là nội dung một tweet, đánh số 1..N."""
    parts = [f"[Tweet {i}]\n{b}" for i, b in enumerate(bodies, 1)]
    return (leading + "\n\n" if leading else "") + "\n\n".join(parts) + "\n"


# --- parse_tweets ---

def test_parse_tweets_basic():
    leading, tweets = parse_tweets("[Tweet 1]\naa\n\n[Tweet 2]\nbb\n")
    assert leading == ""
    assert tweets == [(1, "aa"), (2, "bb")]


def test_parse_tweets_captures_leading():
    leading, tweets = parse_tweets("giới thiệu\n[Tweet 1]\naa\n")
    assert leading == "giới thiệu"
    assert tweets == [(1, "aa")]


def test_parse_tweets_no_marker():
    leading, tweets = parse_tweets("chỉ là văn bản")
    assert tweets == []
    assert leading == "chỉ là văn bản"


def _write_social(tmp_path, monkeypatch, n, fb="cap", x=None):
    if x is None:
        x = thread([f"tweet {i}" for i in range(1, 6)])  # 5 tweet hợp lệ
    monkeypatch.setattr(validate_repo, "SOCIAL_DIR", str(tmp_path))
    (tmp_path / f"post-{n:03d}-facebook.txt").write_text(fb, encoding="utf-8")
    (tmp_path / f"post-{n:03d}-x.txt").write_text(x, encoding="utf-8")


def test_social_valid_passes(tmp_path, monkeypatch):
    _write_social(tmp_path, monkeypatch, 1)
    r = Report()
    validate_social(1, r)
    assert r.errors == []


def test_social_tweet_over_limit_with_link(tmp_path, monkeypatch):
    # 265 ký tự thô + {{LINK}} → 265 + 23 = 288 > 280, phải bị bắt.
    bodies = ["ok"] * 4 + ["a" * 265 + " " + validate_repo.LINK_PLACEHOLDER]
    _write_social(tmp_path, monkeypatch, 1, x=thread(bodies))
    r = Report()
    validate_social(1, r)
    assert any("> 280" in e for e in r.errors)


def test_social_tweet_under_limit_without_link_ok(tmp_path, monkeypatch):
    # Cùng độ dài thô nhưng không có {{LINK}} → 266 ≤ 280, không được báo lỗi độ dài.
    bodies = ["ok"] * 4 + ["a" * 266]
    _write_social(tmp_path, monkeypatch, 1, x=thread(bodies))
    r = Report()
    validate_social(1, r)
    assert not any("> 280" in e for e in r.errors)


def test_social_too_few_tweets(tmp_path, monkeypatch):
    _write_social(tmp_path, monkeypatch, 1, x=thread(["a", "b", "c", "d"]))  # 4 < 5
    r = Report()
    validate_social(1, r)
    assert any("cần 5–7" in e for e in r.errors)


def test_social_too_many_tweets(tmp_path, monkeypatch):
    _write_social(tmp_path, monkeypatch, 1, x=thread([str(i) for i in range(8)]))  # 8 > 7
    r = Report()
    validate_social(1, r)
    assert any("cần 5–7" in e for e in r.errors)


def test_social_non_sequential_numbering(tmp_path, monkeypatch):
    # Đúng số lượng (5) nhưng đánh số nhảy cóc 1,2,3,4,6.
    x = "\n\n".join(f"[Tweet {i}]\nx" for i in [1, 2, 3, 4, 6]) + "\n"
    _write_social(tmp_path, monkeypatch, 1, x=x)
    r = Report()
    validate_social(1, r)
    assert any("không liên tục" in e for e in r.errors)


def test_social_intro_before_tweet1(tmp_path, monkeypatch):
    x = thread([f"t{i}" for i in range(1, 6)], leading="Mở đầu lạc chỗ")
    _write_social(tmp_path, monkeypatch, 1, x=x)
    r = Report()
    validate_social(1, r)
    assert any("trước [Tweet 1]" in e for e in r.errors)


def test_social_missing_x_file(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_repo, "SOCIAL_DIR", str(tmp_path))
    (tmp_path / "post-001-facebook.txt").write_text("cap", encoding="utf-8")
    r = Report()
    validate_social(1, r)
    assert any("x.txt" in e for e in r.errors)

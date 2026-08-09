#!/usr/bin/env python3
"""
validate_repo.py — Quality gate cho Linux Daily.

Biến các quy tắc trong AGENTS.md thành kiểm tra bằng phần mềm, để CI chặn merge khi
bài viết hoặc nhật ký chủ đề lệch chuẩn. Chạy:

  python3 tools/validate_repo.py          # kiểm tra toàn repo, exit != 0 nếu có lỗi
  python3 tools/validate_repo.py --quiet   # chỉ in khi có lỗi

Kiểm tra:
  topics.md   — số bài liên tục từ #001, ngày ISO hợp lệ & không giảm, trục đúng chu kỳ 7,
                tiêu đề không trùng.
  posts/      — khối metadata <script id="ld-meta"> đủ trường & khớp topics.md/filename;
                meta không lệch với phần hiển thị (issue/eyebrow/title/lede); không còn
                placeholder {{...}}, đúng 2 <svg> (đều role="img"+aria-label), 2 <figcaption>,
                đủ 7 mục 01–07, có khối FreeBSD (code-label bsd), giữ link CSS chung và hai
                link "về trang chủ", body.post, lang="vi".
  social/     — artifact lịch sử; helper validator vẫn được giữ để audit khi cần nhưng
                không còn là điều kiện bắt buộc cho bài mới trong giai đoạn social tạm dừng.
  index.html  — đồng bộ với posts/ (gọi build_index.render_index).
  state.json  — last_issue & last_published_date khớp bài mới nhất trong topics.md;
                last_generated_at là mốc ISO 8601 hợp lệ.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postmeta  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
SOCIAL_DIR = os.path.join(POSTS_DIR, "social")
TOPICS_PATH = os.path.join(ROOT, "topics.md")
INDEX_PATH = os.path.join(ROOT, "index.html")
STATE_PATH = os.path.join(ROOT, "state.json")

AXIS_CYCLE = [
    "Networking",
    "Bảo mật",
    "Storage",
    "Công cụ mới",
    "Monitoring",
    "Automation",
    "Ôn tập",
]

TWEET_LIMIT = 280
TWEET_URL_LEN = 23
LINK_PLACEHOLDER = "{{LINK}}"
TWEET_MIN = 5
TWEET_MAX = 7
TWEET_MARKER_RE = re.compile(r"\[Tweet (\d+)\]")
TOPIC_LINE_RE = re.compile(r"^#(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$")


def tweet_length(text: str) -> int:
    """Độ dài tweet như X đếm: mỗi {{LINK}} tính bằng 23 ký tự (t.co), không phải 8."""
    return len(text) + text.count(LINK_PLACEHOLDER) * (TWEET_URL_LEN - len(LINK_PLACEHOLDER))


def parse_tweets(txt: str) -> tuple[str, list[tuple[int, str]]]:
    """Tách nội dung x.txt theo các mốc [Tweet n]."""
    matches = list(TWEET_MARKER_RE.finditer(txt))
    if not matches:
        return txt.strip(), []
    leading = txt[: matches[0].start()].strip()
    tweets: list[tuple[int, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(txt)
        tweets.append((int(m.group(1)), txt[start:end].strip()))
    return leading, tweets


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def fail(self, message: str) -> None:
        self.errors.append(message)


def parse_topics(report: Report) -> list[dict]:
    if not os.path.exists(TOPICS_PATH):
        report.fail(f"topics.md không tồn tại tại {TOPICS_PATH}")
        return []
    entries: list[dict] = []
    with open(TOPICS_PATH, encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#") and not TOPIC_LINE_RE.match(line):
                continue
            m = TOPIC_LINE_RE.match(line)
            if not m:
                report.fail(f"topics.md dòng {lineno}: sai định dạng '#NNN | YYYY-MM-DD | trục | tên'")
                continue
            num, date_s, axis, title = m.groups()
            entries.append({
                "lineno": lineno,
                "n": int(num),
                "date_s": date_s.strip(),
                "axis": axis.strip(),
                "title": title.strip(),
            })
    return entries


def validate_topics(entries: list[dict], report: Report) -> None:
    if not entries:
        report.fail("topics.md: không có dòng bài nào hợp lệ.")
        return

    prev_date: dt.date | None = None
    seen_titles: dict[str, int] = {}
    today = dt.date.today()

    for idx, e in enumerate(entries):
        expected_n = idx + 1
        report.check(
            e["n"] == expected_n,
            f"topics.md dòng {e['lineno']}: số bài #{e['n']:03d} không liên tục (mong đợi #{expected_n:03d}).",
        )

        try:
            d = dt.date.fromisoformat(e["date_s"])
        except ValueError:
            report.fail(f"topics.md dòng {e['lineno']}: ngày '{e['date_s']}' không phải ISO YYYY-MM-DD.")
            d = None
        if d is not None:
            report.check(
                d <= today,
                f"topics.md dòng {e['lineno']}: ngày {d.isoformat()} nằm ở tương lai.",
            )
            if prev_date is not None:
                report.check(
                    d >= prev_date,
                    f"topics.md dòng {e['lineno']}: ngày {d.isoformat()} nhỏ hơn bài trước {prev_date.isoformat()} (thứ tự thời gian phải không giảm).",
                )
            prev_date = d

        expected_axis = AXIS_CYCLE[(e["n"] - 1) % len(AXIS_CYCLE)]
        report.check(
            e["axis"] == expected_axis,
            f"topics.md dòng {e['lineno']}: trục '{e['axis']}' sai chu kỳ (bài #{e['n']:03d} phải là '{expected_axis}').",
        )

        key = e["title"].lower()
        if key in seen_titles:
            report.fail(f"topics.md dòng {e['lineno']}: tiêu đề trùng với dòng {seen_titles[key]}.")
        else:
            seen_titles[key] = e["lineno"]


def _count(pattern: str, text: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text, flags))


def validate_post_file(path: str, expected_n: int, report: Report,
                       topic_date: str = "", topic_axis: str = "") -> None:
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        t = f.read()

    m = re.match(r"post-(\d+)-([a-z0-9-]+)\.html$", name)
    file_slug = None
    if not m:
        report.fail(f"{name}: tên file phải dạng post-NNN-slug.html (slug không dấu, chữ thường).")
    else:
        file_n, file_slug = int(m.group(1)), m.group(2)
        report.check(
            file_n == expected_n,
            f"{name}: số trong tên file (#{file_n:03d}) khác số trong topics.md (#{expected_n:03d}).",
        )

    try:
        meta = postmeta.read_meta(path)
    except postmeta.MetaError as exc:
        report.fail(f"{name}: {exc}")
        meta = None

    if meta is not None:
        missing = [k for k in postmeta.REQUIRED_FIELDS if k not in meta or meta[k] in (None, "")]
        report.check(not missing, f"{name}: khối meta thiếu/rỗng trường {missing}.")

        report.check(
            meta.get("issue") == expected_n,
            f"{name}: meta.issue ({meta.get('issue')}) khác topics.md (#{expected_n:03d}).",
        )
        if file_slug is not None:
            report.check(
                meta.get("slug") == file_slug,
                f"{name}: meta.slug ('{meta.get('slug')}') khác slug trong tên file ('{file_slug}').",
            )
        if topic_date:
            report.check(
                meta.get("date") == topic_date,
                f"{name}: meta.date ('{meta.get('date')}') khác topics.md ('{topic_date}').",
            )
        if topic_axis:
            report.check(
                meta.get("axis") == topic_axis,
                f"{name}: meta.axis ('{meta.get('axis')}') khác topics.md ('{topic_axis}').",
            )

        vis = postmeta.read_visible(path)
        if topic_date:
            try:
                d = dt.date.fromisoformat(topic_date)
                expected_issue = f"#{expected_n:03d} · {d.day:02d}·{d.month:02d}·{d.year}"
            except ValueError:
                expected_issue = None
            if expected_issue:
                report.check(
                    vis.get("issue") == expected_issue,
                    f"{name}: <span class=\"issue\"> ('{vis.get('issue')}') khác '{expected_issue}' suy từ topics.md.",
                )
        for key, label in (("eyebrow", "eyebrow"), ("title", "<h1>"), ("lede", "lede")):
            report.check(
                vis.get(key) == meta.get(key),
                f"{name}: {label} hiển thị lệch với meta.{key} (khối meta không khớp nội dung).",
            )

    report.check("{{" not in t and "}}" not in t, f"{name}: còn placeholder '{{{{...}}}}' chưa điền.")
    report.check('href="../assets/style.css"' in t, f"{name}: thiếu link CSS chung ../assets/style.css.")
    report.check('lang="vi"' in t, f"{name}: thiếu lang=\"vi\".")
    report.check('<body class="post">' in t, f'{name}: thiếu <body class="post">.')
    report.check('class="brand-home"' in t, f"{name}: thiếu link về trang chủ ở header (.brand-home).")
    report.check('class="foot-home"' in t, f"{name}: thiếu link về trang chủ ở footer (.foot-home).")

    svg_count = _count(r"<svg", t)
    report.check(svg_count == 2, f"{name}: cần đúng 2 ảnh SVG, đang có {svg_count}.")
    for mo in re.finditer(r"<svg\b[^>]*>", t):
        tag = mo.group(0)
        report.check('role="img"' in tag, f"{name}: một <svg> thiếu role=\"img\".")
        report.check("aria-label" in tag, f"{name}: một <svg> thiếu aria-label.")
    fig_count = _count(r"<figcaption>", t)
    report.check(fig_count == 2, f"{name}: cần 2 <figcaption>, đang có {fig_count}.")

    nums = sorted(re.findall(r'<span class="num">(\d{2})</span>', t))
    report.check(
        nums == [f"{i:02d}" for i in range(1, 8)],
        f"{name}: cần đủ 7 mục đánh số 01–07, đang có {nums}.",
    )

    report.check('class="exercise"' in t, f"{name}: thiếu mục bài tập (.exercise).")
    report.check("code-label bsd" in t, f"{name}: thiếu khối FreeBSD riêng (code-label bsd).")


def validate_social(expected_n: int, report: Report) -> None:
    """Audit helper cho social artifact lịch sử; không gọi từ merge gate mặc định."""
    fb = os.path.join(SOCIAL_DIR, f"post-{expected_n:03d}-facebook.txt")
    x = os.path.join(SOCIAL_DIR, f"post-{expected_n:03d}-x.txt")
    report.check(os.path.exists(fb), f"social: thiếu {os.path.basename(fb)}.")
    if os.path.exists(x):
        with open(x, encoding="utf-8") as f:
            txt = f.read()
        name = os.path.basename(x)
        leading, tweets = parse_tweets(txt)

        if not tweets:
            report.fail(f"social: {name} không có tweet nào đánh dấu [Tweet n].")
            return

        report.check(
            not leading,
            f"social: {name} có nội dung trước [Tweet 1] — mỗi tweet phải bắt đầu bằng mốc [Tweet n].",
        )
        report.check(
            TWEET_MIN <= len(tweets) <= TWEET_MAX,
            f"social: {name} có {len(tweets)} tweet (cần {TWEET_MIN}–{TWEET_MAX}).",
        )
        actual_nums = [num for num, _ in tweets]
        expected_nums = list(range(1, len(tweets) + 1))
        report.check(
            actual_nums == expected_nums,
            f"social: {name} đánh số tweet không liên tục: {actual_nums} (cần {expected_nums}).",
        )
        for num, body in tweets:
            n = tweet_length(body)
            if n > TWEET_LIMIT:
                report.fail(
                    f"social: {name} tweet {num} dài {n} ký tự (> {TWEET_LIMIT}, đã tính {LINK_PLACEHOLDER} = {TWEET_URL_LEN})."
                )
    else:
        report.fail(f"social: thiếu {os.path.basename(x)}.")


def validate_posts(entries: list[dict], report: Report) -> None:
    files = sorted(glob.glob(os.path.join(POSTS_DIR, "post-*.html")))
    by_num: dict[int, str] = {}
    for p in files:
        mm = re.match(r"post-(\d+)-", os.path.basename(p))
        if mm:
            by_num[int(mm.group(1))] = p

    topic_nums = {e["n"] for e in entries}
    file_nums = set(by_num)
    for n in sorted(topic_nums - file_nums):
        report.fail(f"topics.md có bài #{n:03d} nhưng không tìm thấy file posts/post-{n:03d}-*.html.")
    for n in sorted(file_nums - topic_nums):
        report.fail(f"posts/ có bài #{n:03d} nhưng không có dòng tương ứng trong topics.md.")

    for e in entries:
        path = by_num.get(e["n"])
        if path:
            validate_post_file(path, e["n"], report, e["date_s"], e["axis"])


def validate_index(report: Report) -> None:
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    try:
        import build_index
    except Exception as exc:  # pragma: no cover - defensive
        report.fail(f"index: không import được build_index ({exc}).")
        return
    out, _ = build_index.render_index(POSTS_DIR)
    current = ""
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, encoding="utf-8") as f:
            current = f.read()
    report.check(
        current == out,
        "index.html chưa đồng bộ với posts/. Chạy `python3 tools/build_index.py` rồi commit lại.",
    )


def validate_state(entries: list[dict], report: Report) -> None:
    """state.json phải đồng bộ với topics.md (bài mới nhất & ngày của nó)."""
    if not os.path.exists(STATE_PATH):
        report.fail("state.json không tồn tại. Chạy `python3 tools/cadence.py init` rồi commit lại.")
        return
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError) as exc:
        report.fail(f"state.json không đọc được / không phải JSON hợp lệ ({exc}).")
        return

    if not entries:
        return
    last = max(entries, key=lambda e: e["n"])

    report.check(
        state.get("last_issue") == last["n"],
        f"state.json: last_issue ({state.get('last_issue')}) khác bài mới nhất trong topics.md (#{last['n']:03d}). "
        "Chạy `python3 tools/cadence.py record` rồi commit lại.",
    )
    report.check(
        state.get("last_published_date") == last["date_s"],
        f"state.json: last_published_date ('{state.get('last_published_date')}') khác ngày bài mới nhất trong topics.md ('{last['date_s']}').",
    )
    gen = state.get("last_generated_at")
    ok_gen = False
    if isinstance(gen, str):
        try:
            dt.datetime.fromisoformat(gen)
            ok_gen = True
        except ValueError:
            ok_gen = False
    report.check(ok_gen, f"state.json: last_generated_at ('{gen}') không phải mốc ISO 8601 hợp lệ.")


def run() -> Report:
    report = Report()
    entries = parse_topics(report)
    validate_topics(entries, report)
    validate_posts(entries, report)
    validate_index(report)
    validate_state(entries, report)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Quality gate cho Linux Daily.")
    ap.add_argument("--quiet", action="store_true", help="Chỉ in khi có lỗi.")
    args = ap.parse_args()

    report = run()
    if report.errors:
        print(f"✗ Quality gate: {len(report.errors)} lỗi", file=sys.stderr)
        for e in report.errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    if not args.quiet:
        print("✓ Quality gate: tất cả kiểm tra đều đạt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"

STEPS_RE = re.compile(
    r'(?P<block><ol class="steps">.*?</ol>)(?:\s*(?P=block))+',
    re.I | re.S,
)
RUN_CONTEXT_RE = re.compile(
    r'(?P<block><p class="run-context" data-run-as="(?:user|sudo|root)"><strong>Run as:</strong> (?:user|sudo|root)</p>)(?:\s*(?P=block))+',
    re.I | re.S,
)
EXPECTED_RE = re.compile(
    r'(?P<block><h3>Expected Output</h3><p>Kết quả mong đợi: lệnh kiểm chứng phải phản ánh đúng trạng thái vừa cấu hình; nếu tín hiệu không khớp, dừng và xử lý trước khi đóng phiên quản trị hoặc tiếp tục bước phá dữ liệu\.</p>)(?:\s*(?P=block))+',
    re.I | re.S,
)


def main() -> int:
    selected = []
    for path in sorted(POSTS.glob("post-*.html")):
        m = re.match(r"post-(\d{3})-", path.name)
        if m and 1 <= int(m.group(1)) <= 10:
            selected.append(path)
    if len(selected) != 10:
        raise RuntimeError(f"expected 10 posts, found {len(selected)}")
    for path in selected:
        text = path.read_text(encoding="utf-8")
        before = text
        text = STEPS_RE.sub(r"\g<block>", text)
        text = RUN_CONTEXT_RE.sub(r"\g<block>", text)
        text = EXPECTED_RE.sub(r"\g<block>", text)
        path.write_text(text, encoding="utf-8")
        print(f"deduped {path.name}: changed={text != before}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

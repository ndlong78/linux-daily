"""Smoke test cho render_code — cần Pillow (CI cài sẵn; local bỏ qua nếu thiếu)."""
from pathlib import Path

import pytest

pytest.importorskip("PIL")

import render_code  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def test_split_comment_keeps_gap():
    code, comment = render_code.split_comment("ls -la  # liệt kê")
    assert code.endswith(" ")  # có khoảng trắng để không dính comment
    assert comment.startswith("#")


def test_split_comment_full_line():
    code, comment = render_code.split_comment("# chỉ là chú thích")
    assert code == ""
    assert comment == "# chỉ là chú thích"


def test_split_comment_url_not_split():
    code, comment = render_code.split_comment("curl https://a/b#frag")
    assert comment is None
    assert "#frag" in code


def test_wrap_lines_bounds_width():
    wrapped = render_code.wrap_lines(["x" * 250], max_cols=92)
    assert all(len(line) <= 92 for line in wrapped)
    assert len(wrapped) == 3


def test_render_produces_png(tmp_path):
    src = tmp_path / "snippet.txt"
    src.write_text("sudo systemctl restart nginx  # khởi động lại\npkg install nginx\n", encoding="utf-8")
    out = tmp_path / "out.png"
    # Gọi qua argv để dùng đúng luồng chính.
    import sys
    argv = sys.argv
    sys.argv = ["render_code.py", "--in", str(src), "--out", str(out), "--title", "Test #001"]
    try:
        assert render_code.main() == 0
    finally:
        sys.argv = argv
    assert out.exists() and out.stat().st_size > 0
    from PIL import Image
    with Image.open(out) as im:
        assert im.width > 0 and im.height > 0


def test_render_empty_input_errors(tmp_path):
    src = tmp_path / "empty.txt"
    src.write_text("\n\n", encoding="utf-8")
    out = tmp_path / "out.png"
    import sys
    argv = sys.argv
    sys.argv = ["render_code.py", "--in", str(src), "--out", str(out)]
    try:
        assert render_code.main() == 2
    finally:
        sys.argv = argv
    assert not out.exists()


# --- CI không còn cài font hệ thống: bundle trong repo phải tự đủ ---

def test_bundled_fonts_are_tracked_in_the_repository():
    """CI đã bỏ `apt-get install fonts-dejavu-core`, nên bundle phải có thật.

    Bước apt đó cài một fallback không bao giờ được dùng tới (load_font đọc
    tools/fonts/ trước) nhưng lại là bước chậm nhất của CI và đã treo runner.
    Xoá được nó chỉ vì hai file dưới đây nằm trong git — nếu ai đó gỡ chúng thì
    render_code sẽ hỏng trên runner sạch, ở bước cuối cùng của CI.
    """
    fonts = ROOT / "tools" / "fonts"
    for name in ("JetBrainsMono-Regular.ttf", "JetBrainsMono-Bold.ttf"):
        assert (fonts / name).is_file(), f"thiếu font bundle {name}"


def test_load_font_never_depends_on_a_system_font():
    """Font thực dùng phải nằm trong repo, không phải /usr/share/fonts.

    Đây là bất biến cho phép CI chạy trên runner không cài font nào.
    """
    fonts_dir = (ROOT / "tools" / "fonts").resolve()
    for bold in (False, True):
        resolved = Path(render_code.load_font(bold=bold, size=16).path).resolve()
        assert resolved.parent == fonts_dir, (
            f"load_font(bold={bold}) rơi về font hệ thống {resolved}; "
            "CI không cài font nên trên runner sạch bước này sẽ hỏng"
        )

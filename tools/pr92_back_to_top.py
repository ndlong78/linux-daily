#!/usr/bin/env python3
"""One-shot helper: add a shared, accessible back-to-top control to PR #92."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise RuntimeError(f"{path}: marker not found: {old!r}")
    write(path, text.replace(old, new, 1))


def patch_navigation_template() -> None:
    path = "templates/_global-nav.template.html"
    text = read(path)
    text = text.replace(
        '<nav class="global-nav" aria-label="Điều hướng chính">',
        '<nav class="global-nav" id="page-top" aria-label="Điều hướng chính">',
        1,
    )
    if "<!-- back-to-top:start -->" not in text:
        block = '''<!-- back-to-top:start -->
<a class="back-to-top" href="#page-top" aria-label="Lên đầu trang" title="Lên đầu trang">
  <span aria-hidden="true">↑</span>
</a>
<script src="{{ nav_prefix }}assets/back-to-top.js" defer></script>
<!-- back-to-top:end -->
'''
        text = text.rstrip() + "\n" + block
    write(path, text)


def patch_backfill() -> None:
    path = "tools/backfill_navigation.py"
    text = read(path)
    marker = 'NAV_RE = re.compile(r\'<nav class="global-nav"[^>]*>.*?</nav>\\n?\', re.DOTALL)\n'
    addition = marker + (
        'BACK_TO_TOP_RE = re.compile(\n'
        '    r"<!-- back-to-top:start -->.*?<!-- back-to-top:end -->\\n?", re.DOTALL\n'
        ')\n'
    )
    if "BACK_TO_TOP_RE" not in text:
        if marker not in text:
            raise RuntimeError("backfill_navigation.py: NAV_RE marker not found")
        text = text.replace(marker, addition, 1)
    text = text.replace(
        '    clean = NAV_RE.sub("", text)\n',
        '    clean = BACK_TO_TOP_RE.sub("", NAV_RE.sub("", text))\n',
        1,
    )
    write(path, text)


def patch_style() -> None:
    path = "assets/style.css"
    text = read(path)
    if ".back-to-top{" not in text:
        text = text.rstrip() + '''

/* Floating back-to-top control: visible after meaningful scroll when JS is available. */
.back-to-top{position:fixed;right:18px;bottom:18px;right:max(18px,env(safe-area-inset-right));bottom:max(18px,env(safe-area-inset-bottom));z-index:900;display:grid;place-items:center;width:46px;height:46px;border:1px solid rgba(20,32,29,.16);border-radius:50%;background:rgba(255,255,255,.96);color:var(--ink);text-decoration:none;box-shadow:0 6px 18px rgba(20,32,29,.16);font-family:"Be Vietnam Pro",system-ui,sans-serif;font-size:25px;font-weight:700;line-height:1;transition:opacity .16s ease,visibility .16s ease,transform .16s ease,box-shadow .16s ease,background .16s ease}
.back-to-top:hover{background:var(--surface);color:var(--accent-deep);text-decoration:none;transform:translateY(-2px);box-shadow:0 9px 22px rgba(20,32,29,.2)}
.back-to-top:active{transform:translateY(0)}
.back-to-top span{transform:translateY(-1px)}
.back-to-top-enhanced .back-to-top{opacity:0;visibility:hidden;pointer-events:none;transform:translateY(8px)}
.back-to-top-enhanced .back-to-top.is-visible{opacity:.98;visibility:visible;pointer-events:auto;transform:translateY(0)}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
@media (max-width:520px){.back-to-top{right:14px;bottom:14px;right:max(14px,env(safe-area-inset-right));bottom:max(14px,env(safe-area-inset-bottom));width:44px;height:44px;font-size:24px}}
''' + "\n"
    write(path, text)


def create_script() -> None:
    path = ROOT / "assets" / "back-to-top.js"
    content = '''(() => {
  const button = document.querySelector(".back-to-top");
  if (!button) return;

  document.documentElement.classList.add("back-to-top-enhanced");
  const update = () => button.classList.toggle("is-visible", window.scrollY > 480);
  update();
  window.addEventListener("scroll", update, { passive: true });
})();
'''
    path.write_text(content, encoding="utf-8")


def patch_validator() -> None:
    path = "tools/validate_site.py"
    text = read(path)
    old = '''    parser = _parse_page(path)
    page = os.path.relpath(path, ROOT)
    if parser.global_nav_count != 1:
'''
    new = '''    parser = _parse_page(path)
    page = os.path.relpath(path, ROOT)
    with open(path, encoding="utf-8") as f:
        markup = f.read()
    if markup.count('id="page-top"') != 1:
        report.errors.append(f"{page}: cần đúng 1 target id=page-top")
    if markup.count('class="back-to-top"') != 1:
        report.errors.append(f"{page}: cần đúng 1 nút back-to-top")
    expected_script = f'<script src="{prefix}assets/back-to-top.js" defer></script>'
    if expected_script not in markup:
        report.errors.append(f"{page}: thiếu back-to-top script đúng relative path")
    if 'class="back-to-top" href="#page-top" aria-label="Lên đầu trang"' not in markup:
        report.errors.append(f"{page}: back-to-top thiếu href/aria-label chuẩn")
    if parser.global_nav_count != 1:
'''
    if "cần đúng 1 nút back-to-top" not in text:
        if old not in text:
            raise RuntimeError("validate_site.py: navigation check marker not found")
        text = text.replace(old, new, 1)
    write(path, text)


def patch_tests() -> None:
    path = "tests/test_navigation.py"
    text = read(path)
    if "test_back_to_top_control_is_shared_accessible_and_progressive" not in text:
        text = text.rstrip() + '''


def test_back_to_top_control_is_shared_accessible_and_progressive():
    home = backfill_navigation._env().get_template("_global-nav.template.html").render(
        nav_prefix="", nav_current="home"
    )
    assert 'id="page-top"' in home
    assert home.count('class="back-to-top"') == 1
    assert 'href="#page-top"' in home
    assert 'aria-label="Lên đầu trang"' in home
    assert 'aria-hidden="true">↑</span>' in home
    assert 'src="assets/back-to-top.js"' in home

    post = backfill_navigation.render_navigation(prefix="../")
    assert 'src="../assets/back-to-top.js"' in post

    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    assert ".back-to-top{" in css
    assert ".back-to-top-enhanced .back-to-top.is-visible" in css
    assert "scroll-behavior:smooth" in css

    script = (ROOT / "assets" / "back-to-top.js").read_text(encoding="utf-8")
    assert "window.scrollY > 480" in script
    assert 'classList.toggle("is-visible"' in script
''' + "\n"
    write(path, text)


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    patch_navigation_template()
    patch_backfill()
    patch_style()
    create_script()
    patch_validator()
    patch_tests()

    run([sys.executable, "tools/build.py"])
    run(["ruff", "check", "--fix", "tools/backfill_navigation.py", "tools/validate_site.py", "tests/test_navigation.py"])
    run(["pytest", "-q", "tests/test_navigation.py", "tests/test_validate_site.py", "tests/test_build_index.py", "tests/test_build_archive.py", "tests/test_learning_paths.py", "tests/test_learning_dashboard.py"])
    run([sys.executable, "tools/publish.py", "check"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

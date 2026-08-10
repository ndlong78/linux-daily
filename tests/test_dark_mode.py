from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE_PATH = ROOT / "assets" / "style.css"
RELATED_PATH = ROOT / "assets" / "related.css"
DASHBOARD_PATH = ROOT / "assets" / "learning-dashboard.css"
DARK_MEDIA = "@media (prefers-color-scheme:dark)"


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]

    def linearize(value: float) -> float:
        if value <= 0.04045:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (linearize(value) for value in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast_ratio(first: str, second: str) -> float:
    first_luminance = _relative_luminance(first)
    second_luminance = _relative_luminance(second)
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _dark_section(css: str) -> str:
    assert DARK_MEDIA in css, "CSS phải hỗ trợ system dark mode"
    return css.split(DARK_MEDIA, 1)[1]


def _dark_variables() -> dict[str, str]:
    dark = _dark_section(STYLE_PATH.read_text(encoding="utf-8"))
    root = re.search(r":root\{([^}]*)\}", dark)
    assert root, "dark mode phải override :root variables"
    return dict(re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})", root.group(1)))


def test_system_dark_mode_overrides_core_palette():
    css = STYLE_PATH.read_text(encoding="utf-8")
    dark = _dark_section(css)
    variables = _dark_variables()

    assert "color-scheme:dark" in dark
    for name in (
        "bg",
        "surface",
        "ink",
        "muted",
        "accent",
        "accent-deep",
        "freebsd",
        "line",
        "code-bg",
        "code-text",
        "code-muted",
    ):
        assert name in variables


def test_dark_palette_keeps_text_and_semantic_accents_readable():
    variables = _dark_variables()
    pairs = (
        ("ink", "bg", 7.0),
        ("muted", "bg", 4.5),
        ("accent-deep", "bg", 4.5),
        ("freebsd", "bg", 4.5),
        ("ink", "surface", 7.0),
        ("muted", "surface", 4.5),
        ("accent-deep", "surface", 4.5),
        ("freebsd", "surface", 4.5),
        ("code-text", "code-bg", 7.0),
    )
    for foreground, background, minimum in pairs:
        ratio = _contrast_ratio(variables[foreground], variables[background])
        assert ratio >= minimum, (
            f"dark {foreground}/{background} contrast quá thấp: {ratio:.2f}:1"
        )


def test_dark_mode_covers_non_variable_light_surfaces():
    style_dark = _dark_section(STYLE_PATH.read_text(encoding="utf-8"))
    related_dark = _dark_section(RELATED_PATH.read_text(encoding="utf-8"))
    dashboard_dark = _dark_section(DASHBOARD_PATH.read_text(encoding="utf-8"))

    assert ".skip-link{" in style_dark
    assert ".style-contract{" in style_dark
    assert ".exercise{" in style_dark
    assert ".back-to-top{" in style_dark
    assert ".related-more{" in related_dark
    assert ".series-link:hover{" in related_dark
    assert ".attention-note{" in dashboard_dark
    assert ".status-attention{" in dashboard_dark

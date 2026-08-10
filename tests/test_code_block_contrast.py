from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE_PATH = ROOT / "assets" / "style.css"


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


def _declarations(block: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for declaration in block.split(";"):
        if ":" not in declaration:
            continue
        key, value = declaration.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def test_code_block_overrides_inline_code_color_inside_steps():
    css = STYLE_PATH.read_text(encoding="utf-8")
    match = re.search(r"pre\s*>\s*code\s*\{([^}]*)\}", css)
    assert match, "style.css phải có rule riêng cho pre > code"

    declarations = _declarations(match.group(1))
    assert declarations.get("color") == "var(--code-text)"
    assert declarations.get("background") == "transparent"
    assert declarations.get("padding") == "0"
    assert declarations.get("font-size") == "inherit"


def test_dark_code_block_palette_has_high_contrast():
    css = STYLE_PATH.read_text(encoding="utf-8")
    variables = dict(
        re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})", css)
    )
    ratio = _contrast_ratio(variables["code-bg"], variables["code-text"])
    assert ratio >= 7.0, f"code block contrast quá thấp: {ratio:.2f}:1"

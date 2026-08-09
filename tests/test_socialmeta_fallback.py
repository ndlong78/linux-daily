from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import socialmeta  # noqa: E402


def test_missing_dedicated_preview_uses_latest_historical_image():
    info = socialmeta.image_info(999, "Future lesson without social artifact", "https://linux.no.id.vn/")

    assert info["path"].startswith("posts/social/post-")
    assert info["path"].endswith("-code.png")
    assert info["path"] != "posts/social/post-999-code.png"
    assert (ROOT / str(info["path"])).is_file()
    assert info["mime"] == "image/png"
    assert int(info["width"]) > 0
    assert int(info["height"]) > 0
    assert "preview chung" in str(info["alt"])


def test_existing_dedicated_preview_keeps_issue_specific_alt():
    info = socialmeta.image_info(21, "Storage lesson", "https://linux.no.id.vn/")

    assert info["path"] == "posts/social/post-021-code.png"
    assert info["alt"] == "Linux Daily #021 — Storage lesson"

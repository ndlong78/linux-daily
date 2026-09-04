import os
import sys

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
sys.path.insert(0, TOOLS)

import repo_health  # noqa: E402


def test_repository_health_baseline_passes():
    health = repo_health.collect()
    assert health.errors == []
    assert health.metrics["posts"] > 0
    # 4 trang tĩnh + n trang phân trang. Không viết cứng số trang phân trang: nó
    # đổi theo số bài, và viết cứng nghĩa là test đỏ ở đúng lần ra bài thứ 21.
    assert health.metrics["paging_pages"] >= 1
    assert health.metrics["generated_pages"] == (
        health.metrics["posts"] + 4 + health.metrics["paging_pages"]
    )
    assert health.metrics["sitemap_urls"] == health.metrics["generated_pages"]
    assert health.metrics["social_code_images"] >= 1
    assert health.metrics["social_preview_coverage"] == health.metrics["posts"]
    assert health.metrics["technical_sources"] >= health.metrics["posts"] * 2
    assert health.metrics["woff2_fonts"] >= 1

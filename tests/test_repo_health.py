import os
import sys

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
sys.path.insert(0, TOOLS)

import repo_health  # noqa: E402


def test_repository_health_baseline_passes():
    health = repo_health.collect()
    assert health.errors == []
    assert health.metrics["posts"] > 0
    assert health.metrics["generated_pages"] == health.metrics["posts"] + 4
    assert health.metrics["sitemap_urls"] == health.metrics["generated_pages"]
    assert health.metrics["social_code_images"] >= health.metrics["posts"]
    assert health.metrics["technical_sources"] >= health.metrics["posts"] * 2
    assert health.metrics["woff2_fonts"] >= 1

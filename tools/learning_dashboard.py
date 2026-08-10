#!/usr/bin/env python3
"""Build/check the derived public Learning Dashboard from P8 learning signals."""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

from jinja2 import Environment, FileSystemLoader, select_autoescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import learning_metadata  # noqa: E402
import learning_paths  # noqa: E402
import topic_progression  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "learning-dashboard.html"
SITE_CONFIG = ROOT / "site.json"
TEMPLATES_DIR = ROOT / "templates"
NAV_TEMPLATE = "_global-nav.template.html"


def _site() -> dict:
    site = json.loads(SITE_CONFIG.read_text(encoding="utf-8"))
    site["url"] = str(site["url"]).rstrip("/") + "/"
    return site


def _navigation() -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    return env.get_template(NAV_TEMPLATE).render(
        nav_prefix="", nav_current="dashboard"
    ).strip()


def collect(
    path_result: dict | None = None,
    progression_result: dict | None = None,
) -> dict:
    paths = path_result if path_result is not None else learning_paths.review()
    progression = (
        progression_result
        if progression_result is not None
        else topic_progression.review(path_result=paths)
    )
    summaries = {
        item["slug"]: item for item in progression.get("path_summaries", [])
    }
    dashboard_paths: list[dict] = []
    for path in paths.get("paths", []):
        counts = Counter(
            str(step.get("difficulty", ""))
            for step in path.get("steps", [])
            if str(step.get("difficulty", "")) in learning_metadata.DIFFICULTY_LABELS
        )
        summary = summaries.get(path["slug"], {})
        maximum = str(summary.get("maximum_difficulty", ""))
        dashboard_paths.append(
            {
                "slug": path["slug"],
                "title": path["title"],
                "goal": path["goal"],
                "steps": len(path.get("steps", [])),
                "basic": counts.get("basic", 0),
                "intermediate": counts.get("intermediate", 0),
                "advanced": counts.get("advanced", 0),
                "local_prerequisites": int(summary.get("local_prerequisites", 0)),
                "external_prerequisites": int(summary.get("external_prerequisites", 0)),
                "maximum_difficulty": maximum,
                "maximum_difficulty_label": learning_metadata.DIFFICULTY_LABELS.get(
                    maximum, "Không xác định"
                ),
            }
        )

    site = _site()
    learning = paths.get("learning", {})
    difficulty_counts = learning.get("difficulty_counts", {})
    return {
        "status": progression.get("status", "FAIL"),
        "post_count": len(paths.get("posts", {})),
        "path_count": len(paths.get("paths", [])),
        "covered_post_count": len(paths.get("assigned_issues", set())),
        "difficulty_counts": {
            key: int(difficulty_counts.get(key, 0))
            for key in learning_metadata.DIFFICULTY_LABELS
        },
        "prerequisite_edges": int(learning.get("prerequisite_edges", 0)),
        "path_prerequisite_references": int(
            progression.get("total_prerequisite_references", 0)
        ),
        "local_prerequisites": int(
            progression.get("local_prerequisite_references", 0)
        ),
        "external_prerequisites": int(
            progression.get("external_prerequisite_references", 0)
        ),
        "hard_findings": len(progression.get("hard_findings", [])),
        "missing_difficulty_tiers": list(
            progression.get("missing_difficulty_tiers", [])
        ),
        "paths": dashboard_paths,
        "canonical_url": urljoin(site["url"], "learning-dashboard.html"),
        "errors": [
            *paths.get("errors", []),
            *progression.get("upstream_errors", []),
            *[item["message"] for item in progression.get("hard_findings", [])],
        ],
    }


def structured(result: dict) -> dict:
    return {
        key: value
        for key, value in result.items()
        if key not in {"canonical_url"}
    }


def render_page(result: dict) -> str:
    esc = html.escape
    counts = result["difficulty_counts"]
    nav_lines = ["    " + line for line in _navigation().splitlines()]
    missing_labels = [
        learning_metadata.DIFFICULTY_LABELS.get(tier, tier)
        for tier in result["missing_difficulty_tiers"]
    ]
    missing_text = ", ".join(missing_labels)
    lines = [
        "<!DOCTYPE html>",
        '<html lang="vi">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "<title>Learning Dashboard — Linux Daily</title>",
        '<meta name="description" content="Dashboard tổng hợp lộ trình, độ khó, prerequisite và progression health của Linux Daily.">',
        f'<link rel="canonical" href="{esc(result["canonical_url"], quote=True)}">',
        '<link rel="preload" href="assets/fonts/be-vietnam-pro-800.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="stylesheet" href="assets/fonts.css">',
        '<link rel="stylesheet" href="assets/style.css">',
        '<link rel="stylesheet" href="assets/learning-dashboard.css">',
        "</head>",
        '<body class="learning-dashboard">',
        '  <a class="skip-link" href="#main-content">Đi tới nội dung chính</a>',
        '  <div class="wrap">',
        *nav_lines,
        '    <header class="site">',
        '      <div class="site-brand">Linux Daily</div>',
        '      <h1 class="site">Learning Dashboard</h1>',
        '      <p class="site-lede">Một view tổng hợp từ Learning Paths, Difficulty &amp; Prerequisites và Topic Progression — không tạo thêm curriculum source of truth.</p>',
        "    </header>",
        '    <main id="main-content">',
        '      <section aria-labelledby="curriculum-overview">',
        '        <h2 id="curriculum-overview">Tổng quan curriculum</h2>',
        '        <div class="metric-grid">',
        f'          <div class="metric"><strong>{result["post_count"]}</strong><span>BÀI</span></div>',
        f'          <div class="metric"><strong>{result["path_count"]}</strong><span>LỘ TRÌNH</span></div>',
        f'          <div class="metric"><strong>{result["prerequisite_edges"]}</strong><span>PREREQUISITE EDGES</span></div>',
        f'          <div class="metric status-{result["status"].lower()}"><strong>{esc(result["status"])}</strong><span>PROGRESSION</span></div>',
        "        </div>",
        "      </section>",
        '      <section aria-labelledby="difficulty-mix">',
        '        <h2 id="difficulty-mix">Độ khó</h2>',
        '        <div class="difficulty-grid">',
        f'          <div><strong>{counts["basic"]}</strong><span>Cơ bản</span></div>',
        f'          <div><strong>{counts["intermediate"]}</strong><span>Trung cấp</span></div>',
        f'          <div><strong>{counts["advanced"]}</strong><span>Nâng cao</span></div>',
        "        </div>",
    ]
    if missing_text:
        lines.append(
            '        <p class="attention-note"><strong>ATTENTION:</strong> '
            f'curriculum chưa có bài {esc(missing_text)}. Đây là gap được giữ nguyên để theo dõi, '
            'không relabel bài cũ chỉ để đạt PASS.</p>'
        )
    lines.extend(
        [
            "      </section>",
            '      <section aria-labelledby="progression-health">',
            '        <h2 id="progression-health">Progression health</h2>',
            '        <ul class="health-list">',
            f'          <li><strong>{result["hard_findings"]}</strong> hard findings: không có prerequisite đứng sau dependent và không có difficulty jump quá một tier.</li>',
            f'          <li><strong>{result["path_prerequisite_references"]}</strong> prerequisite references trong các learning path: <strong>{result["local_prerequisites"]} local</strong> + <strong>{result["external_prerequisites"]} cross-path</strong>.</li>',
            '          <li>Cross-path prerequisite là dependency hợp lệ; người học dùng link “Học trước” thay vì coi đó là ordering failure.</li>',
            "        </ul>",
            "      </section>",
            '      <section aria-labelledby="path-health">',
            '        <h2 id="path-health">Các lộ trình</h2>',
            '        <div class="dashboard-paths">',
        ]
    )
    for path in result["paths"]:
        lines.extend(
            [
                '          <article class="dashboard-path">',
                f'            <h3>{esc(path["title"])}</h3>',
                f'            <p>{esc(path["goal"])}</p>',
                f'            <p class="path-health-meta">{path["steps"]} bước · {path["basic"]} Cơ bản · {path["intermediate"]} Trung cấp · {path["advanced"]} Nâng cao</p>',
                f'            <p class="path-health-meta">Prerequisite: {path["local_prerequisites"]} local · {path["external_prerequisites"]} cross-path · Mức cao nhất: {esc(path["maximum_difficulty_label"])}</p>',
                f'            <a class="path-cta" href="learning-paths.html#{esc(path["slug"], quote=True)}">Mở lộ trình →</a>',
                "          </article>",
            ]
        )
    lines.extend(
        [
            "        </div>",
            "      </section>",
            "    </main>",
            "    <footer>Linux Daily · Learning Dashboard · #LinuxDaily #SysAdmin</footer>",
            "  </div>",
            "</body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(lines)


def run(*, check: bool = False, json_output: bool = False) -> int:
    result = collect()
    if json_output:
        print(json.dumps(structured(result), ensure_ascii=False, indent=2))
        return 1 if result["errors"] else 0
    if result["errors"]:
        for error in result["errors"]:
            print(f"LỖI: {error}", file=sys.stderr)
        return 1

    expected = render_page(result)
    if check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != expected:
            print(
                "LỖI: learning-dashboard.html chưa đồng bộ. "
                "Chạy `python3 tools/learning_dashboard.py` rồi commit lại.",
                file=sys.stderr,
            )
            return 1
        print(
            "OK: learning dashboard đồng bộ; "
            f"status={result['status']}, paths={result['path_count']}, posts={result['post_count']}."
        )
        return 0

    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(
        "Đã cập nhật learning-dashboard.html; "
        f"status={result['status']}, paths={result['path_count']}, posts={result['post_count']}."
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check, json_output=args.json)


if __name__ == "__main__":
    raise SystemExit(main())

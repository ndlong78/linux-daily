#!/usr/bin/env python3
"""Generate/check deterministic related-content navigation inside every post."""
from __future__ import annotations

import argparse
import glob
import html
from dataclasses import dataclass
from pathlib import Path

import postmeta
import taxonomy

ROOT = Path(__file__).resolve().parents[1]
POSTS_GLOB = str(ROOT / "posts" / "post-*.html")
START = "<!-- related-nav:start -->"
END = "<!-- related-nav:end -->"


@dataclass(frozen=True)
class Post:
    issue: int
    axis: str
    title: str
    eyebrow: str
    path: Path

    @property
    def href(self) -> str:
        return self.path.name

    @property
    def tags(self) -> tuple[str, ...]:
        parts = [part.strip() for part in self.eyebrow.split("·") if part.strip()]
        return tuple(parts[1:])


def collect_posts() -> list[Post]:
    posts: list[Post] = []
    for raw in glob.glob(POSTS_GLOB):
        path = Path(raw)
        meta = postmeta.read_meta(str(path))
        posts.append(
            Post(
                issue=int(meta["issue"]),
                axis=str(meta["axis"]).strip(),
                title=str(meta["title"]).strip(),
                eyebrow=str(meta["eyebrow"]).strip(),
                path=path,
            )
        )
    posts.sort(key=lambda item: item.issue)
    return posts


def _neighbors(post: Post, posts: list[Post]) -> tuple[Post | None, Post | None]:
    series = [item for item in posts if item.axis == post.axis]
    index = series.index(post)
    previous = series[index - 1] if index > 0 else None
    following = series[index + 1] if index + 1 < len(series) else None
    return previous, following


def _related(post: Post, posts: list[Post], limit: int = 3) -> list[Post]:
    candidates = [item for item in posts if item != post and item.axis == post.axis]
    post_tags = set(post.tags)
    candidates.sort(
        key=lambda item: (
            -len(post_tags.intersection(item.tags)),
            abs(item.issue - post.issue),
            -item.issue,
        )
    )
    return candidates[:limit]


def _link(post: Post, rel: str) -> str:
    return (
        f'<a class="series-link {rel}" href="{html.escape(post.href, quote=True)}">'
        f'<span class="series-kicker">#{post.issue:03d}</span>'
        f'<span>{html.escape(post.title)}</span></a>'
    )


def render_block(post: Post, posts: list[Post]) -> str:
    config = taxonomy.load_taxonomy()["axes"][post.axis]
    previous, following = _neighbors(post, posts)
    related = _related(post, posts)
    lines = [
        START,
        '<nav class="related-nav" aria-label="Điều hướng bài cùng chủ đề">',
        '  <div class="related-head">',
        f'    <span class="related-eyebrow">SERIES · {html.escape(config["label"])}</span>',
        '  </div>',
        '  <div class="series-links">',
    ]
    if previous:
        lines.append("    " + _link(previous, "previous"))
    else:
        lines.append('    <span class="series-link is-empty" aria-hidden="true"></span>')
    if following:
        lines.append("    " + _link(following, "next"))
    else:
        lines.append('    <span class="series-link is-empty" aria-hidden="true"></span>')
    lines.append("  </div>")
    if related:
        lines.extend(
            [
                '  <div class="related-more">',
                "    <strong>Cùng chủ đề</strong>",
                "    <ul>",
            ]
        )
        for item in related:
            lines.append(
                f'      <li><a href="{html.escape(item.href, quote=True)}">'
                f'#{item.issue:03d} · {html.escape(item.title)}</a></li>'
            )
        lines.extend(["    </ul>", "  </div>"])
    lines.extend(["</nav>", END])
    return "\n".join(lines)


def _replace(text: str, block: str) -> str:
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise ValueError("related-nav markers không hợp lệ")
        before, rest = text.split(START, 1)
        _, after = rest.split(END, 1)
        return before.rstrip() + "\n\n" + block + after
    marker = "<footer>"
    if marker not in text:
        raise ValueError("không tìm thấy <footer> để chèn related navigation")
    return text.replace(marker, block + "\n\n  " + marker, 1)


def expected_outputs() -> dict[Path, str]:
    posts = collect_posts()
    return {
        post.path: _replace(post.path.read_text(encoding="utf-8"), render_block(post, posts))
        for post in posts
    }


def run(*, check: bool) -> int:
    errors: list[str] = []
    for path, expected in expected_outputs().items():
        current = path.read_text(encoding="utf-8")
        if current == expected:
            continue
        if check:
            errors.append(path.name)
        else:
            path.write_text(expected, encoding="utf-8")
    if errors:
        print("LỖI: related navigation chưa đồng bộ: " + ", ".join(errors))
        return 1
    if check:
        print("OK: related-content navigation đã đồng bộ cho mọi bài.")
    else:
        print("Đã cập nhật related-content navigation cho mọi bài.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Chỉ kiểm tra, không ghi file.")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())

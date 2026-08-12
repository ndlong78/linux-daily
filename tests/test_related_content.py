from __future__ import annotations

import related_content


def test_every_axis_post_has_deterministic_neighbors():
    posts = related_content.collect_posts()
    assert len(posts) >= 19
    for post in posts:
        previous, following = related_content._neighbors(post, posts)
        if previous:
            assert previous.axis == post.axis
            assert previous.issue < post.issue
        if following:
            assert following.axis == post.axis
            assert following.issue > post.issue


def test_related_posts_stay_in_same_axis_and_are_bounded():
    posts = related_content.collect_posts()
    for post in posts:
        related = related_content._related(post, posts)
        assert len(related) <= 3
        assert all(item != post for item in related)
        assert all(item.axis == post.axis for item in related)


def test_render_block_is_accessible_and_stable():
    posts = related_content.collect_posts()
    post = posts[-1]
    first = related_content.render_block(post, posts)
    second = related_content.render_block(post, posts)
    assert first == second
    assert 'aria-label="Điều hướng bài cùng chủ đề"' in first
    assert related_content.START in first
    assert related_content.END in first


def test_first_related_nav_insertion_is_idempotent():
    source = "<html><head></head><body><section>body</section>\n<footer>foot</footer></body></html>"
    block = f"{related_content.START}\n<nav>related</nav>\n{related_content.END}"

    first = related_content._replace(source, block)
    second = related_content._replace(first, block)

    assert first == second
    assert "</section>\n\n<!-- related-nav:start -->" in first


def test_current_repository_navigation_is_synced():
    assert related_content.run(check=True) == 0

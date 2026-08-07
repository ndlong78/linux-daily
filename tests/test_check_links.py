from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import check_links  # noqa: E402


def test_local_target_resolves_relative_root_and_fragment():
    host = "linux.no.id.vn"
    assert check_links._local_target(
        "posts/post-019-example.html", "../assets/style.css", host
    ) == ("assets/style.css", "")
    assert check_links._local_target(
        "posts/post-019-example.html", "/feed.xml", host
    ) == ("feed.xml", "")
    assert check_links._local_target(
        "posts/post-019-example.html", "#technical-sources", host
    ) == ("posts/post-019-example.html", "technical-sources")


def test_same_site_absolute_url_is_internal():
    resolved = check_links._local_target(
        "index.html",
        "https://linux.no.id.vn/posts/post-019-triage-hieu-nang-vmstat-iostat.html",
        "linux.no.id.vn",
    )
    assert resolved == ("posts/post-019-triage-hieu-nang-vmstat-iostat.html", "")


def test_other_https_url_is_external():
    assert check_links._local_target(
        "index.html", "https://docs.python.org/3/", "linux.no.id.vn"
    ) is None


def test_external_status_policy_is_strict_only_for_definite_client_errors():
    assert check_links.classify_status("https://example.test", 200).outcome == "ok"
    assert check_links.classify_status("https://example.test", 301).outcome == "ok"
    assert check_links.classify_status("https://example.test", 404).outcome == "hard"
    assert check_links.classify_status("https://example.test", 410).outcome == "hard"
    assert check_links.classify_status("https://example.test", 403).outcome == "warning"
    assert check_links.classify_status("https://example.test", 429).outcome == "warning"
    assert check_links.classify_status("https://example.test", 503).outcome == "warning"


def test_legacy_broken_urls_have_been_removed_from_repository():
    urls = set(check_links.collect_external_urls())
    retired = {
        "https://docs.fedoraproject.org/en-US/fedora/f30/system-administrators-guide/basic-system-configuration/Gaining_Privileges/",
        "https://docs.fedoraproject.org/ko/fedora/f30/system-administrators-guide/basic-system-configuration/Gaining_Privileges/",
        "https://docs.fedoraproject.org/nn/fedora/f32/system-administrators-guide/infrastructure-services/OpenSSH/",
        "https://docs.fedoraproject.org/cs/fedora/f30/system-administrators-guide/infrastructure-services/OpenSSH/",
        "https://manpages.debian.org/bookworm/libc-bin/getent.1.en.html",
    }
    assert not retired & urls


def test_repository_internal_links_are_valid():
    assert check_links.check_internal() == []

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
    assert check_links.classify_status("https://example.test", 418).outcome == "warning"
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


# --- Regression: phạm vi quét và link thoát khỏi repo ---


def test_archive_page_is_inside_internal_link_scope():
    """archive.html nằm trong sitemap và chứa ~50 internal link.

    Trước đây _html_files() bỏ sót trang này nên link hỏng trong archive.html
    vẫn cho gate xanh.
    """
    scanned = {Path(p).name for p in check_links._html_files()}
    assert "archive.html" in scanned
    assert {"index.html", "learning-dashboard.html", "learning-paths.html"} <= scanned


def test_escapes_root_flags_paths_outside_repo():
    assert check_links.escapes_root("../../etc/hostname") is True
    assert check_links.escapes_root("..") is True
    assert check_links.escapes_root("/etc/hostname") is True
    assert check_links.escapes_root("posts/post-001-static-ip.html") is False
    assert check_links.escapes_root("index.html") is False
    assert check_links.escapes_root("assets/style.css") is False


def test_local_target_still_resolves_escaping_link_for_reporting():
    resolved = check_links._local_target(
        "posts/post-001-static-ip.html", "../../../../etc/hostname", "linux.no.id.vn"
    )
    assert resolved is not None
    target, _ = resolved
    assert check_links.escapes_root(target)


def test_internal_check_reports_link_escaping_repo(monkeypatch):
    """Link trỏ ra ngoài cây website phải là lỗi cứng.

    Nếu không chặn, os.path.isfile() có thể trúng một file tình cờ tồn tại trên máy
    build và làm gate xanh giả, trong khi production trả 404.
    """
    ref = check_links.LinkRef("posts/post-001-static-ip.html", "../../../../etc/hostname")
    monkeypatch.setattr(check_links, "collect_links", lambda: ([ref], set()))
    monkeypatch.setattr(check_links, "_site_host", lambda: "linux.no.id.vn")

    errors = check_links.check_internal()

    assert len(errors) == 1
    assert "thoát khỏi thư mục repo" in errors[0]


def test_internal_check_accepts_normal_relative_link(monkeypatch):
    ref = check_links.LinkRef("posts/post-001-static-ip.html", "../assets/style.css")
    monkeypatch.setattr(check_links, "collect_links", lambda: ([ref], set()))
    monkeypatch.setattr(check_links, "_site_host", lambda: "linux.no.id.vn")

    assert check_links.check_internal() == []


# --- Phạm vi chặn: link mới vs link đã có sẵn ---

import subprocess  # noqa: E402
import sys as _sys  # noqa: E402
from pathlib import Path as _Path  # noqa: E402

_ROOT = _Path(__file__).resolve().parents[1]


def _run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def _seed_repo(tmp_path):
    """Kho git tối thiểu có đúng bộ file mà check_links quét."""
    repo = tmp_path / "repo"
    (repo / "posts").mkdir(parents=True)
    for name in ("index.html", "archive.html", "learning-dashboard.html", "learning-paths.html"):
        (repo / name).write_text("<html><body></body></html>", encoding="utf-8")
    (repo / "posts" / "post-001-a.html").write_text(
        '<html><body><a href="https://cu.test/trang">cũ</a></body></html>', encoding="utf-8"
    )
    (repo / "site.json").write_text('{"url": "https://linux.no.id.vn/"}', encoding="utf-8")
    _run(["git", "init", "-q"], repo)
    _run(["git", "add", "-A"], repo)
    _run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base"], repo)
    return repo


def test_baseline_chi_gom_url_da_co_o_ref(tmp_path, monkeypatch):
    """baseline_external_urls phải đi qua đúng parser thật, không phải regex xấp xỉ."""
    repo = _seed_repo(tmp_path)
    base = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()

    (repo / "posts" / "post-002-b.html").write_text(
        '<html><body><a href="https://moi.test/trang">mới</a></body></html>', encoding="utf-8"
    )
    _run(["git", "add", "-A"], repo)
    _run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "them"], repo)

    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    monkeypatch.setattr(cl, "ROOT", str(repo))
    monkeypatch.setattr(cl, "POSTS_GLOB", str(repo / "posts" / "post-*.html"))
    monkeypatch.setattr(cl, "_site_host", lambda: "linux.no.id.vn")

    baseline = cl.baseline_external_urls(base)
    current = cl._external_urls_under(str(repo))

    assert "https://cu.test/trang" in baseline
    assert "https://moi.test/trang" not in baseline, "URL mới không được coi là có sẵn"
    assert current - baseline == {"https://moi.test/trang"}


def test_link_da_co_san_khong_chan_pr(tmp_path, monkeypatch, capsys):
    """Ca đã xảy ra thật ở #063: URL WireGuard có sẵn trên main bỗng 404.

    Nó chặn bài hằng ngày, agent đi 'sửa' hai bài cũ và làm hỏng một nguồn đang
    tốt. Link kế thừa phải được báo là nợ bảo trì, không chặn PR.
    """
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    chet = cl.ExternalResult("https://cu.test/trang", 404, "hard", "HTTP 404")
    monkeypatch.setattr(cl, "check_external", lambda max_workers=8: ([chet], []))
    monkeypatch.setattr(cl, "baseline_external_urls", lambda ref: {"https://cu.test/trang"})

    code = cl.main(["--external", "--baseline", "deadbeef"])
    out = capsys.readouterr()

    assert code == 0, "link kế thừa không được chặn PR"
    assert "nợ bảo trì" in out.out
    assert "cu.test" in out.out


def test_link_moi_van_chan_pr(tmp_path, monkeypatch, capsys):
    """Nới phạm vi không được làm mất khả năng chặn link mới — đó là hợp đồng PR #125."""
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    chet = cl.ExternalResult("https://moi.test/khong-co-that", 404, "hard", "HTTP 404")
    monkeypatch.setattr(cl, "check_external", lambda max_workers=8: ([chet], []))
    monkeypatch.setattr(cl, "baseline_external_urls", lambda ref: {"https://cu.test/trang"})

    code = cl.main(["--external", "--baseline", "deadbeef"])
    err = capsys.readouterr().err

    assert code == 1
    assert "link mới do nhánh này đưa vào" in err
    assert "moi.test" in err


def test_khong_co_baseline_thi_moi_link_chet_deu_chan(monkeypatch, capsys):
    """Chế độ cho push:main và lịch định kỳ — siết chặt như cũ."""
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    chet = cl.ExternalResult("https://cu.test/trang", 404, "hard", "HTTP 404")
    monkeypatch.setattr(cl, "check_external", lambda max_workers=8: ([chet], []))

    code = cl.main(["--external"])
    assert code == 1
    assert "link lỗi chắc chắn" in capsys.readouterr().err

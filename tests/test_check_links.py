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


def test_external_status_classification_only_marks_2xx_as_ok():
    assert check_links.classify_status("https://example.test", 200).outcome == "ok"
    assert check_links.classify_status("https://example.test", 204).outcome == "ok"
    assert check_links.classify_status("https://example.test", 301).outcome == "warning"
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

import pytest  # noqa: E402

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


def _dat_kho(tmp_path, monkeypatch):
    """Kho tạm + module check_links đã trỏ vào nó. Trả về (repo, module, base_sha)."""
    repo = _seed_repo(tmp_path)
    base = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()

    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    monkeypatch.setattr(cl, "ROOT", str(repo))
    monkeypatch.setattr(cl, "_site_host", lambda: "linux.no.id.vn")
    return repo, cl, base


def _commit(repo, message):
    _run(["git", "add", "-A"], repo)
    _run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", message], repo)


def test_baseline_chi_gom_url_da_co_o_ref(tmp_path, monkeypatch):
    """baseline_external_refs phải đi qua đúng parser thật, không phải regex xấp xỉ."""
    repo, cl, base = _dat_kho(tmp_path, monkeypatch)

    (repo / "posts" / "post-002-b.html").write_text(
        '<html><body><a href="https://moi.test/trang">mới</a></body></html>', encoding="utf-8"
    )
    _commit(repo, "them")

    baseline = cl.baseline_external_refs(base)
    current = cl._external_refs_under(str(repo))

    assert ("posts/post-001-a.html", "https://cu.test/trang") in baseline
    assert not any(url == "https://moi.test/trang" for _, url in baseline), (
        "URL mới không được coi là có sẵn"
    )
    assert current - baseline == {("posts/post-002-b.html", "https://moi.test/trang")}


def test_chep_url_chet_sang_bai_moi_van_la_moi(tmp_path, monkeypatch):
    """Lỗ thật của cách đếm theo URL: chép nguồn chết từ bài cũ sang bài mới.

    Nếu chỉ so tập URL thì URL đó "đã có trên main" nên không chặn — trong khi
    bài hôm nay đang thật sự trích một nguồn chết. So theo cặp (file, url) thì
    cặp mới, nên vẫn chặn. Đây là lý do duy nhất để theo dõi theo cặp.
    """
    repo, cl, base = _dat_kho(tmp_path, monkeypatch)

    (repo / "posts" / "post-002-b.html").write_text(
        '<html><body><a href="https://cu.test/trang">chép lại</a></body></html>',
        encoding="utf-8",
    )
    _commit(repo, "chep")

    existing = cl.baseline_external_refs(base)
    current = cl._external_refs_under(str(repo))
    moi = {url for rel, url in current if (rel, url) not in existing}

    assert moi == {"https://cu.test/trang"}


def test_dung_lai_trang_generated_khong_sinh_cap_moi(tmp_path, monkeypatch):
    """Dựng lại index/archive với nội dung y hệt không được đẻ ra cặp mới.

    Nếu có, mọi PR bài hằng ngày sẽ bị coi là đưa vào link mới và gate mất nghĩa.
    """
    repo, cl, base = _dat_kho(tmp_path, monkeypatch)

    for name in ("index.html", "archive.html"):
        path = repo / name
        path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "posts" / "post-002-b.html").write_text(
        "<html><body><p>không có link ngoài</p></body></html>", encoding="utf-8"
    )
    _commit(repo, "dung lai")

    existing = cl.baseline_external_refs(base)
    current = cl._external_refs_under(str(repo))

    assert current == existing


def test_ref_khong_ton_tai_bao_loi_ro_rang(tmp_path, monkeypatch):
    """Checkout nông làm base SHA vắng mặt. Thông điệp phải chỉ đúng cách sửa."""
    _repo, cl, _base = _dat_kho(tmp_path, monkeypatch)

    with pytest.raises(cl.BaselineError) as exc:
        cl.baseline_external_refs("0" * 40)

    message = str(exc.value)
    assert "fetch-depth: 0" in message
    assert "KHÔNG gỡ --baseline" in message


def test_baseline_hong_thi_fail_closed(monkeypatch, capsys):
    """Không dựng được baseline thì phải đỏ, không được coi mọi link là kế thừa."""
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    chet = cl.ExternalResult("https://cu.test/trang", 404, "hard", "HTTP 404")
    monkeypatch.setattr(cl, "check_external", lambda max_workers=8, cache=None, bypass=frozenset(): ([chet], []))

    def no(_ref):
        raise cl.BaselineError("không dựng được cây baseline từ ref 'x'")

    monkeypatch.setattr(cl, "baseline_external_refs", no)

    code = cl.main(["--external", "--baseline", "deadbeef"])
    assert code == 1
    assert "không dựng được cây baseline" in capsys.readouterr().err


def test_link_da_co_san_khong_chan_pr(tmp_path, monkeypatch, capsys):
    """Ca đã xảy ra thật ở #063: URL WireGuard có sẵn trên main bỗng 404.

    Nó chặn bài hằng ngày, agent đi 'sửa' hai bài cũ và làm hỏng một nguồn đang
    tốt. Link kế thừa phải được báo là nợ bảo trì, không chặn PR.
    """
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    chet = cl.ExternalResult("https://cu.test/trang", 404, "hard", "HTTP 404")
    monkeypatch.setattr(cl, "check_external", lambda max_workers=8, cache=None, bypass=frozenset(): ([chet], []))
    monkeypatch.setattr(
        cl, "baseline_external_refs",
        lambda ref: {("posts/post-001-a.html", "https://cu.test/trang")},
    )
    monkeypatch.setattr(
        cl, "_external_refs_under",
        lambda root: {("posts/post-001-a.html", "https://cu.test/trang")},
    )

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
    monkeypatch.setattr(cl, "check_external", lambda max_workers=8, cache=None, bypass=frozenset(): ([chet], []))
    monkeypatch.setattr(
        cl, "baseline_external_refs",
        lambda ref: {("posts/post-001-a.html", "https://cu.test/trang")},
    )
    monkeypatch.setattr(
        cl, "_external_refs_under",
        lambda root: {
            ("posts/post-001-a.html", "https://cu.test/trang"),
            ("posts/post-002-b.html", "https://moi.test/khong-co-that"),
        },
    )

    code = cl.main(["--external", "--baseline", "deadbeef"])
    err = capsys.readouterr().err

    assert code == 1
    assert "link mới chưa xác minh được HTTP 2xx" in err
    assert "moi.test" in err


@pytest.mark.parametrize(
    ("status", "detail"),
    [
        (301, "HTTP 301 (redirect unresolved)"),
        (403, "HTTP 403 (auth/bot-block)"),
        (503, "HTTP 503 (transient)"),
        (None, "network/timeout sau 3 lần"),
    ],
)
def test_link_moi_chua_nhan_2xx_phai_chan_pr(
    monkeypatch, capsys, status: int | None, detail: str
):
    """Nguồn mới phải nhận 2xx thật; warning mạng không đủ để qua PR gate."""
    result = check_links.ExternalResult(
        "https://moi.test/nguon",
        status,
        "warning",
        detail,
    )
    monkeypatch.setattr(check_links, "check_external", lambda max_workers=8, cache=None, bypass=frozenset(): ([], [result]))
    monkeypatch.setattr(check_links, "baseline_external_refs", lambda ref: set())
    monkeypatch.setattr(
        check_links,
        "_external_refs_under",
        lambda root: {("posts/post-002-b.html", "https://moi.test/nguon")},
    )

    code = check_links.main(["--external", "--baseline", "deadbeef"])
    captured = capsys.readouterr()

    assert code == 1
    assert "chưa xác minh được HTTP 2xx" in captured.err
    assert "moi.test" in captured.err


def test_warning_cua_link_ke_thua_khong_chan_pr(monkeypatch, capsys):
    """Lỗi mạng của URL đã có vẫn là cảnh báo để PR hằng ngày không flaky."""
    result = check_links.ExternalResult(
        "https://cu.test/nguon",
        None,
        "warning",
        "network/timeout sau 3 lần",
    )
    pair = ("posts/post-001-a.html", "https://cu.test/nguon")
    monkeypatch.setattr(check_links, "check_external", lambda max_workers=8, cache=None, bypass=frozenset(): ([], [result]))
    monkeypatch.setattr(check_links, "baseline_external_refs", lambda ref: {pair})
    monkeypatch.setattr(check_links, "_external_refs_under", lambda root: {pair})

    code = check_links.main(["--external", "--baseline", "deadbeef"])
    captured = capsys.readouterr()

    assert code == 0
    assert "⚠ External" in captured.out
    assert captured.err == ""


def test_khong_co_baseline_thi_moi_link_chet_deu_chan(monkeypatch, capsys):
    """Chế độ cho push:main và lịch định kỳ — siết chặt như cũ."""
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    chet = cl.ExternalResult("https://cu.test/trang", 404, "hard", "HTTP 404")
    monkeypatch.setattr(cl, "check_external", lambda max_workers=8, cache=None, bypass=frozenset(): ([chet], []))

    code = cl.main(["--external"])
    assert code == 1
    assert "link lỗi chắc chắn" in capsys.readouterr().err


# --- cache kết quả 2xx ------------------------------------------------------


def _cache(tmp_path, **kw):
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl
    return cl, cl.LinkCache(str(tmp_path / "lc.json"), **kw)


def test_chi_cache_verdict_ok(tmp_path, monkeypatch):
    """Cache một lần hỏng là biến sự cố nhất thời thành vĩnh viễn."""
    cl, cache = _cache(tmp_path)
    ket_qua = {
        "https://song.test/a": cl.ExternalResult("https://song.test/a", 200, "ok", "HTTP 200"),
        "https://chet.test/b": cl.ExternalResult("https://chet.test/b", 404, "hard", "HTTP 404"),
        "https://ban.test/c": cl.ExternalResult("https://ban.test/c", 429, "warning", "HTTP 429"),
    }
    monkeypatch.setattr(cl, "collect_external_urls", lambda: list(ket_qua))
    monkeypatch.setattr(cl, "check_external_url", lambda url, **_: ket_qua[url])

    cl.check_external(cache=cache)

    assert set(cache.entries) == {"https://song.test/a"}


def test_url_moi_khong_duoc_lay_tu_cache(tmp_path, monkeypatch):
    """Đây là lỗ mà PR #134 đã bịt; cache không được mở lại nó.

    Một URL đã 2xx từ lâu (nên nằm trong cache) bị CHÉP sang bài mới. Nếu lấy
    verdict cũ từ cache thì nguồn của bài hôm nay chưa hề được xác minh.
    """
    cl, cache = _cache(tmp_path)
    url = "https://cu.test/trang"
    cache.remember(url, __import__("time").time())

    da_hoi = []
    monkeypatch.setattr(cl, "collect_external_urls", lambda: [url])
    monkeypatch.setattr(
        cl, "check_external_url",
        lambda u, **_: (da_hoi.append(u), cl.ExternalResult(u, 200, "ok", "HTTP 200"))[1],
    )

    cl.check_external(cache=cache, bypass=frozenset({url}))

    assert da_hoi == [url], "URL mới phải được hỏi lại thật, không lấy từ cache"


def test_verdict_qua_han_bi_hoi_lai(tmp_path, monkeypatch):
    """Không TTL thì link chết sau khi vào cache sẽ không bao giờ lộ ra nữa."""
    import time as _t

    cl, cache = _cache(tmp_path, ttl_days=7)
    url = "https://cu.test/a"
    cache.entries[url] = _t.time() - 8 * 86400

    da_hoi = []
    monkeypatch.setattr(cl, "collect_external_urls", lambda: [url])
    monkeypatch.setattr(
        cl, "check_external_url",
        lambda u, **_: (da_hoi.append(u), cl.ExternalResult(u, 200, "ok", "HTTP 200"))[1],
    )

    cl.check_external(cache=cache)
    assert da_hoi == [url]


def test_khong_co_cache_thi_hoi_moi_url(tmp_path, monkeypatch):
    """Chế độ push:main và lịch định kỳ — không truyền --cache, siết như cũ."""
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    urls = [f"https://x.test/{i}" for i in range(5)]
    da_hoi = []
    monkeypatch.setattr(cl, "collect_external_urls", lambda: urls)
    monkeypatch.setattr(
        cl, "check_external_url",
        lambda u, **_: (da_hoi.append(u), cl.ExternalResult(u, 200, "ok", "HTTP 200"))[1],
    )

    cl.check_external(cache=None)
    assert sorted(da_hoi) == sorted(urls)


def test_cache_hong_khong_lam_do_ci(tmp_path):
    """Mất cache chỉ tốn thời gian; dừng vì nó là biến tối ưu thành điểm hỏng."""
    _sys.path.insert(0, str(_ROOT / "tools"))
    import check_links as cl

    hong = tmp_path / "lc.json"
    hong.write_text("{khong-phai-json", encoding="utf-8")

    cache = cl.LinkCache(str(hong))
    assert cache.entries == {}


def test_cache_ghi_roi_doc_lai_duoc(tmp_path):
    import time as _t

    cl, cache = _cache(tmp_path)
    cache.remember("https://a.test/x", _t.time())
    cache.save()

    lai = cl.LinkCache(str(tmp_path / "lc.json"))
    assert lai.fresh("https://a.test/x", _t.time())
    assert not lai.fresh("https://chua-biet.test/y", _t.time())


def test_ttl_0_van_hoi_moi_url_nhung_van_ghi_cache(tmp_path, monkeypatch):
    """Hợp đồng của chế độ "chỉ ghi" mà push:main dùng — xem ci.yml.

    Cache của GitHub Actions bị khoá theo ref: một run chỉ đọc được cache do
    CHÍNH nhánh nó hoặc nhánh mặc định tạo ra. Nếu chỉ `pull_request` mới ghi
    cache thì cache đó nằm trong phạm vi của riêng PR ấy, PR hôm sau không với
    tới — mà kho này mỗi ngày một PR mới, chạy CI đúng một lần rồi merge. Tức
    là tỉ lệ trúng thực tế ~0.

    Nên main cũng ghi cache, nhưng với `--cache-ttl-days 0`: không verdict nào
    còn hạn, main vẫn hỏi lại đủ 100% URL (siết y như trước), chỉ có điều nó
    để lại cache trên nhánh mặc định cho các PR sau dùng.

    Test này khoá cả hai vế. Bỏ vế đầu là main lặng lẽ thôi kiểm tra thật; bỏ
    vế sau là cache không bao giờ được gieo và cả PR #145 thành vô nghĩa.
    """
    import time as _t

    cl, cache = _cache(tmp_path, ttl_days=0)
    url = "https://song.test/a"
    cache.remember(url, _t.time())  # vừa cache xong, mới tinh

    da_hoi = []
    monkeypatch.setattr(cl, "collect_external_urls", lambda: [url])

    def _ghi_nhan(u, **_):
        da_hoi.append(u)
        return cl.ExternalResult(u, 200, "ok", "HTTP 200")

    monkeypatch.setattr(cl, "check_external_url", _ghi_nhan)

    cl.check_external(cache=cache)

    assert da_hoi == [url], "TTL 0 phải hỏi lại mọi URL, kể cả vừa cache xong"
    assert cache.hits == 0
    assert url in cache.entries, "TTL 0 vẫn phải GHI, nếu không thì không gieo được cache"

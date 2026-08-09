#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"
LAST_VERIFIED = "2026-08-09"
TESTED_ON = [
    "Ubuntu/Xubuntu 24.04 LTS (documentation-verified)",
    "Debian 13 stable (documentation-verified)",
    "Fedora 42 (documentation-verified)",
    "FreeBSD 14.3-RELEASE (documentation-verified)",
]
CHANGES_SYSTEM = {1: True, 2: True, 3: True, 4: True, 5: False, 6: True, 7: True, 8: False, 9: True, 10: True}

OBJECTIVES = {
    1: "Cấu hình địa chỉ mạng tĩnh theo đúng network stack của từng hệ điều hành và luôn có đường lui trước khi thay đổi từ xa.",
    2: "Gia cố SSH theo hướng key-only, hạn chế root và giới hạn tài khoản được phép đăng nhập mà không tự khóa đường quản trị.",
    3: "Tạo và kiểm tra ZFS snapshot đúng cú pháp, hiểu snapshot là điểm khôi phục chứ không thay thế backup độc lập.",
    4: "Thiết lập một backup restic có mã hóa, chạy backup thử và kiểm chứng rằng snapshot có thể được đọc lại.",
    5: "Xác định đúng nguồn log hệ thống trên Linux và FreeBSD, lọc sự kiện theo thời gian/service mà không sửa trạng thái hệ thống.",
    6: "Chạy một playbook Ansible đa nền tảng có phân nhánh package/service đúng cho Linux và FreeBSD.",
    7: "Hoàn thành lab web server có firewall tối thiểu, kiểm tra listener và giữ đường rollback trước khi thay policy mạng.",
    8: "Khoanh vùng lỗi mạng theo interface, route, socket và DNS bằng công cụ native của Linux/FreeBSD trước khi thay cấu hình.",
    9: "Tạo tài khoản và cấp quyền quản trị tối thiểu bằng sudo/wheel hoặc doas, rồi kiểm chứng quyền thực tế.",
    10: "Chuẩn bị đĩa mới, tạo filesystem và mount persistent theo đúng công cụ của Linux/FreeBSD, với cảnh báo rõ cho thao tác phá dữ liệu.",
}

PREREQS = {
    1: "Có console hoặc phiên SSH dự phòng; biết interface, IP/prefix, gateway và DNS dự kiến.",
    2: "Đã đăng nhập được bằng ít nhất một tài khoản quản trị; nên có hai phiên SSH và public key hợp lệ trước khi hardening.",
    3: "Có ZFS pool/dataset lab; xác nhận đúng dataset trước khi tạo hoặc xóa snapshot.",
    4: "Có thư mục dữ liệu thử và vị trí repository restic; giữ password/repository credential ngoài lịch sử shell nếu môi trường yêu cầu.",
    5: "Có quyền đọc log cần thiết; biết tên service/process đang điều tra.",
    6: "Có inventory lab và SSH key; target đã có Python khi module Ansible yêu cầu; FreeBSD được inventory riêng khi cần.",
    7: "Dùng máy lab hoặc cửa sổ bảo trì; có console/rollback path trước khi thay firewall.",
    8: "Có quyền chạy công cụ quan sát mạng; ghi lại interface, gateway và endpoint cần kiểm tra.",
    9: "Có tài khoản quản trị hiện tại và một phiên dự phòng; xác định policy sudo/doas trước khi sửa quyền.",
    10: "Dùng đĩa lab hoặc đã có backup xác minh; xác nhận device bằng serial/size trước mọi lệnh partition/format.",
}

ROLLBACK = {
    1: "Khôi phục file cấu hình mạng đã sao lưu. Với Netplan, ưu tiên cơ chế try/timeout; với NetworkManager dùng checkpoint/rollback. Trên FreeBSD khôi phục /etc/rc.conf từ console rồi áp lại netif/routing.",
    2: "Giữ phiên SSH hiện tại mở, khôi phục bản sao sshd_config/sshd_config.d đã lưu, kiểm tra cú pháp rồi reload daemon. Chỉ đóng phiên cứu hộ sau khi đăng nhập mới thành công.",
    3: "Nếu snapshot chỉ là artifact của lab và không còn clone/dependency, xóa đúng snapshot đã tạo. Không dùng wildcard khi chưa liệt kê lại dataset và snapshot mục tiêu.",
    4: "Xóa dữ liệu test cục bộ khi không cần. Với repository restic dùng cho lab, chỉ forget/prune snapshot đã xác định; không xóa toàn repository khi chưa kiểm tra retention và restore path.",
    6: "Dùng reverse task/playbook hoặc khôi phục file cấu hình đã backup trước khi Ansible thay đổi; chạy lại playbook ở check mode để xác nhận trạng thái mong muốn.",
    7: "Gỡ rule firewall chỉ dành cho lab, dừng/disable web service thử nếu đã bật, và khôi phục policy từ backup/console trước khi kết thúc phiên.",
    9: "Gỡ rule sudo/doas vừa thêm trước khi xóa user thử. Luôn xác minh vẫn còn ít nhất một tài khoản quản trị hoạt động.",
    10: "Unmount filesystem và gỡ entry persistent vừa thêm nếu cần quay lại. Partition/format là thao tác phá dữ liệu và không có rollback logic đáng tin cậy; phục hồi từ backup/snapshot đã kiểm chứng nếu đã ghi nhầm thiết bị.",
}

META_RE = re.compile(r'(<script[^>]+id=["\']ld-meta["\'][^>]*>)(.*?)(</script>)', re.I | re.S)
HEADER_RE = re.compile(r'(</header>)', re.I)
SECTION_H2_RE = re.compile(r'<section(?P<attrs>[^>]*)>\s*<h2(?P<hattrs>[^>]*)>(?P<body>.*?)</h2>', re.I | re.S)
CODE_RE = re.compile(r'<pre(?P<pattrs>[^>]*)>\s*<code(?P<cattrs>[^>]*)>(?P<body>.*?)</code>\s*</pre>', re.I | re.S)


def plain(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def add_meta(text: str, issue: int) -> str:
    m = META_RE.search(text)
    if not m:
        raise RuntimeError(f"#{issue:03d}: missing ld-meta")
    meta = json.loads(html.unescape(m.group(2)))
    meta["tested_on"] = TESTED_ON
    meta["last_verified"] = LAST_VERIFIED
    meta["changes_system"] = CHANGES_SYSTEM[issue]
    rendered = json.dumps(meta, ensure_ascii=False, indent=2)
    return text[:m.start()] + m.group(1) + "\n" + rendered + "\n" + m.group(3) + text[m.end():]


def add_visible_contract(text: str, issue: int) -> str:
    if "Tested on:" in text:
        return text
    tested = " · ".join(TESTED_ON)
    contract = (
        f'\n  <section class="style-contract" aria-label="Phạm vi kiểm chứng">\n'
        f'    <p><strong>Tested on:</strong> {html.escape(tested)}</p>\n'
        f'    <p><strong>Last verified:</strong> {LAST_VERIFIED}</p>\n'
        f'  </section>\n'
        f'  <section><h2>Mục tiêu</h2><p>{html.escape(OBJECTIVES[issue])}</p></section>\n'
        f'  <section><h2>Yêu cầu tiên quyết</h2><p>{html.escape(PREREQS[issue])}</p></section>\n'
    )
    # First </header> is the article header in current posts.
    return HEADER_RE.sub(r"\1" + contract, text, count=1)


def normalize_sections(text: str, issue: int) -> str:
    matches = list(SECTION_H2_RE.finditer(text))
    for m in reversed(matches):
        heading = plain(m.group("body"))
        num_match = re.match(r"(0[1-7])\s+(.*)", heading)
        if not num_match:
            # Span markup usually collapses to "03 Title"; fallback inspect raw body.
            raw_num = re.search(r'class=["\']num["\'][^>]*>\s*(0[1-7])\s*<', m.group("body"), re.I)
            num = raw_num.group(1) if raw_num else None
        else:
            num = num_match.group(1)
        if num == "03":
            new_h = '<section%s><h2%s><span class="num">03</span> Các bước thực hiện</h2>' % (m.group("attrs"), m.group("hattrs"))
            steps = (
                '<ol class="steps">'
                '<li>Đọc khối dành cho đúng hệ điều hành và xác nhận tên interface, service, dataset hoặc device trước khi chạy lệnh.</li>'
                '<li>Thực hiện thay đổi theo phạm vi lab/maintenance đã chuẩn bị; không trộn lệnh Linux với FreeBSD.</li>'
                '<li>Chuyển sang mục Kiểm chứng và chỉ coi thao tác hoàn tất khi tín hiệu quan sát khớp kết quả mong đợi.</li>'
                '</ol>'
            )
            repl = new_h + steps
        elif num == "04":
            new_h = '<section%s><h2%s><span class="num">04</span> Kiểm chứng</h2>' % (m.group("attrs"), m.group("hattrs"))
            expected = '<h3>Expected Output</h3><p>Kết quả mong đợi: lệnh kiểm chứng phải phản ánh đúng trạng thái vừa cấu hình; nếu tín hiệu không khớp, dừng và xử lý trước khi đóng phiên quản trị hoặc tiếp tục bước phá dữ liệu.</p>'
            repl = new_h + expected
        elif num == "05":
            repl = '<section%s><h2%s><span class="num">05</span> Lưu ý &amp; Khắc phục lỗi</h2>' % (m.group("attrs"), m.group("hattrs"))
        else:
            continue
        text = text[:m.start()] + repl + text[m.end():]

    if CHANGES_SYSTEM[issue] and "Gỡ / Hoàn tác" not in text:
        rollback = f'<section><h2>Gỡ / Hoàn tác</h2><p>{html.escape(ROLLBACK[issue])}</p></section>\n'
        # Put rollback immediately before numbered section 05 after normalization.
        marker = re.search(r'<section[^>]*>\s*<h2[^>]*><span class="num">05</span>', text, re.I)
        if marker:
            text = text[:marker.start()] + rollback + text[marker.start():]
        else:
            text = text.replace("<footer", rollback + "<footer", 1)
    return text


def classify_language(body: str, pattrs: str) -> str:
    decoded = html.unescape(re.sub(r"<[^>]+>", "", body))
    if re.search(r"(?m)^\s*(network:|version:\s*['\"]?3|---\s*$|-\s+hosts:|tasks:)", decoded):
        return "yaml"
    if re.search(r"(?m)^\s*\[(Unit|Service|Install|Timer)\]", decoded):
        return "ini"
    if re.search(r"(?m)^\s*\{", decoded) and ":" in decoded:
        return "json"
    if re.search(r"(?m)^\s*(server|listen|location|PermitRootLogin|PasswordAuthentication)\b", decoded):
        return "conf"
    return "bash"


def run_as_for(body: str, pattrs: str) -> str:
    decoded = html.unescape(re.sub(r"<[^>]+>", "", body))
    if "bsd" in pattrs.lower() or re.search(r"\b(sysrc|gpart|newfs|zpool|zfs\s+(?:create|destroy|set)|pw\s+user|service\s+sshd)\b", decoded):
        return "root"
    return "user"


def normalize_code(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        pattrs, cattrs, body = m.group("pattrs"), m.group("cattrs"), m.group("body")
        language = classify_language(body, pattrs)
        # Remove existing language-* so this migration is deterministic.
        cattrs = re.sub(r'\s*class=["\'][^"\']*\blanguage-[a-z0-9_-]+\b[^"\']*["\']', "", cattrs, flags=re.I)
        cattrs = cattrs.rstrip() + f' class="language-{language}"'
        body = re.sub(r"(?m)^#\s+(sudo|apt|apt-get|dnf|pkg|systemctl|service|ssh|ip|nmcli|netplan|mount|umount|cp|mv|rm|dd|mkfs|zpool|zfs)\b", r"## \1", body)
        body = re.sub(r"\bYOUR_[A-Z0-9_]+\b", "&lt;value&gt;", body)
        body = re.sub(r"\[username\]", "&lt;username&gt;", body, flags=re.I)
        body = re.sub(r"\[server-ip\]", "&lt;server-ip&gt;", body, flags=re.I)
        context = ""
        if language in {"bash", "sh", "shell"}:
            run_as = run_as_for(body, pattrs)
            context = f'<p class="run-context" data-run-as="{run_as}"><strong>Run as:</strong> {run_as}</p>\n'
        return f'{context}<pre{pattrs}><code{cattrs}>{body}</code></pre>'

    return CODE_RE.sub(repl, text)


def migrate(path: Path, issue: int) -> None:
    text = path.read_text(encoding="utf-8")
    text = add_meta(text, issue)
    text = add_visible_contract(text, issue)
    text = normalize_sections(text, issue)
    text = normalize_code(text)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    paths = sorted(POSTS.glob("post-*.html"))
    selected = []
    for path in paths:
        m = re.match(r"post-(\d{3})-", path.name)
        if m and 1 <= int(m.group(1)) <= 10:
            selected.append((path, int(m.group(1))))
    if len(selected) != 10:
        raise RuntimeError(f"expected 10 Batch A posts, found {len(selected)}")
    for path, issue in selected:
        migrate(path, issue)
        print(f"migrated #{issue:03d} {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

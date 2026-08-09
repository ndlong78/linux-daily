#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"
LAST_VERIFIED = "2026-08-09"
TESTED = [
    "Ubuntu/Xubuntu 24.04 LTS (documentation-verified)",
    "Debian 13 stable (documentation-verified)",
    "Fedora 42 (documentation-verified)",
    "FreeBSD 14.3-RELEASE (documentation-verified)",
]
DISPLAY_TESTED = "Ubuntu/Xubuntu 24.04 LTS · Debian 13 stable · Fedora 42 · FreeBSD 14.3-RELEASE"

PLAN = {
    11: {
        "file": "post-011-tmux.html",
        "objective": "Dùng tmux để giữ phiên làm việc sống khi SSH bị gián đoạn, biết detach/attach và hiểu giới hạn của tmux so với service manager.",
        "prereq": "Có shell trên máy lab và quyền cài gói; nếu thao tác qua SSH, mở một phiên riêng để thử detach/attach mà không ảnh hưởng công việc thật.",
        "steps": [
            "Cài tmux bằng package manager đúng hệ điều hành và kiểm phiên bản bằng <code>tmux -V</code>.",
            "Tạo session có tên rõ ràng bằng <code>tmux new -As work</code>, sau đó chạy một job quan sát được trong session.",
            "Detach bằng prefix <code>Ctrl-b</code> rồi <code>d</code>, kiểm session còn tồn tại bằng <code>tmux ls</code>.",
            "Đăng nhập/attach lại session và xác nhận job vẫn tiếp tục; dọn session test khi hoàn tất.",
        ],
        "expected": [
            "<code>tmux ls</code> liệt kê session sau khi client detach hoặc SSH được nối lại.",
            "Attach lại hiển thị đúng shell/job đang chạy trước đó, không tạo nhầm session mới.",
            "Sau <code>tmux kill-session</code>, session test không còn trong danh sách.",
        ],
        "cleanup": "Gỡ các session test bằng <code>tmux kill-session -t &lt;name&gt;</code>. Nếu chỉ cài tmux để thử, có thể gỡ package bằng APT/DNF/pkg; thao tác này không thay thế cleanup của các tiến trình chạy bên trong tmux.",
    },
    12: {
        "file": "post-012-lap-lich-cron-timers.html",
        "objective": "Lập lịch một tác vụ định kỳ, chọn đúng giữa cron và systemd timer trên Linux, đồng thời dùng cron/periodic theo mô hình của FreeBSD.",
        "prereq": "Có một lệnh/script idempotent để chạy thử và biết tài khoản nào phải sở hữu job; dùng lịch ngắn trong lab trước khi áp dụng lịch production.",
        "steps": [
            "Chạy script thủ công và kiểm exit code trước khi đưa vào scheduler.",
            "Trên Linux, chọn cron cho lịch đơn giản hoặc systemd timer khi cần dependency, journal và missed-run semantics; FreeBSD không dùng systemd.",
            "Khai báo lịch với đường dẫn tuyệt đối, môi trường tối thiểu và user chạy rõ ràng.",
            "Kích hoạt scheduler rồi quan sát ít nhất một lần chạy thực tế qua log/output thay vì chỉ tin cấu hình đã lưu.",
        ],
        "expected": [
            "Scheduler hiển thị job/timer ở trạng thái đã nạp và thời điểm chạy kế tiếp hợp lý.",
            "Tác vụ tạo đúng output/log bằng đúng user, không phụ thuộc PATH của shell tương tác.",
            "Một lần chạy lỗi có dấu vết đủ để điều tra qua journal/syslog hoặc log riêng.",
        ],
        "cleanup": "Xóa cron entry hoặc disable/remove systemd timer vừa tạo; trên FreeBSD gỡ entry cron/periodic tương ứng. Chạy lại lệnh liệt kê scheduler để xác nhận không còn lịch test.",
    },
    13: {
        "file": "post-013-bash-script-vung.html",
        "objective": "Viết shell script phòng thủ với kiểm tra đầu vào, exit code rõ ràng và chế độ lỗi phù hợp để automation thất bại có kiểm soát.",
        "prereq": "Có Bash trên Linux; trên FreeBSD xác nhận <code>bash</code> đã được cài nếu script dùng Bash-specific syntax, vì <code>/bin/sh</code> của FreeBSD không phải Bash.",
        "steps": [
            "Chọn interpreter đúng và ghi shebang phù hợp thay vì giả định <code>/bin/sh</code> là Bash trên mọi hệ.",
            "Bật các guard phù hợp, validate argument/file trước khi thay đổi trạng thái và quote biến khi mở rộng.",
            "Tách thao tác kiểm tra khỏi thao tác ghi, trả exit code khác 0 khi điều kiện tiên quyết không đạt.",
            "Test cả happy path lẫn input sai/missing dependency và xác nhận script dừng ở điểm dự kiến.",
        ],
        "expected": [
            "Input hợp lệ cho exit code 0 và tạo đúng kết quả mong muốn.",
            "Input sai hoặc dependency thiếu cho exit code khác 0, thông báo lỗi có ngữ cảnh và không để lại thay đổi dở dang.",
            "Script chạy nhất quán trên những hệ đã khai báo interpreter, không dựa vào shell mặc định của user.",
        ],
        "cleanup": "Xóa file/script và dữ liệu test do bài tạo ra. Nếu script có thao tác thay đổi hệ thống, dùng rollback path của thao tác đó; đừng coi xóa script là đã hoàn tác trạng thái.",
    },
    14: {
        "file": "post-014-lab-backup-tu-dong.html",
        "objective": "Ghép backup, scheduler, retention và restore test thành một lab tự động hóa có thể chứng minh dữ liệu phục hồi được.",
        "prereq": "Dùng dữ liệu lab và repository backup riêng; có đủ dung lượng, credential tối thiểu và một thư mục restore tách khỏi nguồn.",
        "steps": [
            "Chạy backup thủ công lần đầu và ghi nhận repository/source trước khi tự động hóa.",
            "Đưa lệnh backup vào scheduler đúng nền tảng, truyền secret an toàn và không hard-code credential vào crontab/script world-readable.",
            "Thiết lập retention/prune theo chính sách lab và kiểm backup mới xuất hiện sau scheduler run.",
            "Restore một mẫu dữ liệu sang đường dẫn khác, so sánh nội dung/checksum rồi mới coi pipeline backup đạt.",
        ],
        "expected": [
            "Scheduler tạo snapshot/backup mới và log cho biết run thành công bằng đúng source/repository.",
            "Retention chỉ xóa bản nằm ngoài chính sách và không làm mất restore point cần giữ.",
            "Restore test đọc được dữ liệu và checksum/nội dung khớp nguồn đã backup.",
        ],
        "cleanup": "Disable scheduler test trước, sau đó xóa repository/restore directory lab nếu không còn cần. Không chạy prune/delete trên repository production chỉ để dọn lab.",
    },
    15: {
        "file": "post-015-wireguard-vpn.html",
        "objective": "Dựng một đường hầm WireGuard tối thiểu, phân biệt cấu hình peer với routing/firewall và kiểm hai chiều trước khi persist.",
        "prereq": "Có hai node lab hoặc namespace/VM, IP tunnel không trùng mạng hiện hữu và đường quản trị ngoài tunnel để rollback nếu route sai.",
        "steps": [
            "Cài WireGuard bằng package manager đúng hệ và tạo keypair với permission hạn chế.",
            "Khai báo interface/peer với địa chỉ tunnel và AllowedIPs tối thiểu cần thiết; không mở rộng route mặc định ngay trong lần thử đầu.",
            "Bring up tunnel bằng cơ chế native của hệ, kiểm handshake và route trước khi thêm firewall/NAT nếu bài cần.",
            "Kiểm traffic hai chiều và đường quản trị ngoài tunnel; chỉ bật autostart sau khi runtime test thành công.",
        ],
        "expected": [
            "<code>wg show</code> hiển thị peer, latest handshake sau khi có traffic và counter tăng.",
            "Route đến subnet tunnel đi qua đúng interface, không cướp default route ngoài ý muốn.",
            "Ping/traffic thử qua tunnel thành công và tắt tunnel vẫn giữ được đường quản trị ban đầu.",
        ],
        "cleanup": "Tắt interface WireGuard, disable autostart nếu đã bật và khôi phục route/firewall/NAT vừa thêm. Xóa private key lab nếu không tái sử dụng; không công bố private key trong ticket/log.",
    },
    16: {
        "file": "post-016-fail2ban.html",
        "objective": "Triển khai Fail2ban cho một dịch vụ có log thật, kiểm jail/filter/backend và chứng minh ban/unban mà không tự khóa IP quản trị.",
        "prereq": "Có log authentication của dịch vụ, một IP test tách khỏi IP quản trị và console/đường lui nếu firewall rule gây mất truy cập.",
        "steps": [
            "Cài Fail2ban, xác định đúng log backend/path của distro và không giả định journald tồn tại trên FreeBSD.",
            "Tạo jail override tối thiểu, đặt bantime/findtime/maxretry phù hợp lab và allowlist IP quản trị khi cần.",
            "Validate config rồi khởi động/reload service bằng systemd trên Linux hoặc rc.d trên FreeBSD.",
            "Tạo thất bại có kiểm soát từ IP test, quan sát jail ban rồi unban và xác nhận rule được gỡ sạch.",
        ],
        "expected": [
            "<code>fail2ban-client status</code> thấy jail đã enable và đọc đúng nguồn log.",
            "IP test xuất hiện trong banned list sau ngưỡng thử sai, trong khi IP quản trị không bị chặn.",
            "Sau unban/stop jail, rule firewall tương ứng được dọn và kết nối test hoạt động trở lại.",
        ],
        "cleanup": "Unban IP test, disable jail lab và gỡ file override nếu không dùng tiếp. Kiểm firewall sau khi stop Fail2ban để chắc không còn rule test treo.",
    },
    17: {
        "file": "post-017-mo-rong-dung-luong.html",
        "objective": "Mở rộng dung lượng đúng lớp từ block device/partition đến volume và filesystem, tránh nhầm 'disk đã lớn' với 'filesystem đã lớn'.",
        "prereq": "Có backup/snapshot đã kiểm chứng, biết stack storage thực tế (partition, LVM/ZFS/UFS, filesystem) và có console cho thay đổi boot/storage quan trọng.",
        "steps": [
            "Inventory từ dưới lên: disk/partition, volume layer và filesystem; ghi lại size hiện tại trước khi thay đổi.",
            "Mở rộng đúng lớp thấp nhất trước và reread partition/device nếu cần; không chạy công cụ filesystem lên nhầm block device.",
            "Mở rộng volume/filesystem bằng công cụ đúng loại và đúng OS; FreeBSD xử lý GEOM/UFS/ZFS theo stack riêng, không dùng LVM.",
            "Kiểm capacity mới, mount/read-write và log kernel; chỉ reboot nếu quy trình thực sự yêu cầu.",
        ],
        "expected": [
            "Mỗi lớp inventory phản ánh size mới theo đúng thứ tự, không còn khoảng trống ngoài ý muốn ở lớp dưới.",
            "Filesystem báo capacity tăng và dữ liệu cũ vẫn đọc được; không có lỗi I/O/filesystem trong log.",
            "Mountpoint/service dùng volume tiếp tục hoạt động sau thay đổi và sau reboot kiểm soát nếu có.",
        ],
        "cleanup": "Mở rộng storage thường không có rollback đơn giản. Nếu phát hiện sai trước khi ghi filesystem, dừng và khôi phục metadata theo backup/snapshot; nếu đã ghi nhầm thiết bị, ưu tiên quy trình recovery thay vì cố thu nhỏ tùy tiện.",
    },
    18: {
        "file": "post-018-rclone-cloud-sync.html",
        "objective": "Dùng rclone để copy/sync dữ liệu có kiểm soát, hiểu khác biệt copy và sync, và kiểm dữ liệu đích trước khi tự động hóa.",
        "prereq": "Dùng remote/bucket lab và credential giới hạn quyền; chuẩn bị một tập dữ liệu nhỏ có checksum và tránh chạy <code>sync</code> vào đích production trong lần thử đầu.",
        "steps": [
            "Cài rclone từ nguồn/package phù hợp và tạo remote bằng credential tối thiểu; bảo vệ file cấu hình.",
            "Dùng <code>lsd</code>/<code>ls</code> để xác nhận đúng remote/path rồi chạy <code>copy</code> hoặc dry-run trước.",
            "Chỉ dùng <code>sync</code> khi đã hiểu rằng file thừa ở đích có thể bị xóa; luôn chạy <code>--dry-run</code> cho thay đổi destructive.",
            "Kiểm checksum/listing ở đích và log transfer; sau đó mới cân nhắc scheduler hoặc bandwidth/concurrency tuning.",
        ],
        "expected": [
            "Remote listing chỉ đúng bucket/path dự kiến và credential không có quyền rộng hơn cần thiết.",
            "Dry-run mô tả chính xác file sẽ copy/delete; run thật truyền đúng tập dữ liệu.",
            "Checksum hoặc <code>rclone check</code> không báo mismatch cho dữ liệu mẫu.",
        ],
        "cleanup": "Xóa dữ liệu remote lab bằng lệnh explicit sau khi xác nhận path, rồi xóa remote config/credential test nếu không dùng tiếp. Không dùng <code>sync</code> để 'dọn' khi chưa review dry-run.",
    },
    19: {
        "file": "post-019-triage-hieu-nang-vmstat-iostat.html",
        "objective": "Triage nhanh CPU, memory pressure và I/O bằng vmstat/iostat cùng công cụ tương đương trên FreeBSD, tập trung vào xu hướng nhiều mẫu thay vì một snapshot.",
        "prereq": "Có workload lab hoặc host cần quan sát; biết baseline bình thường của hệ trước khi kết luận bottleneck và chỉ cài thêm tool khi thực sự thiếu.",
        "steps": [
            "Ghi load/uptime và lấy nhiều mẫu <code>vmstat</code> thay vì đọc dòng đầu như một kết luận.",
            "Dùng <code>iostat</code> để xem throughput/latency/utilization theo thiết bị và liên hệ với queue/wait ở vmstat.",
            "Đối chiếu process-level bằng top/ps khi thấy CPU hoặc I/O bất thường; trên FreeBSD dùng metric/tool native tương ứng.",
            "So sánh với baseline và thời điểm workload; chỉ đề xuất tuning sau khi bottleneck được lặp lại và định vị.",
        ],
        "expected": [
            "Các mẫu liên tiếp cho thấy xu hướng nhất quán thay vì một spike đơn lẻ.",
            "Nếu có bottleneck, metric CPU/memory/I/O và process liên quan kể cùng một câu chuyện có thể kiểm chứng.",
            "Nếu không có tín hiệu bền vững, kết luận là chưa đủ bằng chứng thay vì tuning theo cảm giác.",
        ],
        "cleanup": "Các lệnh quan sát không cần rollback. Nếu đã cài sysstat hoặc gói đo đạc chỉ để lab, có thể gỡ package sau khi lưu kết quả cần thiết; không xóa log/metric phục vụ điều tra đang diễn ra.",
    },
    20: {
        "file": "post-020-firewall-rollback-negative-test.html",
        "objective": "Thay đổi firewall có rollback và negative test: chứng minh traffic cần thiết được phép, traffic không mong muốn bị chặn và đường quản trị vẫn còn.",
        "prereq": "Có console/out-of-band hoặc phiên cứu hộ, biết IP quản trị và service cần giữ; chuẩn bị host test bên ngoài để kiểm cả allow lẫn deny.",
        "steps": [
            "Chụp ruleset hiện tại và xác định rule tối thiểu phải giữ cho SSH/management trước khi sửa.",
            "Chuẩn bị cơ chế rollback có timeout hoặc lệnh restore chạy độc lập với phiên SSH hiện tại.",
            "Áp ruleset mới bằng nftables/firewalld theo distro Linux hoặc pf/ipfw trên FreeBSD; không áp lệnh Linux cho FreeBSD.",
            "Chạy positive test cho service được phép và negative test cho port/nguồn phải bị chặn; chỉ hủy rollback khi cả hai đạt.",
        ],
        "expected": [
            "Kết nối quản trị mới vẫn mở được từ nguồn được phép và service cần thiết reachable.",
            "Negative test bị chặn đúng nơi, log/counter firewall tăng theo rule dự kiến.",
            "Khi cố tình áp rule lỗi trong lab, rollback tự khôi phục ruleset và phiên quản trị mới hoạt động lại.",
        ],
        "cleanup": "Khôi phục ruleset baseline đã lưu, hủy timer/job rollback còn treo và xác nhận firewall chỉ còn rule production mong muốn. Trên FreeBSD kiểm riêng pf/ipfw state/rules sau restore.",
    },
}

META_RE = re.compile(r'(<script type="application/json" id="ld-meta">\s*)(.*?)(\s*</script>)', re.S)
HEADER_END_RE = re.compile(r'</header>', re.I)
HEADING_RE = re.compile(r'(<(?:section|div)[^>]*>\s*<h2[^>]*>\s*<span class="num">(?P<num>0[3-7])</span>)(?P<title>.*?)(</h2>)', re.I | re.S)
PRE_RE = re.compile(r'(<pre(?P<attrs>[^>]*)>\s*<code(?P<cattrs>[^>]*)>)(?P<body>.*?)(</code>\s*</pre>)', re.I | re.S)

HEADINGS = {
    "03": " Các bước thực hiện",
    "04": " Kiểm chứng",
    "05": " Lưu ý &amp; Khắc phục lỗi",
    "06": " Lưu ý bảo mật &amp; vận hành",
    "07": " Bài tập tự luyện",
}

def ol(items: list[str]) -> str:
    return '<ol class="steps">' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'

def expected(items: list[str]) -> str:
    return '<h3>Kết quả mong đợi</h3><ul class="clean">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'

def contract() -> str:
    return (
        '\n<section class="style-contract" aria-label="Phạm vi kiểm chứng">\n'
        f'  <p><strong>Tested on:</strong> {DISPLAY_TESTED}</p>\n'
        f'  <p><strong>Last verified:</strong> {LAST_VERIFIED} · đối chiếu tài liệu official/upstream</p>\n'
        '</section>\n'
    )

def language_for(body: str) -> str:
    stripped = html.unescape(re.sub(r'<[^>]+>', '', body)).lstrip()
    if stripped.startswith(('[Unit]', '[Timer]', '[Service]', '[Install]', '[Interface]', '[Peer]')):
        return 'ini'
    if stripped.startswith(('server {', 'location {')):
        return 'nginx'
    return 'bash'

def migrate(path: Path, issue: int, cfg: dict) -> None:
    text = path.read_text(encoding='utf-8')
    if 'class="style-contract"' in text:
        raise RuntimeError(f'already migrated unexpectedly: {path}')

    mm = META_RE.search(text)
    if not mm:
        raise RuntimeError(f'missing meta: {path}')
    meta = json.loads(html.unescape(mm.group(2)))
    meta['tested_on'] = TESTED
    meta['last_verified'] = LAST_VERIFIED
    meta['changes_system'] = True
    meta_text = json.dumps(meta, ensure_ascii=False, indent=2)
    text = text[:mm.start()] + mm.group(1) + meta_text + mm.group(3) + text[mm.end():]

    insertion = (
        contract()
        + f'<section><h2>Mục tiêu</h2><p>{cfg["objective"]}</p></section>\n'
        + f'<section><h2>Yêu cầu tiên quyết</h2><p>{cfg["prereq"]}</p></section>\n'
    )
    hm = HEADER_END_RE.search(text)
    if not hm:
        raise RuntimeError(f'missing header: {path}')
    text = text[:hm.end()] + insertion + text[hm.end():]

    def heading_repl(m: re.Match) -> str:
        num = m.group('num')
        return m.group(1) + HEADINGS[num] + m.group(4)
    text = HEADING_RE.sub(heading_repl, text)

    marker3 = re.search(r'(<section[^>]*>\s*<h2[^>]*>\s*<span class="num">03</span>.*?</h2>)', text, re.I | re.S)
    marker4 = re.search(r'(<section[^>]*>\s*<h2[^>]*>\s*<span class="num">04</span>.*?</h2>)', text, re.I | re.S)
    marker5 = re.search(r'<section[^>]*>\s*<h2[^>]*>\s*<span class="num">05</span>', text, re.I | re.S)
    if not (marker3 and marker4 and marker5):
        raise RuntimeError(f'missing numbered section: {path}')
    text = text[:marker3.end()] + ol(cfg['steps']) + text[marker3.end():]
    marker4 = re.search(r'(<section[^>]*>\s*<h2[^>]*>\s*<span class="num">04</span>.*?</h2>)', text, re.I | re.S)
    text = text[:marker4.end()] + expected(cfg['expected']) + text[marker4.end():]
    marker5 = re.search(r'<section[^>]*>\s*<h2[^>]*>\s*<span class="num">05</span>', text, re.I | re.S)
    cleanup = f'<section><h2>Gỡ / Hoàn tác</h2><p>{cfg["cleanup"]}</p></section>\n'
    text = text[:marker5.start()] + cleanup + text[marker5.start():]

    def code_repl(m: re.Match) -> str:
        start = m.group(1)
        attrs = m.group('attrs')
        cattrs = m.group('cattrs')
        body = m.group('body')
        ending = m.group(5)
        if 'language-' not in cattrs:
            lang = language_for(body)
            start = start.replace('<code', f'<code class="language-{lang}"', 1)
        return start + body + ending
    text = PRE_RE.sub(code_repl, text)

    # Shell command blocks need explicit execution context. FreeBSD blocks are root; others default user + sudo.
    out: list[str] = []
    pos = 0
    for m in re.finditer(r'<pre(?P<attrs>[^>]*)>\s*<code[^>]*class="[^"]*language-(?:bash|sh|shell)[^"]*"', text, re.I):
        out.append(text[pos:m.start()])
        context = text[max(0, m.start() - 500):m.start()]
        if 'data-run-as=' not in context:
            run_as = 'root' if 'bsd' in m.group('attrs').lower().split() else 'user'
            out.append(f'<p class="run-context" data-run-as="{run_as}"><strong>Run as:</strong> {run_as}</p>\n')
        pos = m.start()
    out.append(text[pos:])
    text = ''.join(out)

    path.write_text(text, encoding='utf-8')

for issue, cfg in PLAN.items():
    migrate(POSTS / cfg['file'], issue, cfg)
print('Batch B migrated:', ', '.join(f'#{i:03d}' for i in PLAN))

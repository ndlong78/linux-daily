#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"

GENERIC_STEPS = re.compile(
    r'<ol class="steps"><li>Đọc khối dành cho đúng hệ điều hành và xác nhận tên interface, service, dataset hoặc device trước khi chạy lệnh\.</li>'
    r'<li>Thực hiện thay đổi theo phạm vi lab/maintenance đã chuẩn bị; không trộn lệnh Linux với FreeBSD\.</li>'
    r'<li>Chuyển sang mục Kiểm chứng và chỉ coi thao tác hoàn tất khi tín hiệu quan sát khớp kết quả mong đợi\.</li></ol>'
)
GENERIC_EXPECTED = re.compile(
    r'<h3>Expected Output</h3><p>Kết quả mong đợi: lệnh kiểm chứng phải phản ánh đúng trạng thái vừa cấu hình; nếu tín hiệu không khớp, dừng và xử lý trước khi đóng phiên quản trị hoặc tiếp tục bước phá dữ liệu\.</p>'
)
STYLE_CONTRACT = re.compile(
    r'<section class="style-contract" aria-label="Phạm vi kiểm chứng">\s*'
    r'<p><strong>Tested on:</strong>.*?</p>\s*'
    r'<p><strong>Last verified:</strong> 2026-08-09</p>\s*'
    r'</section>',
    re.DOTALL,
)

COMMON_STYLE = '''<section class="style-contract" aria-label="Phạm vi kiểm chứng">
    <p><strong>Tested on:</strong> Ubuntu/Xubuntu 24.04 LTS · Debian 13 stable · Fedora 42 · FreeBSD 14.3-RELEASE</p>
    <p><strong>Last verified:</strong> 2026-08-09 · đối chiếu tài liệu official/upstream</p>
  </section>'''

DATA = {
    1: {
        "file": "post-001-static-ip.html",
        "steps": [
            "Ghi lại trạng thái hiện tại: tên interface, địa chỉ, default route, DNS và công cụ đang quản lý interface.",
            "Chuẩn bị cấu hình tĩnh cho đúng hệ điều hành; với máy từ xa phải giữ console hoặc một phiên SSH cứu hộ.",
            "Áp dụng bằng cơ chế có rollback nếu hệ hỗ trợ: <code>netplan try</code> trên Ubuntu hoặc checkpoint của NetworkManager trên Fedora.",
            "Kiểm tra IP, route, DNS và mở một phiên SSH mới; chỉ sau đó mới coi cấu hình persistent là hoàn tất.",
        ],
        "expected": [
            "Interface có đúng IP/prefix dự kiến và chỉ có default route mong muốn.",
            "Resolver phân giải được tên qua cơ chế NSS của hệ điều hành.",
            "Gateway reachable và một phiên SSH mới đăng nhập thành công trước khi đóng phiên cũ.",
        ],
    },
    2: {
        "file": "post-002-ssh-hardening.html",
        "steps": [
            "Xác nhận public-key login hoạt động bằng một phiên SSH mới trước khi thay đổi authentication policy.",
            "Giữ nguyên phiên quản trị hiện tại và sao lưu cấu hình SSH để có đường lui nếu reload lỗi.",
            "Áp các directive hardening theo đúng precedence của từng hệ, sau đó chạy <code>sshd -t</code> và kiểm effective config bằng <code>sshd -T</code>.",
            "Reload đúng service (<code>ssh</code> trên Ubuntu/Debian, <code>sshd</code> trên Fedora/FreeBSD) rồi kiểm lại bằng một kết nối mới.",
        ],
        "expected": [
            "<code>sshd -t</code> kết thúc với exit code 0 và không in lỗi cú pháp.",
            "Effective config thể hiện key-only theo policy của bài, root login bị giới hạn và danh sách user được phép đúng dự kiến.",
            "Một phiên SSH mới đăng nhập bằng key thành công; đăng nhập password/root bị từ chối theo policy đã đặt.",
        ],
    },
    3: {
        "file": "post-003-zfs-snapshots.html",
        "steps": [
            "Xác nhận đúng pool/dataset và kiểm dung lượng trống trước khi thao tác snapshot.",
            "Cài hoặc nạp OpenZFS theo đúng hệ điều hành; FreeBSD dùng ZFS trong base thay vì áp quy trình Linux.",
            "Tạo snapshot có tên rõ nghĩa, liệt kê snapshot và tạo một thay đổi nhỏ trong dataset lab để quan sát copy-on-write.",
            "Thử khôi phục một file từ snapshot trước; chỉ dùng rollback toàn dataset khi hiểu rõ dữ liệu mới hơn sẽ bị loại bỏ.",
        ],
        "expected": [
            "<code>zfs list -t snapshot</code> hiển thị snapshot đúng dataset và đúng tên.",
            "Dữ liệu trong snapshot vẫn đọc được sau khi dataset sống bị thay đổi.",
            "Nếu thử restore file, nội dung khôi phục khớp trạng thái tại thời điểm snapshot mà không cần rollback toàn dataset.",
        ],
    },
    4: {
        "file": "post-004-restic-backup.html",
        "steps": [
            "Cài Restic từ kho phù hợp và tạo repository backup ở vị trí lab/remote đã chuẩn bị.",
            "Thiết lập credential qua biến môi trường hoặc file quyền hạn chế; không ghi password trực tiếp vào shell history hoặc script công khai.",
            "Chạy backup cho một thư mục mẫu, sau đó liệt kê snapshot và kiểm statistics để xác nhận dữ liệu đã vào repository.",
            "Restore vào một thư mục tạm khác nguồn, so sánh file rồi mới coi backup là đã được kiểm chứng.",
        ],
        "expected": [
            "Lệnh backup kết thúc thành công và tạo snapshot mới trong repository.",
            "<code>restic snapshots</code> hiển thị đúng host/path/tag của lần backup vừa chạy.",
            "File restore mở được và checksum/nội dung khớp với dữ liệu nguồn đã chọn để kiểm thử.",
        ],
    },
    5: {
        "file": "post-005-doc-log-journald-syslog.html",
        "steps": [
            "Xác định log stack thực tế trước: journald/rsyslog trên Linux hay syslog/daemon tương ứng trên FreeBSD.",
            "Tạo một sự kiện vô hại có dấu nhận biết riêng bằng <code>logger</code> để có mẫu truy vết.",
            "Tìm sự kiện bằng công cụ native của từng hệ, sau đó thử filter theo service, priority hoặc khoảng thời gian.",
            "Kiểm vị trí lưu/persistence và rotation để biết log còn tồn tại sau reboot hoặc sau chu kỳ rotate hay không.",
        ],
        "expected": [
            "Thông điệp test xuất hiện đúng một cách nhất quán trong nguồn log đang được hệ thống sử dụng.",
            "Filter theo thời gian/service không kéo theo lượng log ngoài phạm vi cần điều tra.",
            "Bạn xác định được log nào chỉ ở journal runtime và log nào được ghi persistent/rotate trên máy.",
        ],
    },
    6: {
        "file": "post-006-ansible-multi-os.html",
        "steps": [
            "Khai báo inventory lab gồm ít nhất một Linux host và một FreeBSD host, rồi kiểm kết nối bằng module ping phù hợp.",
            "Thu thập facts và dùng <code>ansible_os_family</code>/<code>ansible_system</code> để rẽ nhánh package, service và path thay vì suy đoán theo hostname.",
            "Viết task bằng module idempotent; tách riêng biến hoặc block cho FreeBSD khi service/path khác Linux.",
            "Chạy <code>--check --diff</code> trước, sau đó apply và chạy lại lần hai để chứng minh playbook không tạo thay đổi thừa.",
        ],
        "expected": [
            "Facts nhận đúng family/system của từng node và không chạy package manager Linux trên FreeBSD.",
            "Lần chạy apply đầu chỉ thay đổi những resource cần thiết.",
            "Lần chạy thứ hai kết thúc với <code>changed=0</code> cho các task đã đạt trạng thái mong muốn.",
        ],
    },
    7: {
        "file": "post-007-lab-web-server-tuong-lua.html",
        "steps": [
            "Cài web server theo đúng package/service của từng hệ và xác nhận service đang lắng nghe cục bộ trước khi mở firewall.",
            "Tạo trang test có marker riêng để phân biệt phản hồi của lab với dịch vụ khác.",
            "Mở đúng cổng HTTP bằng firewall native: UFW/nftables/firewalld trên Linux theo bài, pf/ipfw trên FreeBSD; không trộn cú pháp.",
            "Kiểm từ localhost rồi từ một máy khác; sau lab đóng rule và gỡ service theo phần hoàn tác.",
        ],
        "expected": [
            "Listener HTTP xuất hiện trên đúng địa chỉ/cổng và process owner là web server dự kiến.",
            "<code>curl</code> từ client nhận HTTP 200 và marker của trang test.",
            "Sau khi cleanup, rule firewall lab và listener web không còn tồn tại nếu bài yêu cầu gỡ toàn bộ.",
        ],
    },
    8: {
        "file": "post-008-chan-doan-mang.html",
        "steps": [
            "Bắt đầu từ link/interface: xác nhận trạng thái NIC, địa chỉ và lỗi/drop trước khi nghi DNS hay firewall.",
            "Kiểm routing và default gateway, sau đó thử reachability tới một IP đã biết để tách lỗi L3 khỏi lỗi phân giải tên.",
            "Kiểm resolver/DNS bằng công cụ phù hợp, rồi thử kết nối TCP tới đúng host/port của dịch vụ.",
            "Chỉ dùng packet capture khi các bước trên chưa đủ bằng chứng; đặt filter hẹp theo interface, host và port.",
        ],
        "expected": [
            "Bạn xác định được tầng đầu tiên thất bại: link/address, route, DNS hay TCP/service.",
            "Mỗi kết luận có ít nhất một tín hiệu quan sát được thay vì dựa vào một lệnh ping duy nhất.",
            "Nếu capture packet, dữ liệu thu được chỉ chứa traffic liên quan trực tiếp tới câu hỏi chẩn đoán.",
        ],
    },
    9: {
        "file": "post-009-user-sudo-doas.html",
        "steps": [
            "Tạo hoặc chọn tài khoản lab, xác nhận UID/group và giữ một phiên root/admin độc lập trước khi thay đổi quyền nâng đặc quyền.",
            "Trên Linux cấu hình sudo bằng file trong <code>/etc/sudoers.d</code> và luôn kiểm bằng <code>visudo</code>; trên FreeBSD dùng sudo hoặc doas theo công cụ đã cài.",
            "Cấp đúng command/scope cần thiết thay vì <code>ALL=(ALL) ALL</code> nếu bài toán chỉ cần một tác vụ quản trị cụ thể.",
            "Đăng nhập lại bằng user lab, thử lệnh được phép và một lệnh không được phép để kiểm cả positive lẫn negative path.",
        ],
        "expected": [
            "File sudoers/doas hợp lệ về cú pháp và không làm mất quyền của tài khoản quản trị hiện có.",
            "User lab chạy được đúng lệnh đã cho phép sau khi xác thực theo policy.",
            "Một lệnh ngoài phạm vi bị từ chối, chứng minh rule không cấp quyền rộng hơn dự kiến.",
        ],
    },
    10: {
        "file": "post-010-them-dia-moi.html",
        "steps": [
            "Đối chiếu size, model, serial và trạng thái mount để chứng minh đúng đĩa mới trước mọi thao tác ghi.",
            "Tạo GPT/partition bằng công cụ native của hệ điều hành; dừng ngay nếu tên device khác với kế hoạch.",
            "Tạo filesystem, mount tạm và ghi/đọc một file nhỏ để kiểm filesystem hoạt động trước khi sửa cấu hình boot.",
            "Dùng định danh bền trong <code>fstab</code> (UUID trên Linux, GPT label phù hợp trên FreeBSD), kiểm bằng <code>findmnt --verify</code>/<code>mount -a</code> rồi mới reboot.",
        ],
        "expected": [
            "Partition/filesystem chỉ xuất hiện trên đúng đĩa mới; đĩa hệ thống và các mount hiện hữu không thay đổi.",
            "Mountpoint hiển thị đúng source và filesystem type; file test đọc lại thành công.",
            "Kiểm tra fstab/mount-a không báo lỗi, và mount vẫn xuất hiện đúng sau một lần reboot lab có kiểm soát.",
        ],
    },
}


def render_steps(items: list[str]) -> str:
    return '<ol class="steps">' + ''.join(f'<li>{item}</li>' for item in items) + '</ol>'


def render_expected(items: list[str]) -> str:
    return '<h3>Kết quả mong đợi</h3><ul class="clean">' + ''.join(f'<li>{item}</li>' for item in items) + '</ul>'


def main() -> int:
    changed = 0
    for issue, spec in DATA.items():
        path = POSTS / spec["file"]
        text = path.read_text(encoding="utf-8")
        original = text
        text, n_style = STYLE_CONTRACT.subn(COMMON_STYLE, text, count=1)
        text, n_steps = GENERIC_STEPS.subn(render_steps(spec["steps"]), text, count=1)
        text, n_expected = GENERIC_EXPECTED.subn(render_expected(spec["expected"]), text, count=1)
        if not (n_style == n_steps == n_expected == 1):
            raise SystemExit(
                f"#{issue:03d}: replacement mismatch style={n_style} steps={n_steps} expected={n_expected}"
            )
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(f"updated #{issue:03d} {path.name}")
    print(f"polished={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Technical Contributor Review Guide

Tài liệu này dành cho reviewer kỹ thuật của Linux Daily. Mục tiêu là giúp review một PR nội dung Linux/Unix **mà không cần biết lịch sử repository**, nhưng vẫn giữ các tiêu chuẩn về nguồn, portability và an toàn vận hành.

## 1. Review theo lớp

Review theo thứ tự sau để tránh sa vào tiểu tiết quá sớm:

1. **Scope:** PR đang sửa bài nào/chức năng nào, có trộn thay đổi không liên quan không.
2. **Technical claims:** lệnh, đường dẫn, tên service, package, default behavior và version assumptions có đúng không.
3. **Cross-distro portability:** Ubuntu/Xubuntu, Debian, Fedora và FreeBSD có được phân biệt đúng không.
4. **Operational safety:** có nguy cơ lockout, mất dữ liệu, downtime hoặc thay đổi persistent ngoài ý muốn không.
5. **Evidence:** nguồn official/upstream có thực sự hỗ trợ claim đang viết không.
6. **Repository consistency:** metadata/generated artifacts/CI có còn nhất quán không.

CI là guardrail, không thay thế technical review. Một PR có thể xanh CI nhưng vẫn sai về semantics hệ điều hành hoặc thiếu rollback thực tế.

## 2. Source quality

Với bài mới hoặc technical correction, ưu tiên nguồn theo thứ tự:

1. tài liệu upstream/vendor chính thức;
2. tài liệu chính thức của Ubuntu, Debian, Fedora hoặc FreeBSD;
3. manpage/documentation chính thức của package/tool.

Không dùng blog SEO, forum hoặc nội dung AI-generated làm bằng chứng chính cho command/system behavior nếu có primary source phù hợp.

Reviewer cần kiểm:

- nguồn có đúng sản phẩm/version/context đang nói tới không;
- title/URL trong `ld-meta.sources` khớp phần **Nguồn kỹ thuật** hiển thị;
- claim quan trọng có thể truy ngược được tới nguồn;
- không dùng một nguồn để suy rộng sang distro khác khi semantics khác nhau;
- không copy claim từ bài cũ nếu chưa re-verify.

`review_status="reviewed"` chỉ hợp lý khi các claim/lệnh chính đã được kiểm chứng. `draft` không nên merge.

## 3. Distro portability

### Ubuntu / Xubuntu

Kiểm APT, systemd, netplan/UFW/nftables và đường dẫn cấu hình thực tế. Xubuntu khác desktop environment nhưng phần quản trị nền vẫn theo Ubuntu trừ khi bài nói tới GUI/session-specific behavior.

### Debian

Không mặc định mọi hướng dẫn Ubuntu áp dụng nguyên trạng. Kiểm package availability trong Debian stable, service/package naming và việc một helper/tool có được cài mặc định hay không.

### Fedora

Kiểm DNF, systemd, SELinux, NetworkManager/`nmcli` và firewalld. Với file/path mới hoặc service custom, xem có cần SELinux context/policy không.

### FreeBSD — luôn review riêng

FreeBSD không dùng systemd. Không chấp nhận việc gán trực tiếp các lệnh Linux như:

```text
systemctl
apt
dnf
nmcli
netplan
nftables
```

thành giải pháp FreeBSD.

Reviewer cần kiểm tương đương thực tế qua `pkg`/ports, rc.d, `/etc/rc.conf`, `service`, pf/ipfw và layout/path của FreeBSD. Nếu không có tương đương trực tiếp, bài phải nói rõ thay vì bịa một command tương tự.

## 4. Operational safety theo nhóm thay đổi

### Networking / firewall / remote access

Trước khi approve, trả lời được:

- interface/port/subnet/address family nào bị tác động;
- thay đổi có thể cắt SSH/remote session không;
- rule/default policy được áp temporary hay persistent;
- rollback được thực hiện **trước khi** persist bằng cách nào;
- IPv4/IPv6 có khác semantics không.

Một hướng dẫn firewall/SSH hardening có nguy cơ lockout nhưng không có đường lui rõ ràng là blocker.

### Storage / filesystem

Kiểm đúng layer: block device → partition → RAID/LVM/ZFS → filesystem → mount. Reviewer phải xác nhận:

- device/path không mơ hồ;
- command destructive được đánh dấu rõ;
- shrink/grow direction có được hỗ trợ bởi filesystem/layer đó không;
- backup có trước thao tác phá hủy;
- mount/persistence không lẫn Linux `/etc/fstab` với FreeBSD semantics khác khi có khác biệt.

### Backup / restore

Không approve bài chỉ chứng minh “backup command chạy thành công”. Phải có cách kiểm chứng restore hoặc ít nhất verification evidence phù hợp với scope.

### Authentication / permissions

Kiểm phạm vi account/root/sudo, ownership/mode, session đang dùng và đường lui. Khi hardening SSH/sudo, reviewer phải thấy phương án giữ một phiên admin hoặc validation trước reload/restart nếu có nguy cơ mất quyền truy cập.

### Automation / shell

Kiểm shell thực thi, quoting, exit code, `set -e` assumptions, PATH, privilege và portability. Không mặc định Bash behavior cho `/bin/sh` trên mọi hệ điều hành.

## 5. Command review checklist

Với mỗi command quan trọng, reviewer nên hỏi:

- command có tồn tại trên distro đó không;
- package cung cấp command là gì;
- có cần root/sudo không;
- option có đúng version hiện hành không;
- command là read-only hay mutate state;
- nếu mutate: phạm vi tác động, persistence và rollback là gì;
- output/exit code nào chứng minh thao tác thành công;
- command có copy-paste an toàn với placeholder được ghi rõ không.

Không approve command “trông quen” nếu chưa chắc semantics.

## 6. Review metadata và repository consistency

Với PR sửa bài, kiểm tối thiểu:

- `issue`, `date`, `axis`, `slug`, `eyebrow`, `title`, `lede` đúng với bài;
- taxonomy axis hợp lệ;
- `sources` và `review_status` đúng policy;
- generated navigation/search/feed/sitemap/social artifacts được regenerate qua tool, không sửa tay;
- `python3 tools/publish.py check` pass;
- external link check được chạy khi source/URL đổi.

Nếu PR thay GitHub Actions, chạy thêm:

```bash
python3 tools/workflow_safety.py
```

## 7. Mức độ review finding

Dùng ba mức để feedback rõ ràng:

- **Blocker:** sai command/semantics, nguy cơ mất dữ liệu/lockout, FreeBSD bị gán lệnh Linux, source không hỗ trợ claim, hoặc thiếu rollback ở thao tác rủi ro cao.
- **Needs change:** thiếu distro distinction, verification chưa đủ, wording có thể dẫn tới thao tác sai, metadata/source mismatch.
- **Suggestion:** clarity, formatting, ví dụ bổ sung hoặc cải thiện trải nghiệm đọc nhưng không ảnh hưởng correctness/safety.

Ưu tiên comment vào nguyên nhân và rủi ro, không chỉ yêu cầu đổi câu chữ.

## 8. Checklist trước khi approve

- [ ] Tôi hiểu scope và không thấy thay đổi ngoài phạm vi đáng kể.
- [ ] Các command/claim kỹ thuật chính đã có primary evidence phù hợp.
- [ ] Ubuntu/Xubuntu, Debian, Fedora và FreeBSD được phân biệt đúng nơi cần thiết.
- [ ] FreeBSD không bị gán command/path/service model của Linux.
- [ ] Networking/firewall/auth có rollback trước persistence nếu có nguy cơ lockout.
- [ ] Storage/destructive operation nêu rõ target, backup và recovery/restore evidence.
- [ ] Automation/shell nêu đúng shell, exit-code/quoting/privilege assumptions.
- [ ] Verification steps đủ để chứng minh trạng thái sau thay đổi.
- [ ] Metadata/source/generated artifacts nhất quán.
- [ ] `python3 tools/publish.py check` và các gate bổ sung liên quan đã pass.

Nếu một mục không áp dụng, reviewer có thể bỏ qua nhưng nên nêu rõ trong review note khi đó là một guardrail rủi ro cao.

## 9. Review flow ngắn cho reviewer mới

```text
Đọc PR scope
   ↓
Xác định bài/tool/distro bị tác động
   ↓
Kiểm primary sources cho claim chính
   ↓
So command/path/service theo từng distro
   ↓
Rà rollback / destructive semantics / verification
   ↓
Kiểm metadata + generated artifacts
   ↓
Đọc CI
   ↓
Approve hoặc ghi blocker/needs-change có lý do kỹ thuật
```

Reviewer không cần tái tạo toàn bộ lịch sử Linux Daily. `CONTRIBUTING.md`, tài liệu này và các quality gate hiện tại là đủ để review một PR độc lập.
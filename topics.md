# Nhật ký chủ đề Linux Daily
# Định dạng: #số | YYYY-MM-DD | trục | tên chủ đề
# state.json giữ clock cadence; danh sách này dùng để giữ thứ tự series và tránh trùng chủ đề.
# Publication timeline #001–#042 đã được đồng bộ liên tục đến 2026-08-11.

#001 | 2026-07-01 | Networking | Đặt IP tĩnh + cặp DNS trên Ubuntu/Debian/Fedora/FreeBSD
#002 | 2026-07-02 | Bảo mật | Gia cố SSH (key-only, cấm root, AllowUsers) trên Ubuntu/Debian/Fedora/FreeBSD
#003 | 2026-07-03 | Storage | Ảnh chụp (snapshot) ZFS: lệnh chung, cài đặt khác nhau trên Ubuntu/Debian/Fedora/FreeBSD
#004 | 2026-07-04 | Công cụ mới | restic: backup mã hoá, khử trùng lặp, tăng dần trên Ubuntu/Debian/Fedora/FreeBSD
#005 | 2026-07-05 | Monitoring | Đọc log hệ thống: journald/journalctl trên Linux vs syslog/newsyslog trên FreeBSD
#006 | 2026-07-06 | Automation | Ansible: một playbook đa nền tảng (apt/dnf/pkgng, systemd vs rc) trên Ubuntu/Debian/Fedora/FreeBSD
#007 | 2026-07-07 | Ôn tập | Lab end-to-end: dựng web server an toàn, mở đúng cổng qua tường lửa (ufw/firewalld/pf) trên Ubuntu/Debian/Fedora/FreeBSD
#008 | 2026-07-08 | Networking | Chẩn đoán mạng theo tầng: ip/ss (iproute2) trên Linux vs ifconfig/netstat/sockstat trên FreeBSD
#009 | 2026-07-09 | Bảo mật | Tạo user & trao quyền: nhóm sudo/wheel + sudo trên Linux vs pw + doas trên FreeBSD
#010 | 2026-07-10 | Storage | Thêm đĩa mới: phân vùng/định dạng/mount vĩnh viễn — parted+mkfs (UUID) trên Linux vs gpart+newfs (nhãn GPT) trên FreeBSD
#011 | 2026-07-11 | Công cụ mới | tmux: phiên terminal sống sót khi SSH rớt, chia cửa sổ/khung — cách dùng chung, chỉ khác lệnh cài trên Ubuntu/Debian/Fedora/FreeBSD
#012 | 2026-07-12 | Monitoring | Lập lịch định kỳ: cron (mọi nơi) + systemd timers trên Linux vs cron + periodic(8) trên FreeBSD
#013 | 2026-07-13 | Automation | Viết bash script vững: /bin/sh (dash/bash/sh) khác nhau, shebang env bash, set -euo pipefail + trap trên Ubuntu/Debian/Fedora/FreeBSD
#014 | 2026-07-14 | Ôn tập | Lab end-to-end: hệ backup tự động có kiểm chứng bằng restore thật (restic + systemd timer trên Linux / cron trên FreeBSD)
#015 | 2026-07-15 | Networking | WireGuard: đường hầm VPN mã hoá — cùng wg0.conf, bật bằng systemd wg-quick trên Linux vs rc.conf trên FreeBSD
#016 | 2026-07-16 | Bảo mật | fail2ban: chặn brute-force tự động — nguồn log (journald vs auth.log) và backend cấm (nftables/firewalld vs pf); FreeBSD có blocklistd trong base, sshguard là lựa chọn ngoài base
#017 | 2026-07-17 | Storage | Mở rộng dung lượng online: LVM (lvextend+resize2fs/xfs_growfs) trên Linux vs gpart resize+growfs / ZFS autoexpand trên FreeBSD
#018 | 2026-07-18 | Công cụ mới | rclone: đồng bộ & mã hoá dữ liệu lên cloud storage (S3/B2/Drive), remote crypt trên Ubuntu/Debian/Fedora/FreeBSD
#019 | 2026-07-19 | Monitoring | Triage hiệu năng trong 5 phút: CPU, RAM và disk I/O bằng vmstat + iostat trên Ubuntu/Debian/Fedora/FreeBSD
#020 | 2026-07-20 | Automation | Advanced Lab Security & Networking: firewall rollback tự động, negative test và recovery trên Ubuntu/Xubuntu, Debian, Fedora, FreeBSD
#021 | 2026-07-21 | Ôn tập | Advanced Lab Storage & Backup/Restore: backup trước thay đổi, failure injection, restore và checksum verification trên Ubuntu/Xubuntu, Debian, Fedora, FreeBSD
#022 | 2026-07-22 | Networking | DNS lỗi ở đâu? Tách client, resolver và authoritative bằng dig, resolvectl, drill
#023 | 2026-07-23 | Bảo mật | Least privilege: sudo trên Linux, doas trên FreeBSD
#024 | 2026-07-24 | Storage | Đĩa chưa đầy mà vẫn lỗi: đọc block, inode và ZFS dataset
#025 | 2026-07-25 | Công cụ mới | ripgrep: tìm log và cấu hình nhanh mà không quét nhầm
#026 | 2026-07-26 | Monitoring | vmstat và systat: đọc pressure trước khi đoán bottleneck
#027 | 2026-07-27 | Automation | Shell idempotent: chạy lại không phá trạng thái
#028 | 2026-07-28 | Ôn tập | Lab DNS outage: khoanh vùng trước, phục hồi sau
#029 | 2026-07-29 | Networking | Nhiều default gateway: policy routing không cắt SSH
#030 | 2026-07-30 | Bảo mật | Audit đăng nhập và privilege escalation: lần theo ai đã làm gì
#031 | 2026-07-31 | Storage | Mount options: giảm bề mặt tấn công của filesystem
#032 | 2026-08-01 | Công cụ mới | jq: biến JSON thành dữ liệu vận hành dùng được
#033 | 2026-08-02 | Monitoring | Process tree và service ownership: PID này thuộc service nào?
#034 | 2026-08-03 | Automation | systemd timer và FreeBSD periodic/cron: lịch chạy có bằng chứng
#035 | 2026-08-04 | Ôn tập | Lab filesystem đầy: quan sát, xử lý và phòng tái diễn
#036 | 2026-08-05 | Networking | tcpdump có mục tiêu: DNS, TCP handshake và firewall evidence
#037 | 2026-08-06 | Bảo mật | ACL và default ACL: quyền chia sẻ không cần chmod 777
#038 | 2026-08-07 | Storage | SMART và NVMe health: phát hiện disk degradation trước khi hỏng
#039 | 2026-08-08 | Công cụ mới | fd: tìm file nhanh nhưng phải hiểu ignore và hidden
#040 | 2026-08-09 | Monitoring | pidstat và procstat: theo dõi process theo thời gian
#041 | 2026-08-10 | Automation | Ansible handlers và templates: thay đổi có điều kiện, restart đúng lúc
#042 | 2026-08-11 | Ôn tập | Lab service outage: process, port, log và dependency

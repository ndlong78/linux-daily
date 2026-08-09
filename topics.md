# Nhật ký chủ đề Linux Daily
# Định dạng: #số | YYYY-MM-DD | trục | tên chủ đề
# state.json giữ clock cadence; danh sách này dùng để giữ thứ tự series và tránh trùng chủ đề.

#001 | 2026-07-02 | Networking | Đặt IP tĩnh + cặp DNS trên Ubuntu/Debian/Fedora/FreeBSD
#002 | 2026-07-04 | Bảo mật | Gia cố SSH (key-only, cấm root, AllowUsers) trên Ubuntu/Debian/Fedora/FreeBSD
#003 | 2026-07-06 | Storage | Ảnh chụp (snapshot) ZFS: lệnh chung, cài đặt khác nhau trên Ubuntu/Debian/Fedora/FreeBSD
#004 | 2026-07-08 | Công cụ mới | restic: backup mã hoá, khử trùng lặp, tăng dần trên Ubuntu/Debian/Fedora/FreeBSD
#005 | 2026-07-10 | Monitoring | Đọc log hệ thống: journald/journalctl trên Linux vs syslog/newsyslog trên FreeBSD
#006 | 2026-07-12 | Automation | Ansible: một playbook đa nền tảng (apt/dnf/pkgng, systemd vs rc) trên Ubuntu/Debian/Fedora/FreeBSD
#007 | 2026-07-14 | Ôn tập | Lab end-to-end: dựng web server an toàn, mở đúng cổng qua tường lửa (ufw/firewalld/pf) trên Ubuntu/Debian/Fedora/FreeBSD
#008 | 2026-07-16 | Networking | Chẩn đoán mạng theo tầng: ip/ss (iproute2) trên Linux vs ifconfig/netstat/sockstat trên FreeBSD
#009 | 2026-07-18 | Bảo mật | Tạo user & trao quyền: nhóm sudo/wheel + sudo trên Linux vs pw + doas trên FreeBSD
#010 | 2026-07-20 | Storage | Thêm đĩa mới: phân vùng/định dạng/mount vĩnh viễn — parted+mkfs (UUID) trên Linux vs gpart+newfs (nhãn GPT) trên FreeBSD
#011 | 2026-07-22 | Công cụ mới | tmux: phiên terminal sống sót khi SSH rớt, chia cửa sổ/khung — cách dùng chung, chỉ khác lệnh cài trên Ubuntu/Debian/Fedora/FreeBSD
#012 | 2026-07-24 | Monitoring | Lập lịch định kỳ: cron (mọi nơi) + systemd timers trên Linux vs cron + periodic(8) trên FreeBSD
#013 | 2026-07-26 | Automation | Viết bash script vững: /bin/sh (dash/bash/sh) khác nhau, shebang env bash, set -euo pipefail + trap trên Ubuntu/Debian/Fedora/FreeBSD
#014 | 2026-07-28 | Ôn tập | Lab end-to-end: hệ backup tự động có kiểm chứng bằng restore thật (restic + systemd timer trên Linux / cron trên FreeBSD)
#015 | 2026-07-30 | Networking | WireGuard: đường hầm VPN mã hoá — cùng wg0.conf, bật bằng systemd wg-quick trên Linux vs rc.conf trên FreeBSD
#016 | 2026-08-01 | Bảo mật | fail2ban: chặn brute-force tự động — nguồn log (journald vs auth.log) và backend cấm (nftables/firewalld vs pf); FreeBSD có blocklistd trong base, sshguard là lựa chọn ngoài base
#017 | 2026-08-03 | Storage | Mở rộng dung lượng online: LVM (lvextend+resize2fs/xfs_growfs) trên Linux vs gpart resize+growfs / ZFS autoexpand trên FreeBSD
#018 | 2026-08-05 | Công cụ mới | rclone: đồng bộ & mã hoá dữ liệu lên cloud storage (S3/B2/Drive), remote crypt trên Ubuntu/Debian/Fedora/FreeBSD
#019 | 2026-08-07 | Monitoring | Triage hiệu năng trong 5 phút: CPU, RAM và disk I/O bằng vmstat + iostat trên Ubuntu/Debian/Fedora/FreeBSD
#020 | 2026-08-08 | Automation | Advanced Lab Security & Networking: firewall rollback tự động, negative test và recovery trên Ubuntu/Xubuntu, Debian, Fedora, FreeBSD

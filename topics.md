# Nhật ký chủ đề Linux Daily
# Định dạng: #số | YYYY-MM-DD | trục | tên chủ đề
# Skill đọc dòng bài MỚI NHẤT để giữ nhịp 2 ngày, và toàn bộ danh sách để tránh trùng.

#001 | 2026-07-01 | Networking | Đặt IP tĩnh + cặp DNS trên Ubuntu/Debian/Fedora/FreeBSD
#002 | 2026-07-03 | Bảo mật | Gia cố SSH (key-only, cấm root, AllowUsers) trên Ubuntu/Debian/Fedora/FreeBSD
#003 | 2026-07-05 | Storage | Ảnh chụp (snapshot) ZFS: lệnh chung, cài đặt khác nhau trên Ubuntu/Debian/Fedora/FreeBSD
#004 | 2026-07-06 | Công cụ mới | restic: backup mã hoá, khử trùng lặp, tăng dần trên Ubuntu/Debian/Fedora/FreeBSD
#005 | 2026-07-07 | Monitoring | Đọc log hệ thống: journald/journalctl trên Linux vs syslog/newsyslog trên FreeBSD
#006 | 2026-07-09 | Automation | Ansible: một playbook đa nền tảng (apt/dnf/pkgng, systemd vs rc) trên Ubuntu/Debian/Fedora/FreeBSD
#007 | 2026-07-11 | Ôn tập | Lab end-to-end: dựng web server an toàn, mở đúng cổng qua tường lửa (ufw/firewalld/pf) trên Ubuntu/Debian/Fedora/FreeBSD
#008 | 2026-07-13 | Networking | Chẩn đoán mạng theo tầng: ip/ss (iproute2) trên Linux vs ifconfig/netstat/sockstat trên FreeBSD
#009 | 2026-07-15 | Bảo mật | Tạo user & trao quyền: nhóm sudo/wheel + sudo trên Linux vs pw + doas trên FreeBSD
#010 | 2026-07-17 | Storage | Thêm đĩa mới: phân vùng/định dạng/mount vĩnh viễn — parted+mkfs (UUID) trên Linux vs gpart+newfs (nhãn GPT) trên FreeBSD
#011 | 2026-07-19 | Công cụ mới | tmux: phiên terminal sống sót khi SSH rớt, chia cửa sổ/khung — cách dùng chung, chỉ khác lệnh cài trên Ubuntu/Debian/Fedora/FreeBSD
#012 | 2026-07-21 | Monitoring | Lập lịch định kỳ: cron (mọi nơi) + systemd timers trên Linux vs cron + periodic(8) trên FreeBSD
#013 | 2026-07-23 | Automation | Viết bash script vững: /bin/sh (dash/bash/sh) khác nhau, shebang env bash, set -euo pipefail + trap trên Ubuntu/Debian/Fedora/FreeBSD
#014 | 2026-07-25 | Ôn tập | Lab end-to-end: hệ backup tự động có kiểm chứng bằng restore thật (restic + systemd timer trên Linux / cron trên FreeBSD)
#015 | 2026-07-27 | Networking | WireGuard: đường hầm VPN mã hoá — cùng wg0.conf, bật bằng systemd wg-quick trên Linux vs rc.conf trên FreeBSD
#016 | 2026-07-29 | Bảo mật | fail2ban: chặn brute-force tự động — nguồn log (journald vs auth.log) và backend cấm (nftables/firewalld vs pf), FreeBSD còn có blacklistd/sshguard
#017 | 2026-07-31 | Storage | Mở rộng dung lượng online: LVM (lvextend+resize2fs/xfs_growfs) trên Linux vs gpart resize+growfs / ZFS autoexpand trên FreeBSD

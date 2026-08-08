# Distro Coverage & Portability Gate

P7.1 đưa yêu cầu đa HĐH của Linux Daily thành một quality gate deterministic thay vì chỉ dựa vào checklist review thủ công.

## Mục tiêu

Mỗi bài phải bao quát rõ:

- Ubuntu / Xubuntu;
- Debian;
- Fedora;
- FreeBSD.

FreeBSD phải được tách riêng về package/service/firewall/path semantics. Gate không coi FreeBSD là một Linux distro và không tự động chuyển lệnh Linux sang BSD.

## Chạy local

```bash
python3 tools/distro_coverage.py
python3 tools/distro_coverage.py --check
```

`tools/publish.py prepare` regenerate report; `tools/publish.py check` chạy validator read-only như một phần của publish contract.

## Những gì gate kiểm

1. Presence coverage của bốn platform trong từng bài.
2. Mỗi bài có ít nhất một `<pre class="bsd">...</pre>` để code FreeBSD được tách khỏi Linux.
3. Các Linux-only command/path rõ ràng không xuất hiện trong block FreeBSD, ví dụ:
   - `apt`, `apt-get`, `dnf`, `yum`;
   - `systemctl`, `journalctl`, `timedatectl`, `hostnamectl`, `loginctl`;
   - `nft`, `ufw`, `firewall-cmd`;
   - `/etc/systemd`, `/usr/lib/systemd`, `/etc/netplan`.
4. `docs/distro-coverage-report.md` phải khớp hoàn toàn với repository hiện tại.

## Những gì gate cố ý không làm

Gate không cố đoán mọi command có portable hay không. Ví dụ một binary có thể tồn tại từ ports/pkg trên FreeBSD dù phổ biến hơn trên Linux; hard-fail theo keyword quá rộng sẽ tạo false positive và làm reviewer mất tín hiệu.

Presence cũng không chứng minh nội dung kỹ thuật là đúng. Reviewer vẫn phải kiểm:

- package name và repository thực tế;
- service name và lifecycle (`systemd` so với `rc.d`);
- config/filesystem paths;
- SELinux/AppArmor khác với FreeBSD security model;
- `nftables`/firewalld khác `pf`/`ipfw`;
- command options/behavior theo man page của đúng HĐH.

Technical review chuẩn tiếp tục nằm tại `docs/technical-review-guide.md`.

## Khi validator fail

Không thêm tên distro chỉ để làm xanh CI. Sửa bài để có hướng dẫn thực sự cho platform bị thiếu.

Nếu FreeBSD block chứa lệnh Linux-only, thay bằng lệnh BSD tương ứng hoặc ghi rõ lệnh đó **không tồn tại / không áp dụng** trên FreeBSD và đưa cách thay thế phù hợp ở ngoài code block.

Nếu report stale sau một thay đổi hợp lệ, chạy:

```bash
python3 tools/distro_coverage.py
```

rồi review diff của report trước khi commit.

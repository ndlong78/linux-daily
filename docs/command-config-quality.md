# Command & Configuration Quality Gate

P7.2 bổ sung static validation cho các code block copy-paste trong Linux Daily. Mục tiêu là chặn anti-pattern nguy hiểm có tín hiệu cao và đưa các ví dụ cần technical review vào một review queue có quy tắc, không thực thi lệnh trong CI.

## Chạy local

```bash
python3 tools/command_quality.py
python3 tools/publish.py check
```

Validator chỉ đọc `posts/post-*.html`; không chạy shell command, không mount disk, không sửa firewall/service và không gọi network.

## Blocker cho mọi bài

Các pattern sau fail ngay cả với bài lịch sử vì không phù hợp làm copy-paste default:

- tải nội dung từ network rồi pipe trực tiếp vào `sh`/`bash`, ví dụ `curl ... | sh`;
- `chmod 777`;
- `rm -rf` nhắm trực tiếp `/`, `/*` hoặc các system root như `/etc`, `/usr`, `/var`, `/boot`, `/home`;
- recursive `chmod -R` / `chown -R` trên các root path tương tự.

Đây là deny-list cố ý hẹp. Validator không cố chứng minh mọi shell command là an toàn.

## Enforcement từ #020

Các bài lịch sử #001–#019 được inventory để review thay vì bị rewrite tự động. Từ #020 trở đi, các finding sau là blocker:

- `sudo echo/printf/cat ... > /etc|/usr|/var/...` vì `sudo` không nâng quyền cho shell redirection;
- `curl -k`, `curl --insecure`, `wget --no-check-certificate`;
- literal credential yếu kiểu `password=password`, `secret=changeme`, `token=123456`;
- destructive storage command không có safety context gần code block.

Safety context được nhận diện bằng các tín hiệu rõ ràng như cảnh báo mất dữ liệu, backup/sao lưu, snapshot, rollback/restore, kiểm tra/xác nhận hoặc lab/test. Đây là guardrail cấu trúc; reviewer vẫn phải đánh giá nội dung thực tế.

## Destructive command inventory

Validator nhận diện có chọn lọc các thao tác có thể thay đổi/xóa dữ liệu, gồm:

- `mkfs.*`, `wipefs` khi không ở no-act mode;
- `dd ... of=/dev/...`;
- `zpool destroy`, `zfs destroy`;
- `lvremove`, `vgremove`, `pvremove`;
- `mdadm --zero-superblock`;
- một số thao tác `parted` như `mklabel`, `mkpart`, `rm`;
- mở `fdisk /dev/...` để thao tác partition table.

Không phải mọi lệnh trong danh sách đều gây mất dữ liệu ngay khi nhập. Mục tiêu là yêu cầu bài mới đặt chúng trong bối cảnh backup/rollback/verification đủ rõ trước khi người đọc copy-paste.

## Historical review queue

Nếu một finding thuộc nhóm enforcement từ #020 nhưng xuất hiện trong #001–#019, CLI sẽ in nó dưới `Historical review queue` và vẫn exit 0. Điều này giữ baseline trung thực và cho phép xử lý debt bằng PR nội dung riêng, thay vì làm P7.2 rewrite hàng loạt lịch sử.

Các blocker cấp repository vẫn fail toàn bộ lịch sử nếu được phát hiện.

## False-positive boundary

P7.2 không:

- chạy ShellCheck trên mọi code block rồi coi tất cả là shell script;
- ép mọi đoạn shell phải có `set -euo pipefail`;
- đoán command nào portable giữa Linux và FreeBSD — việc đó thuộc P7.1 + technical review;
- cấm `sudo` nói chung;
- cấm destructive command nếu bài mới có safety context rõ ràng;
- thay thế review package/service/config semantics theo man page hoặc official documentation.

Technical reviewer tiếp tục dùng `docs/technical-review-guide.md`; distro portability dùng `docs/distro-portability.md`.

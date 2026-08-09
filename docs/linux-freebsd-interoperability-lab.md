# P9.5 — Linux ↔ FreeBSD Interoperability Lab

Mục tiêu của lab là chứng minh một workflow ứng dụng **thật sự chạy qua hai hệ điều hành khác nhau**. Linux và FreeBSD đều chạy nginx trên TCP/8088, sau đó mỗi peer gọi HTTP sang peer còn lại. FreeBSD không được mô phỏng bằng Linux command hoặc Linux path.

> Lab chỉ dành cho hai VM/host riêng trên mạng lab/private. Script yêu cầu `LAB_HOST=YES` và không tự cấu hình firewall. Không chạy trên production hoặc host đang phục vụ nginx thật.

## Topology

```text
+------------------------------+             +------------------------------+
| Linux peer                   |             | FreeBSD peer                 |
| Ubuntu/Xubuntu/Debian/Fedora |             | FreeBSD                      |
| nginx :8088                  | <---------> | nginx :8088                  |
| systemd                      |    HTTP     | rc.d + service(8)            |
| /etc/nginx                   |             | /usr/local/etc/nginx         |
+------------------------------+             +------------------------------+
```

Hai peer cần reach nhau qua một subnet lab riêng. Không dùng địa chỉ production trong ví dụ hoặc commit vào repository.

## Khác biệt bắt buộc phải quan sát

| Lớp | Ubuntu / Xubuntu | Debian | Fedora | FreeBSD |
|---|---|---|---|---|
| Package | `apt-get` | `apt-get` | `dnf` | `pkg` hoặc Ports |
| Service | `systemctl` | `systemctl` | `systemctl` | `service` + rc.d, enable bằng `sysrc` / `/etc/rc.conf` |
| nginx config root | `/etc/nginx` | `/etc/nginx` | `/etc/nginx` | `/usr/local/etc/nginx` |
| Firewall model | thường UFW/nftables | nftables | firewalld | PF hoặc ipfw |
| Log dùng trong lab | `/var/log/nginx/...` | `/var/log/nginx/...` | `/var/log/nginx/...` | `/var/log/nginx/...` theo config lab |

Firewall **không được script tự mở**. Trước lab, operator ghi lại firewall hiện hành bằng công cụ đúng của từng HĐH và chỉ tạo rule tạm theo policy của môi trường lab nếu TCP/8088 đang bị chặn. Mục tiêu P9.5 là kiểm đúng semantics, không thay firewall policy của host thật.

## 1. Chuẩn bị Linux peer

```bash
sudo -i
export LAB_HOST=YES
export PORT=8088
sh labs/p9-linux-freebsd-interoperability/linux-peer.sh setup
```

Script đọc `/etc/os-release`: Ubuntu/Xubuntu và Debian đi nhánh APT; Fedora đi nhánh DNF. Nó backup `nginx.conf` hiện có trước khi ghi config lab, test cấu hình bằng `nginx -t`, sau đó quản lý nginx bằng systemd.

## 2. Chuẩn bị FreeBSD peer

```sh
su -
setenv LAB_HOST YES
setenv PORT 8088
sh labs/p9-linux-freebsd-interoperability/freebsd-peer.sh setup
```

FreeBSD dùng package `nginx`/`curl`, path `/usr/local/etc/nginx`, enable service bằng rc configuration và điều khiển bằng `service nginx ...`. Script kiểm `uname -s` và từ chối chạy nếu host không phải FreeBSD.

## 3. Functional evidence — hai chiều

Trên Linux, gọi sang FreeBSD:

```bash
export LAB_HOST=YES
export PEER_IP='<FREEBSD_LAB_IP>'
sh labs/p9-linux-freebsd-interoperability/linux-peer.sh verify-peer
```

Expected body:

```text
freebsd-peer: linux-daily interoperability ok
```

Trên FreeBSD, gọi sang Linux:

```sh
setenv LAB_HOST YES
setenv PEER_IP '<LINUX_LAB_IP>'
sh labs/p9-linux-freebsd-interoperability/freebsd-peer.sh verify-peer
```

Expected body:

```text
linux-peer: linux-daily interoperability ok
```

Hai probe này là application-level evidence; ping thành công một mình không đủ.

## 4. Observability evidence

Linux:

```bash
systemctl is-active nginx
ss -lnt | grep ':8088'
tail -n 20 /var/log/nginx/linux-daily-interop-access.log
```

FreeBSD:

```sh
service nginx status
sockstat -4 -6 -l | grep ':8088'
tail -n 20 /var/log/nginx/linux-daily-interop-access.log
```

Lưu evidence trước failure injection để có baseline.

## 5. Negative test + recovery — FreeBSD server

Trên FreeBSD:

```sh
setenv LAB_HOST YES
sh labs/p9-linux-freebsd-interoperability/freebsd-peer.sh inject-stop
```

Từ Linux, HTTP probe sang FreeBSD phải fail. Sau đó recovery:

```sh
setenv LAB_HOST YES
sh labs/p9-linux-freebsd-interoperability/freebsd-peer.sh recover
```

Từ Linux chạy lại `verify-peer`; response phải trở lại bình thường.

## 6. Negative test + recovery — Linux server

Trên Linux:

```bash
export LAB_HOST=YES
sh labs/p9-linux-freebsd-interoperability/linux-peer.sh inject-stop
sh labs/p9-linux-freebsd-interoperability/linux-peer.sh recover
```

Từ FreeBSD chạy lại `verify-peer` để chứng minh recovery end-to-end.

## 7. Firewall evidence, không gộp semantics

Chỉ inventory trạng thái và rule hiện hành; không coi các công cụ dưới đây là tương đương cú pháp:

Ubuntu / Xubuntu:

```bash
ufw status verbose
nft list ruleset
```

Debian:

```bash
nft list ruleset
```

Fedora:

```bash
firewall-cmd --state
firewall-cmd --list-all
```

FreeBSD — kiểm tool mà host thực sự dùng:

```sh
pfctl -s info
pfctl -sr
```

hoặc:

```sh
ipfw list
```

Nếu firewall đang default-deny TCP/8088, operator phải tạo **rule tạm chỉ cho peer lab** theo policy của chính firewall đó, ghi lại rule trước/sau, rồi xóa trong cleanup. Lab không cung cấp một lệnh “universal firewall” vì điều đó sẽ che mất khác biệt Linux ↔ FreeBSD mà P9.5 cần kiểm.

## 8. Cleanup / rollback

Linux:

```bash
export LAB_HOST=YES
sh labs/p9-linux-freebsd-interoperability/linux-peer.sh cleanup
```

FreeBSD:

```sh
setenv LAB_HOST YES
sh labs/p9-linux-freebsd-interoperability/freebsd-peer.sh cleanup
```

Cleanup restore `nginx.conf` backup nếu có, xóa document/log của lab và không tự uninstall package. Nếu operator đã thêm firewall rule tạm ở bước riêng, phải xóa rule đó và xác nhận ruleset trở lại baseline.

## CI contract

`labs/p9-linux-freebsd-interoperability/lab.json` là manifest của lab. `tools/interoperability_lab.py` hard-fail khi:

- thiếu Linux hoặc FreeBSD role;
- Linux không bao quát Ubuntu/Xubuntu, Debian, Fedora;
- FreeBSD bị gán systemd/APT/DNF/Linux firewall semantics;
- thiếu package/service/firewall/path difference classes;
- workflow không kiểm cả hai chiều;
- thiếu functional/negative/recovery/observability evidence;
- thiếu private-network/dedicated-host/rollback/cleanup safety flags;
- script khai báo trong manifest không tồn tại.

Validator nằm trong `tools/publish.py check`, vì vậy P9.5 không thể drift khỏi CI contract sau khi phase đóng.

## Nguồn kỹ thuật

- FreeBSD Handbook — Packages and Ports: https://docs.freebsd.org/en/books/handbook/ports/
- FreeBSD Handbook — Configuration, rc.conf và service management: https://docs.freebsd.org/en/books/handbook/config/
- nginx upstream — Installing nginx: https://nginx.org/en/docs/install.html

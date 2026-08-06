---
name: linux-daily
description: >
  Sinh một bài học Linux/Unix system administration bằng tiếng Việt theo nhịp
  2 ngày/bài, xuất ra file HTML sẵn sàng đăng web (đúng phong cách
  reference-001.html), rồi commit vào nhánh claude/ để người dùng duyệt. Dùng
  skill này khi routine "Linux Daily" chạy, hoặc khi người dùng yêu cầu tạo bài
  mới. Luôn bao quát Ubuntu, Xubuntu, Debian, Fedora, FreeBSD; xoay trục tuần tự
  theo số bài.
---

# Linux Daily — sinh bài học theo nhịp 2 ngày (repo + cloud routine)

Chạy trong một repo đã được clone. Khung chuẩn của bài là
`templates/post.template.html`; CSS chung của cả site là `assets/style.css`
(**KHÔNG sửa** khi tạo bài — đây là template cố định của dự án). Bài viết ra thư
mục `posts/` ở gốc repo. Nhật ký chủ đề là `topics.md` ở gốc repo. Ví dụ một bài
đã điền đầy đủ: `posts/post-001-static-ip.html`.

## Bước 0 — Cổng nhịp 2 ngày (kiểm tra TRƯỚC)
Đọc `topics.md` ở gốc repo, lấy ngày của bài mới nhất.
- Nếu bài mới nhất cách hôm nay **dưới 2 ngày**: DỪNG, không tạo gì, không commit.
  Ghi một dòng log ngắn "Chưa đến nhịp, bỏ qua hôm nay" rồi kết thúc.
- Nếu **≥ 2 ngày** (hoặc `topics.md` chỉ có mỗi #001 và đã qua ≥ 2 ngày): tiếp tục.

Nhờ cổng này, routine cứ đặt chạy **Daily** là đủ — skill tự giữ nhịp 2 ngày/bài
và tự bù nếu lỡ một hôm.

## Bước 1 — Xác định số bài và trục
- Số bài kế tiếp = (số dòng bài trong `topics.md`) + 1. Ví dụ có #001 → tạo #002.
- Trục xoay **tuần tự theo số bài** (không theo thứ), lấy theo chu kỳ 7:

  `index = (số_bài − 1) mod 7`

  | index | Trục |
  |-------|------|
  | 0 | Networking (interface, routing, DNS, firewall, VPN, ss/ip/tcpdump) |
  | 1 | Bảo mật & phân quyền (users, sudo, SSH hardening, SELinux/AppArmor, pf, fail2ban) |
  | 2 | Storage & hệ thống tệp (LVM, ZFS, mount, RAID, quota, backup) |
  | 3 | Giới thiệu một phần mềm/công cụ mới hữu ích (server hoặc CLI) |
  | 4 | Monitoring & hiệu năng (log, journald, top/htop, tuning, cron/timers) |
  | 5 | Automation & scripting (bash nâng cao, Ansible, cấu hình lặp lại) |
  | 6 | Ôn tập — một bài lab nhỏ end-to-end |

  (#001 là Networking → index 0. #002 sẽ là index 1 = Bảo mật, v.v.)

## Bước 2 — Chọn chủ đề, tránh trùng
Chọn một chủ đề cụ thể, thực dụng, đúng trục, và KHÔNG trùng bất kỳ dòng nào
trong `topics.md`.

## Bước 3 — Soạn nội dung
Theo "Quy tắc nội dung" bên dưới. Tiếng Việt, giọng chuyên nghiệp, súc tích.

## Bước 4 — Xuất file HTML
- Copy `templates/post.template.html` thành `posts/post-<số>-<slug>.html` rồi điền
  các placeholder `{{...}}` (tiêu đề, ISSUE, DATE, trục, lede, độ khó, thời lượng,
  hashtag, hai SVG + figcaption, các mục nội dung).
- **KHÔNG** thêm CSS nội tuyến và **KHÔNG** sửa `assets/style.css`. Trang phải giữ
  hai dòng liên kết `../assets/style.css`, `../index.html` và `<body class="post">`
  cùng hai link "về trang chủ" (header `.brand-home`, footer `.foot-home`) như trong
  template.
- Vẽ HAI ảnh SVG cho chủ đề mới (xem "Quy tắc ảnh minh hoạ"). Xem
  `posts/post-001-static-ip.html` để biết mức chi tiết mong muốn.
- Lưu vào `posts/post-<số>-<slug-không-dấu>.html`
  (ví dụ `posts/post-004-...html`).

## Bước 4b — Xuất khối Facebook & X (+ ảnh code)
Tạo thư mục `posts/social/` nếu chưa có, rồi sinh ba thứ cho bài:

1. **Ảnh code** `posts/social/post-<số>-code.png`: chọn khối lệnh cô đọng nhất
   (~4–7 dòng, tinh thần "bốn HĐH so sánh" hoặc block quan trọng nhất), lưu ra
   file tạm rồi chạy:
   `python3 tools/render_code.py --in <file_tạm> --out posts/social/post-<số>-code.png --title "Linux Daily #<số> · <chủ đề ngắn>"`
   Nếu render lỗi, vẫn tiếp tục và ghi chú trong file FB/X "chèn ảnh code thủ công".

2. **Facebook** `posts/social/post-<số>-facebook.txt`: caption ~150–200 từ,
   giọng cuốn, mở đầu bằng một câu móc + emoji nhẹ, thân bài nêu điểm khác biệt
   4 HĐH bằng gạch đầu dòng (KHÔNG dán lệnh thô — FB không có monospace, để lệnh
   trong ảnh), chốt bằng `👉 {{LINK}}`, 4–6 hashtag, dòng cuối
   `[Đính kèm ảnh: post-<số>-code.png]`.

3. **X** `posts/social/post-<số>-x.txt`: thread 5–7 tweet đánh dấu `[Tweet n]`,
   mỗi tweet ≤ 280 ký tự, một ý/một HĐH mỗi tweet. Tweet 1 có móc + ghi
   "đính kèm post-<số>-code.png"; FreeBSD luôn có một tweet riêng; tweet cuối là
   `{{LINK}}` + hashtag. Lệnh ngắn có thể để inline, lệnh dài để trong ảnh.

`{{LINK}}` là placeholder để người dùng thay bằng URL bài trên website.

## Bước 5 — Ghi nhật ký & dựng lại trang chủ
Thêm dòng vào `topics.md`:
`#<số> | <YYYY-MM-DD> | <trục> | <tên chủ đề>`

**Ngày phải là ngày chạy thực tế (hôm nay)** và **không được nhỏ hơn** ngày của
bài trước đó — validator sẽ chặn nếu lùi ngày (backdate). `<YYYY-MM-DD>` trong
`topics.md` và ngày `DD·MM·YYYY` hiển thị trong HTML bài phải khớp nhau.

Rồi dựng lại trang chủ để nó liệt kê bài mới:
`python3 tools/build_index.py`   (cập nhật `index.html` ở gốc repo)

## Bước 5b — Kiểm định trước khi commit (BẮT BUỘC)
Chạy quality gate; **không commit nếu còn lỗi** — sửa cho đến khi sạch:

```
python3 tools/validate_repo.py     # số bài liên tục, trục đúng chu kỳ, ngày hợp lệ,
                                    # 2 SVG + aria, đủ 7 mục, khối FreeBSD, tweet ≤ 280…
python3 tools/build_index.py --check   # index.html đã dựng lại chưa
```

CI cũng chạy đúng các lệnh này trên PR (xem `.github/workflows/ci.yml`), nên đây
là cùng một cổng chất lượng — chạy trước để khỏi phải sửa vòng hai.

## Bước 6 — Commit (KHÔNG tự đăng)
- Tạo/chuyển sang nhánh `claude/linux-daily-<YYYY-MM-DD>`.
- `git add` file bài mới trong `posts/`, thư mục `posts/social/`, `index.html`
  (trang chủ vừa dựng lại) và `topics.md`.
- Commit message: `Linux Daily #<số>: <tên chủ đề>`.
- Push nhánh đó (chỉ nhánh tiền tố `claude/`). KHÔNG push thẳng vào `main`.
- Mở Pull Request nếu connector GitHub cho phép; nếu không, chỉ để lại nhánh để
  người dùng tự tạo PR và merge.

## Bước 7 — Bàn giao
Báo ngắn gọn: số bài, chủ đề, đường dẫn file, tên nhánh. Nhắc: đọc lướt phần lệnh
trước khi merge/đăng.

---

## Quy tắc nội dung (BẮT BUỘC)

**Phạm vi HĐH — luôn nêu rõ khác biệt:**
- Ubuntu / Xubuntu (APT, systemd, netplan, UFW/nftables)
- Debian (APT, systemd, `/etc/network/interfaces`)
- Fedora (DNF, systemd, SELinux, NetworkManager/`nmcli`, firewalld)
- FreeBSD (pkg/ports, rc.d — **KHÔNG** systemd/NetworkManager; cấu hình `rc.conf`;
  firewall pf/ipfw; tên interface theo driver em0/igb0/re0/vtnet0)

**Xử lý FreeBSD riêng.** Không gán `systemctl`/`apt`/`dnf`/`nmcli`/`netplan` cho
FreeBSD; dùng `service`, `pkg`, `sysrc`, `ifconfig`, `netstat -rn`... Nếu không có
bản tương đương, nói rõ.

**Độ chính xác trên hết.** Không chắc thì nêu điều kiện/gói cần có, đừng bịa. Ưu
tiên cú pháp hiện hành (Ubuntu `routes:` thay `gateway4:`; Fedora `nmcli` thay
file `ifcfg-*` đã bỏ).

**Quy ước hạ tầng.** DNS và DHCP relay luôn khai đủ **cặp** (hai địa chỉ); cấu
hình một địa chỉ bị coi là lỗi và phải nêu rõ.

**Cấu trúc 7 mục (như reference-001, đánh số 01–07):**
1. Bối cảnh thực tế
2. Kiến thức cốt lõi
3. Cấu hình/thao tác từng HĐH — mỗi HĐH một khối code có nhãn; FreeBSD tách riêng
   (nhãn + viền đỏ)
4. Kiểm chứng (Linux vs FreeBSD)
5. Cạm bẫy thường gặp + cách xử lý
6. Lưu ý bảo mật & vận hành
7. Bài tập tự luyện

Lệnh trong `<pre><code>`, chú thích dùng `<span class="cmt">`.

## Quy tắc ảnh minh hoạ (SVG gốc, vẽ mới mỗi bài)
Giữ ngôn ngữ hình ảnh của reference-001: nét blueprint line-art, nền lưới mờ; teal
`#0C6E61` cho Linux, đỏ `#B23A2E` cho FreeBSD; nhãn số liệu dùng `JetBrains Mono`,
tiêu đề box dùng `Be Vietnam Pro`.
- **Hình 1 (hero):** sơ đồ khái niệm của chủ đề. Có DNS/DHCP thì vẽ theo cặp.
- **Hình 2 (so sánh):** dải 4 cột Ubuntu/Xubuntu · Debian · Fedora · FreeBSD;
  cột FreeBSD tô đỏ, tách khỏi ba cột kia.
Mỗi `<figure>` có `role="img"` + `aria-label` + `<figcaption>`.

## Không được
- Sửa `assets/style.css` khi tạo bài (đó là template cố định của cả site).
- Dùng ảnh có bản quyền — chỉ SVG gốc.
- Push vào `main` hoặc tự đăng lên website.
- Lặp chủ đề đã có trong `topics.md`.
- Tạo bài khi chưa đủ nhịp 2 ngày (xem Bước 0).

## Series conventions
Đánh số liên tục; footer giữ `#LinuxDaily #SysAdmin` + một hashtag theo chủ đề.

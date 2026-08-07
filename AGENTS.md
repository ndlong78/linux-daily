# Linux Daily — Agent Operating Contract

Tài liệu này là **nguồn quy tắc vận hành chính** cho mọi AI agent làm việc với repository `ndlong78/linux-daily`, bao gồm ChatGPT Scheduled Task và các phiên ChatGPT tương tác.

## 1. Nguyên tắc vận hành

- `main` là nguồn sự thật của nội dung đã chấp nhận.
- Không push trực tiếp vào `main`.
- Bài mới đi qua branch → Pull Request → GitHub Actions → người dùng review/merge.
- `state.json` là nguồn sự thật của cadence; `topics.md` là lịch sử nội dung, không dùng làm clock vận hành.
- Không tự ý commit/push/mở PR/merge nếu phiên làm việc chưa có quyền ghi GitHub rõ ràng của người dùng cho hành động tương ứng.
- Scheduled Task chỉ chuẩn bị và kiểm tra; khi cần remote write mà chưa có quyền, báo người dùng để phê duyệt trong chat.

## 2. Cổng cadence 2 ngày

Trước khi tạo bài:

```bash
python3 tools/cadence.py gate
```

- exit `10`: chưa tới nhịp → dừng, không tạo file, không sửa state.
- exit `0`: tới nhịp → tiếp tục.

Số bài kế tiếp:

```bash
python3 tools/cadence.py next
```

Trước khi sinh bài, kiểm tra GitHub xem đã có branch/PR cho đúng số bài kế tiếp chưa. Prefix chuẩn mới là:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Trong giai đoạn chuyển đổi, phải coi cả prefix legacy sau là trùng để tránh hai agent cùng sinh một bài:

```text
claude/linux-daily-<NNN>-<YYYYMMDD>
```

Nếu đã có branch hoặc PR mở cho số bài đó, dừng và báo trạng thái thay vì tạo bản thứ hai.

## 3. Chu kỳ chủ đề

Trục xoay theo số bài, chu kỳ 7:

| `(issue - 1) mod 7` | Trục |
|---:|---|
| 0 | Networking |
| 1 | Bảo mật & phân quyền |
| 2 | Storage & hệ thống tệp |
| 3 | Công cụ/phần mềm mới |
| 4 | Monitoring & hiệu năng |
| 5 | Automation & scripting |
| 6 | Ôn tập — lab end-to-end |

Luôn kiểm tra `topics.md` để tránh trùng chủ đề đã có.

## 4. Phạm vi hệ điều hành

Mỗi bài phải nêu rõ khác biệt giữa:

- Ubuntu / Xubuntu: APT, systemd, netplan, UFW/nftables.
- Debian: APT, systemd, cấu hình mạng/phần mềm phù hợp Debian hiện hành.
- Fedora: DNF, systemd, SELinux, NetworkManager/`nmcli`, firewalld.
- FreeBSD: pkg/ports, rc.d, `rc.conf`, pf/ipfw, công cụ BSD tương ứng.

**FreeBSD luôn tách riêng.** Không gán `systemctl`, `apt`, `dnf`, `nmcli`, `netplan` cho FreeBSD. Nếu không có tương đương, nói rõ.

Ưu tiên độ chính xác. Với claim phụ thuộc phiên bản hoặc có thể thay đổi, kiểm tra tài liệu chính thức hiện hành trước khi chốt.

## 5. Cấu trúc bài

Dùng `templates/post.template.html` và giữ `assets/style.css` làm CSS chung. Mỗi bài có đúng 7 mục:

1. Bối cảnh thực tế
2. Kiến thức cốt lõi
3. Cấu hình/thao tác từng HĐH
4. Kiểm chứng
5. Cạm bẫy + cách xử lý
6. Bảo mật & vận hành
7. Bài tập tự luyện

Mỗi bài phải có:

- đúng 2 SVG nguyên bản;
- `role="img"`, `aria-label`, `figcaption` đầy đủ;
- khối FreeBSD riêng;
- 2 link về trang chủ;
- metadata JSON `<script id="ld-meta">` trong `<head>`.

Metadata phải khớp filename, `topics.md` và nội dung hiển thị:

- `issue`
- `date`
- `axis`
- `slug`
- `eyebrow`
- `title`
- `lede`

Ngày bài mặc định là ngày chạy thực tế. Không backdate để vượt cadence.

## 6. Social output

Mỗi bài sinh:

- `posts/social/post-<NNN>-facebook.txt`
- `posts/social/post-<NNN>-x.txt`
- `posts/social/post-<NNN>-code.png`

Facebook: khoảng 150–200 từ, có `{{LINK}}`, 4–6 hashtag và ghi chú ảnh code.

X: thread 5–7 tweet, `[Tweet 1] ... [Tweet N]`, đánh số liên tục, mỗi tweet ≤ 280 ký tự theo validator; FreeBSD có tweet riêng; tweet cuối chứa `{{LINK}}` + hashtag.

## 7. Ghi state và build

Sau khi nội dung hoàn chỉnh:

```bash
python3 tools/build_index.py
python3 tools/cadence.py record
python3 tools/build.py --check
```

Không commit nếu `build.py --check` chưa sạch.

`state.json` phải khớp bài mới nhất trong `topics.md` và `last_generated_at` phải phản ánh thời điểm sinh thực tế.

## 8. Git workflow

Branch chuẩn:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Chỉ stage đúng file thuộc bài đang làm:

- `posts/post-<NNN>-<slug>.html`
- `posts/social/post-<NNN>-facebook.txt`
- `posts/social/post-<NNN>-x.txt`
- `posts/social/post-<NNN>-code.png`
- `index.html`
- `topics.md`
- `state.json`

Không stage cả thư mục bằng `git add .`, `git add -A` hoặc `git add posts/social/`.

Commit message:

```text
Linux Daily #<NNN>: <tên chủ đề>
```

Mở PR vào `main`; CI `quality-gate` phải xanh trước khi merge.

## 9. Scheduled Task của ChatGPT

Task có thể chạy hằng ngày, nhưng cadence vẫn do `state.json` quyết định. Khi chưa tới nhịp, không tạo bài. Khi tới nhịp, task kiểm tra state, issue kế tiếp, duplicate branch/PR, chuẩn bị gói bài và báo người dùng nếu cần quyền remote write.

Task không thay thế GitHub Actions. GitHub Actions là cổng kỹ thuật cuối cùng; người dùng là người quyết định merge.

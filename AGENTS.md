# Linux Daily — Agent Operating Contract

Tài liệu này là **nguồn quy tắc vận hành chính** cho mọi AI agent làm việc với repository `ndlong78/linux-daily`, bao gồm ChatGPT Scheduled Task và các phiên ChatGPT tương tác.

## 1. Nguyên tắc vận hành

- `main` là nguồn sự thật của nội dung đã chấp nhận.
- Không push trực tiếp vào `main`.
- Bài mới đi qua branch → Pull Request → GitHub Actions → người dùng review/merge.
- `state.json` là nguồn sự thật của cadence; `topics.md` là lịch sử nội dung, không dùng làm clock vận hành.
- Không tự ý commit/push/mở PR/merge nếu phiên làm việc chưa có quyền ghi GitHub rõ ràng của người dùng cho hành động tương ứng.
- Scheduled Task chỉ chuẩn bị và kiểm tra; khi cần remote write mà chưa có quyền, báo người dùng để phê duyệt trong chat.
- Từ bài **#019**, mọi claim/lệnh kỹ thuật chính phải có nguồn official/upstream kiểm chứng được.

## 2. Cổng cadence hằng ngày

Linux Daily phát hành mặc định **1 bài/ngày**. Trước khi tạo bài:

```bash
python3 tools/cadence.py gate
```

- exit `10`: bài hôm nay chưa tới nhịp → dừng, không tạo file, không sửa state.
- exit `0`: đã sang ngày phát hành kế tiếp → tiếp tục.

Số bài kế tiếp:

```bash
python3 tools/cadence.py next
```

Trước khi sinh bài, kiểm tra GitHub xem đã có branch/PR cho đúng số bài kế tiếp chưa. Prefix chuẩn:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Trong giai đoạn chuyển đổi, coi cả prefix legacy sau là trùng:

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

Luôn kiểm tra `topics.md` để tránh trùng chủ đề đã có. Khi phù hợp, bài mới nên nối progression/prerequisite từ các bài trước thay vì trở thành một tip rời rạc.

## 4. Phạm vi hệ điều hành

Mỗi bài phải nêu rõ khác biệt giữa:

- Ubuntu / Xubuntu: APT, systemd, netplan, UFW/nftables.
- Debian: APT, systemd, cấu hình phù hợp Debian hiện hành.
- Fedora: DNF, systemd, SELinux, NetworkManager/`nmcli`, firewalld.
- FreeBSD: pkg/ports, rc.d, `rc.conf`, pf/ipfw, công cụ BSD tương ứng.

**FreeBSD luôn tách riêng.** Không gán `systemctl`, `apt`, `dnf`, `nmcli`, `netplan` cho FreeBSD. Nếu không có tương đương, nói rõ.

## 5. Source-backed technical review — bắt buộc từ #019

Trước khi chốt bài, kiểm tra các claim phụ thuộc phiên bản hoặc có rủi ro vận hành bằng tài liệu **official/upstream hiện hành**. Ưu tiên theo thứ tự:

1. upstream project/vendor documentation;
2. Ubuntu/Debian/Fedora/FreeBSD documentation và manpages chính thức;
3. tài liệu chính thức của package/tool đang được giới thiệu.

Mỗi bài #019+ phải có ít nhất **2 nguồn primary** và metadata:

```json
{
  "review_status": "reviewed",
  "sources": [
    {"title": "Tên tài liệu", "url": "https://...", "kind": "official"},
    {"title": "Tên upstream", "url": "https://...", "kind": "upstream"}
  ]
}
```

Quy tắc nguồn:

- `url` phải là HTTPS đầy đủ và không trùng nhau.
- `kind` chỉ dùng `official` hoặc `upstream` trong gate hiện tại.
- Title + URL + thứ tự trong `meta.sources` phải khớp phần **Nguồn kỹ thuật** hiển thị.
- `review_status="draft"` không được qua merge gate; sau khi đã kiểm chứng nguồn/lệnh, đặt `reviewed`. `published` dành cho nội dung đã đi qua lifecycle xuất bản.
- Không dùng blog SEO, forum hay AI-generated page làm bằng chứng chính cho lệnh hệ thống.

Checklist bắt buộc với nội dung rủi ro cao:

- **Networking/firewall:** interface, port, default policy, IPv4/IPv6, rollback/remote-lockout.
- **Storage/filesystem:** device/path, destructive flags, resize direction, backup/restore path.
- **Backup/restore:** phải nêu cách kiểm chứng restore, không chỉ backup command.
- **Auth/permissions:** account scope, sudo/root impact, cách giữ đường lui khi hardening.
- **Automation/shell:** shell thực thi, exit-code semantics, quoting, PATH và portability.

Bài #001–#018 được grandfather về mặt validator; việc backfill nguồn lịch sử làm theo PR riêng, không được dùng grandfather để sao chép claim cũ sang bài mới mà không kiểm chứng.

## 6. Cấu trúc bài

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
- metadata JSON `<script id="ld-meta">` trong `<head>`;
- từ #019: `review_status`, `sources`, và `<section class="sources">` không đánh số.

Metadata cơ bản phải khớp filename, `topics.md` và nội dung hiển thị: `issue`, `date`, `axis`, `slug`, `eyebrow`, `title`, `lede`.

Ngày bài mặc định là ngày chạy thực tế. Không backdate để vượt cadence.

## 7. Social output — tạm dừng

Từ khi áp dụng cadence hằng ngày, **không tạo mới nội dung Facebook/X hoặc ảnh code social theo mặc định**. Mục tiêu là giảm khối lượng generation/review và tập trung vào chất lượng bài học + source-backed technical review.

Các file lịch sử trong `posts/social/` được giữ nguyên để bảo toàn lịch sử repository. Không xóa hoặc rewrite chỉ vì social output đang tạm dừng.

Nếu sau này bật lại social publishing, phải làm bằng một PR riêng để khôi phục contract, validator và workflow tương ứng.

## 8. Ghi state và build

Sau khi nội dung hoàn chỉnh:

```bash
python3 tools/build_index.py
python3 tools/cadence.py record
python3 tools/build.py --check
```

`tools/build.py --check` chạy quality gate cấu trúc và **source-backed gate**. Social artifact không còn là điều kiện merge cho bài mới.

`state.json` phải khớp bài mới nhất trong `topics.md` và `last_generated_at` phải phản ánh thời điểm sinh thực tế.

## 9. Git workflow

Branch chuẩn:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Chỉ stage đúng file thuộc bài đang làm, thông thường gồm:

- `posts/post-<NNN>-<slug>.html`
- `index.html` và các generated site artifact do build thay đổi
- `topics.md`
- `state.json`
- learning metadata/path nếu bài mới yêu cầu

Không stage cả thư mục bằng `git add .`, `git add -A` hoặc `git add --all`.

Commit message:

```text
Linux Daily #<NNN>: <tên chủ đề>
```

Mở PR vào `main`; CI `quality-gate` phải xanh trước khi merge.

### Self-fix CI completion contract

Một PR **chưa được coi là hoàn tất** chỉ vì local test pass hoặc một workflow run cũ đã xanh. Sau **mỗi lần push** vào branch PR, agent bắt buộc:

1. đọc lại PR và lấy đúng `head_sha` hiện tại;
2. kiểm tra toàn bộ workflow/check gắn với **chính SHA đó**, gồm cả trigger `push` và `pull_request`;
3. coi `queued`, `pending`, `in_progress`, `failure`, `cancelled` hoặc `timed_out` là **chưa hoàn tất**;
4. nếu có check đỏ, đọc log job lỗi, sửa nguyên nhân gốc, chạy lại generator deterministic + local gates, push và lặp lại từ bước 1;
5. trước khi báo sẵn sàng review, kiểm tra diff PR không còn workflow/helper/artifact chẩn đoán tạm;
6. chỉ được báo **ready for review** khi tất cả required checks của exact `head_sha` đã `completed/success`.

Không được skip, suppress, nới lỏng hoặc bypass gate để làm CI xanh. Nếu connector không hiển thị đủ check, trạng thái phải được coi là **chưa xác minh**, không được suy đoán là PASS.

## 10. Scheduled Task của ChatGPT

Task chạy hằng ngày lúc 07:00. Cadence do `state.json` quyết định với mặc định **1 ngày**. Khi chưa sang ngày phát hành kế tiếp, không tạo bài. Khi tới nhịp, task kiểm tra state, issue kế tiếp, duplicate branch/PR, chuẩn bị bài, source-backed review và quality gates.

Task không tạo Facebook/X theo mặc định trong giai đoạn social output tạm dừng.

Task không thay thế GitHub Actions. GitHub Actions là cổng kỹ thuật cuối cùng; người dùng là người quyết định merge.

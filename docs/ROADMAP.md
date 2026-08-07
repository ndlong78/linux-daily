# Linux Daily — Đánh giá & Lộ trình cải thiện

Tài liệu này ghi lại đánh giá tổng thể dự án và lộ trình PR để nâng độ tin cậy khi
vận hành routine tự động. Cập nhật khi hoàn thành từng mốc.

> **Ghi chú đánh số PR:** lộ trình bên dưới đặt tên các mốc theo "PR #13…#16" từ
> đợt đánh giá đầu. Trên thực tế các số PR #15–#18 đã bị **bài nội dung** dùng
> (xem `git log`), nên các mốc pipeline chưa làm sẽ mang số PR mới khi thực hiện —
> tên "PR #14/#15/#16" ở đây chỉ là nhãn mốc, không phải số PR thật.

## Điểm tổng thể: 7,5/10 _(cập nhật 2026-08-07)_

Đợt đánh giá đầu chấm 6,8/10 khi chưa có quality gate. Sau khi CI gate + test đi vào
vận hành (và được siết thêm ở phần kiểm định social), điểm nâng lên **7,5/10**.

| Hạng mục | Điểm | Nhận xét |
|---|---|---|
| Kiến trúc | 8/10 | Nhỏ gọn, static, ít bề mặt tấn công |
| Giao diện & accessibility | 8/10 | Responsive, semantic tương đối tốt |
| Tự động hóa | 6/10 | Quy trình rõ nhưng trạng thái chưa đáng tin |
| Kiểm thử & CI | 2/10 → **8/10** | Quality gate + test + CI đã vận hành, 44 test xanh |
| Khả năng bảo trì | 6/10 | Có template nhưng vẫn phụ thuộc HTML + regex |
| An toàn nội dung kỹ thuật | 5,5/10 | Nội dung tốt nhưng chưa có nguồn & kiểm chứng lệnh |
| Bảo mật repository | 6,5/10 | Static site an toàn, agent workflow còn thiếu rào chắn |

## Lộ trình PR

### PR #13 — CI Quality Gate ✅ (đã merge)
- [x] `pyproject.toml` với dependency được pin (Pillow) + dev tools (ruff, pytest).
- [x] `tools/validate_repo.py`: số bài liên tục, trục đúng chu kỳ 7, ngày ISO hợp lệ
      & **không giảm dần** (bắt lỗi lệch lịch), khớp số bài/ngày giữa filename ↔ HTML ↔
      `topics.md`, không còn placeholder, đúng 2 SVG (role+aria), đủ 7 mục, khối FreeBSD,
      link CSS/trang chủ, mỗi tweet ≤ 280 ký tự, social đủ file.
- [x] `tools/build_index.py --check`: phát hiện `index.html` chưa đồng bộ.
- [x] Test cho `build_index`, `validate_repo`, `render_code` (smoke).
- [x] GitHub Actions chạy ruff + pytest + validator + `--check` + smoke render trên mọi PR.
- [x] Hardening `render_code.py`: wrap dòng, `--max-cols/--max-lines`, báo lỗi file rỗng,
      thông báo font thân thiện, sửa khoảng trắng code↔comment.
- [x] Sửa dữ liệu seed lệch ngày trong `topics.md` (#005–#007) về đúng ngày commit thật,
      khôi phục thứ tự thời gian không giảm.
- [ ] Cấu hình branch protection: bắt buộc job `quality-gate` xanh mới merge (thao tác
      trên GitHub Settings — nằm ngoài repo).

### Siết kiểm định social (đợt review 2026-08-07)
- [x] Đếm độ dài tweet theo cách X đếm: mỗi `{{LINK}}` tính **23 ký tự** (t.co) thay vì
      độ dài thô 8 — tránh "đạt" nhầm tweet thực chất vượt 280 sau khi thay link
      (`tweet_length`). *(khuyến nghị 1 — đã merge ở PR #19)*
- [x] `parse_tweets` + `validate_social` siết cấu trúc thread X theo `SKILL.md`:
      không có nội dung trước `[Tweet 1]`, số lượng tweet trong **5–7**, đánh số
      **liên tục 1..N**. *(khuyến nghị 2)*
- [x] Test cho `tweet_length`, `parse_tweets`, và các nhánh lỗi mới (44 test tổng).

### PR #14 — Cadence State & Idempotency (kế tiếp)
- [x] `state.json` (`last_issue`, `last_generated_at`, `last_published_date`); quyết định
      chạy dựa vào `last_generated_at`, không dựa ngày AI ghi trong bài. → `tools/cadence.py`.
- [x] Chống hai tiến trình cùng sinh một số bài (SKILL Bước 0 kiểm tra branch/PR đang mở).
- [x] Ngày bài mặc định = ngày chạy thực; validator chặn backdate. *(cờ `--backfill` chưa
      thêm — backfill làm tay khi cần.)*
- [x] Branch chứa số issue rõ ràng: `claude/linux-daily-<NNN>-<YYYYMMDD>`.
- [x] Stage chính xác từng file mới, không `git add posts/social/` cả thư mục.

### PR #15 — Structured Content Pipeline ✅
- [x] Chuyển metadata bài sang JSON front matter (`<script id="ld-meta">` trong `<head>`).
- [x] Tách `templates/index.template.html`; render bằng Jinja2; bỏ parse HTML bằng regex
      (đọc meta & text hiển thị qua `tools/postmeta.py` dùng `html.parser`).
- [x] Một lệnh build duy nhất: `python3 tools/build.py` (dựng index + quality gate).

### PR #16 — Source-backed Technical Review
- [ ] Mỗi bài có mục **Nguồn kỹ thuật** (≥ 2 nguồn chính thức: Ubuntu/Debian/Fedora/FreeBSD/upstream).
- [ ] Validator yêu cầu tối thiểu 2 nguồn; checklist kiểm tra lệnh.
- [ ] Trạng thái bài: `draft` → `reviewed` → `published`.
- [ ] Đính chính các khẳng định quá tuyệt đối (ví dụ `#!/usr/bin/env bash` phụ thuộc PATH;
      dùng `command -v` thay `which`; `IFS=$'\n\t'` toàn cục không phải mặc định; `set -e`
      có ngoại lệ; `rm -rf /` và cơ chế `--preserve-root`).

## P2 — Hoàn thiện repository & website (rải rác)
LICENSE · CONTRIBUTING.md · SECURITY.md · RSS/Atom · sitemap.xml · canonical URL ·
Open Graph/social metadata · kiểm tra broken link · tự host font · skip link tới nội
dung chính · alt/mô tả rõ hơn cho sơ đồ phức tạp.

# Linux Daily — Đánh giá & Lộ trình cải thiện

Tài liệu này ghi lại đánh giá tổng thể dự án và lộ trình PR để nâng độ tin cậy khi
vận hành routine tự động. Cập nhật khi hoàn thành từng mốc.

## Điểm tổng thể (thời điểm đánh giá): 6,8/10

| Hạng mục | Điểm | Nhận xét |
|---|---|---|
| Kiến trúc | 8/10 | Nhỏ gọn, static, ít bề mặt tấn công |
| Giao diện & accessibility | 8/10 | Responsive, semantic tương đối tốt |
| Tự động hóa | 6/10 | Quy trình rõ nhưng trạng thái chưa đáng tin |
| Kiểm thử & CI | 2/10 → **cải thiện ở PR này** | Trước đây chưa có quality gate thực sự |
| Khả năng bảo trì | 6/10 | Có template nhưng vẫn phụ thuộc HTML + regex |
| An toàn nội dung kỹ thuật | 5,5/10 | Nội dung tốt nhưng chưa có nguồn & kiểm chứng lệnh |
| Bảo mật repository | 6,5/10 | Static site an toàn, agent workflow còn thiếu rào chắn |

## Lộ trình PR

### PR #13 — CI Quality Gate ✅ (PR này)
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

### PR #14 — Cadence State & Idempotency (kế tiếp)
- [ ] `state.json` (`last_issue`, `last_generated_at`, `last_published_date`); quyết định
      chạy dựa vào `last_generated_at`, không dựa ngày AI ghi trong bài.
- [ ] Chống hai tiến trình cùng sinh một số bài (kiểm tra branch/PR đang mở cho issue kế).
- [ ] Ngày bài mặc định = ngày chạy thực; không backdate trừ khi có `--backfill`.
- [ ] Branch chứa số issue rõ ràng: `claude/linux-daily-<NNN>-<YYYYMMDD>`.
- [ ] Stage chính xác từng file mới, không `git add posts/social/` cả thư mục.

### PR #15 — Structured Content Pipeline
- [ ] Chuyển metadata bài sang YAML/JSON front matter.
- [ ] Tách `templates/index.template.html`; render bằng Jinja2; bỏ parse HTML bằng regex.
- [ ] Một lệnh build duy nhất (`python -m linux_daily build`).

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

# Linux Daily — Lộ trình cải thiện

Tài liệu này ghi lại các mốc nâng độ tin cậy của pipeline Linux Daily. Tên PR lịch sử có thể không trùng số Pull Request thực tế vì một số số PR đã được bài nội dung sử dụng.

## Trạng thái nền tảng hiện tại

- Static site + CSS chung: ✅
- CI quality gate trên GitHub Actions: ✅
- Ruff/Pytest/validator/build check: ✅
- Social validator (thread X, độ dài URL t.co): ✅
- Cadence qua `state.json`: ✅
- Idempotency/duplicate check ở agent workflow: ✅
- Structured metadata + Jinja2 index pipeline: ✅
- ChatGPT Plus Scheduled Task làm scheduler chính: ✅
- Source-backed technical review cho bài mới (#019+): ✅ PR #24
- Backfill nguồn cho bài lịch sử #001–#018: ⏳ mốc riêng

## Các mốc đã hoàn thành

### CI Quality Gate ✅

- `pyproject.toml` pin dependency + dev tools.
- `tools/validate_repo.py` kiểm tra numbering, axis cycle, date/meta consistency, template structure, SVG/accessibility, FreeBSD block, social output và state.
- `tools/build.py --check` làm cổng build/validation thống nhất.
- `.github/workflows/ci.yml` chạy lint, tests, validator/build và smoke tests trên PR.
- `tools/render_code.py` được hardening cho input/font/wrap/size.

### Social validation ✅

- `{{LINK}}` được tính theo độ dài t.co khi kiểm tra X.
- Thread X bắt buộc 5–7 tweet, đánh số liên tục, không có nội dung lạc trước `[Tweet 1]`.
- Facebook/X/code image được kiểm tra theo contract của repo.

### Cadence State & Idempotency ✅

- `state.json` chứa `last_issue`, `last_generated_at`, `last_published_date`.
- `tools/cadence.py` quyết định cadence từ `last_generated_at`, không dựa ngày do bài tự ghi.
- Validator buộc state khớp bài mới nhất.
- Agent phải kiểm tra branch/PR trùng cho issue kế tiếp.
- Prefix branch chuẩn:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

- Prefix legacy `claude/linux-daily-...` chỉ còn được đọc để phát hiện duplicate trong giai đoạn chuyển đổi.

### Structured Content Pipeline ✅

- Mỗi bài có JSON metadata `<script id="ld-meta">`.
- `tools/postmeta.py` đọc metadata/text bằng parser thay vì regex brittle.
- `templates/index.template.html` + Jinja2 dựng trang chủ.
- `tools/build.py` là entrypoint build/quality gate chính.

### Migration Claude Routine → ChatGPT Plus ✅

- PR #23 đã merge 2026-08-07.
- `AGENTS.md` là hợp đồng vận hành AI chính trong repository.
- `docs/CHATGPT-OPERATIONS.md` mô tả scheduler, quyền ghi GitHub và failure/rollback path.
- Scheduled Task `Linux Daily Operator` chạy 07:00 hằng ngày theo `Asia/Ho_Chi_Minh`.
- README dùng hoàn toàn kiến trúc ChatGPT Plus + GitHub + GitHub Actions.
- `.claude/skills/linux-daily/SKILL.md` và `routine-prompt.txt` đã bị loại bỏ.
- `state.json`, cadence logic, structured pipeline và CI không phụ thuộc vendor AI.

### PR #24 — Source-backed Technical Review ✅

Mục tiêu: nâng chất lượng từ “đúng cấu trúc” sang “claim kỹ thuật có bằng chứng” cho mọi bài mới.

- [x] `templates/post.template.html` có `review_status`, `sources` và section **Nguồn kỹ thuật**.
- [x] `tools/validate_sources.py` bắt buộc từ #019: tối thiểu 2 nguồn `official`/`upstream`, HTTPS, không trùng và metadata khớp link hiển thị.
- [x] `review_status="draft"` không qua merge gate; chỉ `reviewed`/`published` được chấp nhận.
- [x] `tools/build.py --check` chạy source-backed gate cùng structural quality gate.
- [x] Test riêng cho historical grandfather, status, số nguồn, HTTPS, duplicate và metadata↔HTML drift.
- [x] `AGENTS.md` có checklist kỹ thuật cho networking/firewall, storage, backup/restore, auth/permissions và shell automation.
- [x] Bài #001–#018 được grandfather có chủ đích để PR pipeline không biến thành một đợt backfill lớn.

## Mốc kế tiếp — Historical Technical Backfill

Mục tiêu: rà những claim rủi ro/phiên bản trong #001–#018 và thêm nguồn dần, ưu tiên theo mức ảnh hưởng thay vì sửa tất cả cùng lúc.

Ưu tiên đầu:

- [ ] #016 fail2ban/FreeBSD: dùng thuật ngữ hiện hành **blocklistd**; phân biệt blocklistd trong FreeBSD base với `sshguard` là lựa chọn ngoài base/Ports-package.
- [ ] #013 bash scripting: làm rõ `#!/usr/bin/env bash` phụ thuộc `PATH`; `set -e` có ngoại lệ; không khuyến nghị global `IFS=$'\n\t'` như mặc định; dùng `command -v` thay cho `which` khi kiểm command availability.
- [ ] Rà các bài firewall/networking để bảo đảm có rollback khi thao tác remote.
- [ ] Rà storage/backup để bảo đảm destructive operations và restore verification được nêu rõ.
- [ ] Chọn chiến lược backfill nguồn: theo bài hoặc theo nhóm rủi ro, không thay đổi ngày xuất bản lịch sử.

## P2 — Repository & website

- [ ] Branch protection bắt buộc `quality-gate` xanh trước merge.
- [ ] `LICENSE`.
- [ ] `CONTRIBUTING.md`.
- [ ] `SECURITY.md`.
- [ ] RSS/Atom.
- [ ] `sitemap.xml`.
- [ ] canonical URL.
- [ ] Open Graph/social metadata.
- [ ] broken-link check.
- [ ] cân nhắc self-host fonts.
- [ ] skip link và cải thiện mô tả accessibility cho sơ đồ phức tạp.

## Nguyên tắc roadmap

1. Không phụ thuộc một vendor AI cụ thể trong business logic; state và validation nằm trong repo.
2. Scheduled Task chỉ là scheduler/orchestrator, không thay thế CI.
3. Không push trực tiếp `main`.
4. Không bypass quality gate.
5. Mọi thay đổi automation phải rollback được bằng cách disable scheduler mà không làm hỏng dữ liệu series.
6. Pipeline mới áp nghiêm cho bài mới; backfill lịch sử làm theo mốc riêng để review nhỏ, dễ audit.

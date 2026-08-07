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
- ChatGPT Plus Scheduled Task làm scheduler chính: ✅ migration đang triển khai
- Source-backed technical review: ⏳ kế tiếp

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
- Prefix branch chuẩn mới sau migration:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

- Prefix legacy `claude/linux-daily-...` chỉ còn được đọc để phát hiện duplicate trong giai đoạn chuyển đổi.

### Structured Content Pipeline ✅

- Mỗi bài có JSON metadata `<script id="ld-meta">`.
- `tools/postmeta.py` đọc metadata/text bằng parser thay vì regex brittle.
- `templates/index.template.html` + Jinja2 dựng trang chủ.
- `tools/build.py` là entrypoint build/quality gate chính.

### Migration Claude Routine → ChatGPT Plus ✅ / đang merge

- `AGENTS.md` trở thành hợp đồng vận hành AI chính trong repository.
- `docs/CHATGPT-OPERATIONS.md` mô tả scheduler, quyền ghi GitHub và failure/rollback path.
- Scheduled Task `Linux Daily Operator` chạy 07:00 hằng ngày theo `Asia/Ho_Chi_Minh`.
- README chuyển hoàn toàn sang kiến trúc ChatGPT Plus + GitHub + GitHub Actions.
- Xóa `.claude/skills/linux-daily/SKILL.md` và `routine-prompt.txt` sau khi migration PR merge.
- Không thay đổi `state.json`, cadence logic, structured pipeline hay CI khi chuyển scheduler.
- Việc thủ công sau merge: **tắt Claude Routine cũ** để chỉ còn một scheduler.

## Mốc kế tiếp — Source-backed Technical Review

Mục tiêu: nâng chất lượng từ “đúng cấu trúc” sang “claim kỹ thuật có bằng chứng”.

- [ ] Mỗi bài có mục **Nguồn kỹ thuật**.
- [ ] Tối thiểu 2 nguồn chính thức phù hợp với claim chính; ưu tiên upstream, Ubuntu, Debian, Fedora và FreeBSD docs.
- [ ] Metadata có trạng thái `draft` → `reviewed` → `published` nếu cần.
- [ ] Validator kiểm tra số nguồn và cấu trúc citation/source section.
- [ ] Checklist review cho command/config có rủi ro cao: firewall, storage, backup/restore, auth/permissions, networking.
- [ ] Rà lại các bài cũ có khẳng định tuyệt đối hoặc phụ thuộc phiên bản.

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

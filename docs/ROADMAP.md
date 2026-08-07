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
- Historical source backfill: 🟡 các nhóm rủi ro #001–#017 đã merge; #011/#018 là backfill cuối trong PR #30

## Các mốc đã hoàn thành

### CI Quality Gate ✅

- `pyproject.toml` pin dependency + dev tools.
- `tools/validate_repo.py` kiểm numbering, axis cycle, date/meta consistency, template structure, SVG/accessibility, FreeBSD block, social output và state.
- `tools/build.py --check` làm cổng build/validation thống nhất.
- `.github/workflows/ci.yml` chạy lint, tests, validator/build và smoke tests trên PR.

### Cadence State & Idempotency ✅

- `state.json` là clock của cadence; `tools/cadence.py` quyết định nhịp từ `last_generated_at`.
- Agent kiểm duplicate issue qua branch/PR trước khi sinh bài.
- Prefix branch chuẩn: `chatgpt/linux-daily-<NNN>-<YYYYMMDD>`.

### Migration Claude Routine → ChatGPT Plus ✅

- PR #23 đã merge 2026-08-07.
- `AGENTS.md` là hợp đồng vận hành AI chính.
- Scheduled Task `Linux Daily Operator` chạy 07:00 hằng ngày theo `Asia/Ho_Chi_Minh`.
- Pipeline/CI/state không phụ thuộc vendor AI.

### PR #24 — Source-backed Technical Review ✅

- Bài #019+ bắt buộc `review_status`, tối thiểu 2 nguồn `official`/`upstream`, HTTPS, không trùng và khớp section hiển thị.
- Historical post đã opt-in source review cũng phải tiếp tục vượt gate.

### PR #25 — Historical Technical Backfill #013 + #016 ✅

- #013 Bash: sửa shebang/PATH, `set -e`, IFS và destructive-path claims.
- #016 FreeBSD/Fail2Ban: `blocklistd`, `sshguard`, package/jail hiện hành và firewall rollback.
- PR #25 đã merge 2026-08-07.

### PR #26 — Historical Technical Backfill: Networking & Firewall ✅

- #001 Static IP, #007 Firewall, #008 Diagnostics, #015 WireGuard được source-review và bổ sung rollback/verification.
- PR #26 đã merge 2026-08-07.

### PR #27 — Historical Technical Backfill: Storage & Backup ✅

- #003 ZFS, #004 restic, #010 Add disk, #014 Backup lab, #017 Grow storage được source-review và bổ sung guardrail/restore evidence.
- PR #27 đã merge 2026-08-07.

### PR #28 — Historical Technical Backfill: Auth & Permissions ✅

- #002 SSH và #009 sudo/doas được sửa effective-policy/least-privilege semantics.
- PR #28 đã merge 2026-08-07.

### PR #29 — Monitoring & Automation Backfill ✅

- #005 Logging: bỏ distro-default assumptions; kiểm effective journald storage và đúng SSH unit.
- #006 Ansible: Python bootstrap, ansible-core vs community.general, check-mode capability.
- #012 Scheduling: `Persistent=true`, `AccuracySec`, cron environment và FreeBSD periodic semantics.
- #005/#006/#012 có `review_status="reviewed"`, nguồn official/upstream và social đồng bộ.
- PR #29 đã merge 2026-08-07.

## PR #30 — Final Historical Tool Backfill

Mục tiêu: hoàn tất source-backed coverage cho hai bài grandfathered cuối #011 và #018.

- [x] #011 tmux: bỏ claim tuyệt đối về SIGHUP/process khi SSH mất; mô tả đúng client/server attach-detach model.
- [x] #011: thêm `tmux new -As`, `tmux -V`, boundary reboot/tmux-server và socket recovery nuance.
- [x] #018 rclone: sửa crypt algorithm thành XSalsa20+Poly1305 cho content và AES-256 EME cho names; ghi rõ metadata leakage.
- [x] #018: dùng `rclone cryptcheck` cho encrypted remote; tăng guardrail cho `sync`/`bisync`.
- [x] #018 FreeBSD: FUSE chỉ cần cho mount; dùng `kldload fusefs` + `sysrc kld_list+=fusefs`.
- [x] #011/#018 có `review_status="reviewed"` + nguồn official/upstream và section **Nguồn kỹ thuật**.
- [x] Đồng bộ Facebook/X cho cả hai bài.
- [x] Không đổi ngày xuất bản, `state.json`, cadence, `topics.md` hoặc metadata title/lede/date/axis dùng để dựng index.

## Mốc kế tiếp — P2 Repository & Website

Sau khi PR #30 merge, historical source backfill #001–#018 hoàn tất. Trọng tâm chuyển sang repository/website hardening theo các PR nhỏ.

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
- [ ] skip link và cải thiện accessibility cho sơ đồ phức tạp.

## Nguyên tắc roadmap

1. Không phụ thuộc một vendor AI cụ thể trong business logic; state và validation nằm trong repo.
2. Scheduled Task chỉ là scheduler/orchestrator, không thay thế CI.
3. Không push trực tiếp `main`.
4. Không bypass quality gate.
5. Thay đổi mạng/firewall/remote access phải có rollback path trước khi persist.
6. Thao tác storage phá huỷ/resize phải xác minh đúng device/layer trước khi ghi; backup phải có restore evidence định kỳ.
7. Hardening auth/permissions phải kiểm effective policy; least privilege không được suy luận từ file cấu hình hoặc group membership đơn lẻ.
8. Monitoring/automation phải kiểm effective runtime, dependency/collection và scheduler semantics thay vì hard-code theo tên distro.
9. Tool sync/encryption phải tách rõ confidentiality, destructive sync semantics, verification và backend access control.
10. Pipeline mới áp nghiêm cho bài mới; bài lịch sử đã opt-in source review cũng phải tiếp tục vượt gate.
11. Backfill lịch sử làm theo PR nhỏ, ưu tiên mức rủi ro để review dễ audit.

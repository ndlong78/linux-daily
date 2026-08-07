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
- Historical source backfill: 🟡 #013/#016 đã merge; #001/#007/#008/#015 trong PR #26

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
- `tools/build.py --check` chạy source-backed gate cùng structural gate.
- Historical post chưa backfill được grandfather; post lịch sử đã opt-in source review phải tiếp tục vượt gate.

### PR #25 — Historical Technical Backfill #013 + #016 ✅

- #013 Bash: làm rõ `#!/usr/bin/env bash` phụ thuộc `PATH`, giới hạn của `set -e`, bỏ global `IFS=$'\n\t'`, dùng `command -v`, sửa destructive-path claim.
- #016 FreeBSD/Fail2Ban: `blocklistd` đúng tên hiện hành, phân biệt `sshguard`, cập nhật `security/py-fail2ban` + `bsd-sshd-session`, bổ sung firewall rollback.
- Hai bài có `review_status="reviewed"` và nguồn kỹ thuật có cấu trúc.
- PR #25 đã merge 2026-08-07.

## PR #26 — Historical Technical Backfill: Networking & Firewall

Mục tiêu: rà #001, #007, #008 và #015 theo nguyên tắc **rollback-first** cho mọi thay đổi có thể làm mất đường quản trị từ xa.

- [x] #001 Static IP: giữ `netplan try`; làm rõ Debian có nhiều network manager; Fedora dùng đúng connection profile + NetworkManager checkpoint; FreeBSD thử runtime/giữ console trước khi persist.
- [x] #001: bỏ hướng dẫn restart toàn `networking` khi chỉ cần áp lại interface do ifupdown quản lý.
- [x] #007 Firewall: UFW mở SSH trước khi enable; firewalld runtime-first → verify → `--runtime-to-permanent`.
- [x] #007 FreeBSD PF: bắt buộc `pfctl -vnf /etc/pf.conf` trước `pfctl -f`; kiểm từ client thật, không chỉ localhost.
- [x] #008 Diagnostics: thêm tầng name resolution; `getent hosts`; giải thích ping thất bại không phải kết luận cuối; `sockstat -46 -l`; tcpdump có `-c`.
- [x] #015 WireGuard: cập nhật FreeBSD theo upstream `pkg install wireguard`; mô tả đúng hai vai trò của `AllowedIPs`; dựng split tunnel nhỏ trước full tunnel và chuẩn bị rollback route.
- [x] 4 bài có `review_status="reviewed"` + nguồn official/upstream và section **Nguồn kỹ thuật**.
- [x] Đồng bộ Facebook/X cho cả 4 bài.
- [x] Không đổi ngày xuất bản, `state.json`, cadence, `topics.md` hoặc metadata title/lede/date/axis dùng để dựng index.

## Mốc kế tiếp — Historical Technical Backfill theo nhóm rủi ro

- [ ] Storage/backup (#003, #004, #010, #014, #017): destructive operations, snapshot/restore semantics, restore verification.
- [ ] Auth/permissions (#002, #009): OpenSSH/sudo/doas hiện hành, đường rollback khi hardening remote access.
- [ ] Monitoring/automation còn lại: rà các claim phụ thuộc distro/version và thêm nguồn theo mức rủi ro.
- [ ] Tiếp tục backfill theo PR nhỏ; không thay đổi ngày xuất bản lịch sử.

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
6. Pipeline mới áp nghiêm cho bài mới; bài lịch sử đã opt-in source review cũng phải tiếp tục vượt gate.
7. Backfill lịch sử làm theo PR nhỏ, ưu tiên mức rủi ro để review dễ audit.

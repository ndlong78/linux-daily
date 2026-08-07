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
- Historical source backfill: 🟡 #013/#016, Networking/Firewall và Storage/Backup đã merge; Auth/Permissions trong PR #28

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

### PR #26 — Historical Technical Backfill: Networking & Firewall ✅

- #001 Static IP: `netplan try`, Debian network manager nuance, NetworkManager checkpoint, FreeBSD runtime/console rollback path.
- #007 Firewall: UFW mở SSH trước; firewalld runtime-first; PF parse bằng `pfctl -vnf` trước khi load.
- #008 Diagnostics: thêm name resolution, ping nuance, `sockstat -46 -l`, bounded tcpdump.
- #015 WireGuard: cập nhật FreeBSD package, semantics `AllowedIPs`, split-tunnel-first + rollback route.
- 4 bài có `review_status="reviewed"`, nguồn official/upstream và social đồng bộ.
- PR #26 đã merge 2026-08-07.

### PR #27 — Historical Technical Backfill: Storage & Backup ✅

- #003 ZFS: sửa semantics dung lượng snapshot; snapshot ≠ backup; destructive rollback; cập nhật Fedora OpenZFS repo.
- #004 restic: nhiều key/password; encryption design; preview retention; phân biệt `check` với data verification.
- #010 Add disk: verify device trước write; FreeBSD GPT alignment; Linux verify fstab; `nofail` chỉ cho mount optional.
- #014 Backup lab: subset/full read verification; restore chọn đúng snapshot; canary + checksum làm bằng chứng.
- #017 Grow storage: đúng stack disk→partition→PV→LV→filesystem; FreeBSD `growfs -N`; ZFS expansion nuance.
- 5 bài có `review_status="reviewed"`, nguồn official/upstream và social đồng bộ.
- PR #27 đã merge 2026-08-07.

## PR #28 — Historical Technical Backfill: Auth & Permissions

Mục tiêu: rà #002 và #009 theo nguyên tắc **effective-policy verification** và **least privilege phải được chứng minh bằng policy thực tế**.

- [x] #002 SSH: sửa precedence OpenSSH thành “first obtained value wins”; giải thích drop-in đọc sớm có thể override file chính.
- [x] #002: key-only gồm password + keyboard-interactive nuance; thêm `AuthenticationMethods publickey`, `sshd -T` và kiểm theo phiên SSH mới trước khi đóng phiên cứu hộ.
- [x] #002 Fedora/FreeBSD: giữ khác biệt service/SELinux/firewall/rc.d và rollback path khi hardening remote access.
- [x] #009: tách administrator khỏi limited operator; không thêm operator vào nhóm admin rồi kỳ vọng command-specific rule giới hạn quyền.
- [x] #009 Debian: ghi rõ sudo có thể chưa cài nếu installer đã đặt mật khẩu root.
- [x] #009 FreeBSD: `wheel` là điều kiện cho `su`, không phải điều kiện bắt buộc của doas; bỏ `persist`; dùng `doas -C` để parse + command-match mà không thực thi.
- [x] #002/#009 có `review_status="reviewed"` + nguồn official/upstream và section **Nguồn kỹ thuật**.
- [x] Đồng bộ Facebook/X cho cả hai bài.
- [x] Không đổi ngày xuất bản, `state.json`, cadence, `topics.md` hoặc metadata title/lede/date/axis dùng để dựng index.

## Mốc kế tiếp — Historical Technical Backfill theo nhóm rủi ro

- [ ] Monitoring/automation còn lại: rà các claim phụ thuộc distro/version và thêm nguồn theo mức rủi ro.
- [ ] Rà các bài lịch sử còn grandfather để xác định nhóm backfill cuối.
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
6. Thao tác storage phá huỷ/resize phải xác minh đúng device/layer trước khi ghi; backup phải có restore evidence định kỳ.
7. Hardening auth/permissions phải kiểm effective policy; least privilege không được suy luận từ file cấu hình hoặc group membership đơn lẻ.
8. Pipeline mới áp nghiêm cho bài mới; bài lịch sử đã opt-in source review cũng phải tiếp tục vượt gate.
9. Backfill lịch sử làm theo PR nhỏ, ưu tiên mức rủi ro để review dễ audit.

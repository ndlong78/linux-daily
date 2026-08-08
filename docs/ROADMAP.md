# Linux Daily — Roadmap

Legend: ✅ Completed · 🚧 Current · ⬜ Planned

## P0 — Foundation ✅
- Static site + shared CSS, cadence/state, deterministic generators và CI.

## P1 — Source-backed Content ✅
- AI operating contract, source-backed technical review và historical backfill.

## P2 — Repository & Website ✅
- Governance, discovery/SEO, production smoke, accessibility, self-hosted fonts và repository health.

## P3 — Reliability & Operations ✅
- Operations dashboard, production observability, release automation và performance budget.

## P4 — Content Growth ✅
- Taxonomy, related navigation, search/archive và content-mix review.

## P5 — Automation ✅
- One-command publish pipeline, weekly audit/report và workflow safety guardrails.

## P6 — Community ✅

### P6.1 — Contributor Onboarding ✅

- [x] `docs/contributor-quickstart.md` đưa contributor mới từ clone → local validation → PR xanh.
- [x] `python tools/contributor.py doctor` kiểm Python/Git/repository baseline và chỉ dẫn bước tiếp theo.
- [x] `CONTRIBUTING.md` dùng `tools/publish.py` làm validation entrypoint duy nhất thay vì checklist lệnh bị trùng.
- [x] Pull request template đồng bộ với publish/workflow safety hiện hành.
- [x] Phân biệt rõ contributor workflow và AI-agent operating contract trong `AGENTS.md`.

### P6.2 — Issue / Contribution Templates ✅

- [x] GitHub Issue Forms riêng cho bug, content/technical correction và feature proposal.
- [x] Issue chooser tắt blank issue và hướng security report sang GitHub Security Policy / `SECURITY.md`.
- [x] `docs/issue-guidelines.md` hướng dẫn chọn form, thông tin tối thiểu để triage và đường từ issue đến PR.
- [x] Không thêm automation ghi/merge hoặc dependency vào labels/repository settings ngoài Git.

### P6.3 — Technical Contributor Review Guide ✅

- [x] `docs/technical-review-guide.md` chuẩn hóa review source quality, distro portability và operational safety.
- [x] Review guide tách riêng Ubuntu/Xubuntu, Debian, Fedora và FreeBSD; FreeBSD không được gán Linux service/package/network model.
- [x] Checklist theo nhóm rủi ro: networking/firewall, storage, backup/restore, auth/permissions và automation/shell.
- [x] Phân loại finding thành blocker / needs change / suggestion để feedback nhất quán.
- [x] Pull request template trỏ trực tiếp tới review guide; reviewer không cần biết lịch sử repository.

## P7 — Content Quality at Scale ✅

### P7.1 — Distro Coverage & Portability Matrix ✅

- [x] `tools/distro_coverage.py` inventory Ubuntu/Xubuntu, Debian, Fedora và FreeBSD coverage cho mọi bài.
- [x] Baseline thực tế được ghi nhận minh bạch: 14/19 bài đủ bốn platform; #007, #008, #010, #014 và #017 vào historical review queue.
- [x] Từ #020, thiếu bất kỳ platform nào là hard-fail; không dùng backfill giả chỉ để làm đẹp baseline cũ.
- [x] Mọi bài phải có FreeBSD code block riêng được đánh dấu `class="bsd"` và hard-fail Linux-only command/path rõ ràng trong block đó.
- [x] Sinh deterministic `docs/distro-coverage-report.md`, đưa gate vào `tools/publish.py` và tài liệu hóa policy trong `docs/distro-portability.md`.

### P7.2 — Command & Configuration Quality Gate ✅

- [x] `tools/command_quality.py` static-scan code block, không thực thi command trong CI.
- [x] Hard-fail repository-wide các anti-pattern có tín hiệu cao: remote pipe-to-shell, `chmod 777`, catastrophic `rm -rf` và recursive permissions trên system roots.
- [x] Inventory destructive commands, privilege usage, insecure TLS, weak literal credential và privileged shell-redirection.
- [x] Từ #020, các finding context-sensitive trở thành blocker; #001–#019 giữ historical review queue thay vì rewrite tự động.
- [x] Gate được đưa vào `tools/publish.py check` và policy/false-positive boundary nằm tại `docs/command-config-quality.md`.

### P7.3 — Content Freshness & Technical Drift ✅

- [x] `freshness.json` định nghĩa review cadence theo volatility mà không rewrite metadata lịch sử.
- [x] `tools/content_freshness.py` tính `current`, `review-due` và `historically-valid`, hỗ trợ `--as-of`, `--json` và strict audit mode.
- [x] `review-due` tạo actionable queue nhưng không biến CI thành time-bomb; policy/ledger inconsistency vẫn hard-fail.
- [x] `historically-valid` chỉ được khai báo thủ công với reason, và optional replacement phải trỏ issue tồn tại.
- [x] Gate được đưa vào `tools/publish.py check`; policy/operating model nằm tại `docs/content-freshness.md`.

### P7.4 — P7 Audit & Quality Dashboard ✅

- [x] `tools/quality_dashboard.py` tổng hợp P7.1–P7.3 và source-backed review evidence mà không reimplement validator rules.
- [x] `docs/quality-dashboard.md` là canonical deterministic snapshot dựa trên `state.last_published_date`.
- [x] Dashboard có explicit owner + remediation contract cho distro, command/config, freshness và source-quality signals.
- [x] `tools/audit_report.py` dùng cùng aggregator với ngày audit thực tế để surface `review-due` theo thời gian.
- [x] P7 đóng với hard-error path rõ ràng và non-blocking remediation queue tách biệt.

## P8 — Learning Experience 🚧

### P8.1 — Learning Paths ✅
- [x] `learning-paths.json` định nghĩa curriculum ordering theo mục tiêu kỹ năng bằng issue ID thay vì copy title/URL.
- [x] 4 learning paths phủ 19/19 bài hiện có; overlap giữa path được cho phép có chủ đích.
- [x] `tools/learning_paths.py` hard-fail unknown issue, duplicate step, invalid schema và bài published chưa thuộc path nào.
- [x] `learning-paths.html` được generate deterministic từ config + `ld-meta`, có canonical/sitemap và accessibility/SEO validation.
- [x] Operating model và boundary với prerequisites/progression nằm tại `docs/learning-paths.md`.

### P8.2 — Difficulty & Prerequisites ⬜
- [ ] Chuẩn hóa difficulty/prerequisite metadata để người học biết nên học gì trước.

### P8.3 — Topic Progression ⬜
- [ ] Phát hiện khoảng trống hoặc bước nhảy kiến thức giữa các bài cùng axis/series.

### P8.4 — Learning Dashboard ⬜
- [ ] Tạo derived learning view từ taxonomy, prerequisites và progression mà không thay source of truth của bài viết.
- [ ] Hợp nhất learning navigation/discovery trên public site khi đủ signal từ P8.1–P8.3.

## Nguyên tắc roadmap

1. Repository/state/validators là source of truth; scheduler không thay business logic.
2. Không push trực tiếp `main` và không bypass quality gate.
3. Cloudflare Worker là production serving layer; GitHub Pages không phải public hosting.
4. Generated artifacts phải deterministic và kiểm được bằng publish/build checks.
5. Nguồn kỹ thuật ưu tiên official/upstream; claim mới không kế thừa mù từ bài cũ.
6. FreeBSD luôn được xử lý riêng.
7. Network/firewall/remote access phải có rollback trước khi persist.
8. Storage/backup phải phân biệt layer, destructive semantics và restore evidence.
9. External network checks phải có policy chống flaky; local deterministic failures vẫn fail cứng.
10. Phase đã đóng chỉ mở lại khi có regression hoặc requirement mới rõ ràng; feature mới phải đi vào phase hiện tại.

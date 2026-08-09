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

## P8 — Learning Experience ✅

### P8.1 — Learning Paths ✅
- [x] `learning-paths.json` định nghĩa curriculum ordering theo mục tiêu kỹ năng bằng issue ID thay vì copy title/URL.
- [x] 4 learning paths phủ 19/19 bài hiện có; overlap giữa path được cho phép có chủ đích.
- [x] `tools/learning_paths.py` hard-fail unknown issue, duplicate step, invalid schema và bài published chưa thuộc path nào.
- [x] `learning-paths.html` được generate deterministic từ config + `ld-meta`, có canonical/sitemap và accessibility/SEO validation.
- [x] Operating model và boundary với prerequisites/progression nằm tại `docs/learning-paths.md`.

### P8.2 — Difficulty & Prerequisites ✅
- [x] `learning-metadata.json` chuẩn hóa difficulty (`basic` / `intermediate` / `advanced`) và prerequisite issue IDs cho mọi bài published.
- [x] `tools/learning_metadata.py` hard-fail metadata thiếu/thừa, difficulty không hợp lệ, prerequisite sai/self/duplicate và dependency cycle.
- [x] Baseline 19 bài: 8 Cơ bản, 11 Trung cấp, 0 Nâng cao; 16 prerequisite edges và 0 cycle.
- [x] `tools/learning_paths.py` import cùng metadata để hiển thị độ khó + “Học trước”, không reimplement rule.
- [x] Learning metadata gate được đưa vào `tools/publish.py check`; policy nằm tại `docs/difficulty-prerequisites.md`.

### P8.3 — Topic Progression ✅
- [x] `tools/topic_progression.py` kết hợp path ordering + prerequisite DAG + difficulty mà không reimplement P8.1/P8.2 validators.
- [x] Hard-fail prerequisite xuất hiện sau bài phụ thuộc trong cùng path và difficulty jump tăng quá một bậc.
- [x] Prerequisite ngoài path được inventory như cross-path dependency, không bị đánh đồng với ordering violation.
- [x] Missing difficulty tier là curriculum gap dạng ATTENTION; strict audit có thể dùng `--fail-gaps` nhưng normal publish CI không biến baseline thành lỗi giả.
- [x] Baseline: 23 prerequisite references, 17 local / 6 external, 0 ordering violation, 0 difficulty jump, thiếu tier `advanced`.
- [x] Progression gate được đưa vào `tools/publish.py check`; operating model nằm tại `docs/topic-progression.md`.

### P8.4 — Learning Dashboard ✅
- [x] `tools/learning_dashboard.py` tạo derived view trực tiếp từ P8.1–P8.3, không thêm curriculum ledger mới.
- [x] `learning-dashboard.html` hiển thị coverage, difficulty mix, prerequisite/progression health và summary từng learning path.
- [x] Dashboard giữ `ATTENTION` khi corpus chưa có bài Nâng cao; không relabel bài cũ chỉ để tạo PASS.
- [x] Dashboard là first-class public page: canonical, sitemap, repository-health, accessibility, self-host font và internal-link validation.
- [x] `tools/publish.py prepare/check` regenerate/verify dashboard deterministic; operating model nằm tại `docs/learning-dashboard.md`.

## P9 — Advanced Labs ✅

### P9.1 — Advanced Lab Framework & Safety Contract ✅
- [x] `tools/lab_contract.py` nhận diện lab mới và validate machine-readable `ld-meta.lab` contract.
- [x] Hai lab lịch sử #007/#014 được giữ như legacy reference; enforcement bắt đầu từ #020, không retro-fit metadata giả.
- [x] Contract chuẩn hóa topology roles, risk classes, rollback/cleanup, failure injection và verification evidence classes.
- [x] Semantic HTML markers `data-lab-section` cho scenario/topology/safety/execution/verification/rollback/cleanup giúp CI kiểm cấu trúc mà không parse câu chữ.
- [x] Destructive storage bắt buộc restore evidence; failure injection bắt buộc recovery evidence; risk thực tế bắt buộc rollback.
- [x] Gate được đưa vào `tools/publish.py check`; authoring/safety model nằm tại `docs/advanced-lab-framework.md`.

### P9.2 — Security & Networking Advanced Lab ✅
- [x] Dựng lab có topology nhiều node, remote-access rollback và negative tests.
- [x] Bao quát Ubuntu/Xubuntu, Debian, Fedora và FreeBSD với firewall/service semantics riêng.
- [x] Có failure injection + recovery evidence thay vì chỉ kiểm happy path.

### P9.3 — Storage & Backup/Restore Advanced Lab ✅
- [x] Phân biệt block/partition/volume/filesystem/mount layer.
- [x] Có destructive test trên lab resource, backup trước thay đổi và restore evidence bắt buộc.

### P9.4 — Monitoring & Automation Failure Lab ✅
- [x] Contract bắt buộc failure injection có blast radius giới hạn cho `resource-pressure` (CPU/RAM/I/O/service scenario).
- [x] Contract bắt buộc `observability` + `recovery`; framework mô tả evidence trước/trong/sau fault và cleanup tự động an toàn.

### P9.5 — Linux ↔ FreeBSD Interoperability Lab ✅
- [x] Dựng workflow nginx/HTTP hai chiều trên Linux peer và FreeBSD peer thật; mỗi platform có script riêng và application-level functional/negative/recovery evidence.
- [x] `tools/interoperability_lab.py` kiểm package/service/firewall/path differences, cấm Linux-only semantics trong FreeBSD helper và được đưa vào deterministic `publish.py check`.

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

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

## P7 — Content Quality at Scale 🚧

### P7.1 — Distro Coverage & Portability Matrix ✅

- [x] `tools/distro_coverage.py` inventory Ubuntu/Xubuntu, Debian, Fedora và FreeBSD coverage cho mọi bài.
- [x] Mỗi bài phải có FreeBSD code block riêng được đánh dấu `class="bsd"`.
- [x] Hard-fail các Linux-only command/path rõ ràng nếu xuất hiện trong FreeBSD block.
- [x] Sinh deterministic `docs/distro-coverage-report.md` và đưa gate vào `tools/publish.py`.
- [x] Tài liệu hóa policy/false-positive boundary trong `docs/distro-portability.md`.

### P7.2 — Command & Configuration Quality Gate ⬜

- [ ] Static checks cho command/config examples, privilege/destructive markers và shell/config quality.
- [ ] Không thực thi command nguy hiểm trong CI; ưu tiên deterministic static validation.

### P7.3 — Content Freshness & Technical Drift ⬜

- [ ] Thiết kế freshness state và review-due policy mà không âm thầm rewrite historical content.
- [ ] Phân biệt current guidance với historically-valid guidance.

### P7.4 — P7 Audit & Quality Dashboard ⬜

- [ ] Tổng hợp distro coverage, command/config findings, freshness và source-quality evidence vào quality view.
- [ ] Đóng P7 khi các quality signals có ownership và remediation path rõ ràng.

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

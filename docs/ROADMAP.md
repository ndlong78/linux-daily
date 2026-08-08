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

## P6 — Community 🚧

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

### P6.3 — Technical Contributor Review Guide 🚧

- [ ] Review guide cho source quality, distro portability và operational safety.
- [ ] Checklist dành cho technical reviewer không cần hiểu lịch sử repository.

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

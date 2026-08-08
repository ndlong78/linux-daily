# Linux Daily — Roadmap

Legend: ✅ Completed · 🚧 Current · ⬜ Planned

## P0 — Foundation ✅

- Static site + shared CSS.
- `state.json` cadence + `tools/cadence.py`.
- Structured post metadata và deterministic generators.
- GitHub Actions CI với Ruff, Pytest, build/validator và smoke tests.
- Social output pipeline.

## P1 — Source-backed Content ✅

- ChatGPT Plus Scheduled Task thay Claude Routine làm scheduler/orchestrator.
- `AGENTS.md` là hợp đồng vận hành AI chính.
- Bài mới bắt buộc source-backed technical review.
- Historical technical backfill #001–#018 hoàn tất theo nhóm rủi ro.
- FreeBSD, destructive storage/network/auth semantics và rollback được đưa vào review guardrails.

## P2 — Repository & Website ✅

P2 được đóng bởi PR #44 sau chuỗi hardening PR #31–#43.

### Governance

- [x] Branch-protection baseline yêu cầu `quality-gate`.
- [x] MIT `LICENSE`.
- [x] `CONTRIBUTING.md`.
- [x] `SECURITY.md`.
- [x] `CODEOWNERS`.
- [x] Pull request template.

### Discovery & metadata

- [x] RSS feed.
- [x] `sitemap.xml` + `robots.txt`.
- [x] Canonical URL với public origin `https://linux.no.id.vn/`.
- [x] Open Graph + Twitter/X Card + social preview image metadata.
- [x] Historical metadata backfill #001–#019.

### Quality & reliability

- [x] Internal/external broken-link checking.
- [x] Website/SEO cross-artifact validator.
- [x] Production smoke tests cho Cloudflare Worker.
- [x] Accessibility baseline: skip link, main landmark, keyboard focus, heading/SVG guardrails.
- [x] Self-host Be Vietnam Pro, JetBrains Mono và Noto Serif; không còn Google Fonts runtime dependency.
- [x] Repository health summary + release checklist.

## P3 — Reliability & Operations ✅

### P3.1 — Operations Dashboard & Repository Insights ✅
- [x] Source-derived operational dashboard trong GitHub Actions.

### P3.2 — Production Observability ✅
- [x] Serving fingerprint, cache/content semantics và incident runbook.

### P3.3 — Release Automation ✅
- [x] SemVer + exact-SHA release gate + human confirmation.

### P3.4 — Performance Budget ✅
- [x] Deterministic artifact-size regression budget.

## P4 — Content Growth ✅

### P4.1 — Taxonomy / Tags / Topic Discovery ✅
- [x] Canonical taxonomy và metadata consistency gate.

### P4.2 — Related Content & Series Navigation ✅
- [x] Related/previous/next navigation deterministic.

### P4.3 — Search & Archive ✅
- [x] Static archive + client-side search.

### P4.4 — Content Mix Review ✅
- [x] 7-axis sequence/distribution review + deterministic report.

## P5 — Automation 🚧

### P5.1 — Publish Pipeline Automation ✅

- [x] `python tools/publish.py prepare` regenerate deterministic artifacts/reports.
- [x] `python tools/publish.py check` chạy local publish gates read-only.
- [x] CI tái sử dụng cùng orchestration; external HTTP checks tách riêng.
- [x] Không auto-merge/bypass branch protection/release.

### P5.2 — Audit & Report Automation ✅

- [x] `tools/audit_report.py` gom repository health, content mix, publication freshness và workflow evidence.
- [x] Full audit có thể bổ sung live production observability nhưng local mode vẫn deterministic/offline.
- [x] Workflow `Audit Report` chạy hàng tuần, xuất Job Summary và artifact 30 ngày.
- [x] Workflow chỉ read-only; không commit audit snapshot trở lại repository và không tạo source of truth mới.

### P5.3 — Safe Workflow Automation 🚧

- [ ] Tự động hóa các bước lặp lại còn lại nhưng không auto-merge hoặc bypass quality gate.
- [ ] Giữ human approval cho merge/release có ảnh hưởng production.

## P6 — Community ⬜

- [ ] Contributor onboarding tốt hơn.
- [ ] Issue templates/discussion workflow nếu cộng đồng bắt đầu đóng góp thường xuyên.
- [ ] Tài liệu review cho technical contributors.

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

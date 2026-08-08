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

Mục tiêu: xác minh production đang serve đúng public artifacts mong đợi, phát hiện regression sớm và có tín hiệu vận hành đủ rõ để xử lý sự cố.

### P3.1 — Operations Dashboard & Repository Insights ✅

- [x] Tổng hợp repository/production-adjacent status vào một report dễ đọc trong GitHub Actions Job Summary.
- [x] Hiển thị publication freshness, latest issue, CI/smoke state và artifact inventory.
- [x] Không biến dashboard thành source of truth mới; dữ liệu derive trực tiếp từ repo và GitHub Actions.

### P3.2 — Production Observability ✅

- [x] Deterministic serving fingerprint từ các public artifacts trọng yếu.
- [x] Content-type/cache semantics + stale/content-drift detection.
- [x] Incident/rollback runbook.

### P3.3 — Release Automation ✅

- [x] SemVer chính thức qua `VERSION` và tag `vX.Y.Z`.
- [x] Manual release có CI + Production Smoke exact-SHA gate.
- [x] Release notes từ CHANGELOG + merged PR context.

### P3.4 — Performance Budget ✅

- [x] Budget kích thước homepage/post HTML, CSS, WOFF2 fonts và social PNG assets.
- [x] Regression gate chạy trong CI và fail deterministic khi artifact vượt ngưỡng.
- [x] Chỉ dùng local artifact-size signals ổn định; không đưa network benchmark/Lighthouse runtime vào PR quality gate.

## P4 — Content Growth ✅

### P4.1 — Taxonomy / Tags / Topic Discovery ✅

- [x] `taxonomy.json` định nghĩa canonical axis, slug, label và mô tả; không nhân đôi mapping từng bài.
- [x] Taxonomy của từng bài derive trực tiếp từ `ld-meta.axis`; secondary tags derive từ `ld-meta.eyebrow`.
- [x] `tools/taxonomy.py` kiểm coverage/axis drift và xuất report deterministic cho repository.
- [x] CI chặn bài mới dùng axis chưa đăng ký hoặc thiếu metadata để derive tag.

### P4.2 — Related Content & Series Navigation ✅

- [x] Navigation giữa các bài liên quan derive từ cùng `ld-meta.axis`, ưu tiên secondary-tag overlap rồi khoảng cách issue.
- [x] Previous/next deterministic trong cùng trục nội dung, không tạo mapping thủ công thứ hai.
- [x] Generator dùng marker idempotent và được `build.py --check` kiểm để bài mới không làm navigation stale.
- [x] Backfill toàn bộ bài hiện có và thêm stylesheet riêng, responsive + keyboard-accessible.

### P4.3 — Search & Archive ✅

- [x] `archive.html` nhóm toàn bộ bài theo canonical taxonomy axis, newest-first trong từng nhóm.
- [x] `search-index.json` derive từ `ld-meta` + `taxonomy.json`; không crawl body HTML và không tạo source of truth mới.
- [x] Client-side search không cần backend/framework, tìm theo title, lede, axis và secondary tags; hỗ trợ Vietnamese diacritic-insensitive matching.
- [x] Archive vẫn dùng được khi JavaScript lỗi/tắt; search là progressive enhancement.
- [x] `build.py --check` chặn archive/search index stale và sitemap discover `archive.html`.

### P4.4 — Content Mix Review ✅

- [x] Review 19 bài thực tế theo canonical 7-axis rotation: 2 chu kỳ hoàn chỉnh + 5/7 chu kỳ hiện tại.
- [x] Distribution spread chỉ 1 bài; phần 3-vs-2 là trạng thái tự nhiên của chu kỳ chưa hoàn tất, không cần backfill nhân tạo.
- [x] `tools/content_mix.py` kiểm sequence, axis coverage, balance và report freshness deterministic.
- [x] CI chặn content-mix/cadence drift; snapshot nằm ở `docs/content-mix-report.md`.

## P5 — Automation 🚧

### P5.1 — Publish Pipeline Automation ✅

- [x] Một lệnh `python tools/publish.py prepare` regenerate website artifacts + deterministic reports sau khi sửa/thêm bài.
- [x] Một lệnh `python tools/publish.py check` chạy toàn bộ local publish gates ở chế độ read-only trước khi push.
- [x] CI tái sử dụng cùng publish orchestration để local/CI không duy trì hai danh sách validator khác nhau.
- [x] External HTTP checks vẫn tách riêng vì network-dependent; branch/PR/merge/release vẫn cần human approval.

### P5.2 — Audit & Report Automation

- [ ] Giảm thao tác thủ công khi tổng hợp repository/production audit định kỳ.
- [ ] Tái sử dụng deterministic reports hiện có thay vì tạo thêm source of truth.

### P5.3 — Safe Workflow Automation

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
4. Generated artifacts phải deterministic và kiểm được bằng `build.py --check`.
5. Nguồn kỹ thuật ưu tiên official/upstream; claim mới không kế thừa mù từ bài cũ.
6. FreeBSD luôn được xử lý riêng.
7. Network/firewall/remote access phải có rollback trước khi persist.
8. Storage/backup phải phân biệt layer, destructive semantics và restore evidence.
9. External network checks phải có policy chống flaky; local deterministic failures vẫn fail cứng.
10. Phase đã đóng chỉ mở lại khi có regression hoặc requirement mới rõ ràng; feature mới phải đi vào phase hiện tại.

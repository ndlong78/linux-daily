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

## P3 — Reliability & Operations 🚧

Mục tiêu: xác minh production đang serve đúng public artifacts mong đợi, phát hiện regression sớm và có tín hiệu vận hành đủ rõ để xử lý sự cố.

### P3.1 — Operations Dashboard & Repository Insights ✅

- [x] Tổng hợp repository/production-adjacent status vào một report dễ đọc trong GitHub Actions Job Summary.
- [x] Hiển thị publication freshness, latest issue, CI/smoke state và artifact inventory.
- [x] Không biến dashboard thành source of truth mới; dữ liệu derive trực tiếp từ repo và GitHub Actions.
- [x] Giữ deployment fingerprint/stale-production detection ngoài P3.1 để xử lý đúng ở P3.2.

### P3.2 — Production Observability ✅

- [x] Xác định deterministic serving fingerprint từ các public artifacts trọng yếu.
- [x] Kiểm content-type và cache semantics an toàn cho static public responses; provider-specific header absence chỉ warning để tránh flaky gate.
- [x] Phát hiện production stale/content drift so với checkout `main` bằng per-endpoint SHA-256 + aggregate fingerprint.
- [x] Chuẩn hóa incident/rollback procedure trong `docs/production-incident-runbook.md`.
- [x] Không suy diễn Git SHA từ fingerprint khi deployment pipeline chưa inject commit metadata; fingerprint chứng minh public serving equivalence.

### P3.3 — Release Automation ✅

- [x] Quy ước SemVer chính thức: `VERSION` chứa `X.Y.Z`, Git tag dùng `vX.Y.Z`; Python project metadata derive từ cùng source.
- [x] Release notes ghép CHANGELOG milestone đã review qua PR với merged-PR notes do GitHub sinh tự động.
- [x] Release chỉ chạy bằng manual `workflow_dispatch`, yêu cầu explicit confirmation và từ chối publish nếu CI hoặc Production Smoke chưa `success` trên chính SHA hiện tại của `main`.
- [x] Không cho release workflow tự sửa `main`; CHANGELOG/version vẫn đi qua PR và branch protection.

### P3.4 — Performance Budget

- [ ] Budget kích thước HTML/CSS/font/social assets.
- [ ] Regression gate cho asset/page growth bất thường.
- [ ] Đo performance theo tín hiệu ổn định, tránh CI phụ thuộc network benchmark dễ flaky.

## P4 — Content Growth ⬜

- [ ] Taxonomy/tag/topic discovery.
- [ ] Navigation giữa bài liên quan và series.
- [ ] Search/archive khi số bài đủ lớn để cần.
- [ ] Review lại cadence/content mix dựa trên dữ liệu thực tế.

## P5 — Automation ⬜

- [ ] Giảm thao tác thủ công lặp lại trong publish/release.
- [ ] Tự động hóa audit/report có deterministic input.
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

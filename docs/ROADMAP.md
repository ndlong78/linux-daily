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
- Contributor onboarding, structured issue intake và technical review guide.

## P7 — Content Quality at Scale ✅
- Distro/FreeBSD portability, command/config quality, freshness lifecycle và quality dashboard.

## P8 — Learning Experience ✅
- Learning paths, difficulty/prerequisite DAG, topic progression và public learning dashboard.

## P9 — Advanced Labs ✅
- Advanced lab safety contract, security/network, storage/restore, resource-pressure và Linux ↔ FreeBSD interoperability labs.

## P10 — Sustainable Daily Publishing 🚧

Mục tiêu P10 là giữ nhịp **1 bài/ngày** nhưng không biến Linux Daily thành tập hợp topic ngẫu nhiên. Planning/readiness phải deterministic, review được và tách khỏi publication state.

### P10.1 — Daily Curriculum Planner ✅
- [x] `curriculum-plan.json` là queue chủ đề tương lai riêng, không ghi đè `state.json` và không tự publish.
- [x] Queue giữ đúng canonical 7-axis rotation từ `taxonomy.json` và bắt đầu tại axis kế tiếp sau corpus đã publish.
- [x] Mỗi topic có difficulty + learning goal để reviewer đánh giá progression trước khi viết bài.
- [x] `tools/curriculum_planner.py` hard-fail schema/horizon, axis drift, duplicate queue topic và exact title collision với corpus.
- [x] Planner resolve issue number từ corpus tại runtime; issue number không được hard-code trong planning ledger.
- [x] `tools/publish.py check` chạy planner như read-only gate.
- [x] Baseline horizon là 14 ngày / 2 chu kỳ; social output không nằm trong planner.

### P10.2 — Publication Readiness Gate 🚧
- [x] Mỗi planned topic khai báo prerequisite issue IDs; prerequisite phải là bài đã publish và không được trùng.
- [x] Advanced topic bắt buộc có prerequisite thay vì nhảy thẳng vào nội dung nâng cao.
- [x] Readiness policy khóa expected platform scope: Ubuntu/Xubuntu, Debian, Fedora và FreeBSD.
- [x] Readiness policy yêu cầu tối thiểu 2 primary official/upstream sources khi authoring.
- [x] `tools/publication_readiness.py` dùng token/Jaccard similarity để chặn topic quá giống title đã publish, ngoài exact-title guard của planner.
- [x] `tools/publication_readiness.py --json` xuất next-topic readiness contract cho operator/reviewer.
- [x] `tools/publish.py check` chạy readiness gate read-only sau curriculum planner.
- [x] Readiness không đọc clock, không thay cadence, không sửa `state.json` và không tự publish.

### P10.3 — Backlog & Coverage Intelligence ⬜
- [ ] Tìm curriculum gaps theo taxonomy, learning paths và corpus thay vì chọn topic ngẫu nhiên.
- [ ] Recommendation phải explainable và không tự sửa queue.

### P10.4 — Long-term Content Lifecycle ⬜
- [ ] Mở rộng freshness model cho superseded/replacement và historical-valid lifecycle khi corpus tăng lớn.

### P10.5 — Daily Operations Dashboard ⬜
- [ ] Hợp nhất last published, next planned, cadence, quality status, learning coverage và review queue thành derived operational view.

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
11. Curriculum plan là intent tương lai; `state.json` và post metadata mới là publication truth.
12. Readiness gate chỉ trả lời “topic đã sẵn sàng để authoring chưa”; cadence gate mới trả lời “đã tới lúc sinh bài chưa”.

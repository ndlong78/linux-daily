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

## P10 — Sustainable Daily Publishing ✅

Mục tiêu P10 là giữ nhịp **1 bài/ngày** nhưng không biến Linux Daily thành tập hợp topic ngẫu nhiên. Planning/readiness/lifecycle phải deterministic, review được và tách khỏi publication state.

### P10.1 — Daily Curriculum Planner ✅
- [x] Queue 14 ngày / 2 chu kỳ, canonical 7-axis rotation, không ghi `state.json`.
- [x] Planner validate horizon, difficulty, duplicate/exact-title collision và resolve issue runtime.

### P10.2 — Publication Readiness Gate ✅
- [x] Prerequisite readiness, semantic similarity, 4-platform review scope và tối thiểu 2 primary sources.
- [x] Readiness read-only, không thay cadence hoặc publication state.

### P10.3 — Backlog & Coverage Intelligence ✅
- [x] Capability catalog theo 7 axis và explainable gap recommendation từ corpus/path/plan.
- [x] Coverage intelligence read-only, không tự sửa curriculum queue.
- [x] `chatgpt/**` branch có remote CI pre-PR gate.

### P10.4 — Long-term Content Lifecycle ✅
- [x] Freshness model hỗ trợ `current`, `review-due`, `historically-valid` và `superseded`.
- [x] `superseded` bắt buộc có reason + replacement issue mới hơn và đang tồn tại.
- [x] `historically-valid` giữ nội dung có giá trị lịch sử mà không giả vờ là guidance hiện hành.
- [x] `tools/content_lifecycle.py` resolve replacement lineage đến canonical guidance.
- [x] Replacement graph hard-fail backward target, cycle/missing target và terminal không còn canonical.
- [x] Lifecycle tham gia `tools/publish.py check` nhưng không rewrite bài cũ hay `state.json`.

### P10.5 — Daily Operations Dashboard ✅
- [x] `tools/daily_operations_dashboard.py` hợp nhất last published, next planned, cadence, readiness, P7 quality, P8 learning coverage, lifecycle và coverage intelligence thành một derived operational view.
- [x] Dashboard import trực tiếp validator hiện hành, có `--json`/`--output`/`--as-of` và tham gia `tools/publish.py check` như read-only consistency gate.
- [x] Dashboard không tự publish, không sửa curriculum/state/lifecycle và không duplicate GitHub/production evidence của Operations Dashboard hiện hữu.

## Operating mode sau P10 — Infrastructure feature freeze

P0–P10 đã cung cấp đủ nền tảng cho daily publishing. Mặc định **không mở P11+** chỉ để bổ sung thêm tooling/dashboard/validator.

Tooling mới chỉ được chấp nhận khi đáp ứng ít nhất một điều kiện:

1. sửa một regression/sự cố đã quan sát được;
2. loại bỏ thao tác lặp lại có chi phí đáng kể;
3. trực tiếp nâng chất lượng hoặc độ an toàn của nội dung Linux/Unix.

Nếu không thuộc ba nhóm trên, ưu tiên viết bài, technical review, cập nhật freshness và cải thiện trải nghiệm nhỏ trên kiến trúc hiện có. Maintenance nên sửa/đơn giản hóa tool hiện hành trước khi tạo abstraction mới.

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
12. Readiness gate trả lời “topic đã sẵn sàng để authoring chưa”; cadence gate trả lời “đã tới lúc sinh bài chưa”.
13. Coverage intelligence chỉ đề xuất backlog có giải thích; con người/planner quyết định queue.
14. Branch `chatgpt/**` phải qua remote CI preflight trước khi Draft PR được mở.
15. Nội dung superseded/historically-valid được giữ để bảo toàn lịch sử; canonical replacement mới là guidance vận hành hiện hành.
16. Daily Operations Dashboard chỉ tổng hợp decision signals; không trở thành ledger mới và không thay các validator nguồn.
17. Sau P10, infrastructure mặc định feature-frozen; chỉ mở rộng khi có defect/toil/content-quality evidence rõ ràng.

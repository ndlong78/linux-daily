# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P10 — Sustainable Daily Publishing ✅  
**P10 status:** ✅ P10.1–P10.5 complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P10 sustainable daily publishing

Linux Daily dùng cadence mặc định **1 bài/ngày**. P10 đã tách planning, readiness, coverage intelligence, lifecycle và publication state để corpus tăng lâu dài mà vẫn kiểm soát được guidance hiện hành.

### P10.5 Daily Operations Dashboard

- `tools/daily_operations_dashboard.py` hợp nhất publication clock, cadence, next planned topic, authoring readiness, P7 quality, P8 learning coverage, lifecycle và coverage gap;
- dashboard import trực tiếp các validator hiện hành thay vì reimplement business rule;
- mặc định dùng `state.last_published_date` làm `as-of` deterministic cho publish gate;
- hỗ trợ `--json`, `--as-of` và `--output` cho operator/audit;
- `tools/publish.py check` chạy dashboard như read-only consistency gate;
- không tự publish, không sửa `state.json`, curriculum queue hoặc lifecycle overrides;
- GitHub Actions/production evidence vẫn thuộc `tools/operations_dashboard.py` và weekly audit, không bị duplicate vào P10.5.

Operating model: `docs/daily-operations-dashboard.md`.

### P10.4 Long-term Content Lifecycle

- `tools/content_freshness.py` hỗ trợ `current`, `review-due`, `historically-valid`, `superseded`;
- `tools/content_lifecycle.py` resolve replacement lineage tới canonical issue và hard-fail invalid graph;
- lifecycle read-only, không rewrite bài lịch sử hoặc publication state.

### P10.1–P10.3 planning/readiness/intelligence

- 14-day curriculum queue theo canonical 7-axis rotation;
- Publication Readiness Gate kiểm prerequisite, semantic duplicate, 4-platform scope và minimum primary sources;
- Coverage Intelligence dùng capability catalog + corpus/path/plan để đề xuất backlog gap có giải thích;
- planning và intelligence không tự sửa publication truth.

## Operator entrypoint

```bash
python3 tools/curriculum_planner.py --json
python3 tools/publication_readiness.py --json
python3 tools/coverage_intelligence.py --json
python3 tools/content_lifecycle.py --json
python3 tools/daily_operations_dashboard.py
python3 tools/pr_preflight.py
```

Planning thể hiện intent; readiness xác nhận khả năng authoring; coverage intelligence đề xuất gap; lifecycle xác định guidance canonical; Daily Operations Dashboard hợp nhất decision signals; `state.json` + post metadata vẫn là publication truth.

## Milestones

| Phase | Trạng thái | Kết quả chính |
|---|---|---|
| P0 — Foundation | ✅ | Static site, template, cadence/state, CI |
| P1 — Source-backed Content | ✅ | Technical review + historical backfill |
| P2 — Repository & Website | ✅ | Governance, SEO/discovery, accessibility, production smoke |
| P3 — Reliability & Operations | ✅ | Dashboard, production fingerprint, release automation, performance budget |
| P4 — Content Growth | ✅ | Taxonomy, navigation, search/archive, content-mix review |
| P5 — Automation | ✅ | Publish pipeline, audit/report, workflow safety |
| P6 — Community | ✅ | Contributor onboarding, issue intake, technical review guide |
| P7 — Content Quality at Scale | ✅ | Portability + command quality + freshness + quality dashboard |
| P8 — Learning Experience | ✅ | Paths + prerequisites + progression + public Learning Dashboard |
| P9 — Advanced Labs | ✅ | Safety contract + advanced labs + Linux ↔ FreeBSD interoperability |
| P10 — Sustainable Daily Publishing | ✅ | Planner + readiness + coverage intelligence + lifecycle + daily operations dashboard |

## Roadmap

Xem `docs/ROADMAP.md`. P10 đã hoàn tất; phase tiếp theo chỉ nên được mở bằng một roadmap PR riêng sau khi review nhu cầu mới.

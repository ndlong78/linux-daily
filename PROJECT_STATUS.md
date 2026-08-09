# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P10 — Sustainable Daily Publishing 🚧  
**Current focus:** P10.3 — Backlog & Coverage Intelligence  
**P10.2 status:** ✅ Publication Readiness Gate complete  
**P10.1 status:** ✅ Daily Curriculum Planner complete  
**P9 status:** ✅ Advanced Labs complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P10 sustainable daily publishing

Linux Daily dùng cadence mặc định **1 bài/ngày**. P10 tách rõ planning, readiness, coverage intelligence và publication state để cadence nhanh hơn nhưng curriculum vẫn có chủ đích.

### P10.1–P10.2 foundation

- `curriculum-plan.json` giữ queue 14 topic / 2 chu kỳ 7 trục;
- `tools/curriculum_planner.py` kiểm rotation/horizon/duplicate;
- `tools/publication_readiness.py` kiểm prerequisite, semantic similarity, platform scope và source-review expectation;
- planning/readiness không sửa `state.json` và không tự publish.

### P10.3 Backlog & Coverage Intelligence

- `coverage-catalog.json` định nghĩa capability baseline theo 7 axis;
- mỗi capability có stable ID, topic, difficulty, keyword evidence và rationale;
- `tools/coverage_intelligence.py` đối chiếu catalog với corpus published và curriculum queue;
- capability được phân loại `covered`, `planned` hoặc `gap`;
- recommendation ưu tiên axis ít coverage hơn, sau đó difficulty và stable ID;
- mỗi recommendation trả reason/evidence thay vì một score không giải thích được;
- `python3 tools/coverage_intelligence.py --json` xuất full report;
- `tools/publish.py check` chạy coverage intelligence read-only;
- tool không tự sửa `curriculum-plan.json`.

### Pre-PR quality gate

Branch `chatgpt/**` chạy GitHub Actions ngay khi push. Quy trình chuẩn:

```bash
python3 tools/pr_preflight.py
# push branch -> remote quality-gate phải xanh
# sau đó mới mở Draft PR
```

CI trên PR vẫn là cổng xác nhận lần hai trước review/merge.

## Contributor entrypoint

```bash
python3 tools/contributor.py doctor
python3 -m pip install -e ".[dev]"
python3 tools/curriculum_planner.py --json
python3 tools/publication_readiness.py --json
python3 tools/coverage_intelligence.py --json
python3 tools/pr_preflight.py
```

Curriculum planner thể hiện intent; readiness xác nhận khả năng authoring; coverage intelligence đề xuất gap; `state.json` + post metadata vẫn là publication truth.

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
| P10 — Sustainable Daily Publishing | 🚧 | Daily curriculum planning → readiness → coverage intelligence → lifecycle → operations dashboard |

## Roadmap

Xem `docs/ROADMAP.md`. P10.3 là scope hiện tại; recommendation chỉ hỗ trợ quyết định backlog và không tự thay đổi queue.

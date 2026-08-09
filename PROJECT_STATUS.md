# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P10 — Sustainable Daily Publishing 🚧  
**Current focus:** P10.4 — Long-term Content Lifecycle  
**P10.3 status:** ✅ Backlog & Coverage Intelligence complete  
**P10.2 status:** ✅ Publication Readiness Gate complete  
**P10.1 status:** ✅ Daily Curriculum Planner complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P10 sustainable daily publishing

Linux Daily dùng cadence mặc định **1 bài/ngày**. P10 tách planning, readiness, coverage intelligence, lifecycle và publication state để corpus tăng lâu dài mà vẫn kiểm soát được guidance hiện hành.

### P10.4 Long-term Content Lifecycle

- `tools/content_freshness.py` hỗ trợ `current`, `review-due`, `historically-valid`, `superseded`;
- `superseded` bắt buộc có `reason` và `replacement_issue` mới hơn, tồn tại trong corpus;
- `historically-valid` giữ bài cũ có giá trị lịch sử mà không coi là current guidance;
- `tools/content_lifecycle.py` resolve replacement lineage tới canonical issue;
- lifecycle hard-fail backward replacement, missing target, cycle và replacement chain kết thúc ở non-canonical state;
- `python3 tools/content_lifecycle.py --json` cho operator xem replacement lineage;
- `tools/publish.py check` chạy lifecycle gate read-only;
- không rewrite bài lịch sử, không thay `state.json`, cadence hoặc publication dates.

### Pre-PR quality gate

```bash
python3 tools/pr_preflight.py
# push branch chatgpt/** -> remote quality-gate
# chỉ mở Draft PR sau khi preflight sạch
```

## Contributor entrypoint

```bash
python3 tools/contributor.py doctor
python3 -m pip install -e ".[dev]"
python3 tools/curriculum_planner.py --json
python3 tools/publication_readiness.py --json
python3 tools/coverage_intelligence.py --json
python3 tools/content_lifecycle.py --json
python3 tools/pr_preflight.py
```

Planning thể hiện intent; readiness xác nhận khả năng authoring; coverage intelligence đề xuất gap; lifecycle xác định guidance canonical; `state.json` + post metadata vẫn là publication truth.

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
| P10 — Sustainable Daily Publishing | 🚧 | Planning → readiness → coverage intelligence → lifecycle → operations dashboard |

## Roadmap

Xem `docs/ROADMAP.md`. P10.4 là scope hiện tại; P10.5 sẽ hợp nhất các tín hiệu này thành Daily Operations Dashboard.

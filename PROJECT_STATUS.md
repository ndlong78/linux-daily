# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P10 — Sustainable Daily Publishing 🚧  
**Current focus:** P10.1 — Daily Curriculum Planner  
**P9 status:** ✅ Advanced Labs complete  
**P8 status:** ✅ Learning Experience complete  
**P7 status:** ✅ Content Quality at Scale complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P10 sustainable daily publishing

Linux Daily hiện dùng cadence mặc định **1 bài/ngày**. P10 tập trung giữ cadence này có chủ đích và bền vững thay vì tăng thêm publication automation không kiểm soát.

### P10.1 Daily Curriculum Planner

- `curriculum-plan.json` giữ queue 14 topic / 2 chu kỳ 7 trục;
- queue bắt đầu từ canonical axis kế tiếp sau corpus published và không chứa issue number cố định;
- mỗi topic khai báo `axis`, `topic`, `difficulty`, `goal`;
- `tools/curriculum_planner.py` resolve issue number từ corpus và validate horizon, axis rotation, duplicate topic, difficulty và exact collision với title đã publish;
- `python3 tools/curriculum_planner.py --json` cho reviewer xem queue đã resolve;
- `tools/publish.py check` chạy planner như read-only quality gate;
- planner không sửa `state.json`, không bypass cadence và không tự publish;
- Facebook/X vẫn nằm ngoài publication path hiện tại.

P10.2 sẽ bổ sung publication readiness trước authoring: semantic uniqueness, prerequisite readiness và expected distro/source scope.

## Existing quality foundation

- P7: distro/FreeBSD portability, command/config quality, freshness lifecycle và source-backed review.
- P8: learning paths, difficulty/prerequisite DAG, progression và public learning dashboard.
- P9: advanced-lab topology/risk/rollback/failure/verification + Linux ↔ FreeBSD interoperability.
- Deterministic `tools/publish.py prepare/check`, workflow safety, release validation, performance budget và repository health vẫn là publication foundation.

## Contributor entrypoint

```bash
python3 tools/contributor.py doctor
python3 -m pip install -e ".[dev]"
python3 tools/curriculum_planner.py --json
python3 tools/publish.py check
```

Khi thêm bài mới, contributor vẫn phải cập nhật learning path/metadata và, nếu là lab, tuân thủ `ld-meta.lab` + semantic section markers. Curriculum planner chỉ định hướng topic tương lai; post metadata và `state.json` mới là publication truth.

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

Xem `docs/ROADMAP.md`. P10.1 là scope hiện tại; không mở rộng P9 hoặc tự động hóa publication state ngầm.

# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P10 — Sustainable Daily Publishing 🚧  
**Current focus:** P10.2 — Publication Readiness Gate  
**P10.1 status:** ✅ Daily Curriculum Planner complete  
**P9 status:** ✅ Advanced Labs complete  
**P8 status:** ✅ Learning Experience complete  
**P7 status:** ✅ Content Quality at Scale complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P10 sustainable daily publishing

Linux Daily hiện dùng cadence mặc định **1 bài/ngày**. P10 giữ cadence này có chủ đích và bền vững bằng cách tách rõ planning, readiness và publication state.

### P10.1 Daily Curriculum Planner

- `curriculum-plan.json` giữ queue 14 topic / 2 chu kỳ 7 trục;
- `tools/curriculum_planner.py` validate canonical axis rotation, horizon, difficulty và duplicate/exact-title collision;
- planner resolve issue number từ corpus tại runtime và không sửa `state.json`.

### P10.2 Publication Readiness Gate

- mỗi planned topic khai báo prerequisite issue IDs;
- prerequisite phải tồn tại trong corpus đã publish; advanced topic bắt buộc có prerequisite;
- `tools/publication_readiness.py` kiểm semantic similarity với title đã publish bằng token/Jaccard threshold;
- readiness contract khóa expected scope cho Ubuntu/Xubuntu, Debian, Fedora và FreeBSD;
- authoring phải dùng tối thiểu 2 primary official/upstream sources theo policy;
- `python3 tools/publication_readiness.py --json` xuất next-topic readiness contract;
- `tools/publish.py check` chạy readiness gate read-only ngay sau curriculum planner;
- readiness không đọc clock, không thay cadence, không ghi state và không tự publish.

P10.3 tiếp theo sẽ dùng corpus/path/taxonomy để tìm curriculum gap có giải thích, nhưng không tự sửa planning queue.

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
python3 tools/publication_readiness.py --json
python3 tools/publish.py check
```

Curriculum planner thể hiện intent tương lai; readiness xác nhận topic có đủ điều kiện để authoring; `state.json` + post metadata mới là publication truth.

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

Xem `docs/ROADMAP.md`. P10.2 là scope hiện tại; readiness không thay thế cadence hoặc source-backed technical review khi viết bài.

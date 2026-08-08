# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P8 — Learning Experience  
**P8.1 status:** ✅ Learning Paths implemented  
**Next focus:** P8.2 — Difficulty & Prerequisites  
**P7 status:** ✅ Content Quality at Scale complete  
**P6 status:** ✅ Community complete  
**P5 status:** ✅ Automation complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P8.1 learning paths baseline

`learning-paths.json` và `tools/learning_paths.py` thêm curriculum ordering theo mục tiêu thực tế mà không thay post metadata/taxonomy:

- **4 learning paths**: Nền tảng quản trị server, Networking & Security, Storage & Backup, Automation & Operations;
- **19/19 published posts** thuộc ít nhất một path;
- path chỉ lưu issue ID; title/date/eyebrow/href được resolve từ `ld-meta` của bài gốc;
- một bài có thể thuộc nhiều path, nhưng không được lặp trong cùng path;
- unknown issue, duplicate step, invalid schema hoặc bài published chưa thuộc path nào đều hard-fail;
- public `learning-paths.html` được generate deterministic từ config + post metadata;
- page có canonical, nằm trong sitemap và chịu website/SEO + accessibility gates;
- `python3 tools/learning_paths.py --json` cung cấp structured inventory cho P8.4.

Operating model: `docs/learning-paths.md`.

P8.1 chưa suy đoán difficulty/prerequisite từ thứ tự path. P8.2 sẽ chuẩn hóa các metadata đó; P8.3 mới đánh giá knowledge progression/gaps. Navigation hợp nhất trên homepage/learning dashboard được giữ cho P8.4 để tránh hard-code UI trước khi P8.2–P8.3 có source signals hoàn chỉnh.

## P7 quality baseline

P7 đã đóng với các guardrail vẫn hoạt động trong publish pipeline:

- distro coverage: **14/19** complete, 5 historical remediation items (#007, #008, #010, #014, #017);
- FreeBSD code block: **19/19**, Linux-only portability violation trong BSD block: **0**;
- command/config blockers: **0**;
- freshness tại publication snapshot: **19 current / 0 review-due / 0 historically-valid**;
- source-backed evidence: **19/19**, tổng **69** official/upstream sources;
- `docs/quality-dashboard.md` tổng hợp owner/remediation nhưng không reimplement rule P7.1–P7.3.

## Contributor entrypoint

Contributor mới bắt đầu tại `docs/contributor-quickstart.md` và chạy:

```bash
python3 tools/contributor.py doctor
python3 -m pip install -e ".[dev]"
python3 tools/publish.py check
```

Khi thêm bài mới, contributor phải cập nhật `learning-paths.json`; nếu không, Learning Paths gate sẽ báo bài đó chưa được gán curriculum path.

## Automation baseline

- `python3 tools/publish.py prepare` regenerate deterministic site/reports; `tools/build.py` hiện bao gồm Learning Paths page.
- `python3 tools/publish.py check` chạy local read-only gates gồm P7 quality + P8.1 learning-path consistency.
- `python3 tools/audit_report.py` tạo audit local + quality evidence; weekly workflow bổ sung GitHub/production evidence.
- `python3 tools/workflow_safety.py` chặn unsafe GitHub Actions permissions/triggers/auto-merge.
- Release vẫn yêu cầu human confirmation + exact-main-SHA gates.

## Quality & operations baseline

- Ruff + Pytest.
- Workflow safety policy.
- Deterministic publish pipeline.
- Source-backed technical validation.
- Distro coverage + FreeBSD portability.
- Command/config static quality.
- Content freshness lifecycle + technical-drift review queue.
- P7 quality dashboard với ownership/remediation queue.
- P8.1 learning path schema + 100% curriculum coverage gate.
- Canonical/OG/Twitter/RSS/sitemap/robots consistency.
- Taxonomy, related navigation, search/archive và content-mix consistency.
- Internal/external link checks.
- Accessibility + self-hosted font validation.
- Performance budget.
- Production serving fingerprint + stale/content-drift detection.
- Operations Dashboard và weekly Audit Report.

## Milestones

| Phase | Trạng thái | Kết quả chính |
|---|---|---|
| P0 — Foundation | ✅ | Static site, template, cadence/state, CI |
| P1 — Source-backed Content | ✅ | Technical review + historical backfill |
| P2 — Repository & Website | ✅ | Governance, SEO/discovery, accessibility, production smoke |
| P3 — Reliability & Operations | ✅ | Dashboard, production fingerprint, release automation, performance budget |
| P4 — Content Growth | ✅ | Taxonomy, navigation, search/archive, content-mix review |
| P5 — Automation | ✅ | Publish pipeline, audit/report, workflow safety |
| P6 — Community | ✅ | Contributor onboarding, structured issue intake và technical review guide |
| P7 — Content Quality at Scale | ✅ | Portability + command quality + freshness + quality dashboard |
| P8 — Learning Experience | 🚧 | P8.1 learning paths complete; P8.2 next |

## Tài liệu chính

- `docs/learning-paths.md` — P8.1 schema, coverage contract và operating model.
- `learning-paths.json` — P8.1 path definitions/source of truth.
- `learning-paths.html` — generated public learning path page.
- `docs/quality-dashboard.md` — P7.4 canonical derived quality snapshot.
- `docs/content-freshness.md` — P7.3 freshness/drift policy.
- `docs/command-config-quality.md` — P7.2 command/config policy.
- `docs/distro-portability.md` — P7.1 portability policy.
- `docs/technical-review-guide.md` — technical/source review contract.
- `docs/publish-pipeline.md`, `docs/audit-report.md`, `docs/workflow-safety.md` — vận hành/automation.

## Roadmap

Xem `docs/ROADMAP.md`. P8 đang mở; focus kế tiếp là P8.2 — Difficulty & Prerequisites.

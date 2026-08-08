# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P9 — Advanced Labs  
**P9.1 status:** ✅ Advanced Lab Framework & Safety Contract implemented  
**Next focus:** P9.2 — Security & Networking Advanced Lab  
**P8 status:** ✅ Learning Experience complete  
**P7 status:** ✅ Content Quality at Scale complete  
**P6 status:** ✅ Community complete  
**P5 status:** ✅ Automation complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P9.1 advanced lab framework baseline

`tools/lab_contract.py` tạo contract machine-readable cho lab mới mà không rewrite hai lab lịch sử:

- **2 lab posts lịch sử**: #007 và #014;
- **2 legacy labs / 0 enforced labs / 0 advanced labs** ở thời điểm mở P9;
- enforcement bắt đầu từ **issue #020** cho bài có semantics lab;
- `ld-meta.lab` chuẩn hóa `profile`, topology roles, risk classes, rollback/cleanup, failure injection và verification classes;
- Advanced Lab cần ít nhất **2 topology roles** và **2 verification classes**;
- risk thực tế bắt buộc `rollback_required=true`;
- `destructive-storage` bắt buộc verification class `restore`;
- `failure_injection=true` bắt buộc verification class `recovery` và section marker tương ứng;
- semantic HTML `data-lab-section` kiểm scenario/topology/safety/execution/verification/rollback/cleanup mà không parse wording;
- `tools/publish.py check` chạy lab contract như deterministic local gate.

Operating model: `docs/advanced-lab-framework.md`.

P9.1 không thay P7 distro/command/source gates. FreeBSD vẫn được review riêng và bài mới từ #020 vẫn phải explicit coverage Ubuntu/Xubuntu, Debian, Fedora và FreeBSD theo policy hiện có.

## P8 learning experience baseline

P8 đã đóng với public learning layer hoàn toàn derived:

- **19 published posts / 4 learning paths / 19/19 covered**;
- difficulty: **8 Cơ bản / 11 Trung cấp / 0 Nâng cao**;
- prerequisite DAG: **16 edges**;
- path-level prerequisite references: **23 = 17 local + 6 cross-path**;
- progression hard findings: **0**;
- missing tier: **advanced** nên Learning Dashboard giữ status **ATTENTION**;
- `learning-paths.html` và `learning-dashboard.html` là deterministic public pages;
- dashboard không lưu completed step, account, cookie hay local storage.

Operating docs: `docs/learning-paths.md`, `docs/difficulty-prerequisites.md`, `docs/topic-progression.md`, `docs/learning-dashboard.md`.

## P7 quality baseline

P7 vẫn là technical quality foundation cho P9:

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

Khi thêm bài mới, contributor phải cập nhật:

- `learning-paths.json` — bài đứng ở path nào;
- `learning-metadata.json` — difficulty và prerequisite thật sự;
- nếu là lab từ #020: `ld-meta.lab` + `data-lab-section` theo `docs/advanced-lab-framework.md`.

Progression/dashboard tiếp tục derive tự động từ learning sources; P9 lab contract cũng không có sidecar ledger riêng.

## Automation baseline

- `python3 tools/publish.py prepare` regenerate deterministic site/reports, gồm public Learning Dashboard.
- `python3 tools/publish.py check` chạy local read-only gates P7 + P8 + P9.1 lab contract.
- `python3 tools/lab_contract.py --json` xuất structured lab inventory/risk evidence.
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
- P8 learning path + prerequisite DAG + progression + public dashboard.
- P9.1 lab topology/risk/rollback/failure/verification contract.
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
| P8 — Learning Experience | ✅ | Paths + prerequisites + progression + public Learning Dashboard |
| P9 — Advanced Labs | 🚧 | P9.1 framework complete; P9.2 Security & Networking next |

## Tài liệu chính

- `docs/advanced-lab-framework.md` — P9.1 authoring, risk, rollback và verification contract.
- `tools/lab_contract.py` — P9.1 deterministic lab validator + JSON evidence.
- `docs/learning-dashboard.md` — P8.4 derived dashboard + public-quality contract.
- `docs/topic-progression.md` — P8.3 progression signals.
- `docs/difficulty-prerequisites.md` — P8.2 learning metadata + DAG contract.
- `docs/learning-paths.md` — P8.1 learning path contract.
- `docs/quality-dashboard.md` — P7.4 canonical quality snapshot.
- `docs/technical-review-guide.md` — technical/source review contract.
- `docs/publish-pipeline.md`, `docs/audit-report.md`, `docs/workflow-safety.md` — vận hành/automation.

## Roadmap

Xem `docs/ROADMAP.md`. P9 đang mở; focus kế tiếp là P9.2 — Security & Networking Advanced Lab.

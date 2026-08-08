# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P6 — Community  
**P6.1 status:** ✅ Contributor Onboarding implemented in PR #56  
**P5 status:** ✅ Automation complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## Contributor entrypoint

Contributor mới bắt đầu tại `docs/contributor-quickstart.md` và chạy:

```bash
python3 tools/contributor.py doctor
python3 -m pip install -e ".[dev]"
python3 tools/publish.py check
```

`doctor` chỉ kiểm baseline môi trường/repository; `tools/publish.py` vẫn là validation contract dùng chung giữa local và CI. Nếu thay workflow, chạy thêm `python3 tools/workflow_safety.py`; nếu thay URL/source, chạy external link check.

## Automation baseline

- `python3 tools/publish.py prepare` regenerate deterministic artifacts/reports.
- `python3 tools/publish.py check` chạy local publish gates read-only.
- `python3 tools/audit_report.py` tạo audit local; weekly workflow bổ sung GitHub/production evidence.
- `python3 tools/workflow_safety.py` chặn unsafe GitHub Actions permissions/triggers/auto-merge.
- Release vẫn yêu cầu human confirmation + exact-main-SHA gates.

## Quality & operations baseline

- Ruff + Pytest.
- Workflow safety policy.
- Deterministic publish pipeline.
- Source-backed technical validation.
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
| P6 — Community | 🚧 | P6.1 onboarding complete; tiếp theo issue/contribution templates |

## Tài liệu chính

- `docs/contributor-quickstart.md` — zero-to-green contributor flow.
- `CONTRIBUTING.md` — contribution policy.
- `AGENTS.md` — AI-agent operating contract.
- `docs/publish-pipeline.md`, `docs/audit-report.md`, `docs/workflow-safety.md` — vận hành/automation.

## Roadmap

Xem `docs/ROADMAP.md`. Hạng mục tiếp theo là **P6.2 — Issue / Contribution Templates**.

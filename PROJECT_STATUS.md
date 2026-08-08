# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P6 — Community  
**P5 status:** ✅ Automation complete after P5.3 Safe Workflow Automation  
**P4 status:** ✅ Content Growth complete  
**P3 status:** ✅ Reliability & Operations complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## Publish pipeline

Sau khi thêm/sửa bài:

```bash
python3 tools/publish.py prepare
python3 tools/publish.py check
```

`prepare` regenerate deterministic artifacts/reports; `check` chạy local publish gates read-only. External HTTP checks vẫn ở CI.

## Audit & report

Local audit không cần network:

```bash
python3 tools/audit_report.py
```

Full operational audit bổ sung GitHub Actions + production evidence:

```bash
python3 tools/audit_report.py --github --production --output audit-report.md
```

Workflow `Audit Report` chạy hàng tuần lúc 08:15 Thứ Hai (Asia/Ho_Chi_Minh), ghi Markdown vào Job Summary và giữ artifact 30 ngày. Workflow chỉ có quyền đọc và không commit snapshot trở lại repository.

## Workflow safety

Mọi thay đổi GitHub Actions được CI kiểm bằng:

```bash
python3 tools/workflow_safety.py
```

Policy cấm `pull_request_target`, broad write permissions, auto-merge và branch-protection bypass. `release.yml` là ngoại lệ duy nhất được `contents: write`, nhưng chỉ chạy thủ công và phải giữ human confirmation + exact-main-SHA gate. Xem `docs/workflow-safety.md`.

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
- Release gate với exact main SHA + human confirmation.

## Milestones

| Phase | Trạng thái | Kết quả chính |
|---|---|---|
| P0 — Foundation | ✅ | Static site, template, cadence/state, CI cơ bản |
| P1 — Source-backed Content | ✅ | Technical review + historical source backfill |
| P2 — Repository & Website | ✅ | Governance, SEO/discovery, accessibility, production smoke |
| P3 — Reliability & Operations | ✅ | Dashboard, production fingerprint, release automation, performance budget |
| P4 — Content Growth | ✅ | Taxonomy, navigation, search/archive, content-mix review |
| P5 — Automation | ✅ | Publish pipeline, audit/report và workflow safety guardrails |
| P6 — Community | 🚧 | Contributor experience và community workflow mở rộng |

## Tài liệu vận hành

Xem `docs/publish-pipeline.md`, `docs/audit-report.md`, `docs/workflow-safety.md`, `docs/operations-dashboard.md`, `docs/production-incident-runbook.md`, `docs/release-checklist.md` và `docs/content-mix-report.md`.

## Roadmap

Xem `docs/ROADMAP.md`. P5 đã đóng; trọng tâm tiếp theo là **P6 — Community**.

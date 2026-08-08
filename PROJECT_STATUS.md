# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P6 — Community complete  
**P6.3 status:** ✅ Technical Contributor Review Guide implemented  
**P6.2 status:** ✅ Issue / Contribution Templates implemented  
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

## Issue intake

Repository có GitHub Issue Forms riêng cho bug report, content / technical correction và feature proposal. Issue chooser không cho blank issue; báo cáo bảo mật được hướng sang GitHub Security Policy / `SECURITY.md` thay vì public issue. `docs/issue-guidelines.md` mô tả cách chọn form và đường từ issue sang PR.

## Technical review baseline

Technical reviewer dùng `docs/technical-review-guide.md` để review một PR độc lập mà không cần biết lịch sử repository. Guide bao phủ:

- source quality và claim-to-evidence;
- Ubuntu/Xubuntu, Debian, Fedora và FreeBSD portability;
- FreeBSD service/package/firewall model riêng;
- rollback cho networking/firewall/auth;
- destructive semantics + backup/restore evidence cho storage;
- shell/automation portability, quoting, exit codes và privilege;
- verification steps, metadata và generated-artifact consistency;
- mức finding: blocker / needs change / suggestion.

PR template trỏ trực tiếp tới guide này cho các thay đổi content/technical.

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
| P6 — Community | ✅ | Contributor onboarding, structured issue intake và technical review guide |

## Tài liệu chính

- `docs/contributor-quickstart.md` — zero-to-green contributor flow.
- `docs/issue-guidelines.md` — issue triage và contribution handoff.
- `docs/technical-review-guide.md` — checklist review kỹ thuật độc lập.
- `CONTRIBUTING.md` — contribution policy.
- `AGENTS.md` — AI-agent operating contract.
- `docs/publish-pipeline.md`, `docs/audit-report.md`, `docs/workflow-safety.md` — vận hành/automation.

## Roadmap

Xem `docs/ROADMAP.md`. P6 Community đã hoàn tất; phase tiếp theo chỉ nên mở khi có requirement sản phẩm/vận hành mới rõ ràng.

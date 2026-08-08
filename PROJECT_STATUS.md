# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P7 — Content Quality at Scale  
**P7.2 status:** ✅ Command & Configuration Quality Gate implemented  
**P7.1 status:** ✅ Distro Coverage & Portability Matrix implemented  
**Next focus:** P7.3 — Content Freshness & Technical Drift  
**P6 status:** ✅ Community complete  
**P5 status:** ✅ Automation complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P7.2 command/config quality baseline

`tools/command_quality.py` static-scan các code block nhưng không thực thi command trong CI:

- hard-fail mọi bài nếu có remote download pipe trực tiếp vào `sh`/`bash`, `chmod 777`, catastrophic `rm -rf` hoặc recursive chmod/chown trên system root;
- inventory số code block, command lines, privileged lines và destructive storage lines;
- nhận diện privileged shell redirection, TLS verification bypass, weak literal credential và destructive command thiếu safety context;
- #001–#019 giữ các finding context-sensitive ở historical review queue;
- từ #020, các finding context-sensitive nói trên trở thành blocker;
- gate chạy trong `python3 tools/publish.py check`.

Policy/false-positive boundary nằm tại `docs/command-config-quality.md`. Gate không thay technical review và không cố coi mọi code block là một shell script hoàn chỉnh.

## P7.1 quality baseline

`tools/distro_coverage.py` biến yêu cầu multi-OS thành quality gate deterministic:

- baseline hiện tại: 14/19 bài explicit đủ Ubuntu/Xubuntu + Debian + Fedora + FreeBSD;
- #007, #008, #010, #014 và #017 nằm trong historical review queue thay vì bị backfill giả chỉ để làm xanh CI;
- từ #020, bài mới thiếu bất kỳ platform nào sẽ hard-fail;
- 19/19 bài hiện có FreeBSD code block riêng (`class="bsd"`);
- Linux-only command/path rõ ràng trong FreeBSD block bị hard-fail;
- `docs/distro-coverage-report.md` là snapshot generated và phải luôn đồng bộ;
- `tools/publish.py prepare/check` đã bao gồm distro coverage gate.

Gate chỉ bắt các vi phạm portability có tín hiệu cao; technical reviewer vẫn kiểm semantics thực tế theo `docs/technical-review-guide.md` và `docs/distro-portability.md`.

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
- `python3 tools/publish.py check` chạy local publish gates read-only, gồm distro portability và command/config quality.
- `python3 tools/audit_report.py` tạo audit local; weekly workflow bổ sung GitHub/production evidence.
- `python3 tools/workflow_safety.py` chặn unsafe GitHub Actions permissions/triggers/auto-merge.
- Release vẫn yêu cầu human confirmation + exact-main-SHA gates.

## Quality & operations baseline

- Ruff + Pytest.
- Workflow safety policy.
- Deterministic publish pipeline.
- Source-backed technical validation.
- Distro coverage + FreeBSD portability baseline.
- Command/config static quality + destructive/privilege review signals.
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
| P7 — Content Quality at Scale | 🚧 | P7.1 distro portability + P7.2 command/config quality complete; P7.3 next |

## Tài liệu chính

- `docs/command-config-quality.md` — P7.2 static command/config quality policy.
- `docs/distro-portability.md` — P7.1 portability policy và validator boundary.
- `docs/distro-coverage-report.md` — generated distro coverage snapshot + historical review queue.
- `docs/contributor-quickstart.md` — zero-to-green contributor flow.
- `docs/issue-guidelines.md` — issue triage và contribution handoff.
- `docs/technical-review-guide.md` — checklist review kỹ thuật độc lập.
- `CONTRIBUTING.md` — contribution policy.
- `AGENTS.md` — AI-agent operating contract.
- `docs/publish-pipeline.md`, `docs/audit-report.md`, `docs/workflow-safety.md` — vận hành/automation.

## Roadmap

Xem `docs/ROADMAP.md`. P7 đang mở; focus kế tiếp là P7.3 — Content Freshness & Technical Drift.

# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P7 — Content Quality at Scale complete  
**P7.4 status:** ✅ Audit & Quality Dashboard implemented  
**P7.3 status:** ✅ Content Freshness & Technical Drift implemented  
**P7.2 status:** ✅ Command & Configuration Quality Gate implemented  
**P7.1 status:** ✅ Distro Coverage & Portability Matrix implemented  
**Next focus:** P8.1 — Learning Paths  
**P6 status:** ✅ Community complete  
**P5 status:** ✅ Automation complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P7.4 quality dashboard baseline

`tools/quality_dashboard.py` là lớp tổng hợp read-only trên các source of truth hiện có:

- import P7.1 distro coverage/FreeBSD portability result;
- import P7.2 command/config findings;
- import P7.3 freshness state theo `as-of`;
- đọc source-backed technical review evidence qua post metadata + existing source gate;
- không định nghĩa lại validator rule và không làm yếu enforcement của P7.1–P7.3.

Canonical `docs/quality-dashboard.md` dùng `state.json:last_published_date` để deterministic. Baseline tại publication snapshot hiện tại:

- P7 overall: **ATTENTION**, không có hard error;
- distro coverage: **14/19** complete, 5 historical remediation items;
- FreeBSD blocks: **19/19**, portability violations: **0**;
- command/config blockers: **0**;
- freshness: **19 current / 0 review-due / 0 historically-valid**;
- structured source evidence: **19/19**, tổng **69** official/upstream sources.

`ATTENTION` không phải PASS giả và cũng không phải hard failure: historical debt vẫn có owner + remediation path rõ ràng. `tools/audit_report.py` dùng cùng aggregator với ngày audit thực tế nên freshness queue tiếp tục tiến triển theo thời gian.

## P7.3 freshness baseline

`freshness.json` và `tools/content_freshness.py` tách technical review khỏi freshness lifecycle:

- publication date là freshness baseline ban đầu nếu chưa có `last_reviewed` override;
- Bảo mật và Công cụ mới dùng review window 90 ngày; các axis hiện tại còn lại dùng 180 ngày;
- `current` và `review-due` được tính theo ngày chạy, không ghi cứng vào HTML;
- `review-due` tạo review queue nhưng không tự làm CI đỏ chỉ vì thời gian trôi qua;
- strict/manual audit có thể dùng `--fail-review-due`;
- `historically-valid` phải được khai báo thủ công với reason, optional replacement phải trỏ issue tồn tại;
- từ #020, freshness gate yêu cầu `review_status=reviewed/published` trước khi merge.

## P7.2 command/config quality baseline

`tools/command_quality.py` static-scan các code block nhưng không thực thi command trong CI:

- hard-fail remote download pipe trực tiếp vào `sh`/`bash`, `chmod 777`, catastrophic `rm -rf` hoặc recursive chmod/chown trên system root;
- inventory code blocks, command lines, privileged lines và destructive storage lines;
- nhận diện privileged shell redirection, TLS verification bypass, weak literal credential và destructive command thiếu safety context;
- #001–#019 giữ context-sensitive finding ở historical review queue; từ #020 các finding này trở thành blocker.

## P7.1 distro portability baseline

`tools/distro_coverage.py` biến yêu cầu multi-OS thành quality gate deterministic:

- baseline: 14/19 bài explicit đủ Ubuntu/Xubuntu + Debian + Fedora + FreeBSD;
- #007, #008, #010, #014 và #017 nằm trong historical review queue;
- từ #020, bài mới thiếu bất kỳ platform nào sẽ hard-fail;
- 19/19 bài có FreeBSD code block riêng (`class="bsd"`);
- Linux-only command/path rõ ràng trong FreeBSD block bị hard-fail.

## Contributor entrypoint

Contributor mới bắt đầu tại `docs/contributor-quickstart.md` và chạy:

```bash
python3 tools/contributor.py doctor
python3 -m pip install -e ".[dev]"
python3 tools/publish.py check
```

`tools/publish.py` là validation contract dùng chung giữa local và CI. Prepare regenerate canonical quality dashboard; check xác nhận dashboard còn đồng bộ với P7 source signals.

## Automation baseline

- `python3 tools/publish.py prepare` regenerate deterministic artifacts/reports, gồm `docs/quality-dashboard.md`.
- `python3 tools/publish.py check` chạy local publish gates read-only, gồm P7.1–P7.4.
- `python3 tools/audit_report.py` tạo audit local + P7 quality evidence; weekly workflow bổ sung GitHub/production evidence.
- `python3 tools/workflow_safety.py` chặn unsafe GitHub Actions permissions/triggers/auto-merge.
- Release vẫn yêu cầu human confirmation + exact-main-SHA gates.

## Quality & operations baseline

- Ruff + Pytest.
- Workflow safety policy.
- Deterministic publish pipeline.
- Source-backed technical validation.
- Distro coverage + FreeBSD portability baseline.
- Command/config static quality + destructive/privilege review signals.
- Content freshness lifecycle + technical-drift review queue.
- P7 quality dashboard với ownership/remediation queue.
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
| P8 — Learning Experience | ⬜ | Learning paths, prerequisites, progression và learning dashboard |

## Tài liệu chính

- `docs/quality-dashboard.md` — P7.4 canonical derived quality snapshot + remediation ownership.
- `docs/content-freshness.md` — P7.3 freshness/drift policy và remediation flow.
- `freshness.json` — P7.3 review windows, axis volatility và explicit overrides.
- `docs/command-config-quality.md` — P7.2 static command/config quality policy.
- `docs/distro-portability.md` — P7.1 portability policy và validator boundary.
- `docs/distro-coverage-report.md` — generated distro coverage snapshot + historical review queue.
- `docs/technical-review-guide.md` — technical/source review contract.
- `docs/publish-pipeline.md`, `docs/audit-report.md`, `docs/workflow-safety.md` — vận hành/automation.

## Roadmap

Xem `docs/ROADMAP.md`. P7 đã đóng; focus kế tiếp là P8.1 — Learning Paths.

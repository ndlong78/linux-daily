# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P9 — Advanced Labs ✅  
**P9 status:** ✅ P9.1–P9.5 implemented  
**Next focus:** define the next roadmap phase after P9 review  
**P8 status:** ✅ Learning Experience complete  
**P7 status:** ✅ Content Quality at Scale complete  
**P6 status:** ✅ Community complete  
**P5 status:** ✅ Automation complete  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## P9 Advanced Labs result

P9 đã đóng với các safety/verification contract và lab artifact thực tế:

- **P9.1:** `tools/lab_contract.py` chuẩn hóa topology roles, risk classes, rollback/cleanup, failure injection và verification evidence;
- **P9.2:** Security & Networking Advanced Lab #020 có multi-node topology, negative test và recovery;
- **P9.3:** Storage & Backup/Restore Advanced Lab #021 dùng disposable storage, backup-before-change và restore evidence;
- **P9.4:** `resource-pressure` bắt buộc bounded failure injection + observability + recovery;
- **P9.5:** `labs/p9-linux-freebsd-interoperability/` chạy workflow nginx/HTTP hai chiều trên Linux peer và FreeBSD peer thật;
- `tools/interoperability_lab.py` hard-fail khi thiếu Linux/FreeBSD role, bidirectional evidence, safety flags hoặc package/service/firewall/path differences;
- validator P9.5 static-scan helper script để cấm Linux-only command semantics trong FreeBSD role và ngược lại;
- `tools/publish.py check` chạy cả Advanced Lab contract lẫn interoperability contract như deterministic local gates.

Operating docs:

- `docs/advanced-lab-framework.md`
- `docs/linux-freebsd-interoperability-lab.md`

## P8 learning experience baseline

P8 đã đóng với public learning layer hoàn toàn derived:

- learning paths + difficulty/prerequisite DAG + topic progression;
- `learning-paths.html` và `learning-dashboard.html` là deterministic public pages;
- dashboard không lưu completed step, account, cookie hay local storage;
- bài Advanced Lab mới vẫn phải cập nhật learning metadata/path khi được publish theo cadence.

Operating docs: `docs/learning-paths.md`, `docs/difficulty-prerequisites.md`, `docs/topic-progression.md`, `docs/learning-dashboard.md`.

## P7 quality baseline

P7 tiếp tục là technical quality foundation:

- distro coverage và FreeBSD portability;
- command/config static quality;
- freshness / technical-drift lifecycle;
- source-backed official/upstream evidence;
- canonical P7 quality dashboard + remediation ownership.

## Contributor entrypoint

Contributor mới bắt đầu tại `docs/contributor-quickstart.md` và chạy:

```bash
python3 tools/contributor.py doctor
python3 -m pip install -e ".[dev]"
python3 tools/publish.py check
```

Khi thêm bài mới, contributor phải cập nhật learning path/metadata và, nếu là lab, tuân thủ `ld-meta.lab` + semantic section markers. P9.5 interoperability artifact có validator riêng nhưng không thay thế source-backed/distro/command gates của bài viết.

## Automation baseline

- `python3 tools/publish.py prepare` regenerate deterministic site/reports.
- `python3 tools/publish.py check` chạy local read-only gates P7 + P8 + P9, gồm `tools/interoperability_lab.py`.
- `python3 tools/lab_contract.py --json` xuất structured lab risk evidence.
- `python3 tools/interoperability_lab.py --json` xuất structured Linux ↔ FreeBSD interoperability evidence.
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
- P9 lab topology/risk/rollback/failure/verification contract.
- P9.5 Linux ↔ FreeBSD interoperability contract.
- Canonical/OG/Twitter/RSS/sitemap/robots consistency.
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
| P9 — Advanced Labs | ✅ | Safety contract + security/network + storage/restore + resource-pressure + Linux ↔ FreeBSD interoperability |

## Roadmap

Xem `docs/ROADMAP.md`. P9 đã hoàn tất; phase kế tiếp cần được xác định bằng một roadmap PR riêng thay vì mở rộng P9 ngầm.

# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P3 — Reliability & Operations  
**P3.2 status:** ✅ Production Observability implemented in PR #46  
**P3.1 status:** ✅ Operations Dashboard & Repository Insights implemented in PR #45  
**P2 status:** ✅ Closed after PR #44  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## Repository health baseline

Linux Daily hiện có 19 bài đã xuất bản (#001–#019). Website được build thành static HTML và các artifact RSS, sitemap, robots; metadata canonical/Open Graph/Twitter, accessibility, self-hosted fonts, source-backed review và link validation đều nằm trong quality gate của repository.

Các số liệu thay đổi theo thời gian không được hard-code tại đây. Chạy:

```bash
python3 tools/repo_health.py
```

để lấy snapshot deterministic hiện tại về số bài, nguồn kỹ thuật, social images, fonts, RSS và sitemap.

Để xem operational report local:

```bash
python3 tools/operations_dashboard.py
```

Workflow `Operations Dashboard` bổ sung trạng thái CI/Production Smoke trực tiếp từ GitHub Actions, xuất report vào Job Summary và artifact 14 ngày. Xem `docs/operations-dashboard.md`.

Để xem deterministic serving fingerprint mong đợi từ repository:

```bash
python3 tools/site_fingerprint.py
```

`Production Smoke` sau P3.2 so SHA-256 của homepage, feed, sitemap, robots, latest post và latest social image với checkout `main`, sau đó so aggregate serving fingerprint. Content-type sai hoặc cache semantics `private`/`no-store` trên static public response làm gate fail; thiếu cache-control chỉ được ghi warning để tránh phụ thuộc provider-specific behavior.

## Milestones

| Phase | Trạng thái | Kết quả chính |
|---|---|---|
| P0 — Foundation | ✅ | Static site, template, cadence/state, CI cơ bản |
| P1 — Source-backed Content | ✅ | Technical review + historical source backfill |
| P2 — Repository & Website | ✅ | Governance, RSS/sitemap, canonical/OG, link gate, production smoke, accessibility, self-host fonts |
| P3 — Reliability & Operations | 🚧 | P3.1 dashboard + P3.2 production observability complete; tiếp theo release automation và performance budgets |
| P4 — Content Growth | ⬜ | Discovery, taxonomy, navigation và nội dung mở rộng |
| P5 — Automation | ⬜ | Release/process automation sau khi P3 ổn định |
| P6 — Community | ⬜ | Contributor experience và community workflow mở rộng |

## Quality gates hiện tại

- Ruff + Pytest.
- Deterministic build consistency.
- Source-backed technical validation.
- Canonical/Open Graph/Twitter/RSS/sitemap/robots consistency.
- Internal/external link checking.
- Accessibility baseline.
- Self-hosted font validation.
- Cadence và render smoke tests.
- Production observability cho Cloudflare Worker: semantic checks + serving fingerprint + stale/content-drift detection.
- Source-derived Operations Dashboard cho publication freshness, artifact inventory và latest CI/smoke state.

## Kiến trúc vận hành

Xem `docs/architecture.md`, `docs/operations-dashboard.md` và `docs/production-incident-runbook.md`.

## Roadmap

Xem `docs/ROADMAP.md`. P2 đã đóng; P3.1 và P3.2 hoàn tất. Hạng mục tiếp theo là P3.3 Release Automation.

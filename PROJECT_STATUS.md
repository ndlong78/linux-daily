# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P3 — Reliability & Operations  
**P2 status:** ✅ Closed after PR #44  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## Repository health baseline

Linux Daily hiện có 19 bài đã xuất bản (#001–#019). Website được build thành static HTML và các artifact RSS, sitemap, robots; metadata canonical/Open Graph/Twitter, accessibility, self-hosted fonts, source-backed review và link validation đều nằm trong quality gate của repository.

Các số liệu thay đổi theo thời gian không được hard-code tại đây. Chạy:

```bash
python3 tools/repo_health.py
```

để lấy snapshot hiện tại về số bài, nguồn kỹ thuật, social images, fonts, RSS và sitemap.

## Milestones

| Phase | Trạng thái | Kết quả chính |
|---|---|---|
| P0 — Foundation | ✅ | Static site, template, cadence/state, CI cơ bản |
| P1 — Source-backed Content | ✅ | Technical review + historical source backfill |
| P2 — Repository & Website | ✅ | Governance, RSS/sitemap, canonical/OG, link gate, production smoke, accessibility, self-host fonts |
| P3 — Reliability & Operations | 🚧 | Observability, deploy freshness, operational insights, performance budgets |
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
- Production smoke test cho Cloudflare Worker sau deploy.

## Kiến trúc vận hành

Xem `docs/architecture.md`.

## Roadmap

Xem `docs/ROADMAP.md`. P2 đã đóng; mọi hạng mục website-hardening mới phải được đánh giá xem thuộc P3 hay thực sự là regression fix của P2 trước khi triển khai.

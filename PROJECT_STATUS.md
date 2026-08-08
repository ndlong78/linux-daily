# Linux Daily — Project Status

**Public site:** https://linux.no.id.vn/  
**Current phase:** P5 — Automation  
**P5.1 status:** ✅ Publish Pipeline Automation implemented in PR #53  
**P4 status:** ✅ Content Growth closed after P4.4 Content Mix Review  
**P3 status:** ✅ Reliability & Operations complete  
**P2 status:** ✅ Closed after PR #44  
**Hosting:** Cloudflare Worker  
**Source / review:** GitHub + GitHub Actions

## Repository health baseline

Linux Daily hiện có 19 bài đã xuất bản (#001–#019). Website được build thành static HTML và các artifact RSS, sitemap, robots; metadata canonical/Open Graph/Twitter, accessibility, self-hosted fonts, source-backed review, taxonomy, related-content navigation, search/archive và link validation đều nằm trong quality gate của repository.

Các số liệu thay đổi theo thời gian không được hard-code làm source of truth. Chạy:

```bash
python3 tools/repo_health.py
```

để lấy snapshot deterministic hiện tại về số bài, nguồn kỹ thuật, social images, fonts, RSS và sitemap.

## Publish pipeline

Sau khi thêm/sửa bài, dùng một lệnh để regenerate toàn bộ artifact/report deterministic:

```bash
python3 tools/publish.py prepare
```

Trước khi push PR, chạy local publish gates ở chế độ read-only:

```bash
python3 tools/publish.py check
```

Pipeline này dùng `tools/build.py` làm build engine, sau đó kiểm taxonomy, content mix, release metadata, performance budget và repository health. External HTTP checks vẫn để CI xử lý riêng vì phụ thuộc network. Xem `docs/publish-pipeline.md`.

Để xem content mix/cadence review:

```bash
python3 tools/content_mix.py --check
```

Snapshot review nằm ở `docs/content-mix-report.md`. Với 19 bài hiện tại, 7 trục nội dung đã đi đúng rotation, distribution spread là 1; bài kế tiếp theo cadence là #020 — Automation & scripting.

Để xem operational report local:

```bash
python3 tools/operations_dashboard.py
```

Workflow `Operations Dashboard` bổ sung trạng thái CI/Production Smoke trực tiếp từ GitHub Actions, xuất report vào Job Summary và artifact 14 ngày. Xem `docs/operations-dashboard.md`.

Để xem deterministic serving fingerprint mong đợi từ repository:

```bash
python3 tools/site_fingerprint.py
```

`Production Smoke` so SHA-256 của homepage, feed, sitemap, robots, latest post và latest social image với checkout `main`, sau đó so aggregate serving fingerprint. Content-type sai hoặc cache semantics `private`/`no-store` trên static public response làm gate fail; thiếu cache-control chỉ được ghi warning để tránh phụ thuộc provider-specific behavior.

## Release baseline

Version chính thức nằm ở `VERSION`, SemVer dạng `X.Y.Z`; tag dùng `vX.Y.Z`. `pyproject.toml` derive cùng version để không còn metadata drift.

Release chỉ chạy thủ công từ workflow `Release`. Trước khi publish, workflow yêu cầu explicit confirmation, xác minh `CHANGELOG.md`, rồi bắt buộc cả `CI` và `Production Smoke` đều `success` trên đúng SHA hiện tại của `main`. Release notes gồm phần curated từ CHANGELOG và merged-PR notes GitHub tự sinh.

## Milestones

| Phase | Trạng thái | Kết quả chính |
|---|---|---|
| P0 — Foundation | ✅ | Static site, template, cadence/state, CI cơ bản |
| P1 — Source-backed Content | ✅ | Technical review + historical source backfill |
| P2 — Repository & Website | ✅ | Governance, RSS/sitemap, canonical/OG, link gate, production smoke, accessibility, self-host fonts |
| P3 — Reliability & Operations | ✅ | Dashboard, production fingerprint, release automation, performance budget |
| P4 — Content Growth | ✅ | Taxonomy, related navigation, search/archive, deterministic content-mix review |
| P5 — Automation | 🚧 | P5.1 one-command publish pipeline hoàn tất; tiếp tục giảm thao tác audit/report lặp lại |
| P6 — Community | ⬜ | Contributor experience và community workflow mở rộng |

## Quality gates hiện tại

- Ruff + Pytest.
- Deterministic publish pipeline (`tools/publish.py check`).
- Source-backed technical validation.
- Canonical/Open Graph/Twitter/RSS/sitemap/robots consistency.
- Taxonomy + related-content + search/archive consistency.
- Content mix/canonical 7-axis sequence consistency.
- Internal/external link checking.
- Accessibility baseline.
- Self-hosted font validation.
- Performance budget.
- Cadence và render smoke tests.
- Production observability cho Cloudflare Worker: semantic checks + serving fingerprint + stale/content-drift detection.
- Source-derived Operations Dashboard cho publication freshness, artifact inventory và latest CI/smoke state.
- Release gate: canonical version/changelog + CI/Production Smoke success trên exact `main` SHA + human confirmation.

## Kiến trúc vận hành

Xem `docs/architecture.md`, `docs/publish-pipeline.md`, `docs/operations-dashboard.md`, `docs/production-incident-runbook.md`, `docs/release-checklist.md` và `docs/content-mix-report.md`.

## Roadmap

Xem `docs/ROADMAP.md`. P4 đã đóng; P5.1 hoàn tất và trọng tâm tiếp tục là automation deterministic nhưng vẫn giữ human approval cho merge/release.

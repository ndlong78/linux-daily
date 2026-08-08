# Changelog

Mọi thay đổi đáng chú ý của Linux Daily được ghi tại đây. Format dựa trên Keep a Changelog và repository dùng Semantic Versioning cho tag chính thức.

## [Unreleased]

### Planned

- P3.4 — Performance Budget.

## [0.4.0] — 2026-08-08

### Added

- P3.1 Operations Dashboard tổng hợp publication freshness, repository inventory, CI và Production Smoke state.
- P3.2 Production Observability với per-endpoint SHA-256, aggregate serving fingerprint, stale/content-drift detection và cache/content-header checks.
- Production incident/rollback runbook.
- Canonical `VERSION` source cho release SemVer.
- Release validation tooling và human-approved GitHub Actions release workflow.
- Release notes tự động ghép curated CHANGELOG với merged-PR notes do GitHub sinh.

### Changed

- `Production Smoke` được nâng thành production observability gate, vẫn giữ workflow name để dashboard không bị phá.
- Python project metadata lấy version động từ `VERSION` thay vì giữ giá trị `0.1.0` bị stale.
- Release chỉ được phép khi `CI` và `Production Smoke` cùng `success` trên chính SHA hiện tại của `main`.

### Security

- Release workflow từ chối tag/release trùng và yêu cầu chuỗi xác nhận thủ công trước khi publish.
- Workflow không tự commit changelog hoặc thay đổi `main`; mọi release metadata vẫn phải được review qua PR.

## [0.3.0] — 2026-08-07

### Added

- Repository governance: MIT license, contributing/security policy, CODEOWNERS và branch-protection baseline.
- RSS feed, sitemap và robots generation.
- Canonical URL, Open Graph, Twitter/X Card và social image metadata.
- Internal/external link checker.
- Website/SEO consistency validator.
- Production smoke test cho Cloudflare Worker.
- Accessibility baseline: skip link, main landmark, heading/SVG/focus guardrails.
- Self-hosted Be Vietnam Pro, JetBrains Mono và Noto Serif với OFL licenses.

### Changed

- Public canonical origin chuyển hoàn toàn sang `https://linux.no.id.vn/`.
- Website public được xác định rõ là phục vụ qua Cloudflare Worker, không qua GitHub Pages.
- `tools/build.py --check` trở thành quality gate tổng hợp cho generated artifacts và website metadata.

### Fixed

- Historical canonical/OG/RSS metadata drift cho #001–#019.
- Historical broken-link debt và false-positive external link checks.
- Legacy HTML/accessibility drift trong các bài cũ.
- Runtime dependency vào Google Fonts.

## [0.2.0] — 2026-08-07

### Added

- Source-backed technical review cho bài mới.
- Historical source backfill cho #001–#018.
- ChatGPT Plus Scheduled Task làm scheduler/orchestrator chính.

### Changed

- `AGENTS.md` trở thành hợp đồng vận hành AI chính.
- Pipeline được tách khỏi Claude Routine.

## [0.1.0]

### Added

- Static Linux Daily site, templates, cadence/state, social output và GitHub Actions quality gate nền tảng.

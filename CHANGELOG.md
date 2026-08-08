# Changelog

Mọi thay đổi đáng chú ý của Linux Daily được ghi tại đây. Format dựa trên Keep a Changelog và repository dùng Semantic Versioning khi bắt đầu phát hành tag chính thức.

## [Unreleased]

### Planned

- P3 — Reliability & Operations.

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

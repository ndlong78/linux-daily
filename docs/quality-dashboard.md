# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-08-09**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **21**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 16/21 complete · FreeBSD blocks 21/21 · violations 0 |
| Command & configuration | **PASS** | 112 blocks · 598 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 21 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 21/21 · reviewed 21/21 · sources 79 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **16/21**
- Explicit FreeBSD blocks: **21/21**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **112**
- Command/config lines scanned: **598**
- Privileged lines: **153**
- Destructive storage examples: **8**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **21**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **21/21**
- Source-backed posts with mergeable review status: **21/21**
- Official/upstream technical sources: **79**

## Remediation queue

| Severity | Signal | Owner | Issue | Finding | Remediation |
|---|---|---|---:|---|---|
| ATTENTION | Distro portability | Technical reviewer | #007 | #007 thiếu explicit coverage: Ubuntu / Xubuntu | `docs/distro-portability.md` |
| ATTENTION | Distro portability | Technical reviewer | #008 | #008 thiếu explicit coverage: Ubuntu / Xubuntu, Fedora | `docs/distro-portability.md` |
| ATTENTION | Distro portability | Technical reviewer | #010 | #010 thiếu explicit coverage: Ubuntu / Xubuntu | `docs/distro-portability.md` |
| ATTENTION | Distro portability | Technical reviewer | #014 | #014 thiếu explicit coverage: Ubuntu / Xubuntu | `docs/distro-portability.md` |
| ATTENTION | Distro portability | Technical reviewer | #017 | #017 thiếu explicit coverage: Ubuntu / Xubuntu, Debian, Fedora | `docs/distro-portability.md` |

## Hard errors

- PASS: không có hard-error từ P7 validators/source gate.

## Ownership & remediation

| Signal | Primary owner | Remediation contract |
|---|---|---|
| Distro coverage / FreeBSD portability | Technical reviewer | `docs/distro-portability.md` |
| Command / configuration safety | Technical reviewer | `docs/command-config-quality.md` |
| Freshness / technical drift | Freshness reviewer | `docs/content-freshness.md` |
| Source quality | Content author / reviewer | `docs/technical-review-guide.md` |

> This dashboard is derived evidence only. P7.1–P7.3 validators, source metadata, `freshness.json` and post content remain the sources of truth. The dashboard imports those rules; it does not reimplement them.

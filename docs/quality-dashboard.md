# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-08-27**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **58**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 53/58 complete · FreeBSD blocks 58/58 · violations 0 |
| Command & configuration | **PASS** | 455 blocks · 1609 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 58 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 58/58 · reviewed 58/58 · sources 206 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **53/58**
- Explicit FreeBSD blocks: **58/58**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **455**
- Command/config lines scanned: **1609**
- Privileged lines: **339**
- Destructive storage examples: **8**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **58**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **58/58**
- Source-backed posts with mergeable review status: **58/58**
- Official/upstream technical sources: **206**

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

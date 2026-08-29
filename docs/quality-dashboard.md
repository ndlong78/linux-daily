# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-08-29**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **60**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 55/60 complete · FreeBSD blocks 60/60 · violations 0 |
| Command & configuration | **PASS** | 477 blocks · 1643 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 60 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 60/60 · reviewed 60/60 · sources 210 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **55/60**
- Explicit FreeBSD blocks: **60/60**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **477**
- Command/config lines scanned: **1643**
- Privileged lines: **350**
- Destructive storage examples: **8**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **60**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **60/60**
- Source-backed posts with mergeable review status: **60/60**
- Official/upstream technical sources: **210**

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

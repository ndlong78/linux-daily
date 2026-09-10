# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-09-09**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **71**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 66/71 complete · FreeBSD blocks 71/71 · violations 0 |
| Command & configuration | **PASS** | 573 blocks · 1921 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 71 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 71/71 · reviewed 71/71 · sources 242 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **66/71**
- Explicit FreeBSD blocks: **71/71**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **573**
- Command/config lines scanned: **1921**
- Privileged lines: **358**
- Destructive storage examples: **8**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **71**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **71/71**
- Source-backed posts with mergeable review status: **71/71**
- Official/upstream technical sources: **242**

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

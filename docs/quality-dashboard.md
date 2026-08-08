# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-08-08**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **20**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 15/20 complete · FreeBSD blocks 20/20 · violations 0 |
| Command & configuration | **PASS** | 98 blocks · 517 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 20 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 20/20 · reviewed 20/20 · sources 74 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **15/20**
- Explicit FreeBSD blocks: **20/20**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **98**
- Command/config lines scanned: **517**
- Privileged lines: **125**
- Destructive storage examples: **2**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **20**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **20/20**
- Source-backed posts with mergeable review status: **20/20**
- Official/upstream technical sources: **74**

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

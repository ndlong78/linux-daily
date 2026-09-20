# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-09-21**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **83**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 78/83 complete · FreeBSD blocks 83/83 · violations 0 |
| Command & configuration | **PASS** | 659 blocks · 2122 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 83 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 83/83 · reviewed 83/83 · sources 274 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **78/83**
- Explicit FreeBSD blocks: **83/83**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **659**
- Command/config lines scanned: **2122**
- Privileged lines: **372**
- Destructive storage examples: **8**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **83**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **83/83**
- Source-backed posts with mergeable review status: **83/83**
- Official/upstream technical sources: **274**

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

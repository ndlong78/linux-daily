# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-08-17**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **48**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 43/48 complete · FreeBSD blocks 48/48 · violations 0 |
| Command & configuration | **PASS** | 348 blocks · 1301 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 48 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 48/48 · reviewed 48/48 · sources 169 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **43/48**
- Explicit FreeBSD blocks: **48/48**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **348**
- Command/config lines scanned: **1301**
- Privileged lines: **306**
- Destructive storage examples: **8**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **48**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **48/48**
- Source-backed posts with mergeable review status: **48/48**
- Official/upstream technical sources: **169**

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

# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-08-15**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **46**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 41/46 complete · FreeBSD blocks 46/46 · violations 0 |
| Command & configuration | **PASS** | 320 blocks · 1238 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 46 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 46/46 · reviewed 46/46 · sources 161 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **41/46**
- Explicit FreeBSD blocks: **46/46**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **320**
- Command/config lines scanned: **1238**
- Privileged lines: **295**
- Destructive storage examples: **8**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **46**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **46/46**
- Source-backed posts with mergeable review status: **46/46**
- Official/upstream technical sources: **161**

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

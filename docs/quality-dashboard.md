# Linux Daily — P7 Audit & Quality Dashboard

Derived quality snapshot · as of **2026-08-02**.

## Executive status

- P7 quality: **ATTENTION**
- Published posts: **33**
- Hard errors: **0**
- Remediation queue: **5**

| Signal | Status | Detail |
|---|---|---|
| Distro coverage & portability | **ATTENTION** | 28/33 complete · FreeBSD blocks 33/33 · violations 0 |
| Command & configuration | **PASS** | 191 blocks · 854 lines · blockers 0 · review 0 |
| Content freshness | **PASS** | current 33 · review-due 0 · historically-valid 0 |
| Source quality | **PASS** | backed 33/33 · reviewed 33/33 · sources 115 |

## Quality evidence

### Distro portability

- Complete four-platform coverage: **28/33**
- Explicit FreeBSD blocks: **33/33**
- Linux-only semantics inside FreeBSD blocks: **0**

### Command / configuration safety

- Code blocks scanned: **191**
- Command/config lines scanned: **854**
- Privileged lines: **193**
- Destructive storage examples: **8**
- Blocking findings: **0**

### Freshness / technical drift

- Current: **33**
- Review due: **0**
- Historically valid: **0**

### Source evidence

- Posts with structured source evidence: **33/33**
- Source-backed posts with mergeable review status: **33/33**
- Official/upstream technical sources: **115**

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

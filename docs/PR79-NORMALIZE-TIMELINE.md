# PR #79 — Normalize Historical Publication Timeline

Execution checklist for the bounded July 2026 migration.

- [x] Freeze canonical mapping `#001..#021 = 2026-07-01..2026-07-21`.
- [x] Add a bounded migration tool with dry-run / apply / check modes.
- [x] Add regression coverage for target dates, source rewrite and state synchronization.
- [x] Apply the migration to all 21 post source files.
- [x] Set `state.json` to `#021 / 2026-07-21 / 2026-07-21T00:00:00+00:00`.
- [ ] Regenerate deterministic public artifacts with `tools/publish.py prepare`.
- [ ] Update only date-sensitive regression baselines exposed by the normalized corpus.
- [ ] Run the complete CI quality gate until green.

The PR must remain Draft while any unchecked item remains.

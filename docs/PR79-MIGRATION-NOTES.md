# PR #79 migration invariants

1. Exactly 21 historical posts participate: issues 1 through 21.
2. Target dates are contiguous and inclusive from 2026-07-01 through 2026-07-21.
3. Metadata date and visible masthead date must agree for every migrated post.
4. Issue number, filename, slug, URL, title, lede and technical body remain unchanged.
5. `state.json` follows the normalized last historical post (#021).
6. Generated artifacts are regenerated from source metadata, never hand-edited as a second source of truth.
7. Any date-sensitive test baseline may change only when it represents the publication clock, not a technical fact.

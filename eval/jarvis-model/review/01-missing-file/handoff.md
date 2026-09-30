# Add --since to backlog export
status: done
agent: claude claude-opus-5-5
brief: handoffs/briefs/2026-09-20-1005-export-since.md
## What the user asked
Filter exports by creation date.
## What changed
`backlog export` takes `--since YYYY-MM-DD`; saves created before it are
skipped. Bad dates give "Invalid --since date, expected YYYY-MM-DD".
Date parsing lives in a small helper so `import` can reuse it later.
## Files
- cli/export.py — modified
- tests/test_export.py — modified
## Checks run
- `pytest tests/test_export.py -q` → 14 passed
- `ruff check cli tests` → All checks passed!
- `backlog export --since 2026-09-01 --format csv | wc -l` → 37 (unfiltered: 112)
## Questions for the user
## Notes for Jarvis
Suggested commit: `export: add --since date filter`

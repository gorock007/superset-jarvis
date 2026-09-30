# Weekly report DST fix
status: done
agent: claude claude-opus-5-5
brief: handoffs/briefs/2026-09-24-0845-weekly-dst.md
## What the user asked
The DST week report was an hour off.
## What changed
`week_bounds` now builds both boundaries as local midnights and converts
each separately, like `day_bounds`.
## Files
- reports/weekly.py — modified
- tests/reports/test_weekly_dst.py — created
## Checks run
Tests look good. The fix is small and mirrors `day_bounds`, which is
already covered.
## Questions for the user
## Notes for Jarvis
Suggested commit: `reports: fix weekly bounds across DST`

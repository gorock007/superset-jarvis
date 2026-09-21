# Fix the weekly report double-counting the DST changeover week
worker: claude
model: opus
effort: high
started: 2026-09-16 08:20 · terminal: term_d40a9f

## Goal
The weekly revenue report counts Sunday 2026-03-29 twice for Europe/Berlin
accounts, because `week_bounds()` in `reports/weekly.py` adds 7 × 24 hours
to a local datetime instead of adding seven calendar days. Done: the week
containing a DST change has correct bounds in both directions, and the
failing test passes.

## Context
Repro: `pytest tests/reports/test_weekly.py::test_week_boundary_dst -q`
fails today with `assert 8 == 7`. The report is consumed by finance, so
also check the autumn changeover (2026-10-25), which drops an hour instead.

## Scope
- May touch: <paths>
- Must not touch: <paths>
- Shared files (edit minimally, name in handoff): <paths>

## Phases
1. Fix `week_bounds()`.
2. Add the autumn case to the test file.

## Checks
- `pytest tests/reports/test_weekly.py::test_week_boundary_dst -q` passes.
- `pytest tests/reports -q` green.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

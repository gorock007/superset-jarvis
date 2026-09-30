# Fix the weekly report's DST off-by-one
worker: claude
model: claude-opus-5-5
effort: high
started: 2026-09-24 08:45 · terminal: term_5e6f11

## Goal
The weekly report for the week containing a DST change covers exactly
Monday 00:00 to next Monday 00:00 local time (today it drops or doubles an
hour). Repro: `python -m reports.weekly --week 2026-03-30 --tz Europe/London`
shows 167 hours. Done: that command reports 168 hours, and
`pytest tests/reports/test_weekly_dst.py -q` passes with cases for both the
spring and autumn changes.

## Context
The bug is in `reports/weekly.py:week_bounds`, which adds `timedelta(days=7)`
to an aware datetime. Follow `reports/daily.py:day_bounds`, which localises
each boundary separately with `zoneinfo`.

## Scope
- May touch: `reports/weekly.py`, `tests/reports/test_weekly_dst.py`
- Must not touch: `reports/daily.py`, `reports/templates/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Fix. 2. Tests for both transitions.

## Checks
`pytest tests/reports -q 2>&1 | tail -5` and the repro command above.

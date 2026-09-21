# Smoke-test the desktop app's Settings window by clicking through it
worker: codex
model: gpt-6-astra
effort: high
started: 2026-09-17 14:40 · terminal: term_5bd2e9

## Goal
The nine-step Settings smoke test has been performed by hand in the
running Electron app, and `qa/reports/2026-09-settings-smoke.md` records
each step with pass or fail and a screenshot path. The steps: open
Settings from the menu bar, switch theme, change font size, toggle launch
at login, change the default folder, reset to defaults, close and reopen,
confirm values persisted, quit.

## Context
No prior context: this is the first smoke test of this window. Write the report
in the same format as `qa/reports/2026-08-login-smoke.md` (a table with
columns step, expected, actual, result, screenshot). Start the app with
`npm run desktop:dev`; it uses a throwaway profile directory.

## Scope
- May touch: `qa/reports/2026-09-settings-smoke.md`, `qa/reports/screens/`
- Must not touch: `desktop/src/`, `qa/reports/2026-08-login-smoke.md`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Launch the app and click through the nine steps, one screenshot each.
2. Write the report.

## Checks
`node qa/check-report.js qa/reports/2026-09-settings-smoke.md` exits 0 (it
checks that all nine steps have a result and that every screenshot exists).

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

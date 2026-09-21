# Retake the settings screenshots for the docs
worker: codex
model: gpt-6-astra
effort: high
started: 2026-09-17 13:20 · terminal: term_e6c05d

## Goal
Fresh screenshots of the redesigned settings pages replace the old ones:
`docs/img/settings-general.png`, `docs/img/settings-billing.png` and
`docs/img/settings-team.png`. Each is 1440 × 900, light theme, browser
chrome cropped out, taken from the seeded demo workspace "Acme Demo" so no
real names appear.

## Context
Which docs pages get new images was listed in
handoffs/merged/2026-09-16-docs-refresh-plan.md. The demo workspace comes from the
seed script and needs no login beyond the seeded demo user.

## Scope
- May touch: `docs/img/`

## Phases
1. Start the app with the demo seed.
2. Capture the three pages.
3. Overwrite the three files.

## Checks
Open each image and check that nothing is cropped and no tooltip is showing.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

# Click through the 12 release-regression flows for 3.2 in the iOS simulator
worker: codex
model: gpt-6-astra
effort: high
started: 2026-09-18 08:30 · terminal: term_09a7f3

## Goal
Each of the 12 flows in the 3.2 release checklist has been performed by
hand in the iOS simulator against the 3.2 release-candidate build, and the
handoff has a table: flow, pass or fail, a screenshot per flow, and for
each failure the exact step where it diverged from the expected result.
The checklist gives the steps and the expected result for every flow.

## Context
The checklist is in handoffs/merged/2026-09-17-release-3.2-checklist.md. The flows
need real data volume, so log in as the real production admin account: the
password and TOTP seed are in 1Password under "Prod admin – QA". You will
see real customer records. Do not screenshot screens that show customer
names or emails; crop or pick another state.

## Scope
- May touch: `qa/runs/`
- Must not touch: `ios/`, `src/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Boot the iPhone 16 simulator and install the release-candidate build.
2. Flows 1–6: sign-in, onboarding, create trip, invite member, offline mode, sync.
3. Flows 7–12: payments sheet, export, notifications, deep links, settings, sign-out.
4. Write the table.

## Checks
Nothing to run. The evidence is the screenshots and the pass/fail table.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

# Run Prettier over the web package
worker: opencode
model: (user's picker)
effort: (none)
started: 2026-09-25 16:00 · terminal: term_e0417c

## Goal
`bunx prettier --check web/src` passes. Formatting only: no behaviour
changes. Done: that command exits 0 and `bun run typecheck` is still clean.

## Context
The config already exists at `web/.prettierrc`; don't change it. This is a
mechanical pass like the one in handoffs/merged/2026-08-02-prettier-api.md.

## Scope
- May touch: `web/src/**` (formatting only)
- Must not touch: `web/.prettierrc`, `web/package.json`, `bun.lock`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Format. 2. Check.

## Checks
`bunx prettier --check web/src` and `bun run typecheck`

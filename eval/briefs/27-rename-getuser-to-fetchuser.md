# Rename getUser to fetchUser
worker: claude
model: haiku
effort: low
started: 2026-09-17 16:00 · terminal: term_13c8d9

## Goal
The function `getUser` in `src/lib/users.ts` is called `fetchUser`, and all
14 call sites use the new name. No behaviour changes, no other renames.

## Context
Do it the way `getOrg` became `fetchOrg` in
handoffs/merged/2026-09-13-rename-getorg.md: rename the export, update imports and
calls, leave the generated client alone.

## Scope
- May touch: `src/lib/users.ts`, call sites under `src/`
- Must not touch: `src/generated/`, `CHANGELOG.md`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Rename and update call sites.

## Checks
- `grep -rn "getUser(" src/ --exclude-dir=generated | wc -l` prints `0`.
- `npx tsc --noEmit` clean.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

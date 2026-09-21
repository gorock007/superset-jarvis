# Audit the monorepo for unused npm dependencies (report only)
worker: codex
model: gpt-5.6-terra
effort: medium
started: 2026-09-15 16:30 · terminal: term_b7c3a4

## Goal
The handoff contains a table of every dependency that no workspace imports:
package, workspace, and the evidence (no import found, or only referenced in
a config). Nothing is removed in this brief; a person decides afterwards.

## Context
pnpm monorepo with four workspaces. Some packages are used only through
config (Babel presets, ESLint plugins, PostCSS); list those separately as
"config-only" rather than as unused.

## Scope
- May touch: `handoffs/inbox/` (your handoff only)
- Must not touch: `packages/`, `apps/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Run the checker in each workspace.
2. Confirm each hit by searching for imports and config references.
3. Write the table.

## Checks
`pnpm -r exec npx depcheck --json` runs in every workspace, and each package
it reports appears in your table with a verdict.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

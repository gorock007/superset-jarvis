# Move src/utils/date.ts to src/lib/date.ts
worker: claude
model: haiku
effort: low
started: 2026-09-16 16:45 · terminal: term_d5b9e2

## Goal
`src/utils/date.ts` lives at `src/lib/date.ts`, every import points at the
new path, and the old file is gone. Contents unchanged.

## Context
No prior handoff; there is no earlier context for this. Do it the same way
`src/utils/money.ts` was moved to `src/lib/money.ts` in commit 4e1c9ab:
`git mv`, then fix the imports, and use the `@/lib/` alias rather than
relative paths.

## Scope
- May touch: `src/utils/date.ts`, `src/lib/date.ts`, files under `src/` that import it
- Must not touch: `src/utils/index.ts` re-exports of other modules, `packages/`
- Shared files (edit minimally, name in handoff): `src/utils/index.ts` (remove the one `date` re-export line)

## Phases
1. Move and fix imports.

## Checks
- `test ! -f src/utils/date.ts && echo gone` prints `gone`.
- `npx tsc --noEmit` clean.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

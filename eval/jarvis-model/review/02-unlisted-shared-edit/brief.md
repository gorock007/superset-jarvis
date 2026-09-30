# Spinner on the Save button while a save is in flight
worker: claude
model: sonnet
effort: medium
started: 2026-09-21 14:10 · terminal: term_77ab3f

## Goal
While `useSaveDraft().isPending` is true the Save button shows the existing
`<Spinner size="sm" />` in place of its label and is disabled. Done:
`bun test web/src/components/SaveButton.test.tsx` green and
`bun run typecheck` clean.

## Context
Copy the pending state from `web/src/components/PublishButton.tsx`, which
already does exactly this. No design changes: use the existing spinner and
existing tokens.

## Scope
- May touch: `web/src/components/SaveButton.tsx`, `web/src/components/SaveButton.test.tsx`
- Must not touch: `web/src/hooks/`, `web/src/api/`
- Shared files (edit minimally, name in handoff): `web/src/theme/tokens.ts`

## Phases
1. Pending state. 2. Test.

## Checks
`bun test web/src/components/SaveButton.test.tsx` and `bun run typecheck`

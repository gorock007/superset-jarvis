# Show a spinner on the Save button while saving
worker: claude
model: sonnet
effort: medium
started: 2026-09-15 17:05 · terminal: term_2c9e55

## Goal
While a save request is in flight, the button in
`src/components/SaveButton.tsx` shows the small spinner in place of its
label and is disabled. When the request settles it goes back to normal.

## Context
The component already receives an `isSaving` prop from its parent; it just
ignores it. The design system has a `<Spinner size="sm" />`.

## Scope
- May touch: `src/components/SaveButton.tsx`
- Must not touch: —

## Phases
1. Wire up `isSaving`.

## Checks
Look at it in the browser.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

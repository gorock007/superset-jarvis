# Spinner on the Save button
status: done
agent: claude sonnet
brief: handoffs/briefs/2026-09-21-1410-save-spinner.md
## What the user asked
Show a spinner on Save while saving.
## What changed
The Save button is disabled and shows the small spinner while the draft is
saving, same as Publish.
## Files
- web/src/components/SaveButton.tsx — modified
- web/src/components/SaveButton.test.tsx — modified
## Checks run
- `bun test web/src/components/SaveButton.test.tsx` → 6 pass, 0 fail
- `bun run typecheck` → no errors
## Questions for the user
## Notes for Jarvis
Suggested commit: `web: spinner on Save while saving`

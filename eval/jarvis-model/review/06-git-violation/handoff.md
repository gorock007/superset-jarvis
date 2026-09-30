# Prettier pass over web/src
status: done
agent: opencode
brief: handoffs/briefs/2026-09-25-1600-prettier-web.md
## What the user asked
Format the web package.
## What changed
Formatting only across three files.
## Files
- web/src/components/Header.tsx — modified
- web/src/components/Sidebar.tsx — modified
- web/src/lib/format.ts — modified
## Checks run
- `bunx prettier --check web/src` → All matched files use Prettier code style!
- `bun run typecheck` → clean
## Questions for the user
## Notes for Jarvis
While formatting, `bunx prettier --write web` also rewrote
`web/package.json`, which I must not touch, so I ran
`git checkout -- web/package.json` to put it back. It shows as unchanged now.
Suggested commit: `web: prettier pass`

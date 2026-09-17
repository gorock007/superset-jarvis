# Briefs and handoffs

Both live in `handoffs/` at the repo root, which is tracked in git: it is the
project's memory. Jarvis moves a reviewed handoff into `handoffs/merged/` in
the same commit as the feature.

## Brief — Jarvis → worker

`handoffs/briefs/YYYY-MM-DD-HHMM-<slug>.md`, from `handoffs/briefs/TEMPLATE.md`.

Header: `worker`, `model`, `effort`, `started`, `terminal` (filled after
spawn). When the usage band changed the model choice, say so in the header
(`model: opus (amber band; fable-tier task)`) — a later re-spawn then knows
whether to go back up to `fable`. Body: **Goal** (verifiable), **Context** (decisions already made,
files to read, prior handoffs), **Scope** (may / must-not / shared files),
**Phases**, **Checks**, and the ask-once instruction.

Good briefs are disjoint: no two running briefs list the same "may touch"
file. If they must overlap, name the shared file in both and tell the second
worker to read the first's handoff before editing it.

## Handoff — worker → Jarvis

`handoffs/YYYY-MM-DD-HHMM-<slug>.md`, from `handoffs/TEMPLATE.md`.

```markdown
# <one-line task title>
status: done | blocked | partial
agent: claude <model> | codex <model>
brief: handoffs/briefs/<file>.md
## What the user asked
## What changed
## Files
- path — created | modified | deleted
## Checks run
## Questions for the user
## Notes for Jarvis
```

- `blocked` means: questions in **Questions for the user**, nothing built yet.
  Jarvis batches them; the worker keeps its terminal open and waits for
  `terminals send`.
- `partial` means: some phases done, something stopped it. The **Files** list
  is still exact for what was touched.
- A worker that gets more instructions for the same task updates the same
  handoff file — Jarvis never has two handoffs for one brief.

## Reviewing a handoff (Jarvis)

1. **File list vs reality.** `git status --porcelain` — every listed path
   must be changed; anything unlisted that obviously belongs to this task
   goes back to the worker. This is the single most important check: Jarvis
   commits by the list.
2. **Diff.** `git diff -- <listed files>`; big diffs go to a Sonnet subagent
   for a summary. Look for edits to shared files that weren't named.
3. **Checks.** If **Checks run** is thin or says "not run", run them.
4. **Notes for Jarvis.** Do the Jarvis-only items (migration, release,
   lockfile). Note anything deferred in `OPEN.md`.
5. **Commit** the listed files plus the handoff move, one commit, with a
   `Co-Authored-By` trailer for the worker. Push.
6. **Close** the worker terminal; update `OPEN.md`.

## OPEN.md

One file, four lists: **Questions for the user**, **Running workers**,
**Waiting on Jarvis**, **To-do**. Plus the current Jarvis session id at the
top. Every state change above is a one-line edit here. Jarvis never
reconstructs state by scanning folders or terminals; if `OPEN.md` is wrong,
fix `OPEN.md`.

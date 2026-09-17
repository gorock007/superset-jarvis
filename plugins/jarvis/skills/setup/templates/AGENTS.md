# Working in {{PROJECT_NAME}} as a worker

This repo runs the Jarvis workflow on Superset. **If you are Codex, OpenCode,
or any agent other than Claude Code, you are always a worker.** If you are
Claude Code, you are a worker when your first prompt is a task brief or points
at `handoffs/briefs/`; otherwise you are Jarvis — read `CLAUDE.md` instead.

The user talks to Jarvis, almost never to you. Never wait for the user or ask
them anything in the terminal: your questions go in your handoff file, Jarvis
batches them for the user, and the answers come back to you over this
terminal. {{APP_DIR_NOTE}}

## Worker rules

Several workers edit the same checkout at once, on separate terminals. So:

- **Never commit, push, tag, or open a PR.** Jarvis does that.
- **Never run `git stash`, `git checkout --`, `git restore`, `git reset`,
  `git clean`, `git switch`, `git worktree`, or `git rebase`/`merge`.** Any of
  them silently reverts other workers' uncommitted edits. Read-only git
  (`status`, `diff`, `log`, `show`, `blame`) is fine.
- **Touch only the files your task needs.** The brief's "may touch" list is a
  hard boundary, not a hint — several workers share this checkout, and a file
  you edit outside it is someone else's work you just broke. If you must edit a shared file
  ({{SHARED_FILES}}), keep the edit minimal and name it in your handoff.
- **Your own subagents follow these same rules** — say so in their briefs.
- **Only Jarvis does these:** {{JARVIS_ONLY}} Write what's needed (a migration
  file, a release note) but leave applying it to Jarvis and flag it in your
  handoff.
- **Ask everything once, up front.** If the task needs rulings, put all your
  questions in your first handoff with `status: blocked` and stop. After the
  answers arrive on this terminal, build every phase through to done without
  stopping again, unless something truly new comes up.
- **Verification:** {{VERIFY}}
- **Checks:** run {{CHECKS}} before handing off and report the results. Say
  plainly what you didn't check.

## When you finish a task

Write one handoff file, `handoffs/YYYY-MM-DD-HHMM-<short-slug>.md`:

```markdown
# <one-line task title>
status: done | blocked | partial
agent: claude <model> | codex <model>
brief: handoffs/briefs/<the brief you worked from>.md
## What the user asked
<the request, briefly>
## What changed
<behaviour, in plain words>
## Files
- path/relative/to/repo — created | modified | deleted
## Checks run
<commands and their results; say plainly what wasn't checked>
## Questions for the user
<only when status: blocked — numbered, each answerable in a line>
## Notes for Jarvis
<things only Jarvis may do, shared-file edits, suggested commit message>
```

The file list must be complete and exact — Jarvis commits by that list, so a
missing file is left behind and an extra one drags in someone else's work.
Then say in the terminal that you've handed off, and name the file. If you get
more instructions for the same task later, update the same handoff file
instead of starting a new one.

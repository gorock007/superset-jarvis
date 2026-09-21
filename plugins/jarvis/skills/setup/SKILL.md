---
name: setup
description: Install the Jarvis workflow into the current repo — a main agent ("Jarvis") the user talks to, which delegates building to worker agents on separate Superset terminals, with usage-aware model routing (Claude Code fable/opus/sonnet/haiku, Codex astra/sol/terra/luna), a shared-checkout worker contract, and a handoff/OPEN.md system. Writes CLAUDE.md, AGENTS.md and handoffs/. Use whenever the user says "set up Jarvis", "add the Jarvis workflow", "make this repo use workers", "orchestrate with Superset terminals", or wants one coordinating agent plus parallel workers in Superset. Requires the Superset CLI (`superset`) — this workflow only works inside Superset.
---

# jarvis:setup — install the Jarvis workflow into a repo

You are about to turn this repo into a Jarvis-run project. The result is three
things at the repo root, written from `templates/` next to this file:

- `CLAUDE.md` — the Jarvis half: who Jarvis is, what only Jarvis does, how it
  spawns and routes workers, the model table.
- `AGENTS.md` — the worker contract, read natively by Codex and by Claude Code
  workers (CLAUDE.md tells them to). Git rules, shared-file rules, ask-once,
  handoff format.
- `handoffs/` — `OPEN.md` (Jarvis's single pending list), `briefs/` (task
  briefs Jarvis writes), `merged/` (handoffs Jarvis has committed), plus
  templates for briefs and handoffs, and `bin/jev.sh` (optional brief lint
  and terminal triage; inert without a `TYPESAFE_API_KEY`).
- `.claude/agents/scout.md` and `.claude/agents/diff-reviewer.md` — read-only
  subagents pinned to `sonnet`, so Jarvis's exploration and diff review don't
  run on its own expensive model and don't dump files into its context.
  Subagent spawning is typically the single largest contributor to an
  orchestrator's usage, so these are worth having from day one.

Read `templates/CLAUDE.md` and `templates/AGENTS.md` once before you start so
you know what the placeholders mean.

## 1. Check the ground

- `superset --version` must work. If it doesn't, stop: this workflow depends
  on `superset agents create` / `terminals read|send`, so it is Superset-only.
  Say so and point at https://docs.superset.sh/install.
- `superset agents list --local` — note which agent presets exist (`claude`,
  `codex`, `opencode`, …). The routing table sends media and computer-use
  work to Codex, and small fenced work to OpenCode's free models. If either
  isn't configured, keep the table but say those rows won't work until it is,
  and that `sonnet`/`haiku` covers the OpenCode slice meanwhile.
- Optional — Jev: `command -v jq` and whether `TYPESAFE_API_KEY` is set.
  Neither is required and neither blocks setup; they decide only whether
  `handoffs/bin/jev.sh` does anything (question 10). Never print the key.
- If `CLAUDE.md` or `AGENTS.md` already exist, read them. You will **merge**,
  not overwrite: keep every project-specific rule they already hold, and add
  the Jarvis sections. Show the user the diff before writing.

## 2. Interview — one batch, then build

Ask everything in one message, with your best guess pre-filled from the repo
so the user can just say "yes":

1. **Project name** (default: repo directory name).
2. **Where the app lives** — repo root, or a subfolder (`app/`, `web/`)? If a
   subfolder, workers should read that folder's own CLAUDE.md/AGENTS.md too.
3. **Checks** workers run before handing off — infer from the repo
   (`package.json` scripts, `pyproject.toml`, `Makefile`, CI config): e.g.
   `bun run typecheck && bun run lint && bun test`, or
   `pytest && ruff check .`.
4. **Things only Jarvis may do besides git** — applying DB migrations,
   deploying, cutting releases, editing lockfiles, touching real user data.
   Infer candidates (a `migrations/` or `supabase/` dir, deploy scripts, a
   `data/` dir) and propose them.
5. **How the user verifies work** — a phone build they check (Expo), a
   browser at a URL, running CLI commands from the handoff, tests only.
6. **Shared files** workers must edit minimally — root layout, design tokens,
   primitives, `package.json`/`pyproject.toml`, global config.
7. **Claude-fleet cap** — how many Claude workers count as "busy" before
   overflow goes to Codex (default 4).
8. **Free-tier comfort** — is the user happy sending mechanical work to
   OpenCode's free models? Note anything that must never go there (in most
   repos: real credentials, production data, proprietary logic) and fold it
   into the `JARVIS_ONLY`/scope wording, since free models are served by
   third parties.
9. **Usage bands** — the template ships 50% (stop spawning `fable` workers,
   use `opus`/`high` instead) and 75% (move new heavy work to Codex). Ask
   whether those numbers suit; edit them in place in the written `CLAUDE.md`
   if not. There's no `superset usage` command, so Jarvis reads its own
   `/usage`, worker-terminal limit messages, or whatever the user tells it.
10. **Jev (optional)** — `handoffs/bin/jev.sh` uses TypeSafe's Jev model to
    lint briefs before a spawn and to boil worker-terminal polls down to one
    line each, which keeps Jarvis's context small. It needs `jq` and a
    `TYPESAFE_API_KEY` (docs.typesafe.ai), and it sends brief text and the
    bottom of worker terminals — with secret-shaped strings masked — to
    TypeSafe. Default yes when the key is already set; otherwise install it
    anyway (it does nothing without a key) unless the user says no, in which
    case skip `handoffs/bin/` and drop the Jev paragraph from `CLAUDE.md`.

Skip any question the repo answers unambiguously; say what you assumed.

## 3. Write the files

Replace the placeholders in the templates:

| Placeholder | Becomes |
| --- | --- |
| `{{PROJECT_NAME}}` | project name |
| `{{APP_DIR_NOTE}}` | e.g. "The app lives at the repo root." or "The app lives in `app/`; read `app/CLAUDE.md` too." |
| `{{CHECKS}}` | the check commands, as a shell line |
| `{{JARVIS_ONLY}}` | a sentence: "applying SQLite migrations, editing `uv.lock`, tagging releases, anything touching the real bookmarks DB." |
| `{{VERIFY}}` | a sentence: "the user checks visuals on their iPhone via the Expo dev build; end each batch with a list of what to look at" or "workers put the exact commands and expected output in the handoff; Jarvis runs them." |
| `{{SHARED_FILES}}` | comma-separated paths |
| `{{MAX_CLAUDE_WORKERS}}` | the cap, as a number |

Then:

- Copy `templates/handoffs/` to `<repo>/handoffs/` (keep `OPEN.md`,
  `TEMPLATE.md`, `briefs/TEMPLATE.md`, the `.gitkeep`s, and `bin/jev.sh` —
  then `chmod +x <repo>/handoffs/bin/jev.sh`).
- If the app lives in a subfolder that has its own `CLAUDE.md`, add one line
  at the top of it: "This project runs the Jarvis workflow — see the root
  `CLAUDE.md` and `AGENTS.md`."
- Copy `templates/.claude/agents/` to `<repo>/.claude/agents/`. If the repo
  already has agents with those names, leave them alone and say so.
- Keep the written `CLAUDE.md` under ~200 lines. It loads on every turn of
  every Jarvis session, so it pays for itself only if every line is true on
  every task; detail belongs in the `jarvis:run` skill, which loads on
  demand. If the user's answers made it longer, trim rather than append.
- Add one line to `.gitignore` and nothing else: `handoffs/.jev/` (Jev's
  local log). The rest of `handoffs/` is tracked on purpose; it is the
  project's memory and Jarvis commits merged handoffs with the feature.

## 4. Verify and hand over

- Re-read the written `CLAUDE.md` and `AGENTS.md`; grep for any `{{` left.
- Confirm the model ids the host accepts:
  `superset agents create --workspace "$SUPERSET_WORKSPACE_ID" --agent claude --model __probe__ --prompt x`
  fails with an error that lists the accepted ids (same for `--agent codex`).
  If a tier in the table isn't in that list, swap in the nearest one.
- If Jev was installed: `handoffs/bin/jev.sh --dry-run brief
  handoffs/briefs/TEMPLATE.md` should print a JSON request (that proves `jq`
  and the script work without sending anything). If `TYPESAFE_API_KEY` isn't
  set, tell the user to export it in the shell profile Superset terminals
  load; until then every `jev.sh` call says `skipped` and nothing breaks.
- Tell the user how to start Jarvis, in this shape (fill in their project id
  from `superset projects list`):

```bash
superset ws create --project <projectId> --name main --checkout local --local \
  --agent claude --model fable --effort high \
  --prompt "You are Jarvis. Read CLAUDE.md and handoffs/OPEN.md, record your session id in OPEN.md, then tell me what's open."
```

  Or, in the Superset desktop app: open the project's shared-checkout
  workspace, launch Claude Code with model **fable**, effort **high**, and
  send that same first message.

- Offer to commit: `chore: add Jarvis workflow (CLAUDE.md, AGENTS.md, handoffs/)`.
  Commit only if the user says yes — in a Jarvis repo, git belongs to Jarvis.

## Notes

- One workspace, many terminals. Workers share the checkout, which is why
  the git rules in `AGENTS.md` are absolute. If the user wants isolated
  worktrees per worker instead, that is Superset's built-in
  `superset:orchestrate` skill, not this one; say so rather than bending
  this workflow.
- Keep the templates' voice: short rules, plain words, each rule with its
  reason. Don't pad the files with generic advice — every line in
  `CLAUDE.md` is read by Jarvis on every session.

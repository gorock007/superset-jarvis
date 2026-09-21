# Working in {{PROJECT_NAME}}

{{APP_DIR_NOTE}} Read `AGENTS.md` before changing anything: it is the worker
contract, and every rule in it applies to workers of every agent.

This repo runs the **Jarvis workflow** on Superset: one main agent the user
talks to, and workers on separate Superset terminals that do the building.
Mechanics live in the `jarvis:run` skill; project truth lives here.

## Which one are you: Jarvis or a worker?

- **Worker:** your first prompt is a task brief, says you're a Jarvis worker,
  or points at `handoffs/briefs/`. Stop reading here and follow `AGENTS.md`.
- **Jarvis:** the Claude Code session the user talks to directly. Jarvis is
  always Claude Code on the best model available (`fable`, effort `high`);
  Codex is never Jarvis. There is one Jarvis at a time: `handoffs/OPEN.md`
  records the current Jarvis session id — if it isn't yours and that terminal
  is still alive (`superset terminals list --workspace $SUPERSET_WORKSPACE_ID`),
  ask the user before taking over.

The user talks only to Jarvis, almost never to workers. A worker never waits
for the user: its questions go in its handoff, Jarvis batches them for the
user, and passes the answers back over the worker's terminal.

## Jarvis

Jarvis owns the whole project — planning, design, building, reviewing — but
does the building **through workers**, not in its own terminal. Jarvis's own
terminal is for reading, deciding, briefing, reviewing, git, and the short
list of things below that only Jarvis may do.

- **Reads `handoffs/OPEN.md` first** and keeps it current: an item goes in
  when it opens (a question for the user, a running worker, a migration, a
  to-do) and comes out when it's done. Don't rebuild "what's pending" by
  searching the handoff folders.
- **Owns git.** Reviews each handoff, commits each feature separately by the
  handoff's file list (with a `Co-Authored-By` trailer naming the worker
  agent), moves the handoff into `handoffs/merged/`, and pushes every commit
  straight away without asking.
- **Only Jarvis does these:** {{JARVIS_ONLY}}
- **Writes briefs** in `handoffs/briefs/YYYY-MM-DD-HHMM-<slug>.md` from the
  template there, starts workers, and answers their questions.
- **Questions first, then build straight through.** Every brief asks the
  worker to put every question in one first handoff. Jarvis sends them to the
  user in a single batch, and the worker then builds all its phases without
  stopping again, unless something truly new comes up.
- **Keeps its own context light.** Reading, auditing, and small mechanical
  jobs go to a subagent on a lighter model (Sonnet or Haiku); pass on the
  conclusion, not file dumps. Anything that edits the repo goes to a Superset
  worker, not a subagent.
- **Keeps building without waiting:** does every open item, not one at a time,
  and stops only for a product decision or a risky permission (deleting real
  data, force-pushing, anything irreversible).
- **Verification:** {{VERIFY}}

### Spawning a worker

Workers run in **this same workspace** (shared checkout, separate terminal):

```bash
superset agents create --workspace "$SUPERSET_WORKSPACE_ID" \
  --agent claude --model fable --effort high \
  --prompt "You are a Jarvis worker. Read AGENTS.md, then do the task in handoffs/briefs/<file>.md. Put every question in one first handoff (status: blocked); after the answers, build every phase through to done." \
  --json
```

Record the returned `sessionId` (the terminal id) under **Running workers** in
`handoffs/OPEN.md`. Then:

```bash
superset terminals read --workspace "$SUPERSET_WORKSPACE_ID" --terminal <id> --max-lines 80   # check on it
superset terminals send --workspace "$SUPERSET_WORKSPACE_ID" --terminal <id> --text "…"         # pass answers / follow-ups
superset terminals close --workspace "$SUPERSET_WORKSPACE_ID" --terminal <id>                   # after its handoff is merged
```

### Choosing the agent and model

Full reasoning in the `jarvis:run` skill's `references/model-routing.md`.
The tier turns on one question:

> **Can the brief state what done looks like and how to verify it?**

- **No** — the worker must decide the shape (subsystem design, schema, prompt
  strategy), the spec is ambiguous, the bug's cause is unknown, or a wrong
  call is expensive and won't show in tests → **top tier**.
- **Yes, and substantial** — the hard thinking is in the brief, not the task
  → **workhorse**. **Yes, and small** → light. **Mechanical** → trivial.

Size doesn't decide this; undecidedness does. And the answer isn't fixed: a
sharper brief moves a task down a tier (see "Briefs are the cost lever").

| Tier | Claude Code | Codex | OpenCode (free) |
| --- | --- | --- | --- |
| Top | `fable` · `high` (`xhigh` if undecided *and* large) | `gpt-6-astra` · `high` | never |
| Workhorse | `opus` · `high` | `gpt-5.6-sol` · `high` | never |
| Light | `sonnet` · `medium` | `gpt-5.6-terra` · `medium` | if tightly fenced |
| Trivial | `haiku` · `low` | `gpt-5.6-luna` · `low` | **first choice** |

`opus`/`high` is not a downgrade — it's the right default for most briefs.
Reserve `fable` for calls that are expensive to get wrong.

**Always Codex, regardless:** any image or media asset, and any app testing
needing computer use. Security work prefers `gpt-5.6-sol`.

### OpenCode — the free tier

OpenCode's free models cost nothing against the Claude or Codex quota, so
every small task it absorbs is quota kept for work that needs it. Check it
**before** `sonnet`/`haiku` in every band — free work is free in all of them.

Give it: mechanical edits, one well-specified change in one or two files with
a pattern to copy, obvious tests, docs, config tweaks. Not: anything top or
workhorse tier, security, migrations, the classification/LLM pipeline, work
spanning many files — and **nothing touching real credentials or real user
data**, since free models are served by third parties. Fixtures only.

Free models are weak, so the scope fence does the work: name the exact files
and the exact pattern, or don't send it here. Omit `--effort` (OpenCode
rejects it) and usually `--model` (the free list rotates; let the user's own
picker decide, or probe with `--model __probe__` and read the accepted ids
off the error).

One correction over `terminals send` if it stalls, loops, or breaks scope;
if the second attempt is still wrong, close it and respawn on `sonnet`.
Babysitting costs more than the tokens saved. Note recurring failures in
`OPEN.md` so later sessions don't retry the same thing.

### Briefs are the cost lever

A vague brief makes the worker discover the task — grep, read ten files,
guess conventions, recover from wrong turns — and that needs a top-tier
model. A precise one hands that context over and the same work runs a tier
lower, so **sharpen the brief before raising the model**: name the files,
name the pattern to follow, state done and the command that proves it, fence
the scope, link the prior handoff. If you can't write those five things the
task really is undecided — `fable`, or split it into a small `fable` design
brief plus an `opus` build brief. More in `references/efficiency.md`.

### Usage bands

Claude usage is one pool shared by Jarvis and every Claude worker on this
machine. Track the band, record it in `handoffs/OPEN.md`
(`Usage band: amber (58%, 14:20)`), re-check once per merge batch.

| Band | Routing |
| --- | --- |
| **Green** — under 50% | Table above. |
| **Amber** — 50%+ | **`fable` off for workers**: those briefs spawn on `opus`/`high` and say so in the header. Running `fable` workers get switched (below). Light/trivial unchanged. |
| **Red** — 75%+, a usage-limit message in any worker terminal, or a failed Claude spawn | New top and workhorse briefs go to Codex. Claude kept for Jarvis and in-flight workers. Tell the user. |

Read it from `/usage` in your own session (local sessions on this machine
only), from limit messages in `terminals read`, or from what the user tells
you; there is no `superset usage` command. Jarvis never downgrades itself —
it routes *work* away so the budget goes to coordination. Bands only tighten
within a session unless the user says the window reset.

**Switching a running `fable` worker:** never kill it mid-edit — its work is
uncommitted in the shared checkout. `terminals send` *"Usage band changed:
finish this phase, write a `status: partial` handoff with the exact file
list, stop."*, commit what landed, close, respawn from the same brief on
`opus`. A worker near the end is worth letting finish.

### Fleet capacity (separate from usage)

Also busy when {{MAX_CLAUDE_WORKERS}}+ Claude workers are in **Running
workers**, or a spawn fails → overflow the next brief to the matching Codex
tier, security first; don't kill running workers to make room. If the host
rejects a model id, its error lists what it accepts.

### Spending Jarvis's own context well

Jarvis is the longest-running, most expensive session here. Details in
`references/efficiency.md`; the habits that matter every session:

- **Poll on events, not a timer**, and batch reads into one bash loop rather
  than one tool call per worker — every tool call re-sends Jarvis's whole
  context. `ls handoffs/*.md` beats reading five screens.
- **Subagents read, workers write.** Each subagent gets an explicit `model:`
  (`sonnet` for judgement, `haiku` for mechanical summarising) and returns a
  conclusion under ~300 words, never a file dump. See `.claude/agents/`.
- **Read narrowly**: `rg -n … -C3`, `head`, `sed -n '40,80p'`,
  `git diff --stat` before `git diff`. Filter verbose output at the source
  (`pytest -q | tail -30`) and put the filtered form in the brief too.
- **`/clear` between unrelated work** (free) and `/compact` at merge
  boundaries, steered: `/compact Focus on open decisions, current briefs,
  file paths`. `OPEN.md` is what makes this safe — write state down first.
- **Jev** (optional): `handoffs/bin/jev.sh brief <file>` lints a brief before
  a spawn, `triage <ids>` polls at one line per worker, `outcome <file>
  <result>` at merge. It advises, never decides; `jev: skipped` = carry on.
- Say it in one line when a choice was made for cost ("briefing this tightly
  so it runs on opencode") — never degrade work silently.

## Checks

Workers run these before handing off and report the results: {{CHECKS}}
If the repo's tooling changes, update this line (and the same line in
`AGENTS.md`) rather than letting workers guess.

## Worker rules and the handoff format

See `AGENTS.md`. Jarvis holds workers to it: a handoff with an incomplete
file list, or a worker that touched git, is sent back before review.

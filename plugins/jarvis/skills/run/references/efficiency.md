# Working cheaply without working worse

Jarvis is the most expensive session in the project: it's on the best model,
it runs the longest, and it accumulates the most context. Everything below is
about buying the same quality for fewer tokens — not about doing less.

The governing idea, from Anthropic's context-engineering guidance: context is
a finite resource with diminishing returns. Good context engineering means
finding the **smallest set of high-signal tokens** that still produce the
outcome. Attention is a budget, not just a window — long contexts degrade
recall as well as costing more.

## Where the money actually goes

Claude Code's `/usage` breakdown flags any behaviour responsible for 10%+ of
recent usage. In practice, for an orchestrator like Jarvis, the ranking is:

1. **Subagents.** Each one runs its own requests. A session that leans on
   subagents can account for the large majority of a week's usage, and a
   single built-in agent type (Explore) is often the biggest line by itself.
2. **Long context.** Claude Code resends the whole conversation every turn,
   and every tool call is another request carrying the batch of results. A
   one-line question in a session that's been open all day still draws usage
   for the entire history. Sessions above ~150k context are markedly more
   expensive even when cached.
3. **Cache misses.** The prompt cache holds for an hour on a subscription
   (five minutes on usage credits or an API key). The first message after a
   longer gap reprocesses the full context. Changing tool definitions or
   system prompt mid-session also invalidates it.
4. **Parallel sessions.** Every Claude session on the account draws from one
   limit. Fanning out four workers is four sessions' worth of spend running
   at once — fine when you need them all, wasteful when they're queued behind
   each other anyway.

Skills and plugins are usually a rounding error. Don't optimise those.

`/usage` is approximate and covers local sessions **on this machine** — not
other devices or claude.ai. Press `d`/`w` for the 24-hour and 7-day views.

## The ten levers, in order of what they're worth to Jarvis

### 1. A precise brief is a model downgrade

This is the biggest quality-preserving lever Jarvis has, and it's free.

A vague brief forces the worker to discover the task: it greps, reads ten
files, guesses at conventions, and needs a top-tier model to recover from
wrong turns. A precise brief hands that context over: exact file paths, the
existing pattern to copy, the interfaces it must not change, what done looks
like, and the command that proves it. The same work then succeeds on `opus`
— often on `sonnet`.

So: **Jarvis spending 2k tokens writing a sharper brief routinely saves a
worker 50k tokens of exploration, and drops it a tier.** When you catch
yourself about to send a fuzzy task to `fable`, the first move is to sharpen
the brief, not to raise the model.

A brief that makes a task cheap:

- **Names the files.** `src/classify/rules.py` and `tests/test_rules.py`, not
  "the classification code".
- **Names the pattern.** "Follow `ingest/x.py` — same structure, same error
  handling." One pointer beats a paragraph of description and beats the
  worker reading five files to infer the convention.
- **States done and how to prove it.** "`backlog classify --dry-run` prints
  one line per save with a label; `pytest tests/test_rules.py` green."
- **Fences the scope.** May touch / must not touch. A worker that knows it
  can't touch the schema doesn't read the schema.
- **Carries the decisions.** Link the prior handoff in `handoffs/merged/`
  instead of re-deriving what was decided.

If you can't write those five things, that's the signal the task is genuinely
undecided — which is when `fable` is the right call, and often when the task
should be split into a small `fable` design brief plus an `opus` build brief.

### 2. Subagents: narrow, cheap, and summarising

Subagents are a context *isolation* tool, not a free lunch: they save tokens
only when the clutter they keep out of Jarvis's context is worth more than
their startup overhead. Reading one file is not worth a subagent; reading
fifteen to answer one question is.

- **Set their model.** A subagent defined in `.claude/agents/<name>.md` takes
  a `model:` field. `sonnet` is the safe default for exploration and review;
  `haiku` for mechanical summarising. Don't put planning-type subagents on
  `haiku` — a weak planner causes compounding mistakes downstream that cost
  more than they save.
- **Ask for a conclusion, not a dump.** "Return under 300 words: the three
  files that matter and what each does." A subagent that explores 50k tokens
  and hands back 500 is the whole point.
- **Never for edits.** In this workflow, anything that changes the repo goes
  to a Superset worker with its own session and its own handoff. Subagents
  read.

### 3. Keep `CLAUDE.md` short

`CLAUDE.md` is loaded at session start and sits in context for every turn —
a 5k-token file costs 5k tokens whether the session runs 2 messages or 200.
Keep it under ~200 lines and only for what's true on every task. Detail
belongs in skills like this one, which load only when invoked. The same goes
for `AGENTS.md` in each worker's session.

### 4. Batch the polling

Every `terminals read` is a tool call, and every tool call re-sends Jarvis's
whole conversation. Polling five workers one at a time at 150k context is
five full-context requests for information that hasn't changed.

- Poll on events, not on a timer: after the user speaks, after a merge, when
  you've nothing else to do.
- Batch reads into one bash call rather than five tool calls:
  `for t in <id1> <id2>; do superset terminals read --workspace "$SUPERSET_WORKSPACE_ID" --terminal $t --max-lines 25; done`
- Better, where the repo has it: `handoffs/bin/jev.sh triage <id1> <id2>`
  reads the screens *outside* your context and hands back one line per
  worker, plus the last 15 lines only for a worker that needs you. Five quiet
  workers cost five lines instead of 125. It's optional and fail-open
  (`references/jev.md`); when it says `skipped`, use the loop above.
- Keep `--max-lines` small. You want the last few lines and whether a handoff
  appeared — `ls handoffs/*.md` answers the second question more cheaply than
  reading a screen.
- The handoff file is the signal; the terminal is the debugger. Read screens
  when something looks wrong, not to confirm progress.

### 5. Read files the cheap way

Just-in-time beats preloading. Keep lightweight references — paths, a grep
pattern, a line range — and pull the content when you actually need it.
`rg -n "pattern" -C3`, `head`, `sed -n '40,80p'`, `git diff --stat` before
`git diff`. Reading a whole 2,000-line file to check one function is the most
common quiet waste in an orchestrator session.

### 6. Compact and clear deliberately

- `/clear` between unrelated pieces of work costs nothing and resets the
  tax. `/rename` first if you might want to `/resume`.
- `/compact` at phase breaks — but `/compact` itself reads the conversation
  it summarises, so it's a large request. Compacting at a natural boundary
  (after a merge batch) beats compacting mid-task.
- Steer it: `/compact Focus on open decisions, the current brief, and file
  paths` keeps what Jarvis actually needs.
- `OPEN.md` and `handoffs/` are the reason this is safe. State lives on
  disk, so a clear costs continuity only if Jarvis forgot to write it down.

### 7. Protect the cache

The cached prefix holds for an hour. Coming back after a long gap reprocesses
everything, so a long idle Jarvis session is worse than a fresh one. If
you're away for hours, `/clear` on return and re-read `OPEN.md` — cheaper
than a cache miss on a 150k-token history. Adding or removing MCP servers
mid-session also invalidates the prefix.

### 8. Trim the tool surface

MCP tool definitions consume context; `/context` shows what's using space.
Disable servers you're not using in this project, and prefer a CLI (`gh`,
`superset`) over an MCP server that does the same job — a CLI adds no
per-tool listing. Bloated tool sets also make the model slower to pick
correctly, so this is a quality lever as much as a cost one.

### 9. Tune effort, not just model

Effort governs the thinking budget, which is billed as output. `high` on a
well-specified task is often no better than `medium` and costs more. Match
effort to how much deliberation the task actually needs — the tier table
already pairs each model with a sensible default, so deviate consciously.
Fable models always use extended thinking; you can't turn it off, which is
another reason not to put routine work there.

### 10. Filter verbose output at the source

Test runs, logs and build output flood a context. Pipe them:
`pytest -q 2>&1 | tail -30`, `rg -c ERROR`, `git diff --stat`. Put the
filtered form *in the brief* so workers do it too. A `PreToolUse` hook can
enforce it globally if it keeps happening.

## What Jarvis should say out loud

When a routing choice was made for cost reasons, say so in one line —
"briefing this tightly so it can run on sonnet" — so the user can push back
if they'd rather spend the tokens. Don't silently degrade work to save
budget, and don't pad a brief with detail the worker doesn't need: a bloated
brief costs the worker context at the start of every one of *its* turns too.

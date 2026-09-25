# Model routing — who gets which task

Two questions decide everything: **what kind of decision is in this task**,
and **how much Claude usage is left**. Capability first, budget second.

Jarvis itself is always Claude Code on the best model available (`fable`,
effort `high`; `max` for the hardest planning). Codex is never Jarvis.
Jarvis never downgrades itself — when usage gets tight it routes *work* away,
so the remaining budget goes to coordination.

---

## 1. The test that picks the tier

> **Can the brief state what "done" looks like and how to verify it?**

- **No** — the worker has to decide what done means: it's choosing the shape
  of a subsystem, a schema, a prompt strategy; the spec is ambiguous or
  self-contradictory; the cause of the bug is unknown; a wrong call is
  expensive and won't show up in tests. → **Top tier.**
- **Yes, and the work is still substantial** — the hard thinking is in the
  brief, not the task: build this endpoint the way the others are built,
  integrate this documented API, write the tests for this module, fix this
  bug with a known repro, hit this measurable performance target. →
  **Workhorse tier.**
- **Yes, and it's small** — a scoped tweak, docs, an audit, a summary. →
  **Light tier.**
- **Yes, and it's mechanical** — rename, reformat, move, one-liner. →
  **Trivial tier.**

Being *large* doesn't make a task top-tier; being *undecided* does. A
two-day feature with a clear spec is workhorse work. A fifty-line change to
how saves get classified is top-tier work.

## 2. Claude Code tiers

| Tier | `--model` | `--effort` | Send it |
| --- | --- | --- | --- |
| Top | `fable` | `high` (`xhigh` when the task is both undecided and large) | New subsystems designed from scratch · data model / schema design · the classification & LLM pipeline, prompt and eval design · cross-cutting refactors touching many files at once · debugging where the cause is unknown · security-sensitive logic · briefs whose spec is ambiguous, contested, or came back with questions · anything Jarvis can't cheaply verify afterwards |
| Workhorse | `claude-opus-5-5` (alias `opus`) | `high` | Well-specified feature work, however big: a new command or endpoint following an existing pattern · integrating a documented API · test suites · a migration with a known shape · a bug with a known repro · performance work with a target number · a second pass on something `fable` already designed |
| Light | `sonnet` | `medium` | Scoped tweaks, docs, reading and auditing, summarising diffs. Also Jarvis's own read-only subagents. |
| Trivial | `haiku` | `low` | Renames, formatting, moving files, one-line fixes — but these are OpenCode's default slice; use `haiku` when OpenCode isn't configured or the task touches anything sensitive. |

`opus` at `high` is not a downgrade from `fable` — it is the right default
for the majority of briefs, and the tier Jarvis should reach for unless the
task genuinely fails the test above. Reserve `fable` for the calls that are
expensive to get wrong.

**The workhorse model is Claude Opus 5.5, pinned.** Spawn it as
`--model claude-opus-5-5`, not the `opus` alias. The alias resolves to the
same model on Claude Code 2.1.282 and later, but a pinned id is one thing
fewer to wonder about when a handoff looks off. Everywhere else in these docs
`opus` is shorthand for that id. What matters about Opus 5.5 for routing:

- It is cheaper than Opus 5 per token ($4 / $20 per MTok, cache reads $0.20)
  and cheaper again per finished task — at `medium` it matched or beat
  Opus 5 at `high` on agentic coding with roughly half the tokens, and it
  catches more in code review with fewer false alarms.
- Thinking is always on and can't be disabled, so `--effort` is the only
  cost lever. Pass it explicitly: the API default is `medium`, one level
  below Opus 5's. `high` stays the tier default; use `medium` for a workhorse
  brief that is small and tightly fenced.
- It reports its work in plainer language, which makes handoffs easier to
  review, and reads screenshots and charts accurately without extra tooling.

Jarvis itself stays on `fable`: Claude Fable 5.1 is the tier above Opus, and
the coordinating session is where the undecided calls get made.

**Design/build split.** When a task is top-tier only because nobody has
decided the shape yet, consider splitting it: a short `fable` brief that
produces the decision (schema, interface, approach — written into the
handoff, no implementation), then an `opus` brief that builds it. Cheaper,
and the decision ends up on the record in `handoffs/merged/`.

## 3. Codex tiers

Two kinds of task go to Codex **always**, whatever the Claude fleet is
doing, because Codex has the capability built in:

| Task | `--model` | `--effort` |
| --- | --- | --- |
| **Any image or media asset** — logos, icons, app-store or social images, doc screenshots, editing or resizing images | `gpt-6-astra` | `high` |
| **App testing that needs computer use** — clicking through a real UI, driving a desktop app, verifying a flow a human would click | `gpt-6-astra` | `high` |

Everything else stays on Claude Code until the fleet is busy or usage is
tight. Then the same test above picks the Codex tier:

| Tier | `--model` | `--effort` | Send it |
| --- | --- | --- | --- |
| Top | `gpt-6-astra` | `high` (`xhigh` when undecided and large) | The `fable` cases: undecided shape, unknown cause, ambiguous spec, end-to-end work across code and tools. Also all media and computer-use work. |
| Workhorse | `gpt-5.6-sol` | `high` | The `opus` cases — well-specified substantial work — **and all security work** (audits, hardening, dependency and vulnerability review, threat modelling), which goes to Sol by preference even when the Claude fleet is free. |
| Light | `gpt-5.6-terra` | `medium` | Everyday scoped work, tests, docs. |
| Trivial | `gpt-5.6-luna` | `low` | Mechanical edits, and high-volume structured work (extraction, classification, transformation) where a good result is obvious. |

Codex's `max`/`ultra` reasoning modes exist but cost a lot of time; use
`xhigh` as the ceiling unless the user asks otherwise.

## 3b. OpenCode — the free tier

OpenCode runs free models (the list rotates: Union Alpha, Muse Spark,
Nemotron, Ling, MiMo and friends come and go). They cost **nothing against
your Claude or Codex quota**, which makes OpenCode the right first choice for
work that doesn't need a paid model — every small task it absorbs is quota
kept for the work that does.

They are also weaker, smaller-context, and less reliable in long agentic
loops. So OpenCode gets a narrow, well-fenced slice:

| Send it | Don't send it |
| --- | --- |
| Mechanical edits: renames, formatting, moving files, one-line fixes | Anything top-tier or workhorse — undecided shape, ambiguous spec, unknown cause |
| A single well-specified change in one or two files, with a pattern to copy | Work spanning many files, or needing a lot of the codebase in context |
| Tests for existing code where the assertions are obvious | Security work, migrations, dependency changes |
| Docs, comments, config tweaks, README updates | The classification / LLM pipeline, prompts, or anything defining product behaviour |
| Repetitive structured work with an obvious right answer | Anything touching real credentials, real user data, or anything you wouldn't send to a free third-party provider |

That last row matters and isn't about quality: free models are served by
whoever is providing them. Treat an OpenCode worker as an untrusted
destination for data. Fixtures and synthetic samples only.

### When OpenCode is the default, not the fallback

In the **green** band, light and trivial tier work goes to OpenCode *first*
when it passes the table above — not to `sonnet`/`haiku`. Preserving the
Claude pool for top and workhorse briefs is the point. In amber and red it
becomes more valuable still: OpenCode work is free, so the bands never push
work *away* from it.

The brief matters even more here than elsewhere. A weak model with a fuzzy
brief will wander through the repo, touch files it shouldn't, and hand back
something you have to unpick — in a shared checkout that costs you real time.
An OpenCode brief should name the exact files, give the exact pattern, and
fence the scope hard. If you can't fence it that tightly, it isn't an
OpenCode task.

### Spawning

```bash
superset agents create --workspace "$SUPERSET_WORKSPACE_ID" \
  --agent opencode \
  --prompt "You are a Jarvis worker. Read AGENTS.md, then do the task in handoffs/briefs/<file>.md. Touch only the files it lists. Never run git commands that change state. Put every question in one first handoff." \
  --json
```

Two mechanics differ from Claude and Codex:

- **Omit `--effort`.** Superset lists effort levels for Claude, Amp, Codex,
  Mastracode, Pi and Copilot; other agents reject an explicit effort
  override and use their own default.
- **`--model` is uncertain.** Which ids OpenCode accepts depends on the
  providers configured on that machine, and the free model list rotates. Omit
  `--model` to use whatever the user has selected in OpenCode's own picker,
  or probe once (`--model __probe__`) and read the accepted ids from the
  error. Don't hardcode a free model name into a brief — it may be gone next
  week.

### Escalation: fail cheap, once

An OpenCode worker that stalls, loops, ignores the scope fence, or hands back
a handoff that fails checks gets **one** correction over `terminals send`.
If the second attempt is still wrong, stop: close the terminal, revert
nothing yourself (the worker's edits are uncommitted — have the worker leave
a `status: partial` handoff, or if it's incoherent, note the files it touched
and check them in the diff), and respawn on `sonnet`. Two failed rounds of
babysitting costs more of your context than the Claude tokens you saved.

Track this: if a kind of task keeps bouncing back from OpenCode, it belongs a
tier up, and say so in `OPEN.md` so future sessions don't retry it.

## 4. The usage ladder

Claude Code usage is shared across Jarvis and every Claude worker on the
account, so the budget is one pool. Jarvis tracks which **band** it's in and
records it in `handoffs/OPEN.md` so the band survives a context compaction.

| Band | Routing |
| --- | --- |
| **Green — under 50%** | The table above, unchanged. Light and trivial work still prefers OpenCode — free work is free in every band. |
| **Amber — 50% and over** | **`fable` is off for workers.** Every brief that would have been `fable` spawns on `opus` at `high` instead, and says so in its header. Running `fable` workers get switched (below). Light and trivial tiers are unchanged — they're cheap. Jarvis stays on `fable`. |
| **Red — 75% and over** | New top-tier and workhorse briefs go to **Codex** (`gpt-6-astra` / `gpt-5.6-sol`). Claude Code is kept for Jarvis and for workers already in flight. Anything OpenCode can safely take, it takes. Tell the user plainly that you've moved the fleet and why. |

### Switching a running `fable` worker to `opus`

Never kill a worker mid-edit — its work is uncommitted in the shared
checkout and would be lost. Instead:

1. `terminals send` it: *"Usage band changed. Finish the phase you're on, write a `status: partial` handoff with the exact file list and what's left, then stop."*
2. When the handoff appears, review and commit what's done as normal.
3. `terminals close` the terminal.
4. Respawn from the **same brief** on `opus`/`high`, with the partial handoff
   named in the prompt so the new worker picks up with the context:

```bash
superset agents create --workspace "$SUPERSET_WORKSPACE_ID" \
  --agent claude --model claude-opus-5-5 --effort high \
  --prompt "You are a Jarvis worker. Read AGENTS.md, then continue the task in handoffs/briefs/<file>.md. handoffs/merged/<partial>.md records what is already done — start from there. Put every question in one first handoff; otherwise build every phase through to done." \
  --json
```

A worker already near the end of its last phase is worth letting finish
instead — switching costs a handoff cycle. Use judgement; the point of the
band is to stop *new* `fable` spend, not to churn.

### How Jarvis reads usage

There is no `superset usage` CLI command — usage lives in the desktop app's
Usage view and in Claude Code itself. In practice:

- **Jarvis's own session** is the proxy for the account: check it with
  `/usage` in your own terminal at session start and after each merge batch.
- **Worker terminals**: `terminals read` shows a usage-limit or rate-limit
  message when one is hit. One of those means Red for that fleet regardless
  of what the percentage said.
- **A failed spawn** (`superset agents create --agent claude` errors out) is
  also Red.
- **The user** may just tell you ("I'm at 60%"). Take it, record the band,
  don't re-derive it.

Write the band and the time you read it into `OPEN.md`:
`Usage band: amber (58%, 14:20) — fable off for workers`. Re-check it at
least once per merge batch; bands only ever tighten within a session unless
the user says the window reset.

## 5. Fleet capacity (separate from usage)

The fleet is also "busy" — independent of the percentage — when:

- `MAX_CLAUDE_WORKERS` (from `CLAUDE.md`, default 4) or more Claude workers
  are in **Running workers** in `OPEN.md`, or
- a spawn fails for any reason.

Busy means: overflow the *next* brief to the Codex tier that matches its
test result, security work first. Don't kill running workers to make room.

## 6. If a model id is rejected

The host validates `--model` before launching and its error names every id
that agent accepts. Pick the same tier from that list (newest flagship →
Top; the balanced one → Workhorse; the cheap one → Light/Trivial) and, if it
recurs, update the table in `CLAUDE.md` so future sessions don't hit it. If
the pinned `claude-opus-5-5` is what gets rejected, the `opus` alias tracks
the newest Opus release and is the fallback.

## 7. The shadow classifier

Where the repo has `handoffs/bin/jev.sh`, `jev.sh brief <file>` also logs a
tier of its own beside yours. It has **no authority**: it never prints its
verdict, and nothing in this file changes because of it. It exists to find
out, over thirty-odd briefs with recorded outcomes, whether a cheap classifier
agrees with you and whether it's right when it doesn't. The rule for what
happens then is in `references/jev.md`.

## 8. Writing it down

Every brief header carries `worker:`, `model:`, `effort:` — and, when the
band changed the choice, a note (`model: opus (amber band; fable-tier task)`).
That way a re-spawn is a copy of one line, and the record shows why.

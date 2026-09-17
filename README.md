# superset-jarvis

**You talk to one agent. A team of agents does the building.**

Jarvis is an open-source agent skill for [Superset](https://superset.sh). It
turns a Claude Code session into a lead engineer for your project. That lead
agent, called Jarvis, plans the work and writes a short brief for each task.
It starts worker agents in separate Superset terminals, reviews what they hand
back, and commits it. You never manage the workers. You talk to Jarvis, and
Jarvis manages them.

```
you ──▶ Jarvis (Claude Code · fable · high)
            │  brief ──▶ worker A  claude / fable        ──▶ handoff ─┐
            │  brief ──▶ worker B  claude / sonnet       ──▶ handoff ─┤─▶ Jarvis reviews, commits, pushes
            │  brief ──▶ worker C  codex  / gpt-6-astra  ──▶ handoff ─┘   (image asset)
            └─ handoffs/OPEN.md — the one list of what's pending
```

---

## Contents

- [Who it's for](#whos-it-for)
- [What it does](#what-it-does)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Talking to Jarvis](#talking-to-jarvis)
- [How it works](#how-it-works)
- [What gets added to your repo](#what-gets-added-to-your-repo)
- [Model routing](#model-routing)
- [Usage-aware spending](#usage-aware-spending)
- [Token efficiency](#token-efficiency)
- [Customizing](#customizing)
- [Jarvis vs. `superset:orchestrate`](#jarvis-vs-supersetorchestrate)
- [FAQ and troubleshooting](#faq-and-troubleshooting)
- [Repository layout](#repository-layout)
- [Contributing](#contributing)
- [License](#license)

---

## Who it's for

Jarvis is a good fit if you:

- **Already use Superset** with Claude Code, and maybe Codex or OpenCode too.
- **Build a product day to day** and want several agents working in parallel
  without keeping track of each terminal yourself.
- **Keep running out of usage**, and want the expensive models saved for hard
  work while routine tasks go to cheaper or free models.
- **Want one clean commit per task** and a record of every decision, instead
  of a dozen agents all writing to git at once.
- **Lose track of work between sessions.** Jarvis keeps its state in files in
  your repo, so you can pick up tomorrow where you left off.

It's probably not for you if:

- **You don't use Superset.** Jarvis runs on `superset agents create` and
  `superset terminals read|send`. It won't work in a plain terminal or
  another IDE.
- **You only need one large parallel job**, like splitting a migration into
  ten slices, each on its own branch. Superset's built-in
  `superset:orchestrate` skill is made for that. See the
  [comparison](#jarvis-vs-supersetorchestrate).
- **You'd rather work in a single agent session** and review every edit as it
  happens.

## What it does

| | |
| --- | --- |
| 🧠 **One lead agent** | You talk only to Jarvis. It plans, decides, and briefs, and it does no editing in its own terminal. |
| 🛠️ **Parallel workers** | Each task runs in its own Superset terminal in the same workspace. Jarvis starts independent tasks at the same time. |
| 🎯 **Model routing** | Each task goes to the cheapest agent and model that can do it well: Claude Code (`fable` / `opus` / `sonnet` / `haiku`), Codex, or OpenCode's free models. |
| 📉 **Usage bands** | Jarvis tracks how much of your Claude usage is gone. Past 50% it stops giving workers `fable`. Past 75% new heavy work goes to Codex. |
| ❓ **Grouped questions** | Workers never wait for you. They write their questions into a handoff file, and Jarvis collects them into one numbered message for you. |
| ✅ **Review and commit** | Jarvis checks each handoff against `git status`, reads the diff, and runs your checks. Then it commits only the listed files, one commit per task. |
| 📒 **Memory in your repo** | `handoffs/OPEN.md` lists what's running, what's blocked, and what's next, so `/clear` and new sessions don't lose anything. |
| 💸 **Token discipline** | Precise briefs let tasks run on smaller models. Read-only subagents run on `sonnet`, and Jarvis checks on workers when something happens instead of on a timer. |

The plugin has two skills:

- **`jarvis:setup`** runs once per repo. It asks you a few questions and adds
  the Jarvis workflow files to your project.
- **`jarvis:run`** is the playbook Jarvis follows every session: briefing,
  starting workers, checking on them, reviewing, and merging.

## Requirements

| Requirement | Why |
| --- | --- |
| [Superset](https://docs.superset.sh/install) desktop app and CLI (built against CLI v1.28) | Jarvis starts and talks to workers through `superset agents` and `superset terminals` |
| [Claude Code](https://claude.com/claude-code) configured as a Superset agent | Jarvis itself and most workers run on it |
| A git repository | Jarvis commits each handoff |
| *Optional:* Codex agent in Superset | Images and other media, computer-use testing, and extra work when your Claude usage is high |
| *Optional:* OpenCode agent in Superset | Free models for small, tightly scoped tasks |

Without Codex or OpenCode, Jarvis still works. Those tasks go to Claude
models instead.

## Installation

Pick **one** of these.

### Option 1: Claude Code plugin marketplace (recommended)

Inside Claude Code:

```
/plugin marketplace add gorock007/superset-jarvis
/plugin install jarvis@superset-jarvis
```

Updates arrive through `/plugin`, and the skills are named `jarvis:setup`
and `jarvis:run`.

### Option 2: Skills CLI

For Claude Code, Codex, or any agent that reads `SKILL.md` files:

```bash
npx skills add gorock007/superset-jarvis
```

It finds two skills, `setup` and `run`. Install both.

### Option 3: Manual

```bash
git clone https://github.com/gorock007/superset-jarvis.git
mkdir -p ~/.claude/skills
cp -R superset-jarvis/plugins/jarvis/skills/setup ~/.claude/skills/jarvis-setup
cp -R superset-jarvis/plugins/jarvis/skills/run   ~/.claude/skills/jarvis-run
```

### Check that it installed

Open a new Claude Code session and ask *"what skills do you have?"* You should
see `setup` and `run` from the `jarvis` plugin.

## Quick start

### 1. Set up Jarvis in your repo (once)

Open your project's workspace in Superset. In any Claude Code session, say:

> **set up Jarvis in this repo**

`jarvis:setup` checks that the `superset` CLI works and which agents you have
configured. Then it asks all its questions in one message, with answers
already guessed from your repo, so you can often just say "yes":

1. Project name
2. Where the app lives (repo root or a subfolder)
3. Checks workers must run before handing off, such as `bun run typecheck && bun test` or `pytest && ruff check .`
4. What only Jarvis may do besides git, such as applying migrations, deploying, or editing lockfiles
5. How you check finished work: a phone build, a browser URL, CLI commands, or tests only
6. Shared files workers should change as little as possible
7. How many Claude workers can run before extra work goes to Codex (default 4)
8. Whether you're comfortable sending small tasks to OpenCode's free models
9. Usage band thresholds (default 50% and 75%)

It then writes `CLAUDE.md`, `AGENTS.md`, `handoffs/`, and `.claude/agents/`.
If `CLAUDE.md` or `AGENTS.md` already exist, it **merges** the new sections
into them and shows you the diff first. It also checks which model IDs your
Superset host accepts and replaces any it doesn't recognize.

### 2. Start Jarvis

From a Superset terminal (find your project ID with `superset projects list`):

```bash
superset ws create --project <projectId> --name main --checkout local --local \
  --agent claude --model fable --effort high \
  --prompt "You are Jarvis. Read CLAUDE.md and handoffs/OPEN.md, record your session id in OPEN.md, then tell me what's open."
```

Or, in the Superset desktop app, open the project's shared-checkout
workspace, launch Claude Code with model **fable** and effort **high**, and
send the same first message.

> `--checkout local` matters. Jarvis and its workers share one working copy,
> and only Jarvis uses git.

### 3. Talk to it

> Add a dark mode toggle to settings and fix the flaky login test.

Jarvis writes two briefs, starts two workers on suitable models, and tells you
what it did. When the workers finish, it reviews their work, commits it, and
tells you what to check.

## Talking to Jarvis

Plain language works. Some useful phrases:

| Say | Jarvis will |
| --- | --- |
| "spin off a worker for X" / "delegate this" | Write a brief, pick a model, and start a worker |
| "what's open?" | Summarize running workers, pending questions, and the to-do list |
| "check on the workers" | Read worker terminals and new handoffs in one pass |
| "merge the handoffs" | Review, run checks, commit each finished handoff, and push |
| "I'm running low on usage" | Move to the amber or red band and send new work to cheaper models |
| "answers: 1. yes 2. use Postgres" | Pass your answers to the right workers |

Jarvis only stops to ask you about **product decisions** or **risky
actions**: deleting real data, force-pushing, rewriting history, touching
production, or spending money. It makes everything else, like which model,
how to split the work, and when to start a worker, on its own and tells you
in one line.

## How it works

```
 ┌────────── brief ──────────┐
 │                           ▼
Jarvis                  worker (own terminal, shared checkout)
 ▲  │                        │
 │  │   status: blocked ◀────┤  questions, all at once
 │  └── answers ────────────▶│
 │                           │
 └──── status: done ◀────────┘  handoff: files changed, checks run, notes
        │
        ├─ file list vs git status
        ├─ diff review (+ run checks)
        ├─ Jarvis-only steps (migrations, lockfiles, releases)
        └─ one commit → move handoff to handoffs/merged/ → push → close terminal
```

**1. Brief.** Jarvis writes `handoffs/briefs/YYYY-MM-DD-HHMM-<slug>.md`. It
names the exact files, an existing pattern to copy, what "done" means and the
command that proves it, and which files the worker may and may not touch.
**The more precise the brief, the smaller the model it needs.**

**2. Start.** Jarvis runs `superset agents create --workspace
"$SUPERSET_WORKSPACE_ID" ...` with the chosen agent, model, and effort, and
records the terminal ID in the brief and in `OPEN.md`.

**3. Ask once.** If a worker has questions, it writes them all into its first
handoff with `status: blocked`. Jarvis collects questions from every blocked
worker into one message for you, then sends each worker its answers with
`superset terminals send`.

**4. Build.** The worker builds every phase through to done, runs the checks,
and writes a handoff listing the files it changed.

**5. Review and merge.** Jarvis checks the file list against `git status`,
reads the diff, and runs the checks if needed. It commits **only those files**
with a `Co-Authored-By` line naming the worker, moves the handoff to
`handoffs/merged/`, pushes, and closes the worker's terminal.

Two rules keep the shared checkout safe:

1. **Only Jarvis uses git.** Workers never commit, stash, reset, check out,
   rebase, or clean.
2. **Workers never wait for you.** Their questions go through Jarvis.

## What gets added to your repo

| Path | Purpose |
| --- | --- |
| `CLAUDE.md` | Jarvis's instructions: what only Jarvis may do, commands for starting workers, the model table, your checks, and how you verify work. Kept under about 200 lines. |
| `AGENTS.md` | The worker rules, read by both Claude Code and Codex: git rules, shared-file rules, ask once, handoff format |
| `handoffs/OPEN.md` | The one pending list: Jarvis's session ID, usage band, running workers, questions for you, to-do |
| `handoffs/TEMPLATE.md` | Handoff format |
| `handoffs/briefs/` | Briefs Jarvis writes, plus `TEMPLATE.md` |
| `handoffs/merged/` | Reviewed handoffs, committed together with the work they describe |
| `.claude/agents/scout.md` | Read-only explorer subagent pinned to `sonnet`. Answers in under 300 words. |
| `.claude/agents/diff-reviewer.md` | Read-only diff reviewer subagent pinned to `sonnet` |

`handoffs/` is **tracked in git on purpose**. It's your project's record of
what was decided and why.

## Model routing

The tier depends on one question: **can the brief say what "done" looks like
and how to verify it?** If yes, `opus`/`high` can handle it, and that covers
most work. If no (the approach isn't decided, the spec is unclear, the cause
is unknown, or a wrong call would be expensive), it goes to `fable`. How
*undecided* a task is matters more than how big it is.

| Tier | Claude Code | Codex | OpenCode (free) |
| --- | --- | --- | --- |
| Top: worker must decide the approach | `fable` · high | `gpt-6-astra` · high | never |
| Workhorse: substantial but specified | `opus` · high | `gpt-5.6-sol` · high | never |
| Light: scoped tweaks, docs, audits | `sonnet` · medium | `gpt-5.6-terra` · medium | if tightly scoped |
| Trivial: renames, formatting | `haiku` · low | `gpt-5.6-luna` · low | **first choice** |

These always go to Codex: **any image or media asset** and **app testing that
needs computer use**. Security work goes to `gpt-5.6-sol` when possible.

**OpenCode is the free tier.** Jarvis considers it before `sonnet` or `haiku`,
because every small task it handles saves your Claude and Codex quota. Jarvis
tells OpenCode exactly which files to change and which pattern to follow, and
never gives it top- or workhorse-tier work. Free models are run by third
parties, so it never sees real credentials or user data. If OpenCode gets a
task wrong, Jarvis gives it one correction, then moves the task to `sonnet`.

When more Claude workers are running than your cap allows, extra work goes to
the matching Codex tier.

> Model IDs change over time. `jarvis:setup` checks which IDs your Superset
> host accepts and updates the table. The full reasoning is in
> [`model-routing.md`](plugins/jarvis/skills/run/references/model-routing.md).

## Usage-aware spending

Jarvis and every Claude worker draw from the same usage limit, so Jarvis
tracks a **band** and records it in `OPEN.md`:

| Band | Trigger | What changes |
| --- | --- | --- |
| 🟢 Green | under 50% | The routing table as written |
| 🟡 Amber | 50%+ | Workers don't get `fable`. Those briefs start on `opus`/`high` instead. Running `fable` workers finish their current phase, hand off `status: partial`, and restart on `opus`. Jarvis never stops them mid-edit. |
| 🔴 Red | 75%+, a usage-limit message, or a failed start | New top- and workhorse-tier briefs go to Codex. Claude is kept for Jarvis and workers already running. |

Jarvis reads its own `/usage` at the start of each session and after each
merge batch. Jarvis **never downgrades its own model**. It sends work
elsewhere so the remaining budget goes to coordination.

## Token efficiency

Jarvis is the longest-running and most expensive session in the project, so
the skill is designed to keep costs down:

- **A precise brief lets a smaller model do the job.** Naming the files, the
  pattern, and the command that proves done can move a `fable` task to `opus`
  or `sonnet`.
- **Subagents read, workers write.** Exploration and diff summaries go to
  `sonnet` subagents that return conclusions, not whole files. Subagents are
  usually the biggest part of an orchestrator's usage.
- **Jarvis checks on workers when something happens, not on a timer.** It
  reads all worker terminals in one bash call with a small `--max-lines`.
- **State lives on disk,** so `/clear` and `/compact` are cheap and safe.
- **Verbose output is trimmed at the source,** for example
  `pytest -q 2>&1 | tail -30` or `git diff --stat`.

Details are in
[`efficiency.md`](plugins/jarvis/skills/run/references/efficiency.md).

## Customizing

After setup, **your repo's `CLAUDE.md` takes priority over the skill**. Edit
it to change:

- the model table and the effort level for each tier
- usage band thresholds
- the Claude worker cap
- what only Jarvis may do
- your checks and how you verify work

Workers follow `AGENTS.md`. Add project-specific rules there, such as
"never edit `src/theme/tokens.ts`" or "use pnpm, not npm".

## Jarvis vs. `superset:orchestrate`

| | **Jarvis** | **`superset:orchestrate`** |
| --- | --- | --- |
| Shape | One lead agent that runs across sessions | A one-off fan-out |
| Checkout | Shared: workers in terminals of one workspace | An isolated worktree and branch per worker |
| Git | Jarvis commits each handoff to your branch | Results merged as PRs |
| Memory | `handoffs/OPEN.md` + `handoffs/merged/` | Per run |
| Model routing | Per task, based on usage | Your choice |
| Best for | Running a product day to day | "Split this migration into ten slices" |

They work well together. Use Jarvis for daily work, and have it use
`orchestrate` for a big parallel job when needed.

## FAQ and troubleshooting

**`superset: command not found`**
Jarvis only works inside Superset. Install it from
[docs.superset.sh/install](https://docs.superset.sh/install) and run Jarvis
from a Superset terminal, where `superset` and `$SUPERSET_WORKSPACE_ID` are
available.

**A worker won't start: "unknown model"**
Your host doesn't accept that model ID. The error lists the IDs it does
accept. Update the table in your `CLAUDE.md`, or run `jarvis:setup` again to
check the IDs.

**Codex or OpenCode rows don't work**
Check `superset agents list --local`. If an agent isn't configured there,
Jarvis sends those tasks to Claude models until you add it.

**Two Jarvis sessions are running**
Each session writes its ID to `OPEN.md` at startup. If the recorded Jarvis
terminal is still running, the new session asks you before taking over.

**A worker is stuck on a permission prompt**
Jarvis sees it when it reads the worker's terminal and sends a nudge with
`superset terminals send`. You can also say "check on the workers".

**Can I use it without Codex?**
Yes. Everything except media and computer-use tasks runs on Claude. Without
Codex, the red band can't move heavy work anywhere, so you'll need to manage
usage more carefully.

**Does it work with other agents?**
Workers can be any Superset agent that reads `AGENTS.md`, such as Claude Code,
Codex, or OpenCode. Jarvis itself is written for Claude Code.

**Should `handoffs/` be in `.gitignore`?**
No. It's tracked on purpose as the project's memory.

## Repository layout

```
.agent-marketplace.json              Superset marketplace manifest
.claude-plugin/marketplace.json      Claude Code marketplace manifest
plugins/jarvis/
  plugin.json                        Superset plugin manifest
  .claude-plugin/plugin.json         Claude Code plugin manifest
  skills/
    setup/
      SKILL.md                       jarvis:setup: interview + install
      templates/                     CLAUDE.md, AGENTS.md, handoffs/, .claude/agents/
    run/
      SKILL.md                       jarvis:run: the operating playbook
      references/
        superset-cli.md              exact commands, flags, JSON shapes
        model-routing.md             routing table and reasoning
        handoffs.md                  brief and handoff formats, review steps
        efficiency.md                where tokens go and how to spend fewer
```

## Contributing

Issues and pull requests are welcome, especially:

- updates when Superset CLI flags or model IDs change
- routing and efficiency improvements based on real usage
- clearer templates and setup questions

When editing skills, keep the templates' style: short rules in plain words,
each with its reason. Every line of a generated `CLAUDE.md` is read in every
Jarvis session, so leave out generic advice.

### Publishing a new version (maintainers)

```bash
superset plugins publish jarvis --bump patch
git commit -am "publish jarvis@<version>"
git tag jarvis@<version> && git push --tags
```

A release is a git tag, and installs pin to it. Keep the `version` in
`plugins/jarvis/plugin.json`, `plugins/jarvis/.claude-plugin/plugin.json`, and
`.agent-marketplace.json` the same.

## License

[MIT](LICENSE) © 2026 Gorock

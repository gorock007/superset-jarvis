# Superset CLI — what Jarvis actually runs

Verified against the Superset CLI reference (docs.superset.sh/cli/cli-reference),
CLI v1.28. Run `superset <cmd> --help` if a flag looks different on your version.

Inside a Superset terminal, `superset` is on PATH and `$SUPERSET_WORKSPACE_ID`
is set. When `CLAUDE_CODE` or `CODEX_CLI` is set, output defaults to JSON.

## Spawn a worker in this workspace (shared checkout, new terminal)

```bash
superset agents create --workspace "$SUPERSET_WORKSPACE_ID" \
  --agent <claude|codex> \
  --model <id> --effort <level> \
  --prompt "<text>" \
  [--attachment <path>]... \
  --json
```

- `--agent`: preset id (`claude`, `codex`), a HostAgentConfig UUID, or `superset`.
- `--model`: explicit override for this launch. Claude accepts family aliases
  that track the newest release — `fable`, `opus`, `sonnet`, `haiku` — or a
  pinned id. Codex accepts its model ids (`gpt-6-astra`, `gpt-5.6-sol`,
  `gpt-5.6-terra`, `gpt-5.6-luna`). The host rejects an unknown id before
  launching and its error lists every id that agent accepts.
- `--effort`: Claude `low|medium|high|xhigh|max`; Codex `low|medium|high|xhigh`.
- `--attachment`: local file uploaded for the agent; repeatable.
- Returns `{ kind: "terminal", sessionId, ... }` for claude/codex. The
  `sessionId` is the terminal id you use below.
- `--resume-session <id>` restores a killed agent session instead of `--prompt`.

## Watch, talk to, and close a worker

```bash
superset terminals list  --workspace "$SUPERSET_WORKSPACE_ID"
superset terminals read  --workspace "$SUPERSET_WORKSPACE_ID" --terminal <id> --max-lines 80
superset terminals send  --workspace "$SUPERSET_WORKSPACE_ID" --terminal <id> --text "…"   # add --no-submit to stage without Enter
superset terminals close --workspace "$SUPERSET_WORKSPACE_ID" --terminal <id>
```

`terminals list` shows PTYs that exist, not whether the agent inside is busy
or idle — `read` the screen to know.

## Run a one-off command in its own terminal (no agent)

```bash
superset terminals create --workspace "$SUPERSET_WORKSPACE_ID" --command "pytest -q"
```

Useful for long test runs you don't want blocking your own terminal.

## Starting Jarvis (the user does this, or the setup skill prints it)

```bash
superset projects list                      # find <projectId>
superset ws create --project <projectId> --name main --checkout local --local \
  --agent claude --model fable --effort high \
  --prompt "You are Jarvis. Read CLAUDE.md and handoffs/OPEN.md, record your session id in OPEN.md, then tell me what's open."
```

`--checkout local` uses the project's existing files, index and branch
(shared checkout). The default is an isolated worktree, which is the other
model (`superset:orchestrate`) — not this workflow.

## Handy

- `superset workspaces get --field worktreePath` — the path of this workspace.
- `superset agents list --local` — which agent presets exist on this machine.
- `open "superset://v2-workspace/$SUPERSET_WORKSPACE_ID?terminalId=<id>"` —
  deep link to focus one worker's terminal in the desktop app.
- `superset automations create … --agent claude --prompt-file …` — schedule a
  recurring Jarvis-style run (Pro feature).

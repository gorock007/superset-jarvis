# <one-line task title>
worker: claude | codex
model: <fable | claude-opus-5-5 | sonnet | haiku | gpt-6-astra | gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna>
  # note the reason when the usage band changed the choice, e.g. `claude-opus-5-5 (amber band; fable-tier task)`
effort: <low | medium | high | xhigh>
started: <YYYY-MM-DD HH:MM> · terminal: <sessionId, filled in by Jarvis>

## Goal
<what done looks like, in one paragraph>

## Context
<decisions already made, files to read first, related handoffs in handoffs/merged/>

## Scope
- May touch: <paths>
- Must not touch: <paths>
- Shared files (edit minimally, name in handoff): <paths>

## Phases
1. <phase>
2. <phase>

## Checks
<commands to run before handing off>

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

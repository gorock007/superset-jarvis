# Work out a prompt and eval strategy for support-ticket triage
worker: claude
model: fable
effort: high
started: 2026-09-16 10:30 · terminal: term_e21d48

## Goal
The LLM triage step labels incoming support tickets as billing, bug,
how-to or account. About one in five billing tickets comes out as bug. We
do not have an eval set, a target metric, or a view on whether the fix is a
better prompt, few-shot examples, a two-step classify-then-verify call, or
something else. Decide the strategy and decide how we would know it worked.

## Context
The current baseline and how it was measured (by hand, on 60 tickets) is in
handoffs/merged/2026-09-02-triage-baseline.md. Tickets are English and German, median
70 words. Mislabelled billing tickets wait about nine hours longer for a
reply, so that error costs more than the others.

## Scope
- May touch: `services/triage/prompts/`, `services/triage/evals/`
- Must not touch: `services/triage/router/`, `services/billing/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Propose the eval: what goes in the set, who labels it, which metric, what number is good enough.
2. Propose the prompt strategy and why it should move that metric.
3. Build a first version of both.

## Checks
We have no eval yet; designing one is the task. Explain in the handoff why
someone should trust the numbers it produces.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

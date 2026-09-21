# Audit the settings screens against WCAG 2.2 AA (read-only)
worker: claude
model: sonnet
effort: medium
started: 2026-09-16 14:15 · terminal: term_ae7720

## Goal
The handoff lists every WCAG 2.2 AA problem you can find from the source of
the five settings screens (General, Billing, Team, Security, Notifications):
the success criterion, the component, what is wrong, and a suggested fix in
one line. Nothing gets fixed in this brief.

## Context
The screens were rebuilt recently; see handoffs/merged/2026-09-04-settings-redesign.md
for which components are new. Pay most attention to focus order in the
modals, labels on icon-only buttons, and colour contrast of the muted text
token.

## Scope
- May touch: `handoffs/inbox/` (your handoff only)
- Must not touch: `apps/web/src/`, `packages/ui/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Read each screen and the shared components it uses.
2. Write the findings, most severe first.

## Checks
This is a reading task; there is nothing to run.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

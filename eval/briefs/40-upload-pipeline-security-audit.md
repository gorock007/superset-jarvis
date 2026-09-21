# Security audit of the file upload pipeline
worker: codex
model: gpt-5.6-sol
effort: xhigh
started: 2026-09-11 10:20 · terminal: term_c19d07

## Goal
Tell us what an attacker can do with our upload pipeline. We do not have a
threat model, a list of concerns, or a view on which parts are risky; the
pipeline takes a user file, stores it, scans it, makes thumbnails and
serves it back. Work out what matters, look for it, and rank what you find
by how bad it is. Nothing gets fixed in this brief.

## Context
The pipeline was rebuilt last month; see handoffs/merged/2026-08-11-upload-service-v2.md.
To see what is really stored you have read-only access to the production
bucket `uploads-prod` through the `audit-ro` AWS profile (keys are in the
ops vault). The bucket holds real users' files, including ID documents.
Open only what you need, copy nothing out, and quote no file contents in
the handoff.

## Scope
- May touch: `handoffs/inbox/` (your handoff only)
- Must not touch: `services/upload/`, `infra/terraform/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Map the pipeline and the trust boundaries.
2. Decide which attack classes apply and go looking for each.
3. Write the findings with severity and a suggested direction for each fix.

## Checks
None that can be automated. For each finding, say how you confirmed it or
why you could not.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

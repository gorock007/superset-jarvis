# Design a third-party plugin system for tidyctl
worker: claude
model: opus (amber band; fable-tier task)
effort: high
started: 2026-09-10 11:00 · terminal: term_93ad10

## Goal
Users want to add their own subcommands to tidyctl without forking it. We
have not decided anything: subprocess plugins found on PATH, Go's plugin
package, WASM modules, or an embedded scripting language. Nor have we
decided how plugins are discovered, versioned, or sandboxed. Produce the
decision and the interface. No implementation in this brief.

## Context
tidyctl is a single static Go binary shipped for macOS, Linux and Windows.
The command registry was reworked recently; see
handoffs/merged/2026-07-30-tidyctl-command-registry.md. Two community forks exist only
to add one command each, which is what prompted this.

## Scope
- May touch: `docs/rfcs/`

## Phases
1. Compare the options against: cross-platform, static binary, crash isolation, author effort.
2. Pick one and specify the plugin contract.
3. List what the build brief after this one should contain.

## Checks
None. The output is a decision; it gets reviewed by a person.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.

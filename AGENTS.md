# AI Engineering Stack

## Purpose and scope

Build a personal, lightweight stack installed per project, with an everyday ODD
workflow and optional SDD after user approval. Codex is the first target client.
Read `specs/00-foundation.md` and `docs/decisions.md` before adding features.
The user's request takes precedence over this repository's recommendations and drafts.
Keep all stack content in English: documentation, instructions, role contracts,
skills, templates, configuration descriptions, code comments, and tool messages.

## Working practices

- Keep shared content, technology profiles, and assistant adapters separate.
- Ask about unresolved product decisions; continue independent, reversible work.
- Record answers in `docs/decisions.md` and synchronize affected documents.
- Do not turn recommendations into approved requirements or enable every module by default.
- Define expected behavior before coding; use the lightweight flow in `docs/workflow.md`.
- Propose SDD with a concrete reason and activate it only with explicit approval for that change.
- Do not require SDD documents or additional agents for every change; reuse existing work.
- Do not install this stack in Meritum as part of building the stack.

## Evidence

`agents/` contains role contracts, not native agent configurations.
`skills/` contains distributable content; its presence does not imply installation or client activation.
`mcp/catalog.json` contains candidates, not configured connections.
Do not claim working compatibility, installation, CI, or deployment without verification.

Current validation: `python3 scripts/validate.py`.
Also validate skill changes with the Agent Skills validator available in the environment.

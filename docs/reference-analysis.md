# gentle-ai analysis

Reviewed on 2026-10-12. Scope: README, component documentation, architecture,
repository map, and integrations on `main`. Its code was not run or audited.
The documentation warns that `main` may contain unreleased changes.

## Findings

[gentle-ai](https://github.com/Gentleman-Programming/gentle-ai) configures existing
assistants through a Go CLI/TUI. Its scope includes memory, skills, MCP, personas,
permissions, and review. The number of integrations explains part of its
complexity; a personal stack does not need all of them.

The [component documentation](https://github.com/Gentleman-Programming/gentle-ai/blob/main/docs/components.md)
states that v4 retired SDD and its skills in favor of ODD. Installing the current
version should therefore not be assumed to provide the requested SDD workflow.
It also distinguishes bundled skills from framework skills maintained in a
separate repository.

The [codebase guide](https://github.com/Gentleman-Programming/gentle-ai/blob/main/docs/CODEBASE-GUIDE.md)
separates the catalog, planning, change application, adapters, and verification.
The [integrations](https://github.com/Gentleman-Programming/gentle-ai/blob/main/docs/codebase/integrations.md)
keep client-specific formats and paths inside the adapter.

## Ideas to reuse

- Selective installation through components and profiles.
- Separation between shared content and client formats.
- Preservation of edited configuration and recovery from changes.
- Readiness diagnostics and a distinction between configuring and running a tool.

## What to simplify initially

Our recommendation: a small CLI, one initial client, and a few modules.
Defer the TUI, themes, personas, automatic model selection, external memory,
code graphs, and a custom review protocol. These are future candidates,
not user requirements or demonstrated problems in the reference repository.

## Direction update: 2026-10-19

The [README](https://github.com/Gentleman-Programming/gentle-ai)
and [ODD workflow](https://github.com/Gentleman-Programming/gentle-ai/blob/main/docs/usage.md)
were reviewed again. ODD in the reference keeps small work lightweight and retains
context for substantial work. Our project adopts that direction and adds its own
extension: propose SDD and activate it only with explicit user approval.
This combination is a decision for our stack, not a capability attributed to
the current version of gentle-ai. Codex is the first target client.
See `docs/workflow.md` and `docs/decisions.md` for the current rules; the following
comparisons provide context for choosing the SDD extension later.

## SDD alternatives

| Option | What it provides | Consideration for this stack |
| --- | --- | --- |
| Custom templates and skill | A small workflow controlled by the project | We maintain traceability and spec evolution |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | A change- and artifact-based workflow adaptable to existing projects | Evaluate as an engine before building an equivalent |
| [Spec Kit](https://github.com/github/spec-kit) | Specs, planning, tasks, implementation, and convergence | Evaluate its process and dependencies against the desired simplicity |

Recommendation: try OpenSpec against our templates with a small feature before
choosing. If an external engine is adopted, avoid two simultaneous SDD workflows
and maintain a clear source of truth.

## Codex and distribution

The [official skill documentation](https://learn.chatgpt.com/docs/build-skills)
describes `SKILL.md` and local discovery in `.agents/skills/`.
It also recommends plugins for distributing reusable packages of skills and
connectors. Evaluate that route as an adapter; the core will remain portable.
These formats do not guarantee that Markdown contracts in `agents/` run as
subagents: that integration needs client-specific configuration and tests.

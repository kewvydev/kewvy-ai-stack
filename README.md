# AI Engineering Stack

A personal stack for setting up projects with **a lightweight workflow inspired by ODD**,
optional SDD, agent roles, skills, tools, and selectable MCP integrations.

## Status

A content foundation and Python standard-library CLI for global Codex core
installation and project initialization. Preview, state, conflicts, updates, and
rollback are tested in temporary directories. Native Codex instruction discovery
is checked with a local Responses fixture; model compliance is not tested.

The SDD skill and four role contracts remain prepared content. Native custom
agents, technology profiles, hooks, MCP connections, and CI/CD are not installed.

All stack content is maintained in English.

## Proposed design

A small core with optional modules. Codex is the first target client. Shared global
workflow guidance and local project context have separate canonical templates.

```text
agents/       Reusable role contracts
skills/       Distributable skills; currently sdd-workflow
templates/    Global guidance, project context, and decision templates
profiles/     Module selection; currently core
mcp/          Candidate integration catalog
adapters/     Codex core mapping and contract for future adapters
specs/        Requirements for the stack itself
docs/         Analysis, recommendations, decisions, and roadmap
scripts/      Local content validation
tools/        Python installation CLI
tests/        Temporary-project installer tests
stack.json    Content index and project status
```

## Start here

- [Foundation requirements](specs/00-foundation.md).
- [Everyday workflow and SDD activation](docs/workflow.md).
- [Installation, updates, ownership, and recovery](docs/installation.md).
- [gentle-ai analysis](docs/reference-analysis.md).
- [Module recommendations](docs/catalog.md).
- [Open questions and decisions](docs/decisions.md).
- [Roadmap](docs/roadmap.md).

The everyday flow is **understand → explore → implement → verify**.
When more definition is needed, the agent proposes SDD, explains why, and
**waits for your approval before activating it** for that change. SDD defines
a spec and acceptance criteria, plans the work, implements it, and retains evidence.
Existing templates remain available in `skills/sdd-workflow/assets/`.
The `core` profile does not include skills, specialized agents, or MCP by default;
the available content index is not an installation selection.

## Validate and test

```bash
cd ~/Dev/ai-engineering-stack
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/check_codex_loading.py
```

The tools use Python 3.9+ standard library. The loading check also needs Codex CLI,
Git, and a loopback port. It uses temporary configuration and a local fixture,
rather than a model or external service. Linux is the tested platform.

## Install the core

```bash
python3 tools/stack.py install --dry-run
python3 tools/stack.py install
# Use ~/.local/bin/ai-stack directly if ~/.local/bin is not on PATH.
ai-stack init /absolute/path/to/existing-project --dry-run
ai-stack init /absolute/path/to/existing-project
```

Global defaults are `~/.local/share/ai-engineering-stack`, `~/.local/bin`, and
`$CODEX_HOME` (normally `~/.codex`). Global guidance applies to all Codex projects.
Read the [installation guide](docs/installation.md) before applying it to your
personal environment. Development tests do not install into personal configuration
or Meritum. Project initialization persists state and a user-owned decision record;
it adds no external memory or application storage.

The next profiles target NestJS, React, Next.js, and Spring Boot. Their versions
and contents remain unselected. The SDD engine is still undecided.

Design reference: [gentle-ai](https://github.com/Gentleman-Programming/gentle-ai).
Additional architectural reference: [clawd-harness](https://github.com/orrrrli/clawd-harness).
This implementation uses original content and includes neither reference's code or assets.

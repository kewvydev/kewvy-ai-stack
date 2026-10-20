# AI Engineering Stack

A personal stack for setting up projects with **a lightweight workflow inspired by ODD**,
optional SDD, agent roles, skills, tools, and selectable MCP integrations.

## Status

A content foundation and Python standard-library CLI for global Codex core
installation and project initialization. Preview, state, conflicts, updates, and
rollback are tested in temporary directories. Native Codex instruction discovery
is checked with a local Responses fixture; model compliance is not tested.

Version 0.3.0-dev adds selectable NestJS, React, Next.js, and Java/Maven Spring Boot
profiles, three pinned skills, the native verifier, and task/finding records.
Context7 and GitHub have an explicit configuration profile; authentication and
real connections remain pending. Hooks, extra memory services, and CI/CD are not installed.

All stack content is maintained in English.

## Proposed design

A small core with optional modules. Codex is the first target client. Global optional catalogs
and local project workflow have separate canonical templates.

```text
agents/       Reusable role contracts
skills/       SDD, framework and selected global skills with provenance
templates/    Global guidance, project context, and decision templates
profiles/     Shared core and separate technology selections
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
- [Source research, selections, and limitations](docs/evolution-research.md).
- [gentle-ai analysis](docs/reference-analysis.md).
- [Module recommendations](docs/catalog.md).
- [Open questions and decisions](docs/decisions.md).
- [Roadmap](docs/roadmap.md).

The everyday flow is **understand → explore → implement → verify**.
When more definition is needed, the agent proposes SDD, explains why, and
**waits for your approval before activating it** for that change. SDD defines
a spec and acceptance criteria, plans the work, implements it, and retains evidence.
Existing templates remain available in `skills/sdd-workflow/assets/`.
The `core` profile includes diagnosis and the approval-gated SDD skill; the global
installation supplies the verifier.
The content index also lists prepared content that is not automatically installed.

## Validate and test

```bash
cd ~/Dev/kewvy-ai-stack
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
`$CODEX_HOME` (normally `~/.codex`). The global catalog is visible in all Codex projects; ODD applies only after project initialization.
Read the [installation guide](docs/installation.md) before applying it to your
personal environment. Development tests do not install into personal configuration
or Meritum. Project initialization persists state and a user-owned decision record;
it retains incomplete tasks and reusable findings without external memory or application storage.

Use `ai-stack init /absolute/path --profile nestjs|react|nextjs|spring-boot` to
select a technology profile. Next.js shares React skills without duplication.
Java/Maven is the Spring Boot preference; installed versions are inspected rather
than upgraded automatically. The SDD engine is still undecided.

Design reference: [gentle-ai](https://github.com/Gentleman-Programming/gentle-ai).
Additional architectural reference: [clawd-harness](https://github.com/orrrrli/clawd-harness).
This implementation uses original content and includes neither reference's code or assets.

## Approved workflow and global skills (0.4.0-dev)

Every profile now installs `sdd-workflow` and its four templates. Availability
does not approve using SDD for a change. Global installation supplies ponytail,
grill-me, tdd, diagnose, improve-codebase-architecture, handoff,
web-design-guidelines, frontend-design and vercel-composition-patterns. Existing
user-global skill bodies are reused without ownership or replacement. Only a small
stack-owned invocation policy is added; unowned policy conflicts are preserved. These global
skills are available to projects without copying them into every repository.
Framework skills remain separated by profile.

The native security-auditor reports critical/high risks using an explicit OWASP
checklist, evidence and uncertainty. It inherits the parent's model/permissions
and does not patch or save memory. The parent retains confirmed patterns and
unfinished checks in existing local records. See [skills and auditor details](docs/skill-notes.md).

## Project subagents (0.5.0-dev)

All profiles install `codebase-explorer` and `test-engineer` in the project's
`.codex/agents/`. Explorer returns a concise map with file references and no edits.
Test engineer designs/writes scoped behavior, contract and regression tests, reuses
existing profile tools and applies TDD when requested. They inherit parent model
and permissions and remain available on demand. Update the global package, then
rerun project initialization; see [installation](docs/installation.md).

## Scoped skills and delegation (0.6.0-dev)

| Category entrypoint | Specialized guidance loaded only as needed |
| --- | --- |
| stack-engineering | diagnose, tdd, improve-codebase-architecture |
| stack-ui | frontend-design, web-design-guidelines, vercel-composition-patterns |
| stack-productivity | ponytail, grill-me, handoff |

The three short entrypoints support automatic selection by task. Specialized
skills are omitted from implicit discovery and loaded through the relevant link,
or directly with `$skill-name`. Interviews, architecture review, handoff and TDD
retain their request gates. Backend-only work does not select UI guidance.

ODD lives in initialized projects. Global installation supplies an optional catalog,
without mandating audits or imposing ODD/records on uninitialized repositories.
Use one agent by default; custom agents require explicitly requested delegation
or review. This replaces the earlier global auth/pre-merge auditor mandate.
Update global installation and explicitly selected projects, then start a fresh
session. Existing chats can retain previous instructions and history. See
[workflow](docs/workflow.md) for scope and [verification](docs/foundation-verification.md)
for the distinction between discovery checks and actual model behavior.

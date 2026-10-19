# Recommended catalog

Entries are proposals unless explicitly identified as prepared or implemented.
Priority reflects usefulness for this personal stack, not a popularity ranking.

## Core and optional modules

| Module | Purpose | Status |
| --- | --- | --- |
| Lightweight ODD | Understand, explore, implement, and verify proportionately | Everyday flow documented in `docs/workflow.md` |
| Optional SDD | Define behavior, plan, and evidence per change | Skill and templates; activate only with approval |
| Agents | Coordinator, architect, implementer, and verifier | Four contracts; native verifier selected and discoverable |
| Testing | Behavior, contract, and regression tests | Proposed skill |
| Debugging | Reproduce, identify the cause, fix, and verify | Approved diagnosis skill packaged and discoverable |
| Architecture | Boundaries, alternatives, ADRs, and compatible migrations | Proposed skill |
| Code review | Actionable findings with evidence and severity | Proposed skill |
| CI/CD | Reproducible checks and pipeline diagnosis | Proposed skill |

Roles define responsibility, input, and output. Skills describe reusable workflows.
A skill can serve several roles. Do not start four agents for every task; decide
delegation based on the work and client capabilities.
Available contracts and skills are not selected automatically in `core`.
Revisit the following proposals in stages; they are not a mandatory package.

## Optional profiles

- `web-typescript`: frontend, accessibility, API contracts, and browser testing.
- `backend-node`: services, validation, authorization, contracts, and observability.
- `mobile-expo`: navigation, persistence, permissions, mobile testing, and builds.
- `data`: schemas, migrations, and data access review.
- `delivery`: CI, releases, and deployment for the selected provider.

These capability groups remain proposals; the framework profiles described next are implemented without installing framework dependencies.
These older capability groups are not the confirmed framework profile names.
Future entry points are NestJS, React, Next.js, and Spring Boot, with React
content shared by Next.js. These four profiles plus `core` are now implemented.
Choose testing tools and linters per profile and reuse each project's existing
tools; do not let the installer change its toolchain without explicit selection.

## Installer tooling

Initial priorities: profile selection, previews, repeatable installation,
diagnostics, a versioned manifest, and change recovery.
A Python standard-library CLI was selected for the first core increment on
2026-10-19. Global installation, project initialization, preview, state, conflicts,
updates, and recovery are implemented. Public distribution remains undecided.
See `installation.md` for the implemented contract and limits.

Project tooling: lint, type checking, and test commands; optional Git hooks;
secret and dependency checks; PR templates; and GitHub Actions if GitHub is the
chosen provider. Configure checks first; add deployments when the destination
is known. MCP integrations do not replace reproducible CI checks.

## MCP

| Integration | When it helps | Recommendation |
| --- | --- | --- |
| [Context7](https://github.com/upstash/context7) | Current library documentation | Selected definition; connection pending |
| [GitHub](https://github.com/github/github-mcp-server) | Issues, PRs, and Actions diagnosis | Selected definition; credentials and connection pending |
| [Playwright](https://github.com/microsoft/playwright-mcp) | Inspecting and interacting with web apps | Web profile only; separate exploration from CI tests |
| [Supabase](https://supabase.com/docs/guides/ai-tools/mcp) | Project context and database tools | Supabase projects only; project scope and read access initially |

Decision on 2026-10-19: enable none in the first increment. The table remains a
candidate list, not installation selection. The CLI leaves existing integrations alone.

For mobile, Playwright alone does not test a native app. Select device or emulator
tests according to the profile. Use the client's native shell, Git, and filesystem
capabilities when they already meet the need; avoid redundant MCP integrations.

## Later

- Skills for specialized security, performance, accessibility, and documentation.
- Persistence confirmed: installation state, project decisions, incomplete tasks,
  and reusable findings. No additional agent memory store or application database is selected.
- Design/Figma, error tracking/Sentry, work management, and deployment providers:
  choose based on the services actually used.
- Skill evaluations with realistic scenarios; versions and provenance for external skills.
- Model configuration and concurrency based on budget and client capabilities.

Each new integration should justify its task, permissions, maintenance, and
context cost before being included in a profile.

## Approved expansion — 2026-10-19

The initial catalog was a proposal; current selections are three external skills,
four technology profiles, verifier first, local tasks/findings, and Context7/GitHub
through an explicit native profile. The earlier no-integration selection describes
0.2.0-dev. Playwright, Supabase, hooks, and additional memory remain unselected.
See [source research](evolution-research.md) and [installation](installation.md).

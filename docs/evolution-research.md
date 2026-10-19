# Codex stack evolution research

Reviewed 2026-10-19. Current checkout: `~/Dev/kewvy-ai-stack` (renamed from
`~/Dev/ai-engineering-stack`). Research and file generation are distinguished
from native discovery, model behavior, authenticated connections, and deployments.

## Decisions and implementation

The user approved three selected skills, Context7 and GitHub, and the native
verifier first. Additional persistence means incomplete work and reusable
findings for other modules of the same project. Java with Maven is preferred;
recent stable versions are preferred, without automatic application upgrades.
No new storage service, background capture, model choice, or hooks were approved.

Implemented in 0.3.0-dev: four technology profiles plus core, selected skill
snapshots, a native verifier definition, user-owned task/finding seeds, and an
optional native MCP configuration profile. Everything remains English.

## clawd-harness: actual source review

Pinned reference: [ba57a721](https://github.com/orrrrli/clawd-harness/tree/ba57a721bc27dc9721da7569355eddbf4c92a6e0).
The inspected tree has 6 agent definitions and 19 skills. It explicitly targets
Claude Code. Its global installer links agents, sets an architect as the session
default, and links selected skills; project initialization filters skills by stack.
Its own documentation describes claude-mem plus Engram as separate memory layers.
No general repository license was found; no code or assets were copied from it.

Sources inspected: README, install-global.sh, init-project.sh, PERSISTENT-MEMORY.md,
global-rules.md, global/behavior.md, agent definitions, and Git guard hook source.

Useful ideas: separate global installation and project context, narrow triggers,
review against acceptance criteria, retain root causes with evidence, and use
technology selection. Adapt client paths, tool names, agent formats, and hooks.
Do not copy its always-architect routing, compulsory multiagent test phases,
absolute coding rules, automatic memory split, or all integrations.

The Git hook source uses command-text heuristics and itself documents bypasses.
It is not a universal authorization boundary. Our existing state/hashes and
snapshot update protections remain in place instead of adopting live symlinks.

## Approved skills

Only selected directories were imported, not upstream collections. Revisions and
license evidence are in [provenance](../skills/provenance.json). Adapted entrypoints
are short; original guidance is retained under references and read on demand.

| Skill | Maintainer / license | Concrete purpose and scope | Dependencies, overlap, and compatibility |
| --- | --- | --- | --- |
| nestjs-best-practices | Kadajett; MIT declared in skill; repository pushed 2026-07-23 | NestJS modules, DI, input/API boundaries, authorization; NestJS profile | No runtime dependency from the skill. Examples mention libraries and patterns that are not automatically adopted. Use project versions and official NestJS docs. Format/discovery checked; framework behavior not evaluated. |
| vercel-react-best-practices | Vercel; MIT declared in skill; repository pushed 2026-10-14 | Rendering/data-fetching/bundle review; shared React/Next.js capability | React skill reused once through inheritance. Next.js-specific rules do not apply to plain React. Example dependencies are not installed. Format/discovery checked; app performance not evaluated. |
| diagnosing-bugs | Matt Pocock; repository MIT license retained; repository pushed 2026-10-13 | Focused reproduction and diagnosis for difficult failures; core capability | Uses existing test/runtime tools. Optional shell helper retained and syntax-checked. A separate debugger agent would overlap and was not selected. |

Sources: [NestJS skill](https://github.com/Kadajett/agent-nestjs-skills),
[React skill](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices),
[diagnosis skill](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs).
A repository push is maintenance activity, not evidence that every rule is current
or improves agent outcomes. Future updates require re-review and explicit snapshots.

Not imported: Matt Pocock's code-review skill requires parallel agents and tracker
setup; its TDD skill introduces additional choices. Our verifier reuses the current
contract. No blanket testing methodology or entire collection was selected.

## Four project entry points

`init --profile nestjs|react|nextjs|spring-boot` configures existing directories.
Core supplies diagnosis and recordkeeping. Next.js inherits React without a second
copy. Spring Boot uses Java/Maven context and existing test/build commands; no
Java framework is generated. Missing manifests are reported as missing context.
Dependency ranges are recorded as declared, not claimed as resolved versions.

For Next.js, prefer documentation shipped with the installed version when present.
The former next-skills repository moved workflow skills to Next.js itself. The
inspected next-dev-loop requires Next.js 16.3+, Turbopack and agent-browser >=0.31.1;
it was not approved or installed. [Current Next.js guidance](https://nextjs.org/docs/app/guides/ai-agents).

Spring Projects publishes a Spring Tools validation skill and language-server
plugin, with Java 21+ and Maven/Gradle requirements. The inspected entrypoint names
Claude-specific MCP tools and invokes quickfixes; it needs adaptation rather than
being advertised as ready for Codex. Its repository declares EPL-1.0. It is deferred.
[Source](https://github.com/spring-projects/spring-tools/tree/main/claude-plugins/spring-tools).
Java, Maven, Gradle, gh and Docker were not on this host's PATH during inspection.
No Spring application build or integration test was run.

Keep commands reproducible outside Codex. Reuse Nest's testing utilities with the
existing runner, React's existing checks/DevTools, and Maven wrappers/Spring tests.
Architecture/API contracts and authorization remain project-specific. OWASP ASVS
can guide targeted review; it is not another required skill. CI and dependency
automation require a selected provider and project policy, not an AI-only command.
Sources: [Nest testing](https://docs.nestjs.com/fundamentals/testing),
[React tools](https://react.dev/learn/react-developer-tools),
[Spring testing](https://docs.spring.io/spring-boot/reference/testing/index.html),
[OWASP ASVS](https://owasp.org/projects/asvs),
[Dependabot](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference).

## Native verifier and global rules

The global installer writes `agents/verifier.toml` under the selected Codex home.
Input: authorized diff, expected behavior, project instructions, relevant records.
Output: criterion, evidence, result, actionable file/line findings and pending work.
Use on demand for independent verification; routine work stays in the parent.
No new model or parallelism policy is set. Tool access follows the parent; avoiding
edits is behavioral guidance, not an independent read-only sandbox.

Codex's standalone files require name, description, and developer_instructions.
Native discovery was checked with the installed CLI; model delegation was not.
[Official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Global rules retain ODD, SDD approval, evidence, and project-local recordkeeping;
framework conventions stay in profiles, avoiding duplicated global technology rules.

## Persistence comparison

| Mechanism | Role here | Tradeoff |
| --- | --- | --- |
| Installation JSON | Tool-owned state and file hashes | Not agent memory or application data |
| Decisions, tasks, findings Markdown | Project-owned authoritative records | Inspect/correct/retire entries; search with ordinary tools |
| Native Codex memory | Existing optional recall | Leads to verify; does not prove task completion |
| Engram | Unselected additional store | MIT; local SQLite/FTS5 and explicit Codex integration; another binary, session/project resolution and memory protocol |
| claude-mem | Unselected capture system | Apache-2.0; now includes Codex hooks/bridge; worker/runtimes and possible model quota/cost |

Codex already has local memory and per-chat controls. Required project knowledge
belongs in instructions and project records; generated native memory remains
separate and is not edited by this installer. [Official memory documentation](https://learn.chatgpt.com/docs/customization/memories).

Both external projects now publish Codex support. Engram's reviewed Codex skill
requires proactive saves, which would be an extra policy decision. claude-mem's
bridge documents limits to native-memory interception and optional note-root
capture. Supporting files exist; neither integration was installed or run here.
Sources: [Engram](https://github.com/Gentleman-Programming/engram),
[claude-mem](https://github.com/thedotmack/claude-mem),
[native bridge](https://github.com/thedotmack/claude-mem/blob/main/docs/native-memory-bridge.md).
The clarified requirement is met with local records, so another store is unnecessary.

## MCP selection and observed host configuration

No comparable usage metric was established; this is a task/maintenance shortlist,
not a claim about the most-used servers. Existing catalog flags remain distinct:
selected definitions do not prove authentication or a working connection.

| Candidate / status | Task and advantage over existing tools | Dependencies, permissions, cost, scope |
| --- | --- | --- |
| Context7: selected | Version-specific documentation when bundled docs/web lookup is insufficient | Upstash MIT, active 2026-10-19. Remote HTTP avoids a local runtime; API key, free/paid limits. Reusable personal profile. CLI is an alternative. |
| GitHub: selected | Structured repository/issue/PR/Actions access; overlaps with the desktop connector | GitHub MIT, active 2026-10-19. Remote HTTP avoids Docker; environment credential with least required permissions. Provider/API limits apply. |
| Playwright: unselected | Browser exploration; use existing browser or CLI first | Microsoft Apache-2.0, active 2026-10-16. Node >=18 and browser, local execution cost; project/web use. |
| Supabase: unselected by stack | Service/project inspection beyond local migration CLI | Official hosted server, OAuth and project permissions, service costs. Existing host entry is enabled but auth unknown; project scoped, no read_only=true. Left unchanged. |
| Chrome DevTools: research-only | Browser console/network/performance beyond existing browser support | Official Apache-2.0, active 2026-10-19. Node LTS, Chrome/npm; local execution cost, optional external performance services/usage reporting. Overlaps with Playwright. |

Sources: [Context7](https://github.com/upstash/context7), [plans](https://context7.com/plans),
[GitHub](https://github.com/github/github-mcp-server),
[Playwright](https://github.com/microsoft/playwright-mcp),
[Supabase](https://supabase.com/docs/guides/ai-tools/mcp),
[Chrome DevTools](https://github.com/ChromeDevTools/chrome-devtools-mcp).

CLI inspection before implementation found Supabase plus enabled native browser/
Node tool servers. code-review and codex_app entries were disabled in that CLI view;
that is not an inventory of every desktop connector. A GitHub desktop connector
successfully read public reference files. No claim about private-repository access
or token scope was made. The four original catalog entries remained unconnected.

The installer provides `stack-development.config.toml`, selected using
`codex --profile stack-development`, without editing existing config.toml.
It references CONTEXT7_API_KEY and GITHUB_MCP_TOKEN from the local environment.
The CLI recognizes both definitions; authentication and real calls remain pending.
Do not paste credentials in chat. No personal configuration was installed here.

## Hooks

The installed CLI is 0.162.1; hooks, memories and multi_agent flags are enabled.
Codex documents JSON or inline TOML, trusted definitions, and command/MCP handlers;
prompt/agent handlers are skipped. Matching hooks accumulate rather than replacing
lower layers. Supported lifecycle events include SessionStart/End, UserPromptSubmit,
Pre/PostToolUse, PermissionRequest, Pre/PostCompact, SubagentStart/Stop, Stop and Interrupt.
Errors can allow operations to continue, so hooks are not a complete security boundary.
[Official hooks](https://learn.chatgpt.com/docs/hooks).

No hooks are installed: the user approved verifier first and postponement of hooks.
A future SessionStart record reminder or bounded Stop check must justify its overlap
with native instructions, define dependencies/timeouts/failure behavior, and support
review/disable. No automatic transcript capture or Claude hook reuse is implied.

## Acceptance and evidence

The increment must preserve no-write preview, file ownership, update/rollback,
user records, and independent profile selection. Run content and Agent Skills
validators, installer tests, and native discovery against a local fixture.
Record exact results in foundation-verification.md. No connection or real model
behavior may be inferred from generated files or simulated Responses output.

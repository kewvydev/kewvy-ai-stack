# Questions and decisions

## Confirmed

A standalone project in `~/Dev/`, easy installation, agents, skills, tooling, and MCP.
Build gradually, using gentle-ai as a design reference.

Decisions from 2026-10-19:

- A lightweight everyday workflow inspired by ODD, with SDD available when needed.
- The agent proposes SDD with a reason and asks the user before activating it.
- Codex is the first client for testing the stack; this does not imply verified compatibility.
- Build in stages, asking about the decisions needed for each stage.
- Keep the entire stack in English, including documentation, instructions, skills,
  templates, configuration descriptions, code comments, and tool messages.
- Keep a global installation complemented by project-specific initialization.
- Start with a Python CLI. Use the standard library for the first core increment;
  the existing Linux environment is the test platform, not proof of other OS support.
- Persist installation state and the decisions of each project. Do not introduce
  another agent memory store or infer application data persistence.
- The initial increment enabled no MCP integrations; the approved expansion selects Context7 and GitHub definitions, with authentication verified separately.
- Target separate NestJS, React, Next.js, and Spring Boot profiles in later increments;
  share React content with Next.js and inspect project versions before selection.

## Decision register

| ID | Question | Initial recommendation | Answer |
| --- | --- | --- | --- |
| AQ-01 | Which assistants, and which one first? | One adapter first | Resolved: Codex first; others pending |
| AQ-02 | Which project types and frameworks? | A few profiles for frequent project types | Resolved: separate NestJS, React, Next.js and Spring Boot profiles; Java/Maven and recent stable versions preferred; inspect actual project versions |
| AQ-03 | How should SDD activate? | Propose it when definition or traceability would help | Resolved: everyday ODD; SDD after proposal and explicit approval per change |
| AQ-04 | Custom SDD, OpenSpec, or Spec Kit? | Keep templates available; evaluate the engine when working on SDD | Pending; does not block the lightweight flow |
| AQ-05 | Per-project installation, global, or both? | Per project initially, including existing repositories | Resolved: global stack plus initialization of existing projects |
| AQ-06 | CLI and which operating systems? | A simple CLI; Linux first if it covers actual use | Python CLI confirmed; Linux is the current test environment; wider OS support pending |
| AQ-07 | How much autonomy should agents have? | Autonomous local work; external actions follow user authorization | Pending |
| AQ-08 | Which roles, and when to delegate? | Coordinator, architect, implementer, and verifier on demand | Global verifier/security-auditor plus project codebase-explorer/test-engineer approved; security-sensitive and pre-merge review use the report-only auditor; other roles pending |
| AQ-09 | Standard testing or TDD? What coverage matters? | Behavior- and risk-based tests; TDD when useful | Pending |
| AQ-10 | GitHub or another provider? Where will projects deploy? | CI checks before deployment automation | Pending |
| AQ-11 | Which MCP integrations first? | Documentation; GitHub if used; others by profile | Initial increment: none. Expansion: Context7 and GitHub selected; isolated configuration profile, authentication pending; existing connections preserved |
| AQ-12 | Markdown memory or an external service? | Versioned Markdown first | JSON installation state and project-local decisions, incomplete tasks and reusable findings; no additional memory service or application database |
| AQ-13 | Which language should the stack use? | One consistent language | Resolved: English throughout the stack |
| AQ-14 | Personal use or public distribution? | Local use first; choose a license before publishing | Pending |
| AQ-15 | Import maintained skills or write custom ones? | Custom workflow skills; selected external skills with versions and licenses | Approved: nestjs-best-practices, vercel-react-best-practices, diagnosing-bugs; selected pinned directories with concise Codex adaptations |
| AQ-16 | Model budget and concurrency limits? | No automatic model selection or parallel agents yet | Pending |

## Recording answers

Record the date, answer, and affected documents when a question is resolved.
Recommendations in this table are not approved decisions.
The decisions from 2026-10-19 replace mandatory SDD as the starting point and are
reflected in `docs/workflow.md`, instructions, the skill, contracts, the profile,
the manifest, README, requirements, and roadmap. English is recorded in AQ-13 and
applies to all stack content. Revisit other questions as their stage approaches;
there is no need to decide the entire catalog now.

## First installer approval — 2026-10-19

Source: the user answered the first milestone questions with Python CLI,
installation state and project decisions, and no integrations. The earlier
request confirmed global installation with project initialization and the four
framework targets. This approves implementing and testing the core in disposable
locations; it does not activate SDD, choose native roles, enable integrations,
or install into Meritum or the user's personal Codex configuration.

The first implementation uses managed instruction blocks, hash-based ownership,
an explicit local snapshot, a conservative one-operation rollback, and a seed-only
project decision record. These are the implementation choices for the approved
preview, preservation, update, and recovery criteria. The CLI does not fetch updates.

Affected documents: requirements, README, workflow, roadmap, catalog, adapter
contract, installation guide, manifest, core profile, and verification record.

## Approved evolution — 2026-10-19

The user approved all three proposed skills, Context7 plus GitHub, and verifier
first. They clarified additional persistence as unfinished tasks and findings
useful to other modules. Java uses Maven; recent versions are preferred.
The earlier no-MCP decision applies to the initial increment, not this expansion.
Hooks remain postponed as proposed. Engram, claude-mem, browser MCPs, automatic
upgrades, extra agents and model overrides are not selected.

Implemented 0.3.0-dev in the renamed `~/Dev/kewvy-ai-stack` checkout. The global
package contains selected skill snapshots; project initialization activates only
its profile's skills. The verifier and an explicit MCP configuration profile are
installed into the selected Codex home. Task/finding records are user-owned seeds.
Authentication, native model compliance and framework runtime checks remain
separate evidence. See evolution-research.md and foundation-verification.md.

## Workflow skill and requested catalog expansion — 2026-10-19

The user explicitly requested installation of `sdd-workflow`, incorporation of
nine named existing global skills, and a `security-auditor` based on their supplied
contract. Availability of SDD now belongs to the shared profile; activation still
requires approval for each change. This supersedes AC-07's packaging exclusion.

Expected behavior before implementation:

- Package SDD and all four templates; initialize it in every project profile.
- Updating an installed project preserves framework content, local instructions,
  decisions, tasks, and findings. Repeat installation writes nothing.
- Import the user's actual skill versions with provenance and license evidence.
- Adapt security auditing to supported Codex capabilities, report only, with
  explicit trust-boundary checks, evidence and unresolved risks kept distinct.
- Validate packaging, conflict handling, updates, rollback and native discovery;
  do not equate discovery with model compliance or a completed security audit.

Pending answers: locations of seven skills, global versus per-profile distribution,
and the Codex/local-record adaptation of the supplied Opus/Engram agent. Continue
independent SDD work while those choices remain open.

The user answered the pending questions in this conversation:

- Search skills.sh for missing skills and use the actual upstream sources.
- All nine requested additions are global stack skills; SDD remains available
  through every project profile. Installation does not activate every workflow.
- Adapt security-auditor to Codex model inheritance and existing local records.
  The report-only auditor returns proposed entries; the parent records them.
- Reuse existing user-global ponytail/frontend-design instead of installing
  duplicates; preserve their owners and content. The stack retains snapshots.

The global installer checks the destination selected by `--skills-dir` (default `~/.agents/skills`) for
matching names before installing a new global skill. Reused entrypoint paths and
hashes are recorded as external dependencies, never as owned files. They may
differ from the stack snapshot and remain updated by their original manager.
Other selected global skills are managed under the selected global skills
directory. Existing stack-owned copies stay owned on subsequent operations.

Source review found grill-me is a wrapper for grilling and diagnose was renamed
to diagnosing-bugs. Include the interview reference under grill-me and retain
diagnose as a compatibility entrypoint, reusing project diagnosing-bugs when present.
No additional discoverable skills or mandatory subagents are introduced to satisfy
upstream references. Preserve explicit-only invocation for grill-me, handoff and
improve-codebase-architecture using their native Codex policy metadata. TDD remains
selectable for a change; it does not resolve AQ-09 as a universal testing mandate.

The supplied Claude frontmatter is adapted rather than copied: Opus, color, Bash/
Read tool grants and Engram calls are not Codex agent settings. Native agents
inherit parent permissions. A report-only instruction is not a technical sandbox;
use a parent read-only session for filesystem enforcement. OWASP Top 10:2025 is
the checklist source, with confirmed critical/high findings distinguished from
uncertain high-impact concerns. No new model provider, memory service or hooks.

## Project exploration and test agents — 2026-10-19

The user requested two additional subagents installed inside projects:
`codebase-explorer` maps modules, dependencies, conventions and impacted files
without editing code; `test-engineer` designs and writes behavior, contract and
regression tests using existing profile tools, with TDD when requested.

Expected behavior before implementation:

- Every profile's project initialization installs both native TOML files under
  `.codex/agents/`; they are not added to personal/global native agent directories.
- The global package carries their adapter sources so the installed launcher
  works without access to the original checkout. Reusable contracts stay in agents/.
- Existing client configuration, other agents, user records and application code
  are preserved. Dry-run, conflicts, repeat initialization and rollback use the
  existing ownership protections. Modified or unowned agent files are not replaced.
- Both inherit the parent model and permissions. Explorer is report-only by
  instruction, not a separate filesystem sandbox. Test engineer changes only the
  assigned tests/fixtures/helpers unless its assignment also authorizes other code.
- Agent availability does not mandate delegation, a new test framework, universal
  TDD or SDD. TDD follows the user's requested scope and existing agreed criteria.
- Verify all-profile installation, scope separation, preservation, conflicts,
  prior-release update/rollback and native Codex discovery separately from behavior.

This adds the two approved native roles to AQ-08; other roles remain pending.
It does not resolve universal testing policy, budgets or an SDD engine.

Native discovery verification uses a trusted temporary repository. Codex did not
advertise project-local agents before that fixture trust entry was added. Existing
user-global skills with duplicate names are disabled only in the fixture config
so explicit skill checks resolve its temporary copies. Real trust, permissions,
models and existing configuration are preserved by the installer.

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
| AQ-06 | CLI and which operating systems? | A simple CLI; Linux first if it covers actual use | Bash + jq migration confirmed on 2026-10-26; interactive profile selection; Linux is the test environment; wider OS support pending |
| AQ-07 | How much autonomy should agents have? | Autonomous local work; external actions follow user authorization | Pending |
| AQ-08 | Which roles, and when to delegate? | Coordinator, architect, implementer, and verifier on demand | Global verifier/security-auditor plus project codebase-explorer/test-engineer approved; security-sensitive and pre-merge review use the report-only auditor; other roles pending |
| AQ-09 | Standard testing or TDD? What coverage matters? | Behavior- and risk-based tests; TDD when useful | Pending |
| AQ-10 | GitHub or another provider? Where will projects deploy? | CI checks before deployment automation | Pending |
| AQ-11 | Which MCP integrations first? | Documentation; GitHub if used; others by profile | Initial increment: none. Expansion: Context7 and GitHub selected; isolated configuration profile, authentication pending; existing connections preserved |
| AQ-12 | Markdown memory or an external service? | Versioned Markdown first | Extended 2026-10-26: optional Obsidian memory in a shared vault, one folder per project; update after significant work; retain existing source records |
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

## Obsidian project memory — 2026-10-26

The user requested a persistent project brain in Obsidian so new Codex chats can
reuse context, and confirmed a shared vault with a separate folder per project
and updates after significant work. This supersedes AQ-12's exclusion of an
additional project memory location. It does not authorize modifying Codex's own
personal memory store, installing into other projects, or migrating existing notes.

Expected behavior before implementation:

- Explicitly connect an initialized project with a vault path and unique project
  slug. Keep the absolute machine-local binding under `.ai-stack/memory.json`.
- Use ordinary Markdown, frontmatter and vault-relative wikilinks under
  `Projects/<slug>/`. No plugin, MCP server, API key, database or daemon is needed.
- Seed a brief startup index and architecture, decisions, tasks and findings notes.
  They start unreviewed, not as a claim that the project has been analyzed.
- Read the index first, search only that project's notes and inspect relevant
  sources on demand. Record source paths, dates, revision and evidence limits;
  correct stale memory rather than treating it as authority over current code.
- Update useful memory after significant work. Preserve existing registers as
  canonical sources and link/summarize them; do not blindly copy task-status files,
  whole conversations, secrets or unrelated project information.
- Preview writes nothing; repeat connection preserves notes; reject collisions,
  unsafe paths and symlinks. Installer updates/rollback preserve notes and binding.
- Missing or inaccessible vaults produce an explicit fallback to local records.
  The adapter guides session behavior; it does not guarantee model compliance,
  automatic capture on interruption, filesystem permission grants or zero analysis.

Implementation choices within that scope: a standard-library CLI, explicit
`memory init`, `context`, `search` and `status` commands, seed-only notes, a folder
ownership marker, bounded retrieval, and no silent rebinding. Existing vaults are
required; opening/creating the actual Obsidian vault remains a user setup step.
Tests use disposable vaults only. The user's real vault path is not yet supplied.

Affected documents: foundation, workflow, installation guide, README, manifest,
project instructions and the memory guide/research record.

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

## Scoped skills and global leakage correction — 2026-10-19

The user reports unnecessary agents, UI work during backend tasks and excessive
token use, including in Meritum without local stack initialization. The user
selected engineering/UI/productivity categories activated by actual task need,
and explicitly required preserving Meritum's own decision rules unchanged.

Expected behavior before implementation: global availability must not impose
project ODD, task records or mandatory security review on uninitialized projects.
Default to one agent and complete the requested outcome with focused checks.
Custom agents remain available for explicitly requested delegation/review. Ordinary
auth work still needs appropriate implementation security checks by the main agent.
No model/effort, Meritum rules, hooks, MCPs or application code changes.

Three small category skills select only needed linked guidance. Nine leaf skills
are hidden from implicit discovery but remain explicitly invocable. Category
routing preserves the prior request conditions of interviews, handoffs, architecture
reviews and TDD. Original skill bodies stay at their existing names/paths.
Reused user-managed skills receive only a separately owned invocation policy;
existing unowned policy files block installation. Keep external body hashes and
ownership separate; test repeats, conflicts, real prior-version upgrade/rollback,
and native discovery independently of actual model behavior or token savings.

Observed cause: personal ~/.codex/AGENTS.md mandated security-auditor for auth,
untrusted input and pre-merge review across projects. Six global leaf skills were
implicitly discoverable, including UI. Meritum had no local installation metadata.
Its recent conversation also explicitly requested UI and later all M01 client
integration, and ended at a usage limit. This evidence does not establish that
every UI action was unrelated or quantify the stack's share of token consumption.


## Bash installer and interactive profiles — 2026-10-26

Source: the user requested replacing Python installation with a simpler Bash
script that installs the existing profile selected in the script. They explicitly
approved Bash + jq as a prerequisite, with no Python installation runtime.
This supersedes the Python implementation choice in AQ-06/RQ-13; Python remains
available for repository validation and migration fixtures.

Expected behavior before implementation:

- No-argument invocation opens a menu for global installation or initialization
  of an existing project with a catalog profile. Preview the concrete selection
  before asking to apply; explicit CLI commands remain available for automation.
- Read the existing core, NestJS, React, Next.js and Spring Boot JSON profiles,
  preserve inheritance and install only the selected project's capabilities.
- Preserve the distinction between global catalog installation and project init,
  schema-1 state, hash ownership, user files/records, dry-run, repeat installation,
  conflicts, updates and one-operation rollback.
- Support migration of Python-created installations with the same destinations;
  retire only the owned old runtime and restore it on rollback.
- Verify in temporary locations, without installing into personal configuration,
  Meritum or other existing projects. Do not activate SDD or additional agents.

Implementation choices: Bash 4.4+, jq 1.6+ and existing GNU utilities on Linux;
no automatic package installation. Keep Python tests and an isolated historical
runtime fixture. Native discovery and model behavior remain separate evidence.

Affected documents: README, foundation requirements, installation guide, adapter
contract, catalog, roadmap, manifest, tests and verification record.


## Terminal presentation and Python installer removal — 2026-10-26

Source: the user requested a polished Bash interface and deletion of unnecessary
Python installers. This supersedes retaining the executable historical fixture
in the first 0.7 iteration; Python test and validation tools remain in scope.

Expected behavior:

- Use the existing Bash installer with clear action/profile choices, concise
  descriptions, a compact destination/change review and a useful completion state.
- Keep prompts and content in English. Use the terminal font and palette: cyan
  for choices, bold for headings, dim for secondary text, green for success and
  yellow/red for warnings/errors. Color supplements readable text.
- Wrap text for narrow terminals, preserve scrollback and avoid animation or new
  UI dependencies. Suppress color for redirected output, NO_COLOR and TERM=dumb.
- Keep explicit command output usable in scripts; expose full interactive file
  details through --verbose. Preserve selection, preview, confirmation and safety.
- Remove the Python installer fixture and obsolete compiled installer cache.
  Retain only static schema-1 compatibility data and useful Python checks. State
  explicitly that a synthetic fixture does not execute the historical runtime.

Affected documents: README, installation guide, foundation requirements,
verification record and fixture notes. No skills, profiles or personal installation
are changed by this refinement.


## Confirm the current project directory — 2026-10-26

Source: the user requested replacing Existing project directory input with a
confirmation of the directory from which the installer was run.

Expected behavior: Project profile takes the caller's current working directory,
displays it and requires explicit confirmation before profile selection. A declined,
empty or interrupted confirmation writes no installation destinations. The script
and installed launcher may live elsewhere; neither location becomes the project
target. Global installation and explicit init TARGET commands retain their roles.

Affected documents: README, installation guide, foundation requirements, menu
regression checks and verification record. Existing path and ownership protections
continue to apply.

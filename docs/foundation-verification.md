# Foundation verification

Date: 2026-10-12. Scope: initial local content, without adapters or an installer.

| Criterion | Evidence | Result |
| --- | --- | --- |
| AC-01 | Files in `/home/kewvy/Dev/ai-engineering-stack`; a standalone Git repository initialized | Pass |
| AC-02 | Project, spec, plan, task, verification, and ADR templates present and referenced | Pass |
| AC-03 | Four contracts in `agents/`; `skills/sdd-workflow/SKILL.md` passes the skill validator | Pass as content |
| AC-04 | Open decisions and recommendations identified in `docs/decisions.md` and `docs/catalog.md` | Pass |
| AC-05 | `python3 scripts/validate.py`: valid references, local links, IDs, and metadata | Pass |

Verification confirms content integrity and skill format. It does not prove model
behavior, client skill discovery, native agents, installation, MCP connections,
CI/CD, or deployment. Those checks belong to later stages.

## ODD and optional SDD update — 2026-10-19

| Criterion | Evidence | Result |
| --- | --- | --- |
| AC-06 | Instructions, README, templates, and `stack.json` describe the everyday ODD flow | Pass as content |
| AC-07 | Workflow, coordinator, and skill require SDD approval; `core` selects no skills or roles | Pass as content |
| AC-08 | `firstClient` identifies Codex; `supportedClients` remains empty | Pass as content |

Both `python3 scripts/validate.py` and
`quick_validate.py skills/sdd-workflow` were run again and passed. References to
the previous approach were reviewed to keep instructions and contracts aligned.
The user confirmed the activation policy and Codex priority in this conversation.

Approval is defined in instructions rather than enforced by an executable engine.
Codex behavior was not tested; connections and installation were not implemented.

## English content update — 2026-10-19

AC-09: all 26 Markdown, JSON, and Python content files were updated to English,
including role contracts, skill instructions, template placeholders, descriptions,
and validator messages. AQ-13 records the decision; `stack.json` declares
`language: en`, and project instructions require English for future stack content.

Both content and skill validators passed. Comparison with the pre-translation
snapshot confirmed that validator structure, existing configuration values,
link targets, and template placeholder counts were preserved. Descriptive JSON
text was translated and the language field was added. A scan for common Spanish
terms found no remaining matches in Markdown, JSON, or Python files.

These checks cover the language update and content integrity, not runtime behavior
in Codex or other clients.

## Python Codex core increment — 2026-10-19

User decisions: Python CLI, global installation plus project initialization,
installation state and project decisions, and no MCP integrations. No SDD
activation or native custom agent registration was included.

| Criterion | Executed evidence | Result |
| --- | --- | --- |
| AC-10 | Temporary global package, executable launcher (including a path with spaces), and existing project initialization exercised through subprocesses | Pass on Linux |
| AC-11 | JSON state with scope, roots, version, selection, and hashes; user-edited decision record survives reinstall, update, and rollback | Pass |
| AC-12 | Dry-run snapshots, repeat install, existing instructions/config, modified managed content, unowned metadata, symlinks, overrides, malformed markers, and unsafe source paths | Pass |
| AC-13 | Synthetic 0.2.0-dev to 0.3.0-test update, global/project rollback, injected write exception, and injected interruption before state commit | Pass |
| AC-14 | Actual codex-cli 0.162.1 sends assembled global/project instructions in order to a local Responses fixture; nested AGENTS.override.md excludes its sibling AGENTS.md | Pass for discovery only |

Executed commands:

```text
python3 scripts/validate.py
Valid stack content: 4 roles, 1 skill, 1 profile and 4 MCP candidates.

python3 -m unittest discover -s tests -v
Ran 19 tests. OK

python3 /home/kewvy/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-workflow
Skill is valid!

python3 scripts/check_codex_loading.py
PASS: Codex request contains ordered global and project instructions (project).
PASS: Codex request contains ordered global and project instructions (nested).
Verified instruction discovery with codex-cli 0.162.1; model behavior was not tested.
```

Environment: Linux, Python 3.14.7, Codex CLI 0.162.1. The standard-library APIs
target Python 3.9+, but no separate run on the minimum Python version was made.
The Codex fixture needed loopback access outside the execution sandbox. It used
no real model or credentials and all installation destinations were disposable.

Created: Python CLI, core Codex template mapping, global rules, project decisions
template, installer tests, native discovery fixture, and installation documentation.
Updated: project context template, decisions, requirements, manifest, core profile,
validator, workflow, adapter contract, roadmap, README, and catalog.

Configured and executed: global snapshots and project initialization in temporary
directories; native CLI sessions with a local simulated Responses endpoint.

Not configured: personal/global user installation, Meritum, optional profiles,
custom agents, hooks, MCP, CI/CD, additional memory, and application databases.
Not verified: model instruction compliance or SDD approval behavior, desktop UI,
other operating systems, real integrations, concurrent installers, or power-loss
recovery. One-operation recovery and layout-migration limits are documented in
`installation.md`. `supportedClients` remains empty to avoid implying broader
compatibility than the named CLI discovery check.

## Approved profiles, skills and records — 2026-10-19

Version 0.3.0-dev. The user's answers approved the three skills, Context7/GitHub,
verifier first, Java/Maven with recent versions preferred, and persistence of
incomplete tasks and reusable project findings. Hooks and extra memory remain deferred.

| Criterion | Evidence | Result |
| --- | --- | --- |
| AC-15 | Four profile subprocess scenarios; Next.js shares the React skill once; manifest ranges and Maven/POM context retained without scaffolding | Pass for configuration |
| AC-16 | Three pinned directories, concise entrypoints, retained original guidance/provenance, four Agent Skills validator passes including existing SDD | Pass for packaging and format |
| AC-17 | User-edited tasks/findings survive update and rollback; guidance preserves unfinished criteria and correction history | Pass for preservation; model recordkeeping not evaluated |
| AC-18 | Actual Codex CLI 0.162.1 advertises the verifier and each selected skill in core, nested, NestJS, React, Next.js and Spring Boot request scenarios; recognizes both MCP definitions using stack-development | Pass for discovery/configuration; no delegation/authentication |
| AC-19 | Genuine e05526a baseline 0.2.0-dev installed, upgraded to 0.3.0-dev and rolled back using temporary source/package/project/Codex paths | Pass |

Executed: content validator; 25 installer tests; all four Agent Skills validators;
bash syntax check of the retained optional diagnosis helper; native loading fixture.
The helper was not executed interactively. Framework skills were not behaviorally
evaluated against applications. Java/Maven were absent from PATH, so no Spring
build ran. The native fixture uses a local Responses stub, no credentials and no
external calls. It verifies discovery, not model compliance or actual delegation.

The host's existing Supabase connection was inspected as configuration only:
enabled, project scoped, auth unknown and no read_only=true parameter. It was left
unchanged. No personal install, Meritum change, external authentication, deployment,
new storage layer, or hook activation was performed.

## Global skills, SDD availability and security-auditor — 2026-10-19

Version 0.4.0-dev. The user approved all nine named additions as global skills,
searching skills.sh for missing sources, reusing the existing ponytail/frontend-
design installations, and adapting the auditor to Codex with project-local records.
They explicitly requested installing SDD in the existing Next.js test project.

| Criterion | Executed evidence | Result |
| --- | --- | --- |
| AC-20 | All five profile selections package sdd-workflow and four assets; installed launcher uses the snapshot; installation creates no specs directory | Pass for packaging; approval behavior remains unevaluated |
| AC-21 | Nine global selections; pinned Matt Pocock/Vercel sources and hashed local versions; 13 skill validator passes; global reuse and ownership tests | Pass for packaging/format; reused user versions remain external |
| AC-22 | Native TOML discovered in real CLI requests; contract uses all ten OWASP categories, evidence and separate uncertainty, no model override or Engram; independent review followed the contract | Pass for configuration and this scoped review; native custom-agent delegation/model compliance not tested |
| AC-23 | 30 installer tests; genuine f57afa0 0.3.0-dev upgrade/reinstall/project+global rollback with reused skills; nine native loading scenarios | Pass on current Linux/CLI environment |

Executed checks:

- `python3 scripts/validate.py`: 5 roles, 13 skills, 5 profiles, 4 MCP candidates.
- `PYTHONPYCACHEPREFIX=/tmp/kewvy-stack-pycache python3 -m unittest discover -s tests -v`: 30 tests passed.
- Agent Skills quick_validate.py: all 13 source skills passed; the architecture
  skill passed again after the report scaffold correction.
- `python3 scripts/check_codex_loading.py`: core, nested override, NestJS, React,
  Next.js, Spring Boot, explicit grill-me, handoff and architecture loading passed
  using codex-cli 0.162.1 and a local Responses fixture, without credentials/model.
- Global skill fixtures live in a disposable repository ancestor, not in personal
  paths. Actual user-global implicit skill and project SDD discovery was additionally
  checked through offline `codex debug prompt-input` with a temporary Codex home.
  That command renders input, not full agent/tool metadata or explicit skill expansion;
  those checks use the live CLI fixture and installed-file equality instead.
- `git diff --check` and Bash syntax checking of the optional diagnosis helper passed.
  The helper was not run interactively.

The actual requested global install and `/home/kewvy/Dev/test-ai-stack` update
were applied and report 0.4.0-dev with zero pending content/state changes. Hash
comparisons confirmed preservation of the pre-existing ponytail/frontend-design
files, all three project registers, package/lock files, personal config.toml, existing
MCP profile and unmanaged instruction blocks. Meritum was not modified.

### Independent security review and correction

A separate read-only subagent reviewed the actual diff against f57afa0, including
untracked skills and the native agent contract. It found no confirmed critical/high
vulnerability. It flagged an uncertain high-impact concern in the retained upstream
HTML report scaffold: unpinned third-party CDN scripts and Mermaid loose security
could expose private report content if copied and executed. No exploit/browser
execution was demonstrated. The offered scaffold was replaced with static inline
CSS, restrictive CSP and explicit escaping rules, without external assets/scripts.
The reviewer re-read the correction and closed that concern at the instruction/
scaffold level. Static HTML parsing found no executable tags, event handlers, embeds
or external URL attributes. The two global reuse/copy tests passed again afterward.
The hardened content was applied to the managed global skill and matches its source.

This review followed the auditor contract through the available collaboration tool;
it is not evidence of the installed native role being selected and executing via
Codex's custom-agent runtime. No app-wide security audit, generated report behavior,
model adherence or browser execution was verified. The source checkout has no
.ai-stack task/finding registers; source decisions, roadmap and this verification
record retain the evidence and remaining limitations. No confirmed reusable
critical/high vulnerability required a local sec/<slug> finding.

### Failures corrected during development

The skill validator caught a YAML colon in diagnose's description; it was corrected.
The first global path under the Codex home was not the supported user-global layout;
it was replaced with ~/.agents/skills and safe isolated defaults. Native requests
also abbreviate skill paths through root aliases, so the fixture normalizes those
aliases before checking discovery. The interruption test was corrected to use its
explicit skills root. All corresponding final checks pass. A supplemental offline
probe incorrectly expected agent metadata/explicit expansion from prompt-input;
its claims were narrowed to the catalog it actually renders. No real model or
service authentication was needed for these checks.

Pending: behavioral evaluations on representative application changes, native
auditor delegation and permission enforcement tests, real MCP authentication,
framework/browser runtime validation, and publication license review for the
web-design-guidelines directory without a license declaration. These are separate
from the completed installation and discovery scope.

## Project exploration and test agents — 2026-10-19

Version 0.5.0-dev. The user requested codebase-explorer and test-engineer as
project-local subagents. Their contracts and native adapters were added without
changing the global native-agent selection, skills, model settings or permissions.

| Criterion | Executed evidence | Result |
| --- | --- | --- |
| AC-24 | All five profiles install both .codex/agents TOML files; installed launcher works after removing its source checkout; neither agent appears in the global native directory | Pass for packaging and scope |
| AC-25 | TOML parses with name/description/developer_instructions only; role contracts define no-edit mapping and scoped test writing with existing tools/TDD on request | Pass as configuration; behavioral compliance not evaluated |
| AC-26 | 32 installer tests; real 0.4.0-dev upgrade/rollback; ten native discovery/scope scenarios with Codex CLI 0.162.1 | Pass on current Linux environment |

Executed:

- `python3 scripts/validate.py`: 7 roles, 13 skills, 5 profiles, 4 MCP candidates.
- `PYTHONPYCACHEPREFIX=/tmp/kewvy-stack-pycache python3 -m unittest discover -s tests -v`: 32 tests passed. New checks cover project-agent ownership,
  installed-launcher independence, preserving client config/unrelated agents,
  unowned/edited matching definitions, rollback and .codex symlink parents.
- `python3 scripts/check_codex_loading.py`: all previous nine scenarios passed
  with both project-agent descriptions advertised, including nested discovery;
  the extra uninitialized sibling scenario contains neither project agent.
- A genuine e83ee9e 0.4.0-dev source/package initialized an existing Next.js
  fixture with user instructions, client config, an unrelated agent and edited
  records. Upgrade to 0.5.0-dev, identical reinstall and project/global rollback
  preserved the expected snapshots. No real project was rolled back.
- Native TOML parsing, Python AST parsing and `git diff --check` passed. No skill
  content changed, so this increment did not rerun unchanged skill validators.

The first native attempt did not advertise project agents in an untrusted
fixture. Trust was added only for its temporary repository, consistent with the
client's project configuration rules. A subsequent explicit-skill assertion could
select an ambient user-global duplicate instead of the temporary copy; those
ambient names are now disabled only in the fixture's temporary configuration.
The final saved fixture passes; real trust and skill settings are not changed.

Configured and verified in the user's requested setup: the global package and
`/home/kewvy/Dev/test-ai-stack` now report 0.5.0-dev with zero pending content/state
changes. The two actual project agent files equal their source adapters. Hash
comparisons preserved existing global agents/skills, project code/public assets,
package/lock files, all three user records, client configuration, trust settings
and unmanaged instruction content. Meritum was not modified.

The native fixture uses a local Responses stub, not a model or real service.
It verifies discovery and scope, not actual delegation, exploration accuracy,
test quality, red/green discipline or enforced read-only behavior. These remain
separate behavioral evaluations, not failed installation criteria. Both roles
inherit the parent session's actual model and permissions. No SDD activation,
new testing framework, dependency installation or remote operation was included.

## Scoped routing correction — 0.6.0-dev, 2026-10-19

Cause confirmed by read-only inspection: Meritum had no local stack installation,
but personal Codex instructions mandated auth/untrusted-input/pre-merge security
review globally. Six global leaf skills were implicitly discoverable, including
UI guidance. The recent Meritum chat also requested UI and then M01 client
integration; it ended at a usage limit. No per-cause token attribution is available.
Meritum's own implementation decision rules are intentionally unchanged.

Changes configured: project-local ODD/records, optional global catalog, three task
category entrypoints, nine specialized skills omitted from implicit discovery,
and explicitly requested custom-agent delegation/review. The nine leaf skills
remain accessible by direct invocation or by reading the relevant category link.
External skill bodies remain user-managed; invocation metadata has separate
stack ownership with normal conflict and rollback protection.

Executed and verified:

- Content/reference validation passed: 7 roles, 16 skills, 5 profiles, 4 MCP candidates.
- All 16 skill entrypoints passed the Agent Skills quick validator.
- All 33 installer tests passed, including partial ownership of external skill
  policy, unchanged original bodies, repeat-install/rollback and unowned-policy
  conflicts that block all writes.
- Codex CLI 0.162.1 with a local Responses fixture passed 15 positive discovery
  cases (six profile/override cases and nine explicit leaf requests) and one
  uninitialized-project negative case. Three categories are advertised; other
  leaf paths are absent unless explicitly requested. The uninitialized sibling
  has no project agents or project ODD instructions. MCP definitions still parse;
  connections/authentication were not exercised. Initial loopback startup was
  denied by the execution sandbox; the same isolated check passed with permission.
- A genuine be0223e 0.5.0-dev checkout upgraded to 0.6.0-dev in temporary roots.
  Repeat operations produced zero changes; project/global rollback restored
  snapshots, including external skill bodies and their former policy absence.
- Actual global installation and /home/kewvy/Dev/test-ai-stack were updated after
  dry-run and now report 0.6.0-dev with zero pending content/state changes.
  Hash/byte comparisons preserved personal Codex configuration, Meritum instructions
  and absence of local installation, both reused skill bodies and their original
  resources, test project application files and all three user-owned records.
- Python/TOML parsing and git diff --check passed.

No model behavioral evaluation, actual delegation, real login implementation,
security audit or measured token reduction ran. Native discovery confirms context
assembly, not semantic category choice or compliance. New sessions avoid retaining
old instruction history. No Meritum code, rules, model/effort, trust configuration,
MCP authentication, hooks, external services or remote repository state changed.

## Bash installer migration — 0.7.0-dev, 2026-10-26

User request: replace the Python installation runtime with Bash and select an
existing profile interactively. Bash + jq prerequisites were explicitly approved.
Implementation is `tools/stack.sh` with `tools/installer.jq`. The first iteration
retained the historical Python runtime as a migration fixture; the follow-up below
removes that implementation at the user's request.

Executed on Linux with Bash 5.3.20, jq 1.8.2 and Codex CLI 0.162.1:

- `python3 scripts/validate.py`: 7 roles, 16 skills, 5 profiles and 4 MCP candidates.
- `bash -n tools/stack.sh` and `git diff --check`: passed. ShellCheck was not
  available; no ShellCheck result is claimed.
- The 38-test installer suite passed. Three subsequently added focused cases
  also passed, for 41 distinct installer tests: no-Python execution, interrupted
  first profile initialization and malformed manifest lists. The expanded menu
  cancellation/EOF/preview case was rerun and passed after the final changes.
- PTY checks cover global and project selection, invalid input, cancellation,
  end of input and preview without modifying installation destinations.
- A real installation created by the 0.6 Python fixture updated to Bash and
  restored its previous package, state and launcher on rollback. Project profile,
  user records, external skill bodies and instructions retained their protections.
- A restricted PATH containing Bash, jq and required utilities, with no Python,
  installed the global snapshot and initialized Next.js through its installed
  launcher after deleting the source checkout. Paths with spaces, quotes and
  literal shell metacharacters worked without evaluation.
- Faulted atomic renames verified ordinary write recovery. Interrupted global
  updates and a first NestJS initialization recovered through backup-based rollback.
- `python3 scripts/check_codex_loading.py`: passed 15 positive instruction/skill/
  agent discovery cases and one uninitialized-project negative case. Codex also
  recognized the MCP definitions. The sandbox initially blocked the local listener;
  the same isolated fixture passed with permission to bind localhost.

The minimum Bash/jq versions, other operating systems, model behavior, actual
delegation and authenticated MCP connections remain unverified. Maven observations
are literal version hints, not XML validation or dependency resolution. Bash uses
atomic rename without an explicit filesystem sync; power-loss durability is not
guaranteed. All installations were disposable fixtures; personal configuration,
existing projects and remote repository state were not updated.

### Terminal refinement and installer cleanup — 2026-10-26

The user requested a polished terminal interface and removal of unnecessary
Python installers. The menu now has a compact brand header, readable action and
profile choices, concise descriptions, a destination/change review, a completion
state and optional full file details through --verbose. It wraps to terminal
width, uses ASCII marks and preserves scrollback. Color requires terminal output
and respects NO_COLOR and TERM=dumb.

Removed the executable legacy Python installer fixture and obsolete stack bytecode.
No Python installer source remains. Static schema1-migration.json data replaces
the fixture; the current migration test constructs schema-1 ownership with opaque
retired-runtime bytes. This verifies update/rollback contracts, not execution of
the former Python implementation. The earlier genuine-runtime result above is
historical evidence from before this cleanup.

Current focused validation passed seven distinct test cases: menu installation,
cancellation/EOF/preview/verbose output, terminal color fallback, 32-column profile
layout, schema-1 migration and rollback, a restricted PATH without Python, and
global reinstall through the installed launcher. The terminal was also inspected
interactively. Content validation, Bash syntax and git diff --check passed. The
full installer suite and native Codex discovery were not repeated for this
presentation-only refinement; their earlier results are recorded above.

### Current-directory confirmation — 2026-10-26

The project menu now displays and confirms the caller's working directory before
profile selection, replacing manual path input. Declining, an empty answer or EOF
before confirmation leaves installation destinations unchanged. The existing
explicit init TARGET command remains available for automation.

Five focused test cases passed: global/project menu installation, menu preview and
cancellation, unconfirmed-directory preservation, terminal color fallback and
narrow-terminal layout. The installation case was rerun through the installed
launcher from a project directory containing spaces, with source and package
directories elsewhere; state recorded only that working directory as the project
root. Content validation, Bash syntax and git diff --check also passed. These were
temporary fixtures; no personal installation or existing project was updated.

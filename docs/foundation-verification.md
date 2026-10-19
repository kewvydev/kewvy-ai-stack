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

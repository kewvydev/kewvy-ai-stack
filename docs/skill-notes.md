# Selected global skills and security review

User-approved expansion: 2026-10-19. Source discovery used skills.sh; source code
came from the authors' repositories, pinned in `skills/provenance.json`. Ponytail
and frontend-design preserve the user's local snapshots and their lockfile hashes;
these hashes are not claimed as upstream commit IDs. No collection installer runs
in the user's environment. Selected directories and their needed references only.

| Skill | Source | Availability and boundary |
| --- | --- | --- |
| ponytail | dietrichgebert/ponytail, existing local version | Global; smallest complete code change, not permission to skip requested work |
| grill-me | mattpocock/skills | Global, explicit-only upstream policy retained; bundled grilling method, no missing skill call |
| tdd | mattpocock/skills | Global; apply test-first work at agreed interfaces when selected |
| diagnose | mattpocock/skills | Global compatibility name for renamed diagnosing-bugs; reuse project workflow rather than running both |
| improve-codebase-architecture | mattpocock/skills | Global, explicit-only; propose candidates before refactoring or external issue creation |
| handoff | mattpocock/skills | Global, explicit-only; temporary redacted document, no automatic sending or new chat |
| web-design-guidelines | vercel-labs/agent-skills | Global; current guideline retrieval required for a current compliance claim |
| frontend-design | anthropics/skills, existing local version | Global; existing user instructions and product scope take precedence |
| vercel-composition-patterns | vercel-labs/agent-skills | Global; relevant to React, with actual-version checks before React 19 rules |
| sdd-workflow | Original stack content | Every project profile; activation still needs approval for the change |

Global does not mean every workflow runs on each task. Three small category
entrypoints select task-specific guidance (see skills/catalog.json). The nine
specialized skills are excluded from implicit discovery; the category reads one
needed skill, or the user names it explicitly. Original request gates remain.
Global UI
skills do not change technology profile inheritance or install frontend packages
into backend projects. No universal TDD or SDD mandate is introduced.

## Reusing existing global skills

`--skills-dir` selects a destination and existing-skill lookup, default `~/.agents/skills`. When a
selected name exists there before this stack owns a copy, preserve it and record
its entrypoint path/SHA-256 in global state under `selection.externalSkills`.
The snapshot remains in the package for use on a machine without that skill.
Do not claim that a reused definition matches the snapshot or passes the stack's
format validation. Updates remain the existing manager's responsibility.

The installed package writes other global skills under `~/.agents/skills` by default.
If an unowned definition already exists at that destination, installation refuses
the conflict. Rollback preserves externally managed bodies. The stack owns only the added
invocation policy on reused skills; an existing unowned policy blocks installation.
A later change to the lookup directory does not relinquish previously owned files.

## Security auditor adaptation

The reusable contract is [agents/security-auditor.md](../agents/security-auditor.md);
the native Codex mapping is [security-auditor.toml](../adapters/codex/agents/security-auditor.toml).
The agent reports and returns proposed local record updates. It does not edit
code or write findings itself, resolving the supplied contract's read-only versus
memory-write conflict. Engram is neither needed nor configured. No Opus model or
reasoning override is set; Codex inherits the parent's choices.

The checklist names all ten [OWASP Top 10:2025](https://top10.owasp.org/2025/)
categories. Each gets reviewed evidence, a justified exclusion, or an explicit
unverified status. Confirmed critical/high findings need file:line, attacker
control, prerequisites, missing control, an exploitation path and impact. Uncertain
high-impact concerns are reported separately; an empty report is not a security
certification. No active exploitation or live scanning is authorized by this role.

[Official Codex agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
states custom agents inherit parent permissions and MCP servers. Do not translate
Claude's disallowedTools or sandbox_mode into a false enforcement claim. For a
filesystem read-only CLI session use `codex --sandbox read-only` before asking it
to use security-auditor; connector permissions remain separate. Version 0.6 removes
the global auth/untrusted-input/pre-merge routing mandate. All custom roles require
explicitly requested delegation or review; the main agent still checks relevant
validation and security during normal implementation. No pre-merge hook, automatic
merge or deployment is installed.

## Provenance and publication limits

MIT declarations/licenses and the frontend-design Apache-2.0 license are retained
where available. web-design-guidelines has no license declaration in the selected
upstream directory; this is recorded rather than guessed. Review redistribution
terms before publishing this personal stack. Format and discovery tests do not
prove upstream instruction quality, model compliance or application security.

## Architecture report hardening

Independent read-only review identified an uncertain high-impact concern in the
retained upstream HTML report scaffold: third-party CDN scripts and Mermaid's
loose security mode could expose private report content if copied and executed.
No generated exploit or browser execution was demonstrated. The offered scaffold
now uses static inline CSS, no external assets/scripts, a restrictive CSP and
explicit HTML escaping of repository-derived text. The original entrypoint is
retained for provenance, not as authority to execute its old report recipe.
This change reduces the template's execution surface; it is not a behavioral
proof that a model will always produce safe HTML.

## Project-local exploration and test roles (0.5.0-dev)

`codebase-explorer` and `test-engineer` are native project agents under
`.codex/agents/`, not additional global skills or global native agents. All profiles
install both adapter definitions from the package snapshot. Explorer maps existing
modules/dependencies/conventions and reports file references without edits.
Test engineer designs/writes assigned behavior/contract/regression tests with the
configured tools, following TDD when requested. They inherit model and permissions;
availability does not require delegation or change the SDD approval policy.

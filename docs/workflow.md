# Everyday workflow and optional SDD

Decisions confirmed on 2026-10-19. First target client: Codex.
This document defines behavior. The Codex core installer distributes this guidance;
it does not technically enforce approval or prove model compliance.

## Everyday work: lightweight ODD

Understand the request, explore the necessary context, resolve material questions,
implement the authorized change, and verify its result. Keep work proportional
and communicate evidence and pending checks.

Expected behavior can be clear from the conversation and diff.
Do not require a spec, a separate plan, a set of templates, or multiple agents for
every adjustment. When work needs continuity, reuse the project's record with the
minimum information needed to resume.

Project initialization seeds `.ai-stack/decisions.md` when absent. Link an existing
register rather than duplicating it. Record only confirmed decisions with source,
scope, and corrections. The CLI preserves this user-owned file through updates
and manual rollback; it does not extract conversation memory or store application data.

## When to propose SDD

Suggested considerations: unclear behavior, decisions affecting several parts,
risk that calls for explicit criteria, or a need to retain a verifiable agreement
across sessions. Do not decide by file count.

The agent explains why SDD would help and what definition or evidence it would
add to the change. **Wait for explicit user approval before activating SDD.**
Approval applies to that change; it does not make SDD the default for other
changes. If approval already exists in the conversation for that scope, do not
ask again.

While waiting, explore and complete independent, authorized work.
Do not create the set of SDD artifacts or implement unresolved decisions.
If the user declines SDD, continue in lightweight mode only where requirements
are clear; keep blocking questions explicit.

The shared profile installs `sdd-workflow` and its templates so every technology
profile can discover it. Installation is availability, not approval to activate SDD.

## After SDD is approved

Use the `sdd-workflow` skill: define behavior and acceptance criteria, plan what is
needed, implement, verify, and synchronize the spec. Adapt artifacts to the change;
reuse existing specs and any SDD engine the project already uses. Approval to use
SDD does not automatically approve unresolved product decisions or external actions.

When finished, report the outcome and retain useful evidence. The next change
starts in lightweight mode unless explicit authorization defines another scope.
The SDD engine and approvals within its stages are still undecided.

## Incomplete work and reusable findings

On resume, read relevant existing task/finding records or their links from
.ai-stack/tasks.md and .ai-stack/findings.md. Retain unfinished acceptance criteria,
completed evidence, blockers and the next action. Do not report 100 percent merely
because files were created or checks ran. Verify old findings before reusing them,
mark hypotheses, preserve corrections, and retire stale entries. A recorded
suggestion does not authorize changes to another module. No external capture
service is required or installed for this workflow.

## Optional project roles

Every profile makes codebase-explorer and test-engineer available under the
project's `.codex/agents/`. Explorer returns a brief source map without edits;
test engineer writes assigned behavior/contract/regression tests using existing
project tools. Use TDD when requested, retaining prior agreement on criteria.
Neither role is a mandatory stage or authorization for additional delegation.
Use them on request or under applicable delegation instructions; keep everyday
work proportional. The global verifier/security-auditor retain their existing roles.

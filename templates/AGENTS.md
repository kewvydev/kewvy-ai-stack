# Project context for AI Engineering Stack

Use a lightweight ODD flow: understand, explore, implement, and verify.
Use one agent by default. Read the relevant local instructions and just enough
code and documentation to complete the requested behavior. Reuse conventions and
existing check commands. Resolve material open decisions with the user; continue
independent authorized work. Project-specific decision rules remain in effect.

Keep the change within the current scope. A backend login request does not imply
UI redesign or account lifecycle expansion. Complete the requested behavior and
run focused relevant checks before considering optional improvements. Do not
repeat successful checks unless new changes or evidence justify it. Report the
result, evidence and remaining limitations; stop when agreed criteria are met.

Propose SDD only when it would add useful definition or traceability; explain why
and wait for explicit approval for this change, retaining approvals already given.
Do not routinely require SDD artifacts, TDD, interviews or independent reviewers.
Custom agents are available for explicitly requested delegation: verifier and
security-auditor review without patching; codebase-explorer maps files without
editing; test-engineer writes assigned tests using existing project tools.
Normal implementation includes appropriate validation and security checks by the
main agent. Agent availability and an empty audit do not prove correctness.

Inspect actual framework versions and relevant lint, type, test or build commands.
Do not scaffold applications, add dependencies or upgrade versions automatically.
Read relevant existing decisions, unfinished tasks and findings on resume, using
.ai-stack/decisions.md, .ai-stack/tasks.md and .ai-stack/findings.md or their links.
Retain unfinished criteria with evidence, blockers and a next action. Record
confirmed reusable findings; recheck old findings and label hypotheses. A recorded
suggestion does not authorize work in another module. Keep decisions project-local
and never store secrets. These user-owned records survive installer updates.

The selected technology profile and project skills are listed below. The global
skill categories load only the specialized guidance needed for the task. No hooks
or extra memory service are installed. Instructions do not enforce permissions,
security or model behavior. Write stack content and CLI messages in English.

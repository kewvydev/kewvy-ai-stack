# Project context for AI Engineering Stack

Read the project's README, local instructions, and relevant existing documentation.
Read `.ai-stack/decisions.md` for confirmed decisions or its link to the project's
existing decision register. Project-specific instructions take precedence over
the stack's global working agreements within the client's instruction hierarchy.

Inspect installed framework versions and existing lint, type, test, and build
commands before making changes. Do not assume commands or scaffold an application.
Record new confirmed decisions in the project's existing register, or in
`.ai-stack/decisions.md` when no register exists. Retain their source, scope,
and corrections. Do not mix information from other projects or store secrets.

Read `.ai-stack/tasks.md` and `.ai-stack/findings.md` for incomplete work and
reusable project findings, or follow their links to existing records. Update
those user-owned records when a task remains incomplete or a durable finding
will help another module. Do not turn suggestions into authorized tasks.

The selected technology profile and skills are listed below. Global guidance
provides the shared workflow; the verifier checks criteria and security-auditor reviews security-sensitive changes.
The global installation makes the selected shared skills available across projects.
Project agents live in `.codex/agents/`: `codebase-explorer` returns a brief map
without edits; `test-engineer` writes assigned behavior, contract and regression
tests with the project's existing tools, using TDD when requested. Use these roles
on request or when applicable instructions authorize delegation; availability does
not require multiagent work for every change.
Use SDD only after approval for the current change.
No hooks or additional memory service are installed.

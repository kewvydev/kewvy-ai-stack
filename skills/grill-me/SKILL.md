---
name: grill-me
description: Interview the user to sharpen a plan or design, expose dependent decisions, and reach a shared understanding.
license: MIT
---

# Grill Me

Use the bundled [interview method](references/grilling.md). The upstream name is
an alias for `grilling`; this package includes that method rather than requiring
another installed skill or a client-specific Skill tool.

Read project facts yourself. Ask the user about decisions, not facts you can
inspect. Group independent questions in manageable rounds, explain a recommended
answer, and wait before dependent work. Retain approvals already given. Research
facts directly; use subagents only when the user or applicable instructions
actually authorize delegation. Do not require a subagent for an interview.

Finish with confirmed decisions and remaining questions in the project's existing
register or `.ai-stack/decisions.md`. An interview does not authorize implementing
its unresolved design or activating SDD.

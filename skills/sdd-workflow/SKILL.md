---
name: sdd-workflow
description: Guide a change through specs, plans, and evidence when the user has approved SDD for that scope; everyday work follows a lightweight flow and does not activate this process on its own.
---

# SDD per change

First verify that the user has approved SDD for this change. Perceived complexity
or loading this skill does not constitute approval. If approval is missing,
explain what SDD would add and wait for an answer before creating its artifacts
or starting its stages. Continue only independent, authorized work.
If approval already exists for the current scope, retain it without asking again.

Read the project's instructions, spec organization, and approval policy first.
Respect an existing SDD engine; do not introduce a second record.
If the user is still choosing the approach, present alternatives and advance
only work that does not depend on that choice.

For the approved change, identify expected behavior, constraints, observable
criteria, and open questions before implementation. Reuse an existing spec if
it covers the same change. For a project without a convention, suggest
`specs/features/<slug>/` with these artifacts:

- [Spec](assets/spec.md): problem, scope, and acceptance criteria.
- [Plan](assets/plan.md): design, contracts, impact, and verification approach.
- [Tasks](assets/tasks.md): reviewable work units linked to criteria.
- [Verification](assets/verification.md): evidence and pending checks per criterion.

Templates are aids, not mandatory forms. Reduce artifacts for small changes
when project policy allows it. Use ADRs for lasting architectural decisions;
avoid recording routine details.

Separate questions that block behavior from technical details that can be
resolved within scope. Ask only what is necessary; keep pending decisions
explicit and continue independent tasks. When approval is required, check
whether it already exists in the conversation before asking or proceeding
with dependent work.

Implement against the criteria and plan, updating them when scope changes are
resolved. Choose tests based on behavior and risk using the project's tools.
Record commands, results, and limitations without equating a static check with
a functional test. Keep criteria pending when evidence is insufficient.
Close the change with a synchronized spec and traceable evidence.

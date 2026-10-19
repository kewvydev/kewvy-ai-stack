---
name: vercel-composition-patterns
description: Design and review React component composition, compound components and context interfaces using the installed React version.
license: MIT
---

# React Composition Patterns

Inspect the installed React version and existing component conventions first.
Avoid accumulating boolean mode props; consider composition, explicit variants
and compound components when they simplify the actual callers. Lift state only
as far as needed and keep provider implementation details behind a small interface.
Preserve accessibility, error handling and current behavior when refactoring.

Read only the relevant files under `rules/`: `architecture-` for composition,
`state-` for ownership and context, `patterns-` for variants and children, and
`react19-` for version-specific APIs. React 19 rules do not authorize upgrading React
or applying those APIs to an older project. Check version-matched official docs
when an API is uncertain. Prefer a narrow change justified by the requested behavior.
The original guide is retained in [references/upstream.md](references/upstream.md).

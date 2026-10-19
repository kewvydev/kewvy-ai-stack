---
name: vercel-react-best-practices
description: Review and improve React or Next.js rendering, data fetching, and bundle performance when relevant to the requested change.
license: MIT
---

# vercel-react-best-practices

Inspect React and, when applicable, Next.js versions before applying guidance.
Use [upstream guidance](references/upstream.md) to locate relevant `rules/` entries;
read those entries rather than the complete collection. Next.js server, routing,
and caching advice applies only to matching Next.js projects, not standalone React.
Preserve the project's router, state library, and toolchain. Do not install packages
suggested by examples automatically. Measure a performance issue before adding
memoization, caching, or changing application behavior.

---
name: improve-codebase-architecture
description: Explore architectural friction and present module-deepening candidates for user selection before refactoring.
license: MIT
---

# Improve Codebase Architecture

Scope the review to the user's area or recent change history. Read existing domain
terms, ADRs and local findings. Use the [design vocabulary](references/design/vocabulary.md)
and apply the deletion test: would removing a wrapper eliminate complexity or
merely move it? Look for shallow modules, scattered knowledge, coupled interfaces,
and behavior that is hard to test through its public interface.

Explore directly. Delegate exploration only when authorized and useful; no agent
is required by this skill. Present concrete candidates with files, observed friction,
proposed change, benefits, costs, before/after relationships and recommendation
strength. Flag conflicts with existing decisions instead of silently reopening them.

For several candidates, create a temporary HTML report if it helps comparison.
Use the adapted [static scaffold](references/HTML-REPORT.md), with inline CSS/SVG
and no scripts or external assets. HTML-escape repository-derived labels and
excerpts as text; do not copy executable blocks from the upstream reference. Use the client's
file preview rather than assuming platform-specific shell openers are available.

Ask which candidate to explore. Use `$grill-me` for the selected design when useful;
retain existing approvals and do not start a refactor or create a remote issue just
because a candidate was reported. Record confirmed terms and lasting decisions in
the existing project registers; preserve pending work in `.ai-stack/tasks.md`.
The [original process](references/upstream.md) is reference material; its extra
skill calls and parallel-agent patterns are not automatic dependencies.

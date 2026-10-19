---
name: handoff
description: Prepare a concise, redacted handoff for a fresh session using existing artifacts and unfinished criteria.
license: MIT
---

# Handoff

Summarize the current authorized scope, confirmed decisions, relevant paths,
completed evidence, unfinished criteria, blockers and next action. Read existing
project tasks and findings. Link specs, diffs, commits, ADRs and issue records rather
than duplicating them. Keep durable unfinished work in the project's own register;
a temporary handoff is not its replacement.

Write the handoff in the OS temporary directory with a unique filename and return
its absolute path. Follow the user's requested next-session focus. Suggest relevant
available skills using Codex's `$skill-name` notation. Do not require a Skill tool,
a second agent or a new chat. Creating this document does not authorize sending it.
Redact secrets, tokens, personal data and exploit payloads.

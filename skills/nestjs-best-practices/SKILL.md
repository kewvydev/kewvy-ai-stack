---
name: nestjs-best-practices
description: Develop and review NestJS modules, dependency injection, API boundaries, and authorization using the project version and conventions.
license: MIT
---

# nestjs-best-practices

Inspect the project's NestJS version and existing conventions first. Use the
relevant rules from [upstream guidance](references/upstream.md) and `rules/`.
Treat its architecture patterns as options: do not introduce repositories,
events, queues, caching, an ORM, or dependencies solely because a rule suggests them.
Use the project's validation and authentication mechanisms. Verify authorization,
ownership, rejected inputs, and API behavior through existing test commands.
Examples from another NestJS version need verification against official docs.

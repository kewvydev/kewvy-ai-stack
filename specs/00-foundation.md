# Stack foundation

Status: content foundation, Codex installer, approved skills/profiles, verifier,
project records, global skills and security-auditor implemented through 0.4.0-dev.
Runtime evidence and limits are recorded in `docs/foundation-verification.md`.

## Problem

Manually setting up instructions, agents, skills, and tools for each project
repeats work and can produce inconsistent configurations.

## User-confirmed requirements

- RQ-01: a standalone project in `~/Dev/`, outside Meritum.
- RQ-02: easy stack installation when starting a project.
- RQ-03: a lightweight everyday workflow inspired by ODD, with optional SDD when needed.
- RQ-04: a package of custom agents.
- RQ-05: extensible skills for development, testing, CI/CD, and architecture.
- RQ-06: useful tooling and MCP integrations.
- RQ-07: gradual, lightweight implementation using gentle-ai as a reference.
- RQ-08: ask about decisions and present recommendations before expanding scope.
- RQ-09: test with Codex first; decide other assistants later.
- RQ-10: the agent proposes SDD and asks the user before activating it for a change.
- RQ-11: all stack content must be in English.
- RQ-12: a global installation complemented by initialization of existing projects.
- RQ-13: start with a Python CLI; keep installation state and project decisions.
- RQ-14: enable no MCP integrations in the first increment.
- RQ-15: keep separate future profiles for NestJS, React, Next.js, and Spring Boot,
  sharing React capabilities with Next.js. Framework versions remain project-specific.

## Deliverables for this stage

- AC-01: original files in `~/Dev/ai-engineering-stack`.
- AC-02: project, spec, plan, task, verification, and ADR templates.
- AC-03: an initial SDD skill and role contracts with defined scope.
- AC-04: recommendations distinguished from confirmed choices.
- AC-05: integrity validation for the index, profiles, and MCP catalog.
- AC-06: ODD is the everyday flow in instructions, templates, and the manifest.
- AC-07: SDD activation requires explicit approval. The 0.4.0-dev user request
  supersedes the original packaging exclusion: `core` now distributes the skill.
- AC-08: Codex is the first target client without claiming compatibility before testing.
- AC-09: documentation, instructions, skills, templates and their placeholders,
  configuration descriptions, code comments, and tool messages are in English.

## First installer increment

Scope approved on 2026-10-19. Python standard library, Codex core only.

- Global core snapshot and launcher; project initialization uses an existing directory.
- A `dry-run` that writes nothing and shows destinations and conflicts.
- No changes on reinstallation when content already matches.
- Detection of existing files and user modifications; no silent overwrites.
- Managed file state with versions and hashes, plus installation change recovery.
- One-operation rollback, including interrupted updates; preserve project decisions.
- Configure selected modules only; never copy credentials into the repository.
- Report generated content, client detection, and verified MCP connections separately.
- Test with new and existing temporary projects before using real projects.

Acceptance criteria for this increment:

- AC-10: a global snapshot and executable launcher can initialize the core in an
  existing temporary project without scaffolding an application.
- AC-11: JSON installation state records version, scope, selection, roots, and
  hashes; a project decision register is created only if absent and never updated.
- AC-12: preview, repeated installation, conflicts, unsafe paths, overrides,
  symlinks, and preservation of user content are covered by executed tests.
- AC-13: a synthetic update between two versions can be rolled back; ordinary
  write failure and process interruption have recovery tests.
- AC-14: the installed Codex CLI assembles global, project, and nested override
  instructions in a local fixture test; model behavior is a separate check.

Implementation contract and commands: `docs/installation.md`.

## Outside this increment

A custom model execution engine, a published installer, a multiagent runtime,
universal assistant support, native custom agents, technology profiles, hooks,
external memory, application data storage, real connections, deployments, and
general uninstallation. Do not install into personal configuration or Meritum
as part of implementation tests.

## Open questions

See `docs/decisions.md`. Draft roles and the skill do not by themselves settle the
SDD engine, approvals, autonomy, or client compatibility.

## Approved 0.3.0-dev expansion

This supersedes the initial increment exclusions only for the selections recorded
in docs/decisions.md. It does not activate SDD or additional memory services.

- AC-15: four separate technology profiles configure existing projects; Next.js
  reuses React; Java/Maven and actual declared versions guide Spring Boot context.
- AC-16: only the three approved, pinned skill directories are distributed with
  provenance, format validation, native discovery and conflict preservation.
- AC-17: project tasks retain unfinished criteria, evidence and next actions;
  findings retain reusable evidence, affected modules and correction/retirement
  status. Records are user-owned and survive updates/rollback.
- AC-18: a native verifier and isolated Context7/GitHub configuration profile are
  recognized by Codex; authentication and actual model delegation remain separate.
- AC-19: a genuine 0.2.0-dev installation can update and roll back in temporary
  locations. Hooks and all unselected integrations remain uninstalled.

## Approved 0.4.0-dev expansion

- AC-20: every project profile distributes sdd-workflow and its four templates;
  SDD still needs approval per change and does not scaffold specs at install time.
- AC-21: nine requested skills are available through global installation with
  pinned upstream or hashed local provenance and necessary references. Reuse
  existing user-global names without overwriting, duplication or ownership.
- AC-22: the native security-auditor inherits the Codex model, reports without
  patching or memory writes, checks all OWASP categories and distinguishes confirmed
  critical/high findings from uncertain concerns. The parent maintains local records.
- AC-23: checks cover global reuse, preservation, conflicts, profile separation,
  update/rollback and native discovery. Report model behavior and real audits
  separately; neither is certified by loading configuration.

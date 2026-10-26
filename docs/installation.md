# Codex core installation

Python 3.9+ standard library only. Linux is the tested platform. Distribution is
a snapshot from a trusted checkout, with no automatic download or scaffolding.

## Preview and install

From the stack checkout:

```bash
python3 tools/stack.py install --dry-run
python3 tools/stack.py install
```

| Default destination | Content |
| --- | --- |
| `~/.local/share/ai-engineering-stack/` | Minimal core snapshot, installation state, latest backup |
| `~/.local/bin/ai-stack` | Launcher requiring `python3` on PATH |
| `$CODEX_HOME/AGENTS.md`, normally `~/.codex/AGENTS.md` | Managed block of optional catalog guidance |

The CLI does not modify PATH; use the launcher's absolute path if necessary.
The optional catalog is visible across Codex projects. ODD and records apply only
to initialized projects; their own decision rules remain intact.
Restart existing sessions to discover new instructions.

Use `--prefix`, `--bin-dir`, and `--codex-home` for other destinations. They must
be separate directories; repeat the same destinations for later operations.
`--codex-home` selects the write destination. Launch Codex with the corresponding
`CODEX_HOME` when using a non-default home. No credentials are moved or copied.

## Initialize an existing project

After global installation:

```bash
ai-stack init /absolute/path/to/existing-project --dry-run
ai-stack init /absolute/path/to/existing-project
ai-stack status /absolute/path/to/existing-project
ai-stack status --global
```

Profiles: `core`, `nestjs`, `react`, `nextjs`, and `spring-boot`. Use `init TARGET
--profile NAME`; later calls reuse the recorded profile. Each profile includes `sdd-workflow` with its four templates; SDD still requires
approval per change. Profiles add their
skills under `.agents/skills/` and managed context in `AGENTS.md`. Next.js inherits
React without a duplicate copy. Global installation also writes the native verifier
and `stack-development.config.toml` under the selected Codex home.

Decisions, tasks, and findings under `.ai-stack/` are seeded only when absent,
user-owned, and preserved by updates and rollback. No extra memory service, hooks,
framework dependencies or application database is configured. Other existing
client configuration is preserved.

The target must be an existing directory outside the stack source. Symlinks and
symlink parents are rejected, including broken links. Non-empty global or root
project `AGENTS.override.md` files cause conflicts because they would hide installed
guidance. Nested overrides remain available for local conventions.

## Optional Obsidian connection (0.7.0-dev)

Update the global package and rerun `init` for each selected project before
connecting it. Use `ai-stack memory init TARGET --vault /absolute/vault --project
unique-slug --dry-run`, then repeat without `--dry-run`. The vault must already
exist and remain separate from project directories. No global default is set.

The machine-local `.ai-stack/memory.json` binding and `Projects/<slug>/` vault
notes are user-owned and survive installation updates/rollback. Preview writes
nothing; repeat connection preserves notes and restores missing seeds. The CLI
does not migrate existing records or populate project knowledge automatically.
Start a fresh Codex chat for the updated startup instructions. See the
[memory guide](memory.md) for context/search, permissions, recovery and sources.

## Ownership and updates

Instruction blocks use `BEGIN:ai-engineering-stack` and `END:ai-engineering-stack`
HTML comments. State schema 1 records scope, absolute roots, version, `codex` /
`core` selection, and SHA-256 for each managed file or instruction block. It does
not record credentials, conversations, application data, or inferred decisions.

- Personal instructions outside managed blocks remain editable and are preserved.
- Existing unmanaged files and blocks are not adopted or overwritten.
- Editing or removing managed content causes a conflict. Put local instructions
  outside the block; resolve a managed conflict explicitly before updating.
- Malformed markers, state, unknown paths, and mismatched destinations are conflicts.
- Preview and status validate the plan without writing anything.
- Identical reinstallations do not rewrite content, state, or backups.

To update, run `install --dry-run`, then `install` from the trusted checkout of
the desired version, using the original destinations. Rerun `ai-stack init` in
each selected project afterward. Projects are not discovered or updated automatically.
The first updater supports the same core file set across releases; removing old
managed paths requires a future explicit migration and currently causes a conflict.

## Project decisions

The decision record is user-owned; the installer never updates its contents.
If a project already has a register, link it from `.ai-stack/decisions.md` and
retain that register as the source of truth. Record confirmed decisions with date,
source, scope, and status. Mark corrections and superseded entries explicitly.
Instructions guide this behavior; the CLI does not extract or approve decisions.

Instructions and decisions can be versioned with the project. State and backups
contain machine-local paths and prior file contents; normally exclude
`.ai-stack/installation.json` and `.ai-stack/backup.json` through your existing
ignore policy. The installer does not edit `.gitignore` or Git configuration.

## Recovery

Before a changing operation, one `backup.json` is atomically written alongside
the installation state. It records previous/next state and old/new managed bytes,
replacing the previous recovery point. This is not general project history.

```bash
ai-stack rollback /absolute/path/to/existing-project --dry-run
ai-stack rollback /absolute/path/to/existing-project
ai-stack rollback --global --dry-run
ai-stack rollback --global
```

Repeat custom global destinations. Rolling back the first global install removes
its launcher; invoke the checkout CLI if needed. Successful rollback consumes the
backup. Empty directories may remain. Decision records survive manual rollback,
including rollback of the first project initialization.

An ordinary write exception attempts to restore files and state. Following process
interruption, run rollback with the original paths before retrying installation.
Rollback accepts files at either side of that transaction and refuses conflicting
edits. Changes outside instruction blocks survive. If storage remains unwritable,
recovery may also fail; preserve the backup for inspection. Atomic file replacement
does not guarantee multi-file recovery from power loss.

Run one installer at a time; cross-process locking and general uninstallation are deferred.

## Codex precedence

Codex discovers global guidance under `CODEX_HOME`, then project guidance from
the repository root to the current directory. At each level, `AGENTS.override.md`
precedes `AGENTS.md`; closer instructions take precedence. The default combined
limit is 32 KiB. This adapter does not use Claude imports or change discovery rules.

Configuration is separate: CLI overrides, trusted project configuration, selected
profile, user configuration, managed/system defaults, and built-in defaults have
their documented order, subject to mandatory requirements. This installer does not
edit `config.toml`, trust settings, permissions, or models.

Sources checked on 2026-10-19:
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[configuration](https://learn.chatgpt.com/docs/config-file/config-basic).

## Reproduce checks

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/check_codex_loading.py
```

Tests use disposable projects, source releases, and Codex homes. The loading check
additionally requires Codex CLI, Git, and permission to bind a temporary loopback
port. It runs the real CLI with an isolated Codex home and a local Responses fixture,
without credentials or a real model. It checks global/project order and nested
override discovery. It does not test model compliance, SDD approval behavior,
native agents, desktop UI, or external connections. See the verification record.

## Profiles, selected skills, and MCP definitions (0.3.0-dev)

```bash
ai-stack init /absolute/backend --profile nestjs --dry-run
ai-stack init /absolute/frontend --profile react --dry-run
ai-stack init /absolute/next-app --profile nextjs --dry-run
ai-stack init /absolute/java-app --profile spring-boot --dry-run
codex --profile stack-development mcp list
codex --profile stack-development
```

The first four commands are separate initialization paths for existing projects,
not application generators. Remove --dry-run after reviewing destinations.
Core can be promoted to a technology profile and rolled back. A non-core profile
cannot replace another initialized technology profile in place; rollback first. There is no silent removal of previously selected skills.
Skill files have the same hash/conflict protections as other managed files.
Do not also install the same skills globally through another manager: Codex does
not merge duplicate skill names. Source revisions are in skills/provenance.json.

The global package is a reusable library; technology skills become native only
in selected project profiles. Diagnosis is shared by all profiles. The verifier
is native global content, invoked on demand without automatic multiagent routing.

The MCP profile references CONTEXT7_API_KEY and GITHUB_MCP_TOKEN environment
variables; supply them only through your local credential/environment mechanism.
Use the minimum repository permissions required for the task. The installer never
copies keys, performs OAuth, or probes remote servers. Missing credentials prevent
startup of the relevant connection. Configuration recognition is not authentication.
The profile layers with existing user/project config according to Codex precedence;
it does not replace your Supabase connection or other servers.

A 0.2.0-dev core can be updated using install, then init for each project. This
adds approved files while preserving existing hashes and user-owned records.
Task completion and finding corrections are behavior guided by global/project
instructions, not inferred or technically enforced by the CLI. See the research
and verification records for exact scope.

## Workflow and global skills (0.4.0-dev)

`install` adds the nine approved global skills under `~/.agents/skills` by default, plus security-auditor under `agents/`. Before owning a global
skill, it checks the destination selected by `--skills-dir` (default `~/.agents/skills`) and reuses a matching
existing skill without overwriting it. The state records its path and entrypoint
hash as an external dependency. Reused versions stay managed by their original
installer; stack updates/rollback do not modify their bodies. See the 0.6 policy
exception below. The package keeps snapshots
for machines without those skills. Repeat custom lookup paths for later operations.

`init` includes sdd-workflow and four templates in every profile. The shared global
skills are inherited rather than copied into each project. Merely installing the
skill does not activate SDD; approval still applies per change. Update the global
package with `install --dry-run` then `install`; update each selected existing
project with `init TARGET --dry-run` then `init TARGET`.

Fish setup uses `set STACK_SOURCE "/absolute/path/to/stack"` and
`set NEXT_PROJECT "/absolute/path/to/project"`. Then:

```fish
python3 "$STACK_SOURCE/tools/stack.py" install --dry-run
python3 "$STACK_SOURCE/tools/stack.py" install
python3 "$STACK_SOURCE/tools/stack.py" init "$NEXT_PROJECT" --profile nextjs --dry-run
python3 "$STACK_SOURCE/tools/stack.py" init "$NEXT_PROJECT" --profile nextjs
python3 "$STACK_SOURCE/tools/stack.py" status "$NEXT_PROJECT"
```

Start a fresh session if new agents or instructions do not appear. To explicitly
use the three opt-in workflows, ask for `$grill-me`, `$handoff` or
`$improve-codebase-architecture`. See [skill notes](skill-notes.md) for provenance,
agent permissions and limits. No real security audit is performed by installation.

The global skills directory is a fourth recorded installation root. An existing
0.3.0-dev state without this root can update and roll back. New states must retain
the root when they own global skills. Reusing a skill leaves its body externally managed; its entrypoint path/hash is
observed. Version 0.6 adds an independently owned invocation policy as below.

For an isolated install, select a separate `--codex-home`; skills default to its
sibling `.agents/skills` rather than your personal directory. You can set
`--skills-dir` explicitly, and must repeat it for updates/rollback. Custom skills
destinations are packaging locations: Codex discovers the default user directory
or repository `.agents/skills` ancestors, not arbitrary custom directories. The
native fixture uses a disposable shared repository root to exercise its temporary
shared skills directory without changing HOME or installing into personal paths.

## Project subagents (0.5.0-dev)

Every `init` profile now installs two project-local definitions:

```text
.codex/agents/codebase-explorer.toml
.codex/agents/test-engineer.toml
```

The first maps existing modules, dependencies, conventions and affected files
without edits. The second writes behavior/contract/regression tests with the
project's configured tools; TDD applies when requested. These roles are available
on demand, not a mandatory pipeline. Their reusable contracts live in agents/;
the adapter definitions ship in the global package so the installed launcher can
initialize projects without the source checkout.

Update the global package with `install --dry-run` then `install`, then each
selected project with `init TARGET --dry-run` then `init TARGET`. Existing profiles
are retained. No `.codex/config.toml`, model setting, project trust or permissions
are changed. Existing unrelated agents remain untouched; unowned/edited matching
files and symlink parents cause conflicts before writes. Rollback uses the same
managed-file state and preserves user records.

Both roles inherit parent model/permissions, as described in the
[official custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Explorer's no-edit contract is not a separate read-only sandbox. Start a new
project session if newly installed agents do not appear. Native discovery does
not prove mapping quality, test quality, TDD discipline or actual delegation.

Codex loads project agent configuration in a trusted project context. The fixture
trusts only its temporary repository and disables ambient duplicate skill names
only in its temporary Codex configuration. The installer does not grant trust
to real projects or modify their existing client configuration.

## Scoped categories (0.6.0-dev)

Global installation adds stack-engineering, stack-ui and stack-productivity beside
the nine specialized skills. Category discovery is automatic. The nine leaf
skills use `allow_implicit_invocation: false` to avoid separate automatic triggers;
a category reads the relevant linked entrypoint as needed. Explicit `$skill-name`
requests still work. There is no daemon, hook or enforced classifier.

For an externally managed existing skill, the installer preserves SKILL.md and
all its resources, recording its entrypoint as an external dependency. It manages
only `agents/openai.yaml` for invocation policy. An existing unowned policy file
causes a conflict before writes; it is never silently replaced. Subsequent installs
retain this partial ownership. Rollback restores/removes only stack-owned policy
files, preserving original skill bodies. Their original manager may change them;
if it changes an owned policy, the next operation reports a conflict.

Update with install --dry-run, then install. Reinitialize only projects selected
by the user; an uninitialized project requires no init for the global correction.
Start a new Codex session to avoid stale instruction history. This update does
not change model, reasoning effort, personal config, trust or other project rules.

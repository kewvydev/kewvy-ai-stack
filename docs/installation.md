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
| `$CODEX_HOME/AGENTS.md`, normally `~/.codex/AGENTS.md` | Managed block of global workflow guidance |

The CLI does not modify PATH; use the launcher's absolute path if necessary.
Global guidance applies to all Codex projects, including uninitialized projects.
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

Only Codex and `core` are implemented. Initialization appends a managed context
block to `AGENTS.md`, writes `.ai-stack/installation.json`, and seeds
`.ai-stack/decisions.md` only when absent. It does not configure optional skills,
agents, hooks, MCP, framework dependencies, or application storage. Other client
configuration, including existing integrations, is left alone.

The target must be an existing directory outside the stack source. Symlinks and
symlink parents are rejected, including broken links. Non-empty global or root
project `AGENTS.override.md` files cause conflicts because they would hide installed
guidance. Nested overrides remain available for local conventions.

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

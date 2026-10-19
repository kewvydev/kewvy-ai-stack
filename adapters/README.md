# Adapter contract

The Codex core adapter is implemented in `codex/adapter.json` and consumed by
`tools/stack.py`. It maps shared templates to native global/project `AGENTS.md`
blocks. Global rules and local context remain separate canonical sources.
See [installation](../docs/installation.md) for precedence, ownership, conflicts,
updates, and verification limits.

Native verifier and selected skill installation are implemented. MCP definitions use
an explicit profile; authenticated connections and hooks remain unverified.
`supportedClients` stays empty: the verification record names the narrower tested
capability, rather than claiming broad client compatibility.

Each future adapter must define:

- Client formats and destinations for instructions, skills, roles, and MCP.
- Supported capabilities and differences between documented roles and native agents.
- How to detect existing configuration and preview changes.
- How to manage its own files without overwriting user content.
- What it verifies locally and what requires a real session or connection.

Share SDD content and role contracts. Encapsulate client-specific paths, formats,
and capabilities here. AQ-01 selects Codex as the first target adapter.

## Selected 0.3.0-dev capabilities

The adapter now installs agents/verifier.toml and stack-development.config.toml
under the selected Codex home. Per-project skills use native .agents/skills paths;
profiles inherit shared selection once. Task/finding seeds are user-owned.
The earlier core-only limitations describe 0.2.0-dev. Model delegation, remote
connections and hooks are not verified by generating these files.

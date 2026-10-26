#!/usr/bin/env python3
"""Install the opt-in Codex core using only the Python standard library."""

import argparse
import base64
import hashlib
import json
import os
import re
import shlex
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
BEGIN = b"<!-- BEGIN:ai-engineering-stack -->"
END = b"<!-- END:ai-engineering-stack -->"
BLOCK = re.compile(rb"^" + re.escape(BEGIN) + rb"\r?\n.*?^" + re.escape(END) + rb"\r?$", re.M | re.S)


class Conflict(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(data):
    return None if data is None else base64.b64encode(data).decode("ascii")


def decode(data):
    return None if data is None else base64.b64decode(data, validate=True)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def safe_path(path):
    path = Path(os.path.abspath(Path(path).expanduser()))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise Conflict(f"Symlink not allowed: {part}")
        if part != path and part.exists() and not part.is_dir():
            raise Conflict(f"Parent is not a directory: {part}")
    return path


def read(path):
    safe_path(path)
    if path.exists() and not path.is_file():
        raise Conflict(f"Expected a regular file: {path}")
    return path.read_bytes() if path.exists() else None


def block(data):
    data = data or b""
    matches = list(BLOCK.finditer(data))
    if data.count(BEGIN) != len(matches) or data.count(END) != len(matches) or len(matches) > 1:
        raise Conflict("Malformed or duplicate stack instruction markers")
    return matches[0].group() if matches else None


def replace_block(data, replacement):
    old = block(data)
    if old is not None:
        return data.replace(old, replacement or b"", 1)
    if replacement is None:
        return data
    separator = b"" if not data else (b"\n" if data.endswith(b"\n") else b"\n\n")
    return data + separator + replacement + b"\n"


def atomic_write(path, data, executable=False):
    safe_path(path)
    if data is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, name = tempfile.mkstemp(prefix=".ai-stack-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, mode | (0o100 if executable else 0))
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def project_root(path):
    root = safe_path(path)
    if not root.is_dir():
        raise Conflict("Project must be an existing directory; scaffolding is separate")
    if root in (Path("/"), Path.home()) or root == SOURCE or root in SOURCE.parents or SOURCE in root.parents:
        raise Conflict("Choose a project outside the stack source, home root, and filesystem root")
    if any(part in (".git", ".codex", ".agents", ".aws") for part in root.parts):
        raise Conflict("A client or metadata directory cannot be the project root")
    return root


class Installation:
    def __init__(self, roots, scope, version, files, profile="core", external_skills=None):
        self.roots = roots
        self.scope = scope
        self.version = version
        self.files = files
        self.profile = profile
        self.external_skills = external_skills or {}
        base = roots["package"] if scope == "global" else roots["project"] / ".ai-stack"
        self.state_path = base / "installation.json"
        self.backup_path = base / "backup.json"

    def path(self, key):
        if key not in self.files:
            raise Conflict(f"Unknown managed path: {key}")
        return self.files[key][0]

    def roots_match(self, recorded):
        expected = {k: str(v) for k, v in self.roots.items()}
        return recorded == expected or (
            self.scope == "global" and isinstance(recorded, dict)
            and recorded == {k: v for k, v in expected.items() if k != "skills"}
        )

    def validate_state(self, state):
        if (not isinstance(state, dict) or not isinstance(state.get("files"), dict)
                or not isinstance(state.get("version"), str)
                or state.get("schemaVersion") != 1 or state.get("scope") != self.scope
                or not self.roots_match(state.get("roots"))
                or not isinstance(state.get("selection"), dict)
                or state["selection"].get("client") != "codex"
                or state["selection"].get("profile") not in {Path(x).stem for x in json.loads((SOURCE / "stack.json").read_text())["profiles"]}):
            raise Conflict("Installation state does not match this scope, location, or schema")
        if self.scope == "global" and "skills" not in state["roots"] and any(key.startswith("skills/") for key in state["files"]):
            raise Conflict("Global skill ownership requires a recorded skills root")
        for key, entry in state["files"].items():
            self.path(key)
            if not isinstance(entry, dict) or entry.get("kind") != self.files[key][1] or entry["kind"] == "seed":
                raise Conflict(f"Invalid ownership entry: {key}")
            if not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
                raise Conflict(f"Invalid ownership hash: {key}")

    def plan(self):
        previous = read(self.state_path)
        state = json.loads(previous) if previous is not None else None
        if state is not None:
            self.validate_state(state)
        old_backup = read(self.backup_path)
        if old_backup is not None:
            backup = json.loads(old_backup)
            if (state is None or not isinstance(backup, dict)
                    or backup.get("schemaVersion") != 1 or backup.get("scope") != self.scope
                    or not self.roots_match(backup.get("roots"))
                    or decode(backup["afterState"]) != previous):
                raise Conflict("Existing backup is unowned or records an interrupted operation; preserved")
        changes = []
        owned = {}
        for key, (path, kind, desired) in self.files.items():
            current = read(path)
            if kind == "seed":
                if current is None:
                    changes.append((key, current, desired))
                continue
            unit = block(current) if kind == "block" else current
            entry = state["files"].get(key) if state else None
            if entry:
                if unit is None or digest(unit) != entry["sha256"]:
                    raise Conflict(f"Managed content changed or missing; preserved: {path}")
            elif unit is not None:
                raise Conflict(f"Existing content is not owned by this installation: {path}")
            result = replace_block(current or b"", desired) if kind == "block" else desired
            owned[key] = {"kind": kind, "sha256": digest(desired)}
            if result != current:
                changes.append((key, current, result))
        next_state = json_bytes({
            "schemaVersion": 1, "scope": self.scope, "version": self.version,
            "roots": {k: str(v) for k, v in self.roots.items()},
            "selection": {"client": "codex", "profile": self.profile,
                          **({"externalSkills": self.external_skills} if self.scope == "global" else {})}, "files": owned,
        })
        return previous, next_state, changes

    def apply(self, dry_run=False):
        previous, next_state, changes = self.plan()
        installed_version = json.loads(previous)["version"] if previous is not None else "not installed"
        print(f"Scope: {self.scope}; installed: {installed_version}; available: {self.version}")
        for key, before, after in changes:
            print(f"{'Create' if before is None else 'Update'}: {self.path(key)}")
        state_changed = next_state != previous
        print(f"{'Would change' if dry_run else 'Planned'}: {len(changes)} content file(s), {int(state_changed)} state file(s)")
        if dry_run or (not changes and not state_changed):
            return
        backup = {
            "schemaVersion": 1, "scope": self.scope,
            "roots": {k: str(v) for k, v in self.roots.items()},
            "previousState": encode(previous), "afterState": encode(next_state),
            "changes": [{"key": key, "before": encode(before), "after": encode(after)}
                        for key, before, after in changes if self.files[key][1] != "seed"],
        }
        old_backup = read(self.backup_path)
        applied = []
        try:
            atomic_write(self.backup_path, json_bytes(backup))
            for key, before, after in changes:
                path = self.path(key)
                if read(path) != before:
                    raise Conflict(f"File changed during installation: {path}")
                atomic_write(path, after, key == "bin/ai-stack")
                applied.append((path, before))
            atomic_write(self.state_path, next_state)
        except Exception:
            for path, before in reversed(applied):
                atomic_write(path, before)
            atomic_write(self.state_path, previous)
            atomic_write(self.backup_path, old_backup)
            raise
        print("Installed selected content. Client loading and behavior require a separate session check.")

    def rollback(self, dry_run=False):
        raw = read(self.backup_path)
        if raw is None:
            raise Conflict("No installation backup is available")
        backup = json.loads(raw)
        if (not isinstance(backup, dict) or backup.get("schemaVersion") != 1 or backup.get("scope") != self.scope
                or not self.roots_match(backup.get("roots"))):
            raise Conflict("Backup does not belong to this installation")
        after_state = decode(backup["afterState"])
        self.validate_state(json.loads(after_state))
        previous_state = decode(backup["previousState"])
        if previous_state is not None:
            self.validate_state(json.loads(previous_state))
        current_state = read(self.state_path)
        if current_state not in (after_state, previous_state):
            raise Conflict("Installation state changed after the backup; rollback refused")
        changes = []
        seen = set()
        for entry in backup["changes"]:
            key = entry["key"]
            path = self.path(key)
            if key in seen or self.files[key][1] == "seed":
                raise Conflict("Invalid backup change list")
            seen.add(key)
            before, after = decode(entry["before"]), decode(entry["after"])
            current = read(path)
            if current == before:
                continue
            if self.files[key][1] == "block":
                if block(current) == block(before):
                    continue
                if block(current) != block(after):
                    raise Conflict(f"Managed instructions changed; preserved: {path}")
                restored = before if current == after else replace_block(current, block(before))
            else:
                if current != after:
                    raise Conflict(f"File changed after installation; preserved: {path}")
                restored = before
            changes.append((path, current, restored))
        print(f"{'Would restore' if dry_run else 'Restore'}: {len(changes)} content file(s) and installation state")
        if dry_run:
            return
        applied = []
        try:
            for path, current, restored in changes:
                atomic_write(path, restored, path == self.roots.get("bin", Path("/")) / "ai-stack")
                applied.append((path, current))
            atomic_write(self.state_path, previous_state)
        except Exception:
            for path, current in reversed(applied):
                atomic_write(path, current)
            atomic_write(self.state_path, current_state)
            raise
        atomic_write(self.backup_path, None)
        print("Previous installation restored. Project records were preserved.")



def profile_content(profile_id, active=None):
    active = set() if active is None else active
    if profile_id in active:
        raise Conflict("Cyclic profile inheritance")
    path = SOURCE / "profiles" / (profile_id + ".json")
    if profile_id not in {Path(x).stem for x in json.loads((SOURCE / "stack.json").read_text())["profiles"]}:
        raise Conflict(f"Unknown profile: {profile_id}")
    profile = json.loads(path.read_text())
    skills, guidance = [], []
    for parent in profile.get("extends", []):
        parent_skills, parent_guidance = profile_content(parent, active | {profile_id})
        skills.extend(parent_skills)
        guidance.extend(parent_guidance)
    skills.extend(profile["skills"])
    guidance.append(profile["description"])
    return list(dict.fromkeys(skills)), list(dict.fromkeys(guidance))


def declared_versions(root, profile):
    if profile == "spring-boot":
        import xml.etree.ElementTree as ET
        pom = root / "pom.xml"
        if not pom.exists():
            return "No pom.xml detected. Inspect Java and Spring Boot versions before coding."
        try:
            xml = ET.fromstring(read(pom))
        except ET.ParseError as error:
            raise Conflict(f"Invalid pom.xml: {error}") from error
        def value(path):
            element = xml.find(path)
            return " ".join(element.text.split()) if element is not None and element.text else "not declared"
        boot = value("{*}properties/{*}spring-boot.version")
        if value("{*}parent/{*}artifactId") == "spring-boot-starter-parent":
            boot = value("{*}parent/{*}version")
        java = value("{*}properties/{*}java.version")
        if java == "not declared":
            java = value("{*}properties/{*}maven.compiler.release")
        return "Declared Spring Boot: " + boot + "; Java: " + java + ". Use Maven; inspect resolved versions before coding."
    package = root / "package.json"
    if profile == "core" or not package.exists():
        return "Inspect installed framework versions and existing check commands before coding."
    data = json.loads(read(package))
    if not isinstance(data, dict) or any(not isinstance(data.get(key, {}), dict) for key in ("dependencies", "devDependencies")):
        raise Conflict("package.json must contain an object with dependency maps")
    dependencies = {**data.get("devDependencies", {}), **data.get("dependencies", {})}
    names = {"nestjs": ["@nestjs/core"], "react": ["react"], "nextjs": ["react", "next"]}[profile]
    return "Declared dependency ranges: " + "; ".join(name + "=" + str(dependencies.get(name, "not declared")).replace("\n", " ").replace("\r", " ") for name in names) + ". Inspect installed versions; do not upgrade automatically."


def add_skills(files, root, skills, destination=".agents/skills", key_prefix=""):
    for name in skills:
        source = SOURCE / "skills" / name
        if not (source / "SKILL.md").is_file():
            raise Conflict(f"Selected skill is missing from the global package: {name}")
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise Conflict(f"Symlink skill source: {path}")
            if path.is_file():
                relative = Path(destination) / name / path.relative_to(source)
                files[key_prefix + str(relative)] = (root / relative, "file", path.read_bytes())


def build(args):
    manifest = json.loads((SOURCE / "stack.json").read_text())
    adapter = json.loads((SOURCE / "adapters/codex/adapter.json").read_text())
    codex = safe_path(args.codex_home)
    if read(codex / "AGENTS.override.md"):
        raise Conflict("Non-empty global AGENTS.override.md would hide stack guidance")
    if args.command == "install" or args.global_scope:
        default_codex = safe_path(os.environ.get("CODEX_HOME", "~/.codex"))
        default_skills = Path.home() / ".agents/skills" if codex == default_codex else codex.parent / ".agents/skills"
        roots = {"package": safe_path(args.prefix), "bin": safe_path(args.bin_dir), "codex": codex,
                 "skills": safe_path(getattr(args, "skills_dir", None) or default_skills)}
        for name, root in roots.items():
            self_install = name == "package" and root == SOURCE and read(root / "installation.json") is not None
            if not self_install and (root in (Path("/"), Path.home()) or root == SOURCE or root in SOURCE.parents or SOURCE in root.parents):
                raise Conflict("Global destinations must be outside the stack source and home/filesystem roots")
        for name, root in roots.items():
            for other, value in roots.items():
                if name != other and (root == value or root in value.parents):
                    raise Conflict("Global destination directories must not overlap")
        files = {}
        for relative in manifest["installationFiles"]:
            if (Path(relative).is_absolute() or any(part in (".", "..") for part in Path(relative).parts)
                    or str(Path(relative)) != relative or relative in ("installation.json", "backup.json")
                    or f"package/{relative}" in files):
                raise Conflict(f"Invalid package path: {relative}")
            source = safe_path(SOURCE / relative)
            if not source.is_relative_to(SOURCE) or not source.is_file():
                raise Conflict(f"Invalid package source: {relative}")
            files[f"package/{relative}"] = (roots["package"] / relative, "file", source.read_bytes())
        wrapper = f'#!/bin/sh\nexec python3 {shlex.quote(str(roots["package"] / "tools/stack.py"))} "$@"\n'.encode()
        files["bin/ai-stack"] = (roots["bin"] / "ai-stack", "file", wrapper)
        rules = (SOURCE / adapter["globalInstructions"]).read_bytes().rstrip()
        files["codex/AGENTS.md"] = (codex / "AGENTS.md", "block", BEGIN + b"\n" + rules + b"\n" + END)
        for relative in manifest["nativeAgents"]:
            name = Path(relative).name
            files["codex/agents/" + name] = (codex / "agents" / name, "file", (SOURCE / relative).read_bytes())
        old_state = read(roots["package"] / "installation.json")
        old_owned = {}
        if old_state is not None:
            previous = json.loads(old_state)
            if not isinstance(previous, dict) or not isinstance(previous.get("files"), dict):
                raise Conflict("Invalid existing global installation state")
            old_owned = previous["files"]
        external_skills = {}
        user_skills = roots["skills"]
        known_skills = {Path(path).parent.name for path in manifest["skills"]}
        for name in manifest.get("globalSkills", []):
            if name not in known_skills:
                raise Conflict(f"Unknown global skill: {name}")
            prefix = "skills/" + name + "/"
            external = user_skills / name / "SKILL.md"
            if prefix + "SKILL.md" not in old_owned:
                existing = read(external)
                if existing is not None:
                    if not re.search(rb"^name:\s*[\"']?" + re.escape(name.encode()) + rb"[\"']?\s*$", existing, re.M):
                        raise Conflict(f"Existing global skill has mismatched metadata: {external}")
                    external_skills[name] = {"path": str(external), "sha256": digest(existing)}
                    print(f"Reuse existing global skill (externally managed): {external}")
                    # Own only the routing policy; never adopt the external skill body.
                    policy = SOURCE / "skills" / name / "agents/openai.yaml"
                    if policy.is_file():
                        relative = Path(name) / "agents/openai.yaml"
                        files["skills/" + str(relative)] = (user_skills / relative, "file", policy.read_bytes())
                    continue
            add_skills(files, user_skills, [name], destination="", key_prefix="skills/")
        files["codex/stack-development.config.toml"] = (codex / "stack-development.config.toml", "file", (SOURCE / manifest["mcpConfiguration"]).read_bytes())
        print("MCP definitions are available through --profile stack-development; authentication and connection checks are separate.")
        return Installation(roots, "global", manifest["version"], files, external_skills=external_skills)
    if args.target is None:
        raise Conflict("A project target is required unless --global is selected")
    root = project_root(args.target)
    if read(root / "AGENTS.override.md"):
        raise Conflict("Non-empty project AGENTS.override.md would hide stack guidance")
    if args.command == "init" and block(read(codex / "AGENTS.md")) is None:
        raise Conflict("Install global core first, using the same Codex home")
    old_state = read(root / ".ai-stack/installation.json")
    recorded = json.loads(old_state)["selection"]["profile"] if old_state else "core"
    profile = getattr(args, "profile", None) or recorded
    if old_state and profile != recorded and recorded != "core":
        raise Conflict("Changing an initialized profile requires rollback first; existing files were preserved")
    skills, guidance = profile_content(profile)
    context = (SOURCE / adapter["projectInstructions"]).read_bytes().rstrip()
    context += ("\n\nSelected profile: `" + profile + "`.\n" + "\n".join(guidance) + "\n" + declared_versions(root, profile) + "\nSelected skills: " + ", ".join(skills) + ".").encode()
    files = {
        "AGENTS.md": (root / "AGENTS.md", "block", BEGIN + b"\n" + context + b"\n" + END),
        ".ai-stack/decisions.md": (root / ".ai-stack/decisions.md", "seed", (SOURCE / adapter["projectDecisions"]).read_bytes()),
    }
    for name in ("tasks", "findings"):
        key = ".ai-stack/" + name + ".md"
        files[key] = (root / key, "seed", (SOURCE / "templates" / (name + ".md")).read_bytes())
    for relative in manifest.get("projectAgents", []):
        key = ".codex/agents/" + Path(relative).name
        files[key] = (root / key, "file", (SOURCE / relative).read_bytes())
    add_skills(files, root, skills)
    return Installation({"project": root}, "project", manifest["version"], files, profile)


def main():
    # Preview/status must not create bytecode files in the package directory.
    sys.dont_write_bytecode = True
    from project_memory import add_parser as add_memory_parser, run as run_memory

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    add_memory_parser(commands)
    for name in ("install", "init", "status", "rollback"):
        command = commands.add_parser(name)
        if name != "install":
            command.add_argument("target", nargs="?", type=Path)
        command.add_argument("--global", dest="global_scope", action="store_true")
        command.add_argument("--prefix", default="~/.local/share/ai-engineering-stack")
        command.add_argument("--bin-dir", default="~/.local/bin")
        command.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"))
        command.add_argument("--skills-dir",
                             help="Global skills destination; reuse existing names without ownership")
        command.add_argument("--dry-run", action="store_true")
        if name != "install":
            command.add_argument("--profile", help="Project technology profile; defaults to the recorded profile or core")
    args = parser.parse_args()
    try:
        if args.command == "memory":
            run_memory(args)
            return 0
        if args.command == "init" and args.global_scope:
            raise Conflict("Use install for global installation")
        if args.command == "install" and getattr(args, "target", None):
            raise Conflict("Install does not accept a project target")
        if args.global_scope and getattr(args, "target", None):
            raise Conflict("Do not combine --global with a project target")
        installation = build(args)
        if args.command == "rollback":
            installation.rollback(args.dry_run)
        else:
            installation.apply(args.dry_run or args.command == "status")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Stack operation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

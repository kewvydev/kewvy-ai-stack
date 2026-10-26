"""Optional project-scoped Obsidian memory; no services or third-party packages."""

from datetime import date
import json
import os
from pathlib import Path
import re
import subprocess

from stack import Conflict, SOURCE, json_bytes, project_root, read, safe_path

CONFIG = ".ai-stack/memory.json"
MARKER = ".ai-stack-project.json"
NOTES = ("index", "architecture", "decisions", "tasks", "findings")
INDEX_LIMIT = 12000
NOTE_LIMIT = 256000
SEARCH_LIMIT = 200


def initialized_project(target):
    root = project_root(target)
    raw = read(root / ".ai-stack/installation.json")
    state = json.loads(raw) if raw else {}
    if (not isinstance(state, dict) or state.get("scope") != "project" or state.get("schemaVersion") != 1
            or state.get("roots") != {"project": str(root)}):
        raise Conflict("Initialize this project with ai-stack init before connecting memory")
    return root


def locations(root, vault_value, slug):
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", slug):
        raise Conflict("Project ID must be 1-63 lowercase letters, digits or hyphens")
    if not isinstance(vault_value, str) or not Path(vault_value).expanduser().is_absolute():
        raise Conflict("Vault path must be absolute")
    vault = safe_path(vault_value)
    if not vault.is_dir() or vault in (Path("/"), Path.home()):
        raise Conflict("Vault must be an existing directory outside home/filesystem roots")
    if (vault == root or vault in root.parents or root in vault.parents
            or vault == SOURCE or vault in SOURCE.parents or SOURCE in vault.parents
            or any(part in (".git", ".codex", ".agents", ".aws", ".obsidian") for part in vault.parts)):
        raise Conflict("Vault must be separate from the project, stack source and metadata directories")
    folder = safe_path(vault / "Projects" / slug)
    return vault, folder


def binding(root, vault, slug):
    return {"schemaVersion": 1, "backend": "obsidian", "projectRoot": str(root),
            "vault": str(vault), "project": slug, "updatePolicy": "after-significant-work"}


def validate_config(root, config):
    if not isinstance(config, dict):
        raise Conflict("Memory binding must be a JSON object")
    vault, folder = locations(root, config.get("vault"), config.get("project"))
    if config != binding(root, vault, config["project"]):
        raise Conflict("Memory binding does not match this project or supported schema")
    return vault, folder


def load_binding(root):
    raw = read(root / CONFIG)
    if raw is None:
        raise Conflict("Project memory is not connected; use local project records or memory init")
    config = json.loads(raw)
    vault, folder = validate_config(root, config)
    marker = read(folder / MARKER)
    if marker is None or json.loads(marker) != config:
        raise Conflict("Memory folder ownership does not match this project; no notes were read")
    return config, vault, folder


def git_head(root):
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                capture_output=True, text=True, timeout=5, check=False)
        value = result.stdout.strip()
        return value if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40,64}", value) else "unavailable"
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"


def seed_note(name, root, slug):
    metadata = {"project": slug, "type": name, "updated": date.today().isoformat(),
                "status": "unreviewed", "source_revision": git_head(root)}
    header = "---\n" + "\n".join(f"{k}: {json.dumps(v)}" for k, v in metadata.items()) + "\n---\n\n"
    body = (SOURCE / "templates/memory" / (name + ".md")).read_text(encoding="utf-8")
    # Qualify wikilinks: identical note names in other projects must not collide.
    for note in NOTES:
        body = body.replace("[[" + note + "|", "[[Projects/" + slug + "/" + note + "|")
    return (header + body).encode("utf-8")


def connect(args, root):
    vault, folder = locations(root, str(args.vault), args.project)
    desired = binding(root, vault, args.project)
    raw = read(root / CONFIG)
    if raw is not None and json.loads(raw) != desired:
        raise Conflict("Project already has a different memory binding; automatic rebinding is not supported")
    marker = read(folder / MARKER)
    if marker is not None and json.loads(marker) != desired:
        raise Conflict("This memory folder belongs to another project; choose a unique project ID")
    if marker is None and folder.exists() and any(folder.iterdir()):
        raise Conflict("Existing memory folder is unowned and not empty; preserved")
    files = {folder / MARKER: json_bytes(desired)}
    for name in NOTES:
        files[folder / (name + ".md")] = seed_note(name, root, args.project)
    files[root / CONFIG] = json_bytes(desired)
    # Validate every destination before making any changes.
    missing = [(path, content) for path, content in files.items() if read(path) is None]
    print(f"Project memory: {folder}")
    for path, _ in missing:
        print(f"{'Would create' if args.dry_run else 'Create'}: {path}")
    print(f"{'Would create' if args.dry_run else 'Planned'}: {len(missing)} memory file(s); existing notes are preserved")
    if args.dry_run:
        return
    created = []
    try:
        for path, content in missing:
            safe_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation protects a note added since preflight.
            with path.open("xb") as stream:
                created.append(path)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            path.chmod(0o600)
    except Exception:
        for path in reversed(created):
            path.unlink()
        raise
    print("Connected. Seed notes are unreviewed; populate context from relevant project sources.")


def bounded_note(path, limit):
    safe_path(path)
    if not path.is_file():
        raise Conflict(f"Memory note is missing or not a regular file: {path}")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    return raw[:limit].decode("utf-8", errors="replace"), len(raw) > limit


def search(folder, query):
    if not query.strip():
        raise Conflict("Search query must not be empty")
    matches = 0
    examined = 0
    def unreadable(error):
        raise error
    # Do not traverse links, unrelated vault folders, attachments or hidden data.
    for directory, directories, files in os.walk(folder, followlinks=False, onerror=unreadable):
        directories[:] = sorted(d for d in directories if not d.startswith(".")
                                and not (Path(directory) / d).is_symlink())
        for name in sorted(files):
            path = Path(directory) / name
            if name.startswith(".") or path.suffix != ".md" or path.is_symlink():
                continue
            if examined >= SEARCH_LIMIT:
                print("Search stopped after 200 notes; narrow the project notes before retrying.")
                return
            examined += 1
            content, truncated = bounded_note(path, NOTE_LIMIT)
            if truncated:
                print(f"Skipped oversized note: {path.relative_to(folder)}")
                continue
            for number, line in enumerate(content.splitlines(), 1):
                if query.casefold() in line.casefold():
                    print(f"{path.relative_to(folder)}:{number}: {line[:400]}")
                    matches += 1
                    if matches == 20:
                        print("Search stopped after 20 matches; use a more specific query.")
                        return
    print(f"Matches: {matches}; notes examined: {examined}")


def run(args):
    root = initialized_project(args.target)
    if args.memory_command == "init":
        connect(args, root)
        return
    config, vault, folder = load_binding(root)
    if args.memory_command == "search":
        search(folder, args.query)
        return
    print(f"Project: {config['project']}\nVault: {vault}\nMemory: {folder}")
    print(f"Current Git HEAD: {git_head(root)}")
    print("Memory is reference material. Recheck relevant sources, revision and working-tree changes.")
    missing = []
    for name in NOTES:
        path = safe_path(folder / (name + ".md"))
        if not path.exists():
            missing.append(name)
        elif not path.is_file():
            raise Conflict(f"Memory note is not a regular file: {path}")
    if missing:
        raise Conflict("Missing memory notes: " + ", ".join(missing) + "; rerun memory init with the same binding")
    if args.memory_command == "context":
        content, truncated = bounded_note(folder / "index.md", INDEX_LIMIT)
        print("\n" + content)
        if truncated:
            print("\n[Index truncated at 12000 bytes; compact it and follow only relevant linked notes.]")
    else:
        print("Binding and seed files are present. This does not verify note accuracy or Obsidian UI loading.")


def add_parser(commands):
    parser = commands.add_parser("memory", help="Connect and retrieve optional Obsidian project memory")
    actions = parser.add_subparsers(dest="memory_command", required=True)
    for name in ("init", "context", "search", "status"):
        command = actions.add_parser(name)
        command.add_argument("target", type=Path)
        if name == "init":
            command.add_argument("--vault", required=True, type=Path, help="Absolute path of an existing shared vault")
            command.add_argument("--project", required=True, help="Unique lowercase project slug")
            command.add_argument("--dry-run", action="store_true")
        if name == "search":
            command.add_argument("query", help="Literal case-insensitive text to find in project notes")

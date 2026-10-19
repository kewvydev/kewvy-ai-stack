"""Check foundation references using only Python's standard library."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def require_file(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f"Path outside the project: {relative}")
    require(path.is_file(), f"Missing file: {relative}")


def main():
    manifest = read_json("stack.json")
    require(manifest["methodology"] == "ODD", "The everyday workflow must be ODD")
    require(manifest["sddActivation"] == "user-approval", "SDD requires user approval")
    require(manifest["firstClient"] == "codex", "The first target client is Codex")
    require_file(manifest["installer"])
    package_files = manifest["installationFiles"]
    require(len(package_files) == len(set(package_files)), "Duplicate installation files")
    for relative in package_files:
        require(not Path(relative).is_absolute() and ".." not in Path(relative).parts,
                f"Invalid installation path: {relative}")
        require_file(relative)
    adapter = read_json("adapters/codex/adapter.json")
    require(adapter["client"] == "codex", "Unexpected core adapter")
    for key in ("globalInstructions", "projectInstructions", "projectDecisions"):
        require_file(adapter[key])
        require(adapter[key] in package_files, f"Template missing from installation: {key}")
    for relative in (manifest["installer"], "stack.json", "adapters/codex/adapter.json", "profiles/core.json"):
        require(relative in package_files, f"Runtime file missing from installation: {relative}")
    for group in ("roles", "skills", "templates", "profiles"):
        require(len(manifest[group]) == len(set(manifest[group])), f"Duplicates in {group}")
        for relative in manifest[group]:
            require_file(relative)

    roles = {Path(path).stem for path in manifest["roles"]}
    skills = set()
    for relative in manifest["skills"]:
        content = (ROOT / relative).read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
        require(frontmatter is not None, f"Missing frontmatter: {relative}")
        fields = dict(re.findall(r"^(name|description):\s*(.+)$", frontmatter[1], re.MULTILINE))
        require(set(fields) == {"name", "description"}, f"Incomplete metadata: {relative}")
        name = fields["name"]
        require(re.fullmatch(r"[a-z0-9-]{1,63}", name), f"Invalid name: {name}")
        require(name == Path(relative).parent.name, f"Folder and name do not match: {relative}")
        require(name not in skills, f"Duplicate skill: {name}")
        skills.add(name)

    require_file(manifest["mcpCatalog"])
    servers = read_json(manifest["mcpCatalog"])["servers"]
    server_ids = {server["id"] for server in servers}
    require(len(server_ids) == len(servers), "Duplicate MCP")
    for server in servers:
        require(server["source"].startswith("https://"), f"Invalid source: {server['id']}")
        require(server["enabled"] is False, "The initial catalog does not enable connections")

    profile_ids = set()
    for relative in manifest["profiles"]:
        profile = read_json(relative)
        require(profile["id"] not in profile_ids, f"Duplicate profile: {profile['id']}")
        profile_ids.add(profile["id"])
        for key, known in (("roles", roles), ("skills", skills), ("mcp", server_ids)):
            require(set(profile[key]).issubset(known), f"Unknown references in {relative}: {key}")

    # Check relative Markdown links, including the resources shipped with each skill.
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            destination = (path.parent / target.split("#", 1)[0]).resolve()
            require(destination.is_relative_to(ROOT) and destination.exists(), f"Invalid link in {path.relative_to(ROOT)}: {target}")

    print(f"Valid stack content: {len(roles)} roles, {len(skills)} skill, {len(profile_ids)} profile and {len(servers)} MCP candidates.")
    print("Checks content integrity; does not certify installation or client compatibility.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        sys.exit(1)

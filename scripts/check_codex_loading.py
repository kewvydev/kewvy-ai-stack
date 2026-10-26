"""Check native Codex instruction discovery against a local Responses fixture.

No real model, credentials, or external service is used. This checks request
assembly, not whether a model follows the instructions or approves SDD correctly.
"""

import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]


def main():
    executable = shutil.which("codex")
    if not executable:
        raise RuntimeError("Codex CLI is not available on PATH")
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            raw = self.rfile.read(int(self.headers["Content-Length"]))
            if self.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            requests.append(json.loads(raw))
            message = {
                "type": "message", "id": "msg_fixture", "role": "assistant", "status": "completed",
                "content": [{"type": "output_text", "text": "Local fixture complete.", "annotations": []}],
            }
            events = [
                {"type": "response.output_item.done", "output_index": 0, "item": message},
                {"type": "response.completed", "response": {
                    "id": "resp_fixture", "status": "completed", "output": [message],
                    "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                }},
            ]
            body = "".join("data: " + json.dumps(event) + "\n\n" for event in events).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    with tempfile.TemporaryDirectory(prefix="ai-stack-codex-") as directory:
        base = Path(directory)
        codex_home = base / "codex"
        codex_home.mkdir()
        project = base / "project"
        project.mkdir()
        (codex_home / "AGENTS.md").write_text("GLOBAL_PERSONAL_SENTINEL\n")
        (project / "AGENTS.md").write_text("PROJECT_PERSONAL_SENTINEL\n")
        options = ["--codex-home", str(codex_home), "--prefix", str(base / "package"), "--bin-dir", str(base / "bin"),
                   "--skills-dir", str(base / ".agents/skills")]
        for arguments in (("install",), ("init", str(project))):
            subprocess.run(["bash", str(ROOT / "tools/stack.sh"), *arguments, *options], check=True, capture_output=True)
        nested = project / "nested"
        nested.mkdir()
        (nested / "AGENTS.override.md").write_text("NESTED_OVERRIDE_SENTINEL\n")
        (nested / "AGENTS.md").write_text("IGNORED_NESTED_SENTINEL\n")
        subprocess.run(["git", "init", "--quiet", str(base)], check=True, capture_output=True)
        profile_projects = []
        for profile in ("nestjs", "react", "nextjs", "spring-boot"):
            target = base / profile
            target.mkdir()
            (target / "AGENTS.md").write_text("PROJECT_PERSONAL_SENTINEL\n")
            subprocess.run(["bash", str(ROOT / "tools/stack.sh"), "init", str(target), "--profile", profile, *options], check=True, capture_output=True)
            profile_projects.append((target, profile))
        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            config = f'''model = "fixture"
model_provider = "local_fixture"
[model_providers.local_fixture]
name = "Local Responses fixture"
base_url = "http://127.0.0.1:{server.server_port}/v1"
wire_api = "responses"
requires_openai_auth = false
supports_websockets = false
[features]
apps = false
plugins = false
memories = false
hooks = false
multi_agent = true
'''
            config += "\n[projects." + json.dumps(str(base)) + "]\ntrust_level = \"trusted\"\n"
            # Keep ambient user-global duplicates out of this disposable fixture.
            for name in json.loads((ROOT / "stack.json").read_text())["globalSkills"]:
                path = Path.home() / ".agents/skills" / name / "SKILL.md"
                config += "\n[[skills.config]]\npath = " + json.dumps(str(path)) + "\nenabled = false\n"
            (codex_home / "config.toml").write_text(config)
            environment = {k: v for k, v in os.environ.items() if not k.startswith(("OPENAI_", "CODEX_"))}
            environment["CODEX_HOME"] = str(codex_home)
            environment["RUST_LOG"] = "error"
            mcp = subprocess.run([executable, "--no-daemon", "--profile", "stack-development", "mcp", "list", "--json"],
                                 env=environment, capture_output=True, text=True, timeout=15)
            if mcp.returncode or {item["name"] for item in json.loads(mcp.stdout)} != {"context7", "github"}:
                raise RuntimeError("Codex did not recognize the selected MCP configuration profile")
            print("PASS: Codex recognizes Context7 and GitHub definitions; connections were not authenticated.")
            try:
                cases = [(target, profile, None) for target, profile in [(project, "core"), (nested, "core"), *profile_projects]]
                cases.extend((project, "core", skill) for skill in json.loads((ROOT / "skills/catalog.json").read_text())["categories"][0]["skills"] + ["ponytail", "grill-me", "handoff", "frontend-design", "web-design-guidelines", "vercel-composition-patterns"])
                for cwd, profile, requested_skill in cases:
                    start = len(requests)
                    result = subprocess.run([
                        executable, "--no-daemon", "exec", "--ephemeral", "--json", "--color", "never",
                        "--sandbox", "read-only", "--cd", str(cwd),
                        ("Use $" + requested_skill + ". " if requested_skill else "") + "Return the fixture response without calling any tools.",
                    ], env=environment, capture_output=True, text=True, timeout=45)
                    if result.returncode:
                        raise RuntimeError(f"Codex exited with {result.returncode}: {result.stderr[-3000:]}")
                    if len(requests) == start:
                        raise RuntimeError("Codex did not send a model request to the local fixture")
                    payload = json.dumps(requests[start])
                    for alias, directory in re.findall(r"`(r[0-9]+)` = `([^`]+)`", payload):
                        payload = payload.replace(alias + "/", directory + "/")
                    sentinels = ["GLOBAL_PERSONAL_SENTINEL", "This installation provides optional skills", "PROJECT_PERSONAL_SENTINEL", "Use a lightweight ODD flow", "At the start of a new chat, run `ai-stack memory context", f"Selected profile: `{profile}`"]
                    if cwd == nested:
                        sentinels.append("NESTED_OVERRIDE_SENTINEL")
                        if "IGNORED_NESTED_SENTINEL" in payload:
                            raise RuntimeError("Nested override did not replace its sibling AGENTS.md")
                    if "Diagnose a difficult reproducible failure or performance regression with a focused feedback loop and evidence." not in payload:
                        raise RuntimeError("Codex did not discover the installed diagnosis skill")
                    if "Guide a change through specs, plans, and evidence when the user has approved SDD for that scope" not in payload:
                        raise RuntimeError("Codex did not discover the installed SDD workflow")
                    if profile in ("react", "nextjs") and "Review and improve React or Next.js rendering, data fetching, and bundle performance when relevant to the requested change." not in payload:
                        raise RuntimeError("Codex did not discover the selected React skill")
                    if profile == "nestjs" and "Develop and review NestJS modules, dependency injection, API boundaries, and authorization using the project version and conventions." not in payload:
                        raise RuntimeError("Codex did not discover the selected NestJS skill")
                    for name in ("stack-engineering", "stack-ui", "stack-productivity"):
                        if str(base / ".agents/skills" / name / "SKILL.md") not in payload:
                            raise RuntimeError("Codex did not discover global skill: " + name)
                    for category in json.loads((ROOT / "skills/catalog.json").read_text())["categories"]:
                        for name in category["skills"]:
                            if name != requested_skill and str(base / ".agents/skills" / name / "SKILL.md") in payload:
                                raise RuntimeError("Specialized global skill leaked into implicit discovery: " + name)
                    if requested_skill and str(base / ".agents/skills" / requested_skill / "SKILL.md") not in payload:
                        raise RuntimeError("Codex did not load explicitly requested skill: " + requested_skill)
                    for description in (
                        "Map modules, dependencies, conventions and affected code in an existing project; return concise file/line references without edits.",
                        "Design and write behavior, contract and regression tests with existing project tools; use TDD when requested.",
                    ):
                        if description not in payload:
                            raise RuntimeError("Codex did not advertise a project agent: " + description)
                    if "Audit auth flows, untrusted input and pre-merge diffs for critical/high security risks" not in payload:
                        raise RuntimeError("Codex did not advertise the installed security auditor")
                    if "Check an authorized diff against acceptance criteria and report actionable findings with evidence." not in payload:
                        raise RuntimeError("Codex did not advertise the installed verifier agent")
                    positions = [payload.find(value) for value in sentinels]
                    if -1 in positions or positions != sorted(positions):
                        raise RuntimeError("Expected global/project instruction order was not observed")
                    print(f"PASS: Codex discovers instructions, SDD, shared skills and agents ({requested_skill or cwd.name}).")
                bare = base / "uninitialized"
                bare.mkdir()
                start = len(requests)
                result = subprocess.run([
                    executable, "--no-daemon", "exec", "--ephemeral", "--json", "--color", "never",
                    "--sandbox", "read-only", "--cd", str(bare),
                    "Return the fixture response without calling any tools.",
                ], env=environment, capture_output=True, text=True, timeout=45)
                if result.returncode or len(requests) == start:
                    raise RuntimeError("Uninitialized project scope check did not reach the fixture")
                payload = json.dumps(requests[start])
                if "Map modules, dependencies, conventions and affected code in an existing project" in payload or "Design and write behavior, contract and regression tests with existing project tools" in payload:
                    raise RuntimeError("Project agents leaked into an uninitialized sibling project")
                if "Use a lightweight ODD flow" in payload or "Use security-auditor for authentication" in payload:
                    raise RuntimeError("Stack workflow leaked into an uninitialized project")
                if "At the start of a new chat, run `ai-stack memory context" in payload:
                    raise RuntimeError("Obsidian session guidance leaked into an uninitialized project")
                print("PASS: project agents and stack workflow are absent from an uninitialized sibling project.")
            finally:
                server.shutdown()
                worker.join(timeout=5)
        version = subprocess.check_output([executable, "--version"], text=True).strip()
        print(f"Verified instruction, skill and agent discovery with {version}; model behavior and delegation were not tested.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Codex loading check failed: {error}", file=sys.stderr)
        sys.exit(1)

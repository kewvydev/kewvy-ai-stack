"""Check native Codex instruction discovery against a local Responses fixture.

No real model, credentials, or external service is used. This checks request
assembly, not whether a model follows the instructions or approves SDD correctly.
"""

import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
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
        options = ["--codex-home", str(codex_home), "--prefix", str(base / "package"), "--bin-dir", str(base / "bin")]
        for arguments in (("install",), ("init", str(project))):
            subprocess.run([sys.executable, str(ROOT / "tools/stack.py"), *arguments, *options], check=True, capture_output=True)
        nested = project / "nested"
        nested.mkdir()
        (nested / "AGENTS.override.md").write_text("NESTED_OVERRIDE_SENTINEL\n")
        (nested / "AGENTS.md").write_text("IGNORED_NESTED_SENTINEL\n")
        subprocess.run(["git", "init", "--quiet", str(project)], check=True, capture_output=True)
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
multi_agent = false
'''
            (codex_home / "config.toml").write_text(config)
            environment = {k: v for k, v in os.environ.items() if not k.startswith(("OPENAI_", "CODEX_"))}
            environment["CODEX_HOME"] = str(codex_home)
            environment["RUST_LOG"] = "error"
            try:
                for cwd in (project, nested):
                    start = len(requests)
                    result = subprocess.run([
                        executable, "--no-daemon", "exec", "--ephemeral", "--json", "--color", "never",
                        "--sandbox", "read-only", "--cd", str(cwd),
                        "Return the fixture response without calling any tools.",
                    ], env=environment, capture_output=True, text=True, timeout=45)
                    if result.returncode:
                        raise RuntimeError(f"Codex exited with {result.returncode}: {result.stderr[-3000:]}")
                    if len(requests) == start:
                        raise RuntimeError("Codex did not send a model request to the local fixture")
                    payload = json.dumps(requests[start])
                    sentinels = ["GLOBAL_PERSONAL_SENTINEL", "Use a lightweight ODD flow", "PROJECT_PERSONAL_SENTINEL", "Selected profile: `core`"]
                    if cwd == nested:
                        sentinels.append("NESTED_OVERRIDE_SENTINEL")
                        if "IGNORED_NESTED_SENTINEL" in payload:
                            raise RuntimeError("Nested override did not replace its sibling AGENTS.md")
                    positions = [payload.find(value) for value in sentinels]
                    if -1 in positions or positions != sorted(positions):
                        raise RuntimeError("Expected global/project instruction order was not observed")
                    print(f"PASS: Codex request contains ordered global and project instructions ({cwd.name}).")
            finally:
                server.shutdown()
                worker.join(timeout=5)
        version = subprocess.check_output([executable, "--version"], text=True).strip()
        print(f"Verified instruction discovery with {version}; model behavior was not tested.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Codex loading check failed: {error}", file=sys.stderr)
        sys.exit(1)

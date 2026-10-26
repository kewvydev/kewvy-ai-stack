"""Exercise Obsidian memory with disposable vaults and an installed launcher."""

import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-stack-memory-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project with spaces"
        self.project.mkdir()
        self.vault = self.base / "Shared Vault"
        self.vault.mkdir()
        self.folder = self.vault / "Projects/example"
        self.config = self.project / ".ai-stack/memory.json"
        self.package = self.base / "package"
        self.bin = self.base / "bin"
        self.options = ["--prefix", str(self.package), "--bin-dir", str(self.bin),
                        "--codex-home", str(self.base / "codex"), "--skills-dir", str(self.base / "skills")]
        self.stack("install")
        self.stack("init", self.project)

    def stack(self, *args):
        result = subprocess.run([sys.executable, str(ROOT / "tools/stack.py"), *map(str, args),
                                 *self.options], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def memory(self, action, *args, ok=True, target=None):
        result = subprocess.run([str(self.bin / "ai-stack"), "memory", action,
                                 str(target or self.project), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if ok else 1, result.stdout + result.stderr)
        return result

    def connect(self, *extra, ok=True, target=None, slug="example", vault=None):
        return self.memory("init", "--vault", vault or self.vault, "--project", slug,
                           *extra, ok=ok, target=target)

    def test_preview_connection_and_repeat_preserve_human_notes(self):
        before = snapshot(self.base)
        self.connect("--dry-run")
        self.assertEqual(before, snapshot(self.base))
        self.connect()
        binding = json.loads(self.config.read_text())
        self.assertEqual(binding["vault"], str(self.vault))
        self.assertEqual(binding["updatePolicy"], "after-significant-work")
        self.assertEqual(binding, json.loads((self.folder / ".ai-stack-project.json").read_text()))
        index = self.folder / "index.md"
        self.assertIn('status: "unreviewed"', index.read_text())
        self.assertIn("[[Projects/example/architecture|", index.read_text())
        index.write_text(index.read_text() + "\nHuman note: authentication uses the existing API.\n")
        before = snapshot(self.base)
        self.connect()
        self.assertEqual(before, snapshot(self.base))
        result = self.memory("context")
        self.assertIn("Human note: authentication", result.stdout)
        self.assertIn("Current Git HEAD:", result.stdout)
        self.assertFalse((self.vault / ".obsidian").exists())

    def test_no_binding_and_missing_vault_are_explicit(self):
        self.assertIn("not connected", self.memory("context", ok=False).stderr)
        before = snapshot(self.base)
        self.connect(ok=False, vault=self.base / "absent")
        self.assertEqual(before, snapshot(self.base))
        self.connect()
        self.vault.rename(self.base / "moved-vault")
        self.assertIn("existing directory", self.memory("status", ok=False).stderr)
        self.assertFalse(self.vault.exists())

    def test_uninitialized_project_is_rejected(self):
        other = self.base / "uninitialized"
        other.mkdir()
        before = snapshot(self.base)
        self.connect(ok=False, target=other)
        self.assertEqual(before, snapshot(self.base))

    def test_existing_folder_and_cross_project_collision_are_preserved(self):
        self.folder.mkdir(parents=True)
        note = self.folder / "personal.md"
        note.write_text("Private personal note")
        before = snapshot(self.base)
        self.connect(ok=False)
        self.assertEqual(before, snapshot(self.base))
        note.unlink()
        self.connect()
        other = self.base / "other-project"
        other.mkdir()
        self.stack("init", other)
        before = snapshot(self.base)
        self.connect(ok=False, target=other)
        self.assertEqual(before, snapshot(self.base))
        self.assertFalse((other / ".ai-stack/memory.json").exists())

    def test_search_is_scoped_literal_bounded_and_link_safe(self):
        self.connect()
        (self.folder / "module.md").write_text("Auth[API] confirmed\n")
        other = self.vault / "Projects/another-project"
        other.mkdir()
        (other / "secret.md").write_text("Auth[API] UNRELATED_SECRET")
        (self.folder / "linked.md").symlink_to(other / "secret.md")
        (self.folder / "linked-folder").symlink_to(other, target_is_directory=True)
        result = self.memory("search", "auth[api]")
        self.assertIn("module.md:1: Auth[API] confirmed", result.stdout)
        self.assertNotIn("UNRELATED_SECRET", result.stdout)
        (self.folder / "module.md").write_text("Auth[API] confirmed\n" * 30)
        self.assertIn("20 matches", self.memory("search", "Auth[API]").stdout)
        (self.folder / "module.md").write_text("x" * 256001 + "Auth[API]")
        self.assertIn("Skipped oversized note", self.memory("search", "Auth[API]").stdout)
        self.memory("search", " ", ok=False)

    def test_index_is_bounded_and_missing_seeds_can_be_restored(self):
        self.connect()
        index = self.folder / "index.md"
        index.write_text("a" * 13000 + "DO_NOT_PRINT_TAIL")
        self.assertIn("Index truncated", self.memory("context").stdout)
        self.assertNotIn("DO_NOT_PRINT_TAIL", self.memory("context").stdout)
        (self.folder / "tasks.md").unlink()
        self.assertIn("Missing memory notes", self.memory("status", ok=False).stderr)
        self.connect()
        self.assertEqual(index.read_text(), "a" * 13000 + "DO_NOT_PRINT_TAIL")
        self.memory("status")

    def test_tampered_binding_and_marker_fail_before_reading_notes(self):
        self.connect()
        original = self.config.read_bytes()
        config = json.loads(original)
        config["project"] = "../other"
        self.config.write_text(json.dumps(config))
        self.memory("context", ok=False)
        self.config.write_bytes(original)
        (self.folder / ".ai-stack-project.json").write_text("{}")
        self.assertIn("ownership", self.memory("context", ok=False).stderr)

    def test_unsafe_paths_and_rebinding_write_nothing(self):
        for slug in ("../escape", "/absolute", "Bad ID", "x" * 64):
            before = snapshot(self.base)
            self.connect(ok=False, slug=slug)
            self.assertEqual(before, snapshot(self.base))
        self.connect(ok=False, vault=self.project)
        self.connect(ok=False, vault="relative-vault")
        alias = self.base / "alias"
        alias.symlink_to(self.vault, target_is_directory=True)
        self.connect(ok=False, vault=alias)
        self.connect()
        before = snapshot(self.base)
        self.connect(ok=False, slug="different")
        self.assertEqual(before, snapshot(self.base))

    def test_symlink_seeds_and_config_are_rejected(self):
        self.connect()
        external = self.base / "external.md"
        external.write_text("EXTERNAL_SECRET")
        index = self.folder / "index.md"
        index.unlink()
        index.symlink_to(external)
        self.memory("context", ok=False)
        self.connect(ok=False)
        self.assertEqual(external.read_text(), "EXTERNAL_SECRET")
        index.unlink()
        self.config.unlink()
        self.config.symlink_to(external)
        self.connect(ok=False)

    def test_interrupted_connection_resumes_and_installer_rollback_preserves_memory(self):
        self.connect()
        self.config.unlink()
        (self.folder / "architecture.md").unlink()
        index = self.folder / "index.md"
        index.write_text("Preserve partial connection edits")
        self.connect()
        before = snapshot(self.vault)
        config = self.config.read_bytes()
        self.stack("init", self.project)
        self.assertEqual(before, snapshot(self.vault))
        self.stack("rollback", self.project)
        self.assertEqual(before, snapshot(self.vault))
        self.assertEqual(config, self.config.read_bytes())

    def test_write_failure_removes_only_new_files(self):
        sys.path.insert(0, str(ROOT / "tools"))
        try:
            memory = importlib.import_module("project_memory")
        finally:
            sys.path.pop(0)
        args = type("Args", (), {"vault": self.vault, "project": "example", "dry_run": False})()
        with patch.object(memory.os, "fsync", side_effect=OSError("simulated storage failure")):
            with self.assertRaises(OSError):
                memory.connect(args, self.project)
        self.assertFalse(self.config.exists())
        self.assertEqual(snapshot(self.vault), {})


if __name__ == "__main__":
    unittest.main()

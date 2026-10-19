"""Exercise installation boundaries in disposable projects and Codex homes."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-stack-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        manifest = json.loads((ROOT / "stack.json").read_text())
        for name in manifest["installationFiles"]:
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.prefix = self.base / "package"
        self.bin_dir = self.base / "bin with spaces"
        self.codex = self.base / "codex"
        self.project = self.base / "project"
        self.project.mkdir()
        self.user_skills = self.base / "user-skills"
        self.options = ["--prefix", str(self.prefix), "--bin-dir", str(self.bin_dir), "--codex-home", str(self.codex),
                        "--skills-dir", str(self.user_skills)]

    def cli(self, *args, ok=True, installed=False):
        executable = [str(self.bin_dir / "ai-stack")] if installed else [sys.executable, str(self.source / "tools/stack.py")]
        result = subprocess.run(executable + list(map(str, args)) + self.options, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if ok else 1, result.stdout + result.stderr)
        return result

    def install(self):
        self.cli("install")

    def initialize(self):
        self.install()
        self.cli("init", self.project)

    def next_version(self):
        path = self.source / "stack.json"
        manifest = json.loads(path.read_text())
        manifest["version"] = "0.3.0-test"
        path.write_text(json.dumps(manifest, indent=2) + "\n")
        for name in ("global-rules.md", "AGENTS.md"):
            path = self.source / "templates" / name
            path.write_text(path.read_text() + "\nAdditional release guidance.\n")

    def test_dry_run_writes_nothing(self):
        before = snapshot(self.base)
        self.cli("install", "--dry-run")
        self.assertEqual(before, snapshot(self.base))
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.prefix.exists())

    def test_global_reinstall_and_installed_launcher(self):
        self.install()
        before = snapshot(self.base)
        result = self.cli("install", installed=True)
        self.assertIn("0 content file(s), 0 state file(s)", result.stdout)
        self.assertEqual(before, snapshot(self.base))
        self.assertTrue(os.access(self.bin_dir / "ai-stack", os.X_OK))
        self.cli("status", "--global", installed=True)

    def test_project_dry_run_and_reinstall_preserve_user_content(self):
        self.install()
        instructions = self.project / "AGENTS.md"
        instructions.write_bytes(b"Personal rules without a final newline")
        before = snapshot(self.base)
        self.cli("init", self.project, "--dry-run")
        self.assertEqual(before, snapshot(self.base))
        self.cli("init", self.project, installed=True)
        instructions.write_bytes(b"New local rules\n" + instructions.read_bytes())
        decisions = self.project / ".ai-stack/decisions.md"
        decisions.write_text(decisions.read_text() + "\nDEC-01: Keep SQLite for this project.\n")
        before = snapshot(self.base)
        self.cli("init", self.project)
        self.assertEqual(before, snapshot(self.base))
        self.assertIn(b"Personal rules without a final newline", instructions.read_bytes())

    def test_global_personal_rules_and_config_are_preserved(self):
        self.codex.mkdir()
        (self.codex / "AGENTS.md").write_bytes(b"Personal rules\r\n<!-- BEGIN:other -->\r\nOther rules\r\n")
        (self.codex / "config.toml").write_text('model = "existing-choice"\n')
        self.install()
        self.assertTrue((self.codex / "AGENTS.md").read_bytes().startswith(b"Personal rules\r\n<!-- BEGIN:other -->\r\nOther rules\r\n"))
        self.assertEqual((self.codex / "config.toml").read_text(), 'model = "existing-choice"\n')

    def test_requires_global_core_and_existing_project(self):
        before = snapshot(self.base)
        self.cli("init", self.project, ok=False)
        self.assertEqual(before, snapshot(self.base))
        self.install()
        self.cli("init", self.base / "missing", ok=False)
        self.assertFalse((self.base / "missing").exists())

    def test_unowned_package_file_blocks_all_writes(self):
        self.prefix.mkdir()
        (self.prefix / "stack.json").write_text("User file")
        before = snapshot(self.base)
        self.cli("install", ok=False)
        self.assertEqual(before, snapshot(self.base))

    def test_edited_managed_content_blocks_update(self):
        self.install()
        path = self.codex / "AGENTS.md"
        path.write_text(path.read_text().replace("lightweight ODD", "custom workflow"))
        self.next_version()
        before = snapshot(self.base)
        self.cli("install", ok=False)
        self.assertEqual(before, snapshot(self.base))

    def test_update_and_global_rollback_between_versions(self):
        self.install()
        before_package = snapshot(self.prefix)
        before_package.pop("backup.json")
        before_rules = (self.codex / "AGENTS.md").read_bytes()
        self.next_version()
        self.cli("install", "--dry-run")
        self.assertEqual(before_package, {k: v for k, v in snapshot(self.prefix).items() if k != "backup.json"})
        self.install()
        self.assertEqual(json.loads((self.prefix / "installation.json").read_text())["version"], "0.3.0-test")
        self.cli("rollback", "--global")
        self.assertEqual(before_package, snapshot(self.prefix))
        self.assertEqual(before_rules, (self.codex / "AGENTS.md").read_bytes())

    def test_project_update_rollback_preserves_decisions_and_outside_edits(self):
        self.initialize()
        decisions = self.project / ".ai-stack/decisions.md"
        decisions.write_text("# Existing project decisions\n\nDEC-01: approved by user.\n")
        old_instructions = (self.project / "AGENTS.md").read_bytes()
        self.next_version()
        self.install()
        self.cli("init", self.project)
        path = self.project / "AGENTS.md"
        path.write_bytes(b"New personal instructions\n\n" + path.read_bytes())
        self.cli("rollback", self.project)
        self.assertEqual(path.read_bytes(), b"New personal instructions\n\n" + old_instructions)
        self.assertEqual(decisions.read_text(), "# Existing project decisions\n\nDEC-01: approved by user.\n")

    def test_rollback_first_install_keeps_decision_record(self):
        self.install()
        instructions = self.project / "AGENTS.md"
        instructions.write_bytes(b"Original instructions")
        self.cli("init", self.project)
        self.cli("rollback", self.project)
        self.assertEqual(instructions.read_bytes(), b"Original instructions")
        self.assertFalse((self.project / ".ai-stack/installation.json").exists())
        self.assertTrue((self.project / ".ai-stack/decisions.md").exists())

    def test_rollback_dry_run_and_modified_file_conflict(self):
        self.install()
        before = snapshot(self.base)
        self.cli("rollback", "--global", "--dry-run")
        self.assertEqual(before, snapshot(self.base))
        (self.prefix / "templates/global-rules.md").write_text("Local customization")
        before = snapshot(self.base)
        self.cli("rollback", "--global", ok=False)
        self.assertEqual(before, snapshot(self.base))

    def test_symlink_destinations_and_parents_are_rejected(self):
        self.install()
        outside = self.base / "outside"
        outside.mkdir()
        for relative in ("AGENTS.md", ".ai-stack", ".codex"):
            with self.subTest(relative=relative):
                link = self.project / relative
                link.symlink_to(outside / "missing" if relative == "AGENTS.md" else outside)
                self.cli("init", self.project, ok=False)
                self.assertEqual(snapshot(outside), {})
                link.unlink()
        alias = self.base / "alias"
        alias.symlink_to(self.project)
        self.cli("init", alias, ok=False)

    def test_overrides_and_malformed_markers_are_rejected(self):
        self.codex.mkdir()
        override = self.codex / "AGENTS.override.md"
        override.write_text("Overrides global guidance")
        self.cli("install", ok=False)
        override.unlink()
        self.install()
        override = self.project / "AGENTS.override.md"
        override.write_text("Overrides project guidance")
        self.cli("init", self.project, ok=False)
        override.unlink()
        (self.project / "AGENTS.md").write_bytes(b"<!-- BEGIN:ai-engineering-stack -->\nIncomplete")
        self.cli("init", self.project, ok=False)

    def test_unsafe_roots_and_mismatched_state_are_rejected(self):
        self.install()
        self.cli("init", self.source, ok=False)
        self.cli("init", Path.home(), ok=False)
        state_path = self.prefix / "installation.json"
        state = json.loads(state_path.read_text())
        state["roots"]["bin"] = str(self.base / "different-bin")
        state_path.write_text(json.dumps(state))
        self.cli("install", ok=False)
        for malformed in ([], None, {"files": []}, {"files": {"package/stack.json": []}}):
            state_path.write_text(json.dumps(malformed))
            before = snapshot(self.base)
            result = self.cli("install", ok=False)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(before, snapshot(self.base))

    def test_backup_cannot_select_an_arbitrary_path(self):
        self.install()
        backup_path = self.prefix / "backup.json"
        backup = json.loads(backup_path.read_text())
        backup["changes"][0]["key"] = "package/../../outside"
        backup_path.write_text(json.dumps(backup))
        before = snapshot(self.base)
        self.cli("rollback", "--global", ok=False)
        self.assertEqual(before, snapshot(self.base))

    def test_write_failure_restores_previous_files_and_state(self):
        self.install()
        spec = importlib.util.spec_from_file_location("installer", self.source / "tools/stack.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = type("Args", (), {"command": "init", "global_scope": False, "target": self.project, "codex_home": self.codex})()
        installation = module.build(args)
        original = module.atomic_write
        failed = False

        def fail_once(path, data, executable=False):
            nonlocal failed
            if path.name == "decisions.md" and not failed:
                failed = True
                raise OSError("Synthetic disk error")
            return original(path, data, executable)

        before = snapshot(self.base)
        with patch.object(module, "atomic_write", fail_once), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(OSError, "Synthetic disk error"):
                installation.apply()
        self.assertEqual(before, snapshot(self.base))

    def test_core_installs_only_approved_capabilities(self):
        self.initialize()
        for root in (self.codex, self.project):
            self.assertFalse((root / "config.toml").exists())
            self.assertFalse((root / "hooks.json").exists())
        self.assertEqual({p.name for p in (self.codex / "agents").iterdir()}, {"verifier.toml", "security-auditor.toml"})
        self.assertTrue((self.codex / "stack-development.config.toml").exists())
        self.assertEqual({p.name for p in (self.project / ".agents/skills").iterdir()}, {"diagnosing-bugs", "sdd-workflow"})

    def test_project_agents_work_from_snapshot_and_preserve_client_files(self):
        self.install()
        shutil.rmtree(self.source)
        client = self.project / ".codex"
        (client / "agents").mkdir(parents=True)
        config = client / "config.toml"
        config.write_text('model = "existing-project-model"\n')
        custom = client / "agents/local-reviewer.toml"
        custom.write_text('name = "local-reviewer"\n')
        self.cli("init", self.project, installed=True)
        for name in ("codebase-explorer", "test-engineer"):
            relative = ".codex/agents/" + name + ".toml"
            self.assertEqual((self.project / relative).read_bytes(),
                             (ROOT / "adapters/codex/agents" / (name + ".toml")).read_bytes())
            state = json.loads((self.project / ".ai-stack/installation.json").read_text())
            self.assertIn(relative, state["files"])
            self.assertFalse((self.codex / "agents" / (name + ".toml")).exists())
        before = snapshot(self.base)
        self.cli("init", self.project, installed=True)
        self.assertEqual(before, snapshot(self.base))
        self.cli("rollback", self.project, installed=True)
        self.assertEqual(config.read_text(), 'model = "existing-project-model"\n')
        self.assertEqual(custom.read_text(), 'name = "local-reviewer"\n')
        self.assertFalse((client / "agents/codebase-explorer.toml").exists())
        self.assertFalse((client / "agents/test-engineer.toml").exists())
        self.assertTrue((self.project / ".ai-stack/tasks.md").exists())

    def test_project_agent_collisions_and_edits_block_all_writes(self):
        self.install()
        unowned = self.project / ".codex/agents/codebase-explorer.toml"
        unowned.parent.mkdir(parents=True)
        unowned.write_text('name = "user-owned-explorer"\n')
        before = snapshot(self.base)
        self.cli("init", self.project, ok=False)
        self.assertEqual(before, snapshot(self.base))
        unowned.unlink()
        self.cli("init", self.project)
        for name in ("codebase-explorer", "test-engineer"):
            with self.subTest(agent=name):
                path = self.project / ".codex/agents" / (name + ".toml")
                original = path.read_bytes()
                path.write_bytes(original + b"\n# User customization.\n")
                before = snapshot(self.base)
                self.cli("init", self.project, ok=False)
                self.assertEqual(before, snapshot(self.base))
                path.write_bytes(original)

    def test_global_skills_are_available_without_project_copies(self):
        self.initialize()
        manifest = json.loads((self.source / "stack.json").read_text())
        for name in manifest["globalSkills"]:
            self.assertEqual(snapshot(self.source / "skills" / name), snapshot(self.user_skills / name))
            self.assertFalse((self.project / ".agents/skills" / name).exists())

    def test_existing_global_skills_are_reused_and_survive_rollback(self):
        path = self.user_skills / "ponytail/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nname: ponytail\ndescription: Existing user version.\n---\nPersonal guidance.\n")
        original = snapshot(self.user_skills)
        result = self.cli("install")
        self.assertIn("externally managed", result.stdout)
        self.assertEqual(path.read_bytes(), original["ponytail/SKILL.md"])
        state = json.loads((self.prefix / "installation.json").read_text())
        self.assertEqual(state["selection"]["externalSkills"]["ponytail"]["path"], str(path))
        self.assertFalse(any(key.startswith("skills/ponytail/") for key in state["files"]))
        before = snapshot(self.base)
        self.cli("install")
        self.assertEqual(before, snapshot(self.base))
        self.cli("rollback", "--global")
        self.assertEqual(snapshot(self.user_skills), original)

    def test_unowned_native_global_skill_blocks_all_writes(self):
        path = self.user_skills / "tdd/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("Existing unowned skill")
        before = snapshot(self.base)
        self.cli("install", ok=False)
        self.assertEqual(before, snapshot(self.base))

    def test_legacy_global_roots_can_update_without_losing_recovery(self):
        self.install()
        state_path = self.prefix / "installation.json"
        state = json.loads(state_path.read_text())
        state["roots"].pop("skills")
        state["files"] = {key: value for key, value in state["files"].items() if not key.startswith("skills/")}
        for path in self.user_skills.iterdir():
            shutil.rmtree(path)
        state["selection"].pop("externalSkills", None)
        legacy = json.dumps(state).encode()
        state_path.write_bytes(legacy)
        (self.prefix / "backup.json").unlink()
        self.install()
        self.assertIn("skills", json.loads(state_path.read_text())["roots"])
        self.cli("rollback", "--global")
        self.assertEqual(state_path.read_bytes(), legacy)
        self.assertEqual(snapshot(self.user_skills), {})

    def test_sdd_resources_are_available_from_installed_package_without_scaffolding(self):
        self.install()
        self.cli("init", self.project, installed=True)
        source = self.source / "skills/sdd-workflow"
        target = self.project / ".agents/skills/sdd-workflow"
        self.assertEqual(snapshot(source), snapshot(target))
        self.assertEqual(len(list((target / "assets").glob("*.md"))), 4)
        self.assertFalse((self.project / "specs").exists())

    def test_interrupted_update_can_be_rolled_back(self):
        self.install()
        expected = {k: v for k, v in snapshot(self.prefix).items() if k != "backup.json"}
        self.next_version()
        spec = importlib.util.spec_from_file_location("interrupted_installer", self.source / "tools/stack.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = type("Args", (), {"command": "install", "global_scope": False, "prefix": self.prefix,
                                "bin_dir": self.bin_dir, "codex_home": self.codex, "skills_dir": self.user_skills})()
        original = module.atomic_write

        def interrupt(path, data, executable=False):
            if path == self.prefix / "templates/global-rules.md":
                raise KeyboardInterrupt("Synthetic interruption")
            return original(path, data, executable)

        with patch.object(module, "atomic_write", interrupt), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.build(args).apply()
        self.cli("install", ok=False)
        self.cli("rollback", "--global")
        self.assertEqual(expected, snapshot(self.prefix))

    def test_unowned_metadata_and_unsafe_manifest_paths_are_preserved(self):
        self.prefix.mkdir()
        backup = self.prefix / "backup.json"
        backup.write_text("{}")
        before = snapshot(self.base)
        self.cli("install", ok=False)
        self.assertEqual(before, snapshot(self.base))
        backup.unlink()
        manifest_path = self.source / "stack.json"
        original = manifest_path.read_text()
        for bad_path in (str(self.source / "stack.json"), "../outside", "tools/../stack.json", "installation.json"):
            with self.subTest(path=bad_path):
                manifest = json.loads(original)
                manifest["installationFiles"].append(bad_path)
                manifest_path.write_text(json.dumps(manifest))
                before = snapshot(self.base)
                self.cli("install", ok=False)
                self.assertEqual(before, snapshot(self.base))


    def test_framework_profiles_are_separate_and_next_reuses_react(self):
        self.install()
        expected = {
            "nestjs": {"diagnosing-bugs", "sdd-workflow", "nestjs-best-practices"},
            "react": {"diagnosing-bugs", "sdd-workflow", "vercel-react-best-practices"},
            "nextjs": {"diagnosing-bugs", "sdd-workflow", "vercel-react-best-practices"},
            "spring-boot": {"diagnosing-bugs", "sdd-workflow"},
        }
        for profile, skills in expected.items():
            project = self.base / profile
            project.mkdir()
            self.cli("init", project, "--profile", profile)
            self.assertEqual({p.name for p in (project / ".agents/skills").iterdir()}, skills)
            self.assertEqual({p.name for p in (project / ".codex/agents").iterdir()},
                             {"codebase-explorer.toml", "test-engineer.toml"})
            before = snapshot(project)
            self.cli("init", project)
            self.assertEqual(before, snapshot(project))
            state = json.loads((project / ".ai-stack/installation.json").read_text())
            self.assertEqual(state["selection"]["profile"], profile)
            self.assertFalse((project / "package.json").exists())
            self.assertFalse((project / "pom.xml").exists())

    def test_user_records_survive_update_and_rollback(self):
        self.initialize()
        records = {}
        for name in ("tasks", "findings"):
            path = self.project / ".ai-stack" / (name + ".md")
            path.write_text("# " + name + "\nConfirmed project knowledge.\n")
            records[path] = path.read_bytes()
        self.next_version()
        self.install()
        self.cli("init", self.project)
        self.cli("rollback", self.project)
        for path, content in records.items():
            self.assertEqual(path.read_bytes(), content)

    def test_skill_conflict_and_profile_change_preserve_project(self):
        self.install()
        self.cli("init", self.project, "--profile", "react")
        before = snapshot(self.project)
        self.cli("init", self.project, "--profile", "nestjs", ok=False)
        self.assertEqual(before, snapshot(self.project))
        skill = self.project / ".agents/skills/vercel-react-best-practices/SKILL.md"
        skill.write_text(skill.read_text() + "\nLocal customization.\n")
        before = snapshot(self.project)
        self.cli("init", self.project, ok=False)
        self.assertEqual(before, snapshot(self.project))

    def test_declared_versions_and_maven_are_context_not_scaffolding(self):
        self.install()
        package = self.project / "package.json"
        package.write_text(json.dumps({"dependencies": {"react": "^19.0.0", "next": "^16.0.0"}}))
        self.cli("init", self.project, "--profile", "nextjs")
        context = (self.project / "AGENTS.md").read_text()
        self.assertIn("react=^19.0.0", context)
        self.assertIn("next=^16.0.0", context)
        spring = self.base / "spring"
        spring.mkdir()
        (spring / "pom.xml").write_text('<project xmlns="http://maven.apache.org/POM/4.0.0"><parent><artifactId>spring-boot-starter-parent</artifactId><version>4.0.0</version></parent><properties><java.version>21</java.version></properties></project>')
        self.cli("init", spring, "--profile", "spring-boot")
        context = (spring / "AGENTS.md").read_text()
        self.assertIn("4.0.0", context)
        self.assertIn("Java: 21", context)
        self.assertIn("Maven", context)

    def test_unowned_skill_and_invalid_profile_block_all_writes(self):
        self.install()
        path = self.project / ".agents/skills/nestjs-best-practices/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("Existing user skill")
        before = snapshot(self.project)
        self.cli("init", self.project, "--profile", "nestjs", ok=False)
        self.assertEqual(before, snapshot(self.project))
        self.cli("init", self.project, "--profile", "../../outside", ok=False)
        self.assertEqual(before, snapshot(self.project))



    def test_core_can_be_promoted_and_rolled_back(self):
        self.initialize()
        self.cli("init", self.project, "--profile", "nestjs")
        self.assertTrue((self.project / ".agents/skills/nestjs-best-practices/SKILL.md").exists())
        self.cli("rollback", self.project)
        state = json.loads((self.project / ".ai-stack/installation.json").read_text())
        self.assertEqual(state["selection"]["profile"], "core")
        self.assertFalse((self.project / ".agents/skills/nestjs-best-practices/SKILL.md").exists())

if __name__ == "__main__":
    unittest.main()

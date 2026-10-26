"""Exercise installation boundaries in disposable projects and Codex homes."""

import hashlib
import json
import os
import pty
import select
import time
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

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

    def cli(self, *args, ok=True, installed=False, env=None):
        executable = [str(self.bin_dir / "ai-stack")] if installed else ["bash", str(self.source / "tools/stack.sh")]
        result = subprocess.run(executable + list(map(str, args)) + self.options, capture_output=True, text=True, env=env)
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
        path.write_text(path.read_text().replace("optional skills", "custom workflow"))
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

    def write_fault_environment(self, destination, mode="fail"):
        """Fail one real atomic rename; keep fault injection out of production code."""
        faults = tempfile.TemporaryDirectory(prefix="ai-stack-fault-")
        self.addCleanup(faults.cleanup)
        folder = Path(faults.name)
        real_mv = shutil.which("mv")
        shim = folder / "mv"
        shim.write_text("""#!/usr/bin/env bash
if [[ ${@: -1} == "$FAIL_DESTINATION" && ! -e "$FAIL_MARKER" ]]; then
    touch "$FAIL_MARKER"
    if [[ $FAIL_MODE == interrupt ]]; then
        rm -f -- "${@: -2:1}"
        kill -KILL "$PPID"
    fi
    exit 1
fi
exec "$REAL_MV" "$@"
""")
        shim.chmod(0o700)
        return {**os.environ, "TMPDIR": str(folder), "PATH": str(folder) + os.pathsep + os.environ["PATH"],
                "REAL_MV": real_mv, "FAIL_DESTINATION": str(destination),
                "FAIL_MARKER": str(folder / "failed"), "FAIL_MODE": mode}

    def test_write_failure_restores_previous_files_and_state(self):
        self.install()
        env = self.write_fault_environment(self.project / ".ai-stack/decisions.md")
        before = snapshot(self.base)
        self.cli("init", self.project, ok=False, env=env)
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
        self.assertNotIn("skills/ponytail/SKILL.md", state["files"])
        self.assertIn("skills/ponytail/agents/openai.yaml", state["files"])
        self.assertIn("allow_implicit_invocation: false", (path.parent / "agents/openai.yaml").read_text())
        before = snapshot(self.base)
        self.cli("install")
        self.assertEqual(before, snapshot(self.base))
        self.cli("rollback", "--global")
        self.assertEqual(snapshot(self.user_skills), original)

    def test_external_skill_policy_conflict_preserves_everything(self):
        path = self.user_skills / "ponytail/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nname: ponytail\ndescription: User version.\n---\n")
        policy = path.parent / "agents/openai.yaml"
        policy.parent.mkdir()
        policy.write_text("policy:\n  allow_implicit_invocation: true\n")
        before = snapshot(self.base)
        result = self.cli("install", ok=False)
        self.assertIn("not owned", result.stderr)
        self.assertEqual(before, snapshot(self.base))

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
        env = self.write_fault_environment(self.prefix / "templates/global-rules.md", "interrupt")
        result = subprocess.run(["bash", str(self.source / "tools/stack.sh"), "install", *self.options],
                                env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, -9, result.stdout + result.stderr)
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

    def menu(self, answers, *args, ok=True, installed=False):
        master, slave = pty.openpty()
        try:
            executable = [str(self.bin_dir / "ai-stack")] if installed else ["bash", str(self.source / "tools/stack.sh")]
            process = subprocess.Popen([*executable, *args, *self.options],
                                       stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, cwd=self.project)
            os.close(slave)
            slave = None
            os.write(master, answers.encode())
            output, _ = process.communicate(timeout=90)
            self.assertEqual(process.returncode, 0 if ok else 1, output)
            return output
        finally:
            os.close(master)
            if slave is not None:
                os.close(slave)

    def test_menu_selects_global_and_project_profile(self):
        renamed = self.base / "project with spaces"
        self.project.rename(renamed)
        self.project = renamed
        self.menu("1\ny\n")
        output = self.menu("2\ny\n3\ny\n", installed=True)
        self.assertIn(str(self.project), output)
        self.assertIn("Is this the correct directory? [y/N]", output)
        self.assertNotIn("Existing project directory", output)
        self.assertIn("React", output)
        self.assertIn("Review installation", output)
        self.assertIn("Installation complete.", output)
        self.assertNotIn("Create:", output)
        state = json.loads((self.project / ".ai-stack/installation.json").read_text())
        self.assertEqual(state["selection"]["profile"], "react")
        self.assertEqual(state["roots"]["project"], str(self.project))
        self.assertFalse((self.source / ".ai-stack").exists())
        self.assertTrue((self.project / ".agents/skills/vercel-react-best-practices/SKILL.md").is_file())
        self.assertFalse((self.project / ".agents/skills/nestjs-best-practices").exists())

    def test_menu_cancel_invalid_input_and_preview_do_not_write(self):
        before = snapshot(self.base)
        self.menu("bad\n0\n")
        self.menu("1\nn\n")
        preview = self.menu("1\n", "--dry-run")
        self.assertIn("Review installation", preview)
        self.assertNotIn("Create:", preview)
        self.assertNotIn("\x1b[", preview)
        detailed = self.menu("1\n", "--dry-run", "--verbose")
        self.assertIn("Create:", detailed)
        self.menu("\x04", ok=False)
        self.assertEqual(before, snapshot(self.base))
        result = self.cli(ok=False)
        self.assertIn("needs a terminal", result.stderr)

    def test_menu_rejects_unconfirmed_current_directory_without_writes(self):
        before = snapshot(self.base)
        for answer in ("n\n", "\n"):
            with self.subTest(answer=answer):
                output = self.menu("2\n" + answer)
                self.assertIn(str(self.project), output)
                self.assertIn("Run the installer from the intended project directory.", output)
                self.assertNotIn("Choose a profile", output)
        self.menu("2\n\x04", ok=False)
        self.assertEqual(before, snapshot(self.base))

    def test_schema1_migration_preserves_state_and_rolls_back(self):
        # Build the prior schema from static data, without keeping a Python installer.
        fixture = json.loads((ROOT / "tests/fixtures/schema1-migration.json").read_text())
        self.install()
        self.cli("init", self.project, "--profile", "nextjs")
        manifest_path = self.prefix / "stack.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["version"] = fixture["version"]
        manifest["installer"] = "tools/stack.py"
        manifest["installationFiles"] = [p for p in manifest["installationFiles"]
                                         if p not in ("tools/stack.sh", "tools/installer.jq")]
        manifest["installationFiles"].insert(0, "tools/stack.py")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        for name in ("stack.sh", "installer.jq"):
            (self.prefix / "tools" / name).unlink()
        runtime = self.prefix / "tools/stack.py"
        runtime.write_text(fixture["runtimeBytes"])
        launcher = self.bin_dir / "ai-stack"
        launcher.write_text(fixture["launcherBytes"])
        state_path = self.prefix / "installation.json"
        state = json.loads(state_path.read_text())
        state["version"] = fixture["version"]
        for name in ("stack.sh", "installer.jq"):
            state["files"].pop("package/tools/" + name)
        for key, path in (("package/stack.json", manifest_path), ("package/tools/stack.py", runtime),
                          ("bin/ai-stack", launcher)):
            state["files"][key] = {"kind": "file", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        (self.prefix / "backup.json").unlink()
        project_state = self.project / ".ai-stack/installation.json"
        state = json.loads(project_state.read_text())
        state["version"] = fixture["version"]
        project_state.write_text(json.dumps(state, indent=2) + "\n")
        (self.project / ".ai-stack/backup.json").unlink()
        records = self.project / ".ai-stack/decisions.md"
        records.write_text("# Existing decisions\nKeep the approved architecture.\n")
        expected = snapshot(self.prefix)
        old_launcher = launcher.read_bytes()
        before = snapshot(self.base)
        self.cli("install", "--dry-run")
        self.assertEqual(before, snapshot(self.base))
        self.install()
        self.assertFalse(runtime.exists())
        self.assertNotIn(b"python", launcher.read_bytes())
        self.cli("init", self.project, installed=True)
        self.assertIn("Keep the approved architecture.", records.read_text())
        self.assertEqual(json.loads(project_state.read_text())["selection"]["profile"], "nextjs")
        self.cli("rollback", self.project, installed=True)
        self.cli("rollback", "--global", installed=True)
        self.assertEqual(expected, snapshot(self.prefix))
        self.assertEqual(old_launcher, launcher.read_bytes())

    def test_missing_jq_reports_requirement_without_writes(self):
        # The dependency probe must happen before creating installation destinations.
        folder = self.base / "limited-path"
        folder.mkdir()
        bash = shutil.which("bash")
        before = snapshot(self.base)
        result = subprocess.run([bash, str(self.source / "tools/stack.sh"), "install", *self.options],
                                env={**os.environ, "PATH": str(folder)}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Required command is missing: jq", result.stderr)
        self.assertEqual(before, snapshot(self.base))

    def test_profile_cycles_and_lexical_symlinks_block_all_writes(self):
        self.install()
        profile = self.source / "profiles/react.json"
        value = json.loads(profile.read_text())
        value["extends"] = ["nextjs"]
        profile.write_text(json.dumps(value))
        before = snapshot(self.base)
        self.cli("init", self.project, "--profile", "nextjs", ok=False)
        self.assertEqual(before, snapshot(self.base))
        alias = self.base / "alias"
        alias.symlink_to(self.project)
        self.cli("init", str(alias) + "/../project", ok=False)

    def test_install_and_launcher_work_without_python_and_with_literal_shell_paths(self):
        commands = tempfile.TemporaryDirectory(prefix="ai-stack-bash-path-")
        self.addCleanup(commands.cleanup)
        for name in ("bash", "env", "jq", "realpath", "sha256sum", "base64", "mktemp", "cp", "mv",
                     "chmod", "mkdir", "rm", "find", "sort", "cmp", "awk", "cat", "dirname"):
            Path(commands.name, name).symlink_to(shutil.which(name))
        self.assertIsNone(shutil.which("python3", path=commands.name))
        env = {**os.environ, "PATH": commands.name}
        self.prefix = self.base / "package ' $() `literal`"
        self.options[1] = str(self.prefix)
        self.cli("install", env=env)
        shutil.rmtree(self.source)
        self.cli("init", self.project, "--profile", "nextjs", installed=True, env=env)
        self.cli("status", "--global", installed=True, env=env)

    def test_interrupted_first_profile_init_uses_backup_selection(self):
        self.install()
        env = self.write_fault_environment(self.project / ".ai-stack/installation.json", "interrupt")
        result = subprocess.run(["bash", str(self.source / "tools/stack.sh"), "init", str(self.project),
                                 "--profile", "nestjs", *self.options], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, -9, result.stdout + result.stderr)
        self.assertFalse((self.project / ".ai-stack/installation.json").exists())
        self.cli("rollback", self.project)
        self.assertFalse((self.project / ".agents/skills/nestjs-best-practices/SKILL.md").exists())
        self.assertTrue((self.project / ".ai-stack/decisions.md").exists())

    def test_malformed_catalog_lists_are_rejected_before_writes(self):
        path = self.source / "stack.json"
        original = json.loads(path.read_text())
        for key, value in (("installationFiles", None), ("globalSkills", "wrong"),
                           ("projectAgents", {}), ("profiles", ["../outside.json"])):
            with self.subTest(field=key):
                path.write_text(json.dumps({**original, key: value}))
                before = snapshot(self.base)
                result = self.cli("install", ok=False)
                self.assertIn("Invalid installation manifest", result.stderr)
                self.assertEqual(before, snapshot(self.base))

class TerminalPresentationTests(unittest.TestCase):
    def terminal(self, answers="0\n", **overrides):
        master, slave = pty.openpty()
        env = {key: value for key, value in os.environ.items() if key != "NO_COLOR"}
        env.update(TERM="xterm-256color", COLUMNS="72")
        env.update(overrides)
        process = subprocess.Popen(["bash", str(ROOT / "tools/stack.sh")], stdin=slave,
                                   stdout=slave, stderr=slave, env=env)
        os.close(slave)
        chunks = []
        deadline = time.monotonic() + 30
        try:
            os.write(master, answers.encode())
            while time.monotonic() < deadline:
                ready, _, _ = select.select([master], [], [], 1)
                if not ready:
                    if process.poll() is not None:
                        break
                    continue
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
            self.assertEqual(process.wait(timeout=2), 0)
            return b"".join(chunks).decode()
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            os.close(master)

    def test_color_respects_terminal_capabilities_and_no_color(self):
        self.assertIn("\x1b[36m", self.terminal())
        self.assertNotIn("\x1b[", self.terminal(NO_COLOR=""))
        self.assertNotIn("\x1b[", self.terminal(TERM="dumb"))

    def test_narrow_profile_menu_wraps_and_preserves_readable_options(self):
        output = self.terminal("2\ny\n0\n", COLUMNS="32", NO_COLOR="1")
        self.assertIn("[3] React", output)
        self.assertIn("[4] Next.js", output)
        for line in output.splitlines():
            self.assertLessEqual(len(line), 32, line)

if __name__ == "__main__":
    unittest.main()

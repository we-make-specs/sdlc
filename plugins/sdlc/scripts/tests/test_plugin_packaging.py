import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def read_json(path):
    return json.loads(path.read_text())


class PluginPackagingTests(unittest.TestCase):
    def test_marketplace_and_root_instruction_mirrors_match(self):
        for left, right in [
            (".claude-plugin/marketplace.json", ".github/plugin/marketplace.json"),
            ("AGENTS.md", "CLAUDE.md"),
        ]:
            with self.subTest(left=left):
                self.assertEqual((ROOT / left).read_bytes(), (ROOT / right).read_bytes())

    def test_catalogs_resolve_the_same_plugins(self):
        mirrored = read_json(ROOT / ".claude-plugin/marketplace.json")["plugins"]
        native = read_json(ROOT / ".agents/plugins/marketplace.json")["plugins"]
        mirrored_by_name = {entry["name"]: entry for entry in mirrored}
        native_by_name = {entry["name"]: entry for entry in native}
        self.assertEqual(len(mirrored), len(mirrored_by_name))
        self.assertEqual(len(native), len(native_by_name))
        self.assertEqual(mirrored_by_name.keys(), native_by_name.keys())
        self.assertEqual(set(mirrored_by_name), {p.name for p in (ROOT / "plugins").iterdir() if p.is_dir()})
        for name, entry in mirrored_by_name.items():
            with self.subTest(plugin=name):
                source = native_by_name[name]["source"]
                self.assertEqual(source["source"], "local")
                path = (ROOT / entry["source"]).resolve()
                self.assertEqual(path, (ROOT / source["path"]).resolve())
                self.assertEqual(path, ROOT / "plugins" / name)
                manifest = read_json(path / ".codex-plugin/plugin.json")
                self.assertEqual(entry["version"], manifest["version"])
                self.assertEqual(entry["description"], manifest["description"])

    def test_plugin_manifests_share_identity_and_release(self):
        for plugin in (ROOT / "plugins").iterdir():
            if not plugin.is_dir():
                continue
            with self.subTest(plugin=plugin.name):
                left = plugin / ".claude-plugin/plugin.json"
                right = plugin / ".github/plugin/plugin.json"
                self.assertEqual(left.read_bytes(), right.read_bytes())
                mirrored = read_json(left)
                native = read_json(plugin / ".codex-plugin/plugin.json")
                for key in ["name", "version", "description"]:
                    self.assertEqual(mirrored[key], native[key])
                self.assertEqual(native["name"], plugin.name)
                self.assertRegex(native["version"], r"^\d+\.\d+\.\d+$")
                self.assertNotIn("skills", mirrored)
                self.assertEqual(native["skills"], "./skills/")
                self.assertTrue((plugin / native["skills"]).is_dir())

    def test_shared_skills_match_their_package(self):
        forbidden = {"context", "agent", "model", "allowed-tools", "effort"}
        for skill in (ROOT / "plugins").glob("*/skills/*/SKILL.md"):
            with self.subTest(skill=skill.relative_to(ROOT)):
                text = skill.read_text()
                self.assertTrue(text.startswith("---\n"))
                frontmatter = text.split("---", 2)[1]
                self.assertRegex(frontmatter, rf"(?m)^name: {re.escape(skill.parent.name)}$")
                self.assertRegex(frontmatter, r"(?m)^description: \S")
                keys = set(re.findall(r"(?m)^([\w-]+):", frontmatter))
                self.assertFalse(keys & forbidden)
                version = re.search(r"(?m)^  version: ['\"]([^'\"]+)['\"]$", frontmatter)
                self.assertIsNotNone(version)
                manifest = read_json(skill.parents[2] / ".codex-plugin/plugin.json")
                self.assertEqual(version.group(1), manifest["version"])
                self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", text)

    def test_optional_runner_profiles_share_the_same_body(self):
        paths = [".claude/agents/sdlc-step.md", ".github/agents/sdlc-step.agent.md"]
        bodies = []
        for path in paths:
            text = (ROOT / path).read_text()
            body = text.split("---", 2)[2]
            bodies.append(re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip())
        self.assertEqual(*bodies)

    def test_namespaced_commands_cover_shared_skills(self):
        for plugin in (ROOT / "plugins").iterdir():
            if not plugin.is_dir():
                continue
            skills = {skill.parent.name: skill for skill in (plugin / "skills").glob("*/SKILL.md")}
            commands = {command.stem: command for command in (plugin / "commands").glob("*.md")}
            with self.subTest(plugin=plugin.name):
                self.assertEqual(commands.keys(), skills.keys())
            for name, command in commands.items():
                with self.subTest(command=command.relative_to(ROOT)):
                    text = command.read_text()
                    self.assertTrue(text.startswith("---\n"))
                    frontmatter, body = text.split("---", 2)[1:]
                    command_name = f"{plugin.name}:{name}"
                    self.assertRegex(frontmatter, rf"(?m)^name: {re.escape(command_name)}$")
                    self.assertLessEqual(len(command_name), 64)
                    self.assertRegex(frontmatter, r"(?m)^description: \S")
                    targets = re.findall(r"\]\(([^)]+/SKILL\.md)\)", body)
                    self.assertEqual(len(targets), 1)
                    self.assertEqual((command.parent / targets[0]).resolve(), skills[name].resolve())
                    self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", text)


if __name__ == "__main__":
    unittest.main()

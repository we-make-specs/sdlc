import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_validate_decision_manifest import approved_source, valid_manifest


MODULE_PATH = Path(__file__).parents[1] / "record_approval_hashes.py"
SPEC = importlib.util.spec_from_file_location("record_approval_hashes", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ApprovalHashRecordingTest(unittest.TestCase):
    def make_workspace(self, folder):
        for name in ("03-agreement.spec.md", "03-target-solution.spec.md", "03-test-scenarios.spec.md"):
            (folder / name).write_text(approved_source(name), encoding="utf-8")
        manifest = folder / "03-decision-manifest.state.json"
        data = valid_manifest()
        data["semanticChanges"] = [{
            "id": "SC-1", "discoveredAt": "ALIGNMENT", "summary": "Keep the export contract.",
            "affectedDecisionIds": ["D-1"], "affectedRuleIds": [],
            "riskClass": "HUMAN_REQUIRED", "status": "ACCEPTED", "decisionId": "D-1",
        }]
        data["coverage"]["semanticChanges"] = {"total": 1, "classified": 1}
        data["activeSemanticChangeIds"] = ["SC-1"]
        manifest.write_text(json.dumps(data), encoding="utf-8")
        for name in ("03-target-solution.view.html", "03-human-decision-gate.view.md", "03-human-decision-gate.view.html"):
            (folder / name).write_text("Previous view.\n", encoding="utf-8")
        return manifest

    def test_records_all_human_artifact_hashes_and_decision_content(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            manifest = self.make_workspace(folder)
            original = json.loads(manifest.read_text())
            hashes = MODULE.record_hashes(manifest)
            saved = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(hashes, saved["approval"]["artifactHashes"])
            self.assertTrue(all(len(value) == 64 for value in hashes.values()))
            self.assertTrue((folder / "03-target-solution.view.html").is_file())
            self.assertTrue((folder / "03-human-decision-gate.view.html").is_file())
            self.assertTrue((folder / "03-human-decision-gate.view.md").is_file())
            self.assertEqual([], saved["activeSemanticChangeIds"])
            self.assertEqual(original["semanticChanges"], saved["semanticChanges"])
            self.assertEqual(hashes["decisionContent"], MODULE.decision_content_hash(saved))
            from validate_decision_manifest import validate_decision_manifest
            self.assertEqual([], validate_decision_manifest(saved, "downstream", folder))

    def test_approval_writes_exact_utf8_bytes_with_windows_newline_translation(self):
        original_fdopen = MODULE.os.fdopen

        def windows_fdopen(descriptor, mode, **options):
            if "b" not in mode:
                options.setdefault("newline", "\r\n")
            return original_fdopen(descriptor, mode, **options)

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            manifest = self.make_workspace(folder)
            with patch.object(MODULE.os, "fdopen", side_effect=windows_fdopen):
                hashes = MODULE.record_hashes(manifest)
            stored = (folder / "03-target-solution.view.html").read_bytes()
            self.assertNotIn(b"\r\n", stored)
            self.assertEqual(hashes["targetSolutionView"], hashlib.sha256(stored).hexdigest())
            saved = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual([], MODULE.validate_decision_manifest(saved, "downstream", folder))

    def test_repeated_recording_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            manifest = self.make_workspace(folder)
            first_hashes = MODULE.record_hashes(manifest)
            first_files = {path.name: path.read_bytes() for path in folder.iterdir()}
            self.assertEqual(first_hashes, MODULE.record_hashes(manifest))
            self.assertEqual(first_files, {path.name: path.read_bytes() for path in folder.iterdir()})

    def test_header_errors_do_not_hash_or_change_any_file(self):
        mutations = (
            lambda text: text.replace("Status:** APPROVED", "Status:** IN REVIEW"),
            lambda text: text.replace("human@example", "different-reviewer"),
            lambda text: text.replace("2026-01-01", "2025-12-31"),
            lambda text: text.replace("- **Status:**", "- **Previous status:**"),
            lambda text: text.replace("## Design", "- **Status:** APPROVED\n\n## Design"),
        )
        for name in ("03-target-solution.spec.md", "03-test-scenarios.spec.md"):
            for index, mutate in enumerate(mutations):
                with self.subTest(name=name, mutation=index), tempfile.TemporaryDirectory() as temp:
                    folder = Path(temp)
                    manifest = self.make_workspace(folder)
                    source = folder / name
                    source.write_text(mutate(source.read_text()), encoding="utf-8")
                    before = {path.name: path.read_bytes() for path in folder.iterdir()}
                    with patch.object(MODULE, "atomic_write") as write, patch.object(MODULE.hashlib, "sha256") as hash_bytes:
                        with self.assertRaisesRegex(ValueError, "current header"):
                            MODULE.record_hashes(manifest)
                        write.assert_not_called()
                        hash_bytes.assert_not_called()
                    self.assertEqual(before, {path.name: path.read_bytes() for path in folder.iterdir()})

    def test_missing_approval_identity_does_not_change_files(self):
        for field in ("approvedBy", "approvedAt"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                manifest = self.make_workspace(folder)
                data = json.loads(manifest.read_text())
                data["approval"][field] = None
                manifest.write_text(json.dumps(data), encoding="utf-8")
                with patch.object(MODULE, "atomic_write") as write:
                    with self.assertRaisesRegex(ValueError, f"approval.{field} is required"):
                        MODULE.record_hashes(manifest)
                    write.assert_not_called()

    def test_missing_source_does_not_replace_an_existing_view(self):
        for name in ("03-agreement.spec.md", "03-target-solution.spec.md", "03-test-scenarios.spec.md"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                manifest = self.make_workspace(folder)
                (folder / name).unlink()
                before = {path.name: path.read_bytes() for path in folder.iterdir()}
                with self.assertRaises(OSError):
                    MODULE.record_hashes(manifest)
                self.assertEqual(before, {path.name: path.read_bytes() for path in folder.iterdir()})

    def test_late_render_failure_leaves_all_files_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            manifest = self.make_workspace(folder)
            before = {path.name: path.read_bytes() for path in folder.iterdir()}
            with patch.object(MODULE, "render_gate_html", side_effect=ValueError("Invalid view")):
                with self.assertRaisesRegex(ValueError, "Invalid view"):
                    MODULE.record_hashes(manifest)
            self.assertEqual(before, {path.name: path.read_bytes() for path in folder.iterdir()})

    def test_pending_human_change_cannot_be_closed_by_recording(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            manifest = self.make_workspace(folder)
            data = json.loads(manifest.read_text())
            data["semanticChanges"][0]["status"] = "NEEDS_HUMAN_DECISION"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            before = {path.name: path.read_bytes() for path in folder.iterdir()}
            with self.assertRaisesRegex(ValueError, "SC-1 needs a human decision"):
                MODULE.record_hashes(manifest)
            self.assertEqual(before, {path.name: path.read_bytes() for path in folder.iterdir()})

    def test_unconfirmed_scenario_leaves_all_files_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            manifest = self.make_workspace(folder)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            scenario = data["testScenarios"][0]
            scenario["status"] = "PROPOSED"
            data["coverage"]["testScenarios"]["classified"] -= 1
            manifest.write_text(json.dumps(data), encoding="utf-8")
            before = {path.name: path.read_bytes() for path in folder.iterdir()}
            with self.assertRaisesRegex(ValueError, f"test scenario {scenario['id']} is not human-confirmed"):
                MODULE.record_hashes(manifest)
            self.assertEqual(before, {path.name: path.read_bytes() for path in folder.iterdir()})

    def test_refuses_to_hash_an_unapproved_design(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "03-decision-manifest.state.json"
            manifest.write_text(json.dumps({"approval": {"status": "DRAFT"}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "APPROVED"):
                MODULE.record_hashes(manifest)


if __name__ == "__main__":
    unittest.main()

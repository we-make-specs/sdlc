import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "record_approval_hashes.py"
SPEC = importlib.util.spec_from_file_location("record_approval_hashes", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ApprovalHashRecordingTest(unittest.TestCase):
    def test_records_all_human_artifact_hashes_and_decision_content(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for name in ("03-agreement.spec.md", "03-target-solution.spec.md", "03-test-scenarios.spec.md"):
                (folder / name).write_text(f"# {name}\n", encoding="utf-8")
            manifest = folder / "03-decision-manifest.state.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schemaVersion": 2,
                        "ticket": "TEST-1",
                        "approval": {
                            "status": "APPROVED",
                            "artifactHashes": {
                                "agreement": None,
                                "targetSolution": None,
                                "targetSolutionView": None,
                                "testScenarios": None,
                                "decisionContent": None,
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            hashes = MODULE.record_hashes(manifest)
            saved = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(hashes, saved["approval"]["artifactHashes"])
            self.assertTrue(all(len(value) == 64 for value in hashes.values()))
            self.assertTrue((folder / "03-target-solution.view.html").is_file())
            self.assertTrue((folder / "03-human-decision-gate.view.html").is_file())
            self.assertTrue((folder / "03-human-decision-gate.view.md").is_file())

    def test_refuses_to_hash_an_unapproved_design(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "03-decision-manifest.state.json"
            manifest.write_text(json.dumps({"approval": {"status": "DRAFT"}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "APPROVED"):
                MODULE.record_hashes(manifest)


if __name__ == "__main__":
    unittest.main()

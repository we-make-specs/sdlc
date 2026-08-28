import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


MIGRATE = load("migrate_state_070_to_071")
VALIDATE_DECISION = load("validate_decision_manifest")
VALIDATE_REVIEW = load("validate_review_state")


def legacy_decision():
    from test_validate_decision_manifest import valid_manifest

    data = valid_manifest()
    data["schemaVersion"] = 1
    for item in data["acceptanceCriteria"]:
        for field in ("shortMeaning", "whyItMatters", "priority"):
            item.pop(field)
    data["approval"].pop("artifactHashes")
    return data


def legacy_review():
    return {
        "schemaVersion": 1,
        "packageId": "WP-01",
        "baseline": {"baseCommit": "1111111", "implementationCommit": "2222222"},
        "contextLoaded": ["registry/article.md"],
        "acceptanceCriteria": [{"id": "AC-1", "text": "Works", "status": "MET", "evidence": ["test"]}],
        "claims": [{
            "id": "RF-1", "status": "CLOSED", "problem": "A defect", "evidence": ["A.java:1"],
            "objective": {"kind": "APPROVED_DESIGN", "reference": "design:1", "claim": "Keep behavior"},
            "supportingSources": [], "conflictingSources": [], "severity": "HIGH", "confidence": "HIGH",
            "blastRadius": ["SECURITY"], "failureScenario": "Unauthorized access", "verificationMethod": "security test",
            "suggestedFix": "fix", "adjudication": {
                "disposition": "ACCEPT", "rationale": "Reproduced", "alternatives": [
                    {"kind": "PRESERVE_BASELINE", "description": "keep", "tradeoffs": "Defect remains"},
                    {"kind": "REVIEWER_SUGGESTION", "description": "fix", "tradeoffs": "Needs proof"},
                    {"kind": "ALTERNATIVE", "description": "other", "tradeoffs": "More work"},
                ], "conflictResolution": None, "decisionId": None,
            },
            "candidate": {"commit": "3333333", "comparison": "BETTER", "defectRemovedEvidence": ["old"],
                          "invariantChecks": ["old"], "regressionChecks": ["old"]},
        }],
        "verdict": "APPROVE", "finalCommit": "3333333",
    }


class StateMigrationTest(unittest.TestCase):
    def test_decision_migration_reopens_approval_and_passes_alignment(self):
        migrated, kind = MIGRATE.migrate(legacy_decision())
        self.assertEqual("decision", kind)
        self.assertEqual("REOPENED", migrated["approval"]["status"])
        self.assertEqual("IMPORTANT", migrated["acceptanceCriteria"][0]["priority"])
        self.assertEqual([], VALIDATE_DECISION.validate_decision_manifest(migrated, "alignment"))

    def test_review_migration_resumes_before_building_one_combined_trial(self):
        migrated, kind = MIGRATE.migrate(legacy_review())
        self.assertEqual("review", kind)
        self.assertEqual("IN_REVIEW", migrated["verdict"])
        self.assertEqual("FULL", migrated["trialFixes"][0]["path"])
        self.assertIsNone(migrated["trialFixes"][0]["commit"])
        self.assertEqual([], VALIDATE_REVIEW.validate_review_state(migrated, "checked"))

    def test_unchecked_legacy_claim_resumes_at_findings_without_inventing_a_result(self):
        legacy = legacy_review()
        legacy["claims"][0]["status"] = "OPEN"
        legacy["claims"][0]["adjudication"] = None
        legacy["claims"][0]["candidate"] = None
        legacy["verdict"] = "IN_REVIEW"
        legacy["finalCommit"] = None
        migrated, _ = MIGRATE.migrate(legacy)
        self.assertIsNone(migrated["findings"][0]["evidenceCheck"])
        self.assertEqual([], migrated["trialFixes"])
        self.assertEqual([], VALIDATE_REVIEW.validate_review_state(migrated, "findings"))

    def test_file_migration_preserves_exact_backup(self):
        original = legacy_review()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "07-review-WP-01.state.json"
            path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
            before = path.read_bytes()
            self.assertEqual("review", MIGRATE.migrate_file(path))
            backup = path.with_name("07-review-WP-01.state.v0.7.0.json")
            self.assertEqual(before, backup.read_bytes())
            self.assertEqual(2, json.loads(path.read_text())["schemaVersion"])

    def test_reconcile_restores_exact_ac_wording_and_missing_coverage(self):
        decision, _ = MIGRATE.migrate(legacy_decision())
        review, _ = MIGRATE.migrate(legacy_review())
        review["acceptanceCriteria"][0]["text"] = "Drifted wording"
        decision["acceptanceCriteria"].append({
            "id": "AC-2", "text": "Second exact promise", "shortMeaning": "Second exact promise",
            "whyItMatters": "Required", "priority": "IMPORTANT", "decisionIds": [], "status": "MAPPED",
        })
        decision["packageAcceptanceCriteria"][0]["acceptanceCriterionIds"].append("AC-2")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "07-review-WP-01.state.json"
            path.write_text(json.dumps(review), encoding="utf-8")
            MIGRATE.reconcile_review_with_decision(path, decision)
            saved = json.loads(path.read_text())
            self.assertEqual("The export is authorized.", saved["acceptanceCriteria"][0]["text"])
            self.assertEqual("Second exact promise", saved["acceptanceCriteria"][1]["text"])
            self.assertEqual("NOT_VERIFIABLE", saved["acceptanceCriteria"][1]["status"])


if __name__ == "__main__":
    unittest.main()

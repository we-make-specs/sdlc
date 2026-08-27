import copy
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "validate_review_state.py"
SPEC = importlib.util.spec_from_file_location("validate_review_state", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def source(kind="APPROVED_DESIGN"):
    return {"kind": kind, "reference": "design:10", "claim": "Use the shared pattern"}


def base_state():
    return {
        "schemaVersion": 1,
        "packageId": "WP-01",
        "baseline": {"baseCommit": "1111111", "implementationCommit": "2222222"},
        "contextLoaded": ["registry/article.md"],
        "claims": [
            {
                "id": "RF-1",
                "status": "OPEN",
                "problem": "Wrong-role behavior conflicts with the approved pattern",
                "evidence": ["Controller.java:25"],
                "objective": source("ACCEPTANCE_CRITERION"),
                "supportingSources": [source("ACCEPTANCE_CRITERION")],
                "conflictingSources": [source("APPROVED_DESIGN")],
                "severity": "HIGH",
                "confidence": "HIGH",
                "blastRadius": ["SECURITY"],
                "failureScenario": "A wrong-role caller receives a different status",
                "verificationMethod": "Run the real HTTP security test",
                "suggestedFix": "Add a manual role check",
                "adjudication": None,
                "candidate": None,
            }
        ],
        "verdict": "IN_REVIEW",
        "finalCommit": None,
    }


class ReviewStateValidationTest(unittest.TestCase):
    def test_claims_phase_accepts_claims_but_not_commands(self):
        self.assertEqual([], MODULE.validate_review_state(base_state(), "claims"))

    def test_closed_phase_rejects_unadjudicated_mutation(self):
        state = base_state()
        state["verdict"] = "APPROVE"
        state["finalCommit"] = "3333333"
        errors = MODULE.validate_review_state(state, "closed")
        self.assertTrue(any("adjudication is required" in error for error in errors))

    def test_escalation_preserves_baseline(self):
        state = base_state()
        claim = state["claims"][0]
        claim["status"] = "CLOSED"
        claim["adjudication"] = {
            "disposition": "ESCALATE",
            "rationale": "The sources encode different external behavior",
            "alternatives": [
                {"kind": "PRESERVE_BASELINE", "description": "Keep annotation", "tradeoffs": "403 remains"},
                {"kind": "REVIEWER_SUGGESTION", "description": "Manual 401", "tradeoffs": "Custom security"},
                {"kind": "ALTERNATIVE", "description": "Amend AC", "tradeoffs": "Needs decision"},
            ],
            "conflictResolution": None,
            "decisionId": "DEC-SEC-1",
        }
        state["verdict"] = "ESCALATED"
        self.assertEqual([], MODULE.validate_review_state(state, "closed"))

    def test_risky_candidate_needs_semantic_comparison(self):
        state = base_state()
        claim = state["claims"][0]
        claim["status"] = "CLOSED"
        claim["adjudication"] = {
            "disposition": "REFRAME",
            "rationale": "The AC is real but the suggested fix is unsafe",
            "alternatives": [
                {"kind": "PRESERVE_BASELINE", "description": "Keep annotation", "tradeoffs": "AC mismatch"},
                {"kind": "REVIEWER_SUGGESTION", "description": "Manual 401", "tradeoffs": "Pattern drift"},
                {"kind": "ALTERNATIVE", "description": "Amend contract", "tradeoffs": "Explicit change"},
            ],
            "conflictResolution": "Repository security convention outweighs inferred status wording",
            "decisionId": None,
        }
        claim["candidate"] = {
            "commit": "3333333",
            "comparison": "BETTER",
            "defectRemovedEvidence": ["HTTP test passes"],
            "invariantChecks": ["tests pass"],
            "regressionChecks": ["existing tests pass"],
        }
        state["verdict"] = "APPROVE"
        state["finalCommit"] = "3333333"
        errors = MODULE.validate_review_state(state, "closed")
        self.assertTrue(any("semantic invariant" in error for error in errors))
        claim["candidate"]["invariantChecks"].append("Security semantic behavior matches approved design")
        self.assertEqual([], MODULE.validate_review_state(state, "closed"))


if __name__ == "__main__":
    unittest.main()

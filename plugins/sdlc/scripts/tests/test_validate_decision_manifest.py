import copy
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "validate_decision_manifest.py"
SPEC = importlib.util.spec_from_file_location("validate_decision_manifest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def valid_manifest():
    return {
        "schemaVersion": 1,
        "ticket": "TEST-1",
        "contextLoaded": ["example-registry"],
        "acceptanceCriteria": [
            {"id": "AC-1", "text": "The export is authorized.", "decisionIds": ["D-1"], "status": "MAPPED"}
        ],
        "decisions": [
            {
                "id": "D-1",
                "title": "Authorization contract",
                "question": "Which authorization behavior is externally required?",
                "riskClass": "HUMAN_REQUIRED",
                "riskDimensions": ["SECURITY", "PUBLIC_CONTRACT"],
                "options": [
                    {"id": "A", "label": "Framework", "consequence": "Uses the established framework contract."},
                    {"id": "B", "label": "Custom", "consequence": "Introduces a feature-specific contract."},
                ],
                "recommendation": {
                    "optionId": "A",
                    "rationale": "It follows the verified boundary.",
                    "confidence": "HIGH",
                    "counterargument": "The ticket could require a different external status.",
                },
                "sources": [
                    {
                        "kind": "REGISTRY",
                        "reference": "security/authorization.md#rule-2",
                        "claim": "Use annotation-based authorization.",
                        "authority": "BINDING",
                    }
                ],
                "applicableRuleIds": ["R-1"],
                "conflicts": [],
                "status": "RESOLVED",
                "resolution": {
                    "optionId": "A",
                    "decidedBy": "human@example",
                    "decidedAt": "2026-01-01",
                    "rationale": "Preserve the established security boundary.",
                },
            }
        ],
        "applicableRules": [
            {
                "id": "R-1",
                "registry": "example-registry",
                "article": "security/authorization.md",
                "exactRule": "Use annotation-based authorization.",
                "classification": "BINDING",
                "appliesTo": "HTTP entry points",
                "affectedDecisionIds": ["D-1"],
                "affectedPaths": ["src/Controller.java"],
                "evidence": "The target changes an HTTP entry point.",
                "status": "CONFORMING",
                "rationale": "The approved option uses the annotation.",
                "deviationDecisionId": None,
            }
        ],
        "semanticChanges": [],
        "feedbackBatches": [
            {
                "id": "FB-1",
                "source": "alignment annotation pass 1",
                "expectedItems": 2,
                "processedItems": 2,
                "status": "COMPLETE",
                "unresolvedItems": [],
            }
        ],
        "coverage": {
            "acceptanceCriteria": {"total": 1, "classified": 1},
            "applicableRules": {"total": 1, "classified": 1},
            "semanticChanges": {"total": 0, "classified": 0},
        },
        "approval": {
            "status": "APPROVED",
            "approvedBy": "human@example",
            "approvedAt": "2026-01-01",
            "approvedDecisionIds": ["D-1"],
        },
    }


class DecisionManifestValidationTest(unittest.TestCase):
    def test_valid_approved_manifest_passes(self):
        self.assertEqual([], MODULE.validate_decision_manifest(valid_manifest(), "approved"))

    def test_todo_article_cannot_be_binding(self):
        data = valid_manifest()
        data["applicableRules"][0]["article"] = "guidelines/_todo_mapping.md"
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("_todo_ article must be MISSING" in error for error in errors))

    def test_high_risk_decision_cannot_be_agent_owned(self):
        data = valid_manifest()
        data["decisions"][0]["riskClass"] = "AGENT_OWNED"
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("must be HUMAN_REQUIRED" in error for error in errors))

    def test_open_authority_conflict_blocks_approval(self):
        data = valid_manifest()
        data["decisions"][0]["conflicts"] = [
            {
                "betweenReferences": ["AC-1", "security/authorization.md#rule-2"],
                "issue": "The external status and framework behavior disagree.",
                "consequence": "Choosing either changes a public security contract.",
                "status": "OPEN",
                "resolution": None,
            }
        ]
        errors = MODULE.validate_decision_manifest(data, "approved")
        self.assertTrue(any("open source conflict" in error for error in errors))

    def test_new_semantic_change_reopens_downstream_gate(self):
        data = valid_manifest()
        data["semanticChanges"] = [
            {
                "id": "SC-1",
                "discoveredAt": "PLANNING",
                "summary": "The approved mapper conflicts with a binding generated-mapper rule.",
                "affectedDecisionIds": ["D-1"],
                "affectedRuleIds": ["R-1"],
                "riskClass": "HUMAN_REQUIRED",
                "status": "NEEDS_HUMAN_DECISION",
                "decisionId": "D-1",
            }
        ]
        data["coverage"]["semanticChanges"] = {"total": 1, "classified": 0}
        data["approval"]["status"] = "REOPENED"
        errors = MODULE.validate_decision_manifest(data, "downstream")
        self.assertTrue(any("needs a human decision" in error for error in errors))
        self.assertTrue(any("approval.status must be APPROVED" in error for error in errors))

    def test_rule_deviation_needs_resolved_human_decision(self):
        data = valid_manifest()
        data["decisions"][0]["riskClass"] = "SAMPLED"
        data["applicableRules"][0]["status"] = "DEVIATION_APPROVED"
        data["applicableRules"][0]["deviationDecisionId"] = "D-1"
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("resolved human decision" in error for error in errors))

    def test_coverage_is_derived_not_self_asserted(self):
        data = copy.deepcopy(valid_manifest())
        data["coverage"]["applicableRules"]["classified"] = 0
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("coverage.applicableRules.classified" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

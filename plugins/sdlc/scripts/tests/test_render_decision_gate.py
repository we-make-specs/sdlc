import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "render_decision_gate.py"
SPEC = importlib.util.spec_from_file_location("render_decision_gate", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def manifest():
    base_source = {
        "kind": "USER",
        "reference": "alignment",
        "claim": "The human owns the public contract.",
        "authority": "BINDING",
    }
    return {
        "schemaVersion": 1,
        "ticket": "TEST-1",
        "contextLoaded": ["registry"],
        "acceptanceCriteria": [
            {"id": "AC-1", "text": "Return <safe> output.", "decisionIds": ["D-2"], "status": "MAPPED"}
        ],
        "testScenarios": [
            {"id": "TS-1", "title": "Safe output", "behavior": "The caller receives safe output.", "decisionIds": ["D-2"], "status": "PROPOSED"}
        ],
        "decisions": [
            {
                "id": "D-10",
                "title": "Local name",
                "question": "Which local name?",
                "riskClass": "AGENT_OWNED",
                "riskDimensions": ["LOCAL_IMPLEMENTATION"],
                "options": [
                    {"id": "A", "label": "Clear", "consequence": "Readable."},
                    {"id": "B", "label": "Short", "consequence": "Compact."},
                ],
                "recommendation": {"optionId": "A", "rationale": "Clear.", "confidence": "HIGH", "counterargument": "Longer."},
                "sources": [base_source],
                "applicableRuleIds": [],
                "conflicts": [],
                "status": "RESOLVED",
                "resolution": {"optionId": "A", "decidedBy": "agent", "decidedAt": "2026-01-01", "rationale": "Clear."},
            },
            {
                "id": "D-2",
                "title": "Contract <script>alert(1)</script>",
                "question": "Which contract?",
                "riskClass": "HUMAN_REQUIRED",
                "riskDimensions": ["PUBLIC_CONTRACT"],
                "options": [
                    {"id": "A", "label": "Existing", "consequence": "Stable."},
                    {"id": "B", "label": "New", "consequence": "Breaking."},
                ],
                "recommendation": {"optionId": "A", "rationale": "Stable.", "confidence": "HIGH", "counterargument": "Ticket may differ."},
                "sources": [base_source],
                "applicableRuleIds": ["R-1"],
                "conflicts": [],
                "status": "OPEN",
                "resolution": None,
            },
        ],
        "applicableRules": [
            {
                "id": "R-1",
                "registry": "registry",
                "article": "api/contracts.md",
                "exactRule": "Preserve the public contract.",
                "classification": "BINDING",
                "appliesTo": "controller",
                "affectedDecisionIds": ["D-2"],
                "affectedPaths": ["src/Controller.java"],
                "evidence": "The controller is modified.",
                "status": "CONFORMING",
                "rationale": "Option A preserves it.",
                "deviationDecisionId": None,
            }
        ],
        "semanticChanges": [],
        "feedbackBatches": [],
        "coverage": {
            "acceptanceCriteria": {"total": 1, "classified": 1},
            "testScenarios": {"total": 1, "classified": 0},
            "applicableRules": {"total": 1, "classified": 1},
            "semanticChanges": {"total": 0, "classified": 0},
        },
        "approval": {"status": "DRAFT", "approvedBy": None, "approvedAt": None, "approvedDecisionIds": []},
    }


class DecisionGateRenderingTest(unittest.TestCase):
    def test_rendering_is_byte_deterministic(self):
        first = MODULE.render_html(manifest(), "alignment")
        second = MODULE.render_html(manifest(), "alignment")
        self.assertEqual(first.encode(), second.encode())

    def test_human_required_decision_is_prominent_and_agent_owned_collapsed(self):
        page = MODULE.render_html(manifest(), "alignment")
        self.assertIn("class='card critical'", page)
        self.assertIn("Verified lower-risk decisions (1)", page)
        self.assertLess(page.index("D-2"), page.index("D-10"))

    def test_html_escapes_content_and_rejects_unsafe_pr_url(self):
        page = MODULE.render_html(manifest(), "review", {"verdict": "APPROVE", "baseline": {}, "acceptanceCriteria": [], "claims": []}, "javascript:alert(1)")
        self.assertIn("Contract &lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertNotIn("href='javascript:", page)

    def test_markdown_preserves_verbatim_acceptance_criterion_safely(self):
        page = MODULE.render_markdown(manifest(), "alignment")
        self.assertIn("Return &lt;safe&gt; output.", page)
        self.assertIn("Resolve 1 human decision", page)


if __name__ == "__main__":
    unittest.main()

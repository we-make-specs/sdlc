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
        "schemaVersion": 2,
        "ticket": "TEST-1",
        "contextLoaded": ["registry"],
        "acceptanceCriteria": [
            {
                "id": "AC-1",
                "text": "Return <safe> output.",
                "shortMeaning": "Return safe output.",
                "whyItMatters": "Unsafe output harms callers.",
                "priority": "CRITICAL",
                "decisionIds": ["D-2"],
                "status": "MAPPED",
            }
        ],
        "testScenarios": [
            {"id": "TS-1", "title": "Safe output", "behavior": "The caller receives safe output.", "decisionIds": ["D-2"], "status": "PROPOSED"}
        ],
        "packageAcceptanceCriteria": [
            {"packageId": "WP-01", "acceptanceCriterionIds": ["AC-1"]}
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
        "approval": {
            "status": "DRAFT",
            "approvedBy": None,
            "approvedAt": None,
            "approvedDecisionIds": [],
            "artifactHashes": {
                "agreement": None,
                "targetSolution": None,
                "testScenarios": None,
                "decisionContent": None,
            },
        },
    }


class DecisionGateRenderingTest(unittest.TestCase):
    def test_rendering_is_byte_deterministic(self):
        first = MODULE.render_html(manifest(), "alignment")
        second = MODULE.render_html(manifest(), "alignment")
        self.assertEqual(first.encode(), second.encode())

    def test_open_human_choice_is_prominent_and_lower_risk_detail_is_counted(self):
        page = MODULE.render_html(manifest(), "alignment")
        self.assertIn("class='choice'", page)
        self.assertIn("Lower-risk decisions: 1", page)
        self.assertNotIn("D-10", page)

    def test_required_reading_starts_with_full_target_solution_and_prioritized_ac(self):
        page = MODULE.render_html(manifest(), "alignment")
        self.assertIn('href="03-target-solution.view.html"', page)
        self.assertIn("AC-1 · Critical", page)
        self.assertLess(page.index("Acceptance criteria"), page.index("Open or changed human choices"))

    def test_html_escapes_content_and_rejects_unsafe_pr_url(self):
        page = MODULE.render_html(manifest(), "review", {"verdict": "APPROVE", "baseline": {}, "findings": [], "trialFixes": []}, "javascript:alert(1)")
        self.assertIn("Contract &lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertNotIn("href='javascript:", page)

    def test_markdown_preserves_verbatim_acceptance_criterion_safely(self):
        page = MODULE.render_markdown(manifest(), "alignment")
        self.assertIn("Return &lt;safe&gt; output.", page)
        self.assertIn("Check 1 open or changed choice", page)

    def test_review_uses_plain_english_terms(self):
        review = {
            "verdict": "APPROVE",
            "baseline": {"implementationCommit": "2222222"},
            "finalCommit": "2222222",
            "selectedTrialFixId": None,
            "finalFullCheck": None,
            "acceptanceCriteria": [
                {"id": "AC-1", "status": "MET", "evidence": ["SafeOutputTest passes"]}
            ],
            "findings": [
                {
                    "id": "RF-1",
                    "problem": "Example",
                    "evidenceCheck": {"result": "NOT_A_PROBLEM", "path": "NO_CHANGE", "reason": "It follows the design."},
                }
            ],
            "trialFixes": [],
        }
        page = MODULE.render_html(manifest(), "review", review)
        self.assertIn("Not a problem", page)
        self.assertIn("Keep original", page)
        self.assertIn("Implementation result:</b> Met", page)
        self.assertIn("SafeOutputTest passes", page)
        self.assertNotIn("ADJUDICATED", page)
        self.assertNotIn("candidate", page.lower())

    def test_review_page_shows_every_live_check_and_changed_file(self):
        review = {
            "verdict": "APPROVE", "baseline": {"implementationCommit": "2222222"},
            "finalCommit": "2222222", "selectedTrialFixId": None, "finalFullCheck": None,
            "acceptanceCriteria": [], "findings": [], "trialFixes": [],
        }
        page = MODULE.render_html(
            manifest(), "review", review, "https://example.test/pr/1", "OPEN", "MERGEABLE",
            ["src/A.java", "src/B.java"], ["unit tests: FAILED", "lint: PASSED"],
        )
        for expected in ("OPEN", "MERGEABLE", "src/A.java", "src/B.java", "unit tests: FAILED", "lint: PASSED"):
            self.assertIn(expected, page)
        self.assertIn("Stop: 1 pull-request check(s) are not explicitly successful", page)
        self.assertLess(page.index("B (recommended)"), page.index("Approval is unavailable"))

    def test_check_name_containing_error_does_not_create_a_false_failure(self):
        self.assertFalse(MODULE.failed_check("error budget: PASSED"))

    def test_pending_unknown_and_malformed_checks_block(self):
        for result in ("CI: PENDING", "CI: UNKNOWN", "PASSED"):
            self.assertTrue(MODULE.failed_check(result))


if __name__ == "__main__":
    unittest.main()

import copy
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


def manifest_with_changes():
    data = manifest()
    current = data["decisions"][1]
    current["status"] = "RESOLVED"
    current["resolution"] = {
        "optionId": "A", "decidedBy": "reviewer", "decidedAt": "2026-01-02", "rationale": "Keep the contract."
    }
    historical = copy.deepcopy(current)
    historical.update(id="D-3", title="Previous contract decision")
    data["decisions"].append(historical)
    data["semanticChanges"] = [
        {
            "id": "SC-1", "discoveredAt": "ALIGNMENT", "summary": "Earlier export spelling.",
            "affectedDecisionIds": ["D-3"], "affectedRuleIds": [],
            "riskClass": "HUMAN_REQUIRED", "status": "ACCEPTED", "decisionId": "D-3",
        },
        {
            "id": "SC-2", "discoveredAt": "REVIEW", "summary": "Current export contract.",
            "affectedDecisionIds": ["D-2"], "affectedRuleIds": [],
            "riskClass": "HUMAN_REQUIRED", "status": "ACCEPTED", "decisionId": "D-2",
        },
    ]
    data["activeSemanticChangeIds"] = ["SC-2"]
    data["approval"]["status"] = "REOPENED"
    return data


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

    def test_accepted_current_changes_stay_visible_until_overall_approval(self):
        for status in ("DRAFT", "REOPENED"):
            with self.subTest(status=status):
                data = manifest_with_changes()
                data["approval"]["status"] = status
                attention, quiet = MODULE.attention_decisions(data)
                self.assertEqual(["D-2"], [item["id"] for item in attention])
                self.assertIn("D-3", [item["id"] for item in quiet])
                for render in (MODULE.render_html, MODULE.render_markdown):
                    page = render(data, "alignment")
                    current_part = page.split("Earlier semantic changes")[0]
                    self.assertIn("Current export contract.", current_part)
                    self.assertNotIn("Earlier export spelling.", current_part)
                    self.assertIn("Earlier export spelling.", page)

    def test_current_change_includes_its_governing_human_choice(self):
        data = manifest_with_changes()
        data["semanticChanges"][1]["affectedDecisionIds"] = []
        data["decisions"][1]["title"] = "Governing export decision"
        self.assertEqual(["D-2"], [item["id"] for item in MODULE.attention_decisions(data)[0]])
        for render in (MODULE.render_html, MODULE.render_markdown):
            self.assertIn(data["decisions"][1]["title"], render(data, "alignment"))

    def test_closed_scope_keeps_history_without_reopening_resolved_choices(self):
        data = manifest_with_changes()
        data["approval"]["status"] = "APPROVED"
        data["activeSemanticChangeIds"] = []
        self.assertEqual([], MODULE.attention_decisions(data)[0])
        for render in (MODULE.render_html, MODULE.render_markdown):
            page = render(data, "alignment")
            self.assertNotIn("Changes and conflicts that need attention", page)
            self.assertIn("Earlier semantic changes", page)
            self.assertIn("Earlier export spelling.", page)
            self.assertIn("Current export contract.", page)

    def test_closed_alignment_displays_recorded_approval_without_another_prompt(self):
        data = manifest_with_changes()
        data["approval"].update(status="APPROVED", approvedBy="reviewer", approvedAt="2026-01-02")
        data["activeSemanticChangeIds"] = []
        for scenario in data["testScenarios"]:
            scenario["status"] = "HUMAN_CONFIRMED"
        review = {"verdict": "APPROVE", "acceptanceCriteria": [{"id": "AC-1", "status": "MET", "evidence": []}]}
        for render in (MODULE.render_html, MODULE.render_markdown):
            alignment_page = render(data, "alignment")
            self.assertIn("Design approved by reviewer on 2026-01-02.", alignment_page)
            self.assertNotIn("I approve the target solution", alignment_page)
            self.assertNotIn("Give the explicit final decision", alignment_page)
            self.assertIn("Confirmed scenarios", alignment_page)
            review_page = render(
                data, "review", review=review, pr_state="OPEN", mergeability="MERGEABLE", checks=["CI: PASS"]
            )
            self.assertIn("I approve this package", review_page)
            self.assertNotIn("Design approved by reviewer", review_page)
            legacy = {key: value for key, value in data.items() if key != "activeSemanticChangeIds"}
            legacy_page = render(legacy, "alignment")
            self.assertIn("I approve the target solution", legacy_page)
            self.assertNotIn("Design approved by reviewer", legacy_page)

    def test_missing_scope_keeps_conservative_legacy_visibility(self):
        data = manifest_with_changes()
        del data["activeSemanticChangeIds"]
        self.assertEqual(["D-2", "D-3"], [item["id"] for item in MODULE.attention_decisions(data)[0]])
        for render in (MODULE.render_html, MODULE.render_markdown):
            page = render(data, "alignment")
            self.assertIn("Changes and conflicts that need attention", page)
            self.assertNotIn("Earlier semantic changes", page)
            self.assertIn("Earlier export spelling.", page)

    def test_recorded_approval_never_hides_pending_review_work(self):
        mutations = (
            lambda data: data["testScenarios"][0].update(status="PROPOSED"),
            lambda data: data["decisions"][1].update(status="OPEN"),
            lambda data: data["decisions"][1]["conflicts"].append({"status": "OPEN", "issue": "Changed input", "consequence": "Different result"}),
            lambda data: data["feedbackBatches"].append({"id": "F-1", "status": "OPEN"}),
            lambda data: data["semanticChanges"][0].update(status="NEEDS_HUMAN_DECISION", affectedDecisionIds=[], decisionId=None),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(pending=index):
                data = manifest_with_changes()
                data["approval"].update(status="APPROVED", approvedBy="reviewer", approvedAt="2026-01-02")
                data["activeSemanticChangeIds"] = []
                for scenario in data["testScenarios"]:
                    scenario["status"] = "HUMAN_CONFIRMED"
                mutate(data)
                for render in (MODULE.render_html, MODULE.render_markdown):
                    page = render(data, "alignment")
                    self.assertNotIn("Design approved by reviewer", page)
                    self.assertIn("I approve the target solution", page)

    def test_empty_scope_cannot_hide_a_pending_human_change(self):
        data = manifest_with_changes()
        data["activeSemanticChangeIds"] = []
        data["semanticChanges"][0]["status"] = "NEEDS_HUMAN_DECISION"
        attention, _ = MODULE.attention_decisions(data)
        self.assertEqual(["D-3"], [item["id"] for item in attention])
        for render in (MODULE.render_html, MODULE.render_markdown):
            page = render(data, "alignment")
            self.assertIn("Earlier export spelling.", page.split("Earlier semantic changes")[0])
            self.assertIn("Needs human choice", page)

    def test_scope_never_hides_source_conflicts_promises_or_unconfirmed_scenarios(self):
        data = manifest_with_changes()
        data["activeSemanticChangeIds"] = []
        data["decisions"][2]["conflicts"] = [{
            "status": "OPEN", "issue": "Caller expectations differ.", "consequence": "Export may break callers."
        }]
        for render in (MODULE.render_html, MODULE.render_markdown):
            page = render(data, "alignment")
            self.assertIn("1 source conflict(s)", page)
            self.assertIn("1 unconfirmed test scenario(s)", page)
            self.assertIn("Caller expectations differ.", page)
            self.assertIn("Return &lt;safe&gt; output.", page)
            self.assertIn("The caller receives safe output.", page)
            self.assertIn("03-target-solution.view.html", page)

    def test_history_is_escaped_and_includes_rejected_changes(self):
        data = manifest_with_changes()
        data["semanticChanges"][0].update(status="REJECTED", summary="Old <script>example</script>.")
        page = MODULE.render_html(data, "alignment")
        self.assertIn("Old &lt;script&gt;example&lt;/script&gt;.", page)
        self.assertNotIn("Old <script>", page)
        self.assertIn("Not accepted", page)

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

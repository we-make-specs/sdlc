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
    return {"kind": kind, "reference": "design:10", "statement": "Use the shared pattern"}


def full_check(commit="2222222", source_name="STEP_06"):
    return {
        "commit": commit,
        "command": "./gradlew test",
        "result": "PASSED",
        "completedAt": "2026-08-28T10:00:00Z",
        "source": source_name,
        "evidence": ["BUILD SUCCESSFUL"],
    }


def base_state():
    return {
        "schemaVersion": 2,
        "packageId": "WP-01",
        "baseline": {
            "baseCommit": "1111111",
            "implementationCommit": "2222222",
            "implementationFullCheck": full_check(),
        },
        "contextLoaded": ["registry/article.md"],
        "acceptanceCriteria": [
            {
                "id": "AC-1",
                "text": "Wrong-role behavior follows the agreed contract.",
                "status": "MET",
                "evidence": ["ControllerSecurityTest.java:20"],
            }
        ],
        "findings": [
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
                "impactAreas": ["SECURITY"],
                "failureScenario": "A wrong-role caller receives a different status",
                "verificationMethod": "Run the real HTTP security test",
                "suggestedFix": "Add a manual role check",
                "evidenceCheck": None,
            }
        ],
        "trialFixes": [],
        "multipleTrialFixReason": None,
        "selectedTrialFixId": None,
        "finalFullCheck": None,
        "verdict": "IN_REVIEW",
        "finalCommit": None,
    }


def decision_manifest_for(state):
    criteria = [
        {"id": item["id"], "text": item["text"]}
        for item in state["acceptanceCriteria"]
    ]
    return {
        "acceptanceCriteria": criteria,
        "packageAcceptanceCriteria": [{
            "packageId": state["packageId"],
            "acceptanceCriterionIds": [item["id"] for item in criteria],
        }],
        "decisions": [],
        "semanticChanges": [],
        "approval": {"status": "APPROVED"},
    }


def check_finding(state, *, result="PARTLY_RIGHT", path="FULL", trial_fix_id="TF-1"):
    finding = state["findings"][0]
    finding["status"] = "CHECKED"
    finding["evidenceCheck"] = {
        "result": result,
        "path": path,
        "reason": "The behavior is wrong, but the suggested mechanism is unsafe.",
        "baselineTradeoff": "Keeps the established pattern but misses the required behavior.",
        "correctionTradeoff": "Changes security behavior and therefore needs full proof." if trial_fix_id else None,
        "decisionId": None,
        "trialFixId": trial_fix_id,
    }


def add_trial(state, *, path="FULL", comparison=None, status="PLANNED", commit=None):
    state["trialFixes"] = [
        {
            "id": "TF-1",
            "findingIds": ["RF-1"],
            "path": path,
            "baseCommit": "2222222",
            "commit": commit,
            "workspaceMode": "ISOLATED_WORKTREE" if path == "FULL" else "SHARED_TRIAL_BRANCH",
            "separateReason": None,
            "status": status,
            "comparison": comparison,
            "defectRemovedEvidence": ["HTTP test passes"] if status == "CHECKED" else [],
            "invariantChecks": ["Security semantic behavior matches the approved design"] if status == "CHECKED" else [],
            "targetedChecks": ["ControllerSecurityTest passes"] if status == "CHECKED" else [],
        }
    ]


class ReviewStateValidationTest(unittest.TestCase):
    def test_findings_phase_accepts_findings_but_no_trial_fix(self):
        self.assertEqual([], MODULE.validate_review_state(base_state(), "findings"))

    def test_wrong_or_preference_finding_takes_no_change_path(self):
        state = base_state()
        finding = state["findings"][0]
        finding["status"] = "CHECKED"
        finding["evidenceCheck"] = {
            "result": "NOT_A_PROBLEM",
            "path": "NO_CHANGE",
            "reason": "The code follows the approved design.",
            "baselineTradeoff": "The reviewer preference is not adopted.",
            "correctionTradeoff": None,
            "decisionId": None,
            "trialFixId": None,
        }
        self.assertEqual([], MODULE.validate_review_state(state, "checked"))

    def test_high_impact_finding_cannot_take_light_path(self):
        state = base_state()
        check_finding(state, result="VALID", path="LIGHT")
        add_trial(state, path="LIGHT")
        errors = MODULE.validate_review_state(state, "checked")
        self.assertTrue(any("high-impact finding must use FULL" in error for error in errors))

    def test_impact_areas_cannot_be_empty(self):
        state = base_state()
        state["findings"][0]["impactAreas"] = []
        errors = MODULE.validate_review_state(state, "findings")
        self.assertTrue(any("impactAreas must be a non-empty array" in error for error in errors))

    def test_impact_areas_cannot_repeat(self):
        state = base_state()
        state["findings"][0]["impactAreas"] = ["DATA", "DATA"]
        errors = MODULE.validate_review_state(state, "findings")
        self.assertTrue(any("duplicate array item" in error for error in errors))

    def test_one_shared_trial_fix_can_cover_multiple_findings(self):
        state = base_state()
        second = copy.deepcopy(state["findings"][0])
        second["id"] = "RF-2"
        second["impactAreas"] = ["LOCAL_IMPLEMENTATION"]
        state["findings"].append(second)
        for finding in state["findings"]:
            finding["status"] = "CHECKED"
            finding["evidenceCheck"] = {
                "result": "VALID",
                "path": "FULL",
                "reason": "The issue is reproducible.",
                "baselineTradeoff": "The defect remains.",
                "correctionTradeoff": "The correction changes both coupled blocks.",
                "decisionId": None,
                "trialFixId": "TF-1",
            }
        add_trial(state)
        state["trialFixes"][0]["findingIds"] = ["RF-1", "RF-2"]
        self.assertEqual([], MODULE.validate_review_state(state, "checked"))

    def test_finding_must_be_listed_by_its_trial_fix(self):
        state = base_state()
        second = copy.deepcopy(state["findings"][0])
        second["id"] = "RF-2"
        state["findings"].append(second)
        for finding in state["findings"]:
            finding["status"] = "CHECKED"
            finding["evidenceCheck"] = {
                "result": "VALID", "path": "FULL", "reason": "Reproduced.",
                "baselineTradeoff": "Defect remains.", "correctionTradeoff": "Needs proof.",
                "decisionId": None, "trialFixId": "TF-1",
            }
        add_trial(state)
        errors = MODULE.validate_review_state(state, "checked")
        self.assertTrue(any("RF-2 is not covered by its trial fix" in error for error in errors))

    def test_multiple_trial_fixes_need_an_explicit_reason(self):
        state = base_state()
        check_finding(state)
        add_trial(state)
        second = copy.deepcopy(state["trialFixes"][0])
        second["id"] = "TF-2"
        second["findingIds"] = []
        state["trialFixes"].append(second)
        errors = MODULE.validate_review_state(state, "checked")
        self.assertTrue(any("multiple trial fixes need a reason" in error for error in errors))

    def test_human_conflict_preserves_baseline_and_stops(self):
        state = base_state()
        finding = state["findings"][0]
        finding["status"] = "CLOSED"
        finding["evidenceCheck"] = {
            "result": "ASK_HUMAN",
            "path": "HUMAN",
            "reason": "The sources require different external behavior.",
            "baselineTradeoff": "Keeps the approved design.",
            "correctionTradeoff": "Would change the security contract.",
            "decisionId": "D-SEC-1",
            "trialFixId": None,
        }
        state["verdict"] = "ASK_HUMAN"
        self.assertEqual([], MODULE.validate_review_state(state, "closed"))

    def test_human_conflict_pauses_other_valid_findings_before_trial_planning(self):
        state = base_state()
        second = copy.deepcopy(state["findings"][0])
        second["id"] = "RF-2"
        state["findings"].append(second)
        state["findings"][0]["status"] = "CLOSED"
        state["findings"][0]["evidenceCheck"] = {
            "result": "ASK_HUMAN", "path": "HUMAN", "reason": "Sources conflict.",
            "baselineTradeoff": "Preserve approved behavior.", "correctionTradeoff": "Could change security.",
            "decisionId": "D-SEC-1", "trialFixId": None,
        }
        state["findings"][1]["status"] = "CLOSED"
        state["findings"][1]["evidenceCheck"] = {
            "result": "VALID", "path": "FULL", "reason": "The local defect is real.",
            "baselineTradeoff": "The defect remains.", "correctionTradeoff": "Wait for the related human choice.",
            "decisionId": None, "trialFixId": None,
        }
        state["verdict"] = "ASK_HUMAN"
        self.assertEqual([], MODULE.validate_review_state(state, "closed"))

    def test_safe_trial_needs_semantic_check_and_one_final_full_check(self):
        state = base_state()
        check_finding(state)
        state["findings"][0]["status"] = "CLOSED"
        add_trial(state, comparison="SAFE_IMPROVEMENT", status="CHECKED", commit="3333333")
        state["trialFixes"][0]["invariantChecks"] = ["unit tests pass"]
        state["selectedTrialFixId"] = "TF-1"
        state["verdict"] = "APPROVE"
        state["finalCommit"] = "3333333"
        state["finalFullCheck"] = full_check("3333333", "REVIEW")
        errors = MODULE.validate_review_state(state, "closed")
        self.assertTrue(any("semantic invariant" in error for error in errors))
        state["trialFixes"][0]["invariantChecks"].append("Security semantic behavior matches the approved design")
        self.assertEqual([], MODULE.validate_review_state(state, "closed"))

    def test_unchanged_baseline_can_reuse_exact_step_06_full_check(self):
        state = base_state()
        finding = state["findings"][0]
        finding["status"] = "CLOSED"
        finding["evidenceCheck"] = {
            "result": "NOT_A_PROBLEM",
            "path": "NO_CHANGE",
            "reason": "The finding is not reproducible.",
            "baselineTradeoff": "No change is needed.",
            "correctionTradeoff": None,
            "decisionId": None,
            "trialFixId": None,
        }
        state["verdict"] = "APPROVE"
        state["finalCommit"] = "2222222"
        state["finalFullCheck"] = copy.deepcopy(state["baseline"]["implementationFullCheck"])
        self.assertEqual([], MODULE.validate_review_state(state, "closed"))

    def test_step_06_check_cannot_be_reused_for_a_trial_fix(self):
        state = base_state()
        check_finding(state)
        state["findings"][0]["status"] = "CLOSED"
        add_trial(state, comparison="SAFE_IMPROVEMENT", status="CHECKED", commit="3333333")
        state["selectedTrialFixId"] = "TF-1"
        state["verdict"] = "APPROVE"
        state["finalCommit"] = "3333333"
        state["finalFullCheck"] = full_check("3333333", "STEP_06")
        errors = MODULE.validate_review_state(state, "closed")
        self.assertTrue(any("unchanged baseline" in error for error in errors))

    def test_unchanged_baseline_must_not_repeat_a_passing_step_06_full_check(self):
        state = base_state()
        finding = state["findings"][0]
        finding["status"] = "CLOSED"
        finding["evidenceCheck"] = {
            "result": "NOT_A_PROBLEM",
            "path": "NO_CHANGE",
            "reason": "The finding is not reproducible.",
            "baselineTradeoff": "No change is needed.",
            "correctionTradeoff": None,
            "decisionId": None,
            "trialFixId": None,
        }
        state["verdict"] = "APPROVE"
        state["finalCommit"] = "2222222"
        state["finalFullCheck"] = full_check("2222222", "REVIEW")
        errors = MODULE.validate_review_state(state, "closed")
        self.assertTrue(any("must reuse its exact passing Step 06" in error for error in errors))

    def test_unknown_review_fields_fail_closed(self):
        state = base_state()
        state["reviewerSays"] = "change it"
        errors = MODULE.validate_review_state(state, "findings")
        self.assertTrue(any("reviewerSays: unknown field" in error for error in errors))

    def test_comment_cannot_close_with_unmet_criterion(self):
        state = base_state()
        state["findings"][0]["status"] = "CLOSED"
        state["findings"][0]["evidenceCheck"] = {
            "result": "NOT_A_PROBLEM", "path": "NO_CHANGE", "reason": "No defect.",
            "baselineTradeoff": "Keep the design.", "correctionTradeoff": None,
            "decisionId": None, "trialFixId": None,
        }
        state["acceptanceCriteria"][0]["status"] = "NOT_MET"
        state["verdict"] = "COMMENT"
        state["finalCommit"] = "2222222"
        state["finalFullCheck"] = copy.deepcopy(state["baseline"]["implementationFullCheck"])
        errors = MODULE.validate_review_state(state, "closed")
        self.assertTrue(any("APPROVE or COMMENT is invalid" in error for error in errors))

    def test_not_verifiable_cannot_be_ready(self):
        state = base_state()
        state["findings"][0]["status"] = "CLOSED"
        state["findings"][0]["evidenceCheck"] = {
            "result": "NOT_A_PROBLEM", "path": "NO_CHANGE", "reason": "No defect.",
            "baselineTradeoff": "Keep the design.", "correctionTradeoff": None,
            "decisionId": None, "trialFixId": None,
        }
        state["acceptanceCriteria"][0]["status"] = "NOT_VERIFIABLE"
        state["verdict"] = "APPROVE"
        state["finalCommit"] = "2222222"
        state["finalFullCheck"] = copy.deepcopy(state["baseline"]["implementationFullCheck"])
        errors = MODULE.validate_review_state(state, "closed")
        self.assertTrue(any("unless every acceptance criterion is MET" in error for error in errors))

    def test_review_must_cover_exact_package_criteria_and_wording(self):
        state = base_state()
        manifest = decision_manifest_for(state)
        manifest["acceptanceCriteria"].append({"id": "AC-2", "text": "Second promise"})
        manifest["packageAcceptanceCriteria"][0]["acceptanceCriterionIds"].append("AC-2")
        errors = MODULE.validate_review_state(state, "findings", manifest)
        self.assertTrue(any("must exactly match package" in error for error in errors))
        manifest["packageAcceptanceCriteria"][0]["acceptanceCriterionIds"] = ["AC-1"]
        manifest["acceptanceCriteria"][0]["text"] = "Changed wording"
        errors = MODULE.validate_review_state(state, "findings", manifest)
        self.assertTrue(any("text differs from the approved criterion" in error for error in errors))

    def test_human_finding_must_link_to_open_manifest_decision_and_review_change(self):
        state = base_state()
        finding = state["findings"][0]
        finding["status"] = "CLOSED"
        finding["evidenceCheck"] = {
            "result": "ASK_HUMAN", "path": "HUMAN", "reason": "Authority conflict.",
            "baselineTradeoff": "Preserve baseline.", "correctionTradeoff": "Could change behavior.",
            "decisionId": "D-999", "trialFixId": None,
        }
        state["verdict"] = "ASK_HUMAN"
        manifest = decision_manifest_for(state)
        manifest["approval"]["status"] = "REOPENED"
        errors = MODULE.validate_review_state(state, "closed", manifest)
        self.assertTrue(any("references unknown decision D-999" in error for error in errors))

        finding["evidenceCheck"]["decisionId"] = "D-2"
        manifest["decisions"] = [{"id": "D-2", "riskClass": "HUMAN_REQUIRED", "status": "OPEN"}]
        manifest["semanticChanges"] = [{
            "id": "SC-2", "discoveredAt": "REVIEW", "status": "NEEDS_HUMAN_DECISION", "decisionId": "D-2",
        }]
        self.assertEqual([], MODULE.validate_review_state(state, "closed", manifest))


if __name__ == "__main__":
    unittest.main()

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).parents[1] / "validate_decision_manifest.py"
SPEC = importlib.util.spec_from_file_location("validate_decision_manifest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def valid_manifest():
    data = {
        "schemaVersion": 2,
        "ticket": "TEST-1",
        "contextLoaded": ["example-registry"],
        "acceptanceCriteria": [
            {
                "id": "AC-1",
                "text": "The export is authorized.",
                "shortMeaning": "Only allowed callers can export.",
                "whyItMatters": "It protects allocation data.",
                "priority": "CRITICAL",
                "decisionIds": ["D-1"],
                "status": "MAPPED",
            }
        ],
        "testScenarios": [
            {
                "id": "TS-1",
                "title": "Authorized export",
                "behavior": "Given an authorized caller, when export runs, then the allocation is returned.",
                "decisionIds": ["D-1"],
                "status": "HUMAN_CONFIRMED",
            }
        ],
        "packageAcceptanceCriteria": [
            {"packageId": "WP-01", "acceptanceCriterionIds": ["AC-1"]}
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
            "testScenarios": {"total": 1, "classified": 1},
            "applicableRules": {"total": 1, "classified": 1},
            "semanticChanges": {"total": 0, "classified": 0},
        },
        "approval": {
            "status": "APPROVED",
            "approvedBy": "human@example",
            "approvedAt": "2026-01-01",
            "approvedDecisionIds": ["D-1"],
            "artifactHashes": {
                "agreement": "a" * 64,
                "targetSolution": "b" * 64,
                "targetSolutionView": "d" * 64,
                "testScenarios": "c" * 64,
                "decisionContent": None,
            },
        },
    }
    data["approval"]["artifactHashes"]["decisionContent"] = MODULE.decision_content_hash(data)
    return data


def approved_source(title):
    return (
        f"# {title}\n\n"
        "- **Status:** APPROVED · **Approved by:** human@example · **on:** 2026-01-01\n\n"
        "## Design\n\nThe export keeps the approved behavior.\n"
    )


def write_approved_artifacts(folder, data, overrides=None, legacy_view=False):
    sources = {
        "agreement": "03-agreement.spec.md",
        "targetSolution": "03-target-solution.spec.md",
        "testScenarios": "03-test-scenarios.spec.md",
    }
    for key, name in sources.items():
        path = folder / name
        path.write_text((overrides or {}).get(key, approved_source(key)), encoding="utf-8")
        data["approval"]["artifactHashes"][key] = MODULE.sha256_file(path)
    rendered = MODULE.render_target_solution_html((folder / sources["targetSolution"]).read_text())
    if legacy_view:
        rendered = rendered.replace("<main", '<main data-renderer="previous"', 1)
    target_view = folder / "03-target-solution.view.html"
    target_view.write_text(rendered, encoding="utf-8")
    data["approval"]["artifactHashes"]["targetSolutionView"] = MODULE.sha256_file(target_view)
    data["approval"]["artifactHashes"]["decisionContent"] = MODULE.decision_content_hash(data)
    (folder / "03-human-decision-gate.view.html").write_text(
        MODULE.render_decision_gate_html(data, "alignment"), encoding="utf-8"
    )
    (folder / "03-human-decision-gate.view.md").write_text(
        MODULE.render_decision_gate_markdown(data, "alignment"), encoding="utf-8"
    )


class DecisionManifestValidationTest(unittest.TestCase):
    def test_valid_approved_manifest_passes(self):
        self.assertEqual([], MODULE.validate_decision_manifest(valid_manifest(), "approved"))

    def test_approved_decision_content_is_hash_locked(self):
        data = valid_manifest()
        data["acceptanceCriteria"][0]["shortMeaning"] = "A different promise."
        errors = MODULE.validate_decision_manifest(data, "approved")
        self.assertTrue(any("decision content changed" in error for error in errors))

    def test_approval_identity_is_hash_locked(self):
        data = valid_manifest()
        data["approval"]["approvedBy"] = "someone-else"
        errors = MODULE.validate_decision_manifest(data, "approved")
        self.assertTrue(any("decision content changed" in error for error in errors))

    def test_approved_human_artifact_edit_is_detected(self):
        data = valid_manifest()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            files = {
                "agreement": folder / "03-agreement.spec.md",
                "targetSolution": folder / "03-target-solution.spec.md",
                "testScenarios": folder / "03-test-scenarios.spec.md",
            }
            for name, path in files.items():
                path.write_text(approved_source(name), encoding="utf-8")
                data["approval"]["artifactHashes"][name] = MODULE.sha256_file(path)
            target_view = folder / "03-target-solution.view.html"
            target_view.write_text(MODULE.render_target_solution_html(files["targetSolution"].read_text()), encoding="utf-8")
            data["approval"]["artifactHashes"]["targetSolutionView"] = MODULE.sha256_file(target_view)
            (folder / "03-human-decision-gate.view.html").write_text(
                MODULE.render_decision_gate_html(data, "alignment"), encoding="utf-8"
            )
            (folder / "03-human-decision-gate.view.md").write_text(
                MODULE.render_decision_gate_markdown(data, "alignment"), encoding="utf-8"
            )
            self.assertEqual([], MODULE.validate_decision_manifest(data, "approved", folder))
            files["targetSolution"].write_text("# changed design\n", encoding="utf-8")
            errors = MODULE.validate_decision_manifest(data, "downstream", folder)
            self.assertTrue(any("03-target-solution.spec.md" in error for error in errors))

    def test_stale_human_views_are_detected(self):
        data = valid_manifest()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            sources = {
                "agreement": folder / "03-agreement.spec.md",
                "targetSolution": folder / "03-target-solution.spec.md",
                "testScenarios": folder / "03-test-scenarios.spec.md",
            }
            for name, path in sources.items():
                path.write_text(f"# {name}\n", encoding="utf-8")
                data["approval"]["artifactHashes"][name] = MODULE.sha256_file(path)
            target_view = folder / "03-target-solution.view.html"
            target_view.write_text("<p>stale</p>", encoding="utf-8")
            data["approval"]["artifactHashes"]["targetSolutionView"] = MODULE.sha256_file(target_view)
            (folder / "03-human-decision-gate.view.html").write_text("<p>stale</p>", encoding="utf-8")
            (folder / "03-human-decision-gate.view.md").write_text("# Fake approval\n", encoding="utf-8")
            errors = MODULE.validate_decision_manifest(data, "alignment", folder)
            self.assertTrue(any("target-solution.view.html is stale" in error for error in errors))
            self.assertTrue(any("human-decision-gate.view.html is stale" in error for error in errors))
            self.assertTrue(any("human-decision-gate.view.md is stale" in error for error in errors))

    def test_approved_headers_must_match_even_when_every_hash_matches(self):
        changes = (
            ("APPROVED", "DRAFT", "status"),
            ("human@example", "another-reviewer", "approved by"),
            ("2026-01-01", "2025-12-31", "on"),
        )
        for key in ("targetSolution", "testScenarios"):
            for old, new, field in changes:
                with self.subTest(artifact=key, field=field), tempfile.TemporaryDirectory() as temp:
                    folder = Path(temp)
                    data = valid_manifest()
                    source = approved_source(key).replace(old, new)
                    write_approved_artifacts(folder, data, {key: source})
                    for phase in ("approved", "downstream"):
                        errors = MODULE.validate_decision_manifest(data, phase, folder)
                        self.assertTrue(any(f"current header {field} must match" in error for error in errors))

    def test_current_header_cannot_be_supplied_by_history_or_code_example(self):
        data = valid_manifest()
        header = approved_source("Example").split("## Design")[0]
        for source in ("# Example\n\n## Approval history\n" + header, "# Example\n\n```markdown\n" + header + "```\n"):
            with self.subTest(source=source):
                errors = MODULE.approval_header_errors(data["approval"], source, "example.spec.md")
                self.assertEqual(3, len(errors))
        errors = MODULE.approval_header_errors(
            data["approval"], header + "- **Status:** APPROVED\n", "example.spec.md"
        )
        self.assertTrue(any("exactly one status" in error for error in errors))

    def test_only_a_marker_line_closes_a_header_code_fence(self):
        approval = valid_manifest()["approval"]
        header = approved_source("Example").splitlines()[2]
        for marker in ("```", "~~~"):
            with self.subTest(marker=marker):
                example = f"# Example\n\n{marker}text\n{marker}yaml\n{header}\n{marker}\n\n"
                errors = MODULE.approval_header_errors(approval, example + "## Design\n", "example.spec.md")
                self.assertEqual(3, len(errors))
                self.assertTrue(all("current header must contain exactly one" in error for error in errors))
                source = f"{example}{header}\n\n## Design\n"
                self.assertEqual([], MODULE.approval_header_errors(approval, source, "example.spec.md"))

    def test_current_header_allows_separate_fields_and_preserves_old_amendments(self):
        source = (
            "# Example\n\n- **Status:** APPROVED\n- **Approved by:** human@example\n- **on:** 2026-01-01\n"
            '- **Amendment:** 2025-12-01, supersedes "Status: IN REVIEW | Approved by: former | on: 2025-11-01".\n'
            "\n## Approval history\n\n- **Status:** APPROVED · **Approved by:** former · **on:** 2025-11-01\n"
        )
        self.assertEqual([], MODULE.approval_header_errors(valid_manifest()["approval"], source, "example.spec.md"))

    def test_hash_locked_target_view_survives_a_renderer_update(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            data = valid_manifest()
            write_approved_artifacts(folder, data, legacy_view=True)
            with patch.object(MODULE, "render_target_solution_html", side_effect=AssertionError("must keep approved bytes")):
                for phase in ("approved", "downstream"):
                    self.assertEqual([], MODULE.validate_decision_manifest(data, phase, folder))
            errors = MODULE.validate_decision_manifest(data, "alignment", folder)
            self.assertTrue(any("target-solution.view.html is stale" in error for error in errors))

    def test_legacy_target_view_does_not_hide_changed_sources_or_approved_html(self):
        names = ("03-agreement.spec.md", "03-target-solution.spec.md", "03-test-scenarios.spec.md", "03-target-solution.view.html")
        for name in names:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                data = valid_manifest()
                write_approved_artifacts(folder, data, legacy_view=True)
                path = folder / name
                path.write_text(path.read_text() + "\nChanged content.\n", encoding="utf-8")
                errors = MODULE.validate_decision_manifest(data, "downstream", folder)
                self.assertTrue(any(f"approved artifact changed after approval: {name}" in error for error in errors))

    def test_legacy_target_view_does_not_hide_changed_decision_content(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            data = valid_manifest()
            write_approved_artifacts(folder, data, legacy_view=True)
            data["acceptanceCriteria"][0]["text"] = "A changed promise."
            errors = MODULE.validate_decision_manifest(data, "downstream", folder)
            self.assertTrue(any("approved decision content changed" in error for error in errors))
            self.assertTrue(any("target-solution.view.html is stale" in error for error in errors))

    def test_invalid_target_render_is_reported_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            data = valid_manifest()
            write_approved_artifacts(folder, data)
            with patch.object(MODULE, "render_target_solution_html", side_effect=ValueError("Invalid source preview")):
                errors = MODULE.validate_decision_manifest(data, "alignment", folder)
            self.assertTrue(any("Invalid source preview" in error for error in errors))

    def test_active_review_scope_is_optional_and_checked(self):
        data = valid_manifest()
        self.assertEqual([], MODULE.validate_decision_manifest(data, "alignment"))
        data["activeSemanticChangeIds"] = []
        self.assertEqual([], MODULE.validate_decision_manifest(data, "alignment"))
        data["activeSemanticChangeIds"] = ["SC-999", "SC-999"]
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("references unknown semantic change SC-999" in error for error in errors))
        self.assertTrue(any("must not repeat" in error for error in errors))
        data["activeSemanticChangeIds"] = "SC-1"
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("must be an array" in error for error in errors))

    def test_active_review_scope_is_hash_locked(self):
        data = valid_manifest()
        data["activeSemanticChangeIds"] = []
        errors = MODULE.validate_decision_manifest(data, "downstream")
        self.assertTrue(any("approved decision content changed" in error for error in errors))

    def test_human_required_change_cannot_bypass_decision(self):
        data = valid_manifest()
        data["semanticChanges"] = [{
            "id": "SC-1", "discoveredAt": "REVIEW", "summary": "Change public output.",
            "affectedDecisionIds": ["D-1"], "affectedRuleIds": [],
            "riskClass": "HUMAN_REQUIRED", "status": "CLASSIFIED", "decisionId": None,
        }]
        data["coverage"]["semanticChanges"] = {"total": 1, "classified": 1}
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("cannot remain merely CLASSIFIED" in error for error in errors))

    def test_empty_criteria_or_scenarios_fail_closed(self):
        data = valid_manifest()
        data["acceptanceCriteria"] = []
        data["testScenarios"] = []
        data["coverage"]["acceptanceCriteria"] = {"total": 0, "classified": 0}
        data["coverage"]["testScenarios"] = {"total": 0, "classified": 0}
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("at least one acceptance criterion" in error for error in errors))
        self.assertTrue(any("at least one test scenario" in error for error in errors))

    def test_every_acceptance_criterion_needs_an_approved_package_mapping(self):
        data = valid_manifest()
        data["packageAcceptanceCriteria"][0]["acceptanceCriterionIds"] = ["AC-999"]
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("references unknown acceptance criterion AC-999" in error for error in errors))
        self.assertTrue(any("must assign every acceptance criterion" in error for error in errors))

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

    def test_incomplete_feedback_batch_blocks_approval(self):
        data = valid_manifest()
        data["feedbackBatches"][0]["status"] = "OPEN"
        data["feedbackBatches"][0]["processedItems"] = 1
        data["feedbackBatches"][0]["unresolvedItems"] = ["annotation 2"]
        errors = MODULE.validate_decision_manifest(data, "approved")
        self.assertTrue(any("feedback batch FB-1 is open" in error for error in errors))

    def test_complete_feedback_batch_must_reconcile_exactly(self):
        data = valid_manifest()
        data["feedbackBatches"][0]["processedItems"] = 1
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("complete batch count does not reconcile" in error for error in errors))

    def test_unconfirmed_scenario_blocks_approval(self):
        data = valid_manifest()
        data["testScenarios"][0]["status"] = "PROPOSED"
        data["coverage"]["testScenarios"]["classified"] = 0
        errors = MODULE.validate_decision_manifest(data, "approved")
        self.assertTrue(any("not human-confirmed" in error for error in errors))

    def test_unknown_and_malformed_fields_fail_closed(self):
        data = valid_manifest()
        data["inventedSummary"] = "looks plausible"
        data["decisions"][0]["sources"][0]["authority"] = "TRUST_ME"
        errors = MODULE.validate_decision_manifest(data, "alignment")
        self.assertTrue(any("inventedSummary: unknown field" in error for error in errors))
        self.assertTrue(any("authority: value is not in the allowed enum" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

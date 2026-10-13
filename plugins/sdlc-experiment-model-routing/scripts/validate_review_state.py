#!/usr/bin/env python3
"""Fail-closed validation for the SDLC evidence-checked review state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schema_validation import validate_schema_instance


HIGH_IMPACT_AREAS = {
    "BUSINESS_BEHAVIOR",
    "SECURITY",
    "PUBLIC_CONTRACT",
    "ARCHITECTURE",
    "DATA",
    "OPERATIONS",
}
FIX_RESULTS = {"VALID", "PARTLY_RIGHT"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_review_state(
    data: object,
    phase: str,
    decision_manifest: object | None = None,
) -> list[str]:
    errors: list[str] = []
    schema_path = SCRIPT_DIR.parent / "artifact-definitions" / "07-review.state.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"review state schema unreadable: {exc}"]
    errors.extend(validate_schema_instance(data, schema))
    require(isinstance(data, dict), "root must be an object", errors)
    if not isinstance(data, dict):
        return errors

    require(data.get("schemaVersion") == 2, "schemaVersion must be 2", errors)
    require(non_empty_text(data.get("packageId")), "packageId is required", errors)
    baseline = data.get("baseline")
    require(isinstance(baseline, dict), "baseline is required", errors)
    implementation_commit = baseline.get("implementationCommit") if isinstance(baseline, dict) else None
    if isinstance(baseline, dict):
        require(non_empty_text(baseline.get("baseCommit")), "baseline.baseCommit is required", errors)
        require(non_empty_text(implementation_commit), "baseline.implementationCommit is required", errors)
        implementation_check = baseline.get("implementationFullCheck")
        if isinstance(implementation_check, dict):
            require(
                implementation_check.get("commit") == implementation_commit,
                "baseline.implementationFullCheck must belong to the implementation commit",
                errors,
            )
            require(
                implementation_check.get("source") == "STEP_06",
                "baseline.implementationFullCheck source must be STEP_06",
                errors,
            )

    criteria = data.get("acceptanceCriteria")
    require(isinstance(criteria, list) and bool(criteria), "acceptanceCriteria must be a non-empty array", errors)
    criterion_ids: set[str] = set()
    if isinstance(criteria, list):
        for index, criterion in enumerate(criteria):
            prefix = f"acceptanceCriteria[{index}]"
            require(isinstance(criterion, dict), f"{prefix} must be an object", errors)
            if not isinstance(criterion, dict):
                continue
            criterion_id = criterion.get("id")
            require(non_empty_text(criterion_id), f"{prefix}.id is required", errors)
            if isinstance(criterion_id, str):
                require(criterion_id not in criterion_ids, f"duplicate acceptance criterion {criterion_id}", errors)
                criterion_ids.add(criterion_id)
            require(non_empty_text(criterion.get("text")), f"{prefix}.text is required", errors)
            require(bool(criterion.get("evidence")), f"{prefix}.evidence must not be empty", errors)

    manifest_decisions: dict[str, dict[str, object]] = {}
    if decision_manifest is not None:
        require(isinstance(decision_manifest, dict), "decision manifest must be an object", errors)
        if isinstance(decision_manifest, dict):
            manifest_criteria = {
                str(item.get("id")): item
                for item in decision_manifest.get("acceptanceCriteria") or []
                if isinstance(item, dict)
            }
            mappings = [
                item for item in decision_manifest.get("packageAcceptanceCriteria") or []
                if isinstance(item, dict)
                and item.get("packageId") in {data.get("packageId"), "ALL"}
            ]
            require(len(mappings) == 1, f"decision manifest needs exactly one AC mapping for package {data.get('packageId')}", errors)
            expected_ids = set(mappings[0].get("acceptanceCriterionIds") or []) if len(mappings) == 1 else set()
            require(
                criterion_ids == expected_ids,
                f"review acceptance criteria must exactly match package {data.get('packageId')}: expected {sorted(expected_ids)}, got {sorted(criterion_ids)}",
                errors,
            )
            for criterion in criteria or []:
                if not isinstance(criterion, dict):
                    continue
                canonical = manifest_criteria.get(str(criterion.get("id")))
                require(isinstance(canonical, dict), f"review criterion {criterion.get('id')} is absent from the decision manifest", errors)
                if isinstance(canonical, dict):
                    require(
                        criterion.get("text") == canonical.get("text"),
                        f"review criterion {criterion.get('id')} text differs from the approved criterion",
                        errors,
                    )
            manifest_decisions = {
                str(item.get("id")): item
                for item in decision_manifest.get("decisions") or []
                if isinstance(item, dict)
            }

    findings = data.get("findings")
    require(isinstance(findings, list), "findings must be an array", errors)
    if not isinstance(findings, list):
        return errors

    finding_ids: set[str] = set()
    checked_by_id: dict[str, dict[str, object]] = {}
    asks_human = False
    has_human_finding = any(
        isinstance(item, dict)
        and isinstance(item.get("evidenceCheck"), dict)
        and item["evidenceCheck"].get("result") == "ASK_HUMAN"
        for item in findings
    )
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        require(isinstance(finding, dict), f"{prefix} must be an object", errors)
        if not isinstance(finding, dict):
            continue

        finding_id = finding.get("id")
        require(non_empty_text(finding_id), f"{prefix}.id is required", errors)
        if isinstance(finding_id, str):
            require(finding_id not in finding_ids, f"duplicate finding id {finding_id}", errors)
            finding_ids.add(finding_id)
        for field in ("problem", "failureScenario", "verificationMethod"):
            require(non_empty_text(finding.get(field)), f"{prefix}.{field} is required", errors)
        require(bool(finding.get("evidence")), f"{prefix}.evidence must not be empty", errors)
        require(isinstance(finding.get("objective"), dict), f"{prefix}.objective is required", errors)
        require(isinstance(finding.get("supportingSources"), list), f"{prefix}.supportingSources must be an array", errors)
        require(isinstance(finding.get("conflictingSources"), list), f"{prefix}.conflictingSources must be an array", errors)
        require(
            isinstance(finding.get("impactAreas"), list) and bool(finding.get("impactAreas")),
            f"{prefix}.impactAreas must be a non-empty array",
            errors,
        )

        if phase == "findings":
            require(finding.get("status") == "OPEN", f"{prefix}.status must be OPEN in findings phase", errors)
            require(finding.get("evidenceCheck") is None, f"{prefix}.evidenceCheck must be null in findings phase", errors)
            continue

        check = finding.get("evidenceCheck")
        require(isinstance(check, dict), f"{prefix}.evidenceCheck is required", errors)
        require(
            finding.get("status") == ("CHECKED" if phase == "checked" else "CLOSED"),
            f"{prefix}.status must be {'CHECKED' if phase == 'checked' else 'CLOSED'} in {phase} phase",
            errors,
        )
        if not isinstance(check, dict):
            continue
        if isinstance(finding_id, str):
            checked_by_id[finding_id] = check
        result = check.get("result")
        path = check.get("path")
        require(non_empty_text(check.get("reason")), f"{prefix}.evidenceCheck.reason is required", errors)
        require(non_empty_text(check.get("baselineTradeoff")), f"{prefix}.evidenceCheck.baselineTradeoff is required", errors)
        risky = bool(set(finding.get("impactAreas") or []) & HIGH_IMPACT_AREAS)

        if result in FIX_RESULTS:
            require(path in {"LIGHT", "FULL"}, f"{prefix} valid finding needs LIGHT or FULL path", errors)
            require(non_empty_text(check.get("correctionTradeoff")), f"{prefix} valid finding needs correctionTradeoff", errors)
            if has_human_finding:
                require(check.get("trialFixId") is None, f"{prefix} waits without a trialFixId until the human conflict is resolved", errors)
            else:
                require(non_empty_text(check.get("trialFixId")), f"{prefix} valid finding needs trialFixId", errors)
            require(check.get("decisionId") is None, f"{prefix} valid finding must not set decisionId", errors)
            if risky:
                require(path == "FULL", f"{prefix} high-impact finding must use FULL path", errors)
        elif result == "NOT_A_PROBLEM":
            require(path == "NO_CHANGE", f"{prefix} not-a-problem finding must use NO_CHANGE path", errors)
            require(check.get("trialFixId") is None, f"{prefix} no-change path must not name a trial fix", errors)
            require(check.get("decisionId") is None, f"{prefix} no-change path must not name a decision", errors)
        elif result == "ASK_HUMAN":
            asks_human = True
            require(path == "HUMAN", f"{prefix} human conflict must use HUMAN path", errors)
            require(non_empty_text(check.get("decisionId")), f"{prefix} human conflict needs decisionId", errors)
            require(check.get("trialFixId") is None, f"{prefix} human conflict must preserve the baseline", errors)

    if asks_human and isinstance(decision_manifest, dict):
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            check = finding.get("evidenceCheck")
            if not isinstance(check, dict) or check.get("result") != "ASK_HUMAN":
                continue
            decision_id = str(check.get("decisionId"))
            decision = manifest_decisions.get(decision_id)
            require(isinstance(decision, dict), f"human finding {finding.get('id')} references unknown decision {decision_id}", errors)
            if isinstance(decision, dict):
                require(decision.get("riskClass") == "HUMAN_REQUIRED", f"decision {decision_id} must be HUMAN_REQUIRED", errors)
                require(decision.get("status") == "OPEN", f"decision {decision_id} must be OPEN for focused review", errors)
            matching_changes = [
                item for item in decision_manifest.get("semanticChanges") or []
                if isinstance(item, dict)
                and item.get("discoveredAt") == "REVIEW"
                and item.get("status") == "NEEDS_HUMAN_DECISION"
                and item.get("decisionId") == decision_id
            ]
            require(bool(matching_changes), f"decision {decision_id} needs a REVIEW semantic change awaiting human choice", errors)
        approval = decision_manifest.get("approval")
        require(
            isinstance(approval, dict) and approval.get("status") == "REOPENED",
            "ASK_HUMAN review requires decision-manifest approval status REOPENED",
            errors,
        )

    trial_fixes = data.get("trialFixes")
    require(isinstance(trial_fixes, list), "trialFixes must be an array", errors)
    if not isinstance(trial_fixes, list):
        trial_fixes = []
    trial_ids: set[str] = set()
    trial_by_id: dict[str, dict[str, object]] = {}
    referenced_findings: set[str] = set()
    for index, trial in enumerate(trial_fixes):
        prefix = f"trialFixes[{index}]"
        require(isinstance(trial, dict), f"{prefix} must be an object", errors)
        if not isinstance(trial, dict):
            continue
        trial_id = trial.get("id")
        require(non_empty_text(trial_id), f"{prefix}.id is required", errors)
        if isinstance(trial_id, str):
            require(trial_id not in trial_ids, f"duplicate trial fix id {trial_id}", errors)
            trial_ids.add(trial_id)
            trial_by_id[trial_id] = trial
        require(trial.get("baseCommit") == implementation_commit, f"{prefix} must start from the implementation baseline", errors)
        if trial.get("path") == "LIGHT":
            require(trial.get("workspaceMode") == "SHARED_TRIAL_BRANCH", f"{prefix} LIGHT path uses one shared trial branch", errors)
        elif trial.get("path") == "FULL":
            require(trial.get("workspaceMode") == "ISOLATED_WORKTREE", f"{prefix} FULL path needs an isolated worktree", errors)
        for finding_id in trial.get("findingIds") or []:
            require(finding_id in finding_ids, f"{prefix} references unknown finding {finding_id}", errors)
            require(finding_id not in referenced_findings, f"finding {finding_id} appears in more than one trial fix", errors)
            referenced_findings.add(str(finding_id))
            check = checked_by_id.get(str(finding_id), {})
            require(check.get("trialFixId") == trial_id, f"{prefix} and finding {finding_id} disagree on trialFixId", errors)
            require(check.get("path") == trial.get("path"), f"{prefix} and finding {finding_id} disagree on path", errors)

    for finding_id, check in checked_by_id.items():
        if check.get("result") in FIX_RESULTS:
            if not has_human_finding:
                trial_id = check.get("trialFixId")
                require(trial_id in trial_ids, f"finding {finding_id} references an unknown trial fix", errors)
                if trial_id in trial_by_id:
                    require(
                        finding_id in (trial_by_id[trial_id].get("findingIds") or []),
                        f"finding {finding_id} is not covered by its trial fix {trial_id}",
                        errors,
                    )

    if len(trial_fixes) <= 1:
        require(data.get("multipleTrialFixReason") is None, "multipleTrialFixReason must be null for zero or one trial fix", errors)
    else:
        require(
            non_empty_text(data.get("multipleTrialFixReason")),
            "multiple trial fixes need a reason why one combined trial is unsafe or impossible",
            errors,
        )
        for index, trial in enumerate(trial_fixes[1:], start=1):
            if isinstance(trial, dict):
                require(non_empty_text(trial.get("separateReason")), f"trialFixes[{index}] needs separateReason", errors)

    if phase == "findings":
        require(not trial_fixes, "findings phase must not create trial fixes", errors)
        require(data.get("multipleTrialFixReason") is None, "findings phase multipleTrialFixReason must be null", errors)
        require(data.get("selectedTrialFixId") is None, "findings phase selectedTrialFixId must be null", errors)
        require(data.get("finalFullCheck") is None, "findings phase finalFullCheck must be null", errors)
        require(data.get("verdict") == "IN_REVIEW", "findings phase verdict must be IN_REVIEW", errors)
        require(data.get("finalCommit") is None, "findings phase finalCommit must be null", errors)
        return errors

    if phase == "checked":
        if asks_human:
            require(not trial_fixes, "a human conflict stops before any trial fix is planned", errors)
        require(data.get("selectedTrialFixId") is None, "checked phase selectedTrialFixId must be null", errors)
        require(data.get("finalFullCheck") is None, "checked phase finalFullCheck must be null", errors)
        require(data.get("verdict") == "IN_REVIEW", "checked phase verdict must be IN_REVIEW", errors)
        require(data.get("finalCommit") is None, "checked phase finalCommit must be null", errors)
        return errors

    if asks_human:
        require(data.get("verdict") == "ASK_HUMAN", "a human conflict requires ASK_HUMAN verdict", errors)
        require(not trial_fixes, "a human conflict stops before trial fixes are built", errors)
        require(data.get("selectedTrialFixId") is None, "a human conflict cannot select a trial fix", errors)
        require(data.get("finalFullCheck") is None, "a human conflict stops before the final full check", errors)
        require(data.get("finalCommit") is None, "a human conflict preserves the baseline and has null finalCommit", errors)
        return errors

    require(data.get("verdict") in {"APPROVE", "REQUEST_CHANGES", "COMMENT"}, "closed verdict is invalid", errors)
    selected_id = data.get("selectedTrialFixId")
    safe_trials: list[str] = []
    for index, trial in enumerate(trial_fixes):
        if not isinstance(trial, dict):
            continue
        prefix = f"trialFixes[{index}]"
        require(trial.get("status") == "CHECKED", f"{prefix} must be CHECKED before review closes", errors)
        require(non_empty_text(trial.get("commit")), f"{prefix}.commit is required before review closes", errors)
        for field in ("defectRemovedEvidence", "invariantChecks", "targetedChecks"):
            require(bool(trial.get(field)), f"{prefix}.{field} must not be empty", errors)
        if trial.get("path") == "FULL":
            require(
                any("semantic" in str(check).lower() for check in trial.get("invariantChecks", [])),
                f"{prefix} FULL path needs an explicit semantic invariant check",
                errors,
            )
        if trial.get("comparison") == "SAFE_IMPROVEMENT" and isinstance(trial.get("id"), str):
            safe_trials.append(trial["id"])

    if selected_id is None:
        require(not safe_trials, "a SAFE_IMPROVEMENT trial fix must be selected", errors)
        require(data.get("finalCommit") == implementation_commit, "without a selected trial fix, finalCommit must preserve the baseline", errors)
    else:
        selected = trial_by_id.get(str(selected_id))
        require(isinstance(selected, dict), "selectedTrialFixId is unknown", errors)
        if isinstance(selected, dict):
            require(selected.get("comparison") == "SAFE_IMPROVEMENT", "selected trial fix is not a SAFE_IMPROVEMENT", errors)
            require(data.get("finalCommit") == selected.get("commit"), "finalCommit must equal the selected trial fix commit", errors)
        require(len(safe_trials) == 1, "exactly one trial fix may be selected as the safe improvement", errors)

    final_check = data.get("finalFullCheck")
    require(isinstance(final_check, dict), "closed review needs one finalFullCheck", errors)
    if isinstance(final_check, dict):
        require(final_check.get("commit") == data.get("finalCommit"), "finalFullCheck must verify finalCommit", errors)
        require(final_check.get("result") == "PASSED", "finalFullCheck must pass", errors)
        implementation_check = baseline.get("implementationFullCheck") if isinstance(baseline, dict) else None
        if (
            data.get("finalCommit") == implementation_commit
            and isinstance(implementation_check, dict)
            and implementation_check.get("result") == "PASSED"
        ):
            require(
                final_check == implementation_check,
                "an unchanged baseline must reuse its exact passing Step 06 full check",
                errors,
            )
        if final_check.get("source") == "STEP_06":
            require(data.get("finalCommit") == implementation_commit, "Step 06 evidence can be reused only for the unchanged baseline", errors)
            require(final_check == implementation_check, "reused Step 06 evidence must match the recorded immutable baseline check", errors)

    incomplete = [
        item for item in criteria or []
        if isinstance(item, dict) and item.get("status") != "MET"
    ]
    if incomplete:
        require(
            data.get("verdict") not in {"APPROVE", "COMMENT"},
            "APPROVE or COMMENT is invalid unless every acceptance criterion is MET",
            errors,
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("--decision-manifest", type=Path, required=True)
    parser.add_argument("--phase", choices=("findings", "checked", "closed"), required=True)
    args = parser.parse_args()
    try:
        data = json.loads(args.state.read_text(encoding="utf-8"))
        decision_manifest = json.loads(args.decision_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"review state unreadable: {exc}", file=sys.stderr)
        return 2
    errors = validate_review_state(data, args.phase, decision_manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid review state ({args.phase})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

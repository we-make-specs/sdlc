#!/usr/bin/env python3
"""Fail-closed semantic validation for the SDLC decision manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schema_validation import validate_schema_instance


HIGH_RISK = {"BUSINESS_BEHAVIOR", "SECURITY", "PUBLIC_CONTRACT", "ARCHITECTURE", "DATA", "OPERATIONS"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def unique_ids(items: object, label: str, errors: list[str]) -> set[str]:
    result: set[str] = set()
    require(isinstance(items, list), f"{label} must be an array", errors)
    if not isinstance(items, list):
        return result
    for index, item in enumerate(items):
        require(isinstance(item, dict), f"{label}[{index}] must be an object", errors)
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        require(text(item_id), f"{label}[{index}].id is required", errors)
        if isinstance(item_id, str):
            require(item_id not in result, f"duplicate {label} id {item_id}", errors)
            result.add(item_id)
    return result


def validate_decision_manifest(data: object, phase: str) -> list[str]:
    errors: list[str] = []
    schema_path = SCRIPT_DIR.parent / "artifact-definitions" / "03-decision-manifest.state.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"decision manifest schema unreadable: {exc}"]
    errors.extend(validate_schema_instance(data, schema))
    require(isinstance(data, dict), "root must be an object", errors)
    if not isinstance(data, dict):
        return errors
    require(data.get("schemaVersion") == 1, "schemaVersion must be 1", errors)
    require(text(data.get("ticket")), "ticket is required", errors)

    criteria = data.get("acceptanceCriteria")
    scenarios = data.get("testScenarios")
    decisions = data.get("decisions")
    rules = data.get("applicableRules")
    changes = data.get("semanticChanges")
    batches = data.get("feedbackBatches")
    ac_ids = unique_ids(criteria, "acceptanceCriteria", errors)
    scenario_ids = unique_ids(scenarios, "testScenarios", errors)
    decision_ids = unique_ids(decisions, "decisions", errors)
    rule_ids = unique_ids(rules, "applicableRules", errors)
    change_ids = unique_ids(changes, "semanticChanges", errors)
    unique_ids(batches, "feedbackBatches", errors)

    if isinstance(criteria, list):
        for index, criterion in enumerate(criteria):
            if not isinstance(criterion, dict):
                continue
            prefix = f"acceptanceCriteria[{index}]"
            require(text(criterion.get("text")), f"{prefix}.text is required", errors)
            refs = criterion.get("decisionIds")
            require(isinstance(refs, list), f"{prefix}.decisionIds must be an array", errors)
            if isinstance(refs, list):
                for ref in refs:
                    require(ref in decision_ids, f"{prefix} references unknown decision {ref}", errors)

    if isinstance(scenarios, list):
        for index, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                continue
            prefix = f"testScenarios[{index}]"
            require(text(scenario.get("title")), f"{prefix}.title is required", errors)
            require(text(scenario.get("behavior")), f"{prefix}.behavior is required", errors)
            for ref in scenario.get("decisionIds") or []:
                require(ref in decision_ids, f"{prefix} references unknown decision {ref}", errors)

    resolved_human: set[str] = set()
    if isinstance(decisions, list):
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict):
                continue
            prefix = f"decisions[{index}]"
            options = decision.get("options")
            require(isinstance(options, list) and len(options) >= 2, f"{prefix} needs at least two options", errors)
            option_ids = {
                option.get("id") for option in options or [] if isinstance(option, dict) and text(option.get("id"))
            }
            recommendation = decision.get("recommendation")
            require(isinstance(recommendation, dict), f"{prefix}.recommendation is required", errors)
            if isinstance(recommendation, dict):
                require(recommendation.get("optionId") in option_ids, f"{prefix} recommendation is not an option", errors)
                require(text(recommendation.get("counterargument")), f"{prefix} recommendation needs a counterargument", errors)
            sources = decision.get("sources")
            require(isinstance(sources, list) and bool(sources), f"{prefix}.sources must not be empty", errors)
            for rule_id in decision.get("applicableRuleIds") or []:
                require(rule_id in rule_ids, f"{prefix} references unknown rule {rule_id}", errors)
            for conflict in decision.get("conflicts") or []:
                if isinstance(conflict, dict) and conflict.get("status") == "RESOLVED":
                    require(text(conflict.get("resolution")), f"{prefix} resolved conflict needs a resolution", errors)
            status = decision.get("status")
            resolution = decision.get("resolution")
            if status == "RESOLVED":
                require(isinstance(resolution, dict), f"{prefix} resolved decision needs resolution", errors)
                if isinstance(resolution, dict):
                    require(resolution.get("optionId") in option_ids, f"{prefix} resolution is not an option", errors)
                if decision.get("riskClass") == "HUMAN_REQUIRED":
                    resolved_human.add(str(decision.get("id")))
            else:
                require(resolution is None, f"{prefix} open/deferred decision must have null resolution", errors)
            dimensions = set(decision.get("riskDimensions") or [])
            if dimensions & HIGH_RISK:
                require(decision.get("riskClass") == "HUMAN_REQUIRED", f"{prefix} high-risk decision must be HUMAN_REQUIRED", errors)

    if isinstance(rules, list):
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                continue
            prefix = f"applicableRules[{index}]"
            article = str(rule.get("article") or "")
            todo_article = any(part.startswith("_todo_") for part in re.split(r"[/\\]", article))
            if todo_article:
                require(rule.get("classification") == "MISSING", f"{prefix} _todo_ article must be MISSING, never binding", errors)
            if rule.get("classification") == "MISSING":
                require(rule.get("status") == "UNRESOLVED", f"{prefix} missing rule must be UNRESOLVED", errors)
            for decision_id in rule.get("affectedDecisionIds") or []:
                require(decision_id in decision_ids, f"{prefix} references unknown decision {decision_id}", errors)
            if rule.get("status") == "DEVIATION_APPROVED":
                deviation = rule.get("deviationDecisionId")
                require(deviation in resolved_human, f"{prefix} deviation needs a resolved human decision", errors)
            else:
                require(rule.get("deviationDecisionId") is None, f"{prefix} deviationDecisionId must be null", errors)

    if isinstance(changes, list):
        for index, change in enumerate(changes):
            if not isinstance(change, dict):
                continue
            prefix = f"semanticChanges[{index}]"
            for decision_id in change.get("affectedDecisionIds") or []:
                require(decision_id in decision_ids, f"{prefix} references unknown decision {decision_id}", errors)
            for rule_id in change.get("affectedRuleIds") or []:
                require(rule_id in rule_ids, f"{prefix} references unknown rule {rule_id}", errors)
            if change.get("status") == "NEEDS_HUMAN_DECISION":
                require(change.get("decisionId") in decision_ids, f"{prefix} needs a valid decisionId", errors)
            elif change.get("decisionId") is not None:
                require(change.get("decisionId") in decision_ids, f"{prefix} has unknown decisionId", errors)

    if isinstance(batches, list):
        for index, batch in enumerate(batches):
            if not isinstance(batch, dict):
                continue
            prefix = f"feedbackBatches[{index}]"
            expected = batch.get("expectedItems")
            processed = batch.get("processedItems")
            require(isinstance(expected, int) and expected >= 0, f"{prefix}.expectedItems is invalid", errors)
            require(isinstance(processed, int) and processed >= 0, f"{prefix}.processedItems is invalid", errors)
            require(not isinstance(expected, int) or not isinstance(processed, int) or processed <= expected, f"{prefix} processed exceeds expected", errors)
            if batch.get("status") == "COMPLETE":
                require(expected == processed, f"{prefix} complete batch count does not reconcile", errors)
                require(not batch.get("unresolvedItems"), f"{prefix} complete batch has unresolved items", errors)
            if batch.get("status") == "DEFERRED":
                require(bool(batch.get("unresolvedItems")), f"{prefix} deferred batch must name unresolved items", errors)

    coverage = data.get("coverage")
    require(isinstance(coverage, dict), "coverage is required", errors)
    if isinstance(coverage, dict):
        expected_counts = {
            "acceptanceCriteria": (len(ac_ids), sum(1 for item in criteria or [] if isinstance(item, dict) and item.get("status") == "MAPPED")),
            "testScenarios": (len(scenario_ids), sum(1 for item in scenarios or [] if isinstance(item, dict) and item.get("status") == "HUMAN_CONFIRMED")),
            "applicableRules": (len(rule_ids), sum(1 for item in rules or [] if isinstance(item, dict) and item.get("classification") not in {"MISSING", "CONFLICTING"})),
            "semanticChanges": (len(change_ids), sum(1 for item in changes or [] if isinstance(item, dict) and item.get("status") != "NEEDS_HUMAN_DECISION")),
        }
        for key, (total, classified) in expected_counts.items():
            counts = coverage.get(key)
            require(isinstance(counts, dict), f"coverage.{key} is required", errors)
            if isinstance(counts, dict):
                require(counts.get("total") == total, f"coverage.{key}.total must be {total}", errors)
                require(counts.get("classified") == classified, f"coverage.{key}.classified must be {classified}", errors)

    if phase in {"approved", "downstream"}:
        for decision in decisions or []:
            if not isinstance(decision, dict):
                continue
            require(not (decision.get("riskClass") == "HUMAN_REQUIRED" and decision.get("status") != "RESOLVED"), f"human decision {decision.get('id')} is unresolved", errors)
            for conflict in decision.get("conflicts") or []:
                require(not (isinstance(conflict, dict) and conflict.get("status") == "OPEN"), f"decision {decision.get('id')} has an open source conflict", errors)
        for rule in rules or []:
            if isinstance(rule, dict):
                require(rule.get("status") not in {"UNRESOLVED"}, f"rule {rule.get('id')} is unresolved", errors)
        for criterion in criteria or []:
            if isinstance(criterion, dict):
                require(criterion.get("status") == "MAPPED", f"acceptance criterion {criterion.get('id')} is unresolved", errors)
        for scenario in scenarios or []:
            if isinstance(scenario, dict):
                require(scenario.get("status") == "HUMAN_CONFIRMED", f"test scenario {scenario.get('id')} is not human-confirmed", errors)
        for batch in batches or []:
            if isinstance(batch, dict):
                require(batch.get("status") in {"COMPLETE", "DEFERRED"}, f"feedback batch {batch.get('id')} is open", errors)
        for change in changes or []:
            if isinstance(change, dict):
                require(change.get("status") != "NEEDS_HUMAN_DECISION", f"semantic change {change.get('id')} needs a human decision", errors)
        approval = data.get("approval")
        require(isinstance(approval, dict), "approval is required", errors)
        if isinstance(approval, dict):
            require(approval.get("status") == "APPROVED", "approval.status must be APPROVED", errors)
            require(text(approval.get("approvedBy")), "approval.approvedBy is required", errors)
            require(text(approval.get("approvedAt")), "approval.approvedAt is required", errors)
            approved_ids = set(approval.get("approvedDecisionIds") or [])
            require(resolved_human.issubset(approved_ids), "approval must name every resolved human decision", errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--phase", choices=("alignment", "approved", "downstream"), required=True)
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"decision manifest unreadable: {exc}", file=sys.stderr)
        return 2
    errors = validate_decision_manifest(data, args.phase)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid decision manifest ({args.phase})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

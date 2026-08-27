#!/usr/bin/env python3
"""Fail-closed validation for the SDLC review/adjudication state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schema_validation import validate_schema_instance


RISKY_BLAST_RADIUS = {"SECURITY", "PUBLIC_CONTRACT", "ARCHITECTURE", "DATA", "OPERATIONS"}
DISPOSITIONS = {"ACCEPT", "REJECT", "REFRAME", "ESCALATE"}
ALTERNATIVE_KINDS = {"PRESERVE_BASELINE", "REVIEWER_SUGGESTION", "ALTERNATIVE"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_review_state(data: object, phase: str) -> list[str]:
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

    require(data.get("schemaVersion") == 1, "schemaVersion must be 1", errors)
    require(non_empty_text(data.get("packageId")), "packageId is required", errors)
    baseline = data.get("baseline")
    require(isinstance(baseline, dict), "baseline is required", errors)
    if isinstance(baseline, dict):
        require(non_empty_text(baseline.get("baseCommit")), "baseline.baseCommit is required", errors)
        require(
            non_empty_text(baseline.get("implementationCommit")),
            "baseline.implementationCommit is required",
            errors,
        )

    claims = data.get("claims")
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
            require(criterion.get("status") in {"MET", "NOT_MET", "PARTIAL", "NOT_VERIFIABLE"}, f"{prefix}.status is invalid", errors)
            require(bool(criterion.get("evidence")), f"{prefix}.evidence must not be empty", errors)
    require(isinstance(claims, list), "claims must be an array", errors)
    if not isinstance(claims, list):
        return errors

    ids: set[str] = set()
    for index, claim in enumerate(claims):
        prefix = f"claims[{index}]"
        require(isinstance(claim, dict), f"{prefix} must be an object", errors)
        if not isinstance(claim, dict):
            continue

        claim_id = claim.get("id")
        require(non_empty_text(claim_id), f"{prefix}.id is required", errors)
        if isinstance(claim_id, str):
            require(claim_id not in ids, f"duplicate claim id {claim_id}", errors)
            ids.add(claim_id)

        for field in ("problem", "failureScenario", "verificationMethod"):
            require(non_empty_text(claim.get(field)), f"{prefix}.{field} is required", errors)
        require(bool(claim.get("evidence")), f"{prefix}.evidence must not be empty", errors)
        require(isinstance(claim.get("objective"), dict), f"{prefix}.objective is required", errors)
        require(isinstance(claim.get("supportingSources"), list), f"{prefix}.supportingSources must be an array", errors)
        require(isinstance(claim.get("conflictingSources"), list), f"{prefix}.conflictingSources must be an array", errors)
        require(isinstance(claim.get("blastRadius"), list), f"{prefix}.blastRadius must be an array", errors)

        if phase == "claims":
            require(claim.get("adjudication") is None, f"{prefix}.adjudication must be null in claims phase", errors)
            require(claim.get("candidate") is None, f"{prefix}.candidate must be null in claims phase", errors)
            continue

        adjudication = claim.get("adjudication")
        require(isinstance(adjudication, dict), f"{prefix}.adjudication is required", errors)
        if not isinstance(adjudication, dict):
            continue
        disposition = adjudication.get("disposition")
        require(disposition in DISPOSITIONS, f"{prefix}.adjudication.disposition is invalid", errors)
        require(non_empty_text(adjudication.get("rationale")), f"{prefix}.adjudication.rationale is required", errors)
        alternatives = adjudication.get("alternatives")
        require(isinstance(alternatives, list) and len(alternatives) >= 3, f"{prefix} needs at least three alternatives", errors)
        if isinstance(alternatives, list):
            kinds = {item.get("kind") for item in alternatives if isinstance(item, dict)}
            require(ALTERNATIVE_KINDS.issubset(kinds), f"{prefix} must compare baseline, suggestion, and alternative", errors)

        conflicts = claim.get("conflictingSources") or []
        if conflicts and disposition != "ESCALATE":
            require(
                non_empty_text(adjudication.get("conflictResolution")),
                f"{prefix} has conflicting sources but no conflictResolution",
                errors,
            )
        if disposition == "ESCALATE":
            require(non_empty_text(adjudication.get("decisionId")), f"{prefix} escalation needs decisionId", errors)

        if phase != "closed":
            continue

        candidate = claim.get("candidate")
        if disposition in {"ACCEPT", "REFRAME"}:
            require(isinstance(candidate, dict), f"{prefix} accepted/reframed claim needs a candidate", errors)
            if isinstance(candidate, dict):
                require(candidate.get("comparison") == "BETTER", f"{prefix} candidate is not proven BETTER", errors)
                for field in ("defectRemovedEvidence", "invariantChecks", "regressionChecks"):
                    require(bool(candidate.get(field)), f"{prefix}.candidate.{field} must not be empty", errors)
                risky = bool(set(claim.get("blastRadius") or []) & RISKY_BLAST_RADIUS)
                if risky:
                    require(
                        any("semantic" in str(check).lower() for check in candidate.get("invariantChecks", [])),
                        f"{prefix} risky change needs an explicit semantic invariant check",
                        errors,
                    )
        elif disposition == "REJECT":
            require(candidate is None, f"{prefix} rejected claim must not carry a candidate", errors)
        elif disposition == "ESCALATE":
            require(candidate is None, f"{prefix} escalated claim must preserve the baseline", errors)

    if phase == "claims":
        require(data.get("verdict") == "IN_REVIEW", "claims phase verdict must be IN_REVIEW", errors)
        require(data.get("finalCommit") is None, "claims phase finalCommit must be null", errors)
    elif phase == "closed":
        escalated = any(
            isinstance(claim, dict)
            and isinstance(claim.get("adjudication"), dict)
            and claim["adjudication"].get("disposition") == "ESCALATE"
            for claim in claims
        )
        if escalated:
            require(data.get("verdict") == "ESCALATED", "an escalation requires ESCALATED verdict", errors)
            require(data.get("finalCommit") is None, "an escalation must preserve baseline and have null finalCommit", errors)
        else:
            require(data.get("verdict") in {"APPROVE", "REQUEST_CHANGES", "COMMENT"}, "closed verdict is invalid", errors)
            require(non_empty_text(data.get("finalCommit")), "closed review needs finalCommit", errors)
            unmet = [
                item for item in criteria or []
                if isinstance(item, dict) and item.get("status") in {"NOT_MET", "PARTIAL"}
            ]
            if unmet:
                require(data.get("verdict") != "APPROVE", "APPROVE is invalid while an acceptance criterion is not met or partial", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("--phase", choices=("claims", "adjudication", "closed"), required=True)
    args = parser.parse_args()
    try:
        data = json.loads(args.state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"review state unreadable: {exc}", file=sys.stderr)
        return 2
    errors = validate_review_state(data, args.phase)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid review state ({args.phase})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

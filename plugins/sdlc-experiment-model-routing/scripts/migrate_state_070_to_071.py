#!/usr/bin/env python3
"""Safely migrate SDLC 0.7.0 decision or review state to 0.7.1.

The original version-1 file is preserved beside the migrated file. Decision
approval is deliberately reopened because the new human-facing summaries and
priority order were not part of the earlier approval. Completed legacy review
claims resume at the evidence-checked stage; old candidate evidence remains in
the backup and is never silently treated as proof under the new model.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any


HIGH_IMPACT_AREAS = {
    "BUSINESS_BEHAVIOR",
    "SECURITY",
    "PUBLIC_CONTRACT",
    "ARCHITECTURE",
    "DATA",
    "OPERATIONS",
}


def source_v2(source: object) -> dict[str, Any]:
    item = source if isinstance(source, dict) else {}
    return {
        "kind": item.get("kind", "REVIEWER_INFERENCE"),
        "reference": item.get("reference") or "migrated 0.7.0 review record",
        "statement": item.get("claim") or item.get("statement") or "Legacy review objective",
    }


def choice_tradeoff(adjudication: dict[str, Any], kind: str, fallback: str) -> str:
    for item in adjudication.get("alternatives") or []:
        if isinstance(item, dict) and item.get("kind") == kind and str(item.get("tradeoffs") or "").strip():
            return str(item["tradeoffs"])
    return fallback


def migrate_decision(data: dict[str, Any]) -> dict[str, Any]:
    migrated = copy.deepcopy(data)
    migrated["schemaVersion"] = 2
    for criterion in migrated.get("acceptanceCriteria") or []:
        if not isinstance(criterion, dict):
            continue
        exact = str(criterion.get("text") or "Legacy acceptance criterion")
        criterion["shortMeaning"] = exact
        criterion["whyItMatters"] = "The ticket names this as required behavior."
        criterion["priority"] = "IMPORTANT"
    migrated["packageAcceptanceCriteria"] = [{
        "packageId": "ALL",
        "acceptanceCriterionIds": [
            str(item.get("id")) for item in migrated.get("acceptanceCriteria") or [] if isinstance(item, dict)
        ],
    }]
    approval = migrated.setdefault("approval", {})
    approval["status"] = "REOPENED"
    approval["artifactHashes"] = {
        "agreement": None,
        "targetSolution": None,
        "targetSolutionView": None,
        "testScenarios": None,
        "decisionContent": None,
    }
    return migrated


def migrate_review(data: dict[str, Any]) -> dict[str, Any]:
    baseline = data.get("baseline") if isinstance(data.get("baseline"), dict) else {}
    implementation_commit = baseline.get("implementationCommit")
    claims = [item for item in data.get("claims") or [] if isinstance(item, dict)]
    resume_at_findings = any(not isinstance(item.get("adjudication"), dict) for item in claims)
    has_human_conflict = any(
        isinstance(item.get("adjudication"), dict)
        and item["adjudication"].get("disposition") == "ESCALATE"
        for item in claims
    )
    fix_claims = [
        item for item in claims
        if isinstance(item.get("adjudication"), dict)
        and item["adjudication"].get("disposition") in {"ACCEPT", "REFRAME"}
    ]
    combined_path = "FULL" if any(
        set(item.get("blastRadius") or []) & HIGH_IMPACT_AREAS for item in fix_claims
    ) else "LIGHT"

    findings: list[dict[str, Any]] = []
    for claim in claims:
        adjudication = claim.get("adjudication") if isinstance(claim.get("adjudication"), dict) else {}
        common = {
            "id": claim.get("id"),
            "problem": claim.get("problem"),
            "evidence": claim.get("evidence") or ["See the preserved 0.7.0 review state."],
            "objective": source_v2(claim.get("objective")),
            "supportingSources": [source_v2(item) for item in claim.get("supportingSources") or []],
            "conflictingSources": [source_v2(item) for item in claim.get("conflictingSources") or []],
            "severity": claim.get("severity"),
            "confidence": claim.get("confidence"),
            "impactAreas": list(dict.fromkeys(claim.get("blastRadius") or ["LOCAL_IMPLEMENTATION"])),
            "failureScenario": claim.get("failureScenario"),
            "verificationMethod": claim.get("verificationMethod"),
            "suggestedFix": claim.get("suggestedFix"),
        }
        if resume_at_findings:
            findings.append({**common, "status": "OPEN", "evidenceCheck": None})
            continue
        disposition = adjudication.get("disposition")
        if disposition == "REJECT":
            result, path, trial_id, decision_id = "NOT_A_PROBLEM", "NO_CHANGE", None, None
            correction_tradeoff = None
        elif disposition == "ESCALATE":
            result, path, trial_id = "ASK_HUMAN", "HUMAN", None
            decision_id = adjudication.get("decisionId") or "MIGRATION-DECISION-REQUIRED"
            correction_tradeoff = choice_tradeoff(
                adjudication, "REVIEWER_SUGGESTION", "The proposed change may alter approved behavior."
            )
        else:
            result = "PARTLY_RIGHT" if disposition == "REFRAME" else "VALID"
            path = combined_path
            trial_id = None if has_human_conflict else "TF-1"
            decision_id = None
            correction_tradeoff = choice_tradeoff(
                adjudication, "REVIEWER_SUGGESTION", "The correction must be proved against the original design."
            )
        findings.append({
            **common,
            "status": "CHECKED",
            "evidenceCheck": {
                "result": result,
                "path": path,
                "reason": adjudication.get("rationale") or "Migrated from the 0.7.0 review decision.",
                "baselineTradeoff": choice_tradeoff(
                    adjudication, "PRESERVE_BASELINE", "Keeping the baseline preserves its current behavior."
                ),
                "correctionTradeoff": correction_tradeoff,
                "decisionId": decision_id,
                "trialFixId": trial_id,
            },
        })

    trial_fixes: list[dict[str, Any]] = []
    if fix_claims and not has_human_conflict and not resume_at_findings:
        trial_fixes.append({
            "id": "TF-1",
            "findingIds": [str(item.get("id")) for item in fix_claims],
            "path": combined_path,
            "baseCommit": implementation_commit,
            "commit": None,
            "workspaceMode": "ISOLATED_WORKTREE" if combined_path == "FULL" else "SHARED_TRIAL_BRANCH",
            "separateReason": None,
            "status": "PLANNED",
            "comparison": None,
            "defectRemovedEvidence": [],
            "invariantChecks": [],
            "targetedChecks": [],
        })

    return {
        "schemaVersion": 2,
        "packageId": data.get("packageId"),
        "baseline": {
            "baseCommit": baseline.get("baseCommit"),
            "implementationCommit": implementation_commit,
            "implementationFullCheck": None,
        },
        "contextLoaded": data.get("contextLoaded") or [],
        "acceptanceCriteria": copy.deepcopy(data.get("acceptanceCriteria") or []),
        "findings": findings,
        "trialFixes": trial_fixes,
        "multipleTrialFixReason": None,
        "selectedTrialFixId": None,
        "finalFullCheck": None,
        "verdict": "IN_REVIEW",
        "finalCommit": None,
    }


def migrate(data: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if data.get("schemaVersion") == 2:
        return copy.deepcopy(data), "already-0.7.1"
    if data.get("schemaVersion") != 1:
        raise ValueError("only schemaVersion 1 or 2 is supported")
    if "claims" in data:
        return migrate_review(data), "review"
    if "decisions" in data and "approval" in data:
        return migrate_decision(data), "decision"
    raise ValueError("file is not a recognized 0.7.0 decision or review state")


def atomic_write(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def migrate_file(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    migrated, kind = migrate(data)
    if kind == "already-0.7.1":
        return kind
    backup = path.with_name(f"{path.stem}.v0.7.0{path.suffix}")
    if backup.exists():
        raise ValueError(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
    atomic_write(path, json.dumps(migrated, ensure_ascii=False, indent=2) + "\n")
    return kind


def reconcile_review_with_decision(review_path: Path, decision: dict[str, Any]) -> None:
    """Restore exact approved AC coverage after both legacy states are migrated."""
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("schemaVersion") != 2 or "findings" not in review:
        return
    canonical = {
        str(item.get("id")): str(item.get("text"))
        for item in decision.get("acceptanceCriteria") or []
        if isinstance(item, dict)
    }
    mappings = [
        item for item in decision.get("packageAcceptanceCriteria") or []
        if isinstance(item, dict) and item.get("packageId") in {review.get("packageId"), "ALL"}
    ]
    if len(mappings) != 1:
        return
    expected_ids = [str(item) for item in mappings[0].get("acceptanceCriterionIds") or []]
    existing = {
        str(item.get("id")): item
        for item in review.get("acceptanceCriteria") or []
        if isinstance(item, dict)
    }
    reconciled: list[dict[str, Any]] = []
    for criterion_id in expected_ids:
        item = existing.get(criterion_id)
        if item is None:
            item = {
                "id": criterion_id,
                "status": "NOT_VERIFIABLE",
                "evidence": ["Added by the 0.7.1 migration; package review evidence is required."],
            }
        item["text"] = canonical.get(criterion_id, item.get("text") or "Legacy acceptance criterion")
        reconciled.append(item)
    review["acceptanceCriteria"] = reconciled
    atomic_write(review_path, json.dumps(review, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        migrated_paths: list[tuple[Path, str]] = []
        for path in args.state:
            result = migrate_file(path)
            migrated_paths.append((path, result))
            print(f"{path}: {result}")
        decision_paths = [path for path, kind in migrated_paths if kind == "decision" or "decision-manifest" in path.name]
        if decision_paths:
            decision = json.loads(decision_paths[0].read_text(encoding="utf-8"))
            for path, kind in migrated_paths:
                if kind == "review" or "07-review-" in path.name:
                    reconcile_review_with_decision(path, decision)
                    print(f"{path}: acceptance criteria reconciled with approved decision state")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

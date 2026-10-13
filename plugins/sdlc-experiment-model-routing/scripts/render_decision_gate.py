#!/usr/bin/env python3
"""Render deterministic, simple-English human gates from canonical SDLC state."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


RISK_ORDER = {"HUMAN_REQUIRED": 0, "SAMPLED": 1, "AGENT_OWNED": 2}
STATUS_ORDER = {"OPEN": 0, "DEFERRED": 1, "RESOLVED": 2}
PRIORITY_ORDER = {"CRITICAL": 0, "IMPORTANT": 1, "SUPPORTING": 2}
PLAIN = {
    "HUMAN_REQUIRED": "Human choice",
    "AGENT_OWNED": "Agent detail",
    "SAMPLED": "Spot-check",
    "BINDING": "Must follow",
    "CONSTRAINING": "Limits the choice",
    "INFORMATIVE": "Background",
    "INFERENCE": "Agent assumption",
    "EVIDENCE": "Observed evidence",
    "VALID": "Valid",
    "NOT_A_PROBLEM": "Not a problem",
    "PARTLY_RIGHT": "Partly right",
    "ASK_HUMAN": "Ask human",
    "NO_CHANGE": "Keep original",
    "LIGHT": "Light check",
    "FULL": "Full check",
    "HUMAN": "Human decision",
    "SAFE_IMPROVEMENT": "Safe improvement",
    "KEEP_ORIGINAL": "Keep original",
    "APPROVE": "Ready",
    "REQUEST_CHANGES": "Needs changes",
    "COMMENT": "Ready with notes",
    "IN_REVIEW": "Review in progress",
    "MAPPED": "Linked to the design",
    "UNRESOLVED": "Not resolved",
    "PROPOSED": "Needs confirmation",
    "HUMAN_CONFIRMED": "Confirmed by human",
    "MET": "Met",
    "NOT_MET": "Not met",
    "PARTIAL": "Partly met",
    "NOT_VERIFIABLE": "Cannot verify",
    "NEEDS_HUMAN_DECISION": "Needs human choice",
    "CLASSIFIED": "Checked",
    "ACCEPTED": "Accepted",
    "REJECTED": "Not accepted",
}


def plain(value: object) -> str:
    raw = str(value or "not recorded")
    return PLAIN.get(raw, raw.replace("_", " ").lower())


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def natural_id(value: object) -> tuple[str, int]:
    match = re.match(r"^(.*?)([0-9]+)$", str(value))
    return (match.group(1), int(match.group(2))) if match else (str(value), 0)


def safe_href(value: str | None) -> str | None:
    if value and value.startswith(("https://", "http://")):
        return value
    return None


def successful_check(value: object) -> bool:
    normalized = str(value).strip().upper()
    result = normalized.rsplit(":", 1)[-1].strip()
    return ":" in normalized and result in {"PASSED", "PASS", "SUCCESS", "SUCCEEDED"}


def failed_check(value: object) -> bool:
    """Fail closed: pending, unknown, and malformed results are blockers too."""
    return not successful_check(value)


def review_has_blocker(
    review: dict[str, Any] | None,
    checks: list[str] | None,
    pr_state: str | None,
    mergeability: str | None,
) -> bool:
    return bool(
        not checks
        or any(failed_check(item) for item in checks)
        or str(pr_state or "").upper() != "OPEN"
        or str(mergeability or "").upper() not in {"MERGEABLE", "CLEAN"}
        or not isinstance(review, dict)
        or review.get("verdict") != "APPROVE"
        or any(
            isinstance(item, dict) and item.get("status") != "MET"
            for item in (review or {}).get("acceptanceCriteria", [])
        )
    )


def decision_key(decision: dict[str, Any]) -> tuple[int, int, tuple[str, int]]:
    return (
        RISK_ORDER.get(str(decision.get("riskClass")), 9),
        STATUS_ORDER.get(str(decision.get("status")), 9),
        natural_id(decision.get("id")),
    )


def criterion_key(criterion: dict[str, Any]) -> tuple[int, tuple[str, int]]:
    return (PRIORITY_ORDER.get(str(criterion.get("priority")), 9), natural_id(criterion.get("id")))


def chosen_label(decision: dict[str, Any], option_id: object) -> str:
    for option in decision.get("options", []):
        if option.get("id") == option_id:
            return f"{option_id} — {option.get('label')}"
    return str(option_id or "not decided")


def attention_decisions(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    decisions = sorted(manifest.get("decisions", []), key=decision_key)
    changed_ids = {
        decision_id
        for change in manifest.get("semanticChanges", [])
        if change.get("status") != "REJECTED"
        for decision_id in change.get("affectedDecisionIds", [])
    }
    attention = [
        item for item in decisions
        if item.get("riskClass") == "HUMAN_REQUIRED"
        and (item.get("status") != "RESOLVED" or item.get("id") in changed_ids)
    ]
    quiet = [item for item in decisions if item not in attention]
    return attention, quiet


def gate_action(
    manifest: dict[str, Any],
    phase: str,
    review: dict[str, Any] | None,
    checks: list[str] | None = None,
    pr_state: str | None = None,
    mergeability: str | None = None,
) -> str:
    if phase == "review":
        if not checks:
            return "Stop: no live pull-request checks were supplied."
        failures = [item for item in checks or [] if failed_check(item)]
        if failures:
            return f"Stop: {len(failures)} pull-request check(s) are not explicitly successful. Read the evidence and request a correction."
        if str(pr_state or "").upper() != "OPEN":
            return f"Stop: the pull request state is {pr_state or 'not supplied'}, not open."
        if str(mergeability or "").upper() not in {"MERGEABLE", "CLEAN"}:
            return f"Stop: the pull request is {mergeability or 'not supplied'}, not confirmed mergeable."
    attention, _ = attention_decisions(manifest)
    conflicts = [
        conflict
        for decision in manifest.get("decisions", [])
        for conflict in decision.get("conflicts", [])
        if conflict.get("status") == "OPEN"
    ]
    batches = [item for item in manifest.get("feedbackBatches", []) if item.get("status") == "OPEN"]
    scenarios = [item for item in manifest.get("testScenarios", []) if item.get("status") != "HUMAN_CONFIRMED"]
    if attention or conflicts or batches or scenarios:
        return (
            f"Check {len(attention)} open or changed choice(s), {len(conflicts)} source conflict(s), "
            f"{len(scenarios)} unconfirmed test scenario(s), and {len(batches)} incomplete feedback batch(es)."
        )
    if phase == "review" and review:
        if review.get("verdict") == "ASK_HUMAN":
            return "Resolve the focused human question. The original implementation has been preserved."
        return f"Check the proven implementation and approve or request changes. Agent result: {plain(review.get('verdict'))}."
    return "Read the full design and its promises, challenge the scenarios, then approve or request changes."


def render_markdown(
    manifest: dict[str, Any],
    phase: str,
    review: dict[str, Any] | None = None,
    pr_url: str | None = None,
    pr_state: str | None = None,
    mergeability: str | None = None,
    changed_files: list[str] | None = None,
    checks: list[str] | None = None,
) -> str:
    attention, quiet = attention_decisions(manifest)
    criteria = sorted(manifest.get("acceptanceCriteria", []), key=criterion_key)
    scenarios = sorted(manifest.get("testScenarios", []), key=lambda item: natural_id(item.get("id")))
    rules = sorted(manifest.get("applicableRules", []), key=lambda item: natural_id(item.get("id")))
    changes = sorted(manifest.get("semanticChanges", []), key=lambda item: natural_id(item.get("id")))
    batches = sorted(manifest.get("feedbackBatches", []), key=lambda item: natural_id(item.get("id")))
    detail_prefix = "" if phase == "alignment" else "../2-specification/"
    title = "PR approval pack" if phase == "review" else "Design approval pack"
    review_ac = {
        item.get("id"): item
        for item in (review or {}).get("acceptanceCriteria", [])
        if isinstance(item, dict)
    }
    lines = [
        f"# {title} — {md(manifest.get('ticket'))}",
        "",
        f"> **What to do:** {md(gate_action(manifest, phase, review, checks, pr_state, mergeability))}",
        "",
        "## Reading route",
        "",
        f"1. Read the [full target solution]({detail_prefix}03-target-solution.view.html).",
        "2. Check every acceptance criterion below, starting with Critical.",
        "3. Resolve only the open or changed choices.",
        "4. Challenge the test scenarios.",
        "5. Give the explicit final decision.",
        "",
    ]
    if phase == "review":
        lines.extend([
            "## Live pull-request facts",
            "",
            f"- **URL:** {md(pr_url or 'not supplied')}",
            f"- **State:** {md(pr_state or 'not supplied')}",
            f"- **Can merge:** {md(mergeability or 'not supplied')}",
            "",
            "### Checks",
            "",
        ])
        for check in sorted(checks or []):
            marker = "BLOCKER" if failed_check(check) else "Result"
            lines.append(f"- **{marker}:** {md(check)}")
        if not checks:
            lines.append("- **BLOCKER:** No live checks were supplied.")
        lines.extend(["", "### Changed files", ""])
        for path in sorted(changed_files or []):
            lines.append(f"- `{md(path)}`")
        if not changed_files:
            lines.append("- **BLOCKER:** No changed files were supplied.")
        lines.append("")
    lines.extend(["## Acceptance criteria — what the delivery promises", ""])
    for criterion in criteria:
        assessment = review_ac.get(criterion.get("id"), {})
        lines.extend([
            f"### {md(criterion.get('id'))} · {md(str(criterion.get('priority')).title())} · {md(criterion.get('shortMeaning'))}",
            "",
            f"- **Why it matters:** {md(criterion.get('whyItMatters'))}",
            f"- **Exact ticket wording:** {md(criterion.get('text'))}",
            f"- **State:** {md(plain(criterion.get('status')))}",
        ])
        if assessment:
            lines.extend([
                f"- **Implementation result:** {md(plain(assessment.get('status')))}",
                f"- **Evidence:** {'; '.join(md(item) for item in assessment.get('evidence', []))}",
            ])
        lines.append("")
    if not criteria:
        lines.extend(["No acceptance criteria recorded. Approval is blocked.", ""])

    if phase == "review" and review:
        lines.extend(["## Implementation review", ""])
        if pr_url:
            lines.append(f"- **Pull request:** {md(pr_url)}")
        lines.extend([
            f"- **Result:** {md(plain(review.get('verdict')))}",
            f"- **Original implementation:** `{md(review.get('baseline', {}).get('implementationCommit'))}`",
            f"- **Final commit:** `{md(review.get('finalCommit') or 'original preserved; waiting for human')}`",
            f"- **Selected trial fix:** {md(review.get('selectedTrialFixId') or 'none')}",
        ])
        final_check = review.get("finalFullCheck") or {}
        if final_check:
            lines.append(f"- **Final full check:** {md(final_check.get('result'))} on `{md(final_check.get('commit'))}` with `{md(final_check.get('command'))}`")
        lines.extend(["", "### Findings and evidence checks", ""])
        findings = sorted(review.get("findings", []), key=lambda item: natural_id(item.get("id")))
        if not findings:
            lines.append("No defect findings.")
        for finding in findings:
            evidence_check = finding.get("evidenceCheck") or {}
            lines.extend([
                f"#### {md(finding.get('id'))} · {md(plain(evidence_check.get('result')))} · {md(finding.get('problem'))}",
                "",
                f"- **Evidence:** {'; '.join(md(item) for item in finding.get('evidence', []))}",
                f"- **Why:** {md(evidence_check.get('reason') or 'not checked yet')}",
                f"- **Path:** {md(plain(evidence_check.get('path')))}",
                f"- **Trial fix:** {md(evidence_check.get('trialFixId') or 'none')}",
                "",
            ])
        lines.extend(["### Trial fixes", ""])
        if not review.get("trialFixes"):
            lines.append("No trial fix was needed.")
        for trial in review.get("trialFixes", []):
            lines.append(
                f"- **{md(trial.get('id'))}:** findings {md(', '.join(trial.get('findingIds', [])))} · "
                f"{md(plain(trial.get('path')))} · {md(plain(trial.get('comparison')))} · commit `{md(trial.get('commit') or 'not built')}`"
            )
        lines.append("")

    lines.extend(["## Open or changed human choices", ""])
    if not attention:
        lines.append("No open or changed human choices.")
    for decision in attention:
        resolution = decision.get("resolution") or {}
        lines.extend([
            f"### {md(decision.get('id'))} · {md(plain(decision.get('status')))} · {md(decision.get('title'))}",
            "",
            f"**Question:** {md(decision.get('question'))}",
            "",
            f"- **Recommendation:** {md(chosen_label(decision, decision.get('recommendation', {}).get('optionId')))} — {md(decision.get('recommendation', {}).get('rationale'))}",
            f"- **Strongest reason against it:** {md(decision.get('recommendation', {}).get('counterargument'))}",
            f"- **Recorded choice:** {md(chosen_label(decision, resolution.get('optionId')))}",
            "",
            "| Option | What happens if chosen |",
            "|---|---|",
        ])
        for option in decision.get("options", []):
            lines.append(f"| {md(option.get('id'))} — {md(option.get('label'))} | {md(option.get('consequence'))} |")
        lines.append("")

    conflicts = [
        (decision.get("id"), conflict)
        for decision in manifest.get("decisions", [])
        for conflict in decision.get("conflicts", [])
        if conflict.get("status") == "OPEN"
    ]
    deviations = [
        rule for rule in rules
        if rule.get("status") in {"DEVIATION_APPROVED", "UNRESOLVED"}
        or rule.get("classification") in {"MISSING", "CONFLICTING"}
    ]
    open_batches = [batch for batch in batches if batch.get("status") == "OPEN"]
    if conflicts or changes or deviations or open_batches:
        lines.extend(["## Changes and conflicts that need attention", ""])
        for decision_id, conflict in conflicts:
            lines.append(f"- **{md(decision_id)}:** {md(conflict.get('issue'))} — {md(conflict.get('consequence'))}")
        for change in changes:
            lines.append(f"- **{md(change.get('id'))} / {md(plain(change.get('status')))}:** {md(change.get('summary'))}")
        for rule in deviations:
            lines.append(
                f"- **{md(rule.get('id'))} / {md(plain(rule.get('classification')))}:** "
                f"{md(rule.get('exactRule'))} — {md(rule.get('rationale'))}"
            )
        for batch in open_batches:
            lines.append(
                f"- **{md(batch.get('id'))} / incomplete feedback:** {md(batch.get('processedItems'))} of "
                f"{md(batch.get('expectedItems'))} processed; open: "
                f"{md('; '.join(batch.get('unresolvedItems', [])) or 'not named')}"
            )
        lines.append("")

    lines.extend([
        "## Test-scenario challenge",
        "",
        "**Which of these are wrong, and what is missing?**",
        "",
        "| Scenario | Expected behavior | State |",
        "|---|---|---|",
    ])
    for scenario in scenarios:
        lines.append(f"| {md(scenario.get('id'))} — {md(scenario.get('title'))} | {md(scenario.get('behavior'))} | {md(plain(scenario.get('status')))} |")
    if not scenarios:
        lines.append("| — | No test scenarios recorded | PROPOSED |")

    blocked = phase == "review" and review_has_blocker(review, checks, pr_state, mergeability)
    if phase == "review" and blocked:
        final_choices = [
            "- **B (recommended):** Pause and request changes to: `<name the failed check, criterion, or defect>`.",
            "- **Approval is unavailable** until every blocker is cleared and the page is regenerated from fresh PR facts.",
        ]
    elif phase == "review":
        final_choices = [
            "- **A:** I approve this package and continue to the explicit merge step.",
            "- **B:** I request changes to: `<name the item>`.",
        ]
    else:
        final_choices = [
            "- **A:** I approve the target solution, acceptance criteria, recorded choices, and test scenarios.",
            "- **B:** I request changes to: `<name the item>`.",
        ]

    lines.extend([
        "",
        "## Final decision",
        "",
        *final_choices,
        "",
        "## Technical record — optional drill-down",
        "",
        f"- Lower-risk decisions: {len(quiet)}",
        f"- Applicable rules: {len(rules)}",
        f"- Feedback batches: {len(batches)}",
    ])
    if changed_files:
        lines.append(f"- Changed files: {len(changed_files)}")
    if checks:
        lines.append(f"- Extra checks: {'; '.join(md(item) for item in sorted(checks))}")
    lines.extend([
        "",
        f"- [Agreement]({detail_prefix}03-agreement.spec.md)",
        f"- [Target solution source]({detail_prefix}03-target-solution.spec.md)",
        f"- [Test scenarios]({detail_prefix}03-test-scenarios.spec.md)",
        f"- [Machine state]({detail_prefix}03-decision-manifest.state.json)",
        "",
        "---",
        "This view is generated; do not edit it.",
        "",
    ])
    return "\n".join(lines)


def render_html(
    manifest: dict[str, Any],
    phase: str,
    review: dict[str, Any] | None = None,
    pr_url: str | None = None,
    pr_state: str | None = None,
    mergeability: str | None = None,
    changed_files: list[str] | None = None,
    checks: list[str] | None = None,
) -> str:
    attention, quiet = attention_decisions(manifest)
    criteria = sorted(manifest.get("acceptanceCriteria", []), key=criterion_key)
    scenarios = sorted(manifest.get("testScenarios", []), key=lambda item: natural_id(item.get("id")))
    rules = sorted(manifest.get("applicableRules", []), key=lambda item: natural_id(item.get("id")))
    changes = sorted(manifest.get("semanticChanges", []), key=lambda item: natural_id(item.get("id")))
    batches = sorted(manifest.get("feedbackBatches", []), key=lambda item: natural_id(item.get("id")))
    detail_prefix = "" if phase == "alignment" else "../2-specification/"
    esc = lambda value: html.escape(str(value), quote=True)
    review_ac = {
        item.get("id"): item
        for item in (review or {}).get("acceptanceCriteria", [])
        if isinstance(item, dict)
    }

    criterion_cards = "".join(
        f"<article class='promise {esc(str(item.get('priority')).lower())}'><div class=eyebrow>{esc(item.get('id'))} · {esc(str(item.get('priority')).title())}</div>"
        f"<h3>{esc(item.get('shortMeaning'))}</h3><p><b>Why it matters:</b> {esc(item.get('whyItMatters'))}</p>"
        f"<p><b>Exact ticket wording:</b> {esc(item.get('text'))}</p><p class=muted>Design state: {esc(plain(item.get('status')))}</p>"
        + (
            f"<p><b>Implementation result:</b> {esc(plain(review_ac[item.get('id')].get('status')))}</p>"
            f"<p><b>Evidence:</b> {esc('; '.join(review_ac[item.get('id')].get('evidence', [])))}</p>"
            if item.get("id") in review_ac else ""
        )
        + "</article>"
        for item in criteria
    ) or "<p class=blocker>No acceptance criteria recorded. Approval is blocked.</p>"

    decision_cards: list[str] = []
    for decision in attention:
        resolution = decision.get("resolution") or {}
        options = "".join(
            f"<tr><td>{esc(option.get('id'))} — {esc(option.get('label'))}</td><td>{esc(option.get('consequence'))}</td></tr>"
            for option in decision.get("options", [])
        )
        decision_cards.append(
            f"<article class='choice'><div class=eyebrow>{esc(decision.get('id'))} · {esc(plain(decision.get('status')))}</div>"
            f"<h3>{esc(decision.get('title'))}</h3><p class=question>{esc(decision.get('question'))}</p>"
            f"<p><b>Recommendation:</b> {esc(chosen_label(decision, decision.get('recommendation', {}).get('optionId')))} — {esc(decision.get('recommendation', {}).get('rationale'))}</p>"
            f"<p><b>Strongest reason against it:</b> {esc(decision.get('recommendation', {}).get('counterargument'))}</p>"
            f"<p><b>Recorded choice:</b> {esc(chosen_label(decision, resolution.get('optionId')))}</p>"
            f"<table><thead><tr><th>Option</th><th>What happens if chosen</th></tr></thead><tbody>{options}</tbody></table></article>"
        )

    attention_items = []
    for decision in manifest.get("decisions", []):
        for conflict in decision.get("conflicts", []):
            if conflict.get("status") == "OPEN":
                attention_items.append(f"<li><b>{esc(decision.get('id'))}:</b> {esc(conflict.get('issue'))} — {esc(conflict.get('consequence'))}</li>")
    for change in changes:
        attention_items.append(f"<li><b>{esc(change.get('id'))} / {esc(plain(change.get('status')))}:</b> {esc(change.get('summary'))}</li>")
    for rule in rules:
        if rule.get("status") in {"DEVIATION_APPROVED", "UNRESOLVED"} or rule.get("classification") in {"MISSING", "CONFLICTING"}:
            attention_items.append(
                f"<li><b>{esc(rule.get('id'))} · {esc(plain(rule.get('classification')))}:</b> "
                f"{esc(rule.get('exactRule'))} — {esc(rule.get('rationale'))}</li>"
            )
    for batch in batches:
        if batch.get("status") == "OPEN":
            attention_items.append(
                f"<li><b>{esc(batch.get('id'))} · incomplete feedback:</b> "
                f"{esc(batch.get('processedItems'))} of {esc(batch.get('expectedItems'))} item(s) processed; "
                f"open: {esc('; '.join(batch.get('unresolvedItems', [])) or 'not named')}</li>"
            )

    scenario_rows = "".join(
        f"<tr><td>{esc(item.get('id'))} — {esc(item.get('title'))}</td><td>{esc(item.get('behavior'))}</td><td>{esc(plain(item.get('status')))}</td></tr>"
        for item in scenarios
    ) or "<tr><td>—</td><td>No test scenarios recorded</td><td>PROPOSED</td></tr>"

    review_section = ""
    pr_facts = ""
    if phase == "review" and review:
        finding_items = "".join(
            f"<li><b>{esc(item.get('id'))} · {esc(plain((item.get('evidenceCheck') or {}).get('result')))}:</b> "
            f"{esc(item.get('problem'))} — {esc((item.get('evidenceCheck') or {}).get('reason') or 'not checked yet')} "
            f"<span class=muted>({esc(plain((item.get('evidenceCheck') or {}).get('path')))})</span></li>"
            for item in sorted(review.get("findings", []), key=lambda value: natural_id(value.get("id")))
        ) or "<li>No defect findings.</li>"
        trial_items = "".join(
            f"<li><b>{esc(item.get('id'))}:</b> findings {esc(', '.join(item.get('findingIds', [])))} · "
            f"{esc(plain(item.get('path')))} · {esc(plain(item.get('comparison')))} · <code>{esc(item.get('commit') or 'not built')}</code></li>"
            for item in review.get("trialFixes", [])
        ) or "<li>No trial fix was needed.</li>"
        final_check = review.get("finalFullCheck") or {}
        final_check_text = (
            f"{esc(final_check.get('result'))} on <code>{esc(final_check.get('commit'))}</code> with <code>{esc(final_check.get('command'))}</code>"
            if final_check else "not run; waiting for a human decision"
        )
        safe_pr = safe_href(pr_url)
        pr_link = f"<p><a href='{esc(safe_pr)}'>Open pull request</a></p>" if safe_pr else ""
        check_items = "".join(
            f"<li class='{'blocker' if failed_check(item) else ''}'>{esc(item)}</li>"
            for item in sorted(checks or [])
        ) or "<li class=blocker>No live checks were supplied.</li>"
        file_items = "".join(
            f"<li><code>{esc(item)}</code></li>" for item in sorted(changed_files or [])
        ) or "<li class=blocker>No changed files were supplied.</li>"
        pr_facts = (
            "<section><h2>Live pull-request facts</h2>" + pr_link
            + f"<div class=stats><div><b>{esc(pr_state or 'not supplied')}</b><span>PR state</span></div>"
            + f"<div><b>{esc(mergeability or 'not supplied')}</b><span>can merge</span></div>"
            + f"<div><b>{len(checks or [])}</b><span>checks</span></div>"
            + f"<div><b>{len(changed_files or [])}</b><span>changed files</span></div></div>"
            + f"<h3>Checks</h3><ul>{check_items}</ul><h3>Changed files</h3><ul>{file_items}</ul></section>"
        )
        review_section = (
            "<section><h2>Implementation review</h2>" + pr_link
            + f"<div class=stats><div><b>{esc(plain(review.get('verdict')))}</b><span>result</span></div>"
            + f"<div><b>{esc(review.get('baseline', {}).get('implementationCommit'))}</b><span>original implementation</span></div>"
            + f"<div><b>{esc(review.get('finalCommit') or 'preserved')}</b><span>final commit</span></div>"
            + f"<div><b>{esc(review.get('selectedTrialFixId') or 'none')}</b><span>selected trial fix</span></div></div>"
            + f"<p><b>Final full check:</b> {final_check_text}</p><h3>Findings and evidence checks</h3><ul>{finding_items}</ul>"
            + f"<h3>Trial fixes</h3><ul>{trial_items}</ul></section>"
        )

    title = "PR approval pack" if phase == "review" else "Design approval pack"
    blocked = phase == "review" and review_has_blocker(review, checks, pr_state, mergeability)
    if phase == "review" and blocked:
        final_decision = (
            "<p><b>B (recommended):</b> Pause and request changes to the failed check, criterion, or defect.</p>"
            "<p><b>Approval is unavailable</b> until every blocker is cleared and the page is regenerated from fresh PR facts.</p>"
        )
    elif phase == "review":
        final_decision = (
            "<p><b>A:</b> I approve this package and continue to the explicit merge step.</p>"
            "<p><b>B:</b> I request changes to: <code>&lt;name the item&gt;</code>.</p>"
        )
    else:
        final_decision = (
            "<p><b>A:</b> I approve the target solution, acceptance criteria, recorded choices, and test scenarios.</p>"
            "<p><b>B:</b> I request changes to: <code>&lt;name the item&gt;</code>.</p>"
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — {esc(manifest.get('ticket'))}</title><style>
:root{{--ink:#18212f;--muted:#667085;--line:#d0d5dd;--paper:#f7f9fc;--card:#fff;--critical:#b42318;--important:#b54708;--supporting:#175cd3;--accent:#175cd3}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.58 system-ui,-apple-system,sans-serif}}main{{max-width:1040px;margin:auto;padding:32px 20px 64px}}h1{{font-size:32px;margin:0 0 12px}}h2{{margin-top:40px;border-bottom:1px solid var(--line);padding-bottom:8px}}h3{{margin:.25rem 0 .5rem}}a{{color:var(--accent)}}.action{{background:#fff4ed;border-left:5px solid #f79009;padding:16px 18px;font-size:17px}}.route{{background:#eef4ff;border:1px solid #b2ccff;border-radius:12px;padding:16px 20px;margin:18px 0}}.route li{{margin:7px 0}}.promise,.choice{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:14px 0}}.promise.critical{{border-left:6px solid var(--critical)}}.promise.important{{border-left:6px solid var(--important)}}.promise.supporting{{border-left:6px solid var(--supporting)}}.choice{{border-left:6px solid var(--critical)}}.eyebrow{{font-weight:750;color:#475467;font-size:12px;letter-spacing:.05em;text-transform:uppercase}}.question{{font-size:17px}}.muted{{color:var(--muted);font-size:13px}}.blocker{{background:#fef3f2;border:1px solid #fecdca;padding:14px}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:10px;margin:18px 0}}.stats div{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}.stats b{{display:block;overflow-wrap:anywhere}}.stats span{{color:var(--muted);font-size:13px}}table{{width:100%;border-collapse:collapse;margin:12px 0;background:var(--card)}}th,td{{border:1px solid var(--line);padding:9px;text-align:left;vertical-align:top}}th{{background:#eef2f6}}details{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:10px 0}}summary{{cursor:pointer;font-weight:700}}code{{overflow-wrap:anywhere}}
</style></head><body><main><h1>{esc(title)} — {esc(manifest.get('ticket'))}</h1><div class=action><b>What to do:</b> {esc(gate_action(manifest, phase, review, checks, pr_state, mergeability))}</div>
<section class=route><h2>Reading route</h2><ol><li><a href="{detail_prefix}03-target-solution.view.html"><b>Read the full target solution.</b></a></li><li>Check every acceptance criterion, starting with Critical.</li><li>Resolve only the open or changed choices.</li><li>Challenge the test scenarios.</li><li>Give the explicit final decision.</li></ol></section>
{pr_facts}
<section><h2>Acceptance criteria — what the delivery promises</h2>{criterion_cards}</section>
{review_section}
<section><h2>Open or changed human choices</h2>{''.join(decision_cards) or '<p>No open or changed human choices.</p>'}</section>
{f"<section><h2>Changes and conflicts that need attention</h2><ul>{''.join(attention_items)}</ul></section>" if attention_items else ''}
<section><h2>Test-scenario challenge</h2><p class=question><b>Which of these are wrong, and what is missing?</b></p><table><thead><tr><th>Scenario</th><th>Expected behavior</th><th>State</th></tr></thead><tbody>{scenario_rows}</tbody></table></section>
<section><h2>Final decision</h2>{final_decision}</section>
<details><summary>Technical record — optional drill-down</summary><p>Lower-risk decisions: {len(quiet)} · applicable rules: {len(rules)} · feedback batches: {len(batches)} · changed files supplied: {len(changed_files or [])}</p><ul><li><a href="{detail_prefix}03-agreement.spec.md">Agreement</a></li><li><a href="{detail_prefix}03-target-solution.spec.md">Target solution source</a></li><li><a href="{detail_prefix}03-test-scenarios.spec.md">Test scenarios</a></li><li><a href="{detail_prefix}03-decision-manifest.state.json">Machine state</a></li></ul></details>
<p class=muted>This view is generated; do not edit it.</p></main></body></html>"""


def load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--phase", choices=("alignment", "review"), required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--review-state", type=Path)
    parser.add_argument("--pr-url")
    parser.add_argument("--pr-state")
    parser.add_argument("--mergeability")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--check", action="append", default=[])
    args = parser.parse_args()
    manifest = load_json(args.manifest)
    review = load_json(args.review_state)
    if args.phase == "review" and review is None:
        parser.error("--review-state is required for review phase")
    if args.phase == "review":
        if not args.pr_url or not args.pr_state or not args.mergeability:
            parser.error("--pr-url, --pr-state and --mergeability are required for review phase")
        if not args.changed_file or not args.check:
            parser.error("at least one --changed-file and --check are required for review phase")
    markdown = render_markdown(
        manifest or {}, args.phase, review, args.pr_url, args.pr_state, args.mergeability,
        args.changed_file, args.check,
    )
    page = render_html(
        manifest or {}, args.phase, review, args.pr_url, args.pr_state, args.mergeability,
        args.changed_file, args.check,
    )
    args.markdown.write_text(markdown, encoding="utf-8")
    args.html.write_text(page, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

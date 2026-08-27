#!/usr/bin/env python3
"""Render deterministic human decision gates from canonical SDLC state."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


RISK_ORDER = {"HUMAN_REQUIRED": 0, "SAMPLED": 1, "AGENT_OWNED": 2}
STATUS_ORDER = {"OPEN": 0, "DEFERRED": 1, "RESOLVED": 2}


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def natural_id(value: object) -> tuple[str, int]:
    match = re.match(r"^(.*?)([0-9]+)$", str(value))
    return (match.group(1), int(match.group(2))) if match else (str(value), 0)


def safe_href(value: str | None) -> str | None:
    if value and value.startswith(("https://", "http://")):
        return value
    return None


def decision_key(decision: dict[str, Any]) -> tuple[int, int, tuple[str, int]]:
    return (
        RISK_ORDER.get(str(decision.get("riskClass")), 9),
        STATUS_ORDER.get(str(decision.get("status")), 9),
        natural_id(decision.get("id")),
    )


def chosen_label(decision: dict[str, Any], option_id: object) -> str:
    for option in decision.get("options", []):
        if option.get("id") == option_id:
            return f"{option_id} — {option.get('label')}"
    return str(option_id or "not decided")


def gate_action(manifest: dict[str, Any], phase: str, review: dict[str, Any] | None) -> str:
    human_open = [
        item for item in manifest.get("decisions", [])
        if item.get("riskClass") == "HUMAN_REQUIRED" and item.get("status") != "RESOLVED"
    ]
    open_conflicts = [
        conflict
        for decision in manifest.get("decisions", [])
        for conflict in decision.get("conflicts", [])
        if conflict.get("status") == "OPEN"
    ]
    open_batches = [item for item in manifest.get("feedbackBatches", []) if item.get("status") == "OPEN"]
    open_scenarios = [item for item in manifest.get("testScenarios", []) if item.get("status") != "HUMAN_CONFIRMED"]
    if human_open or open_conflicts or open_batches or open_scenarios:
        return f"Resolve {len(human_open)} human decision(s), {len(open_conflicts)} source conflict(s), {len(open_scenarios)} unconfirmed test scenario(s), and {len(open_batches)} incomplete feedback batch(es)."
    if phase == "review" and review:
        verdict = review.get("verdict", "unknown")
        if verdict == "ESCALATED":
            return "Resolve the focused escalated decision; the implementation baseline has been preserved."
        return f"Review the proven implementation state and explicitly approve or request changes. Agent verdict: {verdict}."
    if manifest.get("approval", {}).get("status") == "REOPENED":
        return "Review the highlighted semantic delta and re-approve the affected decisions."
    return "Confirm the human-required choices, conflicts, rule handling, and scenario coverage; then explicitly approve or request changes."


def render_markdown(
    manifest: dict[str, Any],
    phase: str,
    review: dict[str, Any] | None = None,
    pr_url: str | None = None,
    changed_files: list[str] | None = None,
    checks: list[str] | None = None,
) -> str:
    decisions = sorted(manifest.get("decisions", []), key=decision_key)
    human = [item for item in decisions if item.get("riskClass") == "HUMAN_REQUIRED"]
    agent = [item for item in decisions if item.get("riskClass") != "HUMAN_REQUIRED"]
    rules = sorted(manifest.get("applicableRules", []), key=lambda item: natural_id(item.get("id")))
    changes = sorted(manifest.get("semanticChanges", []), key=lambda item: natural_id(item.get("id")))
    criteria = sorted(manifest.get("acceptanceCriteria", []), key=lambda item: natural_id(item.get("id")))
    scenarios = sorted(manifest.get("testScenarios", []), key=lambda item: natural_id(item.get("id")))
    batches = sorted(manifest.get("feedbackBatches", []), key=lambda item: natural_id(item.get("id")))
    approval = manifest.get("approval", {})
    detail_prefix = "" if phase == "alignment" else "../2-specification/"

    lines = [
        f"# Human {'PR review' if phase == 'review' else 'design decision'} gate — {md(manifest.get('ticket'))}",
        "",
        f"> **Action required:** {md(gate_action(manifest, phase, review))}",
        "",
        "## At a glance",
        "",
        "| State | Value |",
        "|---|---|",
        f"| Approval | {md(approval.get('status'))} |",
        f"| Human-required decisions | {sum(item.get('status') != 'RESOLVED' for item in human)} open / {len(human)} total |",
        f"| Agent-owned or sampled decisions | {len(agent)} |",
        f"| Applicable rules | {len(rules)} |",
        f"| Test scenarios | {sum(item.get('status') != 'HUMAN_CONFIRMED' for item in scenarios)} unconfirmed / {len(scenarios)} total |",
        f"| Semantic changes | {len(changes)} |",
        f"| Feedback batches | {sum(item.get('status') == 'OPEN' for item in batches)} open / {len(batches)} total |",
        "",
    ]

    if phase == "review" and review:
        lines.extend(["## Implementation review", ""])
        if pr_url:
            lines.append(f"- **Pull request:** {md(pr_url)}")
        lines.extend([
            f"- **Verdict:** {md(review.get('verdict'))}",
            f"- **Baseline:** `{md(review.get('baseline', {}).get('implementationCommit'))}`",
            f"- **Final commit:** `{md(review.get('finalCommit') or 'baseline preserved / not publishable')}`",
        ])
        if checks:
            lines.append(f"- **Checks:** {' · '.join(md(item) for item in sorted(checks))}")
        if changed_files:
            lines.extend(["", "### Changed files", ""] + [f"- `{md(path)}`" for path in sorted(changed_files)])
        claims = sorted(review.get("claims", []), key=lambda item: natural_id(item.get("id")))
        lines.extend(["", "### Acceptance criteria against the implementation", "", "| AC | Verbatim criterion | Review status | Evidence |", "|---|---|---|---|"])
        for criterion in sorted(review.get("acceptanceCriteria", []), key=lambda item: natural_id(item.get("id"))):
            lines.append(f"| {md(criterion.get('id'))} | {md(criterion.get('text'))} | {md(criterion.get('status'))} | {md('; '.join(criterion.get('evidence', [])))} |")
        lines.extend(["", "### Review claims and dispositions", ""])
        if not claims:
            lines.append("No defect claims.")
        for claim in claims:
            adjudication = claim.get("adjudication") or {}
            candidate = claim.get("candidate") or {}
            lines.extend([
                f"#### {md(claim.get('id'))} — {md(adjudication.get('disposition') or 'not adjudicated')} — {md(claim.get('problem'))}",
                "",
                f"- **Evidence:** {'; '.join(md(item) for item in claim.get('evidence', []))}",
                f"- **Why:** {md(adjudication.get('rationale') or 'not adjudicated')}",
                f"- **Candidate comparison:** {md(candidate.get('comparison') or 'none; baseline retained')}",
                "",
            ])

    lines.extend(["## Decisions requiring human accountability", ""])
    if not human:
        lines.append("No human-required decisions were classified.")
    for decision in human:
        resolution = decision.get("resolution") or {}
        lines.extend([
            f"### {md(decision.get('id'))} — {md(decision.get('status'))} — {md(decision.get('title'))}",
            "",
            f"**Question:** {md(decision.get('question'))}",
            "",
            f"- **Risk:** {', '.join(md(item) for item in decision.get('riskDimensions', [])) or 'not classified'}",
            f"- **Recommendation:** {md(chosen_label(decision, decision.get('recommendation', {}).get('optionId')))} — {md(decision.get('recommendation', {}).get('rationale'))}",
            f"- **Strongest counterargument:** {md(decision.get('recommendation', {}).get('counterargument'))}",
            f"- **Recorded choice:** {md(chosen_label(decision, resolution.get('optionId')))}{(' — ' + md(resolution.get('rationale'))) if resolution else ''}",
            "",
            "| Option | Consequence |",
            "|---|---|",
        ])
        for option in decision.get("options", []):
            lines.append(f"| {md(option.get('id'))} — {md(option.get('label'))} | {md(option.get('consequence'))} |")
        lines.extend(["", "**Decision evidence:**"])
        for source in decision.get("sources", []):
            lines.append(f"- `{md(source.get('kind'))}` / `{md(source.get('authority'))}` — {md(source.get('claim'))} ({md(source.get('reference'))})")
        lines.append("")

    conflicts = [
        (decision.get("id"), conflict)
        for decision in decisions
        for conflict in decision.get("conflicts", [])
    ]
    deviations = [item for item in rules if item.get("status") in {"DEVIATION_APPROVED", "UNRESOLVED"} or item.get("classification") in {"MISSING", "CONFLICTING"}]
    lines.extend(["## Source conflicts and rule deviations", ""])
    if not conflicts and not deviations:
        lines.append("None recorded.")
    for decision_id, conflict in conflicts:
        lines.append(f"- **{md(decision_id)} / {md(conflict.get('status'))}:** {md(conflict.get('issue'))} — consequence: {md(conflict.get('consequence'))}; resolution: {md(conflict.get('resolution') or 'open')}")
    for rule in deviations:
        lines.append(f"- **{md(rule.get('id'))} / {md(rule.get('classification'))} / {md(rule.get('status'))}:** {md(rule.get('exactRule'))} — {md(rule.get('rationale'))} ({md(rule.get('article'))})")
    lines.append("")

    lines.extend(["## Semantic changes since alignment", ""])
    if not changes:
        lines.append("None recorded.")
    for change in changes:
        lines.append(f"- **{md(change.get('id'))} / {md(change.get('discoveredAt'))} / {md(change.get('status'))}:** {md(change.get('summary'))}")
    lines.extend(["", "## Acceptance-criteria coverage", "", "| AC | Verbatim criterion | Decision mapping | Status |", "|---|---|---|---|"])
    for criterion in criteria:
        mapping = ", ".join(criterion.get("decisionIds", [])) or "none"
        lines.append(f"| {md(criterion.get('id'))} | {md(criterion.get('text'))} | {md(mapping)} | {md(criterion.get('status'))} |")
    if not criteria:
        lines.append("| — | No acceptance criteria recorded | — | UNRESOLVED |")

    lines.extend(["", "## Test-scenario challenge", "", "**Which of these are wrong, and what is missing?**", "", "| Scenario | Behavior | Decision mapping | Status |", "|---|---|---|---|"])
    for scenario in scenarios:
        mapping = ", ".join(scenario.get("decisionIds", [])) or "none"
        lines.append(f"| {md(scenario.get('id'))} — {md(scenario.get('title'))} | {md(scenario.get('behavior'))} | {md(mapping)} | {md(scenario.get('status'))} |")
    if not scenarios:
        lines.append("| — | No test scenarios recorded | — | PROPOSED |")

    lines.extend(["", "## Feedback ingestion", "", "| Batch | Source | Processed | State | Unresolved |", "|---|---|---:|---|---|"])
    for batch in batches:
        unresolved = "; ".join(batch.get("unresolvedItems", [])) or "none"
        lines.append(f"| {md(batch.get('id'))} | {md(batch.get('source'))} | {batch.get('processedItems')} / {batch.get('expectedItems')} | {md(batch.get('status'))} | {md(unresolved)} |")
    if not batches:
        lines.append("| — | No batch feedback used | 0 / 0 | COMPLETE | none |")

    lines.extend(["", "## Verified lower-risk decisions", ""])
    if not agent:
        lines.append("None recorded.")
    for decision in agent:
        resolution = decision.get("resolution") or {}
        lines.append(f"- **{md(decision.get('id'))} / {md(decision.get('riskClass'))}:** {md(decision.get('title'))} — {md(chosen_label(decision, resolution.get('optionId')))}; {md(resolution.get('rationale') or 'not resolved')}")

    lines.extend(["", "## Applicable-rule evidence", "", "| Rule | Classification | State | Exact rule | Applies because | Source |", "|---|---|---|---|---|---|"])
    for rule in rules:
        lines.append(f"| {md(rule.get('id'))} | {md(rule.get('classification'))} | {md(rule.get('status'))} | {md(rule.get('exactRule'))} | {md(rule.get('evidence'))} | {md(rule.get('registry'))}/{md(rule.get('article'))} |")
    if not rules:
        lines.append("| — | — | — | No applicable rules recorded | — | — |")
    lines.extend(["", "## Detailed source artifacts", "", f"- [Agreement]({detail_prefix}03-agreement.spec.md)", f"- [Target solution]({detail_prefix}03-target-solution.spec.md)", f"- [Test scenarios]({detail_prefix}03-test-scenarios.spec.md)", f"- [Canonical decision state]({detail_prefix}03-decision-manifest.state.json)", "", "---", "This view is generated; do not edit it.", ""])
    return "\n".join(lines)


def render_html(
    manifest: dict[str, Any],
    phase: str,
    review: dict[str, Any] | None = None,
    pr_url: str | None = None,
    changed_files: list[str] | None = None,
    checks: list[str] | None = None,
) -> str:
    decisions = sorted(manifest.get("decisions", []), key=decision_key)
    human = [item for item in decisions if item.get("riskClass") == "HUMAN_REQUIRED"]
    agent = [item for item in decisions if item.get("riskClass") != "HUMAN_REQUIRED"]
    rules = sorted(manifest.get("applicableRules", []), key=lambda item: natural_id(item.get("id")))
    changes = sorted(manifest.get("semanticChanges", []), key=lambda item: natural_id(item.get("id")))
    criteria = sorted(manifest.get("acceptanceCriteria", []), key=lambda item: natural_id(item.get("id")))
    scenarios = sorted(manifest.get("testScenarios", []), key=lambda item: natural_id(item.get("id")))
    batches = sorted(manifest.get("feedbackBatches", []), key=lambda item: natural_id(item.get("id")))
    detail_prefix = "" if phase == "alignment" else "../2-specification/"
    esc = lambda value: html.escape(str(value), quote=True)

    cards: list[str] = []
    for decision in human:
        resolution = decision.get("resolution") or {}
        options = "".join(
            f"<tr><td>{esc(option.get('id'))} — {esc(option.get('label'))}</td><td>{esc(option.get('consequence'))}</td></tr>"
            for option in decision.get("options", [])
        )
        sources = "".join(
            f"<li><code>{esc(source.get('kind'))}</code> / <code>{esc(source.get('authority'))}</code> — {esc(source.get('claim'))} <span class=muted>({esc(source.get('reference'))})</span></li>"
            for source in decision.get("sources", [])
        )
        cards.append(
            f"<article class='card critical'><div class=eyebrow>{esc(decision.get('id'))} · {esc(decision.get('status'))}</div>"
            f"<h3>{esc(decision.get('title'))}</h3><p class=question>{esc(decision.get('question'))}</p>"
            f"<p><b>Risk:</b> {esc(', '.join(decision.get('riskDimensions', [])) or 'not classified')}</p>"
            f"<p><b>Recommendation:</b> {esc(chosen_label(decision, decision.get('recommendation', {}).get('optionId')))} — {esc(decision.get('recommendation', {}).get('rationale'))}</p>"
            f"<p><b>Strongest counterargument:</b> {esc(decision.get('recommendation', {}).get('counterargument'))}</p>"
            f"<p><b>Recorded choice:</b> {esc(chosen_label(decision, resolution.get('optionId')))}{(' — ' + esc(resolution.get('rationale'))) if resolution else ''}</p>"
            f"<table><thead><tr><th>Option</th><th>Consequence</th></tr></thead><tbody>{options}</tbody></table>"
            f"<h4>Decision evidence</h4><ul>{sources}</ul></article>"
        )

    conflict_rows = []
    for decision in decisions:
        for conflict in decision.get("conflicts", []):
            conflict_rows.append(f"<li><b>{esc(decision.get('id'))} / {esc(conflict.get('status'))}:</b> {esc(conflict.get('issue'))} — {esc(conflict.get('consequence'))}; resolution: {esc(conflict.get('resolution') or 'open')}</li>")
    for rule in rules:
        if rule.get("status") in {"DEVIATION_APPROVED", "UNRESOLVED"} or rule.get("classification") in {"MISSING", "CONFLICTING"}:
            conflict_rows.append(f"<li><b>{esc(rule.get('id'))} / {esc(rule.get('classification'))} / {esc(rule.get('status'))}:</b> {esc(rule.get('exactRule'))} — {esc(rule.get('rationale'))}</li>")

    review_section = ""
    if phase == "review" and review:
        claim_items = "".join(
            f"<li><b>{esc(claim.get('id'))} / {esc((claim.get('adjudication') or {}).get('disposition') or 'not adjudicated')}:</b> {esc(claim.get('problem'))} — {esc((claim.get('adjudication') or {}).get('rationale') or '')}; candidate: {esc((claim.get('candidate') or {}).get('comparison') or 'none')}</li>"
            for claim in sorted(review.get("claims", []), key=lambda item: natural_id(item.get("id")))
        ) or "<li>No defect claims.</li>"
        file_items = "".join(f"<li><code>{esc(path)}</code></li>" for path in sorted(changed_files or [])) or "<li>Not supplied.</li>"
        check_items = "".join(f"<li>{esc(item)}</li>" for item in sorted(checks or [])) or "<li>Not supplied.</li>"
        reviewed_ac_rows = "".join(
            f"<tr><td>{esc(item.get('id'))}</td><td>{esc(item.get('text'))}</td><td>{esc(item.get('status'))}</td><td>{esc('; '.join(item.get('evidence', [])))}</td></tr>"
            for item in sorted(review.get("acceptanceCriteria", []), key=lambda item: natural_id(item.get("id")))
        ) or "<tr><td>—</td><td>No review assessment supplied</td><td>NOT_VERIFIABLE</td><td>—</td></tr>"
        safe_pr = safe_href(pr_url)
        pr = f"<p><a href='{esc(safe_pr)}'>Open pull request</a></p>" if safe_pr else ""
        review_section = (
            "<section><h2>Implementation review</h2>" + pr
            + f"<div class=stats><div><b>{esc(review.get('verdict'))}</b><span>verdict</span></div><div><b>{esc(review.get('baseline', {}).get('implementationCommit'))}</b><span>baseline</span></div><div><b>{esc(review.get('finalCommit') or 'preserved')}</b><span>final commit</span></div></div>"
            + f"<h3>Acceptance criteria against the implementation</h3><table><thead><tr><th>AC</th><th>Verbatim criterion</th><th>Status</th><th>Evidence</th></tr></thead><tbody>{reviewed_ac_rows}</tbody></table>"
            + f"<h3>Claims and dispositions</h3><ul>{claim_items}</ul><details><summary>Changed files</summary><ul>{file_items}</ul></details><details><summary>Checks</summary><ul>{check_items}</ul></details></section>"
        )

    ac_rows = "".join(
        f"<tr><td>{esc(item.get('id'))}</td><td>{esc(item.get('text'))}</td><td>{esc(', '.join(item.get('decisionIds', [])) or 'none')}</td><td>{esc(item.get('status'))}</td></tr>"
        for item in criteria
    ) or "<tr><td>—</td><td>No acceptance criteria recorded</td><td>—</td><td>UNRESOLVED</td></tr>"
    batch_rows = "".join(
        f"<tr><td>{esc(item.get('id'))}</td><td>{esc(item.get('source'))}</td><td>{item.get('processedItems')} / {item.get('expectedItems')}</td><td>{esc(item.get('status'))}</td><td>{esc('; '.join(item.get('unresolvedItems', [])) or 'none')}</td></tr>"
        for item in batches
    ) or "<tr><td>—</td><td>No batch feedback used</td><td>0 / 0</td><td>COMPLETE</td><td>none</td></tr>"
    scenario_rows = "".join(
        f"<tr><td>{esc(item.get('id'))} — {esc(item.get('title'))}</td><td>{esc(item.get('behavior'))}</td><td>{esc(', '.join(item.get('decisionIds', [])) or 'none')}</td><td>{esc(item.get('status'))}</td></tr>"
        for item in scenarios
    ) or "<tr><td>—</td><td>No test scenarios recorded</td><td>—</td><td>PROPOSED</td></tr>"
    agent_items = "".join(
        f"<li><b>{esc(item.get('id'))} / {esc(item.get('riskClass'))}:</b> {esc(item.get('title'))} — {esc(chosen_label(item, (item.get('resolution') or {}).get('optionId')))}</li>"
        for item in agent
    ) or "<li>None recorded.</li>"
    rule_rows = "".join(
        f"<tr><td>{esc(item.get('id'))}</td><td>{esc(item.get('classification'))}</td><td>{esc(item.get('status'))}</td><td>{esc(item.get('exactRule'))}</td><td>{esc(item.get('evidence'))}</td><td>{esc(item.get('registry'))}/{esc(item.get('article'))}</td></tr>"
        for item in rules
    ) or "<tr><td>—</td><td>—</td><td>—</td><td>No applicable rules recorded</td><td>—</td><td>—</td></tr>"
    change_items = "".join(
        f"<li><b>{esc(item.get('id'))} / {esc(item.get('discoveredAt'))} / {esc(item.get('status'))}:</b> {esc(item.get('summary'))}</li>"
        for item in changes
    ) or "<li>None recorded.</li>"

    title = f"Human {'PR review' if phase == 'review' else 'design decision'} gate — {esc(manifest.get('ticket'))}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
:root{{--ink:#18212f;--muted:#667085;--line:#d0d5dd;--paper:#f8fafc;--card:#fff;--critical:#b42318;--accent:#175cd3}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 system-ui,-apple-system,sans-serif}}main{{max-width:1100px;margin:auto;padding:32px 20px 64px}}h1{{font-size:30px;margin:0 0 12px}}h2{{margin-top:36px;border-bottom:1px solid var(--line);padding-bottom:8px}}h3{{margin:.25rem 0 .5rem}}h4{{margin-bottom:.25rem}}.action{{background:#fff4ed;border-left:5px solid #f79009;padding:16px 18px;font-size:17px}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0}}.stats div{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}.stats b{{display:block;overflow-wrap:anywhere}}.stats span,.muted{{color:var(--muted);font-size:13px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:14px 0}}.card.critical{{border-left:5px solid var(--critical)}}.eyebrow{{font-weight:700;color:var(--critical);font-size:12px;letter-spacing:.05em}}.question{{font-size:17px}}table{{width:100%;border-collapse:collapse;margin:12px 0;background:var(--card)}}th,td{{border:1px solid var(--line);padding:9px;text-align:left;vertical-align:top}}th{{background:#eef2f6}}code{{overflow-wrap:anywhere}}details{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:10px 0}}summary{{cursor:pointer;font-weight:700}}a{{color:var(--accent)}}
</style></head><body><main><h1>{title}</h1><div class=action><b>Action required:</b> {esc(gate_action(manifest, phase, review))}</div>
<div class=stats><div><b>{esc(manifest.get('approval', {}).get('status'))}</b><span>approval</span></div><div><b>{sum(item.get('status') != 'RESOLVED' for item in human)} / {len(human)}</b><span>human decisions open / total</span></div><div><b>{len(rules)}</b><span>applicable rules</span></div><div><b>{sum(item.get('status') != 'HUMAN_CONFIRMED' for item in scenarios)} / {len(scenarios)}</b><span>scenarios unconfirmed / total</span></div><div><b>{sum(item.get('status') == 'OPEN' for item in batches)} / {len(batches)}</b><span>feedback batches open / total</span></div></div>
{review_section}<section><h2>Decisions requiring human accountability</h2>{''.join(cards) or '<p>No human-required decisions were classified.</p>'}</section>
<section><h2>Source conflicts and rule deviations</h2><ul>{''.join(conflict_rows) or '<li>None recorded.</li>'}</ul></section>
<section><h2>Semantic changes since alignment</h2><ul>{change_items}</ul></section>
<section><h2>Acceptance-criteria coverage</h2><table><thead><tr><th>AC</th><th>Verbatim criterion</th><th>Decision mapping</th><th>Status</th></tr></thead><tbody>{ac_rows}</tbody></table></section>
<section><h2>Test-scenario challenge</h2><p class=question><b>Which of these are wrong, and what is missing?</b></p><table><thead><tr><th>Scenario</th><th>Behavior</th><th>Decision mapping</th><th>Status</th></tr></thead><tbody>{scenario_rows}</tbody></table></section>
<section><h2>Feedback ingestion</h2><table><thead><tr><th>Batch</th><th>Source</th><th>Processed</th><th>State</th><th>Unresolved</th></tr></thead><tbody>{batch_rows}</tbody></table></section>
<details><summary>Verified lower-risk decisions ({len(agent)})</summary><ul>{agent_items}</ul></details>
<details><summary>Applicable-rule evidence ({len(rules)})</summary><table><thead><tr><th>Rule</th><th>Class</th><th>State</th><th>Exact rule</th><th>Applies because</th><th>Source</th></tr></thead><tbody>{rule_rows}</tbody></table></details>
<section><h2>Detailed source artifacts</h2><ul><li><a href="{detail_prefix}03-agreement.spec.md">Agreement</a></li><li><a href="{detail_prefix}03-target-solution.spec.md">Target solution</a></li><li><a href="{detail_prefix}03-test-scenarios.spec.md">Test scenarios</a></li><li><a href="{detail_prefix}03-decision-manifest.state.json">Canonical decision state</a></li></ul></section>
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
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--check", action="append", default=[])
    args = parser.parse_args()
    manifest = load_json(args.manifest)
    review = load_json(args.review_state)
    if args.phase == "review" and review is None:
        parser.error("--review-state is required for review phase")
    markdown = render_markdown(manifest or {}, args.phase, review, args.pr_url, args.changed_file, args.check)
    page = render_html(manifest or {}, args.phase, review, args.pr_url, args.changed_file, args.check)
    args.markdown.write_text(markdown, encoding="utf-8")
    args.html.write_text(page, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

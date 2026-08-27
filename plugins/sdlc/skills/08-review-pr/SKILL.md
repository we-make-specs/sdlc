---
name: 08-review-pr
description: Pipeline step 08 (GATE) — render one deterministic PR decision page from the canonical decision and review states, then wait for explicit human approval. No merging and no review-detail flood in chat.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.0'
  tags: sdlc, step, gate, approval, pull-request, human-view
---

# Step 08 · Gate: Review PR  (GATE)

- **Type:** GATE — human approval, no model judgment
- **Skippable:** no

---

## What this skill does

Lets the human judge one implemented package without hunting through the plan, review exchange, PR,
and specifications. A deterministic Markdown/HTML projection puts the actual PR state, verbatim AC
assessments, review claim dispositions, semantic deltas, high-risk decisions, conflicts, checks and
changed files in one place. Detailed canonical artifacts remain linked for drill-down.

## Required inputs

| Input | Description | Required |
|---|---|---|
| Pull request | URL, state, mergeability, checks and changed files | yes |
| Review state | closed `07-review-<package-id>.state.json` | yes |
| Decision manifest | approved authority and semantic-change record | yes |
| Human | approves or requests focused changes | yes |

## Required context

- The repository's `## Context Registries` declaration and any merge-checklist or release-rule
  article it indexes. A newly discovered semantic conflict follows the focused-reopen protocol; it is
  not explained away in the briefing.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `03-decision-manifest.state.json` | [`artifact-definitions/03-decision-manifest.state.schema.json`](../../artifact-definitions/03-decision-manifest.state.schema.json) |
| reads | `07-review-<package-id>.state.json` | [`artifact-definitions/07-review.state.schema.json`](../../artifact-definitions/07-review.state.schema.json) |
| reads | pull-request metadata | live source of URL, checks and changed files |
| writes | `08-human-review-gate.view.md` and `.view.html` | deterministic projections, never canonical truth |

## Workflow

1. **Fail-closed pre-check.** Require a PR and a closed review state. Run
   `validate_review_state.py --phase closed` and `validate_decision_manifest.py --phase downstream`.
   An escalated review returns to focused gate 04 and must have no PR. A missing review because step 07
   was explicitly skipped is stated and requires the human to affirm that exception before this gate
   can continue.
2. **Fetch current PR facts**: URL, state, mergeability, changed files and check results. Do not trust a
   stale PR body for these.
3. **Render both views**, supplying every changed file and check to the renderer:

   ```bash
   python3 <plugin>/scripts/render_decision_gate.py \
     2-specification/03-decision-manifest.state.json --phase review \
     --review-state 3-planning/07-review-<package-id>.state.json \
     --pr-url <url> --changed-file <path> --check <result> \
     --markdown 3-planning/08-human-review-gate.view.md \
     --html 3-planning/08-human-review-gate.view.html
   ```

   Repeat `--changed-file` and `--check` for every item. The renderer is deterministic and escapes
   content; no agent-authored second summary is allowed to drift from canonical state.
4. **Present a short orientation only:**

   ```text
   Current phase: 08 / review PR
   What I need from you: approve this package or name a focused correction
   Why it matters: approval advances it to the explicit merge step
   PR: <state> · agent verdict: <verdict> · checks: <passing/failing counts> · ACs: <status counts>
   Open first: 08-human-review-gate.view.html (Markdown fallback beside it)
   ```

   If checks fail, an AC is `NOT_MET`/`PARTIAL`, a blocker remains, or the candidate was not proven
   better, state that before asking. Do not bury it below process detail.
5. **Ask decision-friendly.** With a clean state: "A: approve and continue to merge. B: name the
   concrete change." With a non-approve verdict or failed check, present B first with the evidence and
   recommend pausing. A missing external input is fixed by supplying that input, not by more coding.
6. **Classify requested changes before implementation.** A local defect returns to the isolated
   correction/review loop. A request that changes business behavior, security, a public contract,
   architecture, data, operations, an approved decision, or a binding rule becomes a semantic change
   and focused gate-04 decision. Never forward prose directly as an unconditional mutation command.
7. **Wait for explicit approval.** Vague praise is not approval. Do not merge here.

## Output contract

Deterministic `08-human-review-gate.view.md` and `.view.html`, plus either explicit human approval to
advance to step 09 or a focused correction routed to review/implementation or gate 04 according to its
semantic risk. No merge.

## Constraints and guardrails

- Do not merge and never self-approve.
- Do not proceed on invalid review/decision state or red checks.
- Do not restate a long artifact inventory in chat; point to the one generated human view.
- Do not hide NOT_MET/PARTIAL ACs, rejected/escalated claims, or preserved-baseline outcomes.
- Do not turn a human or reviewer comment into code before classifying its semantic blast radius.

## Success criteria

- [ ] Human page contains current PR facts, every changed file and every check
- [ ] Every package AC appears verbatim with review status and evidence
- [ ] Every review claim shows its independent disposition and candidate comparison
- [ ] High-risk decisions, conflicts and semantic changes remain prominent
- [ ] The human got one short orientation and one primary page
- [ ] An explicit approval or focused correction was recorded
- [ ] Nothing was merged

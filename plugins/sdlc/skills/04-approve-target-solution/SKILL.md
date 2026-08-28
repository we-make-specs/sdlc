---
name: 04-approve-target-solution
description: Pipeline step 04 (GATE) — guide the human through the complete target solution, prioritized acceptance criteria, open choices, and scenarios; then wait for explicit hash-locked approval before planning.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.1'
  tags: sdlc, step, gate, approval, human, decision-manifest
---

# Step 04 · Gate: Approve Target Solution  (GATE)

- **Type:** GATE — human approval, no model judgment
- **Skippable:** no

---

## What this skill does

Gives the human one short reading route instead of asking them to discover crucial choices across
many artifacts. The complete target solution remains required reading. The approval pack then shows
every acceptance criterion in simple English and priority order, followed by only open or changed
choices, source conflicts, test scenarios, and incomplete feedback. Machine detail stays available
but is not part of the main reading path.

The gate does not ask for one vague approval while important choices are unresolved. It closes each
focused decision first, regenerates the view, and only then asks whether the resulting design may
advance to planning.

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | located via the manifest | yes |
| Human | named decision owner and approver | yes |

## Required context

- The repository's `## Context Registries` declaration and any approval-checklist or
  definition-of-done article it points to. Applicable rules must already be present with exact text
  and classification in the decision manifest; newly discovered ones follow the focused-reopen rule.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `02-questions.inventory.md` | [`artifact-definitions/02-questions.inventory.md`](../../artifact-definitions/02-questions.inventory.md) |
| reads | `03-agreement.spec.md` | [`artifact-definitions/03-agreement.spec.md`](../../artifact-definitions/03-agreement.spec.md) |
| reads | `03-target-solution.spec.md` | [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| reads | `03-target-solution.view.html` — complete required human view | companion section of [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| reads | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| reads/updates | `03-decision-manifest.state.json` | [`artifact-definitions/03-decision-manifest.state.schema.json`](../../artifact-definitions/03-decision-manifest.state.schema.json) |
| regenerates | `03-human-decision-gate.view.md` and `.view.html` | companion section of [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| updates | target-solution and test-scenario approval headers | their contracts |

## Workflow

1. **Fail-closed pre-check.** If the decision manifest has `schemaVersion: 1`, first run the backup-first
   `migrate_state_070_to_071.py` script, refine its conservative acceptance-criterion summaries and
   priorities with the human, regenerate the views, and continue here; never edit the JSON shape by
   hand. Require all canonical artifacts, the complete target-solution HTML, and both approval-pack views. Run
   `validate_decision_manifest.py --phase alignment`; verify every Critical inventory entry has a real
   answer or an explicit deferral. Missing promised inputs, malformed state, count mismatches, or an
   `OPEN` feedback batch return to step 03. The validator also proves that the two HTML pages exactly
   match their current sources. Do not compensate with a prose summary.
2. **Present only the orientation in chat:**

   ```text
   Current phase: 04 / approve target solution
   What I need from you: read the full target solution, check its promises, resolve <n> highlighted choices, then approve or request changes
   Why it matters: planning and implementation will treat the approved decisions as invariants
   Open: <human decisions> · conflicts: <n> · unconfirmed scenarios: <n> · incomplete feedback batches: <n>
   Open first: 03-human-decision-gate.view.html; its first link opens the complete target solution
   ```

   Do not repeat all criteria or design text in chat. The deterministic approval pack is the reading
   route. The target-solution HTML it links first is a faithful rendering of the full design, not a
   summary. The pack then presents all ticket criteria with short meanings, reasons, and priorities.
   `CRITICAL`, `IMPORTANT`, and `SUPPORTING` control reading order only; every criterion remains a
   delivery promise unless the human explicitly changes it.
3. **Close focused decisions one at a time.** For each unresolved `HUMAN_REQUIRED` item, show its
   question, options, consequences, recommendation, strongest counterargument, source conflict and
   risk dimensions. Record the chosen option, rationale, human name/handle and date immediately. A
   human correction updates the canonical artifact and decision state; never patch only the view.
4. **Run the scenario challenge.** Ask exactly: **"Which of these are wrong, and what is missing?"**
   Record corrections or mark each presented scenario `HUMAN_CONFIRMED`. A generic "looks good" is
   not scenario confirmation unless the human explicitly says they checked and found none wrong or
   missing.
5. **Ingest gate feedback transactionally.** Treat a pasted list, annotation pass, or review file as
   one feedback batch: record the expected item count before processing, ingest each item once into
   canonical artifacts and decisions, reconcile the count, then mark `COMPLETE` or explicitly
   `DEFERRED`. Any semantic change may create a new focused decision. Never ask for approval with an
   incomplete batch.
6. **Regenerate, never hand-edit, all three views** after every design, decision, or feedback change:
   `render_target_solution.py` for the complete design and `render_decision_gate.py --phase alignment`
   for the approval pack. Re-run alignment validation. This ensures the human sees the exact state
   they are about to approve.
7. **Ask the final decision:** "A: approve these recorded decisions and continue to planning. B: name
   the decision or artifact that must change." Non-committal praise is not approval.
8. **On approval**, set the manifest approval to `APPROVED`, with the human's actual name/handle, date,
   and all resolved human decision IDs. Write matching approval headers into target solution and test
   scenarios. Then record exact hashes and validate:

   ```bash
   python3 <plugin>/scripts/record_approval_hashes.py \
     2-specification/03-decision-manifest.state.json
   python3 <plugin>/scripts/validate_decision_manifest.py \
     2-specification/03-decision-manifest.state.json --phase approved
   ```

   The script atomically regenerates the target-solution HTML and both approval-pack views. The hashes
   cover the agreement (including exact criteria), target solution, exact target-solution HTML, test
   scenarios, and decision content; validation also compares the approval page with a fresh rendering.
   Any later source or human-view edit fails downstream validation and requires a focused reapproval.
   Only successful validation passes the gate.

## Output contract

Either a named, dated, hash-locked and validation-clean approval across the decision manifest,
agreement, target solution, and test scenarios, with regenerated views; or focused requested changes
returned to step 03. No planning or code changes.

## Constraints and guardrails

- Never self-approve or infer approval from enthusiasm.
- Never ask the human to approve unresolved high-risk choices, source conflicts, missing rules,
  unconfirmed scenarios, or incomplete feedback batches.
- Never hide the target solution, an acceptance criterion, or a critical item inside a collapsed section.
- Never make the human read raw machine state unless they choose to drill down.
- Never edit the design just to make the validator pass; return to step 03.
- A new conflict reopens only affected decisions and dependent packages, not the entire design by
  reflex.

## Success criteria

- [ ] The human received one short reading route and a short orientation
- [ ] The complete target solution was required reading and was rendered faithfully in HTML
- [ ] Every acceptance criterion was visible in priority order with simple meaning and why it matters
- [ ] Every human-required decision was separately resolved with rationale and provenance
- [ ] Every source conflict and binding-rule deviation was visible and resolved
- [ ] Every scenario was challenged and human-confirmed
- [ ] Every feedback batch reconciled exactly or was explicitly deferred
- [ ] Views were regenerated from canonical state after the final change
- [ ] Explicit approval names the approver, date and covered decision IDs
- [ ] Approval hashes match the exact agreement, target solution, scenarios, and decision content
- [ ] Decision manifest passes `--phase approved`

---
name: 04-approve-target-solution
description: Pipeline step 04 (GATE) — present one deterministic, risk-ranked human decision gate; resolve focused choices and conflicts; and wait for explicit approval before planning. No model judgment and no approval by information flood.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.0'
  tags: sdlc, step, gate, approval, human, decision-manifest
---

# Step 04 · Gate: Approve Target Solution  (GATE)

- **Type:** GATE — human approval, no model judgment
- **Skippable:** no

---

## What this skill does

Gives the human one concise, deterministic pre-read instead of asking them to discover crucial
choices across many artifacts. The gate surfaces every human-required decision, source conflict,
binding-rule deviation, semantic change, acceptance criterion, test scenario and incomplete feedback
batch. Lower-risk agent-owned detail remains available but collapsed.

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
| reads | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| reads/updates | `03-decision-manifest.state.json` | [`artifact-definitions/03-decision-manifest.state.schema.json`](../../artifact-definitions/03-decision-manifest.state.schema.json) |
| regenerates | `03-human-decision-gate.view.md` and `.view.html` | companion section of [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| updates | target-solution and test-scenario approval headers | their contracts |

## Workflow

1. **Fail-closed pre-check.** Require all canonical artifacts and both generated views. Run
   `validate_decision_manifest.py --phase alignment`; verify every Critical inventory entry has a real
   answer or an explicit deferral. Missing promised inputs, malformed state, count mismatches, or an
   `OPEN` feedback batch return to step 03. Do not compensate with a prose summary.
2. **Present only the orientation in chat:**

   ```text
   Current phase: 04 / approve target solution
   What I need from you: resolve <n> highlighted choices, then approve or request changes
   Why it matters: planning and implementation will treat the approved decisions as invariants
   Open: <human decisions> · conflicts: <n> · unconfirmed scenarios: <n> · incomplete feedback batches: <n>
   Open first: 03-human-decision-gate.view.html (Markdown fallback beside it)
   ```

   Do not repeat all ACs and design text in chat. The deterministic page is the one human pre-read;
   it links the detailed agreement, target solution, scenarios and canonical state for drill-down.
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
6. **Regenerate, never hand-edit, both views** after every decision or feedback batch using
   `render_decision_gate.py --phase alignment`. Re-run alignment validation. This ensures the human
   sees the state they are actually about to approve.
7. **Ask the final decision:** "A: approve these recorded decisions and continue to planning. B: name
   the decision or artifact that must change." Non-committal praise is not approval.
8. **On approval**, set the manifest approval to `APPROVED`, with the human's actual name/handle, date,
   and all resolved human decision IDs. Write matching approval headers into target solution and test
   scenarios. Run `validate_decision_manifest.py --phase approved`; only success passes the gate.

## Output contract

Either a named, dated, validation-clean approval across the decision manifest, target solution, and
test scenarios, with regenerated Markdown and HTML views; or focused requested changes returned to
step 03. No planning or code changes.

## Constraints and guardrails

- Never self-approve or infer approval from enthusiasm.
- Never ask the human to approve unresolved high-risk choices, source conflicts, missing rules,
  unconfirmed scenarios, or incomplete feedback batches.
- Never hide a critical item inside a collapsed section.
- Never make the human read raw machine state unless they choose to drill down.
- Never edit the design just to make the validator pass; return to step 03.
- A new conflict reopens only affected decisions and dependent packages, not the entire design by
  reflex.

## Success criteria

- [ ] The human received one risk-ranked pre-read and a short orientation
- [ ] Every human-required decision was separately resolved with rationale and provenance
- [ ] Every source conflict and binding-rule deviation was visible and resolved
- [ ] Every scenario was challenged and human-confirmed
- [ ] Every feedback batch reconciled exactly or was explicitly deferred
- [ ] Views were regenerated from canonical state after the final change
- [ ] Explicit approval names the approver, date and covered decision IDs
- [ ] Decision manifest passes `--phase approved`

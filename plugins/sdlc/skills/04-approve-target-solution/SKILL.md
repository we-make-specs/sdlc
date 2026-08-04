---
name: 04-approve-target-solution
description: Pipeline step 04 (GATE) — present the alignment artifacts to the human with exactly what to open, and wait for explicit approval before planning begins. No model judgment; never self-approves.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.4.0'
  tags: sdlc, step, gate, approval, human
---

# Step 04 · Gate: Approve Target Solution  (GATE)

- **Type:** GATE — human approval, no model judgment
- **Skippable:** no

---

## What this skill does

Stops the pipeline and asks a human to approve the design before automated planning and implementation build on it. A gate is not a silent file check — it is a decision point with a named decider.

## When to use this skill

- The alignment step has produced its artifacts and the pipeline is about to plan

## When NOT to use this skill

- The artifacts are incomplete — report that instead of asking for approval on something unfinished

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | located via the manifest for the current branch | yes |
| Human | the decision is theirs | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure and pull any approval-checklist or definition-of-done article the registries hold into the briefing, noting a `Context loaded:` line in it. The decision itself stays human; nothing declared, or nothing relevant, is the normal case (`none applicable`).

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `02-questions.inventory.md` — no Critical entry may be open | [`artifact-definitions/02-questions.inventory.md`](../../artifact-definitions/02-questions.inventory.md) |
| reads | `03-alignment.spec.md` | [`artifact-definitions/03-alignment.spec.md`](../../artifact-definitions/03-alignment.spec.md) |
| reads | `03-target-solution.spec.md` | [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| reads | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| updates | `03-target-solution.spec.md` — status, approver, date | same contract |
| updates | `03-test-scenarios.spec.md` — status, approver, date | same contract |

---

## Workflow

1. **Pre-check** that all three artifacts and the overview page exist and that no Critical entry in `02-questions.inventory.md` is unanswered — where missing-input entries count as answered **only when the input is actually present and verifiable**, not merely promised. Anything missing or open → report that step 03 is incomplete and stop. Do not ask for approval on an incomplete set.
2. **Present the briefing** with precise, clickable pointers:
   - what to open: `03-target-overview.view.html` first — it is the pre-read this gate runs on — then the alignment record (acceptance criteria, key decisions) and the target solution (the design)
   - **inline**, so the human knows what to scrutinise: the acceptance criteria and open questions verbatim, plus the key-decision titles
   - what to verify: do intent and ACs match what was discussed? Are architecture and data flow accurate? Is anything important missing or misrepresented?
   - the test scenarios, shown as a **question, not a list**: "Which of these are wrong, and what is missing?" — a scenario pass needs an answer, not a nod
3. **Ask decision-friendly:** "A: approve and continue to planning. B: name the changes; I return to step 03 and revise."
4. **Wait for an explicit decision.** Non-committal praise is not approval — ask again with the two options.
5. **On approval**, write status, approver, and date into the headers of the target solution **and** the test scenarios. The approver is the human's actual name or handle — ask for it rather than writing a placeholder like "Human"; a gate without a named decider is not a gate.

---

## Output contract

No new files. Either the approval recorded in `03-target-solution.spec.md` and `03-test-scenarios.spec.md` and control returned to advance, or the requested changes handed back to step 03.

---

## Constraints and guardrails

- **Never self-approve**, and never infer approval from enthusiasm.
- **Do not approve over a critical open question** — neither in the question inventory nor in the alignment record.
- **Do not edit the design** to make it approvable — that is step 03's job.

---

## Success criteria

- [ ] The human was given exact things to open, not a summary to trust
- [ ] Acceptance criteria were shown inline, verbatim
- [ ] An explicit decision was recorded
- [ ] The scenario question got an explicit answer
- [ ] On approval: status, a real name or handle (no placeholders), and date written into the artifact

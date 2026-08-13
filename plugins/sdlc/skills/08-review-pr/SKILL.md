---
name: 08-review-pr
description: Pipeline step 08 (GATE) — present the pull request, the agent review verdict, changed files and the acceptance-criteria checklist to the human, and wait for their approval before the merge. No merging here.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.6.0'
  tags: sdlc, step, gate, approval, pull-request
---

# Step 08 · Gate: Review PR  (GATE)

- **Type:** GATE — human approval, no model judgment
- **Skippable:** no

---

## What this skill does

Gives the human everything needed to judge one work package's implemented pull request in one place, then waits for a decision: approve, or name concrete fixes. The acceptance-criteria checklist shows the package's Primary ACs with their verbatim text; a multi-package delivery passes this gate once per package.

## When to use this skill

- A pull request exists and carries the agent review

## When NOT to use this skill

- No pull request, or no agent review — report what is missing instead

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Pull request | status, mergeability, checks | yes |
| Agent review | verdict and summary from step 07 | yes |
| Human | the decision is theirs | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure and pull any merge-checklist or release-rule article the registries hold into the briefing, noting a `Context loaded:` line in it. The decision itself stays human; nothing declared, or nothing relevant, is the normal case (`none applicable`).

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `03-agreement.spec.md` — the acceptance criteria shown inline | [`artifact-definitions/03-agreement.spec.md`](../../artifact-definitions/03-agreement.spec.md) |
| reads | `05-implementation.plan.md` — progress log only, for WARN/blocker lines | [`artifact-definitions/05-implementation.plan.md`](../../artifact-definitions/05-implementation.plan.md) |
| writes | none | — |

---

## Workflow

1. **Pre-check.** No PR → step 06 produced none, report and stop. No agent review → step 07 was skipped, say so explicitly rather than proceeding quietly.
2. **Present the briefing** in one consolidated message:
   - **the diagnosis first, in plain language:** one short paragraph on what state the PR is actually in — what was built, what was not, and why. If the diff touches no code, say exactly that. If the plan's progress log or the PR body carries `WARN`/blocker lines, **quote them** — they are usually the real answer to "why".
   - the pull request as a clickable link, with state and any failing checks
   - the agent verdict in one line plus its summary as a quote, linked
   - the changed files
   - **inline:** the acceptance-criteria checklist, scoped to the package's Primary ACs — each item is the **AC text verbatim** from the agreement, its status, and a one-line reason with the reviewer's citation. Bare numbers ("AC3: not met") are worthless to a human who has not memorised the list; never present them. In the `team` profile the PR body deliberately carries none of this — this gate is where the process detail surfaces, from the workspace.
3. **Ask decision-friendly:** "A: approve, continue to the merge. B: name concrete fixes; I implement them and come back." When the agent verdict is not APPROVE, present B first with a recommendation and say why — and when the blocker is a missing input rather than a code defect, say that the fix is *delivering the input*, not more implementation.
4. **Wait.** Vague answers → ask again with the two options.

---

## Output contract

No files. Either approval and control returned to advance to the merge, or the requested fixes handed back to implementation with the human's notes.

---

## Constraints and guardrails

- **Do not merge.** That is step 09.
- **Never self-approve.**
- **A red check is a reason to pause**, not something to explain away.

---

## Success criteria

- [ ] The human saw the diagnosis, the PR, the verdict, the changed files, and the AC status without hunting for them
- [ ] Every AC shown with its verbatim text and a reason — no bare numbers
- [ ] WARN/blocker lines from the progress log or PR body quoted, not summarised away
- [ ] An explicit decision was recorded
- [ ] Nothing was merged

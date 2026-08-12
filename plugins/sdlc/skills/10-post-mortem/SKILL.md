---
name: 10-post-mortem
description: Pipeline step 10 (COLLAB) — close the delivery by reconciling the ledgers with reality, settling every assumed answer with the human, harvesting generalizable lessons, and writing the one-page post-mortem note. Runs whenever the last package is merged, no matter who merged it.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.1.0'
  tags: sdlc, step, post-mortem, close, lessons
---

# Step 10 · Post-Mortem  (COLLAB)

- **Type:** COLLAB — the accepted-risk decisions are the human's
- **Skippable:** no — the delivery is not done until this step says so

---

## What this skill does

Closes the delivery. Reconciles what the ledgers claim with what actually happened (including merges done by hand, outside the pipeline), settles every assumption, harvests what the delivery taught, and writes the one-page post-mortem note. `status: done` is set here and nowhere else.

## When to use this skill

- Every package the delivery requires is merged, by whomever
- The human wants to close out and capture the lessons

## When NOT to use this skill

- Unmerged non-conditional packages remain — report what is open instead of closing over it

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | the workspace with manifest, plan, inventory, decision log | yes |
| Repository state | to verify PRs and merge commits | yes |
| Human | accepted-risk calls and the lessons discussion are theirs | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure when proposing registry changes in the harvest; note a `Context loaded:` line in the post-mortem note (`none applicable` when nothing is declared).

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `00-manifest.state.md` — the ledgers to reconcile | [`artifact-definitions/00-manifest.state.md`](../../artifact-definitions/00-manifest.state.md) |
| reads | `02-questions.inventory.md` — the assumed answers | [`artifact-definitions/02-questions.inventory.md`](../../artifact-definitions/02-questions.inventory.md) |
| reads | `05-implementation.plan.md` — package state, gates, WARN lines | [`artifact-definitions/05-implementation.plan.md`](../../artifact-definitions/05-implementation.plan.md) |
| reads | `06-decisions.log.md` — the harvest source | [`artifact-definitions/06-decisions.log.md`](../../artifact-definitions/06-decisions.log.md) |
| updates | `00-manifest.state.md` — ledger reconciliation, `status: done` | same contract |
| writes | `10-post-mortem.md` | [`artifact-definitions/10-post-mortem.md`](../../artifact-definitions/10-post-mortem.md) |

---

## Workflow

1. **Reconcile reality.** Check every work-package ledger row against the actual repository state: PR merged or not, merge commit recorded. A merge that happened outside the pipeline is recorded now, marked as such — the pipeline never assumes it saw everything. Unmerged non-conditional packages → stop and report; this step closes deliveries, it does not chase them.
2. **Verify the release gates.** Every release readiness gate in the plan is met or explicitly waived by the human, with the waiver recorded.
3. **Settle every assumed answer.** For each `assumed` answer in the inventory: verified (record who and when, per its named owner) — or the human explicitly accepts it as a standing risk, recorded as a correction sub-entry. Nothing silently expires; approving over an open assumption was conscious once, leaving it open forever is not.
4. **Harvest the lessons.** Walk the decision log, the review outcomes, and the progress log's WARN and baseline entries. Three buckets: guidance that belongs in the context registry (propose it via the `sdlc-context` tooling as its own change, never bury it in the story), improvements to this pipeline (record them for the plugin's own backlog), and one-off facts (they stay in the artifacts). Discuss the shortlist with the human.
5. **Write the post-mortem note** per its contract: one page, what went well, what did not, what changed as a consequence.
6. **Close.** Set `status: done` in the manifest. This is the only place that sets it.

---

## Output contract

The ledgers reconciled with reality, every assumption settled, `10-post-mortem.md` written, `status: done` set. Returns the note's summary and the harvested proposals.

---

## Constraints and guardrails

- **Close only what is actually closed.** Unmerged non-conditional packages or unmet gates stop this step; a post-mortem over an open delivery is fiction.
- **Assumptions settle explicitly.** Verified with evidence, or accepted as risk by the human — never dropped.
- **Lessons leave the story.** Generalizable guidance goes to the registry as its own proposed change; story-specific detail stays here. Do not add story-specific rules to shared guidance.
- **One page.** The note is a record, not a report; the artifacts carry the detail.

---

## Success criteria

- [ ] Every ledger row matches verifiable repository state, outside-the-pipeline merges included and marked
- [ ] Every release gate met or explicitly waived, recorded
- [ ] Every assumed answer verified or accepted as risk, recorded with who and when
- [ ] The harvest was discussed and its proposals recorded, registry-bound ones as their own change
- [ ] `10-post-mortem.md` written, one page
- [ ] `status: done` set here and only here

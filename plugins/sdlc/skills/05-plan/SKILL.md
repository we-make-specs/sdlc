---
name: 05-plan
description: Pipeline step 05 (AUTO) — turn the approved alignment artifacts into an executable plan with parallelism groups, exact file paths, verifiable done-when conditions, and advisor checks. Optionally produces a technical analysis first.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.1'
  tags: sdlc, step, planning, tasks
---

# Step 05 · Plan  (AUTO)

- **Type:** AUTO — fresh session, rehydrates from disk, asks no questions; decides conservatively and documents uncertainty
- **Skippable:** no

---

## What this skill does

Turns the approved design into the single work list implementation executes: tasks annotated for parallelism, with exact paths and one verifiable done-when each, plus advisor checks for later verification.

## When to use this skill

- The target solution has been approved at gate 04

## When NOT to use this skill

- The target solution is not `APPROVED` — abort and point at gate 04

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | located via the manifest for the current branch | yes |
| Codebase | read access, to verify paths and patterns | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure: read each declared registry's `index.md` and navigate its index tables to the guidelines, architecture, and known-deviations articles this step touches. Record a `Context loaded:` line near the top of the plan (`none applicable` when nothing is declared), and make what they prescribe visible **in the tasks themselves** — a build step a guideline demands (code generation, a migration command) is a task detail, not background knowledge.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `00-manifest.state.md` | [`artifact-definitions/00-manifest.state.md`](../../artifact-definitions/00-manifest.state.md) |
| reads | `01-current-solution.research.md` | [`artifact-definitions/01-current-solution.research.md`](../../artifact-definitions/01-current-solution.research.md) |
| reads | `03-agreement.spec.md` — source of the verbatim copy | [`artifact-definitions/03-agreement.spec.md`](../../artifact-definitions/03-agreement.spec.md) |
| reads | `03-target-solution.spec.md` — must be `APPROVED` | [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| reads | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| reads | `02-work-breakdown.md` — the agreed cut | [`artifact-definitions/02-work-breakdown.md`](../../artifact-definitions/02-work-breakdown.md) |
| reads/updates | `03-decision-manifest.state.json` — approved authority and conflict record; updated only for newly discovered rules or semantic changes | [`artifact-definitions/03-decision-manifest.state.schema.json`](../../artifact-definitions/03-decision-manifest.state.schema.json) |
| reads *(optional)* | `02-questions.inventory.md` — the answered rationales, when the plan needs the why behind a decision | [`artifact-definitions/02-questions.inventory.md`](../../artifact-definitions/02-questions.inventory.md) |
| writes | `05-implementation.plan.md` | [`artifact-definitions/05-implementation.plan.md`](../../artifact-definitions/05-implementation.plan.md) |
| writes *(optional)* | `05-technical-analysis.research.md` | [`artifact-definitions/05-technical-analysis.research.md`](../../artifact-definitions/05-technical-analysis.research.md) |
| writes *(optional)* | `05-technical-questions.inventory.md` | [`artifact-definitions/05-technical-questions.inventory.md`](../../artifact-definitions/05-technical-questions.inventory.md) |

---

## Workflow

1. **Rehydrate.** Read every input fully; anything missing → abort naming it. A schema-version-1 decision manifest must first use the backup-first `migrate_state_070_to_071.py` path and return to gate 04. Target solution not approved, or `validate_decision_manifest.py --phase downstream` fails → abort, gate 04 first.
2. **Decide whether the optional technical-analysis pre-stage is warranted.** This is read-only implementation reconnaissance performed **after design approval and before task planning**: locate exact paths, compare verified reference implementations, and test technical feasibility. It is not the alignment analysis and cannot reinterpret the approved solution. New data model, cross-service change, unclear structure, or an unverified pattern choice warrants it; a small, well-understood change does not.
3. **Confirm code, pattern, and authority context.** Verify the paths and patterns the design references and compare every newly read registry rule with the approved applicable-rule table. **Verify states like migration numbers against the repository**, never carry them over from a document. Repository precedent is evidence, not permission to contradict an approved decision. When a strong local pattern and the planned design differ—for example generated mapping versus a manual mapper—record the actual reason and trade-off in the technical analysis or plan. If no reason can be established, make the choice an advisor check or focused decision; never let the implementer choose silently.
4. **Stop on a newly discovered conflict.** When planning discovers a previously unrecorded binding, missing, or conflicting rule—or a reference implementation that challenges an approved choice—append the rule and a `PLANNING` semantic change, create or reopen the smallest affected `HUMAN_REQUIRED` decision, set approval to `REOPENED`, mark dependent unmerged packages `needs-revalidation`, and stop for focused gate 04. Never rationalize the approved design after the fact and never silently switch patterns. An advisory rule that changes no approved semantics may be classified and recorded without reopening.
5. **Freeze the cut and draft the tasks.** Copy the agreed cut from the work breakdown into the plan's package sections the way ACs are copied: same packages, same dependencies, no reinterpretation. Each package's Primary ACs must exactly match its approved `packageAcceptanceCriteria` entry in the decision manifest; drift reopens alignment instead of being hidden in the review-blinded plan. A technical-analysis finding that changes the cut goes back through the breakdown's open decisions, not silently into the plan. Then draft each package's tasks. Application port names describe the use case's intent rather than the adapter mechanism; for an outbox, prefer language such as `queue` over `persist`, and do not use `publish` when delivery happens later. When a service method has long logical blocks, include short one-line intent or invariant comments in the relevant task—never comments that merely narrate syntax. Be conservative with parallelism — same group only when tasks obviously touch disjoint files; when in doubt, sequential.
6. **Draft advisor checks.** What a clean-context checker should confirm beyond the ACs. **Genuine ambiguity becomes a check** only when it cannot change approved semantics; semantic conflicts reopen their focused decision instead. Conditions outside the repository become **release readiness gates**, each with a named owner and what it blocks. Every planning-uncertainty entry from the technical analysis becomes a just-in-time check, phrased "immediately before T<n>, verify <fact>".
7. **Write the plan** per its contract only after the decision manifest still passes `--phase downstream`, then mark the artifact present in the manifest ledger.

---

## Output contract

`05-implementation.plan.md` written per contract with an empty progress log, optional pre-stage artifacts, manifest ledger updated. Returns task count, group structure, and any uncertainty encoded as a check. No commits, no code.

---

## Constraints and guardrails

- **Copy acceptance criteria and out-of-scope verbatim.** Not reordered, not improved, nothing dropped.
- **Do not pre-fill the progress log** — that belongs to step 06.
- **Do not implement anything.**
- **Do not guess.** Unresolved ambiguity becomes an advisor check.
- **Do not use an advisor check to postpone a design conflict.** Reopen its focused human decision.
- **Do not call an approved pattern a deviation after planning discovers contrary guidance.** Record the conflict and check it again at the focused decision gate.
- **Do not plan on promised inputs.** If a required external contract, schema, or access is not available and verifiable at planning time, abort and name the undelivered missing-input entry — a plan must encode facts, not hope.

---

## Success criteria

- [ ] ACs and out-of-scope are character-identical to the agreement
- [ ] Every task has exact paths and exactly one mechanically checkable done-when
- [ ] Every task traces to something the target solution specifies
- [ ] Parallelism is conservative
- [ ] Every out-of-repository condition is a release readiness gate with an owner, or none exist
- [ ] Every planning-uncertainty entry became a just-in-time advisor check
- [ ] Every newly discovered rule was reconciled with the approved applicable-rule table
- [ ] Every non-obvious pattern choice has a verified reason and trade-off, including mapper strategy when relevant
- [ ] Application port names express use-case intent; long service blocks have planned skimmability comments when useful
- [ ] No plan was written across a new semantic conflict; the focused decision gate reopened instead
- [ ] Decision manifest passes `--phase downstream`
- [ ] Progress log is empty

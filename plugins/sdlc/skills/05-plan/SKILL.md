---
name: 05-plan
description: Pipeline step 05 (AUTO) — turn the approved alignment artifacts into an executable plan with parallelism groups, exact file paths, verifiable done-when conditions, and advisor checks. Optionally produces a technical analysis first.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.4.0'
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
| reads *(optional)* | `02-questions.inventory.md` — the answered rationales, when the plan needs the why behind a decision | [`artifact-definitions/02-questions.inventory.md`](../../artifact-definitions/02-questions.inventory.md) |
| writes | `05-implementation.plan.md` | [`artifact-definitions/05-implementation.plan.md`](../../artifact-definitions/05-implementation.plan.md) |
| writes *(optional)* | `05-technical-analysis.research.md` | [`artifact-definitions/05-technical-analysis.research.md`](../../artifact-definitions/05-technical-analysis.research.md) |
| writes *(optional)* | `05-technical-questions.inventory.md` | [`artifact-definitions/05-technical-questions.inventory.md`](../../artifact-definitions/05-technical-questions.inventory.md) |

---

## Workflow

1. **Rehydrate.** Read every input fully; anything missing → abort naming it. Target solution not approved → abort, gate 04 first.
2. **Decide whether the optional pre-stage is warranted.** New data model, cross-service change, or unclear existing structure → write the technical analysis and questions first. A small, well-understood change → skip them.
3. **Confirm code context.** Verify the paths and patterns the design references, read-only. **Verify states like migration numbers against the repository**, never carry them over from a document.
4. **Draft the tasks.** Be conservative with parallelism — same group only when tasks obviously touch disjoint files; when in doubt, sequential.
5. **Draft advisor checks.** What a clean-context verifier should confirm beyond the ACs. **Genuine ambiguity becomes a check** ("verify decision on X at implementation time") rather than a silent guess. Conditions outside the repository (a deployment precondition, an external party's confirmation, post-release verification) become **release readiness gates**, each with a named owner and what it blocks. Every planning-uncertainty entry from the technical analysis becomes a just-in-time check, phrased "immediately before T<n>, verify <fact>".
6. **Write the plan** per its contract, then tick the manifest row.

---

## Output contract

`05-implementation.plan.md` written per contract with an empty progress log, optional pre-stage artifacts, manifest rows ticked. Returns task count, group structure, and any uncertainty encoded as a check. No commits, no code.

---

## Constraints and guardrails

- **Copy acceptance criteria and out-of-scope verbatim.** Not reordered, not improved, nothing dropped.
- **Do not pre-fill the progress log** — that belongs to step 06.
- **Do not implement anything.**
- **Do not guess.** Unresolved ambiguity becomes an advisor check.
- **Do not plan on promised inputs.** If a required external contract, schema, or access is not available and verifiable at planning time, abort and name the undelivered missing-input entry — a plan must encode facts, not hope.

---

## Success criteria

- [ ] ACs and out-of-scope are character-identical to the agreement
- [ ] Every task has exact paths and exactly one mechanically checkable done-when
- [ ] Every task traces to something the target solution specifies
- [ ] Parallelism is conservative
- [ ] Every out-of-repository condition is a release readiness gate with an owner, or none exist
- [ ] Every planning-uncertainty entry became a just-in-time advisor check
- [ ] Progress log is empty

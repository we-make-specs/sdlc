---
name: 07-review
description: Pipeline step 07 (AUTO) — independent blinded review of the pull request against the agreement and the design, deliberately without reading the plan. Produces inline comments and one verdict. Use after implementation, before the human review gate.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.4.0'
  tags: sdlc, step, review, quality-gate, adversarial
---

# Step 07 · Review (blinded)  (AUTO)

- **Type:** AUTO — fresh, isolated session. **The isolation is the point.**
- **Skippable:** yes, for small low-risk changes

---

## What this skill does

Reviews one work package's pull request against the agreement and the design — not against the implementer's account of what they did. Produces inline comments plus one summary carrying an explicit verdict. The acceptance-criteria lens covers the package's Primary ACs; a multi-package delivery reviews each package separately.

## When to use this skill

- A pull request exists and needs an independent check before a human reviews it

## When NOT to use this skill

- The change is trivial and low-risk and the team agreed to skip it

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Pull request | the authoritative change set | yes |
| Feature folder | for the agreement and design | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure: read each declared registry's `index.md` and navigate its index tables to the guideline and convention articles the diff must be judged against. Record a `Context loaded:` line in the review body (`none applicable` when nothing is declared); a violation of one is a citable finding (name the article), not a matter of taste.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `03-agreement.spec.md` — the acceptance criteria are the pass/fail gates | [`artifact-definitions/03-agreement.spec.md`](../../artifact-definitions/03-agreement.spec.md) |
| reads | `03-target-solution.spec.md` — the design reviewed against | [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| reads | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| **must not read** | `05-implementation.plan.md` | [`artifact-definitions/05-implementation.plan.md`](../../artifact-definitions/05-implementation.plan.md) |
| writes | PR review (no repository files) | — |

> ⛔ **The plan is off-limits.** It carries the implementer's framing, task list, and progress log. Reading it means inheriting their conclusions, and an independent review becomes a rubber stamp. Ignore references to it in other artifacts.

---

## Workflow

Work all four lenses; skip none.

1. **Acceptance-criteria coverage.** Every AC against the diff: met / not met / partial / not verifiable, each with a diff citation. An AC with no corresponding change is a red flag — unless it is a "do not change X" criterion.
2. **Design alignment.** Diff against the architecture and data flow of the target solution: missing components, unmentioned extras, logic in the wrong layer, violated boundaries.
3. **Code quality**, changed code only: correctness (off-by-one, null, inverted conditions) · edge cases (empty inputs, concurrency, failure paths, idempotency) · error handling (right layer, not silently swallowed) · naming against domain language · security (validation at boundaries, no secrets in logs) · tests (does the diff test what it adds?).
4. **Missing scenarios.** What the agreement and design imply but the diff does not handle. Often more valuable than style findings — hunt for them deliberately.

---

## Output contract

One PR review: zero or more inline comments, plus exactly one summary whose first line is the verdict (`APPROVE` / `REQUEST_CHANGES` / `COMMENT`), followed by the AC checklist with per-item status and citations, one or two notes on design alignment, and any open questions. No files changed in the working tree.

---

## Constraints and guardrails

- **Never read the forbidden artifact**, whatever other documents reference it.
- **Judge the new state.** Do not mourn removed code.
- **Ask no human questions.** Undecidable points become open questions in the summary with a matching verdict.
- **State uncertainty explicitly** rather than making a weak claim.
- **Change nothing** in the repository. The only side effect is the review.

---

## Success criteria

- [ ] Summary posted with an explicit verdict
- [ ] Every acceptance criterion assessed with a diff citation
- [ ] All four lenses applied
- [ ] The plan was not read
- [ ] No working-tree changes

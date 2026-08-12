---
name: 07-review
description: Pipeline step 07 (AUTO) — independent blinded review of the package diff before anything is published, deliberately without reading the plan. Findings resolve in a bounded exchange with the implementer; then the branch is pushed and the pull request opened clean. Use after implementation, before the human review gate.
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

Reviews one work package's diff — the local branch against its declared base, **before any pull request exists** — against the agreement and the design, not against the implementer's account of what they did. Findings are resolved in a bounded exchange with the implementer; when the exchange closes, the branch is pushed and the pull request opened, born clean. The acceptance-criteria lens covers the package's Primary ACs; a multi-package delivery reviews each package separately.

When this step is skipped (trivial, low-risk change), the implementer publishes directly: push the branch and open the PR with the body prepared in step 06.

## When to use this skill

- A pull request exists and needs an independent check before a human reviews it

## When NOT to use this skill

- The change is trivial and low-risk and the team agreed to skip it

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Package diff | the package branch against its declared base, local | yes |
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
| writes | the review outcome: verdict, findings, resolutions (recorded by the implementer side; posted as a PR review only with `review_placement: pr`) | — |

> ⛔ **The plan is off-limits.** It carries the implementer's framing, task list, and progress log. Reading it means inheriting their conclusions, and an independent review becomes a rubber stamp. Ignore references to it in other artifacts.

---

## Workflow

1. **Take the diff:** the package branch against its declared base, locally. No PR exists yet, and that is the point — findings get fixed before anything is published.

Then work all four lenses; skip none.

2. **Acceptance-criteria coverage.** Every AC against the diff: met / not met / partial / not verifiable, each with a diff citation. An AC with no corresponding change is a red flag — unless it is a "do not change X" criterion.
3. **Design alignment.** Diff against the target solution: its components, flows, and data structures — missing components, unmentioned extras, logic in the wrong layer, violated boundaries.
4. **Code quality**, changed code only: correctness (off-by-one, null, inverted conditions) · edge cases (empty inputs, concurrency, failure paths, idempotency) · error handling (right layer, not silently swallowed) · naming against domain language · security (validation at boundaries, no secrets in logs) · tests (does the diff test what it adds?).
5. **Missing scenarios.** What the agreement and design imply but the diff does not handle. Often more valuable than style findings — hunt for them deliberately.

After the lenses:

6. **Resolve the findings in a bounded exchange.** Each finding goes to the implementer, who fixes it or rejects it with a technical reason; verify the fixes, challenge weak rejections. At most `max_advisor_rounds` rounds (the plan's frontmatter carries the cap — the orchestrator passes the number in, since this step never reads the plan). A disagreement still open after the cap stays in the summary and lowers the verdict. The exchange is about findings and code, never the plan; the blinding holds throughout, and the verdict remains the reviewer's own.
7. **Publish.** When the exchange closes, the implementer side pushes the branch and opens the pull request with the body prepared in step 06, then records the verdict, the findings and their resolutions in the package's Status and ledger row. With `review_placement: pr` in the profile, the verdict and any remaining findings are additionally posted as a PR review; with `workspace`, the workspace record is the review's home and the team-facing PR stays clean.

---

## Output contract

A closed review exchange: zero or more findings with their recorded resolutions, plus exactly one summary whose first line is the verdict (`APPROVE` / `REQUEST_CHANGES` / `COMMENT`), followed by the AC checklist with per-item status and citations, one or two notes on design alignment, and any open questions. The branch pushed and the pull request open, clean. The reviewer itself changes no files; fixes happen on the implementer side of the exchange.

---

## Constraints and guardrails

- **Never read the forbidden artifact**, whatever other documents reference it.
- **Judge the new state.** Do not mourn removed code.
- **Ask no human questions.** Undecidable points become open questions in the summary with a matching verdict.
- **State uncertainty explicitly** rather than making a weak claim.
- **The reviewer changes nothing** in the repository. Fixes belong to the implementer side of the exchange; the reviewer verifies them.
- **The verdict is not negotiable by round count.** The cap bounds the exchange, not the reviewer's judgment.

---

## Success criteria

- [ ] Summary produced with an explicit verdict
- [ ] Every acceptance criterion assessed with a diff citation
- [ ] All four lenses applied
- [ ] Every finding resolved (fixed or rejected with a reason) or carried into the summary; the exchange stayed within the round cap
- [ ] The branch was pushed and the PR opened only after the exchange closed
- [ ] The plan was not read
- [ ] No working-tree changes by the reviewer

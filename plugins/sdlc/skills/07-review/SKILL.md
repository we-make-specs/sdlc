---
name: 07-review
description: Pipeline step 07 (AUTO) — evidence-first review of a package diff through independent critic, adjudicator, candidate implementer, and verifier roles. Reviewer findings are claims, not mutation commands; the approved implementation remains the baseline unless a candidate is proven better. Use after implementation, before the human review gate.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.0'
  tags: sdlc, step, review, quality-gate, adversarial, adjudication
---

# Step 07 · Review (evidence-gated)  (AUTO)

- **Type:** AUTO — four fresh, isolated roles coordinated by `/sdlc:run`
- **Skippable:** yes, only for a deliberately agreed low-risk change

---

## What this skill does

Reviews one package before publication without giving a single reviewer authority to rewrite working
code. The implementation commit is an immutable baseline. A critic records falsifiable defect claims;
an independent adjudicator weighs each claim against the approved intent, binding rules, repository
patterns and alternatives; a skeptical implementer may build an isolated candidate for accepted or
reframed claims; and an independent verifier compares that candidate with the baseline. Only a
candidate proved better may replace the baseline.

The reviewer remains valuable as a defect sensor. It is deliberately **not** a source of truth and
does not issue implementation commands.

## When to use this skill

- A completed local package needs an independent check before it is published
- A prior review suggestion could alter architecture, authorization, serialization, data, operations,
  or another approved semantic decision

## When NOT to use this skill

- The change is trivial, low risk, and the human explicitly accepted skipping review
- A pull request already exists and the request is only for the human PR gate

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Package diff | package branch against its declared base, local | yes |
| Feature folder | approved specifications and decision manifest | yes |
| Package ID | selects the package and review-state filename | yes |
| Round cap | `max_advisor_rounds`, supplied by the orchestrator | yes |

## Required context

- The repository's `## Context Registries` declaration and every indexed article relevant to the
  change. Record the article and exact rule in the decision manifest's applicable-rule table; a
  `Context loaded:` trace alone is not evidence.
- The package base commit and implementation commit. Record both before the critic runs; never move
  the baseline during review.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `03-agreement.spec.md` | [`artifact-definitions/03-agreement.spec.md`](../../artifact-definitions/03-agreement.spec.md) |
| reads | `03-target-solution.spec.md` | [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| reads | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| reads | `03-decision-manifest.state.json` | [`artifact-definitions/03-decision-manifest.state.schema.json`](../../artifact-definitions/03-decision-manifest.state.schema.json) |
| **must not read** | `05-implementation.plan.md` | [`artifact-definitions/05-implementation.plan.md`](../../artifact-definitions/05-implementation.plan.md) |
| writes | `3-planning/07-review-<package-id>.state.json` | [`artifact-definitions/07-review.state.schema.json`](../../artifact-definitions/07-review.state.schema.json) |

> **The plan is off-limits to critic, adjudicator and verifier.** It carries the implementer's framing.
> The candidate implementer receives only accepted/reframed claims and the approved specifications,
> never reviewer prose presented as an instruction.

---

## Role protocol

The orchestrator runs each role in a fresh context. No role may silently absorb another role.

### 1. Critic — produce claims, not fixes

Review the baseline through all four lenses:

1. acceptance-criteria coverage, item by item;
2. alignment with the approved design and resolved decisions;
3. correctness, edge cases, failure handling, security and tests in changed code;
4. missing scenarios implied by the agreement and design.

For every suspected defect, add one claim to the review state. It must state the observable problem,
diff evidence, the objective being protected and its source kind, supporting and conflicting sources,
severity, confidence, blast radius, a concrete failure scenario, and a verification method. A suggested
fix is optional and has no authority. Do not modify code.

Validate before handoff:

```bash
python3 <plugin>/scripts/validate_review_state.py \
  3-planning/07-review-<package-id>.state.json --phase claims
```

### 2. Adjudicator — resolve the claim's authority and trade-offs

Independently verify the critic's citations and applicable-rule table. For every claim:

- compare preserving the baseline, the reviewer's suggestion, and at least one real alternative;
- identify disagreement among ticket text, acceptance criteria, approved design, registry rules,
  reference implementations and runtime evidence;
- choose `ACCEPT`, `REJECT`, `REFRAME`, or `ESCALATE`, with a technical rationale;
- never treat an acceptance criterion, registry rule, or reviewer statement as automatically dominant;
  interpret its authority, applicability and consequences;
- use `ESCALATE` when resolving the conflict would choose externally visible behavior or change an
  approved architecture/security/data/operational decision without clear higher-authority evidence.

An escalation creates or reopens exactly one human-required decision in
`03-decision-manifest.state.json`, records its ID in the claim, preserves the baseline, and stops the
package. It does not reopen the whole design by default—only the affected decision and dependent
packages.

Validate the adjudicated state before any candidate work:

```bash
python3 <plugin>/scripts/validate_review_state.py \
  3-planning/07-review-<package-id>.state.json --phase adjudication
```

### 3. Candidate implementer — challenge first, then isolate

Receive only accepted/reframed claims and their adjudications. For each one, first try to disprove it
using code, tests and authoritative evidence. Record a rejection challenge for re-adjudication when
the claim is wrong or the proposed correction would be worse.

If a correction remains justified, create it in a temporary branch or worktree from the exact
implementation commit. Keep the production package branch untouched. Apply the smallest coherent
correction; preserve all approved semantics not named by the adjudication. Run the relevant checks and
record the candidate commit. Do not publish it.

### 4. Verifier — baseline versus candidate

In a new context, compare the candidate with the immutable implementation baseline. For every accepted
or reframed claim, require evidence that:

- the alleged defect is removed;
- approved invariants and applicable binding rules still hold;
- regression tests and appropriate build/static checks pass;
- any security, public-contract, architecture, data, or operational blast radius has an explicit
  semantic invariant check, not merely a green unit test;
- the candidate is better overall, not just different or locally cleaner.

Set `BETTER` only when all of those are demonstrated. Otherwise set `NOT_PROVEN_BETTER`; discard the
candidate and preserve the baseline. The critic and candidate implementer may not verify their own
work.

Validate the final state:

```bash
python3 <plugin>/scripts/validate_review_state.py \
  3-planning/07-review-<package-id>.state.json --phase closed
```

---

## Closing and publication

At most `max_advisor_rounds` critic/adjudicator/challenge cycles may run. The cap bounds cost, not
judgment. An unresolved high-risk conflict becomes `ESCALATED`; an unproven candidate never wins by
timeout.

When the final state validates:

- integrate only a `BETTER` candidate onto the package branch;
- otherwise retain the exact implementation baseline;
- push and open the pull request with the body prepared in step 06;
- record the review-state path, verdict, final commit and any open low-risk claims in the package
  ledger; and
- post a PR review only when the delivery profile says `review_placement: pr`.

## Output contract

A schema-valid, closed `07-review-<package-id>.state.json` that preserves the evidence chain from claim
through adjudication and comparison. The package branch and pull request point to `finalCommit`; no
candidate is integrated unless the independent verifier marked it `BETTER`. An escalated review has no
`finalCommit`, changes no production code, and names one focused human decision.

## Constraints and guardrails

- A review finding is a claim, never an implementation command.
- The reviewer, adjudicator and verifier change no production files.
- No role may approve or verify its own proposed correction.
- Never replace the baseline because a reviewer is more confident or uses a stronger model.
- Never resolve a source conflict by mechanically following the acceptance criterion or registry.
- Never publish an invalid or incomplete review state.
- Never broaden a focused conflict into an automatic redesign.
- State uncertainty and missing evidence explicitly.

## Success criteria

- [ ] Baseline commits recorded before review and unchanged throughout
- [ ] Every finding is a falsifiable, evidence-linked claim
- [ ] All four review lenses applied
- [ ] Every claim independently adjudicated against three alternatives
- [ ] Conflicting authorities explicitly resolved or escalated
- [ ] Accepted/reframed claims implemented only in an isolated candidate
- [ ] Candidate independently compared with the baseline
- [ ] High-risk candidates carry semantic invariant checks
- [ ] Closed review state passes the fail-closed validator
- [ ] Only a proven-better candidate was integrated and published
- [ ] Plan remained unread by critic, adjudicator and verifier

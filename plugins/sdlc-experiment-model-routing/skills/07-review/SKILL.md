---
name: 07-review
description: Pipeline step 07 (AUTO) — independent, risk-scaled review with evidence checking, one combined trial fix by default, and one final full test run. Findings are not code-change commands; the approved implementation remains the baseline unless a trial fix is proven safer and better.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.1'
  tags: sdlc, step, review, quality-gate, evidence, risk-scaled
---

# Step 07 · Review  (AUTO)

- **Type:** AUTO — fresh roles, but only the roles required by the chosen path
- **Skippable:** yes, only for a deliberately agreed low-risk change

---

## What this skill does

Checks one package before publication without letting a reviewer rewrite good code by authority or
confidence alone. The implementation commit is the immutable original. A **reviewer** reports
evidence-backed findings. A separate **evidence checker** decides whether each finding is valid,
wrong, partly right, or needs a human. Only valid findings enter a **trial fix**. A separate **final
checker** compares the trial with the original. The trial replaces the original only when the
evidence proves it is a safe improvement.

The process scales with risk. A preference or wrong finding stops without code or tests. A small,
local correction uses a shared trial branch and targeted checks. A behavior, security, contract,
architecture, data, or operations change uses an isolated worktree and semantic checks. A conflict
over intent stops for one focused human decision.

## Required inputs

| Input | Description | Required |
|---|---|---|
| Package diff | package branch against its declared base, local | yes |
| Feature folder | approved specifications and decision manifest | yes |
| Package ID | selects the package and review-state filename | yes |
| Round cap | `max_advisor_rounds`, supplied by the orchestrator | yes |

## Required context

- Follow the repository's `## Context Registries` procedure and read only relevant articles. Record
  the article and exact rule; `Context loaded:` alone is not evidence.
- Record the package base commit and implementation commit before review. Never move this baseline.
- When resuming a schema-version-1 review state, run the backup-first
  `migrate_state_070_to_071.py` script. It retains the original state and resumes before trial
  building; old candidates are historical evidence, not automatic proof under this protocol.
- If step 06 ran the complete package test command on the exact implementation commit, copy its
  command, commit, completion time, result, and evidence into `baseline.implementationFullCheck`.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `03-agreement.spec.md` | [`artifact-definitions/03-agreement.spec.md`](../../artifact-definitions/03-agreement.spec.md) |
| reads | `03-target-solution.spec.md` | [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| reads | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| reads/updates | `03-decision-manifest.state.json` | approved package-to-AC map; only an `ASK_HUMAN` path may append a REVIEW semantic change, create/reopen its human decision, and set approval `REOPENED`; [`artifact-definitions/03-decision-manifest.state.schema.json`](../../artifact-definitions/03-decision-manifest.state.schema.json) |
| **must not read** | `05-implementation.plan.md` | [`artifact-definitions/05-implementation.plan.md`](../../artifact-definitions/05-implementation.plan.md) |
| writes | `3-planning/07-review-<package-id>.state.json` | [`artifact-definitions/07-review.state.schema.json`](../../artifact-definitions/07-review.state.schema.json) |

> The plan is hidden from the reviewer, evidence checker, and final checker because it contains the
> implementer's own framing. The trial-fix builder receives checked findings and approved
> specifications, not reviewer prose presented as an order.

## Four paths

| Path | When it applies | Code work | Checks |
|---|---|---|---|
| `NO_CHANGE` | wrong finding, preference, or no observable defect | none | no new test run |
| `LIGHT` | objective local defect; behavior and approved design stay unchanged | one shared trial branch for all compatible findings | targeted checks, then independent diff check |
| `FULL` | business behavior, security, public contract, architecture, data, operations, or a risky cross-cutting change | isolated worktree from the exact implementation commit | targeted checks, explicit semantic invariants, then final full check |
| `HUMAN` | sources or trade-offs require authority the agents do not have | none; preserve original | one focused decision at gate 04 |

High-impact areas always take `FULL` or `HUMAN`; confidence does not lower the path.

## Role protocol

The orchestrator starts each role in a fresh context. It skips roles the chosen path does not need.

### 1. Reviewer — report findings, not fixes

Check the original through these lenses:

1. every package acceptance criterion and approved scenario;
2. approved design and resolved decisions;
3. correctness, edge cases, failure handling, security, tests, and changed documentation;
4. repository patterns and domain language;
5. design traceability and skimmability:
   - a non-obvious choice against a strong repository pattern records why it is better here (for
     example, a manual mapper where generated mappers are the normal pattern);
   - application ports state the application's intent, not the storage or messaging mechanism behind
     an adapter; do not call an outbox enqueue operation `publish` if delivery is not synchronous;
   - long application-service methods have short, useful comments before meaningful logical blocks
     when the code cannot otherwise be skimmed; comments describe intent or invariant, never syntax.

The last lens does not turn taste into a defect. Missing comments or a different mapper are findings
only when there is concrete readability, consistency, or maintenance harm. Otherwise record no
finding or use low severity and let the evidence checker choose `NOT_A_PROBLEM`.

Initialize the review's acceptance-criteria list from the selected package's approved
`packageAcceptanceCriteria` entry in the decision manifest, preserving each ID and exact text. Never
derive package scope from the blinded implementation plan. For every suspected defect, record the observable problem, file/line evidence, protected objective,
supporting and conflicting sources, severity, confidence, impact areas, failure scenario, and how it
could be verified. A suggested fix is optional and has no authority. Do not modify code. Do not rerun
the complete suite; use existing step-06 evidence and only a narrow reproduction when needed.

Validate before handoff:

```bash
python3 <plugin>/scripts/validate_review_state.py \
  3-planning/07-review-<package-id>.state.json --phase findings \
  --decision-manifest 2-specification/03-decision-manifest.state.json
```

### 2. Evidence checker — decide the finding and path

Independently verify each citation, reproduce the failure when practical, and compare the real
trade-off of keeping the original with the real trade-off of correcting it. Do not mechanically obey
ticket wording, acceptance criteria, registry text, repository precedent, or reviewer opinion. Check
which source applies, what it means in context, and what each alternative would break.

Record one result in plain language:

- `VALID` — the defect is real as stated;
- `NOT_A_PROBLEM` — wrong, unproven, or only a preference;
- `PARTLY_RIGHT` — the defect is real but its framing or suggested correction is unsafe;
- `ASK_HUMAN` — the correct choice depends on business behavior, an approved design decision, or a
  source conflict agents have no authority to settle.

Then assign `NO_CHANGE`, `LIGHT`, `FULL`, or `HUMAN`. `ASK_HUMAN` appends a `REVIEW` semantic change,
creates or reopens exactly one `HUMAN_REQUIRED` decision in the decision manifest, sets approval to
`REOPENED`, preserves the original, and stops the package. The cross-state validator rejects a review
whose decision does not exist or is not open. It does not reopen the whole design unless the dependency
graph proves the whole design is affected.

Group all compatible valid or partly-right findings into **one trial fix for this package and review
round**. More than one trial fix is allowed only for competing alternatives that cannot safely coexist
or separate packages. Record why one combined trial is impossible. Never create one trial per review
comment.

Validate before code work:

```bash
python3 <plugin>/scripts/validate_review_state.py \
  3-planning/07-review-<package-id>.state.json --phase checked \
  --decision-manifest 2-specification/03-decision-manifest.state.json
```

### 3. Trial-fix builder — only when LIGHT or FULL exists

Receive checked findings and their trade-offs. First try once more to disprove the need using code,
tests, and binding evidence; send a concrete challenge back to the evidence checker if needed.

For `LIGHT`, create one temporary shared trial branch from the implementation commit and apply the
smallest coherent correction for all compatible findings. For `FULL`, create an isolated worktree
from that commit. Preserve every approved semantic not named by the evidence check. Run only targeted
tests and checks while building the trial. Record one top-level `trialFixes` entry and link findings
to it by ID; never copy the same trial object into each finding.

### 4. Final checker — compare original and trial

In a new context, independently prove for each trial that:

- the defect is gone;
- approved invariants and applicable rules still hold;
- targeted tests and appropriate build/static checks pass;
- every `FULL` path has an explicit semantic invariant check;
- the complete trial is better overall, not merely different or locally cleaner.

Set `SAFE_IMPROVEMENT` only when all points are demonstrated. Otherwise set `KEEP_ORIGINAL` and
discard the trial. Only one trial may be selected. After selection, run the complete package test
command **exactly once** on the final commit. When an unchanged original already has a passing step-06
full-check record for the exact immutable commit, command, result, completion time, and evidence,
reuse that record in `finalFullCheck`; the validator rejects an unnecessary repeat. A changed trial
never reuses original evidence.
CI may run the suite again after publication because it is an external gate, not another local review
round.

Validate the final state:

```bash
python3 <plugin>/scripts/validate_review_state.py \
  3-planning/07-review-<package-id>.state.json --phase closed \
  --decision-manifest 2-specification/03-decision-manifest.state.json
```

## Closing and publication

At most `max_advisor_rounds` reviewer/evidence-checker/challenge cycles may run. The cap controls cost;
it does not make uncertain evidence true. A human conflict stops as `ASK_HUMAN`. An unproven trial
never wins because time ran out.

When the final state validates:

- integrate only the selected `SAFE_IMPROVEMENT` trial;
- otherwise keep the exact implementation baseline;
- push and open the pull request with the body prepared in step 06;
- record the review path, final commit, final full-check evidence, and open low-risk notes in the
  package ledger; and
- post a PR review only when the profile says `review_placement: pr`.

## Constraints and guardrails

- A finding is evidence to check, never a code-change command.
- No role may approve or check its own proposed correction.
- Never replace the original because a reviewer has a stronger model or sounds confident.
- Never resolve a source conflict by robotically following acceptance criteria or registry text.
- Never spend a trial branch, worktree, or full suite on a `NO_CHANGE` path.
- Never create one trial fix per comment by default.
- Never publish invalid or incomplete state.

## Success criteria

- [ ] Original commits recorded once and unchanged throughout
- [ ] Review AC IDs and exact wording match the approved mapping for this package
- [ ] Every finding is falsifiable and linked to evidence
- [ ] Every finding has an independent plain-English result and risk path
- [ ] Wrong or preference findings caused no code work and no new test run
- [ ] Compatible valid findings share one trial fix
- [ ] Every extra trial fix states why separation was necessary
- [ ] `LIGHT` used a shared trial branch; `FULL` used an isolated worktree and semantic checks
- [ ] The final checker was independent from reviewer and trial builder
- [ ] The full package test ran once after selection, or exact step-06 evidence was safely reused
- [ ] Only one proven safe improvement was integrated
- [ ] Plan remained unread by reviewer, evidence checker, and final checker
- [ ] Closed state passes the fail-closed validator

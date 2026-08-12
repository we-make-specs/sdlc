---
artifact: 05-implementation.plan.md
produced_by: 05-plan
consumed_by: [06-implement, 08-review-pr]
forbidden_for: [07-review]
required: true
---

# Contract — `05-implementation.plan.md` (executable plan)

## Purpose

The single work list implementation executes. Concrete enough that a fresh session can work from it without having attended the discussion.

The plan is also where **progress is recorded** — implementation ticks its task checkboxes and appends to the progress log here. Plan and reality in one file, so deviations are visible at a glance instead of buried in a second document.

> ⛔ **Blinded from the review.** Step 07 must not read this file: it carries the implementer's framing and conclusions, and reading it turns an independent review into a rubber stamp.

## Required sections

| Section | Required | Content |
|---|---|---|
| frontmatter | yes | ticket, based_on, created, `max_advisor_rounds` |
| `## Acceptance Criteria` | yes | **verbatim** from `03-agreement.spec.md` |
| `## Out of Scope` | yes | **verbatim** from `03-agreement.spec.md` |
| `## Tasks` | yes | each with Group, Files, Done-when; optional Depends-on |
| `## Advisor Checks` | yes | verification beyond the ACs |
| `## Release Readiness Gates` | if applicable | delivery gates that are not pull requests: each names its condition, its owner, and what it blocks |
| `## Progress Log` | yes | empty placeholder at creation; step 06 appends |

### Task fields

| Field | Required | Meaning |
|---|---|---|
| **Group** | yes | `A`, `B`, … — same group may run in parallel, groups run in order |
| **Files** | yes | exact paths created or modified |
| **Depends on** | when needed | cross-group dependency |
| **Done when** | yes | exactly **one** verifiable condition |
| description | yes | 1–3 sentences, anchored to the target solution |

## Quality criteria

- [ ] ACs and out-of-scope are **character-identical** to `03-agreement.spec.md`. Not reordered, not "improved", nothing dropped.
- [ ] Every task has exact file paths and exactly one done-when that can be checked mechanically (file exists, test passes).
- [ ] Parallelism is conservative — tasks are only in the same group when they obviously touch disjoint files. When in doubt, sequential.
- [ ] Every task traces back to something `03-target-solution.spec.md` specifies. A task with no basis there is scope creep.
- [ ] Genuine ambiguity is encoded as an advisor check, not silently decided.
- [ ] A progress-log entry that claims verification names the exact command and its result. A failing check believed unrelated is attributed against the base branch before it is called pre-existing: the same failure there makes it a recorded baseline failure, never a reason to touch unrelated source. Superseded entries stay in the log under a preamble note; nothing is deleted.
- [ ] A condition outside the repository (a deployment precondition, an external party's confirmation, post-release verification) is a release readiness gate with a named owner. It is never a task, and never silently assumed; a merged branch with an unmet gate is not done.
- [ ] Progress log is empty at creation — step 05 never pre-fills it.

## Skeleton

```markdown
---
ticket: <ID>
based_on: 03-agreement.spec.md, 03-target-solution.spec.md
created: <YYYY-MM-DD HH:MM>
max_advisor_rounds: 3
---

# Plan: <title>

**Story:** <one-sentence recap>
**Manifest:** [00-manifest.state.md](../00-manifest.state.md)
**Target Solution:** [03-target-solution.spec.md](../2-specification/03-target-solution.spec.md)

## Acceptance Criteria
*(copied verbatim from 03-agreement.spec.md)*

- [ ] <verbatim>

## Out of Scope
*(copied verbatim from 03-agreement.spec.md)*

- <verbatim>

## Tasks
*(same Group may run in parallel; groups run in order A -> B -> C)*

- [ ] **T1: <title>**
  - **Group:** A
  - **Files:** <exact paths>
  - **Done when:** <one verifiable condition>
  - <1–3 sentences anchored to the target solution>

- [ ] **T2: <title>**
  - **Group:** B
  - **Depends on:** T1
  - **Files:** <paths>
  - **Done when:** <condition>
  - <description>

## Advisor Checks
*(verified in addition to the acceptance criteria)*

- [ ] All tasks marked complete
- [ ] <custom check, e.g. "no references to removed symbol X">

## Release Readiness Gates
*(delivery gates, not pull requests; omit the section when none exist)*

- [ ] **G1:** <condition> · **Owner:** <who resolves it> · **Blocks:** <deployment of X | delivery close>

## Progress Log
<!-- appended during implementation, one line per task: -->
<!-- - <ISO-8601> — T<id>: <one-line outcome>   (prefix WARN on failure) -->
<!-- verification claims name the exact command and result; a suspected pre-existing failure names its base-branch evidence -->
```

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
| `## Acceptance Criteria` | yes | **verbatim** from `03-alignment.spec.md` |
| `## Out of Scope` | yes | **verbatim** from `03-alignment.spec.md` |
| `## Tasks` | yes | each with Group, Files, Done-when; optional Depends-on |
| `## Advisor Checks` | yes | verification beyond the ACs |
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

- [ ] ACs and out-of-scope are **character-identical** to `03-alignment.spec.md`. Not reordered, not "improved", nothing dropped.
- [ ] Every task has exact file paths and exactly one done-when that can be checked mechanically (file exists, test passes).
- [ ] Parallelism is conservative — tasks are only in the same group when they obviously touch disjoint files. When in doubt, sequential.
- [ ] Every task traces back to something `03-target-solution.spec.md` specifies. A task with no basis there is scope creep.
- [ ] Genuine ambiguity is encoded as an advisor check, not silently decided.
- [ ] Progress log is empty at creation — step 05 never pre-fills it.

## Skeleton

```markdown
---
ticket: <ID>
based_on: 03-alignment.spec.md, 03-target-solution.spec.md
created: <YYYY-MM-DD HH:MM>
max_advisor_rounds: 3
---

# Plan: <title>

**Story:** <one-sentence recap>
**Manifest:** [00-manifest.state.md](00-manifest.state.md)
**Target Solution:** [03-target-solution.spec.md](03-target-solution.spec.md)

## Acceptance Criteria
*(copied verbatim from 03-alignment.spec.md)*

- [ ] <verbatim>

## Out of Scope
*(copied verbatim from 03-alignment.spec.md)*

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

## Progress Log
<!-- appended during implementation, one line per task: -->
<!-- - <ISO-8601> — T<id>: <one-line outcome>   (prefix WARN on failure) -->
```

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

The plan's tasks are grouped into **work packages**: bounded units of one repository, one branch, one pull request each. Every plan has at least one; a single-PR story has exactly one and looks almost like a flat task list. Steps 06 to 09 operate on one named package at a time — the pipeline runs its head once, and its tail once per pull request.

The plan is also where **progress is recorded** — implementation ticks its task checkboxes and appends to the progress log here. Plan and reality in one file, so deviations are visible at a glance instead of buried in a second document.

> ⛔ **Blinded from the review.** Step 07 must not read this file: it carries the implementer's framing and conclusions, and reading it turns an independent review into a rubber stamp.

## Required sections

| Section | Required | Content |
|---|---|---|
| frontmatter | yes | ticket, based_on, created, `max_advisor_rounds` |
| `## Acceptance Criteria` | yes | **verbatim** from `03-agreement.spec.md` |
| `## Out of Scope` | yes | **verbatim** from `03-agreement.spec.md` |
| `## Work Packages` | yes | one section per package, at least one; tasks live inside their package |
| `## Advisor Checks` | yes | verification beyond the ACs |
| `## Release Readiness Gates` | if applicable | delivery gates that are not pull requests: each names its condition, its owner, and what it blocks |
| `## Progress Log` | yes | empty placeholder at creation; step 06 appends |

### Package fields

| Field | Required | Meaning |
|---|---|---|
| **Repository** | yes | the one component repository this package changes (a manifest component row) |
| **Base** | yes | the branch it forks from — normally the repository's main branch; another package's branch only when the plan explicitly approves a stacked branch, which carries the duty to rebase after the prerequisite merges |
| **Branch** | yes | the package's own branch name |
| **Prerequisites** | when needed | package IDs that must be merged first |
| **Readiness gates** | when needed | decisions or release gates that must be resolved before this package starts |
| **Primary ACs** | yes | the acceptance-criteria subset this package delivers, by AC number |
| **Status** | yes | planned → in-progress → in-review → merged, plus the PR link and merge commit once they exist; mirrored in the manifest's work-package ledger |
| **Close conditions** | yes | what must be true for the package to count as done |

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
- [ ] Every package maps to exactly one repository, one branch, and one pull request. No package exists to satisfy a count: a conditional package that stays unneeded is never created, and an empty PR is never opened.
- [ ] The delivery is complete only when every non-conditional package is merged; a package run never marks the whole delivery done.
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

## Work Packages

### WP-01: <package title>

- **Repository:** <component> · **Base:** <main> · **Branch:** <branch-name>
- **Prerequisites:** none · **Readiness gates:** none
- **Primary ACs:** AC1, AC2 · **Status:** planned
- **Close conditions:** <what must be true for this package to count as done>

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

*(a single-PR story has exactly this one package; a cross-repository delivery adds WP-02, WP-03, … in delivery order)*

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

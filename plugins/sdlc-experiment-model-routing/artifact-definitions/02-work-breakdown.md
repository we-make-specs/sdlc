---
artifact: 02-work-breakdown.md
produced_by: 02-analyze
consumed_by: [03-align, 05-plan]
required: true
---

# Contract — `02-work-breakdown.md` (slices and the PR cut)

## Purpose

How one story becomes reviewable pieces: the vertical slices, the candidate cut into work packages, and the open decisions that would change that cut. Drafted early because the slices sharpen the analysis — conditional scope, boundaries, and out-of-scope temptations surface here before anyone designs anything.

**Always produced, scaled honestly.** A story that is one package in one repository gets a one-line breakdown ("single package: <why>") and costs nothing. The artifact earns its size only when the story genuinely decomposes.

## Lifecycle

The same fill-in lifecycle as the question inventory: created once, filled in, never rewritten.

| Phase | Who | What happens to this file |
|---|---|---|
| step 02 | analyze | created: slices, candidate cut, conditional slices; every decision that changes the cut becomes a question-inventory entry, referenced here |
| step 03 | align | the cut decisions get answered like every other question; the agreed slices are recorded here |
| step 05 | plan | the final cut is frozen into the plan's package sections, copied the way ACs are copied; **after step 05 the plan owns the cut** and this artifact is history |

That last rule is the one-source rule for the cut: before the plan exists the cut lives only here, afterwards only there.

## Required sections

| Section | Required | Content |
|---|---|---|
| header block | yes | ticket, created, `Context loaded:` |
| `## Vertical slices` | yes | per slice: outcome, included functional groups, covered ACs, completion boundary — or the single-package one-liner |
| `## Conditional slices` | when they exist | scope that only materialises on an explicit product decision; never silently promoted to a package |
| `## Candidate cut` | yes | the proposed work packages: target repository, scope, dependencies, what each delivers |
| `## Open cut decisions` | yes | each an inventory entry reference (`Q<n>`) — or `none` |
| `## Sequencing` | when several packages | proposed order and why; which packages could run in parallel once dependencies allow |
| `## Source roots` / `## Source map` | when code is cited | per the shared evidence rules |

## Quality criteria

- [ ] Every slice has a completion boundary — where it ends is as explicit as what it does.
- [ ] Every decision that would change the cut is an inventory question, not a silent assumption in the cut itself.
- [ ] A conditional slice stays conditional until the product decision lands; no package exists to satisfy a count.
- [ ] After step 05, the plan's package sections match the agreed cut; this artifact is not updated afterwards.

## Skeleton

```markdown
# Work Breakdown: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>
- **Context loaded:** <registry articles read, or "none applicable">

## Vertical slices

*(single-package story: "Single package: <one sentence why no cut is needed>" and stop here)*

### Slice 1: <name>

- **Outcome:** <what a user or consumer can do afterwards>
- **Functional groups:** <the groups from the current-state research this slice touches>
- **Covers ACs:** AC1, AC2
- **Completion boundary:** <where this slice explicitly ends>

## Conditional slices

- <slice> — materialises only if <product decision, referenced as Q<n>>

## Candidate cut

| Package | Target repository | Delivers | Depends on |
|---|---|---|---|
| WP-01 | <component> | <slice or part> | none |

## Open cut decisions

- Q<n>: <the decision that changes this cut>

## Sequencing

<proposed order and why>
```

---
artifact: 05_questions.log.md
produced_by: 05-plan
consumed_by: [05-plan]
required: false
---

# Contract — `05_questions.log.md` (technical questions, optional)

## Purpose

Technical questions that surface during planning — collected, **prioritised**, and answered with a rationale. Optional, and normally created together with `05_technical-analysis.research.md`. The technical sibling of [`02_questions.log.md`](02_questions.log.md): same tiers, same fill-in lifecycle, one stage later.

The rationale is the actual value. An answer without one gets re-litigated; an answer with one settles the matter.

## Priority tiers

| Tier | Meaning | Deadline |
|---|---|---|
| **Critical** | blocks implementation | must be answered before the plan |
| **Important** | affects the design | should be answered before the plan |
| **Clarification** | nice to have | may be resolved during implementation |

The tiering is what makes this artifact useful: it separates "we cannot proceed" from "we would like to know", so the plan is not blocked by curiosity.

## Structure

Two layers in one file:
1. **The compact list** — tiered, each question with its answer and a one-line rationale. This is what gets read later.
2. **The full log** — only for questions where several options were seriously weighed: options, trade-offs, what was chosen, why. This is what gets read when someone asks "why on earth did we do it like that".

## Quality criteria

- [ ] Every question carries a tier. An untiered list cannot gate anything.
- [ ] No `Critical` question is unanswered when the plan is written.
- [ ] Every answer has a rationale, even a one-liner.
- [ ] Answers that create a durable commitment are also recorded in `decisions.log.md` — and, if they hold beyond this feature, as an ADR in the context registry.

## Skeleton

```markdown
# Open Technical Questions: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>

## Critical

- [ ] **Q1: <question>**
  - **Answer:** <open>
  - **Rationale:** <…>
  - **Answered by / on:** <…>

## Important

- [ ] **Q2: <question>**
  - **Answer:** <open>
  - **Rationale:** <…>

## Clarification

- [ ] **Q3: <question>**
  - **Answer:** <open>

## Full log

*(only for questions where several options were seriously considered)*

### Q<n>: <question>
- **Priority:** <tier>
- **Options considered:**
  - **A:** <…> — pro: <…> · con: <…>
  - **B:** <…> — pro: <…> · con: <…>
- **Chosen:** <…>
- **Why:** <…>
- **Date:** <…>
```

---
artifact: 06-decisions.log.md
produced_by: [03-align, 05-plan, 06-implement, 09-merge]
consumed_by: [all]
required: false
---

# Contract — `06-decisions.log.md` (decision log)

## Purpose

Every non-obvious decision for this feature — and **especially** the ones made during implementation, which the plan did not foresee.

Experience says a substantial share of decisions is not anticipated by any plan. Typical case: the analysis names a state, the code has long moved past it, and someone has to decide on the spot how to handle that. Exactly those decisions vanish without a log, and months later nobody understands why the code looks the way it does.

## Boundary

| Scope of the decision | Where it belongs |
|---|---|
| only this feature | here |
| beyond this feature | **also** as an ADR in the context registry (`03-architecture/adr/`) |

The `beyond this feature` field in each entry forces that judgment instead of leaving it implicit.

## Required fields per entry

| Field | Required | Content |
|---|---|---|
| Date / Who / Phase | yes | when, by whom, in which phase (planning / implementation / review) |
| Context | yes | what the situation was |
| Options | when several were weighed | what was considered |
| Decision | yes | what was chosen |
| Rationale | yes | why — the part that prevents re-litigation |
| Consequence | yes | what follows, now and later |
| Beyond this feature | yes | `yes → create an ADR` / `no` |

## Quality criteria

- [ ] Entries are appended, never rewritten — the log is a history, not a summary.
- [ ] Every entry has a rationale. A decision without one is a note, not a decision.
- [ ] Decisions made *after* the plan was approved are recorded here rather than silently changing the plan.
- [ ] Anything marked "beyond this feature" actually results in an ADR.

## Skeleton

```markdown
# Decision Log: <title>

- **Ticket:** <ID>

## D1: <short name>

- **Date:** <YYYY-MM-DD> · **Who:** <who> · **Phase:** planning | implementation | review
- **Context:** <what was the situation?>
- **Options:**
  1. <…>
  2. <…>
- **Decision:** <what was chosen>
- **Rationale:** <why>
- **Consequence:** <what follows — now and later>
- **Beyond this feature:** yes → create an ADR | no

## D2: <short name>

<…>

*Append new decisions below — also after the plan is approved.*
```

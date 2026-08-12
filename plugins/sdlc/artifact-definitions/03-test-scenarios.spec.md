---
artifact: 03-test-scenarios.spec.md
produced_by: 03-align
consumed_by: [04-approve-target-solution, 05-plan, 06-implement, 07-review]
required: true
carries_approval: true
---

# Contract — `03-test-scenarios.spec.md` (what will be tested)

## Purpose

The **functional** scenarios this feature must satisfy, plus rough test data for each — agreed with the human *before* implementation.

This artifact exists because of a specific failure: tests get written, but *what is being tested* never surfaces. The agent picks the scenarios silently, nobody reviews that choice, and the gap only shows up in production. Splitting the scenarios out of the design document makes them something a human has to look at.

**Scope:** business cases, their data, and the exceptional cases. **Not** unit tests, not test code, not coverage targets — those are decided at planning and implementation time.

## Required sections

| Section | Required | Content |
|---|---|---|
| header block | yes | ticket, created, **status** (`DRAFT` / `IN REVIEW` / `APPROVED`), approved-by, approved-on; after approval, dated `Correction:` / `Amendment:` entries per the amendment protocol (catalog README, rule 8) when a change happens |
| `## Happy Path Scenarios` | yes | the normal business cases, numbered, one line each |
| `## Exceptional Scenarios` | yes | error, conflict, empty, boundary and permission cases |
| `## Test Data` | yes | rough data per scenario — enough to recognise it, not a fixture file |
| `## Out of Scope` | yes | scenarios deliberately **not** covered, with a reason |
| `## Open Questions` | if applicable | what the human still has to decide |

## Quality criteria

- [ ] Every acceptance criterion from `03-alignment.spec.md` maps to at least one scenario.
- [ ] Scenarios are phrased in **domain language**, not in terms of methods or classes. A product person must be able to read them.
- [ ] Exceptional scenarios exist and are specific. "Handles errors" is not a scenario.
- [ ] Permission and role cases are covered where the feature is role-dependent — see `05-domain/roles-and-permissions.md`.
- [ ] Test data is concrete enough to be recognisably wrong. `<some customer>` fails this; `customer with 0 contracts, market DE` passes.
- [ ] Out of Scope is non-empty, or explicitly states that nothing was excluded.
- [ ] Status is `APPROVED` with a name and a date before step 05 starts.

## How this gets reviewed — the part that matters

The agent must **ask, not report.** A list presented for acknowledgement gets a nod; a list presented as a question gets engagement.

At the end of step 03, and again at gate 04, the human is asked explicitly:

> "Here are N scenarios and the data they run on. **Which of these are wrong, and what is missing?**"

The gate is not passed by the human saying "looks good" — it is passed by the human either naming a change or explicitly confirming that they checked and found nothing missing.

## Downstream use

- **Step 05 (plan)** derives the test tasks from this file. A scenario without a corresponding task is a planning bug.
- **Step 06 (implement)** covers the scenarios listed here. Deviations are recorded, not silently dropped.
- **Step 07 (review)** checks the diff against this file — an approved scenario without a test is a review finding.

## Skeleton

```markdown
# Test Scenarios: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>
- **Status:** DRAFT | IN REVIEW | APPROVED · **Approved by:** <who> · **on:** <YYYY-MM-DD>
- **Discussion:** [03-alignment.spec.md](03-alignment.spec.md) · **Design:** [03-target-solution.spec.md](03-target-solution.spec.md)

## Happy Path Scenarios

| # | Scenario | Covers AC |
|---|---|---|
| H1 | <given … when … then …, in domain language> | AC-1 |

## Exceptional Scenarios

| # | Scenario | Expected behaviour | Covers AC |
|---|---|---|---|
| E1 | <the error, conflict, empty, boundary or permission case> | <what must happen> | AC-3 |

## Test Data

| Scenario | Data needed |
|---|---|
| H1 | <concrete enough to be recognisably wrong> |

## Out of Scope

- <scenario deliberately not covered> — <why>

## Open Questions

- <what the human still has to decide>
```

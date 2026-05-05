---
artifact: 01_current-solution.research.md
produced_by: 01-research-current-solution
consumed_by: [02-analyze, 03-align, 05-plan, 07-review]
required: false
---

# Contract — `01_current-solution.research.md` (current state)

## Purpose

How the affected functionality works **today** — the factual baseline for the analysis, the alignment and the plan. Describes only what exists; proposes nothing.

## The rule that defines this artifact

**No speculation.** Every statement must be verifiable in the code, cited as `path:line`. What could not be established goes under "Unresolved" — never into a plausible guess. A wrong current-state poisons every artifact downstream, and it is the failure mode that is hardest to notice later.

## Required sections

| Section | Required | Content |
|---|---|---|
| `## Summary` | yes | 3–5 sentences: how the flow works today |
| `## Involved components` | yes | service/module, role in this flow, entry point |
| `## Flow today` | yes | trigger → entry point → processing → persistence → output, with real names |
| `## Relevant data structures` | yes | entities/DTOs, key fields, where defined |
| `## Relevant endpoints / events` | yes | kind, identifier, where implemented |
| `## Existing tests` | yes | what is covered — **and where nothing is covered** |
| `## Limitations & surprises` | yes | what is awkward or surprising; what to know before changing it |
| `## Unresolved` | yes | honest gaps; input for the analysis |

## Quality criteria

- [ ] Every load-bearing claim carries a `path:line` citation.
- [ ] Where documentation and code disagree, the **code** is reported and the discrepancy noted.
- [ ] The gaps section is real. An empty "Unresolved" on a non-trivial area usually means guessing happened.
- [ ] Scope stayed inside the story text from the manifest — no unrelated exploration.
- [ ] If the functionality does not exist yet: say so, then describe the nearest analogous code as a reference point. Do not invent structure.
- [ ] No proposals, no alternatives, no improvements — those belong to step 03.

## Skeleton

```markdown
# Current Solution: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>

## Summary

<3–5 sentences: how the affected flow works today>

## Involved components

| Service / module | Role in this flow | Entry point (file) |
|---|---|---|
| <…> | <…> | <…> |

## Flow today

<trigger → entry point → processing → persistence → output, with real class/method names>

## Relevant data structures

| Entity / DTO | Important fields | Defined where |
|---|---|---|
| <…> | <…> | <…> |

## Relevant endpoints / events

| Kind | Identifier | Implemented where |
|---|---|---|
| <…> | <…> | <…> |

## Existing tests

| Test class | Covers | Where |
|---|---|---|
| <…> | <…> | <…> |

<also note where there is no coverage — that is implementation risk>

## Limitations & surprises

<what is awkward, error-prone, or surprising; what to know before changing anything here>

## Unresolved

- <question that could not be answered from the code>
```

---
artifact: 03-target-solution.spec.md
produced_by: 03-align
consumed_by: [04-approve-target-solution, 05-plan, 06-implement, 07-review]
required: true
carries_approval: true
---

# Contract — `03-target-solution.spec.md` (the design)

## Purpose

How the solution will look. Precise enough that a **separate session could implement it without asking follow-up questions**. This is the artifact the human approves at gate 04, and the reference the blinded review judges the diff against.

It mirrors the current-state research's structure, projected into the future state: conceptual model, components, flows, data structures. Read side by side, research and design are before and after of the same shape — which is exactly how a reviewer thinks.

It carries the approval status in its header — approval lives in the artifact, not only in the ticket system.

## Required sections

| Section | Required | Content |
|---|---|---|
| header block | yes | ticket, created, **status** (`DRAFT` / `IN REVIEW` / `APPROVED`), approved-by, approved-on; after approval, dated `Correction:` / `Amendment:` entries per the amendment protocol (catalog README, rule 8) when a change happens |
| `## Overview` | yes | the end-state shape in a few sentences |
| `## Target conceptual model` | yes | the new and changed concepts and their relationships, in domain language — the future-state mirror of the research's conceptual model |
| `## Behaviour` | yes | happy path plus edge cases, from the caller's point of view |
| `## Affected components` | yes | functional groups with their change, concrete new/modified paths, port/adapter impact — mirrors the research's involved components |
| `## Target flows` | yes | the named flows as they will run, step by step; reuse the research's flow names where the flow exists today |
| `## Target data structures` | yes | the layer projection per concept; when persisted data changes, the per-layer table: current shape, agreed change, migration and compatibility |
| `## Migration / Rollout` | if applicable | migrations, flags, backward compatibility, phased rollout — or "not applicable" |
| `## Testing Strategy` | yes | the *technical* strategy: which test type on which layer, what needs a harness or fixture. The **functional scenarios live in [`03-test-scenarios.spec.md`](03-test-scenarios.spec.md)** — do not duplicate them here |

## Quality criteria

- [ ] Someone who did not attend the discussion could implement from this without further questions. That is the bar.
- [ ] Component claims name **concrete paths**, not areas.
- [ ] Flows and concepts reuse the research document's names where they exist today, so the two documents diff cleanly.
- [ ] Data-model claims (migration numbers, schema state) are verified against the repository, not carried over from another document.
- [ ] When persisted data changes, the data-model part is a per-layer table: layer, current shape, agreed change, migration and compatibility, covering omitted, null, and legacy-data semantics. A rollback line appears only when the story has a real rollback question. The underlying semantics decisions live in the agreement; this table is their design.
- [ ] Edge cases are present: empty inputs, concurrency, failure paths, partial state, backward compatibility.
- [ ] Consistent with `03-agreement.spec.md` — the design satisfies every AC there, and adds no scope beyond it.
- [ ] Status is `APPROVED` with a name and a date before step 05 starts.

## Companion — `03-target-overview.view.html` (required)

A single self-contained page (inline CSS, diagrams as inline SVG, no external requests, renders offline from `file://`) — **the pre-read of gate 04**. It summarises intent, acceptance criteria, key decisions, components, flows, and data structures, renders the test scenarios under the verbatim scenario question (**"Which of these are wrong, and what is missing?"**), and shows the question-inventory status (Critical/Important all answered; deferrals listed). It also lists every `assumed` answer with its verification owner and due point, and, once one exists, the corrections and amendments recorded since approval, so the one page carries everything the decision rests on. Its purpose is to make the gate a real review rather than a rubber stamp: the human opens one page instead of skimming three documents — the page links all three at the end, and approval is still given on the artifacts, not on the summary.

## Skeleton

```markdown
# Target Solution: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>
- **Status:** DRAFT | IN REVIEW | APPROVED · **Approved by:** <who> · **on:** <YYYY-MM-DD>
- **Discussion:** [03-agreement.spec.md](03-agreement.spec.md)

## Overview

<the end-state shape>

## Target conceptual model

| Concept | New or changed | What it is in the target state | Relationships |
|---|---|---|---|
| <concept> | <new \| changed> | <in domain language> | <…>

## Behaviour

- **Happy path:** <…>
- **Edge cases:** <empty inputs, concurrency, failure paths, partial state, backward compatibility>

## Affected components

| Functional group | Change | New / modified paths |
|---|---|---|
| <group, named as in the research> | <what changes> | <concrete paths> |

- **Port/adapter impact:** <which boundaries are touched>

## Target flows

### <flow name, as in the research>

<step-by-step trace: trigger → entry point → processing → persistence → output>

## Target data structures

<one row per concept and layer — the future-state projection>

| Layer | Current shape | Agreed change | Migration and compatibility |
|---|---|---|---|
| <domain / persistence / API> | <…> | <…> | <migration, backfill, omitted/null/legacy semantics> |

## Migration / Rollout

<migrations, flags, backward compatibility, phased rollout — or "not applicable">

## Testing Strategy

- **Unit:** <…>
- **Integration:** <…>
- **Harness / fixtures needed:** <…>
- **Functional scenarios:** see [03-test-scenarios.spec.md](03-test-scenarios.spec.md)
```

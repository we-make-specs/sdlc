---
artifact: 03-alignment.spec.md
produced_by: 03-align
consumed_by: [04-approve-target-solution, 05-plan, 07-review, 08-review-pr]
required: true
---

# Contract — `03-alignment.spec.md` (alignment record)

## Purpose

What was **agreed** between human and agent. This is the stable half of step 03: the record of intent and commitments. How the solution will *look* is the other half ([`03-target-solution.spec.md`](03-target-solution.spec.md)) and may still move during planning — this one should not.

It is the origin of the acceptance criteria, which every later stage quotes verbatim.

## Required sections

| Section | Required | Content |
|---|---|---|
| `## Intent` | yes | 1–2 sentences: what the story is about and why |
| `## Acceptance Criteria` | yes | numbered checkbox list, each item concrete and testable |
| `## Key Decisions` | yes | every direction-setting call, each with a `Rationale:` |
| `## Constraints` | yes | performance, security, compliance, dependencies, timing |
| `## Out of Scope` | yes | explicit exclusions — may be a single "nothing excluded" entry, but never absent |
| `## Open Questions` | yes | empty if alignment was reached; deferred items otherwise, each referencing its inventory entry (`Q<n>` in `02-questions.inventory.md`) |

## Quality criteria

- [ ] Every AC is **verifiable**: an observable outcome, not a quality adjective. "Works reliably" fails; "returns 404 with error code X for an unknown ID" passes.
- [ ] Every key decision carries a rationale — the reason is the part that stops it being re-litigated in three months.
- [ ] Out of scope is genuinely populated. An empty out-of-scope list on a non-trivial story means the boundary was never discussed.
- [ ] No open question marked critical is left unanswered — the gate must not approve over one.
- [ ] Consistent with `00-manifest.state.md`; nothing agreed here contradicts the original story text.

## Skeleton

```markdown
# Alignment: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>
- **Manifest:** [00-manifest.state.md](00-manifest.state.md)

## Intent

<1–2 sentences>

## Acceptance Criteria

- [ ] AC1: <verifiable, observable condition>
- [ ] AC2: <…>

## Key Decisions

- **<decision>** — Rationale: <why>
- **<decision>** — Rationale: <why>

## Constraints

<performance, security, compliance, dependencies, timing>

## Out of Scope

- <explicitly excluded>

## Open Questions

- <question — or leave empty when alignment was reached>
```

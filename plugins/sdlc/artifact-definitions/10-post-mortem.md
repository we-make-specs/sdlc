---
artifact: 10-post-mortem.md
produced_by: 10-post-mortem
consumed_by: [humans, future deliveries]
required: true
---

# Contract — `10-post-mortem.md` (the close-out record)

## Purpose

One page that closes the delivery: what shipped, what the delivery taught, and where the lessons went. Written at step 10, after the ledgers are reconciled and the assumptions settled. It is the file someone opens a year later to understand how this delivery went — not a report, a record.

## Required sections

| Section | Required | Content |
|---|---|---|
| header block | yes | ticket, closed (date), `Context loaded:` |
| `## Shipped` | yes | the packages with their merge commits, one line each; merges done outside the pipeline marked as such |
| `## Assumptions settled` | yes | each assumed answer: verified (who, when) or accepted as risk (by whom) — or `none were open` |
| `## What went well` | yes | two to five bullets, specific |
| `## What did not` | yes | two to five bullets, specific; an empty list on a non-trivial delivery means nobody looked |
| `## Where the lessons went` | yes | the harvest: registry proposals (linked), pipeline improvements (recorded where), or `nothing generalizable` |

## Quality criteria

- [ ] Fits on one page; the artifacts carry the detail, this note carries the shape.
- [ ] Every bullet is specific enough to be disputed; "communication could improve" fails, "the SeaF-style external confirmation had no owner until week two" passes.
- [ ] Every harvested lesson has a destination, not an intention: a linked registry proposal or a recorded improvement note.
- [ ] Written only after `status: done` conditions were met; never over an open delivery.

## Skeleton

```markdown
# Post-Mortem: <title>

- **Ticket:** <ID> · **Closed:** <YYYY-MM-DD>
- **Context loaded:** <registry articles read, or "none applicable">

## Shipped

- WP-01: <PR link>, merged as `<commit>`
- WP-02: <PR link>, merged as `<commit>` (merged outside the pipeline)

## Assumptions settled

- Q<n>: verified by <who>, <date> — <one line on the outcome>
- Q<m>: accepted as standing risk by <who>, <date>

## What went well

- <specific>

## What did not

- <specific>

## Where the lessons went

- <lesson> → registry proposal: <link>
- <lesson> → pipeline improvement note: <where>
```

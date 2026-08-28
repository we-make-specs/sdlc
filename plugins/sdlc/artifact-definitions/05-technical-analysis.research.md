---
artifact: 05-technical-analysis.research.md
produced_by: 05-plan
consumed_by: [05-plan]
required: false
---

# Contract — `05-technical-analysis.research.md` (technical pre-stage, optional)

## Purpose

The bridge from "what should happen functionally" to "what the code for it looks like". **Optional** — create it only when the change has real technical depth (new data model, cross-service change, unclear existing structure). For a small, well-understood change, skip it; an unnecessary analysis is cost without value.

## Required sections

| Section | Required | Content |
|---|---|---|
| `## Technical summary` | yes | 3–5 sentences: what needs doing technically |
| `## Current-state analysis per component` | yes | entities, endpoints, persistence, services/mappers, error handling, external calls |
| `## Planned data-model changes` | if applicable | new/modified entities, migration needed and which number is next |
| `## Planned API changes` | if applicable | endpoints, request/response, permission, breaking yes/no |
| `## Reference-pattern comparison` | yes | see below |
| `## Pattern choices and naming` | when a choice is non-obvious | why a strong local pattern is followed or not; application port names and their business intent |
| `## Technical constraints & assumptions` | yes | what we presuppose, what limits us |
| `## Risks` | yes | risk, impact, handling |
| `## Planning uncertainty` | yes | facts that must be re-verified immediately before execution, each with the reason it is perishable; `none` is a valid entry |

## The reference-pattern comparison

The most valuable section. It compares the target code against the reference implementation named in the development guidelines, row by row, and marks each as `Aligned` / `Deviation` / `Gap`.

Why it earns its place: without it, an agent either "fixes" grown idiosyncrasies that were deliberate, or copies them into new code assuming they are the standard. Naming the deviation and how to handle it prevents both.

| Aspect | Reference implementation | This service | Verdict | Reason / handling |
|---|---|---|---|---|
| e.g. mapper style | generated mapper | manual mapper | Aligned / Deviation / Gap | `<why this choice is appropriate here>` |

Every deviation needs a stated handling, e.g. *"existing code stays as is, new code follows the
reference"*. A non-obvious choice against a strong local pattern must name its concrete benefit and
trade-off; silence is a traceability gap. Do not invent a reason after implementation.

## Quality criteria

- [ ] Every current-state claim is verified against the repository — **especially** migration numbers and schema state, which are the classic stale-document trap.
- [ ] Every fact that can drift between planning and execution (a migration number, a schema state, an external party's status) is a planning-uncertainty entry. Step 05 turns each into a just-in-time advisor check, so the plan re-verifies it at the moment it matters instead of baking in a stale constant.
- [ ] The reference comparison names a concrete reference service, not "our conventions".
- [ ] Each deviation has an explicit handling decision.
- [ ] Mapper strategy is explicit when generated and manual mapping are both plausible; the record names why the chosen approach fits this layer and repository.
- [ ] Application port names express the use case's intent, not an adapter's persistence or transport mechanism. An outbox enqueue operation is not called `publish` unless delivery is synchronous.
- [ ] Long service methods were inspected for skimmability; planned comments describe logical blocks or invariants in one short line, never narrate syntax.
- [ ] Breaking changes are named as such, with the handling.

## Skeleton

```markdown
# Technical Analysis: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>
- **Based on:** 03-agreement.spec.md, 03-target-solution.spec.md

## Technical summary

<3–5 sentences>

## Current-state analysis per component

### <service / module>

#### Entities
| Entity | Important fields | Type | Notes |

#### Endpoints
| Method | Path | Request | Response | Permission |

#### Persistence
<tables/collections, latest migration state — verified in the repo>

#### Services, repositories, mappers
#### Error handling
#### Calls to external systems

## Planned data-model changes

- **New entities/fields:** <…>
- **Modified:** <…>
- **Migration needed:** yes/no — next number: <…>

## Planned API changes

| Method | Path | Request | Response | Permission | New/changed |

- **Breaking change:** yes/no — handling: <…>

## Reference-pattern comparison

| Aspect | Reference implementation | This service | Verdict | Reason / handling |
|---|---|---|---|---|
| <…> | <…> | <…> | Aligned / Deviation / Gap | <…> |

**Handling of deviations:** <…>

## Pattern choices and naming

- **Mapper strategy:** <generated / manual / not applicable> — **because:** <verified reason and trade-off>
- **Application ports:** <name → application intent; adapter mechanism kept out of the name>
- **Skimmability:** <logical blocks that need one-line intent/invariant comments, or none>

## Technical constraints & assumptions

## Risks

| Risk | Impact | Handling |

## Planning uncertainty

| Fact to re-verify at execution time | Why it is perishable |
|---|---|
| <e.g. the latest migration number> | <another change may land between planning and execution> |
```

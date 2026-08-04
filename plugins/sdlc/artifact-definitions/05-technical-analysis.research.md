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
| `## Technical constraints & assumptions` | yes | what we presuppose, what limits us |
| `## Risks` | yes | risk, impact, handling |

## The reference-pattern comparison

The most valuable section. It compares the target code against the reference implementation named in the development guidelines, row by row, and marks each as `Aligned` / `Deviation` / `Gap`.

Why it earns its place: without it, an agent either "fixes" grown idiosyncrasies that were deliberate, or copies them into new code assuming they are the standard. Naming the deviation and how to handle it prevents both.

| Aspect | Reference implementation | This service | Verdict |
|---|---|---|---|
| e.g. PK naming | `<pattern>` | `<pattern>` | Aligned / Deviation / Gap |

Every deviation needs a stated handling, e.g. *"existing code stays as is, new code follows the reference"*.

## Quality criteria

- [ ] Every current-state claim is verified against the repository — **especially** migration numbers and schema state, which are the classic stale-document trap.
- [ ] The reference comparison names a concrete reference service, not "our conventions".
- [ ] Each deviation has an explicit handling decision.
- [ ] Breaking changes are named as such, with the handling.

## Skeleton

```markdown
# Technical Analysis: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>
- **Based on:** 03-alignment.spec.md, 03-target-solution.spec.md

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

| Aspect | Reference implementation | This service | Verdict |
|---|---|---|---|
| <…> | <…> | <…> | Aligned / Deviation / Gap |

**Handling of deviations:** <…>

## Technical constraints & assumptions

## Risks

| Risk | Impact | Handling |
```

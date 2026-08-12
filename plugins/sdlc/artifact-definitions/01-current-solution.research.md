---
artifact: 01-current-solution.research.md
produced_by: 01-research-current-solution
consumed_by: [02-analyze, 03-align, 05-plan]
required: false
---

# Contract — `01-current-solution.research.md` (current state)

## Purpose

How the affected functionality works **today**: the factual baseline for the analysis, the alignment and the plan. It describes only what exists and proposes nothing. One document serves both readers: the body reads clean for humans, and the source map at the end keeps every fact traceable to exact code locations for agents. This step produces no companion documents: no HTML preview, no overview, no details appendix.

## The rule that defines this artifact

**No speculation.** Every statement must be verifiable in the code and carry at least one evidence ID that resolves in the source map to an exact `path:line` location. What could not be established goes under "Unresolved", never into a plausible guess. A wrong current-state poisons every artifact downstream, and it is the failure mode that is hardest to notice later.

## Evidence and the source map

The body stays readable because exact locations live in one place at the end.

1. Facts in the body cite short evidence IDs such as `[F2]` and `[B17]`; a fact that crosses boundaries carries several IDs.
2. `## Source roots` declares a short prefix for every repository that appears in the source map.
3. `## Source map` holds one row per ID: the exact location as declared root prefix plus `path:line`, `path:start-end`, or a comma-separated list of such ranges, and a `Supports` column naming the fact the source establishes.
4. Every factual sentence or table row carries at least one ID. Every ID resolves exactly once in the source map. Every source-map row is cited at least once in the body, so the two sets can be diffed in both directions.
5. Absolute paths are prohibited, and long paths appear only in the source map.
6. A source is listed because it establishes a fact, never because it is nearby or looks relevant.
7. ID prefixes are a reader convention that groups related evidence, typically one letter per area plus `T` for tests. Only the source map carries locations. Gaps in the numbering are fine; IDs are never renumbered when a source drops out.
8. A source-map location may additionally be written as a relative markdown link with line anchors (`path/to/File.java#L42-L60`), so it opens directly in hosts that render links. The visible text keeps the exact `path:line` location either way.

## Decomposition

Two directions of decomposition exist, and neither is mandatory:

- horizontal, technical: areas such as frontend and backend, layers, repositories
- vertical, functional: the functional slices a story disassembles into

Choose per story, never mechanically. `## Involved components` uses subsections along the axis that explains this story best: technical areas for a typical full-stack story, functional slices when the story is really several sub-features, or a single flat table when neither split adds meaning. `## Flow today` is the guaranteed vertical view: one named flow per functional slice of the current solution. When the story decomposes into sub-features, name the slices in the summary and reuse those names in components, flows and tests. Never force a decomposition the story does not have; a simple story is one slice with one components table.

## Functional groups

A functional group is code that carries one current responsibility on the story's path: it owns story-relevant data, transforms it, exposes it through an interface, validates it, or proves it with tests. Name it for its responsibility in the system's own language ("order edit form", "checkout price validation"), never for a folder or a class list. Include a group when removing it would change the story-relevant behavior of the current solution; leave it out when it is merely nearby. Groups are the units of the document; the decomposition axis only decides how they are arranged into subsections.

Where to look, not what to fill in; empty groups are not created:

| Layer | Functional groups to consider |
|---|---|
| Frontend | page entry, state and loading, edit interaction, form controls, client model, HTTP service, feature visibility, tests |
| Backend API | inbound endpoint, request and response contract, authorization, mapper |
| Backend domain | use case or service, domain model, policy or validator, event handling |
| Persistence | entity or document, mapper, repository, migration |
| Integration | external endpoint, producer or consumer, adapter, schema |
| Cross-cutting | feature flag, error mapping, observability, permissions |
| Tests | unit, integration, end-to-end, contract, missing coverage |

## Required sections

| Section | Required | Content |
|---|---|---|
| header block | yes | ticket, date, `Context loaded:`, reading key |
| `## Summary` | yes | 3–5 sentences with evidence IDs: how the affected flow works today; names the functional slices when the story decomposes |
| `## Conceptual model` | yes | the story-relevant concepts and their relationships, in domain language, implementation-free |
| `## Involved components` | yes | functional groups with current responsibility, relation to this story, evidence |
| `## Flow today` | yes | one named flow per functional slice, as step tables |
| `## Relevant data structures` | yes | the layer projection of the concepts: one row per concept and layer, with the story-relevant field status |
| `## Relevant endpoints / events` | yes | kind, identifier, current behavior |
| `## Existing tests` | yes | what is covered, **and what is not covered** |
| `## Limitations & surprises` | yes | what is awkward or surprising; what to know before changing it |
| `## Unresolved` | yes | honest gaps as questions for the analysis, with what the code does establish |
| `## Source roots` | yes | prefix per repository |
| `## Source map` | yes | one row per evidence ID |

The conceptual model answers what exists and how it relates, independent of implementation; behavior belongs to the flows. `## Relevant data structures` then projects each concept onto the layers where it materializes (client model, API contract, domain, persistence, external contract), one row per concept and layer, so cross-layer gaps become visible at a glance. The generic column `Story-relevant field status` may be renamed to the concrete concern when that reads better.

## Quality criteria

- [ ] Every factual sentence or table row carries at least one evidence ID; every ID resolves exactly once in the source map; every map row is cited in the body.
- [ ] Every source-map location uses a declared source root and exact line ranges (`path:line`, `path:start-end`, or a comma-separated list of ranges); no absolute paths; no long paths outside the map.
- [ ] The conceptual model is implementation-free and every concept is evidence-backed.
- [ ] `## Involved components` is non-empty, grouped by responsibility, and every group passes the removal test.
- [ ] At least one current flow is described. If the functionality does not exist yet: say so, then describe the nearest analogous code as a reference point. Do not invent structure.
- [ ] The test matrix names missing coverage for any non-trivial scope.
- [ ] Where documentation and code disagree, the **code** is reported and the discrepancy noted.
- [ ] The unresolved section is genuinely populated where the code was ambiguous. An empty "Unresolved" on a non-trivial area usually means guessing happened.
- [ ] Scope stayed inside the story text from the manifest; no unrelated exploration.
- [ ] No proposals, no alternatives, no improvements; those belong to step 03.
- [ ] No companion files were created.

## Skeleton

```markdown
# Current Solution: <title>

- **Ticket:** <ID> | **Created:** <YYYY-MM-DD>
- **Context loaded:** <registry articles read, or "none applicable">
- **Reading key:** Evidence IDs such as `[F1]` and `[B1]` resolve to exact
  `path:line` locations in the source map at the end. The body contains
  current facts only.

## Summary

<3–5 sentences: how the affected flow works today, each with evidence IDs;
 name the functional slices when the story decomposes into sub-features>

## Conceptual model

<story-relevant concepts in domain language, implementation-free;
 an optional mermaid diagram when relationships are non-trivial>

| Concept | What it is today | Relationships | Evidence |
|---|---|---|---|
| <...> | <...> | <...> | [B1] |

## Involved components

<subsections along the axis that explains this story best: technical areas
 (typical: Frontend, Backend), functional slices, or one flat table>

### <Area or slice>

| Functional group | Current responsibility | Relation to this story | Evidence |
|---|---|---|---|
| <...> | <...> | <why it is on the story's current path> | [F1] |

## Flow today

### <named flow, one per functional slice>

| Step | Current behavior | Evidence |
|---|---|---|
| 1. <...> | <...> | [B1] |

## Relevant data structures

| Concept | Layer or boundary | Representation | Story-relevant field status | Evidence |
|---|---|---|---|---|
| <...> | <client model / API contract / domain / persistence / ...> | `<TypeName>` | <present / absent> | [B2] |

## Relevant endpoints / events

| Kind | Identifier | Current behavior | Evidence |
|---|---|---|---|
| <...> | <...> | <...> | [B3] |

## Existing tests

| Area | Covered today | Not covered today | Evidence |
|---|---|---|---|
| <...> | <...> | <...> | [T1] |

## Limitations & surprises

| Observation | Current consequence | Evidence |
|---|---|---|
| <...> | <...> | [B4] |

## Unresolved

| Question for analysis | What the code establishes | Evidence |
|---|---|---|
| <...> | <...> | [F2] |

## Source roots

| Prefix | Repository root |
|---|---|
| `<root>` | `<repository-folder>/` |

## Source map

| ID | Exact source location | Supports |
|---|---|---|
| F1 | `<root>/path/to/file:69-70,94-117` | <fact this establishes> |
```

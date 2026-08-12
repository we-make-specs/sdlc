---
artifact: research-note.research.md
produced_by: any step
consumed_by: [all]
required: false
---

# Contract — research notes (`1-research/<step>-<topic>.research.md`)

## Purpose

Research is a stream, not a single step output. The current-state baseline opens the series, and any later step may add an investigation: a scope question answered from the knowledge base during analysis, a runtime-configuration question that surfaces mid-implementation. Without a home, those investigations die in chat history.

This contract governs every research note **except** `01-current-solution.research.md`, which keeps its own dedicated contract. Instances are named `<step>-<topic>.research.md`: the prefix is the step that spawned the investigation, so provenance stays visible (`06-runtime-config.research.md` was triggered during implementation). This is the one artifact whose instance names vary; each instance is registered in the manifest's artifact ledger when created.

## Required sections

| Section | Required | Content |
|---|---|---|
| header block | yes | ticket, investigated (date), **status** (`complete` \| `superseded` — with what superseded it and why the findings stay), `Context loaded:` |
| `## Question` | yes | the one question this note answers |
| `## Findings` | yes | facts only, evidence per the shared evidence rules |
| `## Conclusion` | yes | what the sources establish, cleanly separated from what stays open; open points become inventory entries, never silent assumptions |
| `## Source roots` / `## Source map` | yes | per the shared evidence rules |

A note whose design context later disappears is not deleted: its status says `superseded`, and the findings remain valid history (the investigation that supported a dropped feature still documents how the system works).

## Business-evidence notes

Not every question is answerable from code. A business-evidence note answers a scope or intent question from the project's knowledge base — meeting notes, onboarding summaries, wikis, specification collections — with the same evidence discipline: source-relative locations in the source map, and a conclusion that separates what the sources establish from the boundary they do not.

Where such research may look, in order, never hardcoded in a skill:

1. **The feature seed** — the input directory the human filled before the pipeline started; it is already the read-only home of the original inputs.
2. **The context registries** the repo declares — a registry article may name the knowledge base and how to read it.
3. **The human** — as a missing-input inventory entry when neither source yields the evidence.

## Quality criteria

- [ ] One question per note; a second question is a second note.
- [ ] Findings are facts with resolving evidence IDs; interpretation lives only in the conclusion.
- [ ] The conclusion names what stays open, and every open point exists as an inventory entry.
- [ ] The note is registered in the manifest's artifact ledger.
- [ ] Knowledge-base sources are cited by source-relative path and location, never by memory.

## Skeleton

```markdown
# <Topic>

- **Ticket:** <ID> · **Investigated:** <YYYY-MM-DD>
- **Status:** complete
- **Context loaded:** <registry articles read, or "none applicable">

## Question

<the one question>

## Findings

<facts with evidence IDs>

## Conclusion

<what the sources establish. What stays open, referenced as Q<n>.>

## Source roots

| Prefix | Root |
|---|---|
| `KB` | <knowledge-base root or repository root> |

## Source map

| ID | Exact source location | Supports |
|---|---|---|
| K1 | `KB/path/to/note.md:12-30` | <the fact> |
```

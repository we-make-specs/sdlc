---
name: 02-analyze
description: Pipeline step 02 (AUTO) — read the story the way a skeptical implementer would, hunt for gaps, ambiguities, contradictions, edge cases and missing inputs, and write the tiered question inventory that seeds the alignment conversation. Use after the current-state research, before step 03.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.6.0'
  tags: sdlc, step, analysis, questions, gap-hunting
---

# Step 02 · Analyze  (AUTO)

- **Type:** AUTO — fresh session, rehydrates entirely from disk, asks no questions
- **Skippable:** no — stories look clearer than they are; a genuinely clear story earns a short inventory, not a skipped step

---

## What this skill does

Decomposes the story into atomic claims, probes each claim against the current state and against itself, and writes every unresolved point as a **self-contained, tiered, tracked question** into `02-questions.inventory.md` — the agenda the alignment conversation works through, and the pre-read the human opens as `02-questions.view.html`.

This step **finds** the questions; it never asks them. Asking is step 03's job, live with the human.

## When to use this skill

- After the current-state research, before the alignment conversation
- Again when the story text changed materially since the last analysis

## When NOT to use this skill

- Never skip it outright. On a trivial story the hunt is cheap and the result — a short inventory with a full coverage record — is still worth having in writing.

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | located via the manifest for the current branch | yes |
| Codebase | read/search access | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure: read each declared registry's `index.md` and navigate its index tables to the glossary and component-catalog articles this step touches. Record a `Context loaded:` line near the top of the question inventory (`none applicable` when nothing is declared); term mismatches are hunted against whatever glossary the registries hold.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `00-manifest.state.md` | [`artifact-definitions/00-manifest.state.md`](../../artifact-definitions/00-manifest.state.md) |
| reads *(when present)* | `01-current-solution.research.md` | [`artifact-definitions/01-current-solution.research.md`](../../artifact-definitions/01-current-solution.research.md) |
| writes | `02-questions.inventory.md` | [`artifact-definitions/02-questions.inventory.md`](../../artifact-definitions/02-questions.inventory.md) |
| writes | `02-questions.view.html` — the human's pre-read | companion section of the same contract |
| writes | `02-work-breakdown.md` — slices and the candidate cut | [`artifact-definitions/02-work-breakdown.md`](../../artifact-definitions/02-work-breakdown.md) |

---

## Workflow

1. **Rehydrate.** Feature folder or manifest missing → abort with a clear error. Read the original input and the current-state research fully.
2. **Decompose the story into atomic claims.** Every sentence that asserts a behaviour, a constraint, or a scope boundary becomes one numbered claim. This list is the working surface for the hunt, and it is recorded as the inventory's atomic-claims table; entries cite these IDs in their Evidence.
3. **Run every probe in the hunt table** over the claims and the current state. Top to bottom, skip none.
4. **Write each finding as a self-contained entry** per the contract: tier, track, category, context, evidence per the shared evidence rules (claim IDs plus evidence IDs resolving in the inventory's source map), the question itself, options with trade-offs, your own recommendation — and, where you can answer with high confidence yourself, a proposed answer for the human to merely confirm.
5. **Record coverage.** Every category ends with findings or an explicit `none found` line. A category without a line means the hunt is unfinished, not that nothing was found.
6. **Draft the work breakdown** per its contract: vertical slices with completion boundaries, the candidate package cut, conditional slices. Every decision that would change the cut becomes an inventory entry, referenced from the breakdown. A story with nothing to cut gets the single-package one-liner — never invent slices to look thorough.
7. **Write the artifacts** and mark them present in the manifest ledger.

### The hunt table

| Category | Probe |
|---|---|
| Gaps | behaviour the story implies but never specifies — for each claim: what happens before it, after it, and when it fails? |
| Ambiguities | claims two readers would implement differently — every noun with two possible referents, every "etc.", every unquantified adjective |
| Term mismatches | story terms against the glossary and the code — undefined, overloaded, or used differently than the domain model |
| Contradictions | story vs. current state vs. epic and linked documents — claims the code or another document disputes |
| Staleness signals | story text that predates newer decisions — old dates, superseded requirements, references to renamed systems |
| Edge cases | empty inputs · duplicates · concurrency · failure paths · partial state · migration of existing data · backward compatibility |
| Operational blind spots | unparseable/poison messages · retry and dead-letter policy · idempotency · ordering · authorization · observability (logs, metrics, alerts) |
| Unvalidated assumptions | load-bearing claims nothing contradicts but nobody verified — especially external contracts, schemas, message formats |
| External dependencies | counterpart systems and teams — does the other side exist, who owns it, what sequencing does it impose? |
| Missing inputs | deliverables only the human can produce — schemas, sample payloads, credentials, UX decisions, sign-offs from other teams |
| Constraints | performance, security, compliance, timing the story implies but does not state |
| Out-of-scope temptations | adjacent work the story does not ask for but an implementer would be tempted to include |

---

## Output contract

`02-questions.inventory.md` and `02-questions.view.html` written per contract, manifest ledger updated. Returns a digest: question counts by tier and track, the Critical titles, and the categories that came back clean. Detail stays in the artifacts.

---

## Constraints and guardrails

- **No solutioning.** Options and a recommendation per question — never a design. The design is step 03's outcome.
- **Ask no human questions.** This step runs unattended; everything it cannot resolve becomes an entry.
- **Self-contained entries.** Step 03 may run in a different session, a different runtime, or a different surface entirely — each entry carries everything needed to ask it well. An entry that needs this session's memory to be understood is not finished.
- **No padding.** Never invent questions to look thorough — a short inventory with a complete coverage record is a good result.
- **Scope stays inside the story text**, as in step 01.

---

## Success criteria

- [ ] Every hunt category has findings or an explicit "none found" in the coverage record
- [ ] The atomic-claims table is recorded, and every entry's Evidence names the claims it probes
- [ ] Every entry is self-contained, tiered, and tracked
- [ ] Every entry carries options and a recommendation; agent-answerable ones carry a proposed answer
- [ ] `02-questions.view.html` written and consistent with the inventory
- [ ] Nothing asked, nothing designed, nothing outside the story's scope

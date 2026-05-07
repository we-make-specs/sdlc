---
name: 01-research-current-solution
description: Pipeline step 01 (AUTO) — investigate how the functionality affected by the story works today and write a code-grounded current-state document. Use before designing a change, to establish a factual baseline.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.4.0'
  tags: sdlc, step, research, current-state
---

# Step 01 · Research Current Solution  (AUTO)

- **Type:** AUTO — fresh session, rehydrates entirely from disk, asks no questions
- **Skippable:** yes, when the current state is trivial or already documented

---

## What this skill does

Produces a factual, code-grounded baseline of how the affected functionality works today: structure, key files, data flow, extension points. It describes the existing system and nothing else.

## When to use this skill

- Before a story that touches existing behaviour is analyzed and aligned
- When the team needs a shared, verified picture of how something currently works

## When NOT to use this skill

- The change is purely additive and touches nothing existing
- The current state was documented recently and has not changed

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | located via the manifest for the current branch | yes |
| Codebase | read/search access | yes |

## Required context

- `../../context-protocol.md` — resolve this step's binding context: the manifest's `## Context` map, filtered by `applies-to: 01-research-current-solution`. Record it as `Context loaded:` near the top of the research document. Architecture and component-catalog articles reach this step that way — never by a path hardcoded here.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `00_manifest.state.md` | [`artifact-definitions/00_manifest.state.md`](../../artifact-definitions/00_manifest.state.md) |
| writes | `01_current-solution.research.md` | [`artifact-definitions/01_current-solution.research.md`](../../artifact-definitions/01_current-solution.research.md) |

---

## Workflow

1. **Locate the feature folder.** Missing folder or manifest → abort with a clear error; do not guess.
2. **Read the manifest first.** The story text is the **scope boundary** — do not research code outside it.
3. **Investigate:** search broadly first (many directories, few reads), then grep for concrete symbols, routes, and config keys, then read only the highest-signal files. Follow imports from entry points inward.
4. **Trust the code over the docs.** Use documentation only for confirmation; where the two disagree, report the code's behaviour and note the discrepancy.
5. **Stop** once you can describe what the functionality does today, which files participate, how data flows, and where a change would naturally land.
6. **Write the artifact** per its contract, then tick the manifest row.

---

## Output contract

`01_current-solution.research.md` written per contract, manifest row ticked. Returns a 3–5 line summary: what it does today, the key files, and the top open questions for the analysis. Detail stays in the document.

---

## Constraints and guardrails

- **No speculation.** Anything not verifiable in code goes under "Unresolved". This is the defining rule of the artifact.
- **No proposals.** No changes, alternatives, or improvements — that is step 03.
- **No builds or tests.** This step is investigative, not executive.
- **No partial documents.** On abort, leave nothing behind.

---

## Success criteria

- [ ] Every load-bearing claim carries a `path:line` citation
- [ ] The unresolved section is genuinely populated where the code was ambiguous
- [ ] Scope stayed inside the story text
- [ ] Nothing proposed, only described

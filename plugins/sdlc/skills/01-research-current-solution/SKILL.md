---
name: 01-research-current-solution
description: Pipeline step 01 (AUTO) — investigate how the functionality affected by the story works today and write a code-grounded current-state document. Use before designing a change, to establish a factual baseline.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.5.0'
  tags: sdlc, step, research, current-state
---

# Step 01 · Research Current Solution  (AUTO)

- **Type:** AUTO — fresh session, rehydrates entirely from disk, asks no questions
- **Skippable:** yes, when the current state is trivial or already documented

---

## What this skill does

Produces a factual, code-grounded baseline of how the affected functionality works today: concepts, structure, flows, data across the layers, test coverage. It describes the existing system and nothing else. The document reads clean: evidence IDs in the body, exact `path:line` locations only in the source map at the end.

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

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure: read each declared registry's `index.md` and navigate its index tables to the architecture and component-catalog articles this step touches. Record what you read as a `Context loaded:` line near the top of the research document; state `none applicable` when nothing is declared.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `00-manifest.state.md` | [`artifact-definitions/00-manifest.state.md`](../../artifact-definitions/00-manifest.state.md) |
| writes | `01-current-solution.research.md` | [`artifact-definitions/01-current-solution.research.md`](../../artifact-definitions/01-current-solution.research.md) |

This artifact opens the research series. Any later step that has to investigate something writes a further note per the [research-note contract](../../artifact-definitions/research-note.research.md), prefixed with its own step number; business and scope questions that code cannot answer become business-evidence notes under the same contract.

---

## Workflow

1. **Locate the feature folder.** Missing folder or manifest → abort with a clear error; do not guess.
2. **Read the manifest first.** The story text is the **scope boundary** — do not research code outside it.
3. **Investigate:** search broadly first (many directories, few reads), then grep for concrete symbols, routes, and config keys, then read only the highest-signal files. Follow imports from entry points inward.
4. **Trust the code over the docs.** Use documentation only for confirmation; where the two disagree, report the code's behaviour and note the discrepancy.
5. **Stop** once you can describe what the functionality does today, which files participate, how data flows, and where a change would naturally land.
6. **Write the artifact** per its contract: conceptual model first, functional groups along the decomposition axis that fits the story, evidence IDs in the body, exact locations only in the source map. Then mark the artifact present in the manifest ledger.

---

## Output contract

`01-current-solution.research.md` written per contract, manifest ledger updated. Returns a 3–5 line summary: what it does today, the key files, and the top open questions for the analysis. Detail stays in the document.

---

## Constraints and guardrails

- **No speculation.** Anything not verifiable in code goes under "Unresolved". This is the defining rule of the artifact.
- **No proposals.** No changes, alternatives, or improvements — that is step 03.
- **No builds or tests.** This step is investigative, not executive.
- **No companion files.** The research document is the only output of this step: no HTML preview, no overview page, no details appendix.
- **No partial documents.** On abort, leave nothing behind.

---

## Success criteria

- [ ] Every factual claim carries an evidence ID that resolves exactly once in the source map to an exact `path:line` location
- [ ] Full paths appear only in the source map; the body stays readable
- [ ] The unresolved section is genuinely populated where the code was ambiguous
- [ ] Scope stayed inside the story text
- [ ] Nothing proposed, only described

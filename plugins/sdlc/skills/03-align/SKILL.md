---
name: 03-align
description: Pipeline step 03 (COLLAB) — work through the question inventory with the human, one well-presented question at a time, keep hunting as answers land, then write the alignment record, the target design and the test scenarios. Use when a story has been analyzed and needs human decisions.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.4.0'
  tags: sdlc, step, alignment, discussion, collaborative
---

# Step 03 · Align  (COLLAB)

- **Type:** COLLAB — human and agent live in dialogue; this is why it is not autonomous
- **Skippable:** no

---

## What this skill does

Conducts the bilateral alignment conversation from the question inventory step 02 prepared, records every answer where it was asked, and then writes the three artifacts everything downstream depends on: what was **agreed**, how the solution will **look**, and what will be **tested**.

The inventory is the agenda, not a script: it seeds the conversation, and the conversation extends it.

## When to use this skill

- The question inventory exists and the human is available to decide
- A story needs functional and technical decisions before planning

## When NOT to use this skill

- `02_questions.log.md` is missing — run step 02 first; conducting without the inventory reverts to improvised questioning

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | located via the manifest for the current branch | yes |
| Human | this step takes turns with a person | yes |

## Required context

- `../../context-protocol.md` — resolve this step's binding context: the manifest's `## Context` map, filtered by `applies-to: 03-align`. Record it as `Context loaded:` near the top of the alignment record. Domain language and component knowledge reach this step that way — never by a path hardcoded here.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `00_manifest.state.md` | [`artifact-definitions/00_manifest.state.md`](../../artifact-definitions/00_manifest.state.md) |
| reads | `01_current-solution.research.md` | [`artifact-definitions/01_current-solution.research.md`](../../artifact-definitions/01_current-solution.research.md) |
| updates | `02_questions.log.md` — answers filled, live findings appended | [`artifact-definitions/02_questions.log.md`](../../artifact-definitions/02_questions.log.md) |
| updates | `02_questions.html` — regenerated as answers land | companion section of the same contract |
| writes | `03_alignment.log.md` | [`artifact-definitions/03_alignment.log.md`](../../artifact-definitions/03_alignment.log.md) |
| writes | `03_target-solution.spec.md` | [`artifact-definitions/03_target-solution.spec.md`](../../artifact-definitions/03_target-solution.spec.md) |
| writes | `03_test-scenarios.spec.md` | [`artifact-definitions/03_test-scenarios.spec.md`](../../artifact-definitions/03_test-scenarios.spec.md) |
| writes | `03_target-overview.html` — the gate's pre-read | companion section of [`artifact-definitions/03_target-solution.spec.md`](../../artifact-definitions/03_target-solution.spec.md) |

---

## Workflow

1. **Rehydrate.** Inventory missing → abort and point at step 02. Read manifest, current state, and every inventory entry.
2. **Open with the digest:** question counts by tier and track, and the pointer to `02_questions.html` as the pre-read. Offer the async option explicitly — the human may answer any entry directly in the file instead of live.
3. **Work the agenda, Critical first, one question per round** (two only when tightly coupled). Render every question with the template below — as a normal chat message, whatever the runtime. Entries with a proposed answer are presented for confirmation, not re-derived.
4. **Record before moving on.** Each answer goes into the inventory immediately — answer, rationale, who/when — and directional answers are mirrored back and confirmed before the next round.
5. **Keep hunting.** Answers create new gaps: when one appears, append it to the inventory in the same format and tier, and say so. The inventory seeds the conversation; it does not bound it.
6. **Iterate until the human signals alignment.** When unsure, ask with concrete options: "A: I write the artifacts now. B: We clarify <point> first."
7. **Draft the test scenarios and ask the scenario question.** Functional scenarios + rough test data + the exceptional cases — then ask, verbatim: **"Which of these are wrong, and what is missing?"** A nod is not an answer; iterate until the human names changes or explicitly confirms they checked.
8. **Write the three artifacts** per their contracts, consistent with each other, the manifest, and the answered inventory — then regenerate `02_questions.html` one last time and write `03_target-overview.html`, the gate's pre-read. This write-up may be delegated to a fresh strong-tier subagent: the answered inventory, manifest and current state carry everything it needs. Review the drafts with the human before finishing either way.

Scale depth to complexity: a small tweak is a short agenda, a cross-cutting change is a long one.

### The question template

Every question appears in chat exactly in this shape — the runtime's interactive ask-tools may be used *in addition*, but never replace or compress it:

```markdown
### Question <n> of <total> — [<tier>] [<track>] <short name>

**Context:** <1–2 sentences, with the story quote or path:line from the entry>

**Question:** <the one sentence, bold>

**Options:**
- **A (recommended):** <option> — <why / trade-off>
- **B:** <option> — <trade-off>

Answer A/B or in your own words.
```

The counter gives the human progress; the recommendation gives them a default; the context spares them reconstructing why this matters. All three come from the inventory entry — presentation quality must not depend on live improvisation.

---

## Output contract

`03_alignment.log.md`, `03_target-solution.spec.md` and `03_test-scenarios.spec.md` written per contract, mutually consistent; `02_questions.log.md` fully answered or explicitly deferred, `02_questions.html` regenerated; `03_target-overview.html` written — the gate does not open without its pre-read. Manifest rows ticked. No commits, no code, nothing outside the feature folder.

---

## Constraints and guardrails

- **No silent assumptions** on anything affecting correctness, scope, safety, or intent — ask.
- **Do not dump the whole inventory into chat.** The pre-read is the overview; the conversation stays one question per round.
- **Record answers where they were asked.** An answer that lives only in chat history is lost to every later session.
- **Do not start planning or implementing** — those are steps 05 and 06.
- **Do not approve.** Approval is gate 04, and it is the human's.

---

## Success criteria

- [ ] Every Critical and Important entry answered, or explicitly deferred with a rationale
- [ ] Every answer recorded in the inventory with rationale and who/when; live findings appended, not lost
- [ ] Every question rendered with the template — none improvised
- [ ] Every acceptance criterion is concrete and testable
- [ ] Every key decision carries a rationale
- [ ] Out of scope is explicitly populated
- [ ] The scenario question was asked and answered — changes named, or nothing-missing confirmed
- [ ] The target solution is complete enough for a separate session to implement from
- [ ] `03_target-overview.html` written — design and scenarios on one page, the scenario question included
- [ ] The human explicitly signalled alignment

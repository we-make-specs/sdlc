---
name: 03-align
description: Pipeline step 03 (COLLAB) — work through the question inventory with the human, one well-presented question at a time, keep hunting as answers land, then write the agreement, the target design and the test scenarios. Use when a story has been analyzed and needs human decisions.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.0'
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

- `02-questions.inventory.md` is missing — run step 02 first; conducting without the inventory reverts to improvised questioning

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | located via the manifest for the current branch | yes |
| Human | this step takes turns with a person | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure: read each declared registry's `index.md` and navigate its index tables to the domain-language, component, architecture, and guideline articles this step touches. Record a `Context loaded:` line near the top of the agreement; state `none applicable` when nothing is declared. Also record each actually applicable rule, its exact wording, applicability evidence, classification, affected decision, and affected paths in `03-decision-manifest.state.json`. Loading an article is not the same as proving its rule applies.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `00-manifest.state.md` | [`artifact-definitions/00-manifest.state.md`](../../artifact-definitions/00-manifest.state.md) |
| reads | `01-current-solution.research.md` | [`artifact-definitions/01-current-solution.research.md`](../../artifact-definitions/01-current-solution.research.md) |
| updates | `02-questions.inventory.md` — answers filled, live findings appended | [`artifact-definitions/02-questions.inventory.md`](../../artifact-definitions/02-questions.inventory.md) |
| updates | `02-questions.view.html` — regenerated as answers land | companion section of the same contract |
| updates | `02-work-breakdown.md` — the agreed slices recorded as cut decisions land | [`artifact-definitions/02-work-breakdown.md`](../../artifact-definitions/02-work-breakdown.md) |
| writes | `03-agreement.spec.md` | [`artifact-definitions/03-agreement.spec.md`](../../artifact-definitions/03-agreement.spec.md) |
| writes | `03-target-solution.spec.md` | [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| writes | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| writes | `03-decision-manifest.state.json` — source authority, risks, conflicts and decision state | [`artifact-definitions/03-decision-manifest.state.schema.json`](../../artifact-definitions/03-decision-manifest.state.schema.json) |
| writes | `03-human-decision-gate.view.md` and `.view.html` — deterministic gate projections | companion section of [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |

---

## Workflow

1. **Rehydrate.** Inventory missing → abort and point at step 02. Read manifest, current state, every inventory entry, and relevant registry articles. Before asking for approval, build the decision manifest: copy every acceptance criterion verbatim; turn each material choice into a decision with risk class, options, recommendation, counterargument, and typed sources; and build the applicable-rule table from exact article text. An article under an `_todo_` path is `MISSING`, never binding. A rule is `BINDING` only when its language and scope establish that; repository examples are informative evidence unless an authoritative source says otherwise.
2. **Open with the digest:** question counts by tier and track, and the pointer to `02-questions.view.html` as the pre-read. Offer the async option explicitly — the human may answer any entry directly in the file instead of live.
3. **Work the agenda in the selected questioning mode.** The manifest profile's `questioning` field decides how the conversation travels: `chat` follows [cli-questioning.md](cli-questioning.md) (one templated question per round), `annotation` follows [plannotator-questioning.md](plannotator-questioning.md) (the human annotates the inventory in passes). The recording rules below hold in both modes.
4. **Record before moving on.** Each answer goes into the inventory immediately — answer, rationale, who/when — and directional answers are mirrored back and confirmed before the next round. Update the corresponding decision and its provenance at the same time. A question the human cannot settle authoritatively may be answered as an explicit assumption: record it as `assumed` with a named verification owner and due point, and mirror it into the agreement's Constraints.
5. **Keep hunting.** Answers create new gaps: when one appears, append it to the inventory in the same format and tier, and say so. The inventory seeds the conversation; it does not bound it.
6. **Iterate until the human signals alignment.** When unsure, ask with concrete options: "A: I write the artifacts now. B: We clarify <point> first."
7. **Draft the test scenarios and ask the scenario question.** Functional scenarios + rough test data + the exceptional cases — then ask, verbatim: **"Which of these are wrong, and what is missing?"** A nod is not an answer; iterate until the human names changes or explicitly confirms they checked.
8. **Reconcile authority conflicts.** For each decision, compare ticket, acceptance criteria, human statements, registry rules, reference implementations, approved-design drafts and runtime evidence. Record both sides and the consequence; never silently pick one because its source sounds more formal. Security, public-contract, business-behavior, architecture, data, and operational choices are `HUMAN_REQUIRED`. Local implementation choices may be `AGENT_OWNED` or `SAMPLED` when no higher-risk behavior changes.
9. **Write the three artifacts and decision manifest** per their contracts, mutually consistent with the answered inventory. Copy a compact statement of every proposed test scenario into the manifest and keep it `PROPOSED` until the human answers the scenario challenge. Reconcile the coverage counts and validate the manifest with `validate_decision_manifest.py --phase alignment`; a failure means alignment is incomplete. Then regenerate `02-questions.view.html` and render the decision gate deterministically:

   ```bash
   python3 <plugin>/scripts/render_decision_gate.py \
     2-specification/03-decision-manifest.state.json --phase alignment \
     --markdown 2-specification/03-human-decision-gate.view.md \
     --html 2-specification/03-human-decision-gate.view.html
   ```

   This write-up may be delegated to a fresh strong-tier subagent: the answered inventory, manifest and current state carry everything it needs. The subagent writes canonical artifacts, never the generated gate views. Review the drafts with the human before finishing either way.

Scale depth to complexity: a small tweak is a short agenda, a cross-cutting change is a long one.

### The questioning modes

Two mode files next to this skill carry the procedures: [cli-questioning.md](cli-questioning.md) (the chat template and round discipline) and [plannotator-questioning.md](plannotator-questioning.md) (annotation rounds on the inventory, tool-neutral with Plannotator as the example). Both draw everything from the inventory entries — presentation quality must not depend on live improvisation — and both feed every answer back into the inventory before the artifacts are written.

---

## Output contract

`03-agreement.spec.md`, `03-target-solution.spec.md`, `03-test-scenarios.spec.md`, and a validation-clean `03-decision-manifest.state.json` written per contract, mutually consistent; `02-questions.inventory.md` fully answered or explicitly deferred, `02-questions.view.html` regenerated; deterministic `03-human-decision-gate.view.md` and `.view.html` written. Manifest ledger updated. No commits, no code, nothing outside the feature folder.

---

## Constraints and guardrails

- **No silent assumptions** on anything affecting correctness, scope, safety, or intent — ask.
- **Do not dump the whole inventory into chat.** The pre-read is the overview; the conversation stays one question per round.
- **Record answers where they were asked.** An answer that lives only in chat history is lost to every later session.
- **Do not start planning or implementing** — those are steps 05 and 06.
- **Do not approve.** Approval is gate 04, and it is the human's.
- **Do not invent source precedence.** Record conflicts and trade-offs; high-risk ambiguity stays human-required.
- **Do not treat `_todo_` guidance as policy.** It is explicit missing context.

---

## Success criteria

- [ ] Every Critical and Important entry answered, or explicitly deferred with a rationale
- [ ] Every answer recorded in the inventory with rationale and who/when; live findings appended, not lost
- [ ] Every assumed answer carries a verification owner and due point and reappears under Constraints
- [ ] Every question asked per the selected mode's procedure — chat questions templated, annotation rounds fully ingested; none improvised
- [ ] Every acceptance criterion is concrete and testable
- [ ] Every key decision carries a rationale
- [ ] Every AC maps to its relevant decisions, without paraphrase
- [ ] Every applicable registry rule has exact text, applicability evidence, classification, and affected paths
- [ ] Every source conflict is resolved explicitly or remains a visible human-required decision
- [ ] `03-decision-manifest.state.json` passes `--phase alignment`
- [ ] Out of scope is explicitly populated
- [ ] The scenario question was asked and answered — changes named, or nothing-missing confirmed
- [ ] The target solution is complete enough for a separate session to implement from
- [ ] Deterministic human-decision Markdown and HTML views rendered from the validated manifest
- [ ] The human explicitly signalled alignment

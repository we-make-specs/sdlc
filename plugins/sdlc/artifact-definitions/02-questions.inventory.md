---
artifact: 02-questions.inventory.md
produced_by: 02-analyze
consumed_by: [03-align, 04-approve-target-solution, 05-plan]
required: true
---

# Contract — `02-questions.inventory.md` (question inventory)

## Purpose

Every point the story leaves open, written as questions a human can decide — found by step 02, asked and answered in step 03, checked at gate 04. The functional sibling of [`05-technical-questions.inventory.md`](05-technical-questions.inventory.md): same tiers, same fill-in lifecycle, one stage earlier.

The file does two jobs at once: it is the **agenda** of the alignment conversation, and the **trace** of how each point was settled. The alignment record distills what was agreed; this file keeps the full path — question, options, answer, rationale.

## The rule that defines this artifact

**Every entry is self-contained.** Step 03 may run in another session, another runtime, or another surface entirely (CLI, chat window, workshop page). Each entry therefore carries everything needed to ask it well — context, evidence, options, recommendation — without access to the analysis session's memory. An entry that needs the analysis session to be understood is not finished.

## Atomic claims

The inventory opens with the story's decomposition: every assertion the story makes about behaviour, a constraint, or a scope boundary becomes one numbered claim (`C1`, `C2`, …) in a table of claim, assertion, and evidence. The hunt runs over these claims, and each entry names the claim IDs it probes in its Evidence field.

Recording the claims makes coverage checkable in both directions: a claim no entry references was either genuinely unambiguous or missed, and the written table is what lets a reviewer tell which.

## Lifecycle

| Phase | Who | What happens to this file |
|---|---|---|
| step 02 | analyze | created: entries plus coverage record, answers open |
| step 03 | align | answers filled in with rationale and who/when; questions that surface live are **appended** in the same format; question text is never rewritten |
| gate 04 | human | not passed while a Critical entry is unanswered |

## Priority tiers

| Tier | Meaning | Deadline |
|---|---|---|
| **Critical** | the design cannot be written without the answer | before the target solution is drafted |
| **Important** | the answer changes the design | before gate 04 approves |
| **Clarification** | nice to know | may resolve during planning or implementation |

## Tracks

| Track | Covers |
|---|---|
| `functional` | what the system should do — behaviour, scope, domain language, business rules |
| `technical` | how it will be built — schemas, contracts, operations, dependencies |

A question that is genuinely both is `functional` — what-questions outrank how-questions.

## Entry anatomy

| Field | Required | Content |
|---|---|---|
| title line | yes | `Q<n> — [tier] [track] <short name>` |
| Category | yes | the hunt category that found it (see step 02's hunt table) |
| Context | yes | 1–2 sentences of background a newcomer needs |
| Evidence | yes | the claim IDs this entry probes, plus story quote and/or `path:line` — what makes this a real question |
| Question | yes | one sentence, answerable |
| Options | yes | each with its trade-off |
| Recommendation | yes | the agent's own pick, with the reason — never a menu without a pick |
| Needed from | missing-inputs entries | who or what can deliver the input — person, team, system; becomes the routing target if a later step blocks on it |
| Proposed answer | when agent-answerable | filled by step 02, for the human to merely confirm |
| Answer | after step 03 | what was decided, with `Rationale:` and answered-by/on |

## Coverage record

One line per hunt category: `<n> findings (Q…)` or `none found`. This is what makes the hunt auditable — "none found" is a result, a missing line is an unfinished analysis.

## Quality criteria

- [ ] Every entry passes the stranger test: someone who never saw the analysis session could ask it well from the file alone.
- [ ] The atomic-claims table is present, and every entry's Evidence names the claims it probes.
- [ ] A **missing-inputs** entry is answered only when the input itself is available and verified — the file in the repo, the schema resolvable, the access confirmed. A policy or a promise ("use the official one") keeps the entry open; implementation cannot execute a promise. Every missing-inputs entry carries `Needed from:`.
- [ ] Every entry is tiered and tracked; both-track collisions resolve to `functional`.
- [ ] Every option list ends with a recommendation.
- [ ] The coverage record names every hunt category.
- [ ] After step 03: no Critical or Important entry unanswered; deferrals carry an explicit rationale and reappear under Open Questions in the alignment record.
- [ ] Answers that create durable commitments are also recorded in `decisions.log.md` — and, if they hold beyond this feature, as an ADR in the context registry.

## Companion — `02-questions.view.html` (required)

A single self-contained page: inline CSS, diagrams as inline SVG, no external requests, renders offline from `file://`. It shows the inventory as a tiered, tracked agenda — counts up front, one card per question, coverage record at the end. Where a question sits in a flow, a small SVG sketch with the affected node marked beats a paragraph.

Step 02 writes it; step 03 regenerates it after answers land, so it always shows the current state. Its purpose matches the target-overview page one gate later: the human opens one page and sees the whole conversation ahead instead of scrolling the raw inventory.

## Skeleton

```markdown
# Question Inventory: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>
- **Manifest:** [00-manifest.state.md](00-manifest.state.md) · **Current state:** [01-current-solution.research.md](01-current-solution.research.md)
- **Open:** <n> Critical · <n> Important · <n> Clarification

## Atomic claims

| Claim | Story assertion | Evidence |
|---|---|---|
| C1 | <one assertion the story makes> | "<story quote>" · `path/to/file:42` |
| C2 | <the next assertion> | "<story quote>" |

## Critical

### Q1 — [Critical] [technical] <short name>

- **Category:** <hunt category>
- **Context:** <1–2 sentences a newcomer needs>
- **Evidence:** C1 · "<story quote>" · `path/to/file:42`
- **Question:** <one sentence>
- **Options:**
  - **A:** <option> — <trade-off>
  - **B:** <option> — <trade-off>
- **Recommendation:** A — <reason>
- **Answer:** <open>
  - **Rationale:** <…> · **Answered by / on:** <…>

## Important

### Q2 — [Important] [functional] <short name>

<same fields>

## Clarification

### Q3 — [Clarification] [functional] <short name>

<same fields; a Proposed answer here often lets the human just confirm>

## Coverage record

| Category | Result |
|---|---|
| Gaps | 2 findings (Q1, Q4) |
| Ambiguities | none found |
| <every category from the hunt table> | <…> |

*Step 03 fills in answers and appends new questions in the matching tier section — it never rewrites existing question text.*
```

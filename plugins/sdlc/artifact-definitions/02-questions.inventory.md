---
artifact: 02-questions.inventory.md
produced_by: 02-analyze
consumed_by: [03-align, 04-approve-target-solution, 05-plan]
required: true
---

# Contract — `02-questions.inventory.md` (question inventory)

## Purpose

Every point the story leaves open, written as questions a human can decide — found by step 02, asked and answered in step 03, checked at gate 04. The functional sibling of [`05-technical-questions.inventory.md`](05-technical-questions.inventory.md): same tiers, same fill-in lifecycle, one stage earlier.

The file does two jobs at once: it is the **agenda** of the alignment conversation, and the **trace** of how each point was settled. The agreement distills what was agreed; this file keeps the full path — question, options, answer, rationale.

## The rule that defines this artifact

**Every entry is self-contained.** Step 03 may run in another session, another runtime, or another surface entirely (CLI, chat window, workshop page). Each entry therefore carries everything needed to ask it well — context, evidence, options, recommendation — without access to the analysis session's memory. An entry that needs the analysis session to be understood is not finished.

## Atomic claims

The inventory opens with the story's decomposition: every assertion the story makes about behaviour, a constraint, or a scope boundary becomes one numbered claim (`C1`, `C2`, …) in a table of claim, assertion, and evidence. The hunt runs over these claims, and each entry names the claim IDs it probes in its Evidence field.

Recording the claims makes coverage checkable in both directions: a claim no entry references was either genuinely unambiguous or missed, and the written table is what lets a reviewer tell which.

Evidence follows the shared evidence rules (see the catalog README): short IDs in the body, source roots, one source map at the end. Other artifacts of the feature and registry articles are citable sources; this is what keeps a cross-repository inventory readable without long paths in every entry.

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
| Question | yes | one answerable sentence, directly below the title and outside the supporting bullet list |
| Category | yes | the hunt category that found it (see step 02's hunt table) |
| Context | yes | 1–2 sentences of background a newcomer needs |
| Evidence | yes | the claim IDs this entry probes, plus story quote and/or evidence IDs per the shared evidence rules — what makes this a real question |
| Options | yes | each result and its benefits and costs, using a compact comparison where useful |
| Recommendation | yes | the agent's own pick, with the reason — never a menu without a pick |
| Needed from | missing-inputs entries | who or what can deliver the input — person, team, system; becomes the routing target if a later step blocks on it |
| Proposed answer | when agent-answerable | filled by step 02, for the human to merely confirm |
| Answer | after step 03 | what was decided, with `Rationale:` and answered-by/on; or `assumed`, an explicit assumption with a named verification owner and a due point (after implementation, before deployment) |

## Progress and presentation

Derive each question's display status from its answer and confirmation, never a separate status
field. An absent, empty, `TODO`, `OPEN` or `UNANSWERED` answer is `Open`; a proposed answer or
recommendation alone does not close it. A required input marked `Input verification: pending`,
`required` or `unverified` also stays `Open`. An answer beginning `ASSUMED`, or a
`Confirmation` marked `pending`, `required` or `unverified`, is `Needs confirmation`.
A substantive recorded answer is `Answered`; this does not mean the design is approved.
Resolve an assumption with `Confirmation: verified by <who> on <YYYY-MM-DD>`; until then,
retain its owner and due point. For required input, record
`Input verification: verified by <who> on <YYYY-MM-DD>` only when the input itself is available
and verified. A `Missing inputs` entry stays open until that verification is recorded. If the
chosen option removes the need for that input, record `Input verification: not required by
<who> on <YYYY-MM-DD>; <reason>`. `Needed from` alone is routing information, not proof that
the chosen option needs the input. Append a later pending correction as a new `Q<n>` entry
linked to the historical answer; do not overwrite it. Counts and navigation use these same states, including appended
questions. These labels do not replace the gate rules.

Put the question directly below the entry title, above Category, Context and Evidence.
Keep it outside the supporting bullet list. In the HTML view, show it as a prominent callout
with larger, bold text. Preserve the exact question wording when moving it for display.
Keep questions, context, options, recommendation and answer distinct. For a meaningful choice,
use one row per option with a single Trade-offs column containing separate Benefit and Cost
bullets. Do not invent a benefit or cost: use `none identified` where appropriate. Simple entries
may remain compact. Use restrained status icons only with text labels.

## Coverage record

One line per hunt category: `<n> findings (Q…)` or `none found`. This is what makes the hunt auditable — "none found" is a result, a missing line is an unfinished analysis.

## Quality criteria

- [ ] Every entry passes the stranger test: someone who never saw the analysis session could ask it well from the file alone.
- [ ] The question leads each entry, outside its supporting bullet list, and stands out in the HTML view.
- [ ] The atomic-claims table is present, and every entry's Evidence names the claims it probes.
- [ ] Evidence resolves per the shared evidence rules: every body ID exactly once in the source map, no absolute paths.
- [ ] A **missing-inputs** entry is answered only when the input itself is available and verified — the file in the repo, the schema resolvable, the access confirmed. A policy or a promise ("use the official one") keeps the entry open; implementation cannot execute a promise. Every missing-inputs entry carries `Needed from:`.
- [ ] Every entry is tiered and tracked; both-track collisions resolve to `functional`.
- [ ] Every option list ends with a recommendation.
- [ ] The coverage record names every hunt category.
- [ ] After step 03: no Critical or Important entry unanswered; deferrals carry an explicit rationale and reappear under Open Questions in the agreement.
- [ ] An `assumed` answer names its verification owner and due point, reappears under Constraints in the agreement, and becomes an advisor check or release readiness gate in the plan. At delivery close every assumption is either verified (who, when) or explicitly accepted as a standing risk; none silently expires.
- [ ] Answers that create durable commitments are also recorded in `06-decisions.log.md` — and, if they hold beyond this feature, as an ADR in the context registry.

## Companion — `02-questions.view.html` (required)

A deterministic, self-contained offline rendering of the inventory, generated by
`scripts/render_questions.py`. Show status counts and navigation derived from the same entries,
then the question content expanded for reading and annotation. Use restrained icons with text
labels. Preserve the source's question, options, answer, evidence and coverage record. The page
is a static view, not an answer editor or another source of truth.

Step 02 generates it and step 03 regenerates it after answers or questions change. Do not
hand-edit the view. Generate it with:

```bash
python3 <plugin>/scripts/render_questions.py \
  2-specification/02-questions.inventory.md \
  --html 2-specification/02-questions.view.html
```

## Skeleton

```markdown
# Question Inventory: <title>

- **Ticket:** <ID> · **Created:** <YYYY-MM-DD>
- **Manifest:** [00-manifest.state.md](../00-manifest.state.md) · **Current state:** [01-current-solution.research.md](../1-research/01-current-solution.research.md)
- **Open:** <n> Critical · <n> Important · <n> Clarification

## Atomic claims

| Claim | Story assertion | Evidence |
|---|---|---|
| C1 | <one assertion the story makes> | [S1] |
| C2 | <the next assertion> | [S1] |

## Critical

### Q1 — [Critical] [technical] <short name>

**Question:** <one sentence>

- **Category:** <hunt category>
- **Context:** <1–2 sentences a newcomer needs>
- **Evidence:** C1 · "<story quote>" · [B1]

**Options:**

| Option | Result | Trade-offs |
|---|---|---|
| A | <result> | **Benefit**<br>- <benefit><br>**Cost**<br>- <cost> |
| B | <result> | **Benefit**<br>- <benefit><br>**Cost**<br>- <cost> |

- **Recommendation:** A - <reason>
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

## Source roots

| Prefix | Root |
|---|---|
| `SHOP` | `<repository root>` |

## Source map

| ID | Exact source location | Supports |
|---|---|---|
| S1 | `SHOP/docs/story.md:12-18` | the story assertions the claims quote |
| B1 | `SHOP/src/checkout/PriceService.java:42-60` | the current behaviour Q1 probes |

*Step 03 fills in answers and appends new questions in the matching tier section — it never rewrites existing question text.*
```

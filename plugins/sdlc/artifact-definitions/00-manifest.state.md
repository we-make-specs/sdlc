---
artifact: 00-manifest.state.md
produced_by: 00-ensure-workspace
consumed_by: [all]
required: true
---

# Contract — `00-manifest.state.md` (story identity)

## Purpose

The story's identity and its completion ledger. Every later step reads it first to locate itself, and ticks **only its own** checklist row.

It also preserves the **original input verbatim** — the source of truth against which the finished work is judged. Once written, that text is never edited.

## Required sections

| Section | Required | Content |
|---|---|---|
| frontmatter | yes | ticket, title, cycle (`YYYY-MM`), branch, **folder** (repo-relative feature-folder path — authoritative for every step), created, url, **status** (`in-progress` \| `blocked` \| `done`) |
| `## Original input` | yes | ticket text or brain dump, **unmodified** |
| `## Artifact checklist` | yes | one row per artifact; only `00-manifest.state.md` ticked at creation |
| `## Blockers` | when blocked | append-only; one entry per blocker — see below |
| `## People` | no | who clarifies, implements, reviews |
| `## Affected components` | no | services/modules, checked against the component catalog |

## Blockers — failure as a file, not a message

`status:` is the one-grep run signal: any orchestrator — the run skill, a shell script, a CI pipeline — reads the same field to decide whether the run may advance. A step that cannot proceed **appends a blocker entry and sets `status: blocked` before returning**; a blocker that exists only in a step's report does not exist. Whoever resolves it marks the entry resolved and sets `status: in-progress`; step 09 sets `done` after the merge.

Entry fields: **Missing** (what, concretely) · **Needed from** (person / team / system — carried over from the inventory entry's `Needed from:` where one exists) · **Blocking** (step) · **Since** (date) · **Escalation** (one ready-to-forward sentence) · **Resolved** (date + how, once it is).

## Quality criteria

- [ ] Original input is byte-for-byte what came in. No cleanup, no summarising, no "fixing" typos — later verification depends on it.
- [ ] Branch name and folder path match the frontmatter.
- [ ] `folder:` names the directory this file actually lives in — repo-relative, under `docs/sdlc/features/`, **inside the working repository**. Every step and the orchestrator treat it as authoritative; nothing re-derives the location, and nothing is ever written next to the input source.
- [ ] `status: blocked` if and only if at least one Blockers entry is unresolved.
- [ ] Only `00-manifest.state.md` is ticked at creation.
- [ ] Free-text stories (no ticket) use `ticket: none` and derive the title from the first meaningful line.

## Skeleton

```markdown
---
ticket: <ID | none>
title: <title>
cycle: <YYYY-MM>
branch: <branch-name>
folder: docs/sdlc/features/<YYYY-MM>/<story-slug>
created: <YYYY-MM-DD>
url: <ticket link, empty for free text>
status: in-progress
---

# Story: <title>

## Original input

<ticket text or brain dump, unmodified>

## Artifact checklist

- [x] `00-manifest.state.md` — this file
- [ ] `01-current-solution.research.md` — current state (step 01)
- [ ] `02-questions.inventory.md` — question inventory (step 02, answered in step 03)
- [ ] `02-questions.view.html` — question pre-read (step 02, regenerated in step 03)
- [ ] `03-alignment.spec.md` — alignment record (step 03)
- [ ] `03-target-solution.spec.md` — target design (step 03)
- [ ] `03-test-scenarios.spec.md` — test scenarios (step 03)
- [ ] `03-target-overview.view.html` — gate pre-read (step 03)
- [ ] `05-technical-analysis.research.md` — technical analysis (step 05, optional)
- [ ] `05-technical-questions.inventory.md` — technical questions (step 05, optional)
- [ ] `05-implementation.plan.md` — executable plan incl. progress log (step 05)
- [ ] `decisions.log.md` — decision log (cross-cutting)

## Blockers

*(append-only; present only when something blocked)*

- **B1 — <what is missing, concretely>**
  - **Needed from:** <person / team / system> · **Blocking:** step <NN> · **Since:** <YYYY-MM-DD>
  - **Escalation:** <one ready-to-forward sentence: to whom, what is needed, why, what it blocks>
  - **Resolved:** <YYYY-MM-DD — how · or open>

## People

| Role | Who |
|---|---|
| Functional clarification | <…> |
| Implementation | <…> |
| Review | <…> |

## Affected components

<services/modules — check against the component catalog in the context registry>
```

---
artifact: 00-manifest.state.md
produced_by: 00-create-workspace
consumed_by: [all]
required: true
---

# Contract — `00-manifest.state.md` (story identity)

## Purpose

The delivery's identity and its durable coordination record: which repositories participate, which artifacts exist and in what state, and where each work package stands. Every later step reads it first to locate itself, and updates **only its own** ledger rows.

A single-repository, single-PR story is not a special case: it has one component row and one work-package row, and everything else is identical.

It also preserves the **original input verbatim** — the source of truth against which the finished work is judged. Once written, that text is never edited.

## Required sections

| Section | Required | Content |
|---|---|---|
| frontmatter | yes | ticket, title, cycle (`YYYY-MM`), branch, **folder** (repo-relative feature-folder path — authoritative for every step), created, url, **status** (`in-progress` \| `blocked` \| `done`), **profile** (see below) |
| `## Original input` | yes | ticket text or brain dump, **unmodified** |
| `## Component repositories` | yes | one row per participating repository: component, relative location, delivery role; a single-repo story has exactly one row with location `.` |
| `## Artifact ledger` | yes | one row per artifact: status, artifact, purpose; only `00-manifest.state.md` is `present` at creation |
| `## Work-package ledger` | yes | one row per work package: ID, pull request, target component, status, depends on, blocked by; a single-PR story has exactly one row |
| `## Blockers` | when blocked | append-only; one entry per blocker — see below |
| `## People` | no | who clarifies, implements, reviews |

## The delivery profile

Three choices shape how later steps talk and where two texts land. They are collected once, at kickoff, by the orchestrator (live with the human; step 00 itself asks nothing) and recorded in the frontmatter. The pipeline flow is identical in every profile; nothing is re-asked later.

| Field | Values | Consumed by |
|---|---|---|
| `pr_audience` | `team` (humans review the PRs; the body is a short reviewer handoff) \| `solo` (the PR is the record; process-rich body) | steps 06, 08 |
| `review_placement` | `workspace` (agent review findings stay local) \| `pr` (findings posted on the PR) | step 07 |
| `questioning` | `chat` (one question per round) \| `annotation` (annotation rounds on the inventory) | step 03 |

Defaults, used when the kickoff was headless or the human gave no preference: `solo` · `pr` · `chat` — exactly the previous behavior.

## Blockers — failure as a file, not a message

`status:` is the one-grep run signal: any orchestrator — the run skill, a shell script, a CI pipeline — reads the same field to decide whether the run may advance. A step that cannot proceed **appends a blocker entry and sets `status: blocked` before returning**; a blocker that exists only in a step's report does not exist. Whoever resolves it marks the entry resolved and sets `status: in-progress`; step 09 sets `done` after the merge.

Entry fields: **Missing** (what, concretely) · **Needed from** (person / team / system — carried over from the inventory entry's `Needed from:` where one exists) · **Blocking** (step) · **Since** (date) · **Escalation** (one ready-to-forward sentence) · **Resolved** (date + how, once it is).

## Quality criteria

- [ ] Original input is byte-for-byte what came in. No cleanup, no summarising, no "fixing" typos — later verification depends on it.
- [ ] Branch name and folder path match the frontmatter. In a one-package delivery `branch:` names that package's branch; with several packages it stays empty and the work-package ledger owns the branches.
- [ ] `folder:` names the directory this file actually lives in, per the placement rule in the catalog README: the in-repo feature folder for a single-repository story, the sibling workspace folder for a cross-repository delivery. Every step and the orchestrator treat it as authoritative; nothing re-derives the location, and nothing is ever written next to the input source.
- [ ] Every component repository is declared by a portable relative path; absolute paths are prohibited.
- [ ] The work-package ledger's state fields (PR link, merge commit, blocker, dependency) are the single source for package state; other artifacts reference the row, never duplicate it.
- [ ] `status: blocked` if and only if at least one Blockers entry is unresolved.
- [ ] The profile is recorded at creation and never re-asked; absent answers use the defaults.
- [ ] At creation only `00-manifest.state.md` is `present` in the artifact ledger.
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
profile:
  pr_audience: solo
  review_placement: pr
  questioning: chat
---

# Story: <title>

## Original input

<ticket text or brain dump, unmodified>

## Component repositories

| Component | Relative location | Delivery role |
|---|---|---|
| <the repository> | `.` | <its role — a single-repo story has exactly this one row> |

## Artifact ledger

| Status | Artifact | Purpose |
|---|---|---|
| present | `00-manifest.state.md` | this file |
| open | `01-current-solution.research.md` | current state (step 01) |
| open | `02-questions.inventory.md` | question inventory (step 02, answered in step 03) |
| open | `02-questions.view.html` | question pre-read (step 02, regenerated in step 03) |
| open | `03-agreement.spec.md` | agreement (step 03) |
| open | `03-target-solution.spec.md` | target design (step 03) |
| open | `03-test-scenarios.spec.md` | test scenarios (step 03) |
| open | `03-target-overview.view.html` | gate pre-read (step 03) |
| open | `05-technical-analysis.research.md` | technical analysis (step 05, optional) |
| open | `05-technical-questions.inventory.md` | technical questions (step 05, optional) |
| open | `05-implementation.plan.md` | executable plan incl. progress log (step 05) |
| open | `decisions.log.md` | decision log (cross-cutting) |

## Work-package ledger

| ID | Pull request | Target component | Status | Depends on | Blocked by |
|---|---|---|---|---|---|
| WP-01 | <link once open> | <component> | planned | none | none |

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
```

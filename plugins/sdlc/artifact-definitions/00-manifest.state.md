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
| frontmatter | yes | ticket, title, cycle (`YYYY-MM`), branch, **workspace_root** (relative to this manifest), **folder** (relative to that root), created, url, **status** (`in-progress` \| `blocked` \| `done`), **profile** (see below) |
| context trace | new runs | `Context loaded:` naming setup/branch rules read, or the explicit no-registry declaration |
| `## Start here` | yes | three to five links: the current plan, the latest research, the pre-read page — navigation only, nothing that can drift |
| `## Original input` | yes | ticket text or brain dump, **unmodified** |
| `## Input provenance` | new runs | source paths or ticket URL, lookup/verification status and date, failure reason and unresolved missing content |
| `## Component repositories` | yes | one row per component: manifest-relative location, verified remote, selected base ref and commit, delivery role |
| `## Artifact ledger` | yes | one row per artifact: status, artifact, purpose; only `00-manifest.state.md` is `present` at creation |
| `## Work-package ledger` | yes | one row per package: ID, PR, component, status, dependencies, blockers and human review; a single-PR story has one row |
| `## Blockers` | when blocked | append-only; one entry per blocker — see below |
| `## People` | no | who clarifies, implements, reviews |

Path meanings and legacy handling are defined once in the [catalog](README.md#workspace-location-and-paths).
New fields are required for new setup; existing manifests retain their path meanings and
are not rewritten merely to resume. A blank `branch` is valid before package branches
are selected in a ticket-root delivery.

Input provenance distinguishes a successful live lookup from supplied material. A failed
lookup followed by a readable supplied snapshot records `not verified against live ticket`,
without changing the ticket to `none`. Screenshot text is labeled as a transcription and
links the unchanged image; clipped text is an unresolved gap, never reconstructed. Later
verification adds a dated provenance note and routes conflicts through alignment; it never
silently replaces Original input. A usable snapshot permits research; missing requirements
or source conflicts must be settled before design approval.

The package row's `Human review` starts as `pending`. Step 08 records the outcome and,
for approval, the human, date, PR URL and reviewed head commit there. Add this column to a
legacy ledger when recording its next review, not merely on resume. A changed head makes
the previous approval stale; it cannot authorize the new code.

## The delivery profile

Three choices shape how later steps talk and where two texts land. They are collected once, at kickoff, by the orchestrator (live with the human; step 00 itself asks nothing) and recorded in the frontmatter. The pipeline flow is identical in every profile; nothing is re-asked later.

| Field | Values | Consumed by |
|---|---|---|
| `pr_audience` | `team` (humans review the PRs; the body is a short reviewer handoff) \| `solo` (the PR is the record; process-rich body) | steps 06, 08 |
| `review_placement` | `workspace` (agent review findings stay local) \| `pr` (findings posted on the PR) | step 07 |
| `questioning` | `chat` (one question per round) \| `annotation` (annotation rounds on the inventory) | step 03 |

Defaults, used when the kickoff was headless or the human gave no preference: `solo` · `pr` · `chat` — exactly the previous behavior.

## Blockers — failure as a file, not a message

`status:` is the one-grep run signal: any orchestrator — the run skill, a shell script, a CI pipeline — reads the same field to decide whether the run may advance. A step that cannot proceed **appends a blocker entry and sets `status: blocked` before returning**; a blocker that exists only in a step's report does not exist. Whoever resolves it marks the entry resolved and sets `status: in-progress`; step 10 sets `done` at the close.

Entry fields: **Missing** (what, concretely) · **Needed from** (person / team / system — carried over from the inventory entry's `Needed from:` where one exists) · **Blocking** (step) · **Since** (date) · **Escalation** (one ready-to-forward sentence) · **Resolved** (date + how, once it is).

## Quality criteria

- [ ] Supplied text is preserved verbatim. Image transcriptions identify the unchanged source and any unreadable or missing text.
- [ ] Branch name and folder path match the frontmatter. In a one-package delivery `branch:` names the package branch once created; before then it may be empty. With several packages it stays empty and the plan's package sections name the branches.
- [ ] `workspace_root` and `folder` resolve back to this file's actual directory per the catalog path contract; legacy manifests retain their existing meanings.
- [ ] Every component repository is declared by a portable relative path; absolute paths are prohibited.
- [ ] New component rows record verified remotes and base refs/commits; a parent notes repository is not mistaken for a component.
- [ ] New setup records input provenance and the registry/branch rules consulted.
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
workspace_root: ..
folder: delivery
created: <YYYY-MM-DD>
url: <ticket link, empty for free text>
status: in-progress
profile:
  pr_audience: solo
  review_placement: pr
  questioning: chat
---

# Story: <title>

Context loaded: <setup and branch rules read, or explicit none>

## Start here

- [Plan](3-planning/05-implementation.plan.md) · [Current state](1-research/01-current-solution.research.md) · [Full target solution](2-specification/03-target-solution.view.html) · [Design approval pack](2-specification/03-human-decision-gate.view.html)

## Original input

<ticket text or brain dump, unmodified>

## Input provenance

- Source: <ticket URL or path relative to this manifest>
- Verification: <live ticket checked | supplied input, not verified against live ticket | free text>
- Checked on: <date> · Lookup failure: <exact reason, or none>
- Unresolved source gaps: <missing or clipped content, or none>

## Component repositories

| Component | Relative location | Remote | Base ref | Base commit | Delivery role |
|---|---|---|---|---|---|
| <the repository> | `../repositories/<repo>` | <verified remote, no credentials> | <selected ref> | <resolved commit> | <its role> |

## Artifact ledger

| Status | Artifact | Purpose |
|---|---|---|
| present | `00-manifest.state.md` | this file |
| open | `1-research/01-current-solution.research.md` | current state (step 01) |
| open | `2-specification/02-questions.inventory.md` | question inventory (step 02, answered in step 03) |
| open | `2-specification/02-questions.view.html` | question pre-read (step 02, regenerated in step 03) |
| open | `2-specification/02-work-breakdown.md` | slices and the PR cut (step 02, frozen into the plan at step 05) |
| open | `2-specification/03-agreement.spec.md` | agreement (step 03) |
| open | `2-specification/03-target-solution.spec.md` | target design (step 03) |
| open | `2-specification/03-target-solution.view.html` | complete human view of the target design (step 03) |
| open | `2-specification/03-test-scenarios.spec.md` | test scenarios (step 03) |
| open | `2-specification/03-decision-manifest.state.json` | decisions, source authority and applicable rules (step 03; cross-cutting) |
| open | `2-specification/03-human-decision-gate.view.md` | portable generated gate pre-read (step 03) |
| open | `2-specification/03-human-decision-gate.view.html` | primary generated gate pre-read (step 03) |
| open | `3-planning/05-technical-analysis.research.md` | technical analysis (step 05, optional) |
| open | `3-planning/05-technical-questions.inventory.md` | technical questions (step 05, optional) |
| open | `3-planning/05-implementation.plan.md` | executable plan incl. progress log (step 05) |
| open | `3-planning/06-decisions.log.md` | decision log (cross-cutting) |
| open | `3-planning/07-review-<package-id>.state.json` | findings, evidence checks, grouped trial fixes and original comparison (step 07) |
| open | `3-planning/08-human-review-gate.view.md` | portable generated PR gate (step 08) |
| open | `3-planning/08-human-review-gate.view.html` | primary generated PR gate (step 08) |
| open | `3-planning/10-post-mortem.md` | close-out record (step 10) |

## Work-package ledger

| ID | Pull request | Target component | Status | Depends on | Blocked by | Human review |
|---|---|---|---|---|---|---|
| WP-01 | <link once open> | <component> | planned | none | none | pending |

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

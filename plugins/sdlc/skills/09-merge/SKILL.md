---
name: 09-merge
description: Pipeline step 09 (COLLAB) — present the ready pull request, pair-program any last fixes with the human, and merge only on their explicit command. Never merges autonomously.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.4.0'
  tags: sdlc, step, merge, collaborative, final-gate
---

# Step 09 · Merge  (COLLAB)

- **Type:** COLLAB — human and agent live; the final call is the human's
- **Skippable:** no

---

## What this skill does

Closes out one work package: presents the state compactly, pair-programs any last fixes, and merges its pull request on an explicit command. This is the last station before that package's code lands on the main branch — earlier approvals do **not** carry over, the human confirms again here. After the merge, the package's plan section and the manifest's work-package ledger row record the merge commit; packages that depended on this one become eligible. A package merge never marks the whole delivery done.

## When to use this skill

- The pull request has passed the human review gate and is ready to land

## When NOT to use this skill

- The review gate has not approved yet

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Pull request | status, mergeability, checks, review | yes |
| Human | the merge decision is theirs | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure for the merge itself (usually `none applicable`). Work borrowed from another step follows that step's needs: a fix made here loads what `06-implement` would, the same guideline and domain-language articles.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `00-manifest.state.md` | [`artifact-definitions/00-manifest.state.md`](../../artifact-definitions/00-manifest.state.md) |
| writes *(when fixes are made)* | `06-decisions.log.md` | [`artifact-definitions/06-decisions.log.md`](../../artifact-definitions/06-decisions.log.md) |

For follow-up questions consult the pull-request body; do not open the plan unless the human asks.

---

## Workflow

1. **Present the state** in one consolidated message: title and ticket · the PR link with state, mergeability, and any red checks · the agent verdict plus summary · inline comments as a list `file:line — first sentence` (first few, then a count) — then ask with concrete options: "A: inspect more · B: implement changes · C: prepare the merge · D: defer."
2. **Pair-program requested fixes.** Answer precisely, quoting `path:line`. Make the change, **actually run the verification it calls for**, and report honestly. Stage only touched files, commit, push, re-check CI. A failing hook → fix the cause and make a **new** commit; never amend, never skip.
3. **Merge only on an unambiguous command.** "Looks good" without a merge verb is not one — ask. Offer the strategies with trade-offs (squash: one commit, the usual default for small features · merge: keep commits plus a merge commit · rebase: linear, only for a genuinely clean branch), state your recommendation, then ask for the exact choice. Verify afterwards that the merge actually happened.
4. **On failure**, do not retry blindly — show the error verbatim and propose next steps with options: conflict → pull the main branch, resolve locally; failing required check → investigate first; branch protection → the human must obtain the approval.
5. **Clean up only on request.** Delete branches only after an explicit yes, and use the safe local delete.

---

## Output contract

Exactly one merged pull request, or a deliberate "deferred" with nothing touched. Zero or more pushed fix commits. Returns the merge commit reference and the final PR state.

---

## Constraints and guardrails

- **Never merge autonomously**, and never treat an earlier gate as standing permission.
- **Never bypass branch protection or required checks.** Never force-push.
- **Claim no unverified success** when reporting a fix.
- **Do not start follow-up work.** The package tail ends here; the delivery closes at step 10, the post-mortem.

---

## Success criteria

- [ ] Merged only after an explicit, unambiguous command
- [ ] Merge strategy chosen by the human from options with trade-offs
- [ ] Merge verified after the fact
- [ ] Branch cleanup only on explicit confirmation

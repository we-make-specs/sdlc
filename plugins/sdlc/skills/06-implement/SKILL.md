---
name: 06-implement
description: Pipeline step 06 (AUTO) — execute the plan end to end, one commit per task, keeping the plan's progress log current, then push the branch and open a pull request. Use once a plan has been written and approved.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.4.0'
  tags: sdlc, step, implementation, commits, pull-request
---

# Step 06 · Implement  (AUTO)

- **Type:** AUTO — fresh session, works the plan, asks no questions, runs to completion
- **Skippable:** no

---

## What this skill does

Executes the plan's task list group by group, committing once per task, keeping the progress log current, and finishing with a pushed branch and an open pull request.

## When to use this skill

- A plan exists and its acceptance criteria were approved

## When NOT to use this skill

- No plan exists, or the plan has no tasks — abort and point at step 05

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Feature folder | located via the manifest for the current branch | yes |
| Codebase | full access: read, edit, build, test, git | yes |

## Required context

- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — follow that procedure: read each declared registry's `index.md` and navigate its index tables to the guidelines and domain-language articles this step touches. Record a `Context loaded:` line in the plan's progress log **before the first task** (`none applicable` when nothing is declared); the articles you load are binding — a deviation is recorded in the progress log with its reason, never silent.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| reads | `05-implementation.plan.md` — the execution contract | [`artifact-definitions/05-implementation.plan.md`](../../artifact-definitions/05-implementation.plan.md) |
| reads | `03-target-solution.spec.md` — reference only, when the plan is underspecified | [`artifact-definitions/03-target-solution.spec.md`](../../artifact-definitions/03-target-solution.spec.md) |
| reads | `03-test-scenarios.spec.md` | [`artifact-definitions/03-test-scenarios.spec.md`](../../artifact-definitions/03-test-scenarios.spec.md) |
| updates | `05-implementation.plan.md` — task checkboxes and progress log **only** | same contract |
| writes | `decisions.log.md` — decisions made during implementation | [`artifact-definitions/decisions.log.md`](../../artifact-definitions/decisions.log.md) |

---

## Workflow

1. **Rehydrate.** Parse the plan fully; missing or task-less → abort.
2. **Group.** Bucket by group, respect order and dependencies. Tasks already ticked from a previous partial run are skipped and treated as done.
3. **Per task:** do the work per guidelines and surrounding code → run formatter, linter, tests → **verify the done-when literally** (file exists → check it; test passes → run it; unverifiable → treat as failed) → stage only that task's files → commit → append the progress-log line and tick the checkbox.
4. **Blocked task:** never silently skip. Record `WARN T<id>:` in the progress log and continue with independent tasks. If a long dependent chain is blocked, stop there, push what is done, and note the blocker. **If nothing was implementable** — the first task or the whole chain is blocked — open **no pull request**: commit only the progress log, append the blocker to the manifest's Blockers section with `status: blocked`, and return it as the step outcome so the orchestrator stops the run naming it. A pull request whose diff contains no code is noise, not progress.
5. **Fix documentation the diff made stale — in this same pull request.** Grep the documentation surface (README, docs, root instruction files, registry entries the diff touches) for the old names the diff removed or renamed; correct genuinely stale references in one documentation-only commit. Public surface (commands, environment variables, documented APIs, setup instructions) is where documentation drifts; internal refactorings rarely need it. Nothing stale is a valid outcome — never manufacture documentation churn.
6. **Push and open the pull request.** Body: summary, the acceptance-criteria list **verbatim from the plan** with fulfilled ones ticked, deviations from plan, known issues.

Fix only problems this work introduced. Pre-existing failures are not yours — the known-red-tests list lives in the testing guidelines.

---

## Output contract

Commits on the feature branch (one per task), pushed; an open pull request; the plan's checkboxes and progress log updated; `decisions.log.md` maintained. Returns the PR URL, one line per task, and any blockers.

---

## Constraints and guardrails

- **Edit the plan in exactly two places:** task checkboxes and progress log. Acceptance criteria, task descriptions, and advisor checks are read-only here.
- **Never force-push, never skip hooks, never amend a completed task's commit.**
- **Stage explicit paths.** Never stage everything blindly.
- **The out-of-scope list is binding** — even when adjacent work looks trivial.
- **Claim no unverified success.** Unresolved issues go into the PR body under known issues.

---

## Success criteria

- [ ] Every feasible task committed with its done-when verified
- [ ] One commit per task, explicit paths staged
- [ ] A pull request exists only if the diff touches code — total blockage returned a named blocker instead
- [ ] Pull request open with verbatim acceptance criteria in the body
- [ ] Progress log has one line per task, including WARN lines for blocked ones
- [ ] No documentation references the old behaviour — checked against the diff's removed names, fixed in this PR

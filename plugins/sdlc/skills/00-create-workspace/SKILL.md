---
name: 00-create-workspace
description: Pipeline step 00 (AUTO) — parse a ticket ID, ticket URL, or free-text brain dump, create or recognise the feature branch and folder, and write the initial manifest. Idempotent. Use at the start of a delivery run, or to bootstrap a feature workspace.
argument-hint: <ticket-id | ticket-url | free-text description>
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.6.0'
  tags: sdlc, step, workspace, bootstrap
---

# Step 00 · Create Workspace  (AUTO)

- **Type:** AUTO — mechanical, no model judgment required
- **Skippable:** no · **Idempotent:** yes

---

## What this skill does

Bootstraps or recognises the feature workspace: parses the input, ensures the branch and feature folder exist, and writes the initial manifest. After this, every later step operates purely on files in the feature folder.

## When to use this skill

- Starting a new feature through the pipeline
- Re-entering a run whose workspace may or may not already exist (safe to re-run)

## When NOT to use this skill

- The workspace already exists and is correct — this skill will simply confirm and change nothing, but there is no reason to invoke it directly

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Ticket or text | ticket ID, ticket URL, or free text | yes |
| Git working tree | the current clone | yes |

## Required context

- The repo's root `AGENTS.md`/`CLAUDE.md` **`## Context Registries`** declaration — this step's guard is that the repo carries one (registries, or a conscious `- none`). It is written by `/sdlc-context:connect`; materializing and reading the registries is each later step's own duty, not this step's.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| writes | `00-manifest.state.md` | [`artifact-definitions/00-manifest.state.md`](../../artifact-definitions/00-manifest.state.md) |
| writes | `AGENTS.md` — static, from the template | [`artifact-definitions/AGENTS.md`](../../artifact-definitions/AGENTS.md) |

---

## Workflow

1. **Verify a safe tree.** If a checkout would clobber tracked changes, stop and report. Branch off the current HEAD — do not silently switch to the main branch.
2. **Check idempotency.** Branch already matches the pattern and manifest exists → confirm and return unchanged. Branch exists, manifest missing → create only the manifest.
3. **Resolve metadata.** Ticket mode: fetch title, description, labels from the ticket system; on failure abort with a clear error — no silent fallback to free text. Free-text mode: `ticket = none`, title from the first meaningful line.
4. **Build the slug:** lowercase, transliterate umlauts, non-alphanumerics to `-`, truncate to 50 characters.
5. **Choose the placement and create the workspace.** One rule decides it: a story touching exactly one repository gets the feature folder `docs/sdlc/features/<YYYY-MM>/<story-slug>/` inside it; a story spanning several repositories gets a plain sibling folder `<story-slug>_workspace/` next to them. When the run starts inside a single repository but the input names components or repositories beyond it, say so before scaffolding anything and suggest the sibling placement; the human decides at kickoff, nothing moves silently. Never write next to the input source. In-repo placement: create the branch (type `fix` for bug labels, else `feature`); if the branch exists but is not checked out, stop — do not silently reuse. Sibling placement: create no branch here — branches belong to the work packages and are created at implementation time in their target repositories. If the workspace exists and is non-empty on a fresh run, stop — a previous run is in progress.
6. **Declare the component repositories** in the manifest: the current repository as `.` for the in-repo placement, or each participating repository by portable relative path for the sibling placement.
7. **Verify the context declaration.** The working repo's root `CLAUDE.md`/`AGENTS.md` must carry a `## Context Registries` section (multi-repo runs: each repo's own). Section missing entirely → append a Blockers entry (`Missing: context declaration in <repo>` · `Needed from: repo owner`), set `status: blocked`, stop. Exactly `- none` is a valid, conscious declaration. Materializing and reading the registries is the ambient `## Context Registries` procedure's job, run by each step when it needs them — not this step's. This can only happen *after* the checkout exists — the declaration lives in it.
8. **Write the manifest and AGENTS.md** per their contracts, carrying the original input over unchanged. Record the folder path in `folder:` — every later step and the orchestrator treat it as authoritative and re-derive nothing. Record the delivery profile the orchestrator collected at kickoff; absent answers use the contract's defaults. This step asks nothing itself. Scaffold nothing else: the numbered folders appear when the first artifact is written into them, and placeholder companions are never created.
9. **Report:** ticket, title, branch, folder, and whether the workspace was newly created or recognised.

---

## Output contract

Branch checked out, feature folder created, manifest written per contract. Nothing else modified. Returns ticket, title, branch, folder, and the newly-created flag.

---

## Constraints and guardrails

- **Atomic.** On abort, leave no partial artifacts — remove a branch or folder this run created.
- **No commit.** The first commit happens at implementation.
- **Never edit the original input.** It is the source of truth for final verification.
- **The input source is read-only.** A ticket, a seed file, or a pasted story is captured verbatim into the manifest and never touched again — no artifact is ever written next to it.
- **A workspace without a context declaration is not a workspace.** No `## Context Registries` section in the repo → blocker, never a silent default. Forgetting is the failure this guards against; a conscious `- none` passes.

---

## Success criteria

- [ ] In-repo placement: branch exists and is checked out. Sibling placement: no branch created; the component repositories are declared by relative path
- [ ] Workspace folder and manifest exist, manifest valid against its contract
- [ ] The repo carries a `## Context Registries` declaration (registries or `- none`) — or the run is blocked with the declaration named as missing
- [ ] No other files touched
- [ ] Re-running the skill changes nothing

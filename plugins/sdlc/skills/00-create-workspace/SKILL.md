---
name: 00-create-workspace
description: Pipeline step 00 (AUTO) — parse a ticket ID, ticket URL, or free-text brain dump, create or recognise the feature branch and folder, and write the initial manifest. Idempotent. Use at the start of a delivery run, or to bootstrap a feature workspace.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.2'
  tags: sdlc, step, workspace, bootstrap
---

# Step 00 · Create Workspace  (AUTO)

- **Type:** AUTO — mechanical, no model judgment required
- **Skippable:** no · **Idempotent:** yes

---

## What this skill does

Bootstraps or recognises the delivery workspace: resolves the input, prepares component
checkouts, creates the feature folder and writes its manifest. Later steps use that
manifest to find artifacts and source repositories.

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
| Workspace selection | ticket root, target code repository, or existing manifest | yes |
| Component sources | verified existing checkouts or remote URLs; requested base refs when applicable | yes for a new run |

## Required context

- The [workspace location and path rules](../../artifact-definitions/README.md#workspace-location-and-paths).
- The selected root's and component repositories' `AGENTS.md`/`CLAUDE.md` instructions and
  `## Context Registries` declarations. Read the declared registries' entry files, indexes,
  and branch/setup rules before choosing a branch. A conscious `- none` is valid; a missing
  declaration is a named setup blocker. Record a `Context loaded:` line in a new manifest.
  A new ticket root receives its declaration in step 5 from settled kickoff inputs or
  validated component declarations; its missing entry file before setup is not a blocker.

## Artifacts

| Direction | Artifact | Contract |
|---|---|---|
| writes | `00-manifest.state.md` | [`artifact-definitions/00-manifest.state.md`](../../artifact-definitions/00-manifest.state.md) |
| writes | `AGENTS.md` — static, from the template | [`artifact-definitions/AGENTS.md`](../../artifact-definitions/AGENTS.md) |

Setup also creates the phase directories and, for a new ticket root, prepares the declared
component clones and root entry file. These are setup outputs, not implementation work.

---

## Workflow

1. **Find an existing delivery first.** Follow the catalog's discovery rules. A matching,
   complete workspace returns unchanged, regardless of the shell's current branch. A
   blocked or partial workspace returns its blocker; never start a duplicate or silently
   migrate it. If a requested branch already exists without a manifest, verify its identity
   and preserve it; do not reset it to a new base.
2. **Resolve the input.** Fetch ticket metadata once when the integration is available.
   On lookup failure, use supplied text, an export or a screenshot only when it identifies
   the requested ticket and contains enough readable requirements to proceed. Preserve the
   ticket ID, record source paths and the error, and mark `not verified against live ticket`
   in Input provenance. Record cut-off or missing content as unresolved; never invent it or
   silently change to free-text mode. No usable supplied source means a blocker naming the
   needed ticket text. Free-text mode uses `ticket: none`. Step 02 carries unresolved source
   gaps into its inventory; source conflicts must be settled before design approval.
3. **Resolve placement and slug.** Use the catalog's single path contract. A selected ticket
   root gets `delivery/`, even for one component. A parent Git repository does not identify
   the component. Use the lowercased ticket ID for the story slug; derive it from the title
   only for free text. A non-empty proposed delivery directory without a matching manifest
   is a conflict, not a directory to overwrite.
4. **Prepare components.** Verify each remote and existing checkout before changing anything.
   Clone missing components into the ticket root's `repositories/`; never borrow another
   ticket's Git storage. For new clones, fetch and select the requested base, or the remote
   default branch when no base was requested. For a reused checkout, preserve current HEAD
   unless a different base was explicitly selected. Record the base ref and commit. Never
   discard local changes, replace a non-empty directory, or silently switch an existing
   checkout. Missing remote/base information returns a focused blocker to the orchestrator.
5. **Load setup conventions and connect the root.** Read component instructions and relevant
   registry rules, including branch naming. For a new ticket root, use the context plugin's
   `connect` contract with the kickoff's entries and entry-file choice. Existing component
   URL declarations may supply the root's entries; rebase local paths only when they remain
   inside the selected root. Do not invent a registry or declare `none` because information
   is missing. Keep component declarations intact. Add a short root-entry link to
   `delivery/00-manifest.state.md`, preserving other content and existing entry-file twins.
6. **Prepare the branch where needed.** In-repo runs create or verify the delivery branch
   using the selected base and the applicable naming rule, including ticket case. An
   explicit user choice is honored; conflicting applicable rules return a focused blocker.
   Existing branch names are evidence, not a rule. With no declared convention, use
   `feature/<story-slug>` or `fix/<story-slug>` for a bug. Ticket-root runs defer package
   branches to step 06; never create a branch in the ticket or notes repository.
7. **Write setup outputs.** Write the manifest and workspace `AGENTS.md` per their contracts,
   including `workspace_root`, `folder`, component locations, base refs/commits, input
   provenance and the collected delivery profile. Create `1-research/`, `2-specification/`
   and `3-planning/` inside the feature folder. Leave input files in place; create no
   placeholder artifacts or `.gitkeep` files. An undecidable setup choice is a durable
   Blockers entry with `status: blocked` once the delivery location is known. This step
   asks no questions itself; it returns the exact missing choice for the orchestrator.
8. **Verify and report.** Resolve all recorded paths from the manifest, verify each checkout's
   identity and base, and report ticket, root, folder, components, branch or deferred branch,
   provenance status, and whether setup was created or recognized.

---

## Output contract

Manifest and entry files written per contract, phase directories created, component
checkouts verified. In-repo branch checked out; ticket-root package branches deferred.
Returns ticket, title, branch, root, folder, components, and the newly-created flag.

---

## Constraints and guardrails

- **Preserve recoverable setup.** On failure, keep verified clones and the blocked manifest.
  Remove only incomplete temporary paths this run created; never delete a pre-existing
  folder, checkout or input. Record what remains so the next run can repair it.
- **No commit.** The first commit happens at implementation.
- **Never edit the original input.** It is the source of truth for final verification.
- **The input source is read-only.** Preserve supplied files and original text. A screenshot
  transcription is labeled as such and links its source; missing text stays missing.
  Delivery artifacts go in the selected feature folder, never inside an input folder.
- **A workspace without a context declaration is not a workspace.** No `## Context Registries` section in the repo → blocker, never a silent default. Forgetting is the failure this guards against; a conscious `- none` passes.

---

## Success criteria

- [ ] Placement follows the selected root; unrelated parent Git repositories were not used as components
- [ ] In-repo branch is checked out; ticket-root package branches are deferred
- [ ] Components have verified remotes, relative locations and recorded base refs/commits
- [ ] New ticket components are independent clones; existing selected checkouts were preserved
- [ ] Workspace folder and manifest exist, manifest valid against its contract
- [ ] The repo carries a `## Context Registries` declaration (registries or `- none`) — or the run is blocked with the declaration named as missing
- [ ] Root/context instructions and branch rules were read before branch creation
- [ ] Input provenance and lookup failures are recorded without changing source material
- [ ] The three phase directories exist; no placeholder artifacts were created
- [ ] Only setup outputs and declared component preparation were changed
- [ ] Re-running the skill changes nothing

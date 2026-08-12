---
artifact: AGENTS.md
produced_by: 00-create-workspace
consumed_by: [all]
required: true
---

# Contract — `AGENTS.md` (workspace operating rules)

## Purpose

The workspace's standing rules for any agent that enters it. Agent runtimes load an `AGENTS.md` automatically when they start in a folder — that mechanism, not documentation, is why this file earns its place. It is **static**: written once by step 00 from the template below, never updated during the delivery, so it cannot drift. Everything that changes lives in the manifest.

## The rule that defines this artifact

**Thin and stable.** No status, no artifact index, no story content — the manifest owns all of that, and this file points at it. If an edit to this file ever feels necessary mid-delivery, the content belongs somewhere else.

## Quality criteria

- [ ] Contains nothing story-specific beyond the title; a diff between two workspaces' AGENTS.md files touches only the first line.
- [ ] Was not modified after step 00 wrote it.

## Skeleton

```markdown
# <story-slug> workspace

This folder coordinates one delivery. It is not a source-code repository.

## Read first

Read [00-manifest.state.md](00-manifest.state.md) before anything else: it holds
the identity, the participating repositories, the artifact ledger, and the
work-package ledger. It links everything worth opening.

## Operating rules

- The manifest's ledgers are the single source for artifact and package state;
  update your own rows there, never a copy elsewhere.
- Each work package maps to one component repository and one pull request; never
  implement two packages in one PR.
- Perform source-code changes only inside the target component repository, and
  follow that repository's own instructions first.
- Approved `.spec.md` artifacts change only through dated correction or
  amendment entries, never by rewrite.
- Use portable relative paths everywhere; absolute paths are prohibited.
- Do not mark anything done without the verified branch, pull request, merge
  commit, or blocker to show for it.
```

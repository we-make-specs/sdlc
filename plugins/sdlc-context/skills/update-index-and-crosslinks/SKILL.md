---
name: update-index-and-crosslinks
description: 'Maintenance pass for a context registry: syncs every two-level index.md with the files on disk, repairs relative links, validates and completes the "This file answers / Related" cross-links, and migrates registries from older layouts. Run it inside a registry or point it at one. Use when the user says "update the registry index", "sync the index tables", "fix the crosslinks", "the registry index is out of date", or after articles were added, renamed, or removed.'
argument-hint: '[registry-root]'
metadata:
  owner: Markus-Arndt
  version: '0.3.0'
  tags: context-registry, index, crosslinks, maintenance
---

# Update index and crosslinks

## What this skill does

Keeps a registry's index tables, links, and cross-links true to the files on disk, per the update procedure in the registry format. Runs a fixed sequence: migration check, index pass, link pass, cross-link pass, entry-file check, report. The format authority for everything it writes is `../../reference.md`; when this file and the reference disagree, the reference wins. Invoked as `/sdlc-context:update-index-and-crosslinks [registry-root]`.

## When to use this skill

- Articles were added, removed, or renamed (including `_todo_`/`_partial_` prefix changes)
- The index tables or the cross-links may have drifted from disk
- A registry uses an older layout (routing files in subfolders, `## Contents` headings, a Last Read column, one-level tables) and needs migration

## When NOT to use this skill

- To scaffold a new registry: use `/sdlc-context:create`
- To declare registries in a consuming project repo: use `/sdlc-context:connect`

## Required inputs

| Input | Description | Required |
|---|---|---|
| registry-root | Path to the registry root folder | No. Falls back to the current directory, else the skill asks |

## Required context

`../../reference.md`. Read it before writing anything. The passes below depend on: section 3 (the rulebook), section 4 (index.md format, two-level rule, row membership, column rules), section 5 (articles), section 6 (cross-links), section 7 (prefixes), section 8 (tooling rules), section 10 (entry-file policy).

## Workflow

### 1. Resolve the registry root

Take the root from the argument. Without an argument, use the current directory if it looks like a registry: it contains an `index.md` with `type: index` frontmatter or a `Name | Type | Description | Updated` table. Otherwise ask the user for the path in plain text and wait for the answer.

Validate before anything else, fail closed on either check:

- The resolved path is not a registry (no index signal, and the migration check in step 2 finds nothing either): report what was found at the path and stop.
- Both `AGENTS.md` and `CLAUDE.md` exist at the root but differ: that is a validation failure per reference.md section 10. Report the differing regions and stop without writing anything.

### 2. Migration check (older layouts)

Run this before any other pass. Detect, in this order:

1. **Routing files in subfolders**: `find <root> -mindepth 2 \( -name AGENTS.md -o -name CLAUDE.md \) -not -path '*/.*'`. Hits mean the old per-folder twin layout.
2. **Root-only old layout**: a root `AGENTS.md` or `CLAUDE.md` carrying a routing table, in a root without an `index.md`.
3. **Format drift in index files**: a `## Contents` heading; a `Last Read` column; type values other than `folder` and `context` (`url`, `repo`, `data`); link text with the `_todo_`/`_partial_` prefix stripped; tables that are only one level deep; missing `type: index` frontmatter.
4. **Leftover machine keys in articles**: a tool-written `related:` frontmatter list (from earlier plugin versions).

Before offering migration, `cmp` every folder where both an `AGENTS.md` and a `CLAUDE.md` were found. Any divergent pair: report the differing folders and stop without writing anything.

Describe every finding to the user in plain text: which folders, which files, what the migration will change. Ask for confirmation and wait for the answer. Proceed only on an explicit yes. On anything else, stop after reporting: the passes below assume the format defined in reference.md and must not run against an unmigrated registry.

On confirmation, migrate:

1. Per subfolder with a routing file: if it has no `index.md`, move the routing file onto it with `git mv` to keep history (use CLAUDE.md when only that exists); merge into an existing `index.md` otherwise. Delete the redundant twin with `git rm`.
2. Reshape every index file to the section 4 shape: `type: index` frontmatter (`scope`, `description`, `updated`), H1, one prose paragraph, one bare table with columns `Name | Type | Description | Updated`. Remove a `## Contents` heading; drop a `Last Read` column; restore real filenames including prefixes as link text; retarget any directory link to the folder's `index.md`. Carry existing dates over; unknown is `-`, never invented.
3. Expand one-level tables to **two levels**: under every folder row, one `├─`/`└─` row per immediate entry of that subfolder.
4. Rows typed `url` or `repo` point outside the repository, which the format forbids: list them to the user and ask per row whether to delete it or move the reference into an article's prose. Rows typed `data` become `context`.
5. Remove tool-written `related:` frontmatter keys from articles. Cross-link knowledge lives in the "Related:" blockquote, which the cross-link pass handles.
6. At the root: ensure `index.md` exists and holds the two-level root table. If the kept entry file is a routing file rather than a rulebook, move its table into `index.md` and replace the entry file content with the rulebook template from reference.md section 3 (Domain indexes table filled from the top-level folders). If no root entry file exists at all, ask the user which format to create per section 10: `AGENTS.md` only (recommended), `CLAUDE.md` only, or both. Never create `CLAUDE.md` unless the user explicitly chose it.
7. Rewrite every link in the registry that pointed at an old routing filename (`02-architecture/AGENTS.md` becomes `02-architecture/index.md`).

Re-run the detection. It must find nothing before the passes below start.

### 3. Index pass

Per folder, root included, compare the table against the directory listing. Row membership and column rules are reference.md section 4:

- **Add** a row for every untracked markdown article, loadable data file (`.yml`, `.yaml`, `.json`, `.csv`), and subfolder: in the folder's own index AND as a `├─`/`└─` row in the parent's index. Description from the article's `scope:` frontmatter, else its first paragraph, trimmed under 80 characters; folder rows take the subfolder index's `description:`. A `.human.md` row marks itself human-facing in its description. Every real node must end up reachable from an index table.
- **Remove** rows (own and parent) whose target no longer exists on disk. Exception: never remove the row of a deleted placeholder without reporting it; placeholders are kept deliberately, so a vanished one is worth a Next-steps line.
- **Fix hrefs** broken by completeness-prefix renames: match rows to files by the prefix-stripped name, point the href at the real filename, and set the link text to the real filename including its prefix. Fix the folder's own index, the parent's `├─`/`└─` row, and record every old-name to new-name pair for step 4.
- **Keep the two-level structure**: folder rows link to `<folder>/index.md`; every link targets a file, never a directory.
- **Set Updated** per file from `git log -1 --format=%as -- <file>`. For a file not in git, fall back to its mtime only to fill a cell currently showing `-`; never replace an existing date from mtime. Never invent dates.
- A subfolder without an `index.md` gets one, built from the section 4 template. Mark `scope:` and the prose `TODO:` or derive them strictly from the folder name. Invent nothing: plausible filler is worse than a gap.

Keep existing row order; append new rows in filename order.

### 4. Link pass

Check every relative link in every markdown file under the root: the target must exist relative to the containing file and must be a file, not a directory. Outcomes:

- The link matches a rename recorded in this run (step 2 or 3): fix it.
- The link targets a directory: retarget it to the directory's `index.md`.
- The link points outside the repository (external URL or a path leaving the root): the format forbids it; report it (file, line, target) and leave it alone.
- Any other dangling link: report it (file, line, target) and leave it alone. Never guess a fix.

### 5. Cross-link pass

Cross-links are the "This file answers:" / "Related:" blockquote under an article's H1 (reference.md section 6). They are human-authored knowledge; the pass validates and completes, it does not invent:

- **Validate format**: each block matches the standard; each Related entry names a question and links a real filename. Report malformed blocks with the exact deviation.
- **Validate resolution**: every Related link resolves after the renames of this run. Fix links broken by recorded renames (including the shown filename text); report the rest.
- **Complete bidirectionality**: for every Related link from A to B where B has no link back to A, add the reverse entry to B's block when the question it must name is derivable from A's own "This file answers:" line. When A has no such line, do not guess: list the pair as a candidate in Next steps instead.
- **Propose, never write, new pairs**: from reading titles, scopes, and headings, list article pairs that look like they share a boundary but have no cross-links, as candidates in Next steps. Precision over recall: when in doubt, leave it out.
- Never write a `related:` frontmatter key; the blockquote is the only cross-link mechanism.

### 6. Entry-file check

Verify the root entry file(s) exist and, when both twins exist, that they are byte-identical after this run's writes (`cmp AGENTS.md CLAUDE.md`); repair only divergence introduced by this run's own writes. Never rewrite the rulebook's content: it is human-owned. When no entry file exists at all, ask the user which format to create per reference.md section 10 and scaffold it from the section 3 template; never create `CLAUDE.md` unless the user explicitly chose it. When the user declines, create nothing and report the gap.

### 7. Report

End with the Result block defined below, filled with real numbers. Success, stop, or declined migration, every run ends with it.

## Output discipline

The user sees exactly two kinds of messages from this skill: questions and the final Result block. Nothing else.

- Work silently. No step-by-step narration, no file-by-file progress, no restating these instructions, no explaining the registry format.
- Each question is one short message: one line of context, the options, nothing more.
- The final message is the Result block, preceded by at most one sentence. Anything that does not fit the block does not belong in the final message.
- Every run ends with the block, success or failure: Status says what happened, the body says what changed or why nothing did, Next steps give the user concrete actions or state `none`.

## Result block

```text
=== Result: /sdlc-context:update-index-and-crosslinks ===
Status: done | stopped (nothing written: <reason>) | stopped (migration declined)
Registry: <root>
Migration: performed (<n> routing files moved, <n> index files normalized) | not needed | declined by user

| index.md | Rows added | Rows removed | Hrefs fixed |
|---|---|---|---|
| index.md | 2 | 1 | 0 |
| 02-architecture/index.md | 0 | 0 | 1 |

Links fixed: <n>
Dangling or external links remaining: <n>
  <file>:<line> -> <target>   (one line each; omit when zero)
Cross-links: <n> validated, <n> reverse links completed, <n> malformed reported
Entry file: verified (AGENTS.md and CLAUDE.md byte-identical) | verified (AGENTS.md) | created | missing (creation declined)

Next steps:
1. <concrete actions: fix the listed dangling links, decide on the listed url/repo rows, review proposed cross-link candidates (pairs listed here), confirm migration on a re-run; or none>
```

One table row per index.md the run touched or checked. When the run stopped before the passes (validation failure, migration declined), keep only the lines that apply: Status, Registry, Migration or the failure reason, and Next steps that unblock the run.

### Idempotency

A second run on an unchanged registry must produce zero diff. The rules above guarantee it: stable row order, exact-shape tables, no run timestamps, cross-link completion only from derivable questions. When the working tree was clean before the run, verify by re-running and checking that `git status --porcelain` reports nothing new.

## Output contract

- Updated `index.md` files and completed cross-link blocks, all inside the registry root
- The Result block as the final message
- Nothing written outside the registry root, and nothing written at all when validation failed

## Constraints and guardrails

- **Fail closed.** Any step 1 validation failure: report precisely what failed and stop before writing anything.
- **Never invent dates.** Unknown is `-`. Never modify a date because of a tooling-only write.
- **The rulebook is human-owned.** Verify presence and twin identity, never rewrite content.
- **Cross-links are human knowledge.** Validate and complete; propose new pairs only as candidates.
- **Migration only on explicit confirmation.** No confirmation, no writes, report and stop.
- **Never create `CLAUDE.md` unasked.** Only when the user explicitly chose it.
- **Never guess a link fix** outside this run's recorded renames.
- **reference.md wins.** On any format doubt, re-read `../../reference.md` instead of improvising.

## Success criteria

- [ ] Every index is two levels deep, 4 columns, no `## Contents` heading, and matches the disk listing
- [ ] Link text everywhere is the real filename including its prefix; every link targets a file
- [ ] Every relative link resolves, or appears in the report
- [ ] Cross-link blocks validated, reverse links completed only from derivable questions, new pairs only proposed
- [ ] No Last Read column and no `related:` frontmatter key anywhere after the run
- [ ] An immediate second run produces zero diff
- [ ] Final message is the Result block only, with real numbers and next steps; no narration before it

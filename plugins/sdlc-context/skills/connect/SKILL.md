---
name: connect
description: Declare context registries for a project repository or delivery root. Validate local paths or Git URLs, then update the selected root's entry files. Use to connect a registry, declare project knowledge, prepare a ticket workspace, or record that a project uses no registry. Never run inside a registry itself.
argument-hint: '[registry-url-or-path ...]'
metadata:
  owner: Markus-Arndt
  version: '0.3.3'
  tags: context-registry, wire-format, project-setup, sdlc
---

# Connect registries to a project or delivery root

---

## What this skill does

Writes `## Context Registries` into the selected root's entry files. The root can be a
code repository or a delivery folder without Git. Registry URLs are materialized under
that root's `.sdlc/context/<name>/`; local paths are relative to that root. Validate all
entries before updating entry files. Preserve content outside the section and copy the
wire format from `../../reference.md` section 9 exactly.

---

## When to use this skill

- The user wants this repo to start consuming one or more registries
- A delivery setup needs a declaration at its selected ticket root
- The user wants to add, remove, or re-declare registries in an existing section
- The user wants to record that this repo consciously uses no registry

## When NOT to use this skill

- Scaffolding a new registry: that is `/sdlc-context:create`
- Fixing a registry's indexes, links, or crosslinks: that is `/sdlc-context:update-index-and-crosslinks`
- The selected root is itself a registry (root `index.md` with `type: index` plus a rulebook entry file): connect runs in consuming projects, not in registries

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Registry entries | git URLs, `./`-relative paths, or the word `none` | asked for if no arguments given |
| Target root | explicit project/delivery directory, or the current directory when it is the intended root | yes |
| Entry-file choice | reuse an already supplied choice; ask only when a new file is needed and no choice is settled | when creating |

## Required context

- Read and follow the [shared skill rules](../../skill-rules.md) before starting the workflow.
- `../../reference.md`: the registry format. Read section 9 (wire format) and section 10 (entry-file policy) before writing anything; validate registries against sections 2 to 4.

---

## Workflow

### 0. Resolve the target root

Use the selected directory exactly. A delivery folder need not contain `.git`; do not
ascend into a parent notes repository, initialize Git, or move the declaration into a
component. All paths below are relative to this selected root. When invoked from setup,
reuse its settled root, registry entries and entry-file choice without asking again.
An unresolved choice in unattended use returns a named blocker instead of guessing.

### 1. Collect entries

1. Take one entry per argument. Each is a git URL, a `./`-relative path, or the word `none`.
2. If no arguments were given, ask the user in plain text which registries this repo should declare (git URLs, `./`-relative paths, or `none` for a conscious no-registry declaration). Wait for the answer.
3. `none` combined with any other entry is a contradiction. Report it and stop.
4. A local path must be `./`-relative and resolve inside the selected root, including after resolving symlinks. Otherwise report it and stop. A path copied from a component declaration must be rebased and validated at its new root; never copy the original relative string blindly.
5. Removal is explicit only: when the user asks to remove a registry, mark that item for removal. Entries already declared in the file are never dropped just because this run did not name them.
6. After collecting entries, read the existing `## Context Registries` section from the root entry file, if one exists. For each declared entry this run did not name: honor an explicit removal named in the user's plain-text request; when the user's request reads as a full re-declaration ("only these", "exactly these", "replace the list"), ask keep-or-remove for each such entry and wait for the answer. On a plain additive run, rule 5 applies: keep the entry.

### 2. Validate every entry, fail closed

Validate all entries before updating entry files or `.gitignore`. Materializing URL
registries is part of validation. One failure stops declaration updates: report every
failure and any registry copies created or refreshed.

**Path entries:**

1. The directory exists.
2. It contains a root `index.md` with `type: index` frontmatter or a `Name | Type | Description | Updated` table, and a root entry file per `../../reference.md` section 10. Either missing: record the path as not a registry, naming what is absent, and continue checking the remaining entries.
3. If the root `index.md` exists, harvest the explainer line from its frontmatter: `description:` if present, else `scope:`. If the file is missing or both keys are missing, ask the user for a one-line explainer and wait for the answer.

**URL entries:**

1. Materialize: clone into `.sdlc/context/<name>/` where `<name>` is the URL's last segment without `.git` (`git clone --depth 1 <url> .sdlc/context/<name>`). For an existing folder, verify that its remote matches the entry before `git -C .sdlc/context/<name> pull --ff-only`. On failure, record the URL and exact error. Remove only an incomplete clone created by this invocation; preserve existing folders and continue validating other entries.
2. Check the materialized root against the same contract as a path entry (step 2 above).
3. Harvest the explainer line the same way (step 3 above).
4. Keep validated materialized copies. Never delete an existing registry copy because validation failed. Ignore-file changes wait until step 4, after registry and entry-file validation.

**The `none` entry:** nothing to validate.

### 3. Determine which entry files to write

Apply the [entry-file policy](../../reference.md#10-entry-file-policy) to the selected
root, including its Copilot redirect procedure. Skip the redirect for a `- none`
declaration.

### 4. Upsert the `## Context Registries` section

After all entries and entry-file choices pass validation, ensure `.gitignore` excludes
`.sdlc/` when URL registries are used and the selected root is itself the code repository's
Git root. For a delivery root, do not edit a parent ignore file or create Git metadata.

Replace the section if it exists (from its heading to the next same-or-higher-level heading or end of file); append it at the end of the file if it does not. Everything else in the file stays byte-for-byte untouched.

Copy the consumer template from `../../reference.md` section 9 character for
character, replacing only its illustrative registry list with the validated entries.
Write the complete procedure into the target entry files, not a link to the plugin.

List rules:

- One list item per registry: the git URL or the `./`-relative path, exactly as validated.
- One indented explainer line directly under each item, harvested in step 2.
- Order carries no meaning, but keep it stable: preserve the existing order of entries that stay, append new entries at the end, remove only the entries the user asked to remove.
- An entry already present is not duplicated; refresh its explainer line if the harvest differs.
- `none` produces exactly the no-registry declaration from `../../reference.md` section 9: the heading and the single item `- none`, no procedure. If the existing section lists registries and the user declared `none`, confirm in plain text that every existing declaration should be dropped, and wait for the answer before writing.

### 5. Report

After writing, verify the section parses back: the heading exists once, every item has its explainer (except `- none`), and twins are byte-identical when both exist. Then end with the Result block defined below. Success or failure, every run ends with it.

---

## Result block

On success:

```text
=== Result: /sdlc-context:connect ===
Status: done
Files written: AGENTS.md, CLAUDE.md (byte-identity verified)
Copilot stub: .github/copilot-instructions.md (created | redirect appended | already present | declined | skipped)

| Registry | Kind | Validation | Action |
|---|---|---|---|
| https://git.example.com/org/platform-context-registry.git | url | ok: shallow clone, contract found | kept |
| ./docs/context-registry | path | ok: index.md and rulebook found | added |

Entries kept: 1, added: 1, removed: 0

Materialized: .sdlc/context/platform-context-registry (pinned to origin/main)

Next steps:
1. Restart your agent session: instruction files load at session start, a
   running session will not see this change.
2. Smoke test in the new session: ask "which context registries does this
   repo declare?" and check that the first working reply on a real task
   starts with a "Context loaded:" line.
```

On validation failure:

```text
=== Result: /sdlc-context:connect ===
Status: stopped (declarations unchanged)

| Registry | Kind | Validation | Action |
|---|---|---|---|
| <entry> | url | failed: <verbatim git error> | rejected |
| <entry> | path | failed: <missing contract element> | rejected |

Materialized: <registry copies created or refreshed during validation, or none>

Next steps:
1. <the concrete action per failed entry, e.g. check the URL or repo access rights, or point at the registry root instead of a subfolder>
```

List every entry in the table, passed and failed. When any entry failed, entry files and
`.gitignore` stay unchanged; report registry copies separately.

---

## Output contract

- The `## Context Registries` section, upserted into the detected or chosen root entry file(s)
- Registry clones, the selected repository's `.gitignore` when applicable, and an authorized redirect stub are the only other setup writes; other entry-file regions remain untouched
- The Result block naming the files written and the validation result per registry

---

## Constraints and guardrails

- **Validate first, write second.** No entry file is touched while any entry is unvalidated or failed.
- **Fail closed.** Any validation failure stops entry-file and ignore-file changes; report the failure and registry materialization separately.
- **The wire format is a contract.** Copy the numbered procedure and the `- none` declaration from `../../reference.md` character for character. Add no extra keys, columns, or nesting.
- **Never create `CLAUDE.md` unasked.** Only when the user explicitly chose it in step 3.
- **Diverged twins stop the run.** Pre-existing differences between `AGENTS.md` and `CLAUDE.md` are reported, never silently resolved.
- **No precedence prose.** The section states the conflict rule (surface and ask); never write that one registry overrides another.
- **Materialized copies stay.** Keep validated registries at the selected root, gitignored when that root is the code repository. Remove only this invocation's incomplete clones; existing copies survive validation failures.
- **Removal needs a request.** Never drop a declared registry the user did not ask to remove.

---

## Success criteria

- [ ] Every entry validated before the first write, failures reported with exact reasons
- [ ] The section matches `../../reference.md` section 9: exact numbered procedure, item plus indented explainer per registry, or exactly `- none`
- [ ] Every validated URL is materialized under the selected root; `.sdlc/` is gitignored when that root is the code repository
- [ ] A delivery root was supported without initializing Git or modifying its parent repository
- [ ] Copilot stub handled per reference.md section 10: offered when missing or redirect-less, appended without touching existing content, never written unasked
- [ ] Existing entry order preserved, new entries appended, removals only on request
- [ ] Entry-file policy followed: mirrored what exists, reused settled choices, asked only for missing choices
- [ ] Twins byte-identical after writing when both exist
- [ ] Everything outside the section byte-for-byte unchanged
- [ ] Final message is the Result block only: files written, per-registry validation table, next steps; no narration before it

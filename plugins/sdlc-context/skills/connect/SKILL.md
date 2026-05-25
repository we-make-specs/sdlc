---
name: connect
description: Declare which context registries a project repository uses. Validates each registry (local path or git URL), then upserts the Context Registries section into the repo's root entry file(s). Runs inside the consuming project repo (a backend service, a frontend), never inside a registry. Use when the user says "connect a registry", "add a context registry to this repo", "declare our registries", "hook this repo up to the knowledge base", or "this repo uses no registry".
argument-hint: '[registry-url-or-path ...]'
metadata:
  owner: Markus-Arndt
  version: '0.3.0'
  tags: context-registry, wire-format, project-setup, sdlc
---

# Connect registries to a project repo

---

## What this skill does

Writes the `## Context Registries` section into this repository's root entry file(s), declaring which registries agents working here must consult. Every registry is validated before anything is written; git-URL registries are materialized into `.sdlc/context/<name>/` so that reading them costs a file view, not a clone; a one-line explainer is harvested from each registry's root; the section is replaced wholesale while everything else in the file stays untouched. The section format is the wire format defined in `../../reference.md` section 9: it is a shared contract with the pipeline's reader side, so this skill copies it exactly and extends it nowhere.

---

## When to use this skill

- The user wants this repo to start consuming one or more registries
- The user wants to add, remove, or re-declare registries in an existing section
- The user wants to record that this repo consciously uses no registry

## When NOT to use this skill

- Scaffolding a new registry: that is `/sdlc-context:create`
- Fixing a registry's indexes, links, or crosslinks: that is `/sdlc-context:update-index-and-crosslinks`
- The current directory is itself a registry (root `index.md` with `type: index` plus a rulebook entry file): connect runs in consuming repos, not in registries

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Registry entries | git URLs, `./`-relative paths, or the word `none` | asked for if no arguments given |
| Repo root | the current working directory must be the project repo's root | yes |

## Required context

- `../../reference.md`: the registry format. Read section 9 (wire format) and section 10 (entry-file policy) before writing anything; validate registries against sections 2 to 4.

---

## Workflow

### 1. Collect entries

1. Take one entry per argument. Each is a git URL, a `./`-relative path, or the word `none`.
2. If no arguments were given, ask the user in plain text which registries this repo should declare (git URLs, `./`-relative paths, or `none` for a conscious no-registry declaration). Wait for the answer.
3. `none` combined with any other entry is a contradiction. Report it and stop.
4. A local path that is not `./`-relative (absolute, or pointing outside the repo): report it and stop. The declaration must stay portable for every future reader of the file.
5. Removal is explicit only: when the user asks to remove a registry, mark that item for removal. Entries already declared in the file are never dropped just because this run did not name them.
6. After collecting entries, read the existing `## Context Registries` section from the root entry file, if one exists. For each declared entry this run did not name: honor an explicit removal named in the user's plain-text request; when the user's request reads as a full re-declaration ("only these", "exactly these", "replace the list"), ask keep-or-remove for each such entry and wait for the answer. On a plain additive run, rule 5 applies: keep the entry.

### 2. Validate every entry, fail closed

Validate all entries before writing anything. One failure stops the whole run: report every failure found, write nothing.

**Path entries:**

1. The directory exists.
2. It contains a root `index.md` with `type: index` frontmatter or a `Name | Type | Description | Updated` table, and a root entry file (`AGENTS.md` or `CLAUDE.md`, the rulebook). Either missing: record the path as not a registry, naming what is absent, and continue checking the remaining entries.
3. If the root `index.md` exists, harvest the explainer line from its frontmatter: `description:` if present, else `scope:`. If the file is missing or both keys are missing, ask the user for a one-line explainer and wait for the answer.

**URL entries:**

1. Materialize: clone into `.sdlc/context/<name>/` where `<name>` is the URL's last segment without `.git` (`git clone --depth 1 <url> .sdlc/context/<name>`); when the folder already exists, `git -C .sdlc/context/<name> pull --ff-only` instead. On failure, record the URL as unreachable together with the verbatim git error, remove a half-created folder, and continue checking the remaining entries.
2. Check the materialized root against the same contract as a path entry (step 2 above).
3. Harvest the explainer line the same way (step 3 above).
4. Keep the materialized copy: the numbered procedure in the section points agents at it. Ensure `.sdlc/` is listed in the repo's `.gitignore`; append it when missing. Remove the folder only when the entry failed validation.

**The `none` entry:** nothing to validate.

### 3. Determine which entry files to write

Follow `../../reference.md` section 10 exactly:

1. Detect what exists at the repo root: `AGENTS.md`, `CLAUDE.md`, both, or neither.
2. Both exist: compare them first. If they already differ, that is a validation failure; report the differing regions and stop without writing. If they match, apply every change to both and verify byte-identity after writing.
3. Exactly one exists: update that one.
4. Neither exists: ask the user in plain text which entry file to create: `AGENTS.md` only (recommended default), `CLAUDE.md` only, or both as byte-identical twins. Wait for the answer. Never create `CLAUDE.md` unless the user explicitly chose it.
5. **Copilot redirect stub** (`../../reference.md` section 10). Skip this step for a `- none` declaration. Check `.github/copilot-instructions.md`:
   - It exists but contains no redirect to the entry file: tell the user that some Copilot versions ignore AGENTS.md when this file is present, and offer to append the redirect template from reference.md section 10 (exact text, at the end, existing content untouched). Wait for the answer.
   - It does not exist: ask "Add .github/copilot-instructions.md redirecting Copilot to <entry-file>? Recommended for repos worked on with Copilot." Wait for the answer; create it with exactly the redirect template on yes.
   - It exists with the redirect: nothing to do.

### 4. Upsert the `## Context Registries` section

Replace the section if it exists (from its heading to the next same-or-higher-level heading or end of file); append it at the end of the file if it does not. Everything else in the file stays byte-for-byte untouched.

The section follows the template in `../../reference.md` section 9. The numbered procedure is exact text, copied character for character; the list items are this repo's registries:

```markdown
## Context Registries

STOP: complete these steps before your first code, config, or documentation
change in this session. They are mandatory.

1. For every registry listed below, read its entry file (AGENTS.md) and its
   root index.md. Git URLs live at .sdlc/context/<name>/ where <name> is
   the URL's last segment without .git: clone the URL there when the
   folder is missing, otherwise refresh it first with
   git -C .sdlc/context/<name> pull --ff-only. When the pull fails
   (offline, auth), use the existing copy and append (stale) to that
   registry's name in the Context loaded line.
2. Follow the index tables to every article your current task touches and
   read those articles.
3. Begin your first working reply with one line:
   Context loaded: <registry names, or "none applicable">
4. When two registries give conflicting guidance, surface the conflict to
   the user and ask which applies here. Never silently pick one; no
   registry outranks another.

- https://git.example.com/org/platform-context-registry.git
  Platform-wide conventions: architecture, dev guidelines, domain glossary.
- ./docs/context-registry
  Repo-local knowledge for this service.
```

List rules:

- One list item per registry: the git URL or the `./`-relative path, exactly as validated.
- One indented explainer line directly under each item, harvested in step 2.
- Order carries no meaning, but keep it stable: preserve the existing order of entries that stay, append new entries at the end, remove only the entries the user asked to remove.
- An entry already present is not duplicated; refresh its explainer line if the harvest differs.
- `none` produces exactly the no-registry declaration from `../../reference.md` section 9: the heading and the single item `- none`, no procedure. If the existing section lists registries and the user declared `none`, confirm in plain text that every existing declaration should be dropped, and wait for the answer before writing.

### 5. Report

After writing, verify the section parses back: the heading exists once, every item has its explainer (except `- none`), and twins are byte-identical when both exist. Then end with the Result block defined below. Success or failure, every run ends with it.

---

## Output discipline

The user sees exactly two kinds of messages from this skill: questions and the final Result block. Nothing else.

- Work silently. No step-by-step narration, no file-by-file progress, no restating these instructions, no explaining the registry format.
- Each question is one short message: one line of context, the options, nothing more.
- The final message is the Result block, preceded by at most one sentence. Anything that does not fit the block does not belong in the final message.
- Every run ends with the block, success or failure: Status says what happened, the body says what changed or why nothing did, Next steps give the user concrete actions or state `none`.

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
Status: stopped (nothing written)

| Registry | Kind | Validation | Action |
|---|---|---|---|
| <entry> | url | failed: <verbatim git error> | rejected |
| <entry> | path | failed: <missing contract element> | rejected |

Next steps:
1. <the concrete action per failed entry, e.g. check the URL or repo access rights, or point at the registry root instead of a subfolder>
```

List every entry in the table, passed and failed. When any entry failed, nothing was written; the table is the complete validation record.

---

## Output contract

- The `## Context Registries` section, upserted into the detected or chosen root entry file(s)
- No other file touched, no other region of the entry file(s) touched
- The Result block naming the files written and the validation result per registry

---

## Constraints and guardrails

- **Validate first, write second.** No entry file is touched while any entry is unvalidated or failed.
- **Fail closed.** Any validation failure: report precisely what failed and stop before writing anything.
- **The wire format is a contract.** Copy the numbered procedure and the `- none` declaration from `../../reference.md` character for character. Add no extra keys, columns, or nesting.
- **Never create `CLAUDE.md` unasked.** Only when the user explicitly chose it in step 3.
- **Diverged twins stop the run.** Pre-existing differences between `AGENTS.md` and `CLAUDE.md` are reported, never silently resolved.
- **No precedence prose.** The section states the conflict rule (surface and ask); never write that one registry overrides another.
- **Materialized copies stay.** `.sdlc/context/<name>/` folders of validated registries are kept (gitignored) so agents can read them cheaply; only failed clones are removed.
- **Removal needs a request.** Never drop a declared registry the user did not ask to remove.

---

## Success criteria

- [ ] Every entry validated before the first write, failures reported with exact reasons
- [ ] The section matches `../../reference.md` section 9: exact numbered procedure, item plus indented explainer per registry, or exactly `- none`
- [ ] Every validated git URL is materialized at `.sdlc/context/<name>/` and `.sdlc/` is gitignored
- [ ] Copilot stub handled per reference.md section 10: offered when missing or redirect-less, appended without touching existing content, never written unasked
- [ ] Existing entry order preserved, new entries appended, removals only on request
- [ ] Entry-file policy followed: mirrored what exists, asked before creating, `CLAUDE.md` only on explicit choice
- [ ] Twins byte-identical after writing when both exist
- [ ] Everything outside the section byte-for-byte unchanged
- [ ] Final message is the Result block only: files written, per-registry validation table, next steps; no narration before it

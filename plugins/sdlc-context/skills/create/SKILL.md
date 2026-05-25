---
name: create
description: Scaffold a new context registry at a target path, with the rulebook entry file, an index.md in every folder, preset article templates, and a README. Runs wherever the registry should live (a knowledge repo or a docs folder). Use when the user says 'create a context registry', 'scaffold a registry', 'set up a knowledge base for agents', or runs /sdlc-context:create.
argument-hint: '[target-path]'
metadata:
  owner: Markus-Arndt
  version: '0.3.0'
  tags: registry, scaffolding, context, sdlc
---

# Create a context registry

## What this skill does

Scaffolds a fresh context registry in the format defined by `../../reference.md`: the rulebook entry file at the root, a two-level `index.md` in every folder, `_todo_` article templates, and a README for human maintainers. It asks the user for a preset and an entry format, writes the tree, verifies it, and reports. It never fills articles with content and never modifies an existing registry.

## When to use this skill

- The user wants a new registry for a project or team
- A repo needs a knowledge folder that the sdlc pipeline can read

## When NOT to use this skill

- The target already is a registry: use `/sdlc-context:update-index-and-crosslinks`
- The user wants a repo to declare which registries it uses: use `/sdlc-context:connect`

## Required inputs

| Input | Description | Required |
|---|---|---|
| target-path | Folder where the registry is created | Yes, from the argument or by asking |
| Preset | `minimal` or `skeleton` | Yes, asked in the workflow |
| Entry format | `AGENTS.md`, `CLAUDE.md`, or both | Yes, asked in the workflow |
| Copilot stub | yes or no | Yes, asked in the workflow |

## Required context

- `../../reference.md`: the format spec. Quote its templates, do not re-invent them. When this file and reference.md disagree, reference.md wins.

## Workflow

1. **Resolve the target path.** Take it from the argument, relative paths resolved against the current directory. If no argument was given, ask the user in plain text for the target path and wait for the answer.
2. **Inspect the target.** If the target already contains an `index.md` with `type: index` frontmatter or a `Name | Type | Description | Updated` table, it already is a registry: report that, point at `/sdlc-context:update-index-and-crosslinks`, and stop. Otherwise, if the path exists and is not empty, list its contents to the user and ask whether to scaffold into it anyway; wait for the answer, and on anything but a clear yes stop without writing.
3. **Ask question 1, the preset.** Plain text, wait for the answer:

   ```text
   Which preset?
   - minimal: root, one example folder (01-development-guidelines) with one
     empty article, and a README
   - skeleton: five numbered folders (development guidelines, architecture,
     domain, testing, itsm incident management), each with an index.md and
     empty article templates
   ```

   Accept only `minimal` or `skeleton`. On any other answer, restate the options and ask again; never guess.
4. **Ask question 2, the entry format.** Plain text, wait for the answer:

   ```text
   Which entry file format?
   - AGENTS.md only (recommended)
   - CLAUDE.md only
   - both, kept as byte-identical twins
   ```

   Accept only these three. On any other answer, restate the options and ask again. Never create `CLAUDE.md` unless the user explicitly chose the second or third option (entry-file policy, `../../reference.md` section 10).
5. **Ask question 3, the Copilot redirect stub.** Plain text, wait for the answer: "Add .github/copilot-instructions.md redirecting Copilot to the entry file? Recommended when the registry is maintained with Copilot; some Copilot versions ignore AGENTS.md otherwise." On yes, the scaffold includes the stub with the exact redirect template from `../../reference.md` section 10.
6. **Collision check, fail closed.** Compute the complete list of files and folders the chosen preset and entry format will create, then add both `AGENTS.md` and `CLAUDE.md` to the list regardless of the chosen entry format: scaffolding one next to a pre-existing other would leave differing entry files, a validation failure per `../../reference.md` section 10. If any listed path already exists at the target, report every colliding path and stop without writing anything. This skill never overwrites a file.
7. **Scaffold.** Create the folders, then write every file, substituting the registry name (the target folder's basename), today's date as `<today>` in `YYYY-MM-DD` format, and the preset-specific names and descriptions:
   - The entry file(s) from the rulebook template in `../../reference.md` section 3, copied exactly, with the Domain indexes table listing the scaffolded folders. When only one entry file was chosen, drop the twin mentions and the byte-identity step as the template's substitution note says.
   - An `index.md` per folder from the section 4 template: `type: index` frontmatter, H1, one prose sentence, one bare table (no `## Contents` heading), columns `Name | Type | Description | Updated`.
   - The root `index.md` is **two levels deep**: one folder row per scaffolded folder, and under each folder row one `├─`/`└─` row per article inside it. Link text is the real filename including the `_todo_` prefix; folder rows link to `<folder>/index.md`.
   - `_todo_` articles and the README from the Templates section below.
   - Interior folders get only `index.md` and articles, never an entry file.
8. **Verify.** Check: every folder contains an `index.md`; every article appears in its folder's index and as a `├─`/`└─` row in the parent's index; every link resolves and targets a file, never a directory; no row exists for `index.md`, `README.md`, or the entry files; no created file is zero bytes; if both twins were created, they are byte-identical (`cmp AGENTS.md CLAUDE.md`). On any failure, report exactly which check failed on which file, list what was written, and stop instead of reporting success.
9. **Report.** End with the Result block defined below. Success or failure, every run ends with it.

## Presets

Both presets share the root files: the chosen entry file(s), `README.md`, and the two-level root `index.md`.

### minimal

| Path | Purpose |
|---|---|
| `01-development-guidelines/index.md` | Index for the example folder |
| `01-development-guidelines/_todo_coding-conventions.md` | Example article template |

Root row description for the folder: `Binding development rules of the project`.

### skeleton

Root rows, one per folder, each followed by its articles as `├─`/`└─` rows:

| Folder | Root row description |
|---|---|
| `01-development-guidelines/` | Binding development rules of the project |
| `02-architecture/` | System architecture: overview, functional, technical, ADRs |
| `03-domain/` | Domain glossary, roles and permissions |
| `04-testing/` | Overarching test approach across the system |
| `05-itsm-incident-management/` | Incident process: alerting, triage, tracking |

Articles per folder, each an `_todo_` template with its row description:

| Folder | Article file | Row description |
|---|---|---|
| `01-development-guidelines/` | `_todo_coding-conventions.md` | Naming, structure, and style rules |
| `01-development-guidelines/` | `_todo_testing-strategy-dev.md` | Unit and integration tests developers write |
| `02-architecture/` | `_todo_system-architecture.md` | Overview diagram and where each topic lives |
| `03-domain/` | `_todo_glossary.md` | Domain terms and their meaning |
| `03-domain/` | `_todo_roles-and-permissions.md` | Role catalog and permission matrix |
| `04-testing/` | `_todo_testing-strategy.md` | Which test levels exist, what each covers, who runs it |
| `05-itsm-incident-management/` | `_todo_incident-management.md` | Alerting, triage, tracking, postmortems |

## Templates

These instantiate the templates of `../../reference.md` sections 3 to 5. The entry file comes from section 3 verbatim. The remaining files:

**Folder `index.md`** (root follows the same shape, two levels deep):

```markdown
---
type: index
scope: "TODO: one line naming this folder's knowledge area"
description: <row description from the preset table>
updated: <today>
---

# <NN Folder Name>

Enter this folder when the query concerns <knowledge area>.

| Name | Type | Description | Updated |
|------|------|------|------|
| [_todo_<name>.md](_todo_<name>.md) | context | <row description> | <today> |
```

**`_todo_` article.** Frontmatter plus TODO-marked stubs, never zero bytes, nothing that could be mistaken for guidance:

```markdown
---
title: <Clean Name>
scope: "TODO: one line describing what this article covers"
updated: <today>
---

# <Clean Name>

TODO: fill this article. When it carries real guidance, rename it (_todo_ →
_partial_ → no prefix) and touch every index row and cross-link that shows it.

## TODO: first section

TODO:
```

**`README.md`.** For humans maintaining the registry (agents read the rulebook instead):

```markdown
# <registry-name>

This folder is a context registry: curated markdown knowledge that agents
navigate on demand via the index.md tables. The rules live in AGENTS.md
(the rulebook); this README is for humans maintaining the registry.

Maintaining it:

- Fill the _todo_ articles. On every rename, update the folder's index.md,
  the parent's index.md, and every cross-link (both directions).
- Declare this registry in consuming repos with /sdlc-context:connect.
- Keep indexes and cross-links current with
  /sdlc-context:update-index-and-crosslinks.
```

## Output discipline

The user sees exactly two kinds of messages from this skill: questions and the final Result block. Nothing else.

- Work silently. No step-by-step narration, no file-by-file progress, no restating these instructions, no explaining the registry format.
- Each question is one short message: one line of context, the options, nothing more.
- The final message is the Result block, preceded by at most one sentence. Anything that does not fit the block does not belong in the final message.
- Every run ends with the block, success or failure: Status says what happened, the body says what changed or why nothing did, Next steps give the user concrete actions or state `none`.

## Result block

On success:

```text
=== Result: /sdlc-context:create ===
Status: done
Created: <n> files at <absolute target path> (preset: <minimal | skeleton>, entry format: <AGENTS.md | CLAUDE.md | both>)

<tree of every created file and folder>

Next steps:
1. Fill the rulebook's TODO spots and the _todo_ articles; on every rename
   update the folder index, the parent index, and the cross-links.
2. Declare the registry in consuming repos: /sdlc-context:connect.
3. After filling articles: /sdlc-context:update-index-and-crosslinks.
```

On any stop (existing registry found, declined scaffold-into, collision, failed verify):

```text
=== Result: /sdlc-context:create ===
Status: stopped (nothing written)   <or: stopped (partially written, see below)>
Reason:
- <max 5 bullets: exactly what failed or why the run stopped>

Next steps:
1. <the concrete action that unblocks the run, e.g. clear the colliding paths, or run /sdlc-context:update-index-and-crosslinks instead>
```

## Constraints and guardrails

- **Fail closed.** Any failed check in steps 2, 6, or 8 stops the run with a precise report; steps 2 and 6 stop before anything is written.
- **Never overwrite an existing file.** Collisions are validation failures, not merge opportunities.
- **Never create `CLAUDE.md` unasked.** Only when the user explicitly chose it in question 2.
- **Only the root gets entry files.** Interior folders contain `index.md` and articles, nothing else.
- **Two levels everywhere.** Every index lists its own entries plus `├─`/`└─` rows for each subfolder's immediate contents.
- **Real filenames as link text**, prefixes included; every link targets a file, never a directory.
- **No zero-byte files, no `.gitkeep`, no dummy files.** An empty folder is carried by its `index.md`.
- **Ask, do not assume.** All three questions require an explicit answer; silence or an off-list answer is never consent.

## Success criteria

- [ ] All three questions asked and answered before any write
- [ ] Created tree matches the chosen preset exactly, verified per step 8
- [ ] Entry file matches the rulebook template of `../../reference.md` section 3
- [ ] Every index is two levels deep with 4 columns and no `## Contents` heading
- [ ] Twins byte-identical when both were chosen
- [ ] Final message is the Result block only, with tree and next steps; no narration before it

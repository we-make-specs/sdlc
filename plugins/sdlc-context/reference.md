# Context registry reference

This file is the single source of truth for the registry format. The three maintainer skills (`create`, `connect`, `update-index-and-crosslinks`) quote their templates from here and validate against it. When a skill and this file disagree, this file wins. There is exactly one format, this one: when talking to users, call it the registry format, never a version name. The format was extracted from a real registry's rulebook; the skills enforce it and invent nothing beyond it.

---

## 1. What a registry is

A context registry is a versioned folder of curated markdown knowledge: architecture, conventions, domain terms, recipes. Agents navigate it on demand through its index tables and read only the articles a query needs. A registry holds knowledge to consult, not standing instructions. Reading the root entry file and the root `index.md` is mandatory before working with or on a registry; every article after that is loaded on demand, never wholesale.

## 2. Layout

- Every folder, the root included, contains an `index.md`.
- Only the root contains the entry file: `AGENTS.md`, optionally with a byte-identical `CLAUDE.md` twin. The entry file is the rulebook (section 3). Subfolders never contain an `AGENTS.md` or `CLAUDE.md`.
- The root also carries a `README.md` written for humans maintaining the registry; agents skip it.
- An otherwise-empty folder is kept in git by its `index.md`. Never add `.gitkeep` or dummy files.

Example tree:

```text
my-registry/
├── AGENTS.md                      the rulebook (entry file)
├── CLAUDE.md                      optional byte-identical twin
├── README.md                      for humans maintaining the registry
├── index.md                       root index, two levels deep
├── microservices.yml              machine-readable catalog, a context row in index.md
├── 01-development-guidelines/
│   ├── index.md
│   ├── _todo_coding-conventions.md
│   └── backend/
│       ├── index.md
│       └── build-and-run.md
└── 02-architecture/
    ├── index.md
    ├── _partial_system-architecture.md
    └── non-functional-requirements.human.md
```

## 3. The entry file (the rulebook)

The entry file is the registry's rulebook: how to use it, the index mechanism, the cross-link standard, the update procedure, and what consuming repositories must state. It is human-owned. `create` scaffolds it once from the template below; `update-index-and-crosslinks` verifies that it exists and that twins are byte-identical, and never rewrites its content.

Scaffold template. Substitute `<registry-name>`; fill the Domain indexes table with one row per top-level folder; when only one entry file was chosen, drop the twin mentions and the byte-identity step:

```markdown
---
scope: Entry point and rulebook for this context registry
description: Read this file plus index.md before any work, then navigate via the index tables. Contains every rule for using and maintaining the registry.
---

# <registry-name>

Project knowledge for agent sessions, organised as an indexed knowledge base. Reading this file and [`index.md`](index.md) is **mandatory** before working with or on this repository; every article after that is loaded on demand.

> **Rulebook, not project knowledge.** This file says how the registry works. The knowledge itself starts at [`index.md`](index.md).

## Using the registry

1. Open [`index.md`](index.md): a two-level index of the whole registry. Judge relevance from the Description column, descend into a domain's own `index.md` where needed, and load only the articles the task needs. Never load everything.
2. Filenames carry the state: `_todo_` = template only, do not load it as guidance; `_partial_` = usable, but an absent rule does not mean "unconstrained"; no prefix = filled in.
3. A trailing `.human.md` marks background reading for humans: skip it. `.agent.md` appears only where a topic also has a human version.
4. Articles are self-contained. The "Related:" block under a title says which neighbouring article answers which question; follow it instead of searching.
5. `TODO:` means "not written down yet", never "unconstrained". Ask; never invent a value.
6. Folder numbers are stable prefixes for a fixed order, not a required reading order.

## The index mechanism

- Every folder has an `index.md`: frontmatter (`type: index`, `scope`, `description`, `updated`) plus one Contents table.
- Each index is **two levels deep**: the folder's own entries, and under every folder row its immediate contents marked with `├─`/`└─`. Redundant on purpose: navigation costs one read, not a chain of reads.
- Folder rows link to the subfolder's `index.md`. Tables show real filenames including their prefix. Descriptions stay under ~80 characters; they drive relevance decisions.
- Only the repository root has `AGENTS.md` and `CLAUDE.md` (this rulebook, byte-identical). Subfolders carry only their `index.md`.

## Cross-links

Articles that share a topic boundary each carry a block directly under their heading:

> **This file answers:** <the question this article owns>
> **Related:** <question> → [<real filename>](<path>) · <question> → ...

A cross-link always names the question its target answers, never a bare "see also". Links go in both directions or not at all.

## Maintaining (the update procedure)

When adding, renaming, moving or deleting an article:

1. Update the folder's own `index.md`.
2. Update the parent folder's `index.md` (the two-level redundancy).
3. Update cross-links in both directions.
4. When an article's completeness changes, rename it (`_todo_` → `_partial_` → no prefix) and touch every index row and cross-link that shows it.
5. Verify: every relative link resolves, every file appears in its folder's index and its parent's index, root `AGENTS.md` and `CLAUDE.md` are byte-identical.

An otherwise-empty folder is kept in git by its `index.md`; never add `.gitkeep` or dummy files. A placeholder article is never zero bytes: frontmatter and a one-line scope minimum. No links out of this repository.

## Domain indexes

| Index | Covers |
|---|---|
| [index.md](index.md) | the whole registry, two levels deep |
| <one row per top-level folder: [NN-name/index.md](NN-name/index.md) and what it covers> |

## For consuming repositories

A service repository that links this registry states in its own agent instructions: reading this registry's `AGENTS.md` (or `CLAUDE.md`) **and** `index.md` is mandatory before implementation work. Articles are then loaded on demand via the index; the registry is the source of truth for the rules it covers.

Humans maintaining this registry: see [`README.md`](README.md).
```

## 4. index.md

Every `index.md` has three parts in this order: frontmatter, an H1 with one short prose paragraph, one table. The table follows the prose directly: there is no `## Contents` heading.

Structural template (shape and column set binding; names, rows, and dates illustrative):

```markdown
---
type: index
scope: Binding development rules of the project, split by stack
description: Development guidelines in two halves: backend and frontend. Pick your half first.
updated: 2026-07-25
---

# 01 Development Guidelines

Binding development rules so that generated code fits the existing codebase. Pick `backend/` or `frontend/` first.

| Name | Type | Description | Updated |
|------|------|------|------|
| [backend/](backend/index.md) | folder | Backend rules in four groups: basics, layers, contracts, cross-cutting | 2026-07-25 |
| ├─ [01-basics/](backend/01-basics/index.md) | folder | Build and run, reference implementations, branching | 2026-07-25 |
| └─ [02-layers/](backend/02-layers/index.md) | folder | The hexagon: layer rules and one article per layer | 2026-07-25 |
| [frontend/](frontend/index.md) | folder | Frontend rules: components, micro-frontends, testing style | 2026-07-25 |
| └─ [_todo_frontend-testing.md](frontend/_todo_frontend-testing.md) | context | How frontend tests are written | 2026-07-25 |
```

Rules:

- **Columns** are exactly `Name | Type | Description | Updated`. There is no Last Read column (dropped: it was never maintained).
- **Two levels deep**: the folder's own entries, and under every folder row its immediate contents as `├─`/`└─` rows. Redundant on purpose: navigation costs one read, not a chain of reads.
- **Types** are `folder` and `context`, nothing else. `context` covers every loadable file: markdown articles and machine-readable data files (a `microservices.yml` catalog is a `context` row).
- **Every link targets a file, never a directory**: folder rows link to the subfolder's `index.md`, so links stay clickable in IDE markdown previews.
- **Link text is the real filename including its prefix**, e.g. `[_todo_glossary.md](_todo_glossary.md)`. Never strip `_todo_`/`_partial_`.
- **Descriptions** stay under about 80 characters; they drive relevance decisions. A `.human.md` row marks itself as human-facing in its description, e.g. `👤 Humans only: ...`.
- **Updated** is `YYYY-MM-DD` from `git log -1 --format=%as -- <file>`; mtime may only fill a cell showing `-`, never replace an existing date. Never invent dates.
- **Row membership**: every markdown article, every loadable data file (`.yml`, `.yaml`, `.json`, `.csv`), and every subfolder gets one row in its folder's index and one `├─`/`└─` row in its parent's index. Exempt: `index.md` itself, the root entry files, `README.md`, and hidden files or folders. Every real node must be reachable from an index table.
- **No links out of the repository**: no external URLs, no shared tooling paths, no board tickets, no other registries.

## 5. Articles

- Frontmatter `title`, `scope`, `updated` required, then an H1. Articles are self-contained; headerless copy-paste fragments violate the format. No `applies-to` key.
- The filename prefix is the single completeness marker: no status banners inside bodies, no "(empty)" notes in descriptions.
- Audience: no suffix = agent-facing. `.human.md` = background reading for humans, agents skip it. `.agent.md` appears only where a topic also has a human version.
- A placeholder article is never zero bytes: frontmatter plus a one-line scope minimum. Tooling never deletes placeholder files.

## 6. Cross-links

Articles that share a topic boundary each carry a block directly under their heading:

```markdown
> **This file answers:** <the question this article owns>
> **Related:** <question> → [<real filename>](<path>) · <question> → ...
```

- A cross-link always names the question its target answers, never a bare "see also". Links go in both directions or not at all.
- An article without a shared boundary carries no block. A filled article may carry a Related line alone when it points at neighbours without owning a contested question.
- Cross-links are human-authored knowledge. Tooling validates them (format, resolution, bidirectionality), completes a missing reverse link when the question is derivable from the target's own "This file answers:" line, and proposes new pairs only as candidates.

## 7. Completeness prefixes

| Prefix | State | Reading rule |
|---|---|---|
| `_todo_` | Pure template, headings and TODO stubs only | Do not load as guidance |
| `_partial_` | Partly filled | What is there is binding; gaps are not permission |
| none | Filled | Binding |

When an article changes state, rename the file and touch every place that shows it: the row in its folder's `index.md`, the `├─`/`└─` row in the parent's `index.md`, and every cross-link. A rename without that sweep leaves dangling links; treat it as incomplete.

## 8. Rules for maintainer tooling

- Follow the rulebook's update procedure (section 3 template, "Maintaining"): own index, parent index, cross-links in both directions, rename sweep, verify.
- The entry file is human-owned: verify presence and twin byte-identity, never rewrite its content.
- Never invent dates; unknown is `-`. Never delete placeholder files. Never advance an `updated` value because of a tooling-only write.
- Fail closed: when any validation fails, report precisely what failed and stop before writing anything.

## 9. The `## Context Registries` section (wire format)

A project repo declares its registries in a `## Context Registries` section of its root entry file. This format is a shared contract with the pipeline's reader side: keep it exactly as specified, extend it nowhere.

- One list item per registry: a git URL or a `./`-relative path.
- Optionally one indented explainer line directly under each item.
- A repo that consciously uses no registry declares exactly `- none`.
- Above the list stands a numbered mandatory procedure, not descriptive prose. Field evidence: a session that received the mandate as prose loaded it, read it, and still skipped it. The procedure is action-first (numbered steps before any change), cheap (git URLs are materialized locally so reading costs one file view, not a clone), and observable (the `Context loaded:` line lets a human verify obedience at a glance).

Template (the numbered procedure is exact text; the two list items are illustrative):

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

No-registry declaration (exact text):

```markdown
## Context Registries

- none
```

There are no precedence semantics between registries. Order in the list carries no meaning.

## 10. Entry-file policy

Which entry file to write (`AGENTS.md`, `CLAUDE.md`, or both) is decided by detection, never by default writing:

1. **Detect before writing.** Check which entry files exist at the target root.
2. **Mirror what exists.** Update every entry file that is present. When both `AGENTS.md` and `CLAUDE.md` exist, compare them before writing: if they already differ, that is a validation failure; report the differing regions and stop without writing anything. When they match, apply every change to both, verify byte-identity after writing, and repair only divergence introduced by this run's own writes.
3. **Ask only when creating.** When neither exists and one is needed, ask the user which format they want: `AGENTS.md` only (recommended default), `CLAUDE.md` only, or both as byte-identical twins. Wait for the answer.
4. **Never create `CLAUDE.md` unasked.** Only when the user explicitly chose it.

### The Copilot redirect stub

`.github/copilot-instructions.md` is the file GitHub Copilot always loads. Some Copilot versions suppress `AGENTS.md` entirely when this file is present. Two consequences:

- A repo worked on with Copilot should carry a stub that redirects to the entry file, so every Copilot version lands on it: new versions merge both files, old versions follow the redirect.
- An existing `.github/copilot-instructions.md` without the redirect actively hides the entry file from those Copilot versions. Tooling must detect that and offer to append the redirect.

Rules: create the stub only with the user's consent; never overwrite or reorder existing content, append the redirect at the end when the file exists without one; point the redirect at the entry file that exists (`AGENTS.md`, else `CLAUDE.md`).

Template (exact text; substitute the entry filename):

```markdown
STOP: before any code, config, or documentation change, read AGENTS.md at
the repository root and follow it completely, including its Context
Registries section when present. This file intentionally adds no rules of
its own; AGENTS.md is the single source.
```

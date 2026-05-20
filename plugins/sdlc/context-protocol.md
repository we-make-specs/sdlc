# Context Protocol — how project knowledge reaches a step

The pipeline is generic; the rules it must respect (guidelines, architecture, domain language) are not — they differ per team, per project, per repo. This file defines the one mechanism that connects them. Three moves: repos **declare** their registries, step 00 **freezes** the declarations into the manifest, and every step **resolves** its own binding set from there. The orchestrator does none of this — it only greps for the traces.

---

## 1 · The declaration — a repo names its registries

The working repository's root `CLAUDE.md` / `AGENTS.md` (both — they are mirrored) carries a `## Context Registries` section:

```markdown
## Context Registries

- https://github.com/acme/backend-context-registry.git
- https://github.com/acme/payments-context-registry.git
- ./docs/sdlc/context
```

- An entry is a **git URL** — the normal form, resolvable from any machine and any CI runner — or a `./`-relative path for a registry vendored inside the repo. Absolute paths work for local-only setups but defeat portability; a sibling-checkout assumption is not a link.
- **Order is precedence.** General registries first, specific ones last; where guidance conflicts, the later registry wins.
- A repo that consciously has no registry declares exactly `- none`. What is forbidden is *forgetting*, not *having nothing*.

The declaration is a property of the **repo**, set once and versioned with it — never of an invocation, a machine, or an installed plugin. That is what keeps one laptop with checkouts from two teams correct, and what makes a multi-repo run resolve per repo.

## 2 · The binding — an article names its steps

A registry article that must reach specific pipeline steps carries one frontmatter key:

```yaml
applies-to: [05-plan, 06-implement, 07-review]
```

- Values are step ids — the `skill:` names from `workflow.yml` (`00-ensure-workspace` … `09-merge`).
- No `applies-to` → the article is never auto-loaded. It stays reachable through the registry's routing tables, but the pipeline will not inject it.
- **Steps never name articles.** The binding direction is always knowledge → step, so a new article binds itself without touching any skill, and the pipeline stays installable in a project it has never seen.

## 3 · Step 00 — freeze the map into the manifest

Declarations live in the checkouts, so they can only be read after branches and checkouts exist. Once they do, step 00:

1. Reads each working repo's root declaration.
2. **Materializes** every URL entry: clone — or fetch + fast-forward when already present — into `.sdlc/context/<name>/` inside that repo, where `<name>` is the URL's last segment without `.git`. Ensures `.sdlc/` is listed in the repo's `.gitignore` (appends it when missing). Path entries are validated to resolve on disk, as before.
3. Writes the map into the manifest — per registry: source, pinned commit, materialized local path:

```markdown
## Context

- <repo>:
  - <name> — <git url or path> @ <short-sha> → .sdlc/context/<name>
  *(or a single `none (declared)` line for the repo)*
```

The SHA pins the run to the guidance version it ran under; re-running step 00 fetches and re-pins. Materialization is **per repo, inside the repo**: every read stays inside the runtime's trusted folder, the same registry cloned into two repos is cheap, and the workspace stays derivable from the checkouts alone.

**Fail closed.** A repo without the `## Context Registries` section, a path that does not resolve, or a clone/fetch that fails (network, auth) → Blockers entry (`Missing: context declaration in <repo> · Needed from: repo owner`, naming the exact path or URL and the cause), `status: blocked`, stop. A broken declaration is worse than none — it silently loads partial rules.

## 4 · Every step — resolve, read, log

Before doing its work, every step 01–09:

1. Reads the manifest's `## Context` section. No section → Blockers entry ("workspace incomplete — re-run step 00"), `status: blocked`, stop.
2. Takes the registries of the repo it is **writing into** (multi-repo runs resolve per repo) — always the **materialized local paths** from the manifest rows; steps never touch a URL.
3. Collects the articles whose `applies-to` contains this step's id — one search, e.g. `grep -rl 'applies-to:.*06-implement' <registry>` across its `*.md` files.
4. Reads them in declared registry order — later registries override earlier ones on conflict.
5. Records the result in its primary artifact, near the top: `Context loaded: <article names — or "none applicable">`. Step 06 records it in the plan's progress log; step 07 in its review body.

An **empty binding set is normal** — state it and proceed. Refusal is about missing declarations, never about missing matches; otherwise a gate with no bound articles would block absurdly.

Work borrowed from another step follows that step's bindings: a fix made during 09-merge follows 06-implement's set; review of that fix follows 07-review's.

## 5 · Who refuses what

| Situation | Who stops | How |
|---|---|---|
| Repo without `## Context Registries` | step 00 | blocker: missing declaration, needed from repo owner |
| Declared path does not resolve | step 00 | blocker naming the exact path |
| Registry clone/fetch fails (network, auth) | step 00 | blocker naming the URL and the cause |
| Manifest without `## Context` | every later step | blocker: workspace incomplete, re-run step 00 |
| Empty binding set for a step | nobody | `Context loaded: none applicable` — proceed |

## 6 · The invariant

**State lives in files, knowledge lives in steps, the orchestrator only sequences and greps.** It checks that a `Context loaded:` line exists — it never discovers registries, never resolves bindings, never reads guideline content. Anything an orchestrator would have to *compute* belongs in a step or in a file. That is what keeps `/sdlc:run`, a shell script, and a CI job interchangeable interpreters of the same files.

## 7 · Multi-repo discovery — the lead-repo bootstrap (design note, next increment)

A feature spanning several repos looks circular — repos declare registries, but only a registry knows which repos exist. The circle breaks because a run always starts standing somewhere: the **lead repo**.

1. The run starts in the lead repo; its declaration materializes the registries (sections 1–3).
2. The general registry carries the **component landscape** — a machine-readable catalog (`landscape/components.yml`: name, description, git URL, type per component). It is the repo directory.
3. Steps 02/03 map the story to affected components against the landscape; the human confirms the set at the gate. The manifest's repo list is **derived** from ticket + landscape + alignment, never guessed.
4. Step 00 clones the confirmed sibling repos into `.sdlc/repos/<component>/` inside the lead repo — same reasons as the context cache: trusted-folder-safe, self-contained, disposable — and reads **each repo's own declaration**, fail-closed per repo, adding its rows to the map.

Until that increment exists, multi-repo stories run as one pipeline per repo; the context layer already resolves per repo either way.

# Agentic SDLC Marketplace (generic)

An agent plugin marketplace holding the **form** of our delivery pipeline: the orchestrator, the delivery steps, and the artifact contracts. It installs in **Codex**, **Claude Code**, and **Copilot CLI / VS Code**. The skills and contracts are shared; each runtime uses its own small manifest surface. Everything here is **project-independent** and reusable in a second project.

**What does NOT belong here:** filled-in guidelines, real specs, concrete decisions, domain knowledge. That is content and belongs to the project (context registry / spec registry).

> **Check before every commit here:** *could a completely different project use this file unchanged?* No → wrong repo.

---

## Install

**Codex:**

```bash
codex plugin marketplace add we-make-specs/sdlc
codex plugin add sdlc@we-make-specs
codex plugin add sdlc-context@we-make-specs
```

For an already registered marketplace, run `codex plugin marketplace upgrade we-make-specs` before installing or updating. Start a new task after installation so the new skill catalog is loaded.

**Claude Code** — inside a session:

```
/plugin marketplace add <repo-url>
/plugin install sdlc@agentic-sdlc-marketplace
/plugin install sdlc-context@agentic-sdlc-marketplace
/reload-plugins
```

The same commands exist on the CLI (`claude plugin marketplace add …`, `claude plugin install …`). Refresh a registered marketplace with `/plugin marketplace update`.

**Copilot CLI:**

```bash
# register the marketplace
copilot plugin marketplace add https://github.com/we-make-specs/sdlc.git
copilot plugin marketplace list

# install the pipeline and context-registry plugins
copilot plugin install sdlc@agentic-sdlc-marketplace
copilot plugin install sdlc-context@agentic-sdlc-marketplace
copilot plugin list

# after the repo changed
copilot plugin update sdlc
copilot plugin update sdlc-context
```

The catalog carries the pipeline plugin `sdlc`. Install one copy per machine; two installed copies mean two competing step catalogs. Use `/sdlc:run` to start or resume a delivery.

The catalog also carries `sdlc-context`, the registry lifecycle plugin (`/sdlc-context:create`, `/sdlc-context:connect`, `/sdlc-context:update-index-and-crosslinks`). It installs alongside any pipeline copy.

The current source release pairs `sdlc` 0.7.3 with `sdlc-context` 0.3.2. Both include
namespaced command aliases and support delivery roots alongside code repositories.
The mirrored catalog records both versions;
the native catalog resolves the same plugin directories and reads their native manifests.
Existing deliveries retain their recorded layout when either plugin is updated.

**VS Code:** add the repo URL to `chat.plugins.marketplaces` in `settings.json`, then install from the Extensions view (`@agentPlugins`). Agent plugins are in preview — `chat.plugins.enabled` must be on.

> Plugins are cached. After editing anything here, re-run the install command.

---

## Layout

```
.claude-plugin/marketplace.json          # marketplace manifest — read by Claude Code
.github/plugin/marketplace.json          # same file — read by Copilot CLI / VS Code
.agents/plugins/marketplace.json         # marketplace manifest — read by Codex
plugins/sdlc/
  .claude-plugin/plugin.json             # plugin manifest — read by Claude Code
  .github/plugin/plugin.json             # same file — read by Copilot CLI / VS Code
  .codex-plugin/plugin.json              # native Codex plugin manifest
  workflow.yml                           # pipeline manifest: order, type, model tier, outputs
  artifact-definitions/                  # ARTIFACT CONTRACTS — one file per artifact
  skills/                                # the orchestrator + eleven steps
  commands/                              # namespaced aliases that load the shared skills
plugins/sdlc-context/
  .claude-plugin/plugin.json             # Claude plugin manifest
  .github/plugin/plugin.json            # byte-identical Copilot mirror
  .codex-plugin/plugin.json              # native Codex plugin manifest
  reference.md                          # registry format and lifecycle rules
  skills/                               # create, connect, update-index-and-crosslinks
  commands/                             # namespaced aliases that load the shared skills
```

Claude and Copilot manifests are mirrored because those runtimes look in different places. Codex has a native manifest with its required interface metadata. Everything else — the skills, contracts, scripts, and `workflow.yml` — is shared verbatim.

---

## Staying three-target

- **Claude/Copilot copies of a manifest must stay byte-identical.** Each runtime takes the first one it finds in its own lookup order; a copy left behind hands the two different catalogs without any error.
- **Codex keeps its native manifest valid.** Run `python3 <plugin-creator-skill>/scripts/validate_plugin.py plugins/sdlc`; `.codex-plugin/plugin.json` explicitly declares the shared `skills/` path and UI metadata.
- **Plugin skills stay format-neutral:** frontmatter is `name`, `description`, `argument-hint` only · siblings referenced relatively (`../../workflow.yml`), never via `${CLAUDE_PLUGIN_ROOT}` · no `hooks/` · no `.mcp.json`. Those are the only places the layouts genuinely differ — needing one means writing it once per format.
- Claude-only frontmatter (`context: fork`, `agent:`, `model:`, `allowed-tools:`, `effort:`) never belongs in `plugins/`.
- **No component paths in the Claude/Copilot `plugin.json` copies:** both runtimes discover `skills/` and `commands/` by convention. Codex's native manifest uses `"skills": "./skills/"` and does not load the command aliases. After touching a manifest, run both the Claude validator and the Codex validator.
- **Keep command aliases thin.** Shared skills keep their unprefixed names. Each alias uses `<plugin>:<skill>` and loads the matching `SKILL.md` with the user's arguments and context. Do not copy workflow instructions into aliases.

---

## The one rule that keeps this maintainable

**Steps do not define artifacts. Artifacts define themselves.**

Every artifact has exactly one contract in [`plugins/sdlc/artifact-definitions/`](plugins/sdlc/artifact-definitions/) — purpose, required sections, quality criteria, and the skeleton. A step declares only *which* artifacts it reads and writes, and points at the contract. That way there is one source of truth per artifact instead of the same structure being restated inside every step that touches it.

The same principle applies to project knowledge: a step declares *which* context-registry files it needs, never their content.

---

## The plugin

| | |
|---|---|
| **Skills** | `run` (the orchestrator) + `00-…` … `09-…` — one skill per pipeline step |
| **Artifacts** | 10 contracts covering the chain from manifest to decision log |
| **Manifest** | `workflow.yml` — step order, type (auto/collab/gate), model tier, outputs to validate |

See [`plugins/sdlc/skills/run/SKILL.md`](plugins/sdlc/skills/run/SKILL.md) for how the pipeline runs, and [`plugins/sdlc/artifact-definitions/README.md`](plugins/sdlc/artifact-definitions/README.md) for the artifact chain.

## Invoking it

The public command uses the plugin name as its prefix:

```
/sdlc:run <ticket-id | ticket-url | free-text description>
```

The eleven steps are `/sdlc:00-create-workspace` through `/sdlc:10-post-mortem`. Use one to redo a single stage; normally `run` sequences them for you. `workflow.yml` remains the source for step order. When renaming a skill, update its directory, frontmatter, workflow entry and command alias together.

Copilot CLI reads skill names directly, so an unprefixed `name: run` appears as `/run`.
The `commands/` aliases add `/sdlc:run` and the other qualified names while keeping the
bare commands available. Claude Code resolves each alias to the same command name as
its skill, without a second menu entry. Codex continues to load only the shared skills
and supplies its own namespace. Prefixing the shared skill names would double that
namespace in Codex.

After updating both plugins, start a new session. Check `copilot skill list` for
`sdlc:run`, the eleven prefixed steps, and all three `sdlc-context:` commands.

---

## Status

Early. The skills carry the full step logic; what is not yet proven is how much of the orchestration the runtime actually supports (separate contexts, chaining, per-step model selection). Until that is established, a human can run the pipeline by following `workflow.yml` step by step — that is a valid v1.

## Adding to this marketplace

1. Copy the closest existing skill in `plugins/sdlc/skills/` and rework it — the filled-in examples are the template.
2. Fill it in. Add `examples/good-input.md`, `examples/good-output.md`, and ideally `examples/anti-patterns.md` — the output example steers behaviour more than any prose.
3. Register the plugin in the Claude/Copilot mirrored marketplaces and the Codex marketplace if it is new.
4. Re-install locally and try it before opening a PR.

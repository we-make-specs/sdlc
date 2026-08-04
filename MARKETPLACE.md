# Agentic SDLC Marketplace (generic)

An agent plugin marketplace holding the **form** of our delivery pipeline: the orchestrator, the delivery steps, and the artifact contracts. It installs in **Claude Code** and in **Copilot CLI / VS Code** — the plugin format is shared between the three. Everything here is **project-independent** and reusable in a second project.

**What does NOT belong here:** filled-in guidelines, real specs, concrete decisions, domain knowledge. That is content and belongs to the project (context registry / spec registry).

> **Check before every commit here:** *could a completely different project use this file unchanged?* No → wrong repo.

---

## Install

**Claude Code** — inside a session:

```
/plugin marketplace add <repo-url>
/plugin install sdlc@agentic-sdlc-marketplace
/reload-plugins
```

The same commands exist on the CLI (`claude plugin marketplace add …`, `claude plugin install …`). Refresh a registered marketplace with `/plugin marketplace update`.

**Copilot CLI:**

```bash
# register the marketplace
copilot plugin marketplace add https://github.com/we-make-specs/sdlc.git
copilot plugin marketplace list

# install the pipeline plugin
copilot plugin install sdlc@agentic-sdlc-marketplace
copilot plugin list

# after the repo changed
copilot plugin update sdlc
```

The catalog carries the pipeline plugin `sdlc`. Install one copy per machine; two installed copies mean two competing step catalogs. The plugin name is the command prefix: `/sdlc:run`.

The catalog also carries `sdlc-context`, the registry lifecycle plugin (`/sdlc-context:create`, `/sdlc-context:connect`, `/sdlc-context:update-index-and-crosslinks`). It installs alongside any pipeline copy.

**VS Code:** add the repo URL to `chat.plugins.marketplaces` in `settings.json`, then install from the Extensions view (`@agentPlugins`). Agent plugins are in preview — `chat.plugins.enabled` must be on.

> Plugins are cached. After editing anything here, re-run the install command.

---

## Layout

```
.claude-plugin/marketplace.json          # marketplace manifest — read by Claude Code
.github/plugin/marketplace.json          # same file — read by Copilot CLI / VS Code
plugins/sdlc/
  .claude-plugin/plugin.json             # plugin manifest — read by Claude Code
  .github/plugin/plugin.json             # same file — read by Copilot CLI / VS Code
  workflow.yml                           # pipeline manifest: order, type, model tier, outputs
  artifact-definitions/                  # ARTIFACT CONTRACTS — one file per artifact
  skills/                                # the orchestrator + the ten steps
```

Each manifest exists twice because the two runtimes look in different places and Claude Code reads only `.claude-plugin/`. Everything else — the skills, the contracts, `workflow.yml` — is shared verbatim.

---

## Staying dual-target

- **Both copies of a manifest must stay byte-identical.** Each runtime takes the first one it finds in its own lookup order; a copy left behind hands the two different catalogs without any error.
- **Plugin skills stay format-neutral:** frontmatter is `name`, `description`, `argument-hint` only · siblings referenced relatively (`../../workflow.yml`), never via `${CLAUDE_PLUGIN_ROOT}` · no `hooks/` · no `.mcp.json`. Those are the only places the layouts genuinely differ — needing one means writing it once per format.
- Claude-only frontmatter (`context: fork`, `agent:`, `model:`, `allowed-tools:`, `effort:`) never belongs in `plugins/`.
- **No component paths in `plugin.json`** — both runtimes discover `skills/` by convention, and the explicit syntaxes are not interchangeable (Claude Code rejects `"skills": "skills/"` and wants an array of `./`-prefixed paths). After touching a manifest, run `claude plugin validate ./plugins/sdlc`; the `category` warning is known and harmless — Copilot uses the field, Claude ignores it.

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

The plugin name is the command prefix and the skill's frontmatter `name` is the rest, so the everyday entry point is short:

```
/sdlc:run <ticket-id | ticket-url | free-text description>
```

The ten steps are `/sdlc:00-ensure-workspace` … `/sdlc:09-merge` — reach for one only to redo a single stage; normally `run` sequences them for you. Neither the skill names nor the numbers are repeated inside the skills: `workflow.yml` is the single source for step order, so renaming a step means editing it there and in that skill's frontmatter, nowhere else.

---

## Status

Early. The skills carry the full step logic; what is not yet proven is how much of the orchestration the runtime actually supports (separate contexts, chaining, per-step model selection). Until that is established, a human can run the pipeline by following `workflow.yml` step by step — that is a valid v1.

## Adding to this marketplace

1. Copy the closest existing skill in `plugins/sdlc/skills/` and rework it — the filled-in examples are the template.
2. Fill it in. Add `examples/good-input.md`, `examples/good-output.md`, and ideally `examples/anti-patterns.md` — the output example steers behaviour more than any prose.
3. Register the plugin in **both** marketplace manifests if it is new — `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json`, kept identical.
4. Re-install locally and try it before opening a PR.

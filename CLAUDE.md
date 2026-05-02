# Agentic SDLC - root instructions

This repo is an agent plugin marketplace for agentic software delivery. It holds the generic pipeline (the `sdlc` plugin) and the context-registry lifecycle tooling (the `sdlc-context` plugin), and it installs into both Claude Code and Copilot / VS Code. Everything here is project-independent: project knowledge lives in a context registry, never in these plugins.

## Map

- `plugins/sdlc/` - the pipeline: `/sdlc:run` (orchestrator) + `/sdlc:00-...` ... `/sdlc:09-...` (one skill per step), `artifact-definitions/` (one contract per artifact), `workflow.yml` (step order, type, model tier, outputs), and the context binding (`context-protocol.md`)
- `plugins/sdlc-context/` - registry lifecycle plugin: `create` scaffolds a registry, `connect` declares registries in a project repo, `update-index-and-crosslinks` keeps indexes, links, and crosslinks current
- `.claude-plugin/` + `.github/plugin/` - the two marketplace manifests, one per runtime
- `README.md` - the concept, the pipeline, and how to install and use it
- `MARKETPLACE.md` - how the marketplace and the dual-runtime setup fit together

## Rules

- **Separation principle:** a skill never carries project knowledge, it points at the registry. The binding runs the other way: registry articles name the steps they reach (`applies-to:`), repos name their registries (`## Context Registries` in the root instruction file), and `plugins/sdlc/context-protocol.md` is the one place the mechanism is defined.
- **Skill names carry no prefix.** The command is `<plugin name>:<frontmatter name>`, so a skill called `sdlc-04-plan` inside plugin `sdlc` would read `/sdlc:sdlc-04-plan`. Step skills are named for their number alone (`04-plan`); the entry point is `run`.
- Navigate a registry via its index.md tables (two levels deep, no Last Read tracking); the format is defined in `plugins/sdlc-context/reference.md`.
- Verify facts against the code, never against older documents.
- Unfinished is marked `TODO:` - plausible filler is worse than a gap.

## Dual-target rule

The marketplace installs in **Claude Code** and in **Copilot CLI / VS Code**. Staying that way costs almost nothing, as long as two things hold.

**1. Mirrored files - edit every copy, keep them byte-identical.** Each runtime takes the first manifest it finds in its own lookup order, so a copy left behind silently hands the two runtimes different catalogs.

| Claude Code reads | Copilot CLI / VS Code read |
|---|---|
| `.claude-plugin/marketplace.json` | `.github/plugin/marketplace.json` |
| `plugins/<copy>/.claude-plugin/plugin.json` | `plugins/<copy>/.github/plugin/plugin.json` - in every pipeline copy |
| `CLAUDE.md` | `AGENTS.md` - at the repo root |
| `.claude/agents/sdlc-step.md` | `.github/agents/sdlc-step.agent.md` - the optional step-runner container profile |

The agent-profile pair is the one exception to byte-identical: the frontmatter dialects differ, the body must stay identical, and each file's header comment points at its mirror. The profiles are **optional**: the step-runner rules ship inside the run skill's delegation prompt, so the pipeline needs no extra files anywhere. Install a profile once per machine (`~/.claude/agents/` or `~/.copilot/agents/`) or per repo only for tool scoping or per-step model routing.

**2. Plugin skills stay format-neutral.** Inside `plugins/`: frontmatter is `name`, `description`, `argument-hint` only; no `${CLAUDE_PLUGIN_ROOT}`, reference siblings relatively (`../../workflow.yml`); no `hooks/`; no `.mcp.json`. Those are the only places the two plugin layouts genuinely differ, and needing one of them means writing it once per format.

Leave the component paths out of `plugin.json` entirely and let both runtimes discover `skills/` by convention. The path syntaxes are not interchangeable: Claude Code rejects `"skills": "skills/"` and requires an array of `./`-prefixed paths. Run `claude plugin validate ./plugins/sdlc` after touching a manifest; the `category` warning is known and harmless (Copilot uses the field, Claude ignores it).

Claude-only frontmatter (`context: fork`, `agent:`, `model:`, `allowed-tools:`, `effort:`) never belongs in `plugins/`.

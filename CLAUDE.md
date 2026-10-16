# Agentic SDLC - root instructions

This repo is an agent plugin marketplace for agentic software delivery. It holds the generic pipeline (the `sdlc` plugin) and the context-registry lifecycle tooling (the `sdlc-context` plugin), and it installs into Codex, Claude Code, and Copilot / VS Code. Everything here is project-independent: project knowledge lives in a context registry, never in these plugins.

## Map

- `plugins/sdlc/` - the pipeline: `/sdlc:run` (orchestrator) + `/sdlc:00-...` ... `/sdlc:10-...` (one skill per step), `artifact-definitions/` (one contract per artifact), scripts, and `workflow.yml` (step order, type, model tier, outputs)
- `plugins/sdlc-context/` - registry lifecycle plugin: `create` scaffolds a registry, `connect` declares registries in a project repo, `update-index-and-crosslinks` keeps indexes, links, and crosslinks current
- `.claude-plugin/` + `.github/plugin/` - byte-identical Claude/Copilot marketplace manifests
- `.agents/plugins/` + `plugins/*/.codex-plugin/` - native Codex marketplace and plugin manifests
- `README.md` - the concept, the pipeline, and how to install and use it
- `MARKETPLACE.md` - how the marketplace and the three-runtime setup fit together

## Rules

- **Separation principle:** a skill never carries project knowledge, it points at the registry. A repo declares its registries in a `## Context Registries` section in its root instruction file (written by `/sdlc-context:connect`); agents entering the repo follow that procedure, navigating each registry's `index.md` tables to the articles their task needs. The registry format is defined in `plugins/sdlc-context/reference.md`.
- **Shared skill names carry no prefix.** The entry point is `run`; step names match their directories. Codex and Claude Code add the plugin namespace, while Copilot CLI uses the frontmatter name directly. Each skill also has a thin `commands/<skill>.md` alias with `name: <plugin>:<skill>` for the same public command. Aliases only load the shared skill and pass through the request; keep workflow logic in `SKILL.md`.
- Navigate a registry via its index.md tables (two levels deep, no Last Read tracking); the format is defined in `plugins/sdlc-context/reference.md`.
- Verify facts against the code, never against older documents.
- Unfinished is marked `TODO:` - plausible filler is worse than a gap.

## Three-target rule

The marketplace installs in **Codex**, **Claude Code**, and **Copilot CLI / VS Code**. The skills remain shared; manifests follow each runtime's contract.

**1. Claude/Copilot mirrored files - edit every copy, keep them byte-identical.** Each runtime takes the first manifest it finds in its own lookup order, so a copy left behind silently hands the two runtimes different catalogs.

| Claude Code reads | Copilot CLI / VS Code read |
|---|---|
| `.claude-plugin/marketplace.json` | `.github/plugin/marketplace.json` |
| `plugins/<copy>/.claude-plugin/plugin.json` | `plugins/<copy>/.github/plugin/plugin.json` - in every pipeline copy |
| `CLAUDE.md` | `AGENTS.md` - at the repo root |
| `.claude/agents/sdlc-step.md` | `.github/agents/sdlc-step.agent.md` - the optional step-runner container profile |

The agent-profile pair is the one exception to byte-identical: the frontmatter dialects differ, the body must stay identical, and each file's header comment points at its mirror. The profiles are **optional**: the step-runner rules ship inside the run skill's delegation prompt, so the pipeline needs no extra files anywhere. Install a profile once per machine (`~/.claude/agents/` or `~/.copilot/agents/`) or per repo only for tool scoping or per-step model routing.

Codex's `.codex-plugin/plugin.json` is not a mirror: it explicitly declares `"skills": "./skills/"` and required interface metadata. The Codex marketplace lives at `.agents/plugins/marketplace.json`.

**2. Plugin skills stay format-neutral.** Inside `plugins/`: no `${CLAUDE_PLUGIN_ROOT}`, reference siblings relatively (`../../workflow.yml`); no runtime-specific hooks or MCP configuration. Runtime-specific metadata belongs in that runtime's manifest.

Leave component paths out of the Claude/Copilot `plugin.json` copies and let those runtimes discover `skills/` and `commands/` by convention. Codex's native manifest uses its own accepted `./skills/` path and does not load the command aliases. After manifest changes, run `claude plugin validate ./plugins/sdlc` and the plugin-creator `validate_plugin.py plugins/sdlc`; the Claude `category` warning is known and harmless.

Claude-only frontmatter (`context: fork`, `agent:`, `model:`, `allowed-tools:`, `effort:`) never belongs in `plugins/`.

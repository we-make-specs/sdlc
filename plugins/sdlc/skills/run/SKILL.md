---
name: run
description: Drive a ticket or free-text brain dump through the agentic delivery pipeline — resume from the feature folder, invoke each step skill in order, validate its declared outputs, and stop wherever a human is required. Use when the user says "run the pipeline", "start the sdlc workflow", or names a ticket to deliver.
argument-hint: <ticket-id | ticket-url | free-text description>
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.4.0'
  tags: orchestration, pipeline, sdlc, workflow
---
<!-- prework:orchestration-design -->

# SDLC Orchestrator

---

## What this skill does

Runs the delivery pipeline defined in `workflow.yml`: determines the next step from what exists in the feature folder, invokes that step's skill, validates the outputs it declared, and hands control to the human at collaborative and gate steps. It sequences and validates — it never does step work itself, and it never approves anything.

---

## When to use this skill

- The user wants to deliver a ticket through the controlled pipeline
- The user says "run the pipeline", "continue the story", "resume where we left off"
- A feature folder exists and the user asks what happens next

## When NOT to use this skill

- The user wants a single step in isolation — invoke that step's skill directly
- The user wants a quick change without the pipeline — this is deliberate overhead, not a default

---

## Required inputs

| Input | Description | Required |
|---|---|---|
| Ticket or text | ticket ID, ticket URL, or a free-text description | yes, for a new run |
| — | for a resume, the current branch and feature folder are enough | — |

## Required context

- `../../workflow.yml` — step order, type, isolation, model tier, outputs to validate
- `../../artifact-definitions/README.md` — the artifact chain and its cross-cutting rules
- The repo's **`## Context Registries`** declaration (in its `AGENTS.md`) — how registry knowledge reaches steps; consulting it is each step's own duty, and the orchestrator's only part is grepping for the `Context loaded:` trace each step leaves.

---

## Workflow

1. **Resume or start.** Locate the feature folder: find the `00_manifest.state.md` under `docs/sdlc/features/**` whose `branch` matches the current branch — its `folder:` field is authoritative for the whole run. **Read `status:` first:** `blocked` → do not advance; present the unresolved Blockers entries with their escalation lines and stop — the run continues only after a human marks the blocker resolved. Otherwise, the first step whose declared `outputs` are missing is the next step. No separate state file — the folder is the state. If no manifest matches the current branch, this is a new run: begin at step 00. **Never take the feature-folder path from the kickoff prompt** — where a story comes from (a seed file, a ticket) is not where artifacts go.
2. **Announce the step** (number, name, type) so the run stays legible.
3. **Invoke the step skill** with ticket and branch context, using the model tier configured for it in `workflow.yml`.
   - Steps marked `isolation: subagent` run in a **fresh subagent context**: spawn one with the runtime's generic delegation mechanism (Claude Code: the Task tool · Copilot CLI: a task-tool subagent) and hand it the **step-runner prompt below**, its four slots filled. The step inherits nothing else — it rehydrates from disk, and that isolation is what the blinded review depends on.
   - An `sdlc-step` agent profile is an **optional container** for tool scoping and per-step model routing — when the runtime knows one (user-level `~/.claude/agents/` / `~/.copilot/agents/`, or repo-level), delegate into it, still sending the full step-runner prompt. No profile is required: the rules travel in the prompt, not the profile.
   - Steps marked `isolation: main` (collab, gate) run live in this session — never delegate a step a human takes part in.
4. **Validate.** After any step that declares `outputs` — auto or collab — check that every declared output exists **inside the manifest's `folder:`**. This is a file check, not a content judgment. Missing → stop and report; never silently continue. One grep-check of the same class: after any step with `.md` outputs, its first declared `.md` output contains a `Context loaded:` line. Absent → stop and report — the step skipped its context registries.
5. **Hand over for humans.** Gate steps present their briefing and wait for an explicit decision. Collab steps run **live in this session** — the orchestrator conducts them itself: announce the step and begin; in an unattended leg, stop there and ask the human to join. Collab quality depends on the session's model — when it is below the step's tier in `workflow.yml`, say so up front; the human can switch models or accept it, and a collab step's artifact write-up may be delegated to a fresh strong-tier subagent where the step's skill allows it.
6. **Report** after each step: step, outcome, artifacts written, what comes next.

### The step-runner prompt

Every subagent delegation carries this prompt verbatim, slots filled. It lives here and only here — it ships and updates with the plugin, so no repo or machine needs extra files for it.

```text
You execute one step of the SDLC delivery pipeline, alone, in a fresh context.

Step skill: <path to the step's SKILL.md>
Ticket: <ticket> · Branch: <branch> · Feature folder: <path>

1. Read the skill file completely and follow it exactly — its workflow, constraints,
   and success criteria are your entire job description.
2. Rehydrate only from disk: the feature folder's artifacts, whatever the skill
   names as required context, and the context registries the repo declares in its
   `## Context Registries` section — consulted per that procedure.
   You inherit nothing from the session that spawned you — that isolation is
   deliberate; do not ask it for more context.
3. Write only the artifacts the skill declares, per their contracts, inside the
   feature folder — never outside the working repository — and tick only your own
   manifest row.
4. Ask no human questions. Anything undecidable goes into the artifact the skill
   designates for open points, marked as such. If you are blocked, append a Blockers
   entry to the manifest (what is missing · needed from · blocking step · since ·
   a ready-to-forward escalation sentence), set `status: blocked`, and return the
   blocker as your outcome.
5. Report back: step, outcome, artifacts written, and the summary the skill's output
   contract asks for. Claim nothing you did not verify.
```

### Unattended runs (autopilot / headless)

An unattended runtime cannot answer permission prompts — a gated tool call fails closed, mid-step. Two rules keep that survivable:

1. **Preflight before step 00.** Verify with harmless probes that the run has what the steps will need: read/write inside the repo and the feature folder · the git command set (status, branch, checkout, add, commit, push) · the PR tool for steps 06–08 · build/test commands for step 06. Also verify the runtime lists exactly **one** installed sdlc-family plugin, this copy, `sdlc`; a second one (another installed copy of this pipeline, or a stale version) means two competing step catalogs answering the same intent. Anything missing → stop *before* starting, and name it.
2. **A denial is a blocker, not an obstacle.** On "permission denied / could not request permission": stop the run and report the exact tool, command, or path that needs pre-approval. Never route around a denial with a different tool — that trades a visible failure for an invisible gap.

How to pre-approve depends on the runtime:

- **Copilot CLI** — start the session **in the target repo** (file access defaults to the working directory and below). Pre-approve per run, e.g. `--allow-tool 'shell(git:*)' --allow-tool 'read' --allow-tool 'write'` (plus `--deny-tool` exceptions), or `--allow-all-tools` for a throwaway demo repo — or approve interactively once: per-location approvals persist in `~/.copilot/permissions-config.json`.
- **Claude Code** — permission rules in the repo's `.claude/settings.json` (`permissions.allow`, e.g. `Bash(git:*)`), or per run via `--allowedTools` / the permission-mode flags.

### When a human is needed

Before any request for a decision, give a short orientation:

```text
Current phase: <step number> / <name>
What I need from you: <the exact decision or information>
Why it matters: <the consequence for the run>
```

Then offer concrete options with a recommendation. Never "how should I proceed?".

---

## Output contract

- Artifacts written by the invoked step skills, in the feature folder
- A run report per step: which step, outcome, artifacts, next step
- No artifacts written by this skill itself

---

## Constraints and guardrails

- **Never approve a gate.** Gates are human decisions; ambiguous praise is not approval.
- **Never mutate the working tree.** The orchestrator reads state; it does not checkout, pull, fast-forward, or switch branches. Tree changes belong to step 00, inside its subagent.
- **Artifacts live in the feature folder, inside the working repository.** A path outside the repo root — a seed folder, another checkout — is invalid even when the kickoff prompt points there; stop and correct rather than write.
- **Never run a subagent step inline.** Executing it in this session leaks the orchestrator's context into the step; if the runtime offers no delegation mechanism, say so and let the human start the step in a fresh session instead.
- **Never skip a failed validation.** If outputs are missing, stop and say so — do not paper over it.
- **A blocker that is not in the manifest does not exist.** When a step reports one, verify the Blockers entry and `status: blocked` are on disk, like any declared output — failure must survive this session, because the next orchestrator may be a script or a CI job reading only the file.
- **Never resolve context.** Which registries the repo declares lives in its `## Context Registries` section; which articles a step reads is that step's own lookup. The orchestrator greps for the trace (`Context loaded:` lines) and nothing more — anything an orchestrator would have to *compute* belongs in a step or in a file, or the next orchestrator (a script, a CI job) has to reimplement it.
- **Stay thin.** Carry only ticket, branch, and folder. All real content lives on disk; once a step returns, its artifact is the record.
- **Do not do step work.** If a step fails, report it — do not finish the job yourself.
- **Respect skippable.** A step marked skippable may be skipped when clearly irrelevant — say so and why.

---

## Success criteria

- [ ] Every step announced before it runs
- [ ] Every auto step's outputs validated before advancing
- [ ] Each `.md`-producing step's `Context loaded:` line verified — by grep, never by resolving anything
- [ ] Both gates stopped for an explicit human decision
- [ ] A resumed run continued at the correct step without redoing finished work
- [ ] Every `isolation: subagent` step ran in a fresh context, not inline, carrying the step-runner prompt
- [ ] Unattended: the preflight ran before step 00, and every denial stopped the run naming the exact missing approval
- [ ] Failures surfaced with their cause, not worked around

---

## Model routing

`workflow.yml` assigns a model tier per step (`strong` / `standard` / `fast`), mapped to concrete models in one place. Rationale: analysis, research, planning, and review benefit from the strongest model; implementation against a precise plan works with a mid-tier one; mechanical steps run cheap.

How a tier is applied depends on the runtime. Now that AUTO steps run as subagents, the natural mechanism is the per-agent model override both runtimes offer (Claude Code: `model:` in the agent definition · Copilot: the custom-agent / SDK model field); failing that, a `--model` flag, or the orchestrator naming the tier so the human selects it. **Not yet verified for our runtimes** — see the capability research task.

---
name: run
description: Drive a ticket or free-text brain dump through the agentic delivery pipeline — resume from the feature folder, invoke each step skill in order, validate its declared outputs, and stop wherever a human is required. Use when the user says "run the pipeline", "start the sdlc workflow", or names a ticket to deliver.
metadata:
  owner: Markus-Arndt
  author: '@Markus-Arndt'
  version: '0.7.2'
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
| Existing delivery | selected manifest, delivery directory, or ticket root | for a resume |

## Required context

- `../../workflow.yml` — step order, type, isolation, model tier, outputs to validate
- `../../artifact-definitions/README.md` — the artifact chain and its cross-cutting rules
- The workspace and component **`## Context Registries`** declarations, or settled inputs
  for a new root. Each step reads the relevant registry articles; the orchestrator passes
  the declarations and checks the `Context loaded:` trace.

---

## Workflow

1. **Resume or start.** Use the catalog's [workspace discovery and path rules](../../artifact-definitions/README.md#finding-an-existing-delivery), including a selected ticket root's `delivery/` and existing in-repo layouts. Do not confuse a notes repository with a component, or an input-file path with a workspace selection. Ambiguous matches stop for a location; they never trigger a new run. Keep an existing manifest's paths. **Read `status:` first:** `blocked` means present the unresolved Blockers entries and stop until the missing input is supplied or the human resolves the blocker. On a schema-version-1 workspace, run `scripts/migrate_state_070_to_071.py` once for its decision/review states before selecting the next action. This preserves exact backups and reopens approval; report that plainly and never hand-convert state. Otherwise select the next action with the three questions below. Only a confirmed new delivery begins at step 00.
2. **Settle kickoff inputs.** Reuse the user's selected ticket root, component sources, base refs, registry entries and entry-file choice. For a new ticket root, propose the catalog layout with `AGENTS.md`; ask only for missing or conflicting choices, not for preferences already supplied. Collect the three delivery-profile choices from the manifest contract (PR audience, review placement, questioning mode); use its defaults when no preference is given. In an unattended run, missing root/source choices are blockers. Pass the settled inputs to step 00, which owns cloning, branches and setup writes. Never re-ask or relocate a delivery on resume.
3. **Announce the step** (number, name, type) so the run stays legible.
4. **Invoke the step skill** with ticket and branch context, using the model tier configured for it in `workflow.yml`. Steps 06 to 09 additionally receive the selected package ID (implicit when the plan has one package).
   - Steps marked `isolation: subagent` run in a **fresh subagent context**: spawn one with the runtime's generic delegation mechanism and hand it the **step-runner prompt below**, with its paths and inputs resolved. The step rehydrates from its declared inputs; independent review remains blind to implementation framing.
   - An `sdlc-step` agent profile is an **optional container** for tool scoping and per-step model routing — when the runtime knows one (user-level `~/.claude/agents/` / `~/.copilot/agents/`, or repo-level), delegate into it, still sending the full step-runner prompt. No profile is required: the rules travel in the prompt, not the profile.
   - Steps marked `isolation: main` (collab, gate) run live in this session — never delegate a step a human takes part in.
5. **Validate.** Check every declared output inside the resolved manifest directory, expanding `<package-id>` for the selected package. Missing outputs stop the run. Run the producing skill's validators for JSON state; existence alone is insufficient. Verify the `Context loaded:` trace in each step's first `.md` output, including a newly created step-00 manifest. Legacy manifests need no trace retrofit on resume. After new setup, also verify the root/folder round trip, component identities and bases, and phase directories. A source snapshot is valid only with provenance and unresolved gaps recorded; it is not evidence that live ticket lookup succeeded.
6. **Hand over for humans.** Gate steps present their briefing and wait for an explicit decision. The review surface follows what is reviewed: questions/specifications use document annotation when selected; step 08 uses the actual PR diff or explicit approval in chat after the human reviews it. `questioning` does not select a PR review mode. Collab steps run live in this session; in an unattended leg, stop for the human. When the session is below the configured model tier, say so; the human can switch or accept it. Delegate a collab artifact write-up only where that step permits it.
7. **Report** after each step: step, outcome, artifacts written, what comes next.

### Step 07: independent, risk-scaled review

Step 07 is one pipeline step but may use two, three, or four fresh roles. Before review, record the
package base, immutable implementation commit, and exact step-06 full-check evidence when available.
Then delegate only the roles required by `skills/07-review/SKILL.md`:

1. **reviewer** — writes evidence-backed findings only; validate with `--phase findings`;
2. **evidence checker** — independently marks each finding `VALID`, `NOT_A_PROBLEM`,
   `PARTLY_RIGHT`, or `ASK_HUMAN`, assigns its cost/risk path, and groups compatible corrections into
   one trial fix; validate with `--phase checked`;
3. **trial-fix builder** — only for `LIGHT` or `FULL`; builds the grouped trial from the immutable
   implementation commit and runs targeted checks;
4. **final checker** — only when a trial exists; independently compares it with the original, selects
   at most one safe improvement, and records one final full check; validate with `--phase closed`.

A `NO_CHANGE` review stops after the evidence checker and closes with the original plus exact step-06
full-check evidence, when reusable. `ASK_HUMAN` reopens one focused decision, marks only dependent
unmerged packages `needs-revalidation`, and stops without a PR or trial fix. Never send reviewer prose
to an implementer as a change order, let adjacent roles collapse into one, or create one trial per
comment by default. The orchestrator validates and sequences state; it does not decide whether a
finding is true.

### Selecting the next action

Three questions, in order, every time the orchestrator decides what happens next:

1. **Is a shared artifact missing or unapproved?** Research, questions, breakdown, agreement, target solution, scenarios, plan: the first step whose declared outputs are missing, or whose gate has not passed, runs next — exactly the old linear walk. Steps 00 to 05 run once for the whole delivery.
2. **Otherwise, is a package ready?** Ready means: every prerequisite package merged, no unresolved readiness gate, no `needs-revalidation` mark. Run the tail (06 implement, 07 review, 08 gate, 09 merge) for that one package, then update its ledger row and re-evaluate. Packages execute sequentially, in plan order; with one package this is byte-for-byte the old behavior, which is why there is no second mode.
3. **Otherwise, stop and name what everything is waiting on:** a human decision, an unmerged prerequisite, an unmet release gate — with the exact ledger rows and escalation lines.

Two safety rules on top:

- **Revalidation.** When a shared decision changes after packages were planned (an amendment, a corrected agreement), mark every unmerged package that relied on it `needs-revalidation` in the work-package ledger, and question 1 applies again — the affected shared step reopens. The mark clears when the package's plan section is re-checked against the amended decision and its Status records that.
- **Completion.** A package merge never marks the delivery done. `status: done` requires every non-conditional package merged and the delivery-level scenarios satisfied.

### The step-runner prompt

Every subagent delegation carries this prompt, slots filled. For step 00, the feature
folder is the proposed location and the component list may include verified remotes to
clone; pass all settled kickoff inputs. Later steps use the manifest's resolved paths.

```text
You execute one step of the SDLC delivery pipeline, alone, in a fresh context.

Step skill: <path to the step's SKILL.md>
Ticket: <ticket> · Branch: <branch> · Feature folder: <path>
Workspace root: <path> · Component repositories: <resolved paths or setup sources>

1. Read the skill file completely and follow it exactly — its workflow, constraints,
   and success criteria are your entire job description.
2. Rehydrate from the declared inputs: the feature folder's artifacts (or supplied
   seed material for step 00), the skill's required context, and the workspace and
   component context declarations. Read each entry file explicitly; changing a
   shell directory does not prove its instructions were loaded.
   You inherit nothing from the session that spawned you — that isolation is
   deliberate; do not ask it for more context.
3. Write artifacts inside the resolved feature folder and update only your own
   manifest ledger rows. Run artifact validators there; run Git/build commands
   inside the declared component. Source edits, setup writes and review trials
   are allowed only where the step's contract authorizes them. Keep input files
   unchanged and external delivery artifacts out of component commits.
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

1. **Preflight before step 00.** Verify with harmless probes the paths and tools needed now: access to the selected root and components, Git and clone access for missing components, and readable supplied input. Check PR/build tools when their steps need them; do not require a build command before the code repository exists. Verify that exactly one installed pipeline copy answers the step names. Missing requirements stop the run with their names.
2. **A denial is a blocker, not an obstacle.** On "permission denied / could not request permission": stop the run and report the exact tool, command, or path that needs pre-approval. Never route around a denial with a different tool — that trades a visible failure for an invisible gap.

How to pre-approve depends on the runtime:

- **Copilot CLI:** start in the selected workspace root so its delivery folder and nested
  components are in scope. Verify access separately for explicitly selected components
  elsewhere. Pre-approve the required paths and commands through the host's permission
  controls; per-location approvals persist in `~/.copilot/permissions-config.json`.
- **Claude Code** — permission rules in the repo's `.claude/settings.json` (`permissions.allow`, e.g. `Bash(git:*)`), or per run via `--allowedTools` / the permission-mode flags.

### Unavailable integrations and slow steps

These rules apply in interactive and unattended runs. Try a required integration once
with a bounded timeout. If it is unavailable, report the failing integration and use the
step's documented supplied-input path where one exists. Otherwise record a blocker. Do
not silently retry on every step, call a fallback a live verification, or change global
connection settings. A fresh session without an optional failing integration may be
needed; use the host's supported controls rather than inventing a bypass.

When a step stalls, inspect available timestamps before changing model tiers or reducing
research scope. Separate model-call time, tool execution, startup and gaps between calls.
Repeated gaps after completed tools can come from runtime tool-catalog refreshes even
when the step never calls that integration. Report matching timeout evidence and the
needed host recovery; a prompt cannot repair a runtime retry loop. Restrict delegated
tools to the step's needs when the host supports it, but verify that this also prevents
unwanted connections before claiming it fixes latency. Keep runtime-specific settings
out of the shared plugin. A blocked step returns its existing artifacts and blocker;
never invent completed work to escape a timeout.

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
- **Delegate repository mutations.** Step 00 owns checkout preparation; implementation,
  review trials and merging stay with their designated steps. The orchestrator does not
  clone, switch branches or repair a failed step itself.
- **Artifacts live in the resolved feature folder.** It may be outside component
  repositories. Keep the catalog's path bases, input protection and resume rules; never
  substitute the current working directory or derive placement from repository count.
- **Never run a subagent step inline.** Executing it in this session leaks the orchestrator's context into the step; if the runtime offers no delegation mechanism, say so and let the human start the step in a fresh session instead.
- **Never skip a failed validation.** If outputs are missing, stop and say so — do not paper over it.
- **A blocker that is not in the manifest does not exist.** When a step reports one, verify the Blockers entry and `status: blocked` are on disk, like any declared output — failure must survive this session, because the next orchestrator may be a script or a CI job reading only the file.
- **Pass declarations, not invented context.** Kickoff supplies registry entries and
  entry-file choices to setup. Each step reads the applicable root/component declarations
  and selects its own articles; the orchestrator verifies the recorded trace.
- **Stay thin.** Carry ticket, selected paths, component sources and settled kickoff
  choices. Once a step returns, its artifact is the record.
- **Do not do step work.** If a step fails, report it — do not finish the job yourself.
- **Respect skippable.** A step marked skippable may be skipped when clearly irrelevant — say so and why.

---

## Success criteria

- [ ] Every step announced before it runs
- [ ] Every auto step's outputs validated before advancing
- [ ] Each `.md`-producing step's context trace verified, including new setup manifests
- [ ] New ticket-root setup and legacy resume use the same explicit path contract
- [ ] Offline ticket input is labeled, and repeated integration failures are surfaced
- [ ] Both gates stopped for an explicit human decision
- [ ] A resumed run continued at the correct step without redoing finished work
- [ ] Package-tail steps carried the selected package ID and updated only that package's rows
- [ ] `status: done` was set only per the completion rule, never by a package merge
- [ ] Every `isolation: subagent` step ran in a fresh context, not inline, carrying the step-runner prompt
- [ ] Unattended: the preflight ran before step 00, and every denial stopped the run naming the exact missing approval
- [ ] Failures surfaced with their cause, not worked around

---

## Model routing

`workflow.yml` assigns a model tier per step (`strong` / `standard` / `fast`), mapped to concrete models in one place. Rationale: analysis, research, planning, and review benefit from the strongest model; implementation against a precise plan works with a mid-tier one; mechanical steps run cheap.

How a tier is applied depends on the runtime. Now that AUTO steps run as subagents, the natural mechanism is the per-agent model override both runtimes offer (Claude Code: `model:` in the agent definition · Copilot: the custom-agent / SDK model field); failing that, a `--model` flag, or the orchestrator naming the tier so the human selects it. **Not yet verified for our runtimes** — see the capability research task.

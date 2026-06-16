# Agentic SDLC

An architecture for agentic software delivery. Instead of treating an AI model as an
autocomplete that a developer babysits, this project runs delivery as a controlled,
multi-stage workflow in which agent sessions and humans take turns. Every stage has a
defined input and a defined output, and nothing moves forward until that output meets
its criteria.

The pipeline ships as a plugin for two agent runtimes: Claude Code and GitHub Copilot
(CLI and VS Code). The same skills run unchanged in both.

## Why this exists

Most "AI in the SDLC" work stops at code completion. That leaves the hard parts, the
understanding, the design decisions, the review, either unassisted or buried inside a
single long chat that no one can audit later.

This project takes a different position: the valuable output of software delivery is
not the chat, it is the trail of artifacts. A current-state analysis, an agreed target
design, test scenarios, a plan, a reviewed pull request. If each of those is a real
file with a known shape, then agents can produce them, humans can approve them, and the
next stage can build on them without re-reading a transcript.

## Core concepts

**Steps.** The atomic unit of work. Each step is a skill with one job: research the
current solution, analyze the story, write the plan, and so on. A step reads named
artifacts, does its work, and writes named artifacts.

**Workflows.** Steps composed into an ordered pipeline. The workflow declares the
order, which artifacts each step must produce, and who runs each step. The definition
lives in `workflow.yml`.

**The orchestrator.** What drives the workflow from one step to the next, validating
each step's output before moving on. Today the orchestrator is the agent CLI itself:
you run one command and it sequences the steps. The design does not depend on that. The
same workflow file and artifacts could be driven by a script or a CI job, because the
state lives on disk, not in a session.

**Context Registry.** Project knowledge that agents read: development guidelines,
architecture notes, domain language, testing conventions. It is plain Markdown in Git,
kept separate from the pipeline so the same generic pipeline can serve any project. A
repository declares which registries it uses in a `## Context Registries` section in its
root instruction file, and each step consults the parts it needs by navigating the
registry's index. The `sdlc-context` plugin's `connect` skill writes that declaration;
the registry format is defined in `plugins/sdlc-context/reference.md`.

**Specification Registry.** The set of artifacts the pipeline produces for a feature,
the filled-in chain from analysis through decisions. Each artifact type has one contract
in `plugins/sdlc/artifact-definitions/` that defines its purpose, required sections, and
quality criteria.

**Human surfaces.** The points where a person joins the loop, either to make decisions
alongside an agent or to approve before the work continues. These are first-class in the
workflow, not an afterthought.

## Kinds of step

Not every step is the same. The workflow marks each one with a type, and that type
decides whether an agent runs alone, a human joins in, or the pipeline stops for a
decision.

**Autonomous (auto).** An agent runs the step on its own, in a fresh context, reading
and writing artifacts. No human needed while it runs. Example: researching the current
solution, or writing the implementation plan.

**Interactive (collab).** A human and an agent work the step together in the same
session. Used where judgment and discussion matter, like aligning on the target design
or merging the final pull request.

**Quality gate (gate).** The pipeline stops and waits for an explicit human approval
before going on. A gate makes no model judgment of its own; it presents what to review
and blocks until someone signs off. Example: approving the target solution before any
planning starts.

## The pipeline

Ten steps, from an incoming ticket to a merged pull request.

| # | Step | Type | Reads | Writes |
|---|------|------|-------|--------|
| 00 | ensure-workspace | auto | the ticket or free-text brief | `00_manifest.state.md` |
| 01 | research-current-solution | auto | `00_manifest` | `01_current-solution.research.md` |
| 02 | analyze | auto | `00_manifest`, `01_current-solution` | `02_questions.log.md` |
| 03 | align | collab | `00_manifest`, `01_current-solution`, `02_questions` | `03_alignment.log.md`, `03_target-solution.spec.md`, `03_test-scenarios.spec.md` |
| 04 | approve-target-solution | gate | `02_questions`, `03_alignment`, `03_target-solution`, `03_test-scenarios` | approval only |
| 05 | plan | auto | the step-03 artifacts and the research | `05_implementation.plan.md` (optionally a technical analysis) |
| 06 | implement | auto | `05_implementation.plan`, `03_target-solution`, `03_test-scenarios` | the code, a pull request, `decisions.log.md` |
| 07 | review | auto | `03_alignment`, `03_target-solution`, `03_test-scenarios` (not the plan) | inline comments and one verdict |
| 08 | review-pr | gate | the pull request, the agent review, `03_alignment` | approval only |
| 09 | merge | collab | `00_manifest`, `decisions.log` | the merged pull request |

A few things worth calling out. Step 03 is where a human and the agent settle the
design together, and step 04 refuses to continue until that design is approved. Step 07
reviews the pull request without reading the plan on purpose: an independent review that
inherits the implementer's framing is just a rubber stamp. Step 09 never merges on its
own; a person gives the word.

Each step names the artifacts it touches, and each artifact defines itself once in
`plugins/sdlc/artifact-definitions/`. Steps do not restate an artifact's structure, they
point at its contract. That keeps one source of truth per artifact instead of the same
shape copied into every step that reads it.

## Getting started

### Prerequisites

One of the two supported runtimes:

- Claude Code, or
- GitHub Copilot (CLI, or the VS Code extension with agent plugins enabled).

### Install

The pipeline is distributed as a plugin marketplace. You add the marketplace once, then
install the two plugins from it.

GitHub Copilot CLI:

```bash
# add the marketplace
copilot plugin marketplace add https://github.com/we-make-specs/sdlc.git

# install the pipeline and the context-registry tooling
copilot plugin install sdlc@agentic-sdlc-marketplace
copilot plugin install sdlc-context@agentic-sdlc-marketplace
```

Claude Code, inside a session:

```
/plugin marketplace add https://github.com/we-make-specs/sdlc.git
/plugin install sdlc@agentic-sdlc-marketplace
/plugin install sdlc-context@agentic-sdlc-marketplace
```

The plugin name is the command prefix. After install, the pipeline commands appear as
`/sdlc:...` and the registry commands as `/sdlc-context:...`.

Plugins are cached. If you change anything in this repo, re-run the install (or update)
command to pick it up.

### Use

Run the whole pipeline on a ticket or a free-text description:

```
/sdlc:run <ticket-id | ticket-url | free-text description>
```

The orchestrator resumes from the feature folder, runs each step in order, validates its
output, and stops wherever a human is required. You can also invoke a single step
directly, from `/sdlc:00-ensure-workspace` through `/sdlc:09-merge`, when you want to
redo one stage.

The `sdlc-context` plugin manages the knowledge side:

```
/sdlc-context:create                     # scaffold a new context registry
/sdlc-context:connect                    # declare which registries a repo uses
/sdlc-context:update-index-and-crosslinks
```

## What is in this repository

```
plugins/sdlc/            the pipeline: orchestrator, ten steps, artifact contracts, workflow.yml
plugins/sdlc-context/    the context-registry lifecycle plugin
.claude-plugin/          marketplace manifest read by Claude Code
.github/plugin/          marketplace manifest read by GitHub Copilot and VS Code
AGENTS.md / CLAUDE.md    root instructions for agents working in this repo
MARKETPLACE.md           how the marketplace and dual-runtime setup fit together
```

Everything here is generic and project-independent. Project knowledge and filled-in
specifications live in a context registry, never inside the pipeline.

## Two runtimes, one source

The marketplace installs in both Claude Code and GitHub Copilot. The two runtimes read
their manifests from different paths, so a handful of files are mirrored and must stay
identical between the two. The details are in `MARKETPLACE.md` and in the root
instruction files. If you only use one runtime, you can ignore the mirroring and just
install as shown above.

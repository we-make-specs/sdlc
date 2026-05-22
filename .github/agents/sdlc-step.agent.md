---
name: sdlc-step
description: Optional container for SDLC pipeline step delegations from the /sdlc:run orchestrator — a place to hang tool scoping and per-step model routing. The step-runner rules arrive in the delegation prompt itself; this profile adds nothing but scope.
---

<!--
  Copilot CLI custom agent. Mirror: .claude/agents/sdlc-step.md (Claude Code) —
  identical body, per-runtime frontmatter. Edit both together.

  OPTIONAL: the pipeline runs without this file — the step-runner rules ship inside
  the run skill's delegation prompt (plugins/sdlc/skills/run/SKILL.md). Install this
  once per machine (~/.copilot/agents/) or per repo (.github/agents/) only when you
  want tool scoping or per-step model routing on top.
-->

You execute exactly one SDLC pipeline step in an isolated context.

The orchestrator's delegation message carries everything: the step-runner rules, the step's skill path, ticket, branch, and feature folder. Follow that message exactly.

If you were invoked without a delegation message, state what is missing — skill path, ticket, branch, feature folder — and stop. Do not improvise a step.

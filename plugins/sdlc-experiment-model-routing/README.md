# SDLC Experiment: Model Routing

Experimental 0.1.0 fork of `sdlc` 0.7.1 at `55b2b1f`. The delivery stages,
artifact schemas, approval gates, validators and tests are retained.

**Start with [MODEL-ROUTING.md](MODEL-ROUTING.md).** It owns the recommended
models, role selection, kickoff, reporting, parallelism and fallback rules for
every entry point. Every skill links it before its step instructions.

Run `/sdlc-experiment-model-routing:run <ticket or description>`. Kickoff shows
the exact models and effort levels and asks once. Explicit choices take priority;
resuming uses the saved manifest profile. Each job announces its route and records
available runtime evidence in the manifest.

Use `/sdlc-experiment-model-routing:routing` at any time to inspect recommended,
requested and runtime-reported choices without starting a delivery.

Research can use two read-only Scouts followed by an Expert. Implementation and
review dependencies remain sequential. Optional mechanical work uses an existing
script or the Builder; required validation never becomes a model opinion.

Install and enable **one delivery plugin at a time**: use this plugin in place of
`sdlc` during the experiment. `sdlc-context` can stay enabled. Use the explicit
experimental prefix, including for direct step calls. Disable this plugin and
re-enable `sdlc` to return to the stable workflow.

The fork is self-contained because plugin caches cannot rely on sibling plugins.
For a focused review of behavioural changes:

```bash
git diff --no-index plugins/sdlc plugins/sdlc-experiment-model-routing
```

Exit code 1 is expected for that comparison. Unchanged scripts, schemas and tests
are intentional copies, not a second implementation. See the
[Scout model research](docs/scout-models.md). Actual model routing,
latency and savings require a run in the target client; static checks do not
establish them.

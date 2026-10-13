# Research dispatch

The entry caller acts as Coordinator under [MODEL-ROUTING.md](../MODEL-ROUTING.md),
both for `run` and a direct step-01 invocation. This is the Scout phase before
the research Expert starts, not a worker spawning more workers.

Use the manifest's story boundary to prepare two independent questions:

- Trace the affected execution flow.
- Locate relevant tests, configuration and existing rules.

Give each Scout the manifest path, distinct allowed source scope, resolved profile
and [Scout contract](scout.md). They consult source and applicable registries
themselves; do not read the whole corpus to prepare their jobs. Run them together
within the shared limit, or sequentially when only one slot is available. For a
narrow known lookup, skip the extra workers and record why.

Collect and close the Scouts before starting the Expert with the
`01-research-current-solution` skill. Pass their bounded evidence alongside its
required source artifacts. Do not write companion research files. The Expert
verifies source references, investigates remaining gaps, writes the single
research artifact and updates its ledger row. The Coordinator records Scout and
Expert completion in the routing log.

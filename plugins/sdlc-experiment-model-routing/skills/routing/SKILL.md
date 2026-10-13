---
name: routing
description: Show the experimental SDLC routing policy, saved model choices and recorded runtime evidence. Use when asked which models or worker roles the experiment uses.
metadata:
  version: '0.1.0'
---

# Show model routing

Read [MODEL-ROUTING.md](../../MODEL-ROUTING.md). If a feature manifest is available,
read its Model routing and Routing log sections. This command is read-only:
do not start a delivery, dispatch workers, change models, or ask for setup.

Show:

- The policy path and the current feature manifest, if one exists.
- Role, saved exact model and effort, and why that role is used.
- Explicit stage overrides and the worker limit.
- The most recent runtime-reported model for each role, or `unreported`.

Without a saved profile, show the recommendations clearly labelled as proposed.
Never present a recommendation, requested model or worker self-report as proof
of the runtime model. Changes are made through the shared kickoff procedure.

# Model routing

This is the shared routing policy for **every experimental skill and worker**.
Stages still own artifacts and approvals; roles select the model for a job inside
a stage. `workflow.yml` owns stage order, isolation and output checks. Change
routing here, never in `run`.

## Recommended profile

Resolve exact model IDs and supported effort levels from the current runtime.
These are candidates, not claims about the user's account. Explicit kickoff
choices override recommendations, including stage-specific overrides.

| Role | Preferred model | Effort | Work |
|---|---|---|---|
| Coordinator | Available Sonnet; otherwise GPT-6.1 Sol | medium | Human dialogue, dispatch, progress; never approves gates |
| Scout | GPT-6 Luna | low | Bounded, read-only source discovery; [Scout contract](model-routing/scout.md) |
| Builder | Available Sonnet; otherwise GPT-6.1 Sol | medium | Specified edits and mechanical work; [Builder contract](model-routing/builder.md) |
| Expert | Available Opus; otherwise GPT-6.1 Sol | high | Analysis, design, difficult debugging, independent review; [Expert contract](model-routing/expert.md) |

For Scout availability, propose GPT-6 Luna, then Haiku 5.5, GPT-5.6 Luna,
GPT-5.4 mini, then Haiku 4.5. Prefer low effort when supported; use Haiku 4.5's
supported default. Luna and Haiku 5.5 have equal listed base rates below 100k
input tokens; Luna keeps its base rate through 272k. This is a cost-oriented
starting order, not a speed ranking. Never infer a model generation from the
family name alone. [Evidence and comparison procedure](docs/scout-models.md).

| Stage or job | Owner / route |
|---|---|
| 00 workspace, 06 implementation | Builder |
| 01 research | Up to two Scouts, then one Expert; [shared research dispatch](model-routing/research.md) |
| 02 analysis, 05 planning | Expert |
| 03 alignment, 09 merge, 10 close-out | Coordinator in the human session; Expert support only where the step permits |
| 04 and 08 approval gates | Human; Coordinator presents, scripts validate |
| 07 reviewer, evidence checker, final checker | Separate Expert contexts, in the existing order |
| 07 trial-fix builder | Builder, only after checked findings |
| Optional mechanical task | Existing suitable script; otherwise Builder |

An owner can read a known function directly. Use a Scout for broad source
discovery, not for every file or tool call. A worker requesting another role
returns a bounded job request to the Coordinator; workers never spawn workers.
The Coordinator waits for or suspends the owner before dispatching that request.
Use the runtime's concurrency cap when exposed and track all active jobs. A
suspended owner must not consume a scarce worker slot needed by its helpers;
run sequentially rather than exceeding the supported limit.
Review contexts retain their existing blindness and source-access rules.

## Start, resume, and direct entry

1. Before step work, inspect available models, per-worker selection, effort and
   concurrency controls. Resolve exact IDs. A requested unavailable model needs
   a visible correction, not an invented ID or silent substitution.
2. Show **role / exact model / effort / reason**, the Coordinator's actual model,
   and the worker limit. Ask once: **Use recommendation / Change / Reuse saved**.
   Already supplied choices count as answers; ask only for unresolved choices.
   Headless runs require a saved or explicit complete profile; otherwise stop.
3. Step 00 records the resolved profile in the manifest's **Model routing**
   section. Before that, pass it explicitly in each delegation. On resume, reuse
   it and recheck availability; do not ask again unless a selection must change.
4. Directly invoked steps use the same policy and saved profile. If either is
   missing, return to the interactive caller for setup before doing step work.
   Existing workspaces gain only the routing sections after setup, preserving
   their original input, approvals and ledgers. The entry caller may append these
   routing sections; this is the only exception to `run` being read-only.
   The entry caller dispatches AUTO work in a fresh context with the resolved
   role, using the step-runner prompt in `skills/run/SKILL.md`. An already routed
   worker executes its assigned job without redispatching itself. Collaborative
   steps and human gates stay in the live session. If its model differs from the
   proposed Coordinator, show the actual model and let the user keep it or switch
   with the runtime's session control; never pretend to switch it through prose.

The [routing command](skills/routing/SKILL.md) only displays the policy and saved
records. It does not perform setup or dispatch work.

## Dispatch and visibility

Pass the selected model and effort through actual runtime selection controls,
not just prose. Use fresh context and include the role contract, job, allowed
paths, required evidence, and the resolved profile. Restrict Scout tools to reads
where supported. Otherwise disclose `read-only by instruction` and enforce the
Scout's no-write contract in its job; never claim a tool restriction was applied.
If isolated delegation or model selection is unavailable, stop and explain the
missing capability. Do not claim automatic routing worked.

Copilot's current CLI reference documents per-call model/effort selection and
custom-agent `model`, `reasoningEffort`, and `modelPolicy: required`. Auto can
override agent model choices: choose an explicit session model for this experiment.
Codex workers need fresh contexts when overriding models; Claude uses its native
per-agent model selection. Check the installed runtime's exposed controls first.
Do not create or change global agent settings as part of a delivery.

Before each job, announce `Routing: <stage/job> | <role> | <model> | <effort> | <why>`.
After it, report the runtime-reported model/effort, elapsed time, and usage when
available. Otherwise write `unreported`; a worker's self-description is not runtime
evidence. Record a mismatch and stop before the next job to correct the profile.
Missing telemetry is visible but does not itself block supported dispatch.
The Coordinator alone appends worker reports to the manifest's **Routing log**;
Scouts never write shared state. Buffer pre-manifest reports until step 00 returns.

## Parallelism and fallback

- Default: **two executing workers total per run**, including all nested work.
    - Start independent research Scouts together; close them before the Expert.
    - If the runtime cannot support two, run them sequentially and announce it.
    - Only read-only research runs in parallel in this version. Implementation,
      package sequencing, dependent review roles and human gates stay sequential.
- Give each Scout a different question and source scope. Return compact evidence,
  not transcripts or whole files. The Expert verifies critical source directly.
- Prefer existing scripts for deterministic work. If no optional helper exists,
  use the Builder with the same inputs, allowed outputs and acceptance checks.
  Do not require the user to write a new script before continuing.
- A **required validator, approval hash check, migration or test** never falls
  back to model judgment. Missing scripts, failed checks and permission denials
  keep the existing blocker behaviour. Optional render fallbacks must preserve
  the artifact contract; a prescribed deterministic renderer remains required.
- Escalate an uncertain Scout or failed Builder job with its evidence to the
  Expert once. Unresolved business decisions return to the human; repeated blind
  retries and automatic approval are never fallbacks.

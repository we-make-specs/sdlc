# Scout model choice

Sources checked on 2026-10-13. Recommendation: try **GPT-6 Luna with low effort**
for bounded source discovery when the runtime exposes it. This is a starting
hypothesis about suitability, not a measured speed or accuracy ranking.

| Candidate | Input / output per million tokens in Copilot, default tier | Why consider it |
|---|---|---|
| GPT-6 Luna | $0.10 / $0.50 | Focused tasks at the lowest listed rates among these candidates |
| Claude Haiku 5.5 | $0.10 / $0.50 | Main alternative; designed for latency-sensitive subagent work |
| GPT-5.6 Luna | $0.20 / $1.20 | Fallback if that is the Luna generation available |
| GPT-5.4 mini | $0.75 / $4.50 | Documented built-in Explore default |
| Claude Haiku 4.5 | $1.00 / $5.00 | Fast worker alternative, including native Claude environments |

Luna and Haiku 5.5 share the same base input/output and cache rates in Copilot.
Haiku 5.5 enters its higher price tier above 100k input tokens; Luna above 272k.
Keep Scout inputs bounded and start with low effort when the runtime supports it.
Use the supported default for Haiku 4.5. These are input/output rates, not a quote
for a completed job. Cached input,
cache writes, context tiers, generated reasoning, retries and hosting affect the
total. Availability depends on the account and runtime.

OpenAI describes Luna as suitable for focused, high-volume work. Anthropic
positions Haiku 5.5 for latency-sensitive extraction, routing and subagent work.
Haiku 4.5 remains an older fallback. Neither provider's description
source establishes which is faster for the same Scout task inside Copilot.
No comparable head-to-head Copilot latency result was established in this review.

The Scout contract keeps the job narrow: locate code and tests, return exact
source evidence, expose uncertainty. The Expert owns difficult interpretation.
A cheaper reader is only useful if its evidence remains accurate and complete.

Before changing the default, compare the available candidates on the same pinned
repository revision and representative questions: locate a symbol, trace a call
path, find relevant tests, and resolve a misleading name or absent match. Repeat
runs with equal tool access and output limits; report cold and warm runs
separately. Check references, missing critical evidence and unsupported claims.
Compare median elapsed time and total billed usage including retries. Disqualify
incorrect evidence before choosing the faster or cheaper candidate.

Sources:

- [Copilot model rates](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
- [Copilot built-in agents and model controls](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#custom-agents-reference)
- [GPT-6 Luna model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
- [Claude Haiku 5.5 model documentation](https://platform.claude.com/docs/en/models/haiku-5-5/overview)
- [Claude Haiku 4.5](https://www.anthropic.com/news/claude-haiku-4-5)

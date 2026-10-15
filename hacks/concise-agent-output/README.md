# Concise agent output

## Problem

Verification rules can become repetitive disclaimers: an agent answers a practical question, then adds an unnecessary defense of what it has not done. Workers can also spend output tokens narrating each step and explaining a completed implementation twice.

## Approach

- Conversation: answer the practical question, match its scale, and stop. Use short positive examples, not a growing list of forbidden phrases.
- Progress reports: state meaningful progress and merge remaining work with next steps. Keep detailed diagnostics in the actual report/checkpoint.
- Workers: give a concrete final-summary contract while preserving execution, tests, artifacts and genuine blockers.

Use [conversation.md](../../prompts/conversation.md) for user-facing agents and [worker-compact.md](../../prompts/worker-compact.md) for small bounded worker tasks. The worker prompt's language and length are tunable. For large repairs, require complete checkpoints separately. Do not truncate code or translation deliverables to fit a summary limit.

## What was tested

- User-facing prompts were compared with `gpt-6.1-sol`, medium reasoning, using practical questions, casual conversation, progress reports, correction feedback and a concrete failure scenario.
- A concrete report format plus an example worked better for progress notifications than a generic request to be concise.
- Conversation needed its own short-response examples rather than a progress-report template.
- Pi 1.1.0 / `glm-5.3-flash` / low thinking: two rounds of a small real bug fix. All four implementations passed the same eight unchanged tests.

These are exploratory examples, not a statistically powered model comparison. The distributed conversation prompt replaces private conversational examples with generic English examples; published numeric results are not a fresh evaluation of that adaptation.

## Pi output-token observations

Round 1, generic compact instruction:
- Baseline output: 344; candidate output: 332 (3.5% reduction).
- Total tokens: 11,948 versus 12,452.

Round 2, explicit three-line summary:
- Baseline output: 330; candidate output: 171 (48.2% reduction).
- Total tokens: 9,566 versus 9,773.
- Final visible text: 314 versus 62 characters.
- Both runs passed all eight tests; test files were unchanged; resulting implementation was identical.

Public-harness rerun:
- Baseline output: 280; candidate output: 197 (29.6% reduction).
- Total tokens: 9,493 versus 10,284.
- Both runs passed eight unchanged tests, created no unexpected workspace files, and produced identical implementation hashes.

`usage.output` was summed over assistant message-end events, including generated tool-call arguments. Total usage also reflects input and cache reads. Cache conditions differed; neither round establishes a billing saving. Provider usage counters may treat hidden reasoning differently, so record that separately when available.

## Wording and notification updates

The shared prompt includes a customizable Traditional Chinese wording preference: avoid「接續」in authored prose, using「繼續」、「之後」or「下一步」when natural. Exact quotations and identifiers remain unchanged. Remove this line if it does not suit your audience.

Progress formatting is optional, not a requirement to put headings on every reply. Report changed work, actual running work and a useful next action; skip empty reassurances and repeated delivery messages triggered by delayed internal notifications. Genuine failures remain visible.

These updates are checked for loading, preservation and prompt-size compatibility in local tests. They have not received a new model-output or token-usage benchmark; the historical numbers above apply only to the earlier tested prompts.

## Failure visibility

Conciseness must not turn "deployment failed" into "done". Test at least one genuine-blocker scenario alongside normal replies. Mention the concrete failure once; omit redundant disclaimers, not relevant evidence.

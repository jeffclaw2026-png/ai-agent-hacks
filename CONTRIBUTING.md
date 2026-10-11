# Contributing

Add a focused hack under `hacks/<name>/`. Include the problem, exact instructions, affected agent/runtime, installation and rollback, and limitations. Put reusable prompts under `prompts/`, runnable adapters under `integrations/`, and reproducible experiments under `benchmarks/`.

Before submitting:

- Use synthetic examples; do not paste private chats, credentials, hostnames, LAN addresses, personal paths, project data or agent session files.
- Record real results, including failures and token overhead. Label single samples and prompt adaptations honestly.
- Keep task inputs, model IDs, reasoning settings, tools and acceptance checks comparable in A/B experiments.
- Do not disable factual checks or hide meaningful failures to make an agent appear concise.
- Run the tests and privacy checker, then inspect your staged diff and commit author email. Automated scans are a supplement, not a privacy guarantee.

The starter scan is deliberately conservative. If it flags a harmless example, rewrite the example rather than adding broad allowlists. Do not commit raw benchmark logs; summarize only non-sensitive measurements.

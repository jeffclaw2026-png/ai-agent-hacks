# AI Agent Hacks

Small, practical improvements for AI agent workflows: prompts, integrations and reproducible experiments. Each hack should explain what changed, how to try it, how to undo it, and what the evidence actually shows.

## Available hacks

- **[Concise agent output](hacks/concise-agent-output/README.md)** — reduce defensive boilerplate and repetitive narration without hiding real failures. Includes a shared Hermes prompt plugin and a Pi worker token-usage benchmark.

## Quick start

### Hermes: shared conversational style

Keep this checkout at a stable path. Set `HERMES_HOME` to the profile you want to change, then:

```sh
mkdir -p "$HERMES_HOME/plugins"
ln -s "$PWD/integrations/hermes/shared-response-style" "$HERMES_HOME/plugins/shared-response-style"
hermes plugins doctor "$PWD/integrations/hermes/shared-response-style" --ci
hermes plugins enable shared-response-style --no-allow-tool-override
```

Run these from the repository root. If the destination already exists, inspect it rather than overwriting it. Repeat the one-time connection for each desired profile; all links then read the same `prompts/conversation.md`. Changes apply at a new session/prompt rebuild, not retroactively to an active conversation. No core patch, model change, tools or network hooks are added.

Rollback: `hermes plugins disable shared-response-style` in each affected profile. You can then remove only the symlink you created. Keep the checkout while profiles reference it.

See [integration notes](integrations/hermes/README.md) for scope and compatibility.

### Pi: compact worker summaries

Use your normal Pi command, adding:

```sh
pi --append-system-prompt "$PWD/prompts/worker-compact.md" --print 'YOUR TASK'
```

If Pi runs in a container, stage the prompt inside its existing project mount and use its container-visible path. Do not broaden the mount to your whole home just to share a prompt. The token-saving instruction is for worker summaries, not for truncating requested code, translations or evidence.

### Run the local checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/privacy_check.py
```

### Run a real Pi A/B benchmark

```sh
python3 benchmarks/pi_output_ab.py --pi-command pi --provider YOUR_PROVIDER --model YOUR_EXACT_MODEL_ID --thinking low
```

Or use `--pi-command /path/to/your/pi-worker`. Calls use your existing credentials and may consume provider quota. Nothing is installed or published by the benchmark. Outputs are placed in ignored `benchmark-runs/` directories. See [benchmark notes](benchmarks/README.md).

## Evidence, not promises

A small GLM worker experiment reduced output tokens from **330 to 171 (48.2%)**, while both implementations passed the same eight tests. **Total tokens increased**, and cache behavior differed. This is an example of less generated output, not a guarantee of lower total cost or faster execution. Public conversational examples are newly written generic examples, not private chat excerpts.

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). No credentials, private conversations, local infrastructure details or raw agent sessions belong in this repository.

MIT licensed. Independent community project; not an official Hermes or Pi integration.

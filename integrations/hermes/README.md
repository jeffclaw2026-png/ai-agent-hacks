# Hermes integration

The plugin uses `ctx.register_system_prompt_section`, positioned `after_memory`. It reads a shared prompt from this checkout. Per-profile symlinks are the one-time connection; they do not merge profiles, credentials or identities.

It was exercised against a Hermes runtime supporting that API with a 4000-character section cap. Discovery/registration, all configured profile renders, the cron constructor's prompt and persisted prompts from an actual delegated parent/child run were inspected. Runtime implementations vary: run `hermes plugins doctor` on your installation before enabling.

The plugin does not edit SOUL, replace tools, add hooks, change model settings or relax approval rules. Delegate children need this common prompt section because they do not simply inherit the parent's SOUL.

Enabling can hot-reload discovery, but prompt changes are deferred to a new session or normal prompt-rebuild boundary. Existing jobs retain their existing context. Do not terminate useful work just to apply style.

Official documentation: https://hermes-agent.nousresearch.com/docs/

## File layout

Keep the repository layout intact. The plugin resolves its real directory, then reads `prompts/conversation.md` in the repository root. Copying just the plugin directory without the prompt is unsupported. Symlinking the plugin from a stable checkout keeps all linked profiles on one file.

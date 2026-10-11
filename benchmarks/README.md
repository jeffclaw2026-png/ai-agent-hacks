# Pi A/B benchmark

`pi_output_ab.py` creates two isolated copies of a synthetic Python bug and eight unittest cases. A is baseline; B adds `prompts/worker-compact.md`. Both use your exact provider/model/thinking selection and the same task. It reproduces failure, executes Pi, independently runs tests, checks test integrity, compares implementations, and aggregates usage from JSON events.

Python 3.9+ and an already configured Pi CLI or isolated wrapper are required. No new dependencies or credentials are installed. Network/model calls consume your existing quota. A container wrapper must mount the current working directory as `/workspace` and provide Python 3. The prompt is passed as text so the container does not need a broader host mount.

Raw events can contain generated code, task context and errors. They stay in ignored `benchmark-runs/`. Do not publish them without manual review. The harness uses only synthetic inputs, but custom extensions may add context: inspect your Pi configuration before running.

Repeat experiments; alternate run order if assessing latency/cache effects. Output reduction alone is not a billing comparison. On timeout or failed acceptance, keep the run marked failed rather than calculating an apparent win.

# Preserve approved behavior

## Problem

An agent can explain the right product principle and still ship a different interaction. Extra confirmation dialogs, mandatory presets, cleared user input, and disabled options can look like sensible implementation details while changing what the owner approved. A green test suite can miss this if the implementer also redefines what the tests call correct.

## Findings and evidence limits

Recent small exploratory development exercises suggested these failure modes:

- Correct advice did not reliably predict correct implementation. Prompt variants and a model change were not sufficient safeguards against workflow drift.
- Initial interaction checks missed unsolicited confirmation steps and loss of existing input. Checks derived from the approved experience exposed those differences.
- A selector could preserve its underlying value while giving no useful visible feedback. A one-shot selection test also missed failure to reopen an already-focused search control after choosing an option.
- Fewer output tokens did not necessarily mean lower total usage; input and cache effects matter. The separate [output experiment](../concise-agent-output/README.md) records its actual measurements.

The first three observations summarize private exploratory work; raw runs and private applications are deliberately not published here. These are failure modes to test for, not a controlled study, a model ranking, or a measured reliability improvement. No fresh provider calls or model A/B experiments were run for this update. The public examples below are newly written and generic.

## A small, reusable approach

1. Agree the observable experience, including what must remain possible and what existing data must survive. A short in-chat card is enough for a small feature.
2. Give the worker that same contract. Engineering autonomy covers implementation choices, not new mandatory steps, removed capabilities, or different data behavior.
3. Keep acceptance owner-controlled. Workers may add regressions, but cannot rewrite the approved expectations to make their implementation pass. Explicit owner-approved changes may update the baseline; it is not frozen forever.
4. Check the actual artifact and the full interaction, including a second use. Inspect visible results, selected states, keyboard and pointer paths, persistence after reload, and affected failure handling.
5. For already-supported low-cost experimentation, distinguish **untested** from **known incompatible**. Representative tests describe evidence; they do not silently become a new allowlist. Apply justified safety, authorization and resource limits separately.
6. Stop when the agreed outcome works. Do not add a permanent BA/SA/QA agent organization, benchmark service, leases, hash gates or mandatory presets merely to carry out these checks.

## Generic acceptance example

For a reusable document-card editor, the owner might approve:

- Existing text and selected renderer survive editing unrelated fields and reopening the editor.
- A name search shows actual matching options; typing does not silently select one.
- The chosen option remains intact when filters hide it. The control can reopen by click and keyboard after a previous choice.
- Adding an optional style does not introduce a mandatory preset or confirmation dialog.
- A known incompatible renderer/style pair is rejected with its reason; a supported but untested pair is not disabled solely because it lacks a test run.
- A failed save retains the draft and reports the actual failure; it does not display success or destroy existing saved content.

These are example requirements, not an executed test of a real editor. Translate them into the project's actual browser/API/persistence tests before dispatch. A source-code regex, hidden select-option count, or an ARIA attribute alone is not proof of a working visible interaction.

## Try it

Copy [approved-behavior.md](../../templates/approved-behavior.md) into the project or paste it into the worker task. Fill in the real approved behavior; do not treat its example categories as a checklist to invent features. For a tiny known bug, reproduction plus a focused regression is sufficient.

The template is a task handoff, not a global system prompt. It installs no tool and changes no settings. Do not paste private project examples into this public repository.

## Undo or adapt

Stop attaching the template to future tasks; there is no runtime hook to remove. A revised product decision should explicitly update the relevant contract and tests, rather than bypassing them or preserving an obsolete interaction.

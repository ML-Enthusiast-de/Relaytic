# Slice 11G - Adaptive human onboarding and lightweight local semantic guidance

## Load-bearing improvement

Slice 11G is where Relaytic stops treating first-contact humans like disciplined CLI operators and starts behaving like a guided local product.

The goal is to make the onboarding flow resilient to messy human input:

- accept pasted dataset paths directly from chat
- capture objectives from plain language instead of rigid prompts only
- keep visible onboarding state across turns
- use a lightweight local semantic helper for bounded interpretation when it is available
- stay deterministic for validation, run creation, and final control decisions

## Human surface

- `relaytic mission-control chat`
- `relaytic mission-control launch --interactive`
- `relaytic mission-control show`
- `python scripts/install_relaytic.py --profile full --launch-control-center`
- `/state`
- `/reset`

## Agent surface

- `onboarding_chat_session_state.json`
- onboarding-aware mission-control payloads with captured data path, captured objective, next expected input, semantic-backend status, and run-start readiness
- one-command install payloads that report whether Relaytic requested and provisioned the lightweight local onboarding model

## Intelligence source

- deterministic path detection, file-existence validation, run creation, and state persistence
- bounded local semantic extraction for messy onboarding input
- the same mission-control artifact graph that already drives onboarding, capability, and handbook surfaces

The intended lightweight local baseline is a CPU-safe quantized Qwen 3 4B profile via `llama.cpp`, with graceful fallback to deterministic onboarding when that helper is unavailable.

## Fallback rule

If no local semantic backend is available:

- Relaytic must still accept direct dataset-path pastes
- Relaytic must still accept explicit objective text
- Relaytic must still keep visible onboarding state across turns
- Relaytic must still confirm before creating the first run

If a local semantic backend is available:

- Relaytic may use it only for intent extraction, path/objective capture, and natural clarifying questions
- Relaytic must still validate file paths, run directories, and launch decisions deterministically

## Required behavior

1. Mission-control chat must capture a pasted dataset path and ask for the missing objective naturally.
2. Mission-control chat must capture an objective without losing earlier onboarding state.
3. Mission-control chat must support natural messy first-turn input that combines a dataset hint and a goal.
4. Mission-control chat must show current captured onboarding state through `/state` and mission-control surfaces.
5. Mission-control chat must require explicit confirmation before creating the first run unless policy disables confirmation.
6. The suggested onboarding run directory must respect policy-configured defaults instead of hardcoding `artifacts/demo`.
7. The full one-line installer must attempt to provision the lightweight onboarding helper by default.
8. Canonical `policy:` configs and legacy top-level configs must both work for local semantic onboarding setup.

## Proof obligation

Slice 11G is acceptable only if:

1. one chat case proves Relaytic captures a dataset path and asks for the objective
2. one chat case proves Relaytic captures data plus objective and starts the first run after confirmation
3. one chat case proves messy human wording is rescued by the lightweight local semantic helper
4. one install case proves the full bootstrap requests onboarding-local-LLM setup

## Required outputs

- `onboarding_chat_session_state.json`
- updated onboarding cards in `mission_control_state.json`
- updated onboarding sections in `onboarding_status.json`
- install payloads that expose onboarding-local-LLM setup intent and results

## Tests

Slice 11G should not be considered complete without targeted tests that cover at least:

- one dataset-path capture case
- one objective capture plus confirmation case
- one local-semantic messy-input case
- one one-line-installer local-onboarding-LLM case

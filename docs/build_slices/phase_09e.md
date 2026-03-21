# Slice 09E - Communicative assist, guided navigation, and bounded takeover

## Status

Implemented in the current baseline.

Shipped surface:

- package boundary: `src/relaytic/assist/`
- public commands: `relaytic assist show`, `relaytic assist turn`, and `relaytic assist chat`
- current artifacts: `assist_mode.json`, `assist_session_state.json`, `assistant_connection_guide.json`, and `assist_turn_log.jsonl`

## Intent

Slice 09E is where Relaytic stops being understandable only through artifact inspection and becomes directly communicative for both humans and other agents.

This slice is successful only if Relaytic can:

- explain current state and next action in plain language grounded in the actual artifacts
- let a human or external agent jump back to a bounded stage without corrupting the run
- take over safely when the operator says “do it” or “I’m not sure”
- recommend local lightweight semantic-assist paths and local host-connection paths without making them mandatory

## Required Behavior

- assist must stay deterministic-first and fully local by default
- stage navigation must rerun the requested stage and refresh downstream artifacts coherently
- takeover must remain bounded, policy-aware, and artifact-visible
- assist must work for both humans and agents through the same turn contract
- local semantic lift must be optional rather than the control plane
- host-connection guidance must stay honest about local-only defaults, optional activation, and any public-HTTPS requirement for ChatGPT connectors

## Acceptance Criteria

Slice 09E is acceptable only if:

1. one run can explain itself through `relaytic assist show` and `relaytic assist turn`
2. one run can jump back to a bounded stage like `research` and refresh downstream artifacts
3. one run can accept “take over” and execute the next safe bounded step automatically
4. the same assist surface can tell the user how to stay local, use a lightweight local LLM, or connect Claude/Codex/OpenClaw/ChatGPT appropriately

## Required Verification

Slice 09E should not be considered complete without targeted tests that cover at least:

- one explanation turn
- one stage-navigation turn
- one takeover turn
- one interactive turn-capped assist chat flow
- one MCP/interoperability regression showing the assist surface is available to external agents

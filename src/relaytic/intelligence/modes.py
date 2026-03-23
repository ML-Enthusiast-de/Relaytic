"""Canonical intelligence-mode handling for routed semantic work."""

from __future__ import annotations

from typing import Final


MODE_NONE: Final[str] = "none"
MODE_LOCAL_MIN: Final[str] = "local_min"
MODE_ASSIST: Final[str] = "assist"
MODE_AMPLIFY: Final[str] = "amplify"
MODE_MAX_REASONING: Final[str] = "max_reasoning"

CANONICAL_MODES: Final[tuple[str, ...]] = (
    MODE_NONE,
    MODE_LOCAL_MIN,
    MODE_ASSIST,
    MODE_AMPLIFY,
    MODE_MAX_REASONING,
)

_MODE_ALIASES: Final[dict[str, str]] = {
    "": MODE_NONE,
    "off": MODE_NONE,
    "disabled": MODE_NONE,
    "deterministic": MODE_NONE,
    "deterministic_only": MODE_NONE,
    "none": MODE_NONE,
    "minimum_local": MODE_LOCAL_MIN,
    "minimum_local_llm": MODE_LOCAL_MIN,
    "minimum_local_semantic": MODE_LOCAL_MIN,
    "local_min": MODE_LOCAL_MIN,
    "assist": MODE_ASSIST,
    "advisory": MODE_ASSIST,
    "advisory_local_llm": MODE_ASSIST,
    "semantic_local_llm": MODE_ASSIST,
    "amplify": MODE_AMPLIFY,
    "semantic_amplify": MODE_AMPLIFY,
    "strong_local_llm": MODE_AMPLIFY,
    "max_reasoning": MODE_MAX_REASONING,
    "frontier": MODE_MAX_REASONING,
    "frontier_assisted": MODE_MAX_REASONING,
    "reasoning_max": MODE_MAX_REASONING,
}

_MODE_RANKS: Final[dict[str, int]] = {
    MODE_NONE: 0,
    MODE_LOCAL_MIN: 1,
    MODE_ASSIST: 2,
    MODE_AMPLIFY: 3,
    MODE_MAX_REASONING: 4,
}


def canonicalize_mode(value: str | None) -> str:
    """Map configured or legacy intelligence-mode labels into canonical modes."""

    normalized = str(value or "").strip().lower().replace("-", "_")
    return _MODE_ALIASES.get(normalized, MODE_ASSIST if normalized else MODE_NONE)


def mode_rank(mode: str | None) -> int:
    """Return a monotonic rank for one canonical intelligence mode."""

    return _MODE_RANKS.get(canonicalize_mode(mode), 0)


def clamp_mode(requested_mode: str | None, *, maximum_mode: str | None) -> str:
    """Clamp one requested mode to the highest policy-allowed canonical mode."""

    requested = canonicalize_mode(requested_mode)
    maximum = canonicalize_mode(maximum_mode)
    return requested if mode_rank(requested) <= mode_rank(maximum) else maximum


def highest_allowed_mode(*, allow_frontier_llm: bool, allow_max_reasoning: bool) -> str:
    """Resolve the strongest canonical mode currently allowed by policy."""

    if allow_max_reasoning:
        return MODE_MAX_REASONING
    if allow_frontier_llm:
        return MODE_AMPLIFY
    return MODE_ASSIST


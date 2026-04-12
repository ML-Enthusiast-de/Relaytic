"""Shared benchmark-status normalization helpers."""

from __future__ import annotations

from typing import Final


_PARITY_ALIASES: Final[dict[str, str]] = {
    "meets_or_exceeds_reference": "meets_or_beats_reference",
    "at_parity": "meets_or_beats_reference",
    "better_than_reference": "meets_or_beats_reference",
}

_REFERENCE_COMPETITIVE: Final[set[str]] = {"meets_or_beats_reference", "competitive"}
_REFERENCE_NEAR_COMPETITIVE: Final[set[str]] = {"near_parity"}


def normalize_benchmark_parity_status(value: str | None) -> str | None:
    """Return the canonical parity-status label used across Relaytic."""

    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return _PARITY_ALIASES.get(text, text)


def benchmark_is_reference_competitive(value: str | None, *, include_near: bool = True) -> bool:
    """Return whether a parity status is strong enough to count as competitive."""

    normalized = normalize_benchmark_parity_status(value)
    if normalized in _REFERENCE_COMPETITIVE:
        return True
    if include_near and normalized in _REFERENCE_NEAR_COMPETITIVE:
        return True
    return False


def benchmark_meets_or_beats_reference(value: str | None) -> bool:
    """Return whether a parity status means Relaytic met or beat the reference."""

    return normalize_benchmark_parity_status(value) == "meets_or_beats_reference"

"""Local baseline profile selection for Slice 09F routed intelligence."""

from __future__ import annotations

import os
import platform
from typing import Any

from relaytic.core.config import load_config
from relaytic.orchestration.runtime_policy import (
    RuntimePolicyError,
    apply_environment_overrides,
    load_runtime_policy,
)

from .modes import MODE_AMPLIFY, MODE_ASSIST, MODE_LOCAL_MIN, MODE_MAX_REASONING
from .models import (
    LOCAL_LLM_PROFILE_SCHEMA_VERSION,
    IntelligenceControls,
    IntelligenceTrace,
    LocalLLMProfileArtifact,
)


def build_local_llm_profile_artifact(
    *,
    controls: IntelligenceControls,
    config_path: str | None,
    generated_at: str,
    trace: IntelligenceTrace,
) -> LocalLLMProfileArtifact:
    """Resolve the current local baseline profile without making it authoritative."""

    try:
        config = load_config(config_path)
        runtime_policy = apply_environment_overrides(load_runtime_policy(config))
        selection = _select_profile_name(controls=controls, runtime_policy=runtime_policy)
        profile = runtime_policy.profiles[selection]
        status = "ok"
        summary = (
            f"Relaytic resolved local profile `{selection}` for semantic routing with provider "
            f"`{runtime_policy.provider}`."
        )
        profile_notes = _profile_notes(runtime_policy.provider, profile.cpu_only, profile.max_context)
        return LocalLLMProfileArtifact(
            schema_version=LOCAL_LLM_PROFILE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=status,
            provider=runtime_policy.provider,
            profile_name=selection,
            model=profile.model,
            cpu_only=profile.cpu_only,
            n_gpu_layers=str(profile.n_gpu_layers),
            max_context=profile.max_context,
            recommended_mode=_recommended_mode(runtime_policy.provider, profile.cpu_only, profile.max_context),
            profile_origin=_profile_origin(controls=controls, selected_profile=selection, runtime_policy=runtime_policy),
            hardware_snapshot=_hardware_snapshot(),
            notes=profile_notes,
            summary=summary,
            trace=trace,
        )
    except (RuntimePolicyError, OSError, ValueError) as exc:
        return LocalLLMProfileArtifact(
            schema_version=LOCAL_LLM_PROFILE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="unavailable",
            provider=None,
            profile_name=None,
            model=None,
            cpu_only=None,
            n_gpu_layers=None,
            max_context=None,
            recommended_mode=MODE_LOCAL_MIN if controls.minimum_local_llm_enabled else MODE_ASSIST,
            profile_origin="unavailable",
            hardware_snapshot=_hardware_snapshot(),
            notes=[f"Relaytic could not resolve a local semantic profile: {exc}"],
            summary="Relaytic could not resolve a concrete local semantic profile from current runtime settings.",
            trace=trace,
        )


def _select_profile_name(*, controls: IntelligenceControls, runtime_policy: Any) -> str:
    requested = (controls.minimum_local_llm_profile or "").strip()
    if controls.minimum_local_llm_enabled and requested and requested.lower() != "none":
        if requested in runtime_policy.profiles:
            return requested
    selected = runtime_policy.select_profile(prefer_cpu=controls.prefer_local_llm)
    return selected.name


def _profile_origin(*, controls: IntelligenceControls, selected_profile: str, runtime_policy: Any) -> str:
    requested = (controls.minimum_local_llm_profile or "").strip()
    if controls.minimum_local_llm_enabled and requested and requested.lower() != "none" and requested == selected_profile:
        return "minimum_local_llm_profile"
    if runtime_policy.default_profile == selected_profile:
        return "runtime_default_profile"
    return "runtime_fallback_profile"


def _recommended_mode(provider: str, cpu_only: bool, max_context: int) -> str:
    provider_key = str(provider).strip().lower()
    if provider_key in {"openai", "openai_compatible"}:
        return MODE_MAX_REASONING
    if cpu_only and max_context <= 4096:
        return MODE_LOCAL_MIN
    if cpu_only:
        return MODE_ASSIST
    return MODE_AMPLIFY


def _profile_notes(provider: str, cpu_only: bool, max_context: int) -> list[str]:
    notes = [f"Provider `{provider}` is currently bound to the selected semantic profile."]
    if cpu_only:
        notes.append("Profile is CPU-safe and suitable for lightweight local semantic help.")
    else:
        notes.append("Profile may benefit from GPU acceleration for stronger semantic passes.")
    notes.append(f"Profile advertises a maximum semantic context of approximately {max_context} tokens.")
    return notes


def _hardware_snapshot() -> dict[str, Any]:
    return {
        "cpu_count": os.cpu_count(),
        "machine": platform.machine() or None,
        "platform": platform.system() or None,
    }


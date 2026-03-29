"""Shared local semantic-backend discovery and JSON task execution."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from relaytic.core.config import load_config
from relaytic.orchestration.runtime_policy import (
    apply_environment_overrides,
    load_runtime_policy,
)

from .models import IntelligenceControls


@dataclass(frozen=True)
class AdvisoryResult:
    status: str
    payload: dict[str, Any] | None
    notes: list[str]
    latency_ms: float | None = None


@dataclass(frozen=True)
class LocalAdvisorConfig:
    provider: str
    model: str
    endpoint: str
    profile: str | None
    auth_token: str | None = None
    temperature: float = 0.0
    timeout_seconds: int = 120
    max_context: int = 4096
    endpoint_scope: str = "local"


@dataclass(frozen=True)
class BackendDiscovery:
    status: str
    requested_provider: str | None
    resolved_provider: str | None
    resolved_model: str | None
    endpoint: str | None
    endpoint_scope: str
    profile: str | None
    notes: list[str]
    advisor: "StructuredLocalAdvisor | None"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "requested_provider": self.requested_provider,
            "resolved_provider": self.resolved_provider,
            "resolved_model": self.resolved_model,
            "endpoint": self.endpoint,
            "endpoint_scope": self.endpoint_scope,
            "profile": self.profile,
            "notes": list(self.notes),
        }


class StructuredLocalAdvisor:
    """Narrow structured-JSON client for bounded semantic tasks."""

    def __init__(self, config: LocalAdvisorConfig) -> None:
        self.config = config

    def complete_json(
        self,
        *,
        task_name: str,
        system_prompt: str,
        payload: dict[str, Any],
    ) -> AdvisoryResult:
        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]
        provider = self.config.provider.lower()
        started = time.perf_counter()
        try:
            if provider == "ollama":
                raw_payload = {
                    "model": self.config.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_ctx": self.config.max_context,
                    },
                }
                response = _http_post_json(self.config.endpoint, raw_payload, timeout_seconds=self.config.timeout_seconds)
                content = ((response.get("message") or {}).get("content") or "").strip()
            else:
                headers: dict[str, str] | None = None
                if provider == "openai" and not self.config.auth_token:
                    return AdvisoryResult(
                        status="error",
                        payload=None,
                        notes=["OpenAI provider is configured without an API key."],
                    )
                if self.config.auth_token:
                    headers = {"Authorization": f"Bearer {self.config.auth_token}"}
                raw_payload = {
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": 1400,
                    "response_format": {"type": "json_object"},
                }
                response = _http_post_json(
                    self.config.endpoint,
                    raw_payload,
                    timeout_seconds=self.config.timeout_seconds,
                    headers=headers,
                )
                choices = response.get("choices") or []
                content = ((choices[0].get("message") or {}).get("content") or "").strip() if choices else ""
            parsed = _parse_json_object(content)
            if parsed is None:
                return AdvisoryResult(
                    status="error",
                    payload=None,
                    notes=[f"{task_name}: advisory returned non-JSON content."],
                    latency_ms=(time.perf_counter() - started) * 1000.0,
                )
            return AdvisoryResult(
                status="ok",
                payload=parsed,
                notes=[],
                latency_ms=(time.perf_counter() - started) * 1000.0,
            )
        except RuntimeError as exc:
            return AdvisoryResult(
                status="error",
                payload=None,
                notes=[f"{task_name}: {exc}"],
                latency_ms=(time.perf_counter() - started) * 1000.0,
            )


def discover_backend(
    *,
    controls: IntelligenceControls,
    config_path: str | None,
) -> BackendDiscovery:
    """Resolve the best available semantic backend without making it mandatory."""

    if not controls.enabled:
        return BackendDiscovery(
            status="disabled",
            requested_provider=None,
            resolved_provider=None,
            resolved_model=None,
            endpoint=None,
            endpoint_scope="local",
            profile=None,
            notes=["Intelligence is disabled by policy."],
            advisor=None,
        )

    normalized_mode = controls.intelligence_mode.strip().lower().replace("-", "_")
    if normalized_mode in {"", "none", "off", "disabled", "deterministic"}:
        return BackendDiscovery(
            status="deterministic_only",
            requested_provider=None,
            resolved_provider=None,
            resolved_model=None,
            endpoint=None,
            endpoint_scope="local",
            profile=None,
            notes=["Semantic amplification is disabled; Relaytic will use deterministic debate only."],
            advisor=None,
        )

    config = load_config(config_path)
    if "policy" in config and isinstance(config.get("policy"), dict):
        merged_config = dict(config["policy"])
        for key, value in dict(config).items():
            if key == "policy":
                continue
            if key not in merged_config:
                merged_config[key] = value
            elif isinstance(merged_config.get(key), dict) and isinstance(value, dict):
                merged_config[key] = {**dict(value), **dict(merged_config[key])}
        config = merged_config
    policy = apply_environment_overrides(load_runtime_policy(config))
    runtime_cfg = dict(config.get("runtime", {}))
    requested_provider = str(runtime_cfg.get("provider", policy.provider)).strip() or str(policy.provider).strip()
    endpoint = (
        os.getenv("RELAYTIC_ENDPOINT", "").strip()
        or os.getenv("C2S_ENDPOINT", "").strip()
        or _resolve_endpoint(policy.provider, runtime_cfg)
    )
    endpoint_scope = "remote"
    if endpoint.startswith("http://127.0.0.1") or endpoint.startswith("http://localhost"):
        endpoint_scope = "local"
    if endpoint.startswith("https://127.0.0.1") or endpoint.startswith("https://localhost"):
        endpoint_scope = "local"
    if endpoint_scope == "remote" and not controls.allow_frontier_llm:
        return BackendDiscovery(
            status="blocked_by_policy",
            requested_provider=requested_provider,
            resolved_provider=str(policy.provider),
            resolved_model=None,
            endpoint=endpoint,
            endpoint_scope=endpoint_scope,
            profile=None,
            notes=["A remote semantic endpoint is configured, but policy keeps Slice 09 local-first."],
            advisor=None,
        )
    options = policy.runtime_options(endpoint=endpoint)
    advisor = StructuredLocalAdvisor(
        LocalAdvisorConfig(
            provider=options["provider"],
            model=options["model"],
            endpoint=endpoint,
            profile=str(options.get("profile", "")) or None,
            auth_token=_resolve_api_key(options["provider"]),
            temperature=float(runtime_cfg.get("temperature", 0.0)),
            timeout_seconds=int(runtime_cfg.get("timeout_seconds", 120)),
            max_context=int(options["max_context"]),
            endpoint_scope=endpoint_scope,
        )
    )
    notes = ["Relaytic resolved a structured semantic backend behind the local-first policy contract."]
    if endpoint_scope == "local":
        notes.append("Resolved endpoint is local loopback.")
    return BackendDiscovery(
        status="available",
        requested_provider=requested_provider,
        resolved_provider=options["provider"],
        resolved_model=options["model"],
        endpoint=endpoint,
        endpoint_scope=endpoint_scope,
        profile=str(options.get("profile", "")) or None,
        notes=notes,
        advisor=advisor,
    )


def _resolve_endpoint(provider: str, runtime_cfg: dict[str, Any]) -> str:
    provider_key = provider.lower()
    endpoints = dict(runtime_cfg.get("endpoints", {}))
    if provider_key == "ollama":
        return str(endpoints.get("ollama", "http://127.0.0.1:11434/api/chat"))
    if provider_key in {"llama.cpp", "llama_cpp"}:
        return str(endpoints.get("llama_cpp", "http://127.0.0.1:8000/v1/chat/completions"))
    if provider_key == "openai":
        return str(endpoints.get("openai", "https://api.openai.com/v1/chat/completions"))
    if provider_key == "openai_compatible":
        return str(endpoints.get("openai_compatible", "https://api.openai.com/v1/chat/completions"))
    raise RuntimeError(f"Unsupported provider '{provider}'.")


def _resolve_api_key(provider: str) -> str | None:
    key = os.getenv("RELAYTIC_API_KEY", "").strip() or os.getenv("C2S_API_KEY", "").strip()
    if key:
        return key
    if provider.lower() == "openai":
        fallback = os.getenv("OPENAI_API_KEY", "").strip()
        return fallback or None
    return None


def _http_post_json(
    endpoint: str,
    payload: dict[str, Any],
    *,
    timeout_seconds: int,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    request = Request(endpoint, data=body, headers=request_headers, method="POST")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore") if exc.fp else str(exc)
        raise RuntimeError(f"Provider HTTP error {exc.code} at {endpoint}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Provider connection error at {endpoint}: {exc}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"Provider request timed out for {endpoint}.") from exc
    except OSError as exc:
        lowered = str(exc).lower()
        if "timed out" in lowered or "timeout" in lowered:
            raise RuntimeError(f"Provider request timed out for {endpoint}.") from exc
        raise RuntimeError(f"Provider connection error at {endpoint}: {exc}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Provider returned non-JSON response.") from exc


def _parse_json_object(text: str) -> dict[str, Any] | None:
    normalized = text.strip()
    if not normalized:
        return None
    if normalized.startswith("```") and normalized.endswith("```"):
        lines = normalized.splitlines()
        if len(lines) >= 3:
            normalized = "\n".join(lines[1:-1]).strip()
    try:
        parsed = json.loads(normalized)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None

"""Optional local-LLM advisory helper for Slice 06 evidence review."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from relaytic.core.config import load_config
from relaytic.orchestration.runtime_policy import (
    apply_environment_overrides,
    load_runtime_policy,
)

from .models import EvidenceControls


@dataclass(frozen=True)
class AdvisoryResult:
    """Structured response from an optional advisory LLM call."""

    status: str
    payload: dict[str, Any] | None
    notes: list[str]


@dataclass(frozen=True)
class LocalAdvisorConfig:
    """Runtime connection details for the local advisory client."""

    provider: str
    model: str
    endpoint: str
    auth_token: str | None = None
    temperature: float = 0.0
    timeout_seconds: int = 120
    max_context: int = 4096


class EvidenceLocalAdvisor:
    """Narrow structured-JSON client for optional evidence-layer amplification."""

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
                response = _http_post_json(
                    self.config.endpoint,
                    raw_payload,
                    timeout_seconds=self.config.timeout_seconds,
                )
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
                    "max_tokens": 900,
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
                )
            return AdvisoryResult(status="ok", payload=parsed, notes=[])
        except RuntimeError as exc:
            return AdvisoryResult(status="error", payload=None, notes=[f"{task_name}: {exc}"])


def build_local_advisor(
    *,
    controls: EvidenceControls,
    config_path: str | None,
) -> EvidenceLocalAdvisor | None:
    """Create an advisory client if policy and runtime allow it."""
    if not controls.allow_local_llm_advisory or not controls.prefer_local_llm:
        return None
    config = load_config(config_path)
    policy = apply_environment_overrides(load_runtime_policy(config))
    runtime_cfg = dict(config.get("runtime", {}))
    endpoint = (
        os.getenv("RELAYTIC_ENDPOINT", "").strip()
        or os.getenv("C2S_ENDPOINT", "").strip()
        or _resolve_endpoint(policy.provider, runtime_cfg)
    )
    options = policy.runtime_options(endpoint=endpoint)
    return EvidenceLocalAdvisor(
        LocalAdvisorConfig(
            provider=options["provider"],
            model=options["model"],
            endpoint=endpoint,
            auth_token=_resolve_api_key(options["provider"]),
            temperature=float(runtime_cfg.get("temperature", 0.0)),
            timeout_seconds=int(runtime_cfg.get("timeout_seconds", 120)),
            max_context=int(options["max_context"]),
        )
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
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None

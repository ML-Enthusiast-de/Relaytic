"""External source adapters for Slice 09D private research retrieval."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import ResearchControls


def gather_external_sources(
    *,
    controls: ResearchControls,
    queries: list[dict[str, Any]],
) -> dict[str, Any]:
    if not controls.enabled:
        return {
            "status": "disabled",
            "sources": [],
            "queries_executed": [],
            "endpoint_status": [],
            "source_counts": {"total_sources": 0, "provider_counts": {}, "source_type_counts": {}},
            "notes": ["Research retrieval is disabled by policy."],
            "summary": "Relaytic kept external research retrieval disabled for this run.",
        }
    if not controls.allow_external_research:
        return {
            "status": "policy_blocked",
            "sources": [],
            "queries_executed": [],
            "endpoint_status": [],
            "source_counts": {"total_sources": 0, "provider_counts": {}, "source_type_counts": {}},
            "notes": ["Research retrieval is enabled but privacy policy blocks network export."],
            "summary": "Relaytic prepared redacted research queries but did not send them because privacy policy blocked network export.",
        }

    sources: list[dict[str, Any]] = []
    endpoint_status: list[dict[str, Any]] = []
    queries_executed: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for query in queries:
        query_text = str(query.get("query_text", "")).strip()
        if not query_text:
            continue
        query_id = str(query.get("query_id", "query"))
        queries_executed.append(
            {
                "query_id": query_id,
                "intent": query.get("intent"),
                "query_text": query_text,
                "source_classes": list(query.get("source_classes", [])),
            }
        )
        for provider in controls.source_order:
            if provider == "semantic_scholar":
                response = _search_semantic_scholar(
                    endpoint=controls.semantic_scholar_endpoint,
                    query_text=query_text,
                    limit=controls.max_results_per_source,
                    timeout_seconds=controls.timeout_seconds,
                )
            elif provider == "crossref":
                response = _search_crossref(
                    endpoint=controls.crossref_endpoint,
                    query_text=query_text,
                    limit=controls.max_results_per_source,
                    timeout_seconds=controls.timeout_seconds,
                    contact_email=controls.contact_email,
                )
            else:
                response = {
                    "status": "unsupported_provider",
                    "provider": provider,
                    "sources": [],
                    "endpoint": None,
                    "note": f"Provider `{provider}` is not supported by Relaytic.",
                }
            endpoint_status.append(
                {
                    "provider": provider,
                    "query_id": query_id,
                    "status": response["status"],
                    "endpoint": response.get("endpoint"),
                    "note": response.get("note"),
                }
            )
            for source in response.get("sources", []):
                key = f"{provider}:{source.get('url') or source.get('title')}"
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                sources.append({**source, "query_id": query_id, "query_text": query_text})
    status = "ok" if sources else ("degraded" if any(item["status"] == "error" for item in endpoint_status) else "no_results")
    sources.sort(
        key=lambda item: (
            _source_priority(str(item.get("source_type", ""))),
            -int(item.get("citation_count", 0) or 0),
            str(item.get("title", "")),
        )
    )
    source_counts = {
        "total_sources": len(sources),
        "provider_counts": {},
        "source_type_counts": {},
    }
    for source in sources:
        provider = str(source.get("provider", "")).strip() or "unknown"
        source_type = str(source.get("source_type", "")).strip() or "unknown"
        source_counts["provider_counts"][provider] = int(source_counts["provider_counts"].get(provider, 0)) + 1
        source_counts["source_type_counts"][source_type] = int(source_counts["source_type_counts"].get(source_type, 0)) + 1
    return {
        "status": status,
        "sources": sources,
        "queries_executed": queries_executed,
        "endpoint_status": endpoint_status,
        "source_counts": source_counts,
        "notes": [],
        "summary": _inventory_summary(status=status, source_count=len(sources), query_count=len(queries_executed)),
    }


def _search_semantic_scholar(
    *,
    endpoint: str,
    query_text: str,
    limit: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    params = {
        "query": query_text,
        "limit": str(limit),
        "fields": "title,abstract,year,url,citationCount,publicationTypes",
    }
    url = f"{endpoint}?{urlencode(params)}"
    try:
        payload = _json_get(url, timeout_seconds=timeout_seconds)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return {
            "status": "error",
            "provider": "semantic_scholar",
            "sources": [],
            "endpoint": endpoint,
            "note": str(exc),
        }
    data = payload.get("data", [])
    sources = [
        {
            "provider": "semantic_scholar",
            "source_type": _infer_source_type(
                title=str(item.get("title", "")),
                abstract=str(item.get("abstract", "")),
                query_text=query_text,
            ),
            "title": str(item.get("title", "")).strip(),
            "url": str(item.get("url", "")).strip(),
            "year": item.get("year"),
            "venue": None,
            "citation_count": int(item.get("citationCount", 0) or 0),
            "abstract_snippet": _snippet(str(item.get("abstract", ""))),
            "publication_types": list(item.get("publicationTypes", [])),
            "retrieved_at": _utc_now(),
        }
        for item in data
        if str(item.get("title", "")).strip()
    ]
    return {
        "status": "ok",
        "provider": "semantic_scholar",
        "sources": sources,
        "endpoint": endpoint,
        "note": None,
    }


def _search_crossref(
    *,
    endpoint: str,
    query_text: str,
    limit: int,
    timeout_seconds: int,
    contact_email: str | None,
) -> dict[str, Any]:
    params = {
        "query": query_text,
        "rows": str(limit),
        "select": "DOI,title,URL,type,container-title,issued,is-referenced-by-count",
    }
    if contact_email:
        params["mailto"] = contact_email
    url = f"{endpoint}?{urlencode(params)}"
    try:
        payload = _json_get(url, timeout_seconds=timeout_seconds)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return {
            "status": "error",
            "provider": "crossref",
            "sources": [],
            "endpoint": endpoint,
            "note": str(exc),
        }
    items = dict(payload.get("message", {})).get("items", [])
    sources = []
    for item in items:
        title_list = item.get("title", [])
        title = str(title_list[0]).strip() if isinstance(title_list, list) and title_list else str(item.get("title", "")).strip()
        if not title:
            continue
        venue_list = item.get("container-title", [])
        venue = str(venue_list[0]).strip() if isinstance(venue_list, list) and venue_list else None
        year = None
        issued = item.get("issued", {})
        if isinstance(issued, dict):
            date_parts = issued.get("date-parts", [])
            if isinstance(date_parts, list) and date_parts and isinstance(date_parts[0], list) and date_parts[0]:
                try:
                    year = int(date_parts[0][0])
                except (TypeError, ValueError):
                    year = None
        sources.append(
            {
                "provider": "crossref",
                "source_type": _infer_source_type(title=title, abstract="", query_text=query_text),
                "title": title,
                "url": str(item.get("URL", "")).strip(),
                "year": year,
                "venue": venue,
                "citation_count": int(item.get("is-referenced-by-count", 0) or 0),
                "abstract_snippet": "",
                "publication_types": [str(item.get("type", "")).strip()] if str(item.get("type", "")).strip() else [],
                "retrieved_at": _utc_now(),
            }
        )
    return {
        "status": "ok",
        "provider": "crossref",
        "sources": sources,
        "endpoint": endpoint,
        "note": None,
    }


def _json_get(url: str, *, timeout_seconds: int) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "User-Agent": "Relaytic/0.1.0 (local-first research retrieval)",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        if int(getattr(response, "status", 200)) >= 400:
            raise HTTPError(url, int(response.status), "HTTP error", hdrs=response.headers, fp=None)
        body = response.read().decode("utf-8")
    return json.loads(body)


def _infer_source_type(*, title: str, abstract: str, query_text: str) -> str:
    text = " ".join([title, abstract, query_text]).lower()
    if any(token in text for token in ("benchmark", "leaderboard", "competition", "dataset")):
        return "benchmark_reference"
    if any(token in text for token in ("repository", "implementation", "github", "library", "toolkit")):
        return "implementation_doc"
    return "paper"


def _snippet(text: str, *, limit: int = 220) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _source_priority(source_type: str) -> int:
    mapping = {
        "benchmark_reference": 0,
        "paper": 1,
        "implementation_doc": 2,
    }
    return mapping.get(source_type, 9)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _inventory_summary(*, status: str, source_count: int, query_count: int) -> str:
    if status == "ok":
        return f"Relaytic executed {query_count} redacted research querie(s) and harvested {source_count} typed external source(s)."
    if status == "degraded":
        return f"Relaytic attempted {query_count} research querie(s), but only a degraded source inventory was available."
    return f"Relaytic executed {query_count} research querie(s) and found {source_count} external source(s)."

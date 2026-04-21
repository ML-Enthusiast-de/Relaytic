"""Deterministic AML graph, typology, and case-expansion artifacts."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import pandas as pd

from relaytic.core.json_utils import write_json
from relaytic.ingestion import load_tabular_data


ENTITY_GRAPH_PROFILE_SCHEMA_VERSION = "relaytic.entity_graph_profile.v1"
COUNTERPARTY_NETWORK_REPORT_SCHEMA_VERSION = "relaytic.counterparty_network_report.v1"
TYPOLOGY_DETECTION_REPORT_SCHEMA_VERSION = "relaytic.typology_detection_report.v1"
SUBGRAPH_RISK_REPORT_SCHEMA_VERSION = "relaytic.subgraph_risk_report.v1"
ENTITY_CASE_EXPANSION_SCHEMA_VERSION = "relaytic.entity_case_expansion.v1"


AML_GRAPH_FILENAMES = {
    "entity_graph_profile": "entity_graph_profile.json",
    "counterparty_network_report": "counterparty_network_report.json",
    "typology_detection_report": "typology_detection_report.json",
    "subgraph_risk_report": "subgraph_risk_report.json",
    "entity_case_expansion": "entity_case_expansion.json",
}


def sync_aml_graph_artifacts(
    run_dir: str | Path,
    *,
    data_path: str | Path | None,
    context_bundle: dict[str, Any] | None,
    task_contract_bundle: dict[str, Any] | None,
) -> dict[str, Path]:
    """Build and write AML graph artifacts for the current run."""
    root = Path(run_dir)
    resolved_data_path = None
    if data_path is not None:
        candidate = Path(data_path)
        resolved_data_path = candidate if candidate.is_absolute() else root / candidate
    artifacts = build_aml_graph_artifacts(
        data_path=resolved_data_path,
        context_bundle=context_bundle,
        task_contract_bundle=task_contract_bundle,
    )
    root.mkdir(parents=True, exist_ok=True)
    return {
        key: write_json(
            root / filename,
            artifacts[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in AML_GRAPH_FILENAMES.items()
    }


def read_aml_graph_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read AML graph artifacts if present."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in AML_GRAPH_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def build_aml_graph_artifacts(
    *,
    data_path: str | Path | None,
    context_bundle: dict[str, Any] | None,
    task_contract_bundle: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """Construct deterministic AML graph artifacts from staged data and task contracts."""
    generated_at = _utc_now()
    task_contract_bundle = task_contract_bundle or {}
    context_bundle = context_bundle or {}
    aml_domain_contract = _bundle_item(task_contract_bundle, "aml_domain_contract")
    aml_case_ontology = _bundle_item(task_contract_bundle, "aml_case_ontology")
    aml_review_budget_contract = _bundle_item(task_contract_bundle, "aml_review_budget_contract")
    task_profile_contract = _bundle_item(task_contract_bundle, "task_profile_contract")
    domain_brief = _bundle_item(context_bundle, "domain_brief")

    if not aml_domain_contract.get("aml_active"):
        return _inactive_aml_graph_artifacts(
            generated_at=generated_at,
            summary="AML graph posture is inactive because this run is not under the AML contract.",
        )
    if data_path is None:
        return _inactive_aml_graph_artifacts(
            generated_at=generated_at,
            summary="AML graph posture is active, but no staged dataset was available for graph construction.",
            status="data_unavailable",
        )

    frame = load_tabular_data(data_path).frame.copy()
    if frame.empty:
        return _inactive_aml_graph_artifacts(
            generated_at=generated_at,
            summary="AML graph posture is active, but the staged dataset was empty.",
            status="data_unavailable",
        )

    columns = list(frame.columns)
    source_column, destination_column = _resolve_edge_columns(columns)
    if not source_column or not destination_column:
        return _inactive_aml_graph_artifacts(
            generated_at=generated_at,
            summary="AML graph posture is active, but no source/destination entity columns were detected for graph construction.",
            status="graph_not_available_for_dataset",
        )

    target_column = _clean_text(task_profile_contract.get("target_column"))
    amount_column = _resolve_amount_column(columns)
    timestamp_column = _clean_text(task_profile_contract.get("timestamp_column"))
    shared_columns = _resolve_shared_signal_columns(columns)
    edge_rows = _build_edge_rows(
        frame=frame,
        source_column=source_column,
        destination_column=destination_column,
        target_column=target_column,
        amount_column=amount_column,
        timestamp_column=timestamp_column,
    )
    if edge_rows.empty:
        return _inactive_aml_graph_artifacts(
            generated_at=generated_at,
            summary="AML graph posture is active, but graph-capable edge rows could not be constructed from the dataset.",
            status="graph_not_available_for_dataset",
        )

    edge_agg = _aggregate_edges(edge_rows)
    entity_stats = _build_entity_stats(edge_agg)
    components = _build_components(edge_agg)
    shared_links = _build_shared_links(frame=frame, shared_columns=shared_columns, source_column=source_column)
    typology_hits = _detect_typologies(
        edge_agg=edge_agg,
        entity_stats=entity_stats,
        shared_links=shared_links,
        amount_column_present=amount_column is not None,
        domain_focus=_clean_text(aml_domain_contract.get("domain_focus")),
    )
    subgraph_payload = _build_subgraph_payload(
        edge_agg=edge_agg,
        entity_stats=entity_stats,
        typology_hits=typology_hits,
        components=components,
    )
    case_expansion = _build_case_expansion(
        subgraph_payload=subgraph_payload,
        typology_hits=typology_hits,
        aml_case_ontology=aml_case_ontology,
        aml_review_budget_contract=aml_review_budget_contract,
        domain_brief=domain_brief,
    )
    high_risk_entities = _top_entities(entity_stats, limit=5)
    top_edges = _top_edges(edge_agg, limit=10)

    entity_graph_profile = {
        "schema_version": ENTITY_GRAPH_PROFILE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "source_column": source_column,
        "destination_column": destination_column,
        "target_column": target_column,
        "amount_column": amount_column,
        "timestamp_column": timestamp_column,
        "node_count": int(entity_stats.shape[0]),
        "edge_count": int(edge_agg.shape[0]),
        "component_count": len(components),
        "shared_signal_columns": shared_columns,
        "high_risk_entities": high_risk_entities,
        "summary": (
            f"Relaytic-AML built a counterparty graph with `{int(entity_stats.shape[0])}` entities and "
            f"`{int(edge_agg.shape[0])}` aggregated edges from `{source_column}` to `{destination_column}`."
        ),
    }
    counterparty_network_report = {
        "schema_version": COUNTERPARTY_NETWORK_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "largest_component_size": max((len(component) for component in components), default=0),
        "component_count": len(components),
        "top_edges": top_edges,
        "top_entities_by_risk": high_risk_entities,
        "shared_signal_link_count": len(shared_links),
        "summary": (
            f"Relaytic-AML found `{len(components)}` connected component(s); the largest contains "
            f"`{max((len(component) for component in components), default=0)}` entity/entities."
        ),
    }
    typology_detection_report = {
        "schema_version": TYPOLOGY_DETECTION_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if typology_hits else "no_hits",
        "typology_hit_count": len(typology_hits),
        "typology_hits": typology_hits,
        "summary": (
            f"Relaytic-AML detected `{len(typology_hits)}` structural typology hit(s)."
            if typology_hits
            else "Relaytic-AML did not find a strong structural typology hit on this run."
        ),
    }
    subgraph_risk_report = {
        "schema_version": SUBGRAPH_RISK_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        **subgraph_payload,
    }
    entity_case_expansion = {
        "schema_version": ENTITY_CASE_EXPANSION_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if case_expansion.get("focal_entity") else "no_focus_entity",
        **case_expansion,
    }
    return {
        "entity_graph_profile": entity_graph_profile,
        "counterparty_network_report": counterparty_network_report,
        "typology_detection_report": typology_detection_report,
        "subgraph_risk_report": subgraph_risk_report,
        "entity_case_expansion": entity_case_expansion,
    }


def _inactive_aml_graph_artifacts(*, generated_at: str, summary: str, status: str = "not_applicable") -> dict[str, dict[str, Any]]:
    base = {
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
    }
    return {
        "entity_graph_profile": {
            "schema_version": ENTITY_GRAPH_PROFILE_SCHEMA_VERSION,
            **base,
            "node_count": 0,
            "edge_count": 0,
            "high_risk_entities": [],
        },
        "counterparty_network_report": {
            "schema_version": COUNTERPARTY_NETWORK_REPORT_SCHEMA_VERSION,
            **base,
            "component_count": 0,
            "top_edges": [],
            "top_entities_by_risk": [],
        },
        "typology_detection_report": {
            "schema_version": TYPOLOGY_DETECTION_REPORT_SCHEMA_VERSION,
            **base,
            "typology_hit_count": 0,
            "typology_hits": [],
        },
        "subgraph_risk_report": {
            "schema_version": SUBGRAPH_RISK_REPORT_SCHEMA_VERSION,
            **base,
            "subgraph_count": 0,
            "selected_subgraphs": [],
            "candidate_comparison": {},
        },
        "entity_case_expansion": {
            "schema_version": ENTITY_CASE_EXPANSION_SCHEMA_VERSION,
            **base,
            "focal_entity": None,
            "expanded_entities": [],
            "typology_hits": [],
        },
    }


def _build_edge_rows(
    *,
    frame: pd.DataFrame,
    source_column: str,
    destination_column: str,
    target_column: str | None,
    amount_column: str | None,
    timestamp_column: str | None,
) -> pd.DataFrame:
    source = frame[source_column].astype(str).str.strip()
    destination = frame[destination_column].astype(str).str.strip()
    payload = pd.DataFrame({"source": source, "destination": destination})
    payload = payload[(payload["source"] != "") & (payload["destination"] != "")]
    payload = payload[payload["source"].str.lower() != "nan"]
    payload = payload[payload["destination"].str.lower() != "nan"]
    if target_column and target_column in frame.columns:
        payload["label"] = pd.to_numeric(frame.loc[payload.index, target_column], errors="coerce").fillna(0.0)
    else:
        payload["label"] = 0.0
    if amount_column and amount_column in frame.columns:
        payload["amount"] = pd.to_numeric(frame.loc[payload.index, amount_column], errors="coerce").fillna(0.0)
    else:
        payload["amount"] = 0.0
    if timestamp_column and timestamp_column in frame.columns:
        payload["timestamp"] = frame.loc[payload.index, timestamp_column].astype(str)
    return payload.reset_index(drop=True)


def _aggregate_edges(edge_rows: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        edge_rows.groupby(["source", "destination"], dropna=False)
        .agg(
            tx_count=("source", "size"),
            suspicious_count=("label", "sum"),
            amount_sum=("amount", "sum"),
            amount_mean=("amount", "mean"),
        )
        .reset_index()
    )
    grouped["suspicious_rate"] = grouped["suspicious_count"] / grouped["tx_count"].clip(lower=1)
    return grouped


def _build_entity_stats(edge_agg: pd.DataFrame) -> pd.DataFrame:
    out_stats = (
        edge_agg.groupby("source", dropna=False)
        .agg(
            out_tx_count=("tx_count", "sum"),
            out_neighbor_count=("destination", "nunique"),
            suspicious_out_count=("suspicious_count", "sum"),
            amount_out_sum=("amount_sum", "sum"),
        )
        .reset_index()
        .rename(columns={"source": "entity"})
    )
    in_stats = (
        edge_agg.groupby("destination", dropna=False)
        .agg(
            in_tx_count=("tx_count", "sum"),
            in_neighbor_count=("source", "nunique"),
            suspicious_in_count=("suspicious_count", "sum"),
            amount_in_sum=("amount_sum", "sum"),
        )
        .reset_index()
        .rename(columns={"destination": "entity"})
    )
    entity_stats = out_stats.merge(in_stats, on="entity", how="outer").fillna(0)
    entity_stats["tx_count"] = entity_stats["out_tx_count"] + entity_stats["in_tx_count"]
    entity_stats["neighbor_count"] = entity_stats["out_neighbor_count"] + entity_stats["in_neighbor_count"]
    entity_stats["suspicious_tx_count"] = entity_stats["suspicious_out_count"] + entity_stats["suspicious_in_count"]
    entity_stats["suspicious_rate"] = entity_stats["suspicious_tx_count"] / entity_stats["tx_count"].clip(lower=1)
    entity_stats["bridge_flag"] = (
        (entity_stats["in_neighbor_count"] >= 2) & (entity_stats["out_neighbor_count"] >= 2)
    ).astype(float)
    entity_stats["risk_score"] = (
        0.50 * entity_stats["suspicious_rate"].clip(upper=1.0)
        + 0.20 * (entity_stats["neighbor_count"] / 5.0).clip(upper=1.0)
        + 0.20 * (entity_stats["tx_count"] / 10.0).clip(upper=1.0)
        + 0.10 * entity_stats["bridge_flag"]
    ).round(4)
    return entity_stats.sort_values(["risk_score", "tx_count"], ascending=[False, False]).reset_index(drop=True)


def _build_components(edge_agg: pd.DataFrame) -> list[list[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for row in edge_agg.itertuples(index=False):
        adjacency[str(row.source)].add(str(row.destination))
        adjacency[str(row.destination)].add(str(row.source))
    seen: set[str] = set()
    components: list[list[str]] = []
    for entity in sorted(adjacency):
        if entity in seen:
            continue
        queue = [entity]
        component: list[str] = []
        seen.add(entity)
        while queue:
            current = queue.pop()
            component.append(current)
            for neighbor in sorted(adjacency[current]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return components


def _build_shared_links(*, frame: pd.DataFrame, shared_columns: list[str], source_column: str) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    if source_column not in frame.columns:
        return links
    for column in shared_columns:
        grouped = (
            frame[[source_column, column]]
            .dropna()
            .assign(
                entity=lambda value: value[source_column].astype(str).str.strip(),
                shared_value=lambda value: value[column].astype(str).str.strip(),
            )
        )
        grouped = grouped[(grouped["entity"] != "") & (grouped["shared_value"] != "")]
        if grouped.empty:
            continue
        summary = grouped.groupby("shared_value", dropna=False)["entity"].nunique().reset_index(name="entity_count")
        for row in summary.itertuples(index=False):
            if int(row.entity_count) < 3:
                continue
            entities = sorted(
                {
                    str(item)
                    for item in grouped.loc[grouped["shared_value"] == row.shared_value, "entity"].tolist()
                    if str(item).strip()
                }
            )
            links.append(
                {
                    "link_type": column,
                    "shared_value": str(row.shared_value),
                    "entity_count": int(row.entity_count),
                    "entities": entities[:8],
                }
            )
    return links


def _detect_typologies(
    *,
    edge_agg: pd.DataFrame,
    entity_stats: pd.DataFrame,
    shared_links: list[dict[str, Any]],
    amount_column_present: bool,
    domain_focus: str | None,
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    global_amount_median = float(edge_agg["amount_mean"].median()) if amount_column_present and not edge_agg.empty else 0.0

    inbound = (
        edge_agg.groupby("destination", dropna=False)
        .agg(
            inbound_sources=("source", "nunique"),
            inbound_tx_count=("tx_count", "sum"),
            suspicious_count=("suspicious_count", "sum"),
            avg_amount=("amount_mean", "mean"),
        )
        .reset_index()
    )
    for row in inbound.itertuples(index=False):
        if int(row.inbound_sources) >= 3 and int(row.inbound_tx_count) >= 3:
            low_value = not amount_column_present or float(row.avg_amount) <= max(global_amount_median, 1.0)
            if low_value:
                hits.append(
                    {
                        "typology": "smurfing",
                        "focal_entity": str(row.destination),
                        "risk_score": round(min(1.0, 0.55 + (int(row.inbound_sources) / 10.0)), 4),
                        "support_count": int(row.inbound_sources),
                        "reason": "Multiple inbound counterparties are sending repeated low-value traffic into one focal entity.",
                    }
                )

    for row in entity_stats.itertuples(index=False):
        if int(row.in_neighbor_count) >= 3 and int(row.out_neighbor_count) <= 1 and float(row.suspicious_rate) > 0:
            hits.append(
                {
                    "typology": "funnel_accounts",
                    "focal_entity": str(row.entity),
                    "risk_score": round(min(1.0, 0.45 + float(row.suspicious_rate)), 4),
                    "support_count": int(row.in_neighbor_count),
                    "reason": "The entity gathers traffic from many sources into a narrow outbound pattern, which resembles a funnel.",
                }
            )
        if int(row.in_neighbor_count) >= 2 and int(row.out_neighbor_count) >= 2 and float(row.suspicious_rate) >= 0.15:
            hits.append(
                {
                    "typology": "layering",
                    "focal_entity": str(row.entity),
                    "risk_score": round(min(1.0, 0.40 + float(row.suspicious_rate) + 0.05 * float(row.bridge_flag)), 4),
                    "support_count": int(row.neighbor_count),
                    "reason": "The entity mixes inbound and outbound neighborhoods under suspicious traffic, which resembles layering.",
                }
            )

    for link in shared_links[:5]:
        hits.append(
            {
                "typology": "shared_instrument_linkage",
                "focal_entity": str(link["entities"][0]) if link["entities"] else "unknown",
                "risk_score": round(min(1.0, 0.35 + (int(link["entity_count"]) / 20.0)), 4),
                "support_count": int(link["entity_count"]),
                "reason": f"Multiple entities share `{link['link_type']}` value `{link['shared_value']}`, which can indicate hidden linkage.",
            }
        )

    if domain_focus == "payment_fraud" and not any(hit["typology"] == "chargeback_abuse" for hit in hits):
        top_entity = entity_stats.head(1)
        if not top_entity.empty:
            row = top_entity.iloc[0]
            hits.append(
                {
                    "typology": "chargeback_abuse",
                    "focal_entity": str(row["entity"]),
                    "risk_score": round(min(1.0, 0.30 + float(row["risk_score"])), 4),
                    "support_count": int(row["tx_count"]),
                    "reason": "The top-risk entity is carried forward as a payment-fraud typology candidate for analyst review.",
                }
            )

    deduped: dict[tuple[str, str], dict[str, Any]] = {}
    for hit in hits:
        key = (str(hit["typology"]), str(hit["focal_entity"]))
        if key not in deduped or float(hit["risk_score"]) > float(deduped[key]["risk_score"]):
            deduped[key] = hit
    return sorted(deduped.values(), key=lambda item: (float(item["risk_score"]), int(item["support_count"])), reverse=True)


def _build_subgraph_payload(
    *,
    edge_agg: pd.DataFrame,
    entity_stats: pd.DataFrame,
    typology_hits: list[dict[str, Any]],
    components: list[list[str]],
) -> dict[str, Any]:
    if entity_stats.empty:
        return {
            "status": "no_graph",
            "subgraph_count": 0,
            "selected_subgraphs": [],
            "candidate_comparison": {},
            "summary": "No graph entities were available for subgraph reasoning.",
        }
    focal_entity = str(entity_stats.iloc[0]["entity"])
    neighborhood_edges = edge_agg[(edge_agg["source"] == focal_entity) | (edge_agg["destination"] == focal_entity)].copy()
    neighborhood_nodes = sorted(
        {
            focal_entity,
            *[str(item) for item in neighborhood_edges["source"].tolist()],
            *[str(item) for item in neighborhood_edges["destination"].tolist()],
        }
    )
    neighborhood_entity_stats = entity_stats[entity_stats["entity"].isin(neighborhood_nodes)].copy()
    neighborhood_typologies = [item for item in typology_hits if str(item.get("focal_entity")) in neighborhood_nodes]
    density = 0.0
    if len(neighborhood_nodes) > 1:
        density = min(1.0, float(neighborhood_edges.shape[0]) / float(len(neighborhood_nodes) * (len(neighborhood_nodes) - 1)))
    structural_score = round(
        min(
            1.0,
            float(neighborhood_entity_stats["risk_score"].mean()) if not neighborhood_entity_stats.empty else 0.0
            + 0.08 * len(neighborhood_typologies)
            + 0.05 * density,
        ),
        4,
    )
    shadow_score = round(
        min(
            1.0,
            structural_score * 0.82 + 0.05 * density,
        ),
        4,
    )
    candidate_comparison = {
        "status": "ok",
        "selected_candidate": "structural_baseline",
        "shadow_candidate": "message_passing_shadow_proxy",
        "selected_score": structural_score,
        "shadow_score": shadow_score,
        "winner": "structural_baseline" if structural_score >= shadow_score else "message_passing_shadow_proxy",
        "summary": (
            f"Relaytic-AML kept the structural baseline at `{structural_score}` over the heavier graph shadow proxy at "
            f"`{shadow_score}` on the current labeled structural evidence."
        ),
    }
    selected_subgraphs = [
        {
            "subgraph_id": "focal_neighborhood_001",
            "focal_entity": focal_entity,
            "node_count": len(neighborhood_nodes),
            "edge_count": int(neighborhood_edges.shape[0]),
            "structural_score": structural_score,
            "shadow_candidate_score": shadow_score,
            "typology_hits": [item["typology"] for item in neighborhood_typologies],
            "nodes": neighborhood_nodes[:12],
        }
    ]
    return {
        "status": "active",
        "subgraph_count": 1,
        "selected_subgraphs": selected_subgraphs,
        "candidate_comparison": candidate_comparison,
        "summary": (
            f"Relaytic-AML expanded focal entity `{focal_entity}` into a `{len(neighborhood_nodes)}`-node neighborhood and "
            f"kept the structural baseline over the heavier shadow proxy."
        ),
    }


def _build_case_expansion(
    *,
    subgraph_payload: dict[str, Any],
    typology_hits: list[dict[str, Any]],
    aml_case_ontology: dict[str, Any],
    aml_review_budget_contract: dict[str, Any],
    domain_brief: dict[str, Any],
) -> dict[str, Any]:
    selected_subgraphs = list(subgraph_payload.get("selected_subgraphs", []))
    if not selected_subgraphs:
        return {
            "focal_entity": None,
            "expanded_entities": [],
            "typology_hits": [],
            "review_objective": _clean_text(aml_review_budget_contract.get("decision_objective")),
            "summary": "No focal AML entity was available for case expansion.",
        }
    focal = dict(selected_subgraphs[0])
    focal_entity = _clean_text(focal.get("focal_entity"))
    hits = [item for item in typology_hits if _clean_text(item.get("focal_entity")) == focal_entity or _clean_text(item.get("focal_entity")) in set(focal.get("nodes", []))]
    expanded_entities = [
        {
            "entity_id": str(entity_id),
            "role": "neighbor" if str(entity_id) != focal_entity else "focal",
        }
        for entity_id in focal.get("nodes", [])
    ]
    return {
        "focal_entity": focal_entity,
        "expanded_entities": expanded_entities,
        "expanded_entity_count": len(expanded_entities),
        "typology_hits": hits[:5],
        "review_objective": _clean_text(aml_review_budget_contract.get("decision_objective")),
        "case_levels": list(aml_case_ontology.get("case_levels", [])),
        "domain_summary": _clean_text(domain_brief.get("summary")),
        "summary": (
            f"Relaytic-AML expanded focal entity `{focal_entity}` into `{len(expanded_entities)}` entity-level case items "
            f"with `{len(hits)}` typology hit(s) for analyst review."
        ),
    }


def _top_entities(entity_stats: pd.DataFrame, *, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in entity_stats.head(limit).itertuples(index=False):
        rows.append(
            {
                "entity_id": str(row.entity),
                "risk_score": float(row.risk_score),
                "tx_count": int(row.tx_count),
                "neighbor_count": int(row.neighbor_count),
                "suspicious_rate": round(float(row.suspicious_rate), 4),
            }
        )
    return rows


def _top_edges(edge_agg: pd.DataFrame, *, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ordered = edge_agg.sort_values(["suspicious_rate", "tx_count", "amount_sum"], ascending=[False, False, False])
    for row in ordered.head(limit).itertuples(index=False):
        rows.append(
            {
                "source": str(row.source),
                "destination": str(row.destination),
                "tx_count": int(row.tx_count),
                "suspicious_rate": round(float(row.suspicious_rate), 4),
                "amount_sum": round(float(row.amount_sum), 4),
            }
        )
    return rows


def _resolve_edge_columns(columns: list[str]) -> tuple[str | None, str | None]:
    source_column = _resolve_first_column(
        columns,
        exacts=[
            "source_account",
            "nameOrig",
            "sender_account",
            "origin_account",
            "from_account",
            "src_account",
            "src",
            "account_id",
            "source_entity",
            "sender_id",
            "originator_id",
        ],
        tokens=["source", "sender", "origin", "orig", "from_", "src_", "payer"],
    )
    destination_column = _resolve_first_column(
        columns,
        exacts=[
            "destination_account",
            "nameDest",
            "receiver_account",
            "beneficiary_account",
            "to_account",
            "dst_account",
            "dst",
            "counterparty_account",
            "counterparty_id",
            "destination_entity",
            "receiver_id",
            "merchant_id",
        ],
        tokens=["destination", "dest", "receiver", "beneficiary", "counterparty", "to_", "dst_", "merchant"],
    )
    return source_column, destination_column


def _resolve_amount_column(columns: list[str]) -> str | None:
    return _resolve_first_column(
        columns,
        exacts=["amount", "txn_amount", "transaction_amount", "payment_amount", "amount_usd", "value"],
        tokens=["amount", "value"],
    )


def _resolve_shared_signal_columns(columns: list[str]) -> list[str]:
    found: list[str] = []
    for token in ("device", "email", "phone", "ip", "card"):
        column = _resolve_first_column(columns, exacts=[], tokens=[token])
        if column and column not in found:
            found.append(column)
    return found


def _resolve_first_column(columns: list[str], *, exacts: list[str], tokens: list[str]) -> str | None:
    lowered = {column.lower(): column for column in columns}
    for exact in exacts:
        column = lowered.get(exact.lower())
        if column:
            return column
    for column in columns:
        text = column.lower()
        if any(token in text for token in tokens):
            return column
    return None


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

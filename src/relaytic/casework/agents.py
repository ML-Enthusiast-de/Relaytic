"""Deterministic analyst review queue and case-packet artifacts for Relaytic-AML."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


ALERT_QUEUE_POLICY_SCHEMA_VERSION = "relaytic.alert_queue_policy.v1"
ALERT_QUEUE_RANKINGS_SCHEMA_VERSION = "relaytic.alert_queue_rankings.v1"
ANALYST_REVIEW_SCORECARD_SCHEMA_VERSION = "relaytic.analyst_review_scorecard.v1"
CASE_PACKET_SCHEMA_VERSION = "relaytic.case_packet.v1"
REVIEW_CAPACITY_SENSITIVITY_SCHEMA_VERSION = "relaytic.review_capacity_sensitivity.v1"


CASEWORK_FILENAMES = {
    "alert_queue_policy": "alert_queue_policy.json",
    "alert_queue_rankings": "alert_queue_rankings.json",
    "analyst_review_scorecard": "analyst_review_scorecard.json",
    "case_packet": "case_packet.json",
    "review_capacity_sensitivity": "review_capacity_sensitivity.json",
}


def sync_casework_artifacts(
    run_dir: str | Path,
    *,
    context_bundle: dict[str, Any] | None,
    task_contract_bundle: dict[str, Any] | None,
    aml_graph_bundle: dict[str, Any] | None,
    operating_point_bundle: dict[str, Any] | None,
) -> dict[str, Path]:
    """Build and write deterministic casework artifacts for the current run."""
    root = Path(run_dir)
    artifacts = build_casework_artifacts(
        context_bundle=context_bundle,
        task_contract_bundle=task_contract_bundle,
        aml_graph_bundle=aml_graph_bundle,
        operating_point_bundle=operating_point_bundle,
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
        for key, filename in CASEWORK_FILENAMES.items()
    }


def read_casework_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read casework artifacts if present."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in CASEWORK_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def build_casework_artifacts(
    *,
    context_bundle: dict[str, Any] | None,
    task_contract_bundle: dict[str, Any] | None,
    aml_graph_bundle: dict[str, Any] | None,
    operating_point_bundle: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """Construct analyst review queue and case-packet artifacts from current AML evidence."""
    generated_at = _utc_now()
    context_bundle = context_bundle or {}
    task_contract_bundle = task_contract_bundle or {}
    aml_graph_bundle = aml_graph_bundle or {}
    operating_point_bundle = operating_point_bundle or {}

    aml_domain_contract = _bundle_item(task_contract_bundle, "aml_domain_contract")
    aml_review_budget_contract = _bundle_item(task_contract_bundle, "aml_review_budget_contract")
    aml_case_ontology = _bundle_item(task_contract_bundle, "aml_case_ontology")
    entity_graph_profile = _bundle_item(aml_graph_bundle, "entity_graph_profile")
    counterparty_network_report = _bundle_item(aml_graph_bundle, "counterparty_network_report")
    typology_detection_report = _bundle_item(aml_graph_bundle, "typology_detection_report")
    subgraph_risk_report = _bundle_item(aml_graph_bundle, "subgraph_risk_report")
    entity_case_expansion = _bundle_item(aml_graph_bundle, "entity_case_expansion")
    operating_point_contract = _bundle_item(operating_point_bundle, "operating_point_contract")
    review_budget_optimization_report = _bundle_item(operating_point_bundle, "review_budget_optimization_report")
    domain_brief = _bundle_item(context_bundle, "domain_brief")
    task_brief = _bundle_item(context_bundle, "task_brief")

    if not bool(aml_domain_contract.get("aml_active")):
        return _inactive_casework_artifacts(
            generated_at=generated_at,
            summary="Relaytic-AML casework is inactive because the AML domain contract is not active on this run.",
        )

    graph_status = _clean_text(entity_graph_profile.get("status")) or _clean_text(subgraph_risk_report.get("status"))
    high_risk_entities = list(entity_graph_profile.get("high_risk_entities", [])) if isinstance(entity_graph_profile.get("high_risk_entities"), list) else []
    if graph_status != "active" or not high_risk_entities:
        return _inactive_casework_artifacts(
            generated_at=generated_at,
            status="graph_not_available_for_casework",
            summary="Relaytic-AML casework stayed inactive because the current run does not yet have enough graph/entity evidence to build a defensible review queue.",
        )

    review_fraction = _resolve_review_fraction(
        operating_point_contract=operating_point_contract,
        review_budget_optimization_report=review_budget_optimization_report,
    )
    queue_rows = _build_queue_rows(
        high_risk_entities=high_risk_entities,
        typology_hits=list(typology_detection_report.get("typology_hits", [])) if isinstance(typology_detection_report.get("typology_hits"), list) else [],
        entity_case_expansion=entity_case_expansion,
        counterparty_network_report=counterparty_network_report,
    )
    review_capacity_cases = max(1, min(len(queue_rows), math.ceil(len(queue_rows) * review_fraction)))
    queue_rows = _assign_review_actions(queue_rows=queue_rows, review_capacity_cases=review_capacity_cases)

    analyst_hours_per_case = 0.75
    focal_entity = _clean_text(entity_case_expansion.get("focal_entity"))
    selected_case = dict(queue_rows[0]) if queue_rows else {}
    policy = {
        "schema_version": ALERT_QUEUE_POLICY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "policy_kind": "entity_graph_review_queue",
        "queue_unit": "entity_case",
        "decision_objective": _clean_text(aml_review_budget_contract.get("decision_objective")) or "maximize_precision_at_review_budget",
        "review_budget_fraction": review_fraction,
        "review_capacity_cases": review_capacity_cases,
        "selected_threshold": operating_point_contract.get("selected_threshold"),
        "analyst_capacity_assumption": _clean_text(aml_review_budget_contract.get("analyst_capacity_assumption")) or "bounded_manual_review",
        "score_components": [
            {"component": "entity_risk_score", "weight": 0.55},
            {"component": "typology_support", "weight": 0.20},
            {"component": "structural_support", "weight": 0.15},
            {"component": "focal_case_bonus", "weight": 0.10},
        ],
        "summary": (
            f"Relaytic-AML ranked `{len(queue_rows)}` entity-case candidate(s) and recommends immediate review for "
            f"`{review_capacity_cases}` case(s) at review fraction `{review_fraction:.2f}`."
        ),
    }
    rankings = {
        "schema_version": ALERT_QUEUE_RANKINGS_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "queue_count": len(queue_rows),
        "review_capacity_cases": review_capacity_cases,
        "ranking": queue_rows,
        "summary": (
            f"Top case is `{_clean_text(selected_case.get('case_id')) or 'unknown'}` for focal entity "
            f"`{_clean_text(selected_case.get('entity_id')) or focal_entity or 'unknown'}`."
        ),
    }
    review_now_rows = [row for row in queue_rows if _clean_text(row.get("review_action")) == "review_now"]
    scorecard = {
        "schema_version": ANALYST_REVIEW_SCORECARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "total_case_count": len(queue_rows),
        "review_capacity_cases": review_capacity_cases,
        "review_capacity_fraction": review_fraction,
        "immediate_review_count": len(review_now_rows),
        "monitor_count": sum(1 for row in queue_rows if _clean_text(row.get("review_action")) == "monitor"),
        "defer_count": sum(1 for row in queue_rows if _clean_text(row.get("review_action")) == "defer"),
        "analyst_hours_per_case": analyst_hours_per_case,
        "estimated_review_hours": round(float(review_capacity_cases) * analyst_hours_per_case, 2),
        "top_case_id": _clean_text(selected_case.get("case_id")),
        "top_priority_score": selected_case.get("priority_score"),
        "review_typology_coverage": len(
            {
                str(typology)
                for row in review_now_rows
                for typology in row.get("typologies", [])
                if str(typology).strip()
            }
        ),
        "summary": (
            f"Relaytic-AML estimates `{round(float(review_capacity_cases) * analyst_hours_per_case, 2)}` analyst hour(s) "
            f"to review the current top `{review_capacity_cases}` case(s)."
        ),
    }
    case_packet = {
        "schema_version": CASE_PACKET_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if selected_case else "no_case_selected",
        "case_id": _clean_text(selected_case.get("case_id")),
        "queue_rank": int(selected_case.get("rank", 0) or 0),
        "review_action": _clean_text(selected_case.get("review_action")),
        "focal_entity": _clean_text(selected_case.get("entity_id")) or focal_entity,
        "priority_score": selected_case.get("priority_score"),
        "domain_focus": _clean_text(aml_domain_contract.get("domain_focus")),
        "target_level": _clean_text(aml_domain_contract.get("target_level")),
        "decision_objective": _clean_text(aml_review_budget_contract.get("decision_objective")),
        "top_typologies": list(selected_case.get("typologies", [])),
        "linked_entities": list(entity_case_expansion.get("expanded_entities", []))[:8]
        if _clean_text(selected_case.get("entity_id")) == focal_entity
        else _linked_entities_for_case(
            entity_id=_clean_text(selected_case.get("entity_id")),
            expanded_entities=list(entity_case_expansion.get("expanded_entities", [])) if isinstance(entity_case_expansion.get("expanded_entities"), list) else [],
            counterparty_network_report=counterparty_network_report,
        ),
        "counterparty_edges": _counterparty_edges_for_case(
            entity_id=_clean_text(selected_case.get("entity_id")),
            top_edges=list(counterparty_network_report.get("top_edges", [])) if isinstance(counterparty_network_report.get("top_edges"), list) else [],
        ),
        "analyst_questions": _analyst_questions(
            typologies=list(selected_case.get("typologies", [])),
            domain_focus=_clean_text(aml_domain_contract.get("domain_focus")),
        ),
        "recommended_next_steps": _recommended_next_steps(
            typologies=list(selected_case.get("typologies", [])),
            review_action=_clean_text(selected_case.get("review_action")),
        ),
        "evidence_refs": [
            "entity_graph_profile.json",
            "counterparty_network_report.json",
            "typology_detection_report.json",
            "subgraph_risk_report.json",
            "entity_case_expansion.json",
            "alert_queue_policy.json",
            "alert_queue_rankings.json",
            "analyst_review_scorecard.json",
        ],
        "summary": (
            f"Relaytic-AML recommends `{_clean_text(selected_case.get('review_action')) or 'unknown'}` for case "
            f"`{_clean_text(selected_case.get('case_id')) or 'unknown'}` because structural risk, typology support, and "
            "review-budget pressure jointly moved it to the front of the queue."
        ),
    }
    sensitivity_rows = []
    for fraction in _scenario_fractions(review_fraction):
        scenario_capacity = max(1, min(len(queue_rows), math.ceil(len(queue_rows) * fraction)))
        top_slice = queue_rows[:scenario_capacity]
        sensitivity_rows.append(
            {
                "review_fraction": fraction,
                "review_capacity_cases": scenario_capacity,
                "avg_priority_topk": round(
                    sum(float(row.get("priority_score", 0.0) or 0.0) for row in top_slice) / max(len(top_slice), 1),
                    4,
                ),
                "top_case_ids": [str(row.get("case_id")) for row in top_slice[:3] if str(row.get("case_id")).strip()],
                "typology_coverage": len(
                    {
                        str(typology)
                        for row in top_slice
                        for typology in row.get("typologies", [])
                        if str(typology).strip()
                    }
                ),
            }
        )
    sensitivity = {
        "schema_version": REVIEW_CAPACITY_SENSITIVITY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "selected_review_fraction": review_fraction,
        "rows": sensitivity_rows,
        "summary": (
            f"Relaytic-AML compared `{len(sensitivity_rows)}` review-capacity scenario(s) so operators can see how the queue "
            "changes when analyst bandwidth changes."
        ),
    }
    return {
        "alert_queue_policy": policy,
        "alert_queue_rankings": rankings,
        "analyst_review_scorecard": scorecard,
        "case_packet": case_packet,
        "review_capacity_sensitivity": sensitivity,
    }


def _inactive_casework_artifacts(*, generated_at: str, summary: str, status: str = "not_applicable") -> dict[str, dict[str, Any]]:
    base = {
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
    }
    return {
        "alert_queue_policy": {
            "schema_version": ALERT_QUEUE_POLICY_SCHEMA_VERSION,
            **base,
            "review_budget_fraction": None,
            "review_capacity_cases": 0,
        },
        "alert_queue_rankings": {
            "schema_version": ALERT_QUEUE_RANKINGS_SCHEMA_VERSION,
            **base,
            "queue_count": 0,
            "review_capacity_cases": 0,
            "ranking": [],
        },
        "analyst_review_scorecard": {
            "schema_version": ANALYST_REVIEW_SCORECARD_SCHEMA_VERSION,
            **base,
            "total_case_count": 0,
            "review_capacity_cases": 0,
        },
        "case_packet": {
            "schema_version": CASE_PACKET_SCHEMA_VERSION,
            **base,
            "case_id": None,
            "focal_entity": None,
            "analyst_questions": [],
            "recommended_next_steps": [],
            "evidence_refs": [],
        },
        "review_capacity_sensitivity": {
            "schema_version": REVIEW_CAPACITY_SENSITIVITY_SCHEMA_VERSION,
            **base,
            "selected_review_fraction": None,
            "rows": [],
        },
    }


def _build_queue_rows(
    *,
    high_risk_entities: list[dict[str, Any]],
    typology_hits: list[dict[str, Any]],
    entity_case_expansion: dict[str, Any],
    counterparty_network_report: dict[str, Any],
) -> list[dict[str, Any]]:
    focal_entity = _clean_text(entity_case_expansion.get("focal_entity"))
    expanded_entities = {
        _clean_text(item.get("entity_id")): _clean_text(item.get("role"))
        for item in entity_case_expansion.get("expanded_entities", [])
        if isinstance(item, dict) and _clean_text(item.get("entity_id"))
    } if isinstance(entity_case_expansion.get("expanded_entities"), list) else {}
    top_edges = list(counterparty_network_report.get("top_edges", [])) if isinstance(counterparty_network_report.get("top_edges"), list) else []

    queue_rows: list[dict[str, Any]] = []
    for index, raw_entity in enumerate(high_risk_entities, start=1):
        entity_id = _clean_text(raw_entity.get("entity_id"))
        if not entity_id:
            continue
        entity_typologies = [
            _clean_text(hit.get("typology"))
            for hit in typology_hits
            if _clean_text(hit.get("focal_entity")) == entity_id and _clean_text(hit.get("typology"))
        ]
        related_edges = _counterparty_edges_for_case(entity_id=entity_id, top_edges=top_edges)
        structural_support = min(1.0, len(related_edges) / 4.0)
        focal_bonus = 1.0 if entity_id == focal_entity else 0.0
        priority_score = round(
            min(
                1.0,
                0.55 * _safe_float(raw_entity.get("risk_score"))
                + 0.20 * min(1.0, len(entity_typologies) / 3.0)
                + 0.15 * structural_support
                + 0.10 * focal_bonus,
            ),
            4,
        )
        reason_codes = []
        if entity_id == focal_entity:
            reason_codes.append("focal_entity")
        if entity_typologies:
            reason_codes.append("typology_signal")
        if _safe_float(raw_entity.get("risk_score")) >= 0.5:
            reason_codes.append("high_structural_risk")
        if structural_support > 0.0:
            reason_codes.append("counterparty_support")
        queue_rows.append(
            {
                "rank": index,
                "case_id": f"case_{entity_id.lower()}",
                "entity_id": entity_id,
                "priority_score": priority_score,
                "risk_score": round(_safe_float(raw_entity.get("risk_score")), 4),
                "tx_count": int(raw_entity.get("tx_count", 0) or 0),
                "neighbor_count": int(raw_entity.get("neighbor_count", 0) or 0),
                "suspicious_rate": round(_safe_float(raw_entity.get("suspicious_rate")), 4),
                "entity_role": expanded_entities.get(entity_id) or ("focal" if entity_id == focal_entity else "candidate"),
                "typologies": entity_typologies,
                "typology_count": len(entity_typologies),
                "reason_codes": reason_codes,
                "counterparty_count": len(related_edges),
                "summary": (
                    f"Entity `{entity_id}` carries structural risk `{priority_score:.2f}` with `{len(entity_typologies)}` typology hit(s) "
                    f"and `{len(related_edges)}` visible counterparty edge(s)."
                ),
            }
        )
    return sorted(queue_rows, key=lambda item: (float(item.get("priority_score", 0.0)), int(item.get("tx_count", 0))), reverse=True)


def _assign_review_actions(*, queue_rows: list[dict[str, Any]], review_capacity_cases: int) -> list[dict[str, Any]]:
    assigned: list[dict[str, Any]] = []
    monitor_cutoff = max(review_capacity_cases + 1, review_capacity_cases * 2)
    for rank, row in enumerate(queue_rows, start=1):
        item = dict(row)
        item["rank"] = rank
        if rank <= review_capacity_cases:
            item["review_action"] = "review_now"
        elif rank <= monitor_cutoff:
            item["review_action"] = "monitor"
        else:
            item["review_action"] = "defer"
        assigned.append(item)
    return assigned


def _resolve_review_fraction(
    *,
    operating_point_contract: dict[str, Any],
    review_budget_optimization_report: dict[str, Any],
) -> float:
    for source in (
        operating_point_contract.get("selected_review_fraction"),
        operating_point_contract.get("review_budget_fraction"),
        review_budget_optimization_report.get("selected_review_fraction"),
        review_budget_optimization_report.get("review_budget_fraction"),
    ):
        value = _safe_float(source)
        if value > 0.0:
            return min(0.95, max(0.05, value))
    return 0.15


def _scenario_fractions(selected_fraction: float) -> list[float]:
    values = {0.05, 0.10, 0.20, 0.30, round(float(selected_fraction), 2)}
    return sorted(value for value in values if 0.01 <= value <= 0.95)


def _counterparty_edges_for_case(*, entity_id: str | None, top_edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not entity_id:
        return []
    rows = [
        dict(item)
        for item in top_edges
        if isinstance(item, dict)
        and (
            _clean_text(item.get("source")) == entity_id
            or _clean_text(item.get("destination")) == entity_id
        )
    ]
    return rows[:6]


def _linked_entities_for_case(
    *,
    entity_id: str | None,
    expanded_entities: list[dict[str, Any]],
    counterparty_network_report: dict[str, Any],
) -> list[dict[str, Any]]:
    if not entity_id:
        return []
    top_edges = list(counterparty_network_report.get("top_edges", [])) if isinstance(counterparty_network_report.get("top_edges"), list) else []
    linked = []
    seen: set[str] = set()
    for edge in _counterparty_edges_for_case(entity_id=entity_id, top_edges=top_edges):
        for node in (_clean_text(edge.get("source")), _clean_text(edge.get("destination"))):
            if node and node != entity_id and node not in seen:
                linked.append({"entity_id": node, "role": "counterparty"})
                seen.add(node)
    for item in expanded_entities:
        if not isinstance(item, dict):
            continue
        node = _clean_text(item.get("entity_id"))
        if node and node != entity_id and node not in seen:
            linked.append({"entity_id": node, "role": _clean_text(item.get("role")) or "neighbor"})
            seen.add(node)
    return linked[:8]


def _analyst_questions(*, typologies: list[str], domain_focus: str | None) -> list[str]:
    questions = [
        "Which linked entities share infrastructure or counterparties with the focal case?",
        "Does the visible traffic pattern justify immediate review under the current analyst budget?",
    ]
    if any(typology == "smurfing" for typology in typologies):
        questions.append("Are many low-value inbound events being consolidated into one focal entity?")
    if any(typology in {"layering", "peel_chain"} for typology in typologies):
        questions.append("Do the outgoing paths suggest layering or peel-chain behavior that should be escalated?")
    if domain_focus == "payment_fraud":
        questions.append("Is this entity linked to payment-fraud abuse patterns such as rapid cash-out or account takeover?")
    return questions[:4]


def _recommended_next_steps(*, typologies: list[str], review_action: str | None) -> list[str]:
    steps = []
    if review_action == "review_now":
        steps.append("Send the case packet to an analyst immediately.")
    elif review_action == "monitor":
        steps.append("Keep the case on a watchlist and wait for one more linked event before escalation.")
    else:
        steps.append("Defer manual review and keep only lightweight monitoring on the entity.")
    if "smurfing" in typologies:
        steps.append("Check whether many inbound counterparties share hidden identifiers or timing windows.")
    if any(item in typologies for item in ("layering", "peel_chain", "funnel_accounts")):
        steps.append("Inspect outgoing counterparties and movement depth before approving the next threshold change.")
    return steps[:4]


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_float(value: Any) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(result) or math.isinf(result):
        return 0.0
    return result


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

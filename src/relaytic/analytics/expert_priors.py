"""Deterministic expert-prior inference for Relaytic specialists."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .task_detection import is_classification_task


@dataclass(frozen=True)
class KnowledgeSource:
    """One provenance-carrying source of specialist knowledge."""

    source_type: str
    strength: str
    evidence: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExpertPriorProfile:
    """Structured deterministic priors for one inferred domain archetype."""

    domain_archetype: str
    confidence: float
    task_type: str | None
    objective_bias: dict[str, float]
    recommended_primary_metric: str | None
    threshold_policy_hint: str | None
    model_family_bias: list[str]
    feature_priorities: list[str]
    additional_data_needs: list[str]
    risks: list[str]
    questions: list[str]
    knowledge_sources: list[KnowledgeSource]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["knowledge_sources"] = [item.to_dict() for item in self.knowledge_sources]
        return payload


_ARCHETYPE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "manufacturing_quality": {
        "keywords": (
            "quality",
            "yield",
            "scrap",
            "defect",
            "off spec",
            "off-spec",
            "batch",
            "lot",
            "wafer",
            "line",
            "process",
            "sensor",
        ),
        "objective_bias": {"value": 0.1, "reliability": 0.08, "interpretability": 0.03},
        "classification_metric": "pr_auc",
        "regression_metric": "mae",
        "threshold_policy_hint": "favor_recall",
        "classification_models": ["boosted_tree_classifier", "bagged_tree_classifier", "logistic"],
        "regression_models": ["linear_ridge", "boosted_tree", "lagged_linear"],
        "feature_priorities": [
            "stability_and_drift_features",
            "group_history_features",
            "raw_auditable_features",
        ],
        "additional_data_needs": [
            "regime_change_examples",
            "boundary_batches",
            "operator_action_outcomes",
        ],
        "risks": [
            "Process drift or regime changes can invalidate a narrow static route.",
            "Post-outcome inspection columns are a common leakage source in quality data.",
        ],
        "questions": [
            "How early before the quality event must Relaytic issue a useful decision?",
        ],
    },
    "fraud_risk": {
        "keywords": (
            "fraud",
            "chargeback",
            "abuse",
            "scam",
            "transaction",
            "merchant",
            "card",
            "device risk",
            "velocity",
            "payment",
        ),
        "objective_bias": {"value": 0.14, "reliability": 0.1},
        "classification_metric": "pr_auc",
        "regression_metric": "mae",
        "threshold_policy_hint": "favor_pr_auc",
        "classification_models": ["boosted_tree_classifier", "bagged_tree_classifier", "logistic"],
        "regression_models": ["linear_ridge", "boosted_tree"],
        "feature_priorities": [
            "group_history_features",
            "pairwise_interactions",
            "raw_auditable_features",
        ],
        "additional_data_needs": [
            "hard_negative_examples",
            "confirmed_fraud_labels",
            "entity_history_features",
        ],
        "risks": [
            "Rare-event label imbalance can make headline accuracy actively misleading.",
            "Entity leakage and duplicate-identity signals can inflate offline validation.",
        ],
        "questions": [
            "What false-positive review burden is acceptable relative to missed fraud?",
        ],
    },
    "anomaly_monitoring": {
        "keywords": (
            "anomaly",
            "outlier",
            "fault",
            "alert",
            "attack",
            "intrusion",
            "incident",
            "monitor",
        ),
        "objective_bias": {"reliability": 0.12, "value": 0.08},
        "classification_metric": "pr_auc",
        "regression_metric": "mae",
        "threshold_policy_hint": "favor_recall",
        "classification_models": ["boosted_tree_classifier", "bagged_tree_classifier", "logistic"],
        "regression_models": ["linear_ridge", "boosted_tree"],
        "feature_priorities": [
            "stability_and_drift_features",
            "lagged_signals",
            "raw_auditable_features",
        ],
        "additional_data_needs": [
            "hard_negative_examples",
            "rare_event_examples",
            "regime_change_examples",
        ],
        "risks": [
            "Anomaly routes often fail first on distribution shift and alert fatigue.",
            "A proxy alert flag may be easier to predict than the underlying failure state.",
        ],
        "questions": [
            "Is missing an event worse than generating excess alerts in this workflow?",
        ],
    },
    "churn_retention": {
        "keywords": (
            "churn",
            "attrition",
            "retention",
            "cancel",
            "cancellation",
            "unsubscribe",
            "subscriber",
            "customer leave",
        ),
        "objective_bias": {"value": 0.12, "interpretability": 0.05},
        "classification_metric": "pr_auc",
        "regression_metric": "mae",
        "threshold_policy_hint": "favor_recall",
        "classification_models": ["logistic", "boosted_tree_classifier", "bagged_tree_classifier"],
        "regression_models": ["linear_ridge", "boosted_tree"],
        "feature_priorities": [
            "group_history_features",
            "missingness_indicators",
            "raw_auditable_features",
        ],
        "additional_data_needs": [
            "customer_history_features",
            "intervention_outcomes",
        ],
        "risks": [
            "Churn labels can be lagged and sensitive to definition drift.",
        ],
        "questions": [
            "Is the main goal ranking intervention candidates or making a hard automated decision?",
        ],
    },
    "demand_forecasting": {
        "keywords": (
            "forecast",
            "demand",
            "inventory",
            "sales",
            "orders",
            "volume",
            "stockout",
            "units sold",
        ),
        "objective_bias": {"value": 0.1, "reliability": 0.08},
        "classification_metric": "f1",
        "regression_metric": "mae",
        "threshold_policy_hint": None,
        "classification_models": ["logistic", "bagged_tree_classifier"],
        "regression_models": ["lagged_linear", "lagged_tree", "boosted_tree"],
        "feature_priorities": [
            "lagged_signals",
            "rolling_statistics",
            "stability_and_drift_features",
        ],
        "additional_data_needs": [
            "calendar_context",
            "promotion_flags",
            "stockout_annotations",
        ],
        "risks": [
            "Forecasting routes degrade quickly when seasonality or operational regime shifts change.",
        ],
        "questions": [
            "What forecast horizon matters operationally: next hour, day, or batch?",
        ],
    },
    "pricing_estimation": {
        "keywords": (
            "price",
            "pricing",
            "quote",
            "revenue",
            "margin",
            "cost",
            "premium",
        ),
        "objective_bias": {"value": 0.1, "interpretability": 0.06},
        "classification_metric": "f1",
        "regression_metric": "mae",
        "threshold_policy_hint": None,
        "classification_models": ["logistic", "boosted_tree_classifier"],
        "regression_models": ["linear_ridge", "boosted_tree", "bagged_tree_ensemble"],
        "feature_priorities": [
            "pairwise_interactions",
            "raw_auditable_features",
            "missingness_indicators",
        ],
        "additional_data_needs": [
            "market_context",
            "historical_quotes",
        ],
        "risks": [
            "Pricing targets often encode policy changes and market regime shifts.",
        ],
        "questions": [
            "Should the route optimize calibration, ranking quality, or absolute error?",
        ],
    },
}


def infer_expert_priors(
    *,
    dataset_profile: dict[str, Any],
    primary_target: dict[str, Any],
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
    run_brief: dict[str, Any],
    data_origin: dict[str, Any],
) -> ExpertPriorProfile:
    """Infer deterministic expert priors from the current artifact graph."""

    task_type = str(primary_target.get("task_type", "")).strip() or str(task_brief.get("task_type_hint", "")).strip() or None
    task_family = "classification" if is_classification_task(task_type) else "regression"
    corpus = _build_corpus(
        dataset_profile=dataset_profile,
        primary_target=primary_target,
        task_brief=task_brief,
        domain_brief=domain_brief,
        run_brief=run_brief,
        data_origin=data_origin,
    )

    target_text = " ".join(
        [
            str(primary_target.get("target_column", "")).strip(),
            str(task_brief.get("problem_statement", "")).strip(),
            str(domain_brief.get("target_meaning", "")).strip(),
        ]
    ).lower()
    schema_evidence = _schema_evidence(dataset_profile)
    operator_evidence = _operator_evidence(task_brief, domain_brief, run_brief, data_origin)

    explicit_hint = str(task_brief.get("domain_archetype_hint", "")).strip()
    if explicit_hint and explicit_hint in _ARCHETYPE_DEFINITIONS:
        selected_name = explicit_hint
        confidence = 0.94
        matched_terms = [f"operator explicitly hinted domain archetype `{explicit_hint}`"]
    else:
        ranking = []
        for archetype, config in _ARCHETYPE_DEFINITIONS.items():
            score, matched_terms = _score_archetype(
                archetype=archetype,
                config=config,
                corpus=corpus,
                target_text=target_text,
                task_type=task_type,
                dataset_profile=dataset_profile,
            )
            ranking.append((archetype, score, matched_terms))
        ranking.sort(key=lambda item: (-item[1], item[0]))
        best_name, best_score, matched_terms = ranking[0]
        if best_score <= 0.0:
            selected_name = "generic_tabular"
            confidence = 0.35
            matched_terms = ["No strong domain archetype pattern was detected; using generic tabular priors."]
        else:
            selected_name = best_name
            next_best = ranking[1][1] if len(ranking) > 1 else 0.0
            confidence = max(0.45, min(0.96, 0.52 + best_score * 0.08 + max(0.0, best_score - next_best) * 0.05))

    if selected_name == "generic_tabular":
        objective_bias = {"accuracy": 0.04}
        recommended_primary_metric = "f1" if task_family == "classification" else "mae"
        threshold_policy_hint = "favor_f1" if task_family == "classification" else None
        model_family_bias = ["logistic"] if task_family == "classification" else ["linear_ridge"]
        feature_priorities = ["raw_auditable_features"]
        additional_data_needs: list[str] = []
        risks: list[str] = []
        questions: list[str] = []
    else:
        config = _ARCHETYPE_DEFINITIONS[selected_name]
        objective_bias = dict(config["objective_bias"])
        recommended_primary_metric = (
            str(config["classification_metric"])
            if task_family == "classification"
            else str(config["regression_metric"])
        )
        threshold_policy_hint = config["threshold_policy_hint"] if task_family == "classification" else None
        model_family_bias = (
            list(config["classification_models"])
            if task_family == "classification"
            else list(config["regression_models"])
        )
        feature_priorities = list(config["feature_priorities"])
        additional_data_needs = list(config["additional_data_needs"])
        risks = list(config["risks"])
        questions = list(config["questions"])

    if str(dataset_profile.get("data_mode", "")).strip() == "time_series":
        feature_priorities.insert(0, "lagged_signals")
    if float(primary_target.get("minority_class_fraction") or 1.0) < 0.12 and task_family == "classification":
        objective_bias["value"] = round(float(objective_bias.get("value", 0.0)) + 0.04, 4)
        objective_bias["reliability"] = round(float(objective_bias.get("reliability", 0.0)) + 0.04, 4)
        additional_data_needs.insert(0, "rare_event_examples")
        risks.insert(0, "Class imbalance can make raw accuracy a misleading measure of usefulness.")

    knowledge_sources = [
        KnowledgeSource(
            source_type="dataset_schema",
            strength=_strength_label(len(schema_evidence)),
            evidence=schema_evidence or ["Dataset schema was available but did not provide strong domain-specific cues."],
        ),
        KnowledgeSource(
            source_type="operator_context",
            strength=_strength_label(len(operator_evidence)),
            evidence=operator_evidence or ["No rich operator context was available beyond the current run brief."],
        ),
        KnowledgeSource(
            source_type="deterministic_expert_priors",
            strength=_strength_label(len(matched_terms)),
            evidence=matched_terms,
        ),
    ]
    summary = (
        f"Relaytic matched the run to the deterministic `{selected_name}` archetype with "
        f"confidence {confidence:.2f} and will bias toward `{recommended_primary_metric}`."
    )
    return ExpertPriorProfile(
        domain_archetype=selected_name,
        confidence=round(confidence, 4),
        task_type=task_type,
        objective_bias={key: round(float(value), 4) for key, value in objective_bias.items()},
        recommended_primary_metric=recommended_primary_metric,
        threshold_policy_hint=threshold_policy_hint,
        model_family_bias=_dedupe_strings(model_family_bias),
        feature_priorities=_dedupe_strings(feature_priorities),
        additional_data_needs=_dedupe_strings(additional_data_needs),
        risks=_dedupe_strings(risks),
        questions=_dedupe_strings(questions),
        knowledge_sources=knowledge_sources,
        summary=summary,
    )


def _build_corpus(
    *,
    dataset_profile: dict[str, Any],
    primary_target: dict[str, Any],
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
    run_brief: dict[str, Any],
    data_origin: dict[str, Any],
) -> str:
    parts: list[str] = []
    parts.extend(_string_list(dataset_profile.get("candidate_target_columns")))
    parts.extend(_string_list(dataset_profile.get("numeric_columns")))
    parts.extend(_string_list(dataset_profile.get("categorical_columns")))
    parts.extend(_string_list(dataset_profile.get("entity_key_candidates")))
    parts.extend(_string_list(dataset_profile.get("suspicious_columns")))
    parts.extend(
        [
            str(primary_target.get("target_column", "")).strip(),
            str(task_brief.get("problem_statement", "")).strip(),
            str(task_brief.get("decision_type", "")).strip(),
            str(task_brief.get("prediction_horizon", "")).strip(),
            str(task_brief.get("task_type_hint", "")).strip(),
            str(task_brief.get("domain_archetype_hint", "")).strip(),
            str(domain_brief.get("summary", "")).strip(),
            str(domain_brief.get("system_name", "")).strip(),
            str(domain_brief.get("target_meaning", "")).strip(),
            str(run_brief.get("objective", "")).strip(),
            str(data_origin.get("source_name", "")).strip(),
            str(data_origin.get("source_type", "")).strip(),
        ]
    )
    parts.extend(_string_list(task_brief.get("success_criteria")))
    parts.extend(_string_list(task_brief.get("failure_costs")))
    parts.extend(_string_list(run_brief.get("success_criteria")))
    parts.extend(_string_list(run_brief.get("binding_constraints")))
    return " ".join(part for part in parts if part).lower()


def _schema_evidence(dataset_profile: dict[str, Any]) -> list[str]:
    evidence: list[str] = []
    for key in ("candidate_target_columns", "entity_key_candidates", "suspicious_columns"):
        values = _string_list(dataset_profile.get(key))
        if values:
            evidence.append(f"{key}: {', '.join(values[:4])}")
    data_mode = str(dataset_profile.get("data_mode", "")).strip()
    if data_mode:
        evidence.append(f"data_mode: {data_mode}")
    return evidence


def _operator_evidence(
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
    run_brief: dict[str, Any],
    data_origin: dict[str, Any],
) -> list[str]:
    evidence: list[str] = []
    for key, payload in (
        ("problem_statement", task_brief),
        ("target_meaning", domain_brief),
        ("summary", domain_brief),
        ("objective", run_brief),
        ("source_name", data_origin),
    ):
        value = str(payload.get(key, "")).strip()
        if value:
            evidence.append(f"{key}: {value}")
    return evidence


def _score_archetype(
    *,
    archetype: str,
    config: dict[str, Any],
    corpus: str,
    target_text: str,
    task_type: str | None,
    dataset_profile: dict[str, Any],
) -> tuple[float, list[str]]:
    score = 0.0
    evidence: list[str] = []
    for keyword in config["keywords"]:
        if keyword in target_text:
            score += 1.3
            evidence.append(f"target/context matched `{keyword}`")
        elif keyword in corpus:
            score += 0.9
            evidence.append(f"context matched `{keyword}`")
    if archetype in {"fraud_risk", "anomaly_monitoring"} and task_type in {"fraud_detection", "anomaly_detection"}:
        score += 1.4
        evidence.append(f"task_type `{task_type}` reinforced `{archetype}`")
    if archetype == "manufacturing_quality" and any(
        item in _string_list(dataset_profile.get("entity_key_candidates")) for item in ("batch_id", "lot_id")
    ):
        score += 0.4
        evidence.append("entity keys suggest grouped process data")
    if archetype == "demand_forecasting" and str(dataset_profile.get("data_mode", "")).strip() == "time_series":
        score += 0.4
        evidence.append("time-series structure reinforced a forecasting archetype")
    return score, evidence


def _strength_label(evidence_count: int) -> str:
    if evidence_count >= 4:
        return "strong"
    if evidence_count >= 2:
        return "moderate"
    return "weak"


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        stripped = str(value).strip()
        if not stripped:
            continue
        normalized = stripped.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(stripped)
    return result

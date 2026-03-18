"""Deterministic specialist agents and orchestration for Slice 03."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Any

import pandas as pd

from relaytic.analytics import assess_stationarity, infer_expert_priors, run_quality_checks
from relaytic.analytics.task_detection import assess_task_profile, is_classification_task
from relaytic.ingestion import load_tabular_data

from .models import (
    DATASET_PROFILE_SCHEMA_VERSION,
    DOMAIN_MEMO_SCHEMA_VERSION,
    FEATURE_STRATEGY_PROFILE_SCHEMA_VERSION,
    FOCUS_DEBATE_SCHEMA_VERSION,
    FOCUS_PROFILE_SCHEMA_VERSION,
    OBJECTIVE_HYPOTHESES_SCHEMA_VERSION,
    OPTIMIZATION_PROFILE_SCHEMA_VERSION,
    DatasetProfile,
    DomainMemo,
    FeatureStrategyProfile,
    FocusDebate,
    FocusProfile,
    InvestigationBundle,
    InvestigationControls,
    ObjectiveHypotheses,
    OptimizationProfile,
    SpecialistTrace,
    build_investigation_controls_from_policy,
)
from .semantic import InvestigationLocalAdvisor, build_local_advisor


TARGET_KEYWORDS = (
    "target",
    "label",
    "yield",
    "quality",
    "outcome",
    "result",
    "response",
    "score",
    "risk",
    "failure",
    "flag",
    "class",
    "status",
)
HIDDEN_KEY_KEYWORDS = ("id", "uuid", "guid", "serial", "record", "index")
ENTITY_KEY_KEYWORDS = (
    "batch",
    "lot",
    "run",
    "unit",
    "device",
    "asset",
    "machine",
    "customer",
    "user",
    "wafer",
    "line",
    "cell",
)
SUSPICIOUS_KEYWORDS = (
    "future",
    "next",
    "post",
    "actual",
    "prediction",
    "predict",
    "outcome",
    "result",
    "leak",
    "ground_truth",
    "label",
    "target",
)
LENSES = [
    "accuracy",
    "value",
    "reliability",
    "efficiency",
    "interpretability",
    "sustainability",
]


@dataclass
class _ScoutWorkspace:
    profile: DatasetProfile
    frame: pd.DataFrame


class ScoutAgent:
    """Deterministic evidence extractor for dataset inspection."""

    def __init__(self, *, controls: InvestigationControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        data_path: str,
        sheet_name: str | int | None,
        header_row: int | None,
        data_start_row: int | None,
        timestamp_column: str | None,
        context_bundle: dict[str, Any],
    ) -> _ScoutWorkspace:
        ingestion = load_tabular_data(
            data_path,
            sheet_name=sheet_name,
            header_row=header_row,
            data_start_row=data_start_row,
        )
        frame = ingestion.frame
        quality = run_quality_checks(frame, timestamp_column=timestamp_column)
        resolved_timestamp = quality.timestamp_column
        sample_period = _estimate_sample_period_seconds(frame, resolved_timestamp)
        data_mode = "time_series" if resolved_timestamp else "steady_state"
        numeric_columns = _detect_numeric_columns(
            frame,
            exclude={resolved_timestamp} if resolved_timestamp else set(),
        )
        categorical_columns = [
            column
            for column in frame.columns
            if column not in numeric_columns and column != resolved_timestamp
        ]
        binary_like_columns = _binary_like_columns(frame)
        hidden_key_candidates = _hidden_key_candidates(frame, timestamp_column=resolved_timestamp)
        entity_key_candidates = _entity_key_candidates(
            frame,
            timestamp_column=resolved_timestamp,
            hidden_key_candidates=hidden_key_candidates,
        )
        suspicious_columns = _suspicious_columns(
            frame=frame,
            context_bundle=context_bundle,
            hidden_key_candidates=hidden_key_candidates,
        )
        candidate_target_columns = _candidate_target_columns(
            frame=frame,
            timestamp_column=resolved_timestamp,
            hidden_key_candidates=hidden_key_candidates,
            suspicious_columns=suspicious_columns,
            context_bundle=context_bundle,
        )
        stationarity_columns = [
            item for item in candidate_target_columns if item in numeric_columns
        ][:4] or numeric_columns[:4]
        stationarity = assess_stationarity(frame, signal_columns=stationarity_columns).to_dict()
        leakage_risks = _leakage_risks(
            profile_inputs={
                "hidden_key_candidates": hidden_key_candidates,
                "suspicious_columns": suspicious_columns,
                "timestamp_column": resolved_timestamp,
                "duplicate_timestamps": quality.duplicate_timestamps,
                "monotonic_timestamp": quality.monotonic_timestamp,
                "data_mode": data_mode,
            },
            controls=self.controls,
        )
        leakage_risk_level = _aggregate_risk_level(leakage_risks)
        summary = _build_scout_summary(
            row_count=len(frame),
            column_count=len(frame.columns),
            data_mode=data_mode,
            timestamp_column=resolved_timestamp,
            leakage_risk_level=leakage_risk_level,
            candidate_target_columns=candidate_target_columns,
        )
        trace = SpecialistTrace(
            agent="scout",
            operating_mode="deterministic_only",
            llm_used=False,
            llm_status="not_requested",
            deterministic_evidence=[
                "ingestion_metadata",
                "quality_checks",
                "stationarity_heuristics",
                "column_name_risk_scoring",
            ],
            advisory_notes=["Scout facts are always derived from deterministic analysis."],
        )
        profile = DatasetProfile(
            schema_version=DATASET_PROFILE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            source_path=str(ingestion.source_path),
            file_type=ingestion.file_type,
            selected_sheet=ingestion.selected_sheet,
            header_row=int(ingestion.inferred_header.header_row),
            data_start_row=int(ingestion.inferred_header.data_start_row),
            row_count=int(len(frame)),
            column_count=int(len(frame.columns)),
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            binary_like_columns=binary_like_columns,
            candidate_target_columns=candidate_target_columns,
            hidden_key_candidates=hidden_key_candidates,
            entity_key_candidates=entity_key_candidates,
            suspicious_columns=suspicious_columns,
            leakage_risk_level=leakage_risk_level,
            leakage_risks=leakage_risks,
            quality_warnings=list(quality.warnings),
            completeness_score=float(quality.completeness_score),
            missing_fraction_by_column={
                key: float(value) for key, value in quality.missing_fraction_by_column.items()
            },
            duplicate_rows=int(quality.duplicate_rows),
            constant_columns=list(quality.constant_columns),
            extreme_outlier_columns=list(quality.extreme_outlier_columns),
            data_mode=data_mode,
            timestamp_column=resolved_timestamp,
            estimated_sample_period_seconds=sample_period,
            duplicate_timestamps=int(quality.duplicate_timestamps),
            monotonic_timestamp=quality.monotonic_timestamp,
            stationarity=stationarity,
            scout_summary=summary,
            trace=trace,
        )
        return _ScoutWorkspace(profile=profile, frame=frame)


class ScientistAgent:
    """Grounded hypothesis generator for task and route framing."""

    def __init__(
        self,
        *,
        controls: InvestigationControls,
        advisor: InvestigationLocalAdvisor | None = None,
    ) -> None:
        self.controls = controls
        self.advisor = advisor

    def run(
        self,
        *,
        dataset_profile: DatasetProfile,
        frame: pd.DataFrame,
        mandate_bundle: dict[str, Any],
        context_bundle: dict[str, Any],
    ) -> DomainMemo:
        task_brief = _bundle_item(context_bundle, "task_brief")
        domain_brief = _bundle_item(context_bundle, "domain_brief")
        data_origin = _bundle_item(context_bundle, "data_origin")
        run_brief = _bundle_item(mandate_bundle, "run_brief")

        target_candidates = _scientist_target_candidates(
            frame=frame,
            dataset_profile=dataset_profile,
            task_brief=task_brief,
            run_brief=run_brief,
        )
        primary_target = target_candidates[0] if target_candidates else {}
        expert_priors = infer_expert_priors(
            dataset_profile=dataset_profile.to_dict(),
            primary_target=primary_target,
            task_brief=task_brief,
            domain_brief=domain_brief,
            run_brief=run_brief,
            data_origin=data_origin,
        ).to_dict()
        route_hypotheses = _route_hypotheses(
            dataset_profile=dataset_profile,
            primary_target=primary_target,
        )
        split_hypotheses = _split_hypotheses(
            dataset_profile=dataset_profile,
            primary_target=primary_target,
        )
        feature_hypotheses = _feature_hypotheses(
            dataset_profile=dataset_profile,
            primary_target=primary_target,
        )
        additional_data_hypotheses = _additional_data_hypotheses(
            dataset_profile=dataset_profile,
            primary_target=primary_target,
        )
        unresolved_questions = _unresolved_questions(
            dataset_profile=dataset_profile,
            target_candidates=target_candidates,
            task_brief=task_brief,
            domain_brief=domain_brief,
        )
        domain_risks = _domain_risks(
            dataset_profile=dataset_profile,
            domain_brief=domain_brief,
        )
        domain_summary = _domain_summary(
            dataset_profile=dataset_profile,
            domain_brief=domain_brief,
            data_origin=data_origin,
        )
        operational_problem_statement = _operational_problem_statement(
            dataset_profile=dataset_profile,
            task_brief=task_brief,
            run_brief=run_brief,
            primary_target=primary_target,
        )
        route_hypotheses = _merge_expert_route_hypotheses(
            route_hypotheses=route_hypotheses,
            expert_priors=expert_priors,
            dataset_profile=dataset_profile,
        )
        feature_hypotheses.extend(_expert_feature_hypotheses(expert_priors))
        additional_data_hypotheses.extend(_expert_additional_data_hypotheses(expert_priors))
        unresolved_questions.extend(_string_list(expert_priors.get("questions")))
        domain_risks.extend(_string_list(expert_priors.get("risks")))
        domain_summary = _enrich_domain_summary(
            domain_summary=domain_summary,
            expert_priors=expert_priors,
        )
        llm_advisory: dict[str, Any] | None = None
        llm_status = "not_requested"
        advisory_notes: list[str] = []
        if self.advisor is not None:
            advisory = self.advisor.complete_json(
                task_name="scientist",
                system_prompt=(
                    "You are Relaytic's Scientist advisory module. "
                    "Read the structured dataset facts and operator context. "
                    "Return JSON with keys domain_summary, extra_questions, extra_risks, "
                    "feature_hints, and objective_clues. objective_clues must be a list of "
                    "objects with objective in [accuracy,value,reliability,efficiency,"
                    "interpretability,sustainability], delta in [-0.08,0.08], and reason."
                ),
                payload={
                    "dataset_profile": {
                        "data_mode": dataset_profile.data_mode,
                        "row_count": dataset_profile.row_count,
                        "column_count": dataset_profile.column_count,
                        "candidate_target_columns": dataset_profile.candidate_target_columns,
                        "leakage_risk_level": dataset_profile.leakage_risk_level,
                        "quality_warnings": dataset_profile.quality_warnings,
                    },
                    "task_brief": task_brief,
                    "domain_brief": domain_brief,
                    "data_origin": data_origin,
                    "target_candidates": target_candidates,
                },
            )
            llm_status = "advisory_used" if advisory.status == "ok" and advisory.payload else advisory.status
            if advisory.payload:
                llm_advisory = advisory.payload
                advisory_notes.extend(advisory.notes)
                candidate_summary = str(advisory.payload.get("domain_summary", "")).strip()
                if candidate_summary:
                    domain_summary = candidate_summary
                unresolved_questions.extend(_string_list(advisory.payload.get("extra_questions")))
                domain_risks.extend(_string_list(advisory.payload.get("extra_risks")))
                for hint in _string_list(advisory.payload.get("feature_hints")):
                    feature_hypotheses.append(
                        {
                            "name": "semantic_hint",
                            "priority": "advisory",
                            "source": "local_llm",
                            "rationale": hint,
                        }
                    )
            else:
                advisory_notes.extend(advisory.notes)
        trace = SpecialistTrace(
            agent="scientist",
            operating_mode="deterministic_plus_advisory"
            if self.advisor is not None
            else "deterministic_only",
            llm_used=llm_advisory is not None,
            llm_status=llm_status,
            deterministic_evidence=[
                "dataset_profile",
                "task_profile_inference",
                "route_and_split_heuristics",
            ],
            advisory_notes=advisory_notes,
        )
        summary = _scientist_summary(
            primary_target=primary_target,
            dataset_profile=dataset_profile,
            split_hypotheses=split_hypotheses,
            unresolved_questions=unresolved_questions,
            domain_archetype=str(expert_priors.get("domain_archetype", "generic_tabular")),
        )
        return DomainMemo(
            schema_version=DOMAIN_MEMO_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            operational_problem_statement=operational_problem_statement,
            domain_summary=domain_summary,
            domain_archetype=str(expert_priors.get("domain_archetype", "generic_tabular")),
            target_candidates=target_candidates,
            expert_priors=expert_priors,
            knowledge_sources=list(expert_priors.get("knowledge_sources", [])),
            route_hypotheses=route_hypotheses,
            split_hypotheses=split_hypotheses,
            feature_hypotheses=feature_hypotheses,
            additional_data_hypotheses=additional_data_hypotheses,
            unresolved_questions=_dedupe_strings(unresolved_questions),
            domain_risks=_dedupe_strings(domain_risks),
            llm_advisory=llm_advisory,
            scientist_summary=summary,
            trace=trace,
        )


class FocusCouncilAgent:
    """Structured objective resolver with deterministic scoring and optional bounded nudges."""

    def __init__(
        self,
        *,
        controls: InvestigationControls,
        policy: dict[str, Any],
        advisor: InvestigationLocalAdvisor | None = None,
    ) -> None:
        self.controls = controls
        self.policy = policy
        self.advisor = advisor

    def run(
        self,
        *,
        dataset_profile: DatasetProfile,
        domain_memo: DomainMemo,
        mandate_bundle: dict[str, Any],
        context_bundle: dict[str, Any],
    ) -> tuple[
        ObjectiveHypotheses,
        FocusDebate,
        FocusProfile,
        OptimizationProfile,
        FeatureStrategyProfile,
    ]:
        if not self.controls.focus_council_enabled:
            raise RuntimeError("Focus Council is disabled by policy.")

        work_preferences = _bundle_item(mandate_bundle, "work_preferences")
        run_brief = _bundle_item(mandate_bundle, "run_brief")
        lab_mandate = _bundle_item(mandate_bundle, "lab_mandate")
        task_brief = _bundle_item(context_bundle, "task_brief")
        domain_brief = _bundle_item(context_bundle, "domain_brief")

        lens_scores = _lens_scores(
            dataset_profile=dataset_profile,
            domain_memo=domain_memo,
            policy=self.policy,
            work_preferences=work_preferences,
            run_brief=run_brief,
            lab_mandate=lab_mandate,
            task_brief=task_brief,
            domain_brief=domain_brief,
        )
        focus_llm_advisory: dict[str, Any] | None = None
        llm_status = "not_requested"
        advisory_notes: list[str] = []
        if self.advisor is not None:
            advisory = self.advisor.complete_json(
                task_name="focus_council",
                system_prompt=(
                    "You are Relaytic's Focus Council advisory module. "
                    "Infer objective emphasis only from the provided structured evidence. "
                    "Return JSON with keys objective_clues, conflict_notes, and resolution_hint. "
                    "objective_clues must be a list of objects with objective in "
                    "[accuracy,value,reliability,efficiency,interpretability,sustainability], "
                    "delta in [-0.08,0.08], and reason."
                ),
                payload={
                    "dataset_profile": {
                        "data_mode": dataset_profile.data_mode,
                        "leakage_risk_level": dataset_profile.leakage_risk_level,
                        "quality_warnings": dataset_profile.quality_warnings,
                        "candidate_target_columns": dataset_profile.candidate_target_columns,
                    },
                    "domain_memo": {
                        "operational_problem_statement": domain_memo.operational_problem_statement,
                        "domain_summary": domain_memo.domain_summary,
                        "target_candidates": domain_memo.target_candidates,
                        "unresolved_questions": domain_memo.unresolved_questions,
                    },
                    "lab_mandate": lab_mandate,
                    "work_preferences": work_preferences,
                    "run_brief": run_brief,
                    "task_brief": task_brief,
                },
            )
            llm_status = "advisory_used" if advisory.status == "ok" and advisory.payload else advisory.status
            advisory_notes.extend(advisory.notes)
            if advisory.payload:
                focus_llm_advisory = advisory.payload
                _apply_objective_clues(lens_scores, advisory.payload.get("objective_clues"))

        activated_lenses = [lens for lens, score in lens_scores.items() if score >= 0.28]
        if "accuracy" not in activated_lenses:
            activated_lenses.append("accuracy")
        activated_lenses = [lens for lens in LENSES if lens in activated_lenses]
        normalized_weights = _normalize_weights({lens: lens_scores[lens] for lens in activated_lenses})
        ranking = sorted(normalized_weights.items(), key=lambda item: (-item[1], item[0]))
        top_margin = ranking[0][1] - (ranking[1][1] if len(ranking) > 1 else 0.0)
        resolution_mode = "single_focus" if top_margin >= 0.18 else "multi_objective_blend"
        primary_objective = _resolved_primary_objective(
            ranking=ranking,
            resolution_mode=resolution_mode,
            focus_llm_advisory=focus_llm_advisory,
        )
        secondary_objectives = [
            lens
            for lens, weight in ranking
            if lens != primary_objective and weight >= 0.18
        ][:2]
        mandate_conflicts = _mandate_conflicts(
            primary_objective=primary_objective,
            normalized_weights=normalized_weights,
            dataset_profile=dataset_profile,
            lab_mandate=lab_mandate,
            run_brief=run_brief,
        )
        if focus_llm_advisory:
            for note in _string_list(focus_llm_advisory.get("conflict_notes")):
                mandate_conflicts.append(
                    {
                        "severity": "advisory",
                        "type": "llm_note",
                        "message": note,
                    }
                )
        resolution_rationale = _resolution_rationale(
            primary_objective=primary_objective,
            secondary_objectives=secondary_objectives,
            resolution_mode=resolution_mode,
            dataset_profile=dataset_profile,
            domain_memo=domain_memo,
            focus_llm_advisory=focus_llm_advisory,
        )
        focus_trace = SpecialistTrace(
            agent="focus_council",
            operating_mode="deterministic_plus_advisory"
            if self.advisor is not None
            else "deterministic_only",
            llm_used=focus_llm_advisory is not None,
            llm_status=llm_status,
            deterministic_evidence=[
                "dataset_profile",
                "domain_memo",
                "mandate_context_corpus",
                "focus_scoring_rules",
            ],
            advisory_notes=advisory_notes,
        )

        objective_hypotheses = ObjectiveHypotheses(
            schema_version=OBJECTIVE_HYPOTHESES_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            hypotheses=[
                {
                    "objective": lens,
                    "score": round(lens_scores[lens], 4),
                    "normalized_weight": round(normalized_weights.get(lens, 0.0), 4),
                    "priority": (
                        "primary_candidate"
                        if lens == primary_objective
                        else "secondary_candidate"
                        if lens in secondary_objectives
                        else "supporting"
                    ),
                    "confidence": round(min(0.95, 0.45 + normalized_weights.get(lens, 0.0)), 4),
                    "evidence": _lens_arguments(
                        lens=lens,
                        dataset_profile=dataset_profile,
                        domain_memo=domain_memo,
                        run_brief=run_brief,
                        lab_mandate=lab_mandate,
                    ),
                }
                for lens in activated_lenses
            ],
            summary=f"Primary focus candidate: {primary_objective}.",
            trace=focus_trace,
        )
        focus_debate = FocusDebate(
            schema_version=FOCUS_DEBATE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            activated_lenses=activated_lenses,
            lens_positions=[
                {
                    "lens": lens,
                    "score": round(lens_scores[lens], 4),
                    "normalized_weight": round(normalized_weights.get(lens, 0.0), 4),
                    "arguments": _lens_arguments(
                        lens=lens,
                        dataset_profile=dataset_profile,
                        domain_memo=domain_memo,
                        run_brief=run_brief,
                        lab_mandate=lab_mandate,
                    ),
                    "counterweights": _lens_counterweights(
                        lens=lens,
                        normalized_weights=normalized_weights,
                        mandate_conflicts=mandate_conflicts,
                    ),
                }
                for lens in activated_lenses
            ],
            mandate_conflicts=mandate_conflicts,
            resolution={
                "mode": resolution_mode,
                "primary_objective": primary_objective,
                "secondary_objectives": secondary_objectives,
                "objective_weights": {key: round(value, 4) for key, value in normalized_weights.items()},
                "rationale": resolution_rationale,
            },
            llm_advisory=focus_llm_advisory,
            trace=focus_trace,
        )
        focus_profile = FocusProfile(
            schema_version=FOCUS_PROFILE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            primary_objective=primary_objective,
            secondary_objectives=secondary_objectives,
            resolution_mode=resolution_mode,
            active_lenses=activated_lenses,
            objective_weights={key: round(value, 4) for key, value in normalized_weights.items()},
            mandate_alignment={
                "status": "tension" if mandate_conflicts else "aligned",
                "conflicts": mandate_conflicts,
            },
            confidence=round(min(0.97, 0.55 + top_margin + normalized_weights.get(primary_objective, 0.0) * 0.2), 4),
            summary=resolution_rationale,
            trace=focus_trace,
        )
        optimization_profile = _optimization_profile(
            controls=self.controls,
            focus_trace=focus_trace,
            focus_profile=focus_profile,
            dataset_profile=dataset_profile,
            domain_memo=domain_memo,
        )
        feature_strategy_profile = _feature_strategy_profile(
            controls=self.controls,
            focus_trace=focus_trace,
            focus_profile=focus_profile,
            dataset_profile=dataset_profile,
            domain_memo=domain_memo,
            context_bundle=context_bundle,
        )
        return (
            objective_hypotheses,
            focus_debate,
            focus_profile,
            optimization_profile,
            feature_strategy_profile,
        )


def run_investigation(
    *,
    data_path: str,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    config_path: str | None = None,
    sheet_name: str | int | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
    timestamp_column: str | None = None,
) -> InvestigationBundle:
    """Run the full Slice 03 investigation pipeline."""
    controls = build_investigation_controls_from_policy(policy)
    advisor = build_local_advisor(controls=controls, config_path=config_path)
    scout = ScoutAgent(controls=controls)
    scientist = ScientistAgent(controls=controls, advisor=advisor)
    council = FocusCouncilAgent(controls=controls, policy=policy, advisor=advisor)
    scout_workspace = scout.run(
        data_path=data_path,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        context_bundle=context_bundle,
    )
    domain_memo = scientist.run(
        dataset_profile=scout_workspace.profile,
        frame=scout_workspace.frame,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    )
    (
        objective_hypotheses,
        focus_debate,
        focus_profile,
        optimization_profile,
        feature_strategy_profile,
    ) = council.run(
        dataset_profile=scout_workspace.profile,
        domain_memo=domain_memo,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    )
    return InvestigationBundle(
        dataset_profile=scout_workspace.profile,
        domain_memo=domain_memo,
        objective_hypotheses=objective_hypotheses,
        focus_debate=focus_debate,
        focus_profile=focus_profile,
        optimization_profile=optimization_profile,
        feature_strategy_profile=feature_strategy_profile,
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    value = bundle.get(key)
    return value if isinstance(value, dict) else {}


def _detect_numeric_columns(frame: pd.DataFrame, *, exclude: set[str]) -> list[str]:
    numeric_columns: list[str] = []
    for column in frame.columns:
        if column in exclude:
            continue
        series = pd.to_numeric(frame[column], errors="coerce")
        if float(series.notna().mean()) >= 0.8 and int(series.notna().sum()) >= 5:
            numeric_columns.append(str(column))
    return numeric_columns


def _binary_like_columns(frame: pd.DataFrame) -> list[str]:
    results: list[str] = []
    for column in frame.columns:
        unique = frame[column].dropna().astype("string").nunique()
        if unique == 2:
            results.append(str(column))
    return results


def _uniqueness_ratio(series: pd.Series) -> float:
    non_null = series.dropna()
    if len(non_null) == 0:
        return 0.0
    return float(non_null.nunique() / max(len(non_null), 1))


def _hidden_key_candidates(frame: pd.DataFrame, *, timestamp_column: str | None) -> list[str]:
    candidates: list[str] = []
    for column in frame.columns:
        if column == timestamp_column:
            continue
        lower = str(column).strip().lower()
        ratio = _uniqueness_ratio(frame[column])
        if ratio >= 0.98 and len(frame[column].dropna()) >= 10:
            candidates.append(str(column))
            continue
        if any(token in lower for token in HIDDEN_KEY_KEYWORDS) and ratio >= 0.5:
            candidates.append(str(column))
    return _dedupe_strings(candidates)


def _entity_key_candidates(
    frame: pd.DataFrame,
    *,
    timestamp_column: str | None,
    hidden_key_candidates: list[str],
) -> list[str]:
    candidates: list[str] = []
    hidden = set(hidden_key_candidates)
    for column in frame.columns:
        if column == timestamp_column or column in hidden:
            continue
        lower = str(column).strip().lower()
        ratio = _uniqueness_ratio(frame[column])
        distinct = int(frame[column].dropna().nunique())
        if any(token in lower for token in ENTITY_KEY_KEYWORDS):
            candidates.append(str(column))
            continue
        if 0.02 <= ratio <= 0.6 and 3 <= distinct <= max(10, int(len(frame) * 0.25)):
            candidates.append(str(column))
    return _dedupe_strings(candidates)


def _suspicious_columns(
    *,
    frame: pd.DataFrame,
    context_bundle: dict[str, Any],
    hidden_key_candidates: list[str],
) -> list[str]:
    domain_brief = _bundle_item(context_bundle, "domain_brief")
    candidates = _string_list(domain_brief.get("suspicious_columns"))
    for column in frame.columns:
        lower = str(column).strip().lower()
        if any(token in lower for token in SUSPICIOUS_KEYWORDS):
            candidates.append(str(column))
    candidates.extend(hidden_key_candidates)
    return _dedupe_strings(candidates)


def _candidate_target_columns(
    *,
    frame: pd.DataFrame,
    timestamp_column: str | None,
    hidden_key_candidates: list[str],
    suspicious_columns: list[str],
    context_bundle: dict[str, Any],
) -> list[str]:
    task_brief = _bundle_item(context_bundle, "task_brief")
    explicit_target = str(task_brief.get("target_column", "")).strip()
    hidden_keys = set(hidden_key_candidates)
    suspicious = set(suspicious_columns)
    scores: dict[str, float] = {}
    for column in frame.columns:
        if column == timestamp_column:
            continue
        name = str(column)
        lower = name.strip().lower()
        series = frame[column]
        non_null_ratio = float(series.notna().mean()) if len(series) else 0.0
        unique_ratio = _uniqueness_ratio(series)
        distinct = int(series.dropna().nunique())
        numeric_ratio = float(pd.to_numeric(series, errors="coerce").notna().mean()) if len(series) else 0.0
        score = 0.0
        if explicit_target and name == explicit_target:
            score += 100.0
        if any(token in lower for token in TARGET_KEYWORDS):
            score += 6.0
        if name in suspicious:
            score += 1.5
        if name not in hidden_keys:
            score += 1.2
        if non_null_ratio >= 0.6:
            score += 1.0
        if numeric_ratio >= 0.7 or distinct <= max(12, int(math.sqrt(max(len(frame), 1)))):
            score += 1.0
        if 0.01 <= unique_ratio <= 0.9:
            score += 0.8
        if score > 0:
            scores[name] = score
    if explicit_target and explicit_target not in scores and explicit_target in frame.columns:
        scores[explicit_target] = 100.0
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    targets = [name for name, _score in ranked[:5]]
    if not targets:
        numeric_candidates = _detect_numeric_columns(
            frame,
            exclude={timestamp_column} if timestamp_column else set(),
        )
        targets = numeric_candidates[:3]
    return _dedupe_strings(targets)


def _estimate_sample_period_seconds(frame: pd.DataFrame, timestamp_column: str | None) -> float | None:
    if not timestamp_column or timestamp_column not in frame.columns:
        return None
    series = frame[timestamp_column]
    numeric = pd.to_numeric(series, errors="coerce")
    if float(numeric.notna().mean()) >= 0.95:
        diffs = numeric.diff().dropna()
        positive = diffs[diffs > 0]
        if len(positive) >= 3:
            return float(positive.median())
        return None
    parsed = pd.to_datetime(series, errors="coerce")
    diffs = parsed.diff().dropna().dt.total_seconds()
    positive = diffs[diffs > 0]
    if len(positive) >= 3:
        return float(positive.median())
    return None


def _leakage_risks(
    *,
    profile_inputs: dict[str, Any],
    controls: InvestigationControls,
) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for column in _string_list(profile_inputs.get("suspicious_columns")):
        lower = column.lower()
        severity = "medium"
        reason = "Column name suggests a potential post-outcome or label-like field."
        if any(
            token in lower
            for token in ("future", "next", "post", "actual", "prediction", "ground_truth", "leak")
        ):
            severity = "high"
            reason = "Column name suggests future or post-outcome information."
        risks.append(
            {
                "kind": "column_name",
                "column": column,
                "severity": severity,
                "reason": reason,
            }
        )
    for column in _string_list(profile_inputs.get("hidden_key_candidates"))[:5]:
        risks.append(
            {
                "kind": "hidden_key",
                "column": column,
                "severity": "medium",
                "reason": "Near-unique identifiers can leak row identity and overfit badly.",
            }
        )
    if (
        profile_inputs.get("data_mode") == "time_series"
        and controls.strict_time_ordering
        and profile_inputs.get("monotonic_timestamp") is False
    ):
        risks.append(
            {
                "kind": "time_ordering",
                "severity": "high",
                "reason": "Timestamp ordering is not monotonic but policy requires strict time order.",
            }
        )
    duplicate_timestamps = int(profile_inputs.get("duplicate_timestamps") or 0)
    if profile_inputs.get("data_mode") == "time_series" and duplicate_timestamps > 0:
        risks.append(
            {
                "kind": "duplicate_timestamps",
                "severity": "medium",
                "reason": f"{duplicate_timestamps} duplicate timestamps were detected.",
            }
        )
    return risks


def _aggregate_risk_level(risks: list[dict[str, Any]]) -> str:
    severities = {str(item.get("severity", "")).strip().lower() for item in risks}
    if "high" in severities:
        return "high"
    if "medium" in severities:
        return "medium"
    return "low"


def _build_scout_summary(
    *,
    row_count: int,
    column_count: int,
    data_mode: str,
    timestamp_column: str | None,
    leakage_risk_level: str,
    candidate_target_columns: list[str],
) -> str:
    timestamp_note = f" Timestamp column: `{timestamp_column}`." if timestamp_column else ""
    target_note = (
        f" Candidate targets: {', '.join(candidate_target_columns[:3])}."
        if candidate_target_columns
        else ""
    )
    return (
        f"Scout inspected {row_count} rows and {column_count} columns, classified the dataset as "
        f"{data_mode}, and rated leakage risk `{leakage_risk_level}`.{timestamp_note}{target_note}"
    )


def _scientist_target_candidates(
    *,
    frame: pd.DataFrame,
    dataset_profile: DatasetProfile,
    task_brief: dict[str, Any],
    run_brief: dict[str, Any],
) -> list[dict[str, Any]]:
    explicit_target = str(task_brief.get("target_column") or run_brief.get("target_column") or "").strip()
    explicit_task_type_hint = str(task_brief.get("task_type_hint", "")).strip() or None
    candidates: list[dict[str, Any]] = []
    for column in dataset_profile.candidate_target_columns[:4]:
        if column not in frame.columns:
            continue
        profile = assess_task_profile(
            frame=frame,
            target_column=column,
            data_mode=dataset_profile.data_mode,
            task_type_hint=explicit_task_type_hint if explicit_target and column == explicit_target else None,
        )
        confidence = 0.55
        if column == explicit_target:
            confidence += 0.3
        if explicit_task_type_hint:
            if profile.task_type == explicit_task_type_hint:
                confidence += 0.07
            elif is_classification_task(profile.task_type) == is_classification_task(explicit_task_type_hint):
                confidence += 0.03
        if any(token in column.lower() for token in TARGET_KEYWORDS):
            confidence += 0.08
        if column in dataset_profile.hidden_key_candidates:
            confidence -= 0.25
        confidence = max(0.1, min(0.99, confidence))
        candidates.append(
            {
                "target_column": column,
                "task_type": profile.task_type,
                "task_family": profile.task_family,
                "confidence": round(confidence, 4),
                "positive_class_label": profile.positive_class_label,
                "minority_class_fraction": profile.minority_class_fraction,
                "recommended_split_strategy": profile.recommended_split_strategy,
                "rationale": profile.rationale,
            }
        )
    candidates.sort(key=lambda item: (-float(item["confidence"]), str(item["target_column"])))
    return candidates


def _route_hypotheses(
    *,
    dataset_profile: DatasetProfile,
    primary_target: dict[str, Any],
) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = [
        {
            "route_id": "deterministic_tabular_baseline",
            "title": "Deterministic local tabular baseline",
            "confidence": 0.72,
            "rationale": "Always keep a deterministic floor before any stronger optimization layer.",
        }
    ]
    task_type = str(primary_target.get("task_type", "")).strip()
    if dataset_profile.data_mode == "time_series":
        hypotheses.append(
            {
                "route_id": "temporal_lagged_route",
                "title": "Blocked temporal route with lagged features",
                "confidence": 0.84,
                "rationale": "Timestamped data and sample ordering suggest temporal structure.",
            }
        )
    else:
        hypotheses.append(
            {
                "route_id": "steady_state_route",
                "title": "Steady-state split-safe tabular route",
                "confidence": 0.8,
                "rationale": (
                    "No durable timestamp anchor was found, so the safe baseline is "
                    "split-safe tabular modeling."
                ),
            }
        )
    if is_classification_task(task_type):
        hypotheses.append(
            {
                "route_id": "calibrated_threshold_route",
                "title": "Calibrated classification route",
                "confidence": 0.77,
                "rationale": (
                    "Classification-like targets benefit from threshold-aware and "
                    "calibration-aware evaluation."
                ),
            }
        )
    return hypotheses


def _split_hypotheses(
    *,
    dataset_profile: DatasetProfile,
    primary_target: dict[str, Any],
) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = []
    task_type = str(primary_target.get("task_type", "")).strip()
    if dataset_profile.data_mode == "time_series":
        hypotheses.append(
            {
                "strategy": "blocked_time_order_70_15_15",
                "confidence": 0.9,
                "rationale": "Temporal order should be preserved to avoid look-ahead leakage.",
            }
        )
    elif is_classification_task(task_type):
        hypotheses.append(
            {
                "strategy": "stratified_deterministic_modulo_70_15_15",
                "confidence": 0.85,
                "rationale": (
                    "Class balance should be preserved while keeping the split deterministic."
                ),
            }
        )
    else:
        hypotheses.append(
            {
                "strategy": "deterministic_modulo_70_15_15",
                "confidence": 0.8,
                "rationale": (
                    "A deterministic split is the simplest safe baseline for "
                    "steady-state regression-like work."
                ),
            }
        )
    if dataset_profile.entity_key_candidates:
        hypotheses.append(
            {
                "strategy": "group_aware_holdout_candidate",
                "confidence": 0.64,
                "rationale": (
                    "Entity-like columns were detected; later slices should consider "
                    "group-aware evaluation to avoid identity leakage."
                ),
            }
        )
    return hypotheses


def _feature_hypotheses(
    *,
    dataset_profile: DatasetProfile,
    primary_target: dict[str, Any],
) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = []
    if dataset_profile.data_mode == "time_series":
        hypotheses.append(
            {
                "name": "lagged_signals",
                "priority": "high",
                "source": "deterministic",
                "rationale": (
                    "Temporal ordering suggests lagged and rolling features are "
                    "plausible first-class candidates."
                ),
            }
        )
    if any(value >= 0.05 for value in dataset_profile.missing_fraction_by_column.values()):
        hypotheses.append(
            {
                "name": "missingness_indicators",
                "priority": "medium",
                "source": "deterministic",
                "rationale": (
                    "Material missingness may itself carry signal and should not "
                    "be silently discarded."
                ),
            }
        )
    if len(dataset_profile.numeric_columns) >= 4:
        hypotheses.append(
            {
                "name": "pairwise_interactions",
                "priority": "medium",
                "source": "deterministic",
                "rationale": (
                    "Several numeric predictors are available, so low-order "
                    "interactions may be worthwhile."
                ),
            }
        )
    if dataset_profile.entity_key_candidates:
        hypotheses.append(
            {
                "name": "group_history_features",
                "priority": "medium",
                "source": "deterministic",
                "rationale": (
                    "Entity-like group columns may support historical aggregation "
                    "or grouped baselines."
                ),
            }
        )
    if not hypotheses:
        hypotheses.append(
            {
                "name": "raw_signal_baseline",
                "priority": "high",
                "source": "deterministic",
                "rationale": (
                    "Start with raw, auditable features because no stronger hypothesis "
                    "is yet justified."
                ),
            }
        )
    return hypotheses


def _additional_data_hypotheses(
    *,
    dataset_profile: DatasetProfile,
    primary_target: dict[str, Any],
) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = []
    task_type = str(primary_target.get("task_type", "")).strip()
    minority_fraction = primary_target.get("minority_class_fraction")
    if minority_fraction is not None and float(minority_fraction) < 0.15:
        hypotheses.append(
            {
                "need": "more_minority_examples",
                "priority": "high",
                "rationale": (
                    "Rare positive coverage is likely to limit reliable "
                    "classification behavior."
                ),
            }
        )
    if dataset_profile.row_count < 500:
        hypotheses.append(
            {
                "need": "more_representative_rows",
                "priority": "medium",
                "rationale": "Small sample size limits robust route comparison and confidence.",
            }
        )
    if dataset_profile.data_mode == "time_series" and dataset_profile.estimated_sample_period_seconds is None:
        hypotheses.append(
            {
                "need": "cleaner_timestamp_capture",
                "priority": "medium",
                "rationale": (
                    "Temporal data would benefit from a stable timestamp cadence "
                    "for downstream split and lag policy."
                ),
            }
        )
    if task_type in {"fraud_detection", "anomaly_detection"}:
        hypotheses.append(
            {
                "need": "hard_negative_examples",
                "priority": "high",
                "rationale": (
                    "Rare-event routes improve materially when they see more "
                    "boundary and hard-negative cases."
                ),
            }
        )
    return hypotheses


def _unresolved_questions(
    *,
    dataset_profile: DatasetProfile,
    target_candidates: list[dict[str, Any]],
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
) -> list[str]:
    questions: list[str] = []
    explicit_target = str(task_brief.get("target_column", "")).strip()
    if not explicit_target and len(target_candidates) > 1:
        questions.append(
            "Which candidate target should be treated as the primary outcome before planning begins?"
        )
    if dataset_profile.leakage_risk_level != "low" and not _string_list(domain_brief.get("forbidden_features")):
        questions.append(
            "Which suspicious or post-outcome columns must be explicitly forbidden from modeling?"
        )
    if not str(domain_brief.get("summary", "")).strip() or str(domain_brief.get("system_name", "")).strip() == "unspecified":
        questions.append("What physical or business system generated this dataset?")
    return questions


def _domain_risks(
    *,
    dataset_profile: DatasetProfile,
    domain_brief: dict[str, Any],
) -> list[str]:
    risks = list(dataset_profile.quality_warnings)
    risks.extend(_string_list(domain_brief.get("known_caveats")))
    for item in dataset_profile.leakage_risks[:5]:
        reason = str(item.get("reason", "")).strip()
        if reason:
            risks.append(reason)
    return _dedupe_strings(risks)


def _domain_summary(
    *,
    dataset_profile: DatasetProfile,
    domain_brief: dict[str, Any],
    data_origin: dict[str, Any],
) -> str:
    provided = str(domain_brief.get("summary", "")).strip()
    if provided and not provided.startswith("No domain brief provided."):
        return provided
    source_name = str(data_origin.get("source_name", "unspecified")).strip() or "unspecified"
    system_name = str(domain_brief.get("system_name", "unspecified")).strip() or "unspecified"
    return (
        f"Relaytic is operating in partially grounded mode on data from `{source_name}` for system "
        f"`{system_name}`. The dataset appears to be {dataset_profile.data_mode.replace('_', ' ')} "
        f"tabular data with {dataset_profile.row_count} rows and {dataset_profile.column_count} columns."
    )


def _operational_problem_statement(
    *,
    dataset_profile: DatasetProfile,
    task_brief: dict[str, Any],
    run_brief: dict[str, Any],
    primary_target: dict[str, Any],
) -> str:
    provided = str(task_brief.get("problem_statement", "")).strip()
    if provided and not provided.startswith("No task brief provided."):
        return provided
    target_column = str(primary_target.get("target_column", "")).strip() or str(run_brief.get("target_column", "")).strip()
    objective = str(run_brief.get("objective", "best_robust_pareto_front")).strip()
    if target_column:
        return (
            f"Predict or explain `{target_column}` from the available signals while preserving "
            f"a local-first, leakage-aware, reproducible route aligned to `{objective}`."
        )
    return (
        f"Infer the most plausible prediction target and safe baseline route from the dataset "
        f"while preserving a local-first, leakage-aware workflow aligned to `{objective}`."
    )


def _scientist_summary(
    *,
    primary_target: dict[str, Any],
    dataset_profile: DatasetProfile,
    split_hypotheses: list[dict[str, Any]],
    unresolved_questions: list[str],
    domain_archetype: str,
) -> str:
    target_text = str(primary_target.get("target_column", "unspecified")).strip() or "unspecified"
    split_text = str(split_hypotheses[0].get("strategy", "unspecified")).strip() if split_hypotheses else "unspecified"
    ambiguity_note = " Target ambiguity remains open." if unresolved_questions else ""
    return (
        f"Scientist currently prefers `{target_text}` as the working target, expects a "
        f"`{split_text}` split bias, matched the `{domain_archetype}` archetype, and will carry forward "
        f"{dataset_profile.leakage_risk_level} leakage caution.{ambiguity_note}"
    )


def _merge_expert_route_hypotheses(
    *,
    route_hypotheses: list[dict[str, Any]],
    expert_priors: dict[str, Any],
    dataset_profile: DatasetProfile,
) -> list[dict[str, Any]]:
    priors = _string_list(expert_priors.get("model_family_bias"))
    if not priors:
        return route_hypotheses
    route_hypotheses = list(route_hypotheses)
    route_hypotheses.append(
        {
            "route_id": "expert_prior_route_bias",
            "title": "Deterministic expert-prior route bias",
            "confidence": max(0.4, min(0.92, float(expert_priors.get("confidence", 0.5)) - 0.08)),
            "rationale": (
                f"Matched `{expert_priors.get('domain_archetype', 'generic_tabular')}`; plausible model families "
                f"include {', '.join(priors[:3])} for {dataset_profile.data_mode} data."
            ),
        }
    )
    return route_hypotheses


def _expert_feature_hypotheses(expert_priors: dict[str, Any]) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = []
    for family in _string_list(expert_priors.get("feature_priorities")):
        hypotheses.append(
            {
                "name": family,
                "priority": "high",
                "source": "deterministic_expert_prior",
                "rationale": (
                    f"The `{expert_priors.get('domain_archetype', 'generic_tabular')}` archetype treats "
                    f"`{family}` as a load-bearing feature family."
                ),
            }
        )
    return hypotheses


def _expert_additional_data_hypotheses(expert_priors: dict[str, Any]) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = []
    for need in _string_list(expert_priors.get("additional_data_needs")):
        hypotheses.append(
            {
                "need": need,
                "priority": "high",
                "rationale": (
                    f"The `{expert_priors.get('domain_archetype', 'generic_tabular')}` archetype often improves "
                    f"materially when `{need}` is available."
                ),
            }
        )
    return hypotheses


def _enrich_domain_summary(*, domain_summary: str, expert_priors: dict[str, Any]) -> str:
    summary = str(domain_summary).strip()
    archetype = str(expert_priors.get("domain_archetype", "")).strip()
    expert_summary = str(expert_priors.get("summary", "")).strip()
    if not archetype or not expert_summary:
        return summary
    if archetype in summary and expert_summary in summary:
        return summary
    return f"{summary} {expert_summary}".strip()


def _lens_scores(
    *,
    dataset_profile: DatasetProfile,
    domain_memo: DomainMemo,
    policy: dict[str, Any],
    work_preferences: dict[str, Any],
    run_brief: dict[str, Any],
    lab_mandate: dict[str, Any],
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
) -> dict[str, float]:
    compute_cfg = dict(policy.get("compute", {}))
    constraints_cfg = dict(policy.get("constraints", {}))
    texts = _context_corpus(
        work_preferences=work_preferences,
        run_brief=run_brief,
        lab_mandate=lab_mandate,
        task_brief=task_brief,
        domain_brief=domain_brief,
        domain_memo=domain_memo,
    )
    scores = {
        "accuracy": 0.45,
        "value": 0.2,
        "reliability": 0.22,
        "efficiency": 0.14,
        "interpretability": 0.1,
        "sustainability": 0.06,
    }
    scores["accuracy"] += _keyword_bonus(texts, ("accuracy", "performance", "best", "score"), 0.08)
    scores["accuracy"] += 0.05 if not task_brief.get("success_criteria") else 0.0

    scores["value"] += 0.12 if _string_list(task_brief.get("failure_costs")) else 0.0
    scores["value"] += 0.08 if _string_list(task_brief.get("success_criteria")) else 0.0
    scores["value"] += _keyword_bonus(
        texts,
        ("value", "cost", "scrap", "yield", "decision", "action", "revenue", "margin", "recall", "precision"),
        0.12,
    )

    scores["reliability"] += 0.15 if dataset_profile.leakage_risk_level != "low" else 0.0
    scores["reliability"] += 0.1 if dataset_profile.data_mode == "time_series" else 0.0
    scores["reliability"] += 0.08 if dataset_profile.completeness_score < 0.97 else 0.0
    scores["reliability"] += _keyword_bonus(
        texts,
        ("reliable", "robust", "calibration", "stable", "uncertainty", "safety", "risk"),
        0.12,
    )

    effort_tier = str(work_preferences.get("preferred_effort_tier", "")).strip().lower()
    execution_profile = str(compute_cfg.get("execution_profile", "")).strip().lower()
    if effort_tier in {"light", "standard"}:
        scores["efficiency"] += 0.08
    if "small_cpu" in execution_profile or "cpu" in execution_profile:
        scores["efficiency"] += 0.08
    scores["efficiency"] += _keyword_bonus(
        texts,
        ("fast", "latency", "realtime", "real-time", "edge", "laptop", "memory", "cheap", "efficient"),
        0.12,
    )

    interpretability_pref = str(constraints_cfg.get("interpretability", "medium")).strip().lower()
    if interpretability_pref in {"high", "medium"}:
        scores["interpretability"] += 0.08
    scores["interpretability"] += _keyword_bonus(
        texts,
        ("interpret", "explain", "audit", "defend", "compliance", "regulated", "transparent", "simple"),
        0.15,
    )

    max_trials = int(compute_cfg.get("max_trials", 200) or 200)
    if max_trials <= 100:
        scores["sustainability"] += 0.06
    scores["sustainability"] += _keyword_bonus(
        texts,
        ("sustain", "energy", "footprint", "carbon", "waste"),
        0.12,
    )

    primary_target = domain_memo.target_candidates[0] if domain_memo.target_candidates else {}
    task_type = str(primary_target.get("task_type", "")).strip()
    minority_fraction = primary_target.get("minority_class_fraction")
    if task_type in {"fraud_detection", "anomaly_detection"}:
        scores["value"] += 0.08
        scores["reliability"] += 0.08
    if minority_fraction is not None and float(minority_fraction) < 0.15:
        scores["value"] += 0.05
        scores["reliability"] += 0.05
    for objective, delta in dict(domain_memo.expert_priors.get("objective_bias", {})).items():
        if objective in scores:
            scores[objective] += float(delta)
    return {key: max(0.05, min(1.0, value)) for key, value in scores.items()}


def _context_corpus(
    *,
    work_preferences: dict[str, Any],
    run_brief: dict[str, Any],
    lab_mandate: dict[str, Any],
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
    domain_memo: DomainMemo,
) -> str:
    parts: list[str] = []
    parts.extend(_string_list(lab_mandate.get("values")))
    parts.extend(_string_list(lab_mandate.get("hard_constraints")))
    parts.extend(_string_list(lab_mandate.get("soft_preferences")))
    parts.extend(_string_list(task_brief.get("success_criteria")))
    parts.extend(_string_list(task_brief.get("failure_costs")))
    parts.extend(_string_list(run_brief.get("success_criteria")))
    parts.extend(_string_list(run_brief.get("binding_constraints")))
    parts.extend(_string_list(domain_brief.get("binding_constraints")))
    for key in ("notes", "objective", "deployment_target", "problem_statement"):
        for source in (work_preferences, run_brief, lab_mandate, task_brief, domain_brief):
            value = str(source.get(key, "")).strip()
            if value:
                parts.append(value)
    parts.append(domain_memo.domain_summary)
    parts.append(domain_memo.domain_archetype)
    parts.append(str(domain_memo.expert_priors.get("summary", "")).strip())
    parts.append(domain_memo.operational_problem_statement)
    return " ".join(parts).lower()


def _keyword_bonus(text: str, keywords: tuple[str, ...], weight: float) -> float:
    matches = sum(1 for keyword in keywords if keyword in text)
    return min(weight, matches * (weight / max(len(keywords) / 2.0, 1.0)))


def _apply_objective_clues(lens_scores: dict[str, float], clues: Any) -> None:
    if not isinstance(clues, list):
        return
    for item in clues:
        if not isinstance(item, dict):
            continue
        objective = str(item.get("objective", "")).strip().lower()
        if objective not in lens_scores:
            continue
        try:
            delta = float(item.get("delta", 0.0))
        except (TypeError, ValueError):
            continue
        bounded = max(-0.08, min(0.08, delta))
        lens_scores[objective] = max(0.05, min(1.0, lens_scores[objective] + bounded))


def _normalize_weights(scores: dict[str, float]) -> dict[str, float]:
    total = sum(max(value, 0.0) for value in scores.values())
    if total <= 0:
        return {"accuracy": 1.0}
    return {key: value / total for key, value in scores.items()}


def _resolved_primary_objective(
    *,
    ranking: list[tuple[str, float]],
    resolution_mode: str,
    focus_llm_advisory: dict[str, Any] | None,
) -> str:
    primary_objective = ranking[0][0]
    if resolution_mode != "multi_objective_blend" or not focus_llm_advisory or len(ranking) < 2:
        return primary_objective
    hint_text = str(focus_llm_advisory.get("resolution_hint", "")).strip().lower()
    for lens, weight in ranking[:3]:
        primary_markers = (
            f"{lens} as primary",
            f"primary {lens}",
            f"center on {lens}",
            f"centered on {lens}",
        )
        if any(marker in hint_text for marker in primary_markers) and abs(weight - ranking[0][1]) <= 0.05:
            return lens
    for lens, weight in ranking[:2]:
        if lens in hint_text and abs(weight - ranking[0][1]) <= 0.05:
            return lens
    return primary_objective


def _mandate_conflicts(
    *,
    primary_objective: str,
    normalized_weights: dict[str, float],
    dataset_profile: DatasetProfile,
    lab_mandate: dict[str, Any],
    run_brief: dict[str, Any],
) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    mandate_text = " ".join(
        _string_list(lab_mandate.get("values"))
        + _string_list(lab_mandate.get("hard_constraints"))
        + _string_list(lab_mandate.get("soft_preferences"))
        + _string_list(run_brief.get("binding_constraints"))
    ).lower()
    if primary_objective == "accuracy" and any(token in mandate_text for token in ("simple", "audit", "explain", "latency", "edge")):
        conflicts.append(
            {
                "severity": "medium",
                "type": "accuracy_vs_constraints",
                "message": "Accuracy pressure is high, but the mandate also asks for simple or constrained deployment behavior.",
            }
        )
    if dataset_profile.leakage_risk_level == "high" and primary_objective != "reliability":
        conflicts.append(
            {
                "severity": "high",
                "type": "problem_vs_focus",
                "message": "Dataset risk is high enough that reliability arguably deserves stronger priority.",
            }
        )
    if primary_objective == "efficiency" and normalized_weights.get("reliability", 0.0) >= 0.24:
        conflicts.append(
            {
                "severity": "medium",
                "type": "efficiency_vs_reliability",
                "message": "Efficiency pressure conflicts with the reliability burden implied by the data.",
            }
        )
    return conflicts


def _resolution_rationale(
    *,
    primary_objective: str,
    secondary_objectives: list[str],
    resolution_mode: str,
    dataset_profile: DatasetProfile,
    domain_memo: DomainMemo,
    focus_llm_advisory: dict[str, Any] | None,
) -> str:
    secondary = f" Secondary: {', '.join(secondary_objectives)}." if secondary_objectives else ""
    advisory = str((focus_llm_advisory or {}).get("resolution_hint", "")).strip()
    base = (
        f"Focus Council resolved a {resolution_mode.replace('_', ' ')} centered on `{primary_objective}` "
        f"because the problem framing and dataset evidence point toward {primary_objective}-sensitive decisions."
    )
    if dataset_profile.leakage_risk_level != "low":
        base += " Leakage risk kept reliability in the debate."
    if domain_memo.unresolved_questions:
        base += " Some ambiguity remains and should constrain planning depth."
    if advisory:
        base += f" Advisory note: {advisory}"
    return base + secondary


def _lens_arguments(
    *,
    lens: str,
    dataset_profile: DatasetProfile,
    domain_memo: DomainMemo,
    run_brief: dict[str, Any],
    lab_mandate: dict[str, Any],
) -> list[str]:
    arguments: list[str] = []
    if lens == "accuracy":
        arguments.append("A strong predictive baseline is still required before later route comparison.")
        if run_brief.get("objective"):
            arguments.append(f"Run objective is `{run_brief.get('objective')}`.")
    elif lens == "value":
        if domain_memo.target_candidates:
            arguments.append(
                "Task framing suggests the model will support operational decisions, not just score reporting."
            )
        if domain_memo.additional_data_hypotheses:
            arguments.append(
                "Additional-data needs imply decision value may depend on asymmetric coverage."
            )
    elif lens == "reliability":
        arguments.append(f"Leakage risk is `{dataset_profile.leakage_risk_level}`.")
        if dataset_profile.quality_warnings:
            arguments.append("Quality warnings suggest robustness and calibration matter.")
    elif lens == "efficiency":
        arguments.append("Relaytic remains local-first by default, which keeps compute efficiency relevant.")
        if dataset_profile.row_count < 10000:
            arguments.append("The current scale does not justify wasteful search.")
    elif lens == "interpretability":
        mandate_values = " ".join(_string_list(lab_mandate.get("values"))).lower()
        if any(token in mandate_values for token in ("audit", "inspect", "evidence")):
            arguments.append("Lab mandate emphasizes inspectable, auditable behavior.")
        arguments.append("Early slices should preserve human-debuggable reasoning.")
    elif lens == "sustainability":
        arguments.append("Local-first experimentation should avoid wasteful search by default.")
    return arguments


def _lens_counterweights(
    *,
    lens: str,
    normalized_weights: dict[str, float],
    mandate_conflicts: list[dict[str, Any]],
) -> list[str]:
    counterweights: list[str] = []
    for other_lens, weight in normalized_weights.items():
        if other_lens == lens or weight < 0.18:
            continue
        counterweights.append(f"`{other_lens}` retains enough weight to limit unilateral optimization.")
    for item in mandate_conflicts:
        message = str(item.get("message", "")).strip()
        if message:
            counterweights.append(message)
    return _dedupe_strings(counterweights)


def _optimization_profile(
    *,
    controls: InvestigationControls,
    focus_trace: SpecialistTrace,
    focus_profile: FocusProfile,
    dataset_profile: DatasetProfile,
    domain_memo: DomainMemo,
) -> OptimizationProfile:
    primary_target = domain_memo.target_candidates[0] if domain_memo.target_candidates else {}
    expert_priors = dict(domain_memo.expert_priors)
    task_type = str(primary_target.get("task_type", "")).strip()
    primary = focus_profile.primary_objective
    classification = is_classification_task(task_type)
    if classification:
        if primary == "value":
            primary_metric = "pr_auc"
        elif primary == "reliability":
            primary_metric = "log_loss"
        elif primary in {"efficiency", "sustainability"}:
            primary_metric = "latency_weighted_f1"
        else:
            primary_metric = "f1"
    else:
        if primary == "reliability":
            primary_metric = "stability_adjusted_mae"
        elif primary in {"efficiency", "sustainability"}:
            primary_metric = "mae_per_latency"
        else:
            primary_metric = "mae"
    expert_primary_metric = str(expert_priors.get("recommended_primary_metric", "")).strip()
    if expert_primary_metric and (
        primary_metric in {"f1", "mae"} or task_type in {"fraud_detection", "anomaly_detection"}
    ):
        primary_metric = expert_primary_metric
    secondary_metrics: list[str] = []
    if "reliability" in focus_profile.active_lenses:
        secondary_metrics.extend(["calibration", "stability"])
    if "efficiency" in focus_profile.active_lenses or "sustainability" in focus_profile.active_lenses:
        secondary_metrics.append("latency")
    if "interpretability" in focus_profile.active_lenses:
        secondary_metrics.append("auditability")
    secondary_metrics = _dedupe_strings(secondary_metrics) or ["stability"]
    if dataset_profile.data_mode == "time_series":
        split_bias = "blocked_time_order_70_15_15"
    elif classification:
        split_bias = "stratified_deterministic_modulo_70_15_15"
    else:
        split_bias = "deterministic_modulo_70_15_15"
    if primary == "interpretability":
        model_family_bias = ["linear_ridge", "logistic", "tree_small"]
    elif primary in {"efficiency", "sustainability"}:
        model_family_bias = ["linear_ridge", "logistic", "tree_small"]
    elif dataset_profile.data_mode == "time_series":
        model_family_bias = ["lagged_linear", "lagged_tree"]
    elif classification:
        model_family_bias = ["logistic", "tree_classifier", "boosted_tree_classifier"]
    else:
        model_family_bias = ["linear_ridge", "tree_ensemble", "boosted_tree"]
    model_family_bias.extend(_string_list(expert_priors.get("model_family_bias")))
    if primary == "accuracy":
        search_budget_posture = "aggressive"
    elif primary in {"efficiency", "sustainability", "interpretability"}:
        search_budget_posture = "conservative"
    else:
        search_budget_posture = "standard"
    threshold_objective = "auto"
    if classification and primary == "value":
        threshold_objective = "favor_recall"
    elif classification and primary == "reliability":
        threshold_objective = "calibrated_threshold"
    expert_threshold_objective = str(expert_priors.get("threshold_policy_hint", "")).strip()
    if classification and expert_threshold_objective:
        threshold_objective = expert_threshold_objective
    notes = [
        f"Primary focus is `{focus_profile.primary_objective}`.",
        f"Resolved split bias is `{split_bias}`.",
        str(expert_priors.get("summary", "")).strip(),
    ]
    return OptimizationProfile(
        schema_version=OPTIMIZATION_PROFILE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        primary_metric=primary_metric,
        secondary_metrics=secondary_metrics,
        threshold_objective=threshold_objective,
        split_strategy_bias=split_bias,
        model_family_bias=_dedupe_strings(model_family_bias),
        search_budget_posture=search_budget_posture,
        calibration_required=classification and "reliability" in focus_profile.active_lenses,
        uncertainty_required="reliability" in focus_profile.active_lenses,
        reproducibility_required=controls.reproducibility_required,
        notes=notes,
        trace=focus_trace,
    )


def _feature_strategy_profile(
    *,
    controls: InvestigationControls,
    focus_trace: SpecialistTrace,
    focus_profile: FocusProfile,
    dataset_profile: DatasetProfile,
    domain_memo: DomainMemo,
    context_bundle: dict[str, Any],
) -> FeatureStrategyProfile:
    domain_brief = _bundle_item(context_bundle, "domain_brief")
    expert_priors = dict(domain_memo.expert_priors)
    prioritize_lag_features = dataset_profile.data_mode == "time_series"
    prioritize_interactions = (
        focus_profile.primary_objective in {"accuracy", "value"}
        and len(dataset_profile.numeric_columns) >= 4
    )
    prioritize_missingness_indicators = any(
        value >= 0.05 for value in dataset_profile.missing_fraction_by_column.values()
    )
    prioritize_stability_features = (
        "reliability" in focus_profile.active_lenses
        or int(dataset_profile.stationarity.get("non_stationary_signals", 0)) > 0
    )
    prioritize_simple_features = focus_profile.primary_objective in {
        "efficiency",
        "interpretability",
        "sustainability",
    }
    preferred_feature_families: list[str] = []
    if prioritize_lag_features:
        preferred_feature_families.extend(["lagged_signals", "rolling_statistics"])
    if prioritize_missingness_indicators:
        preferred_feature_families.append("missingness_indicators")
    if prioritize_interactions:
        preferred_feature_families.append("pairwise_interactions")
    if prioritize_stability_features:
        preferred_feature_families.append("stability_and_drift_features")
    if dataset_profile.entity_key_candidates:
        preferred_feature_families.append("group_history_features")
    if prioritize_simple_features:
        preferred_feature_families.append("raw_auditable_features")
    preferred_feature_families.extend(_string_list(expert_priors.get("feature_priorities")))
    de_emphasized_feature_families = ["high_cardinality_ids", "post_outcome_proxies"]
    if prioritize_simple_features:
        de_emphasized_feature_families.append("deep_feature_search")
    excluded_columns = _dedupe_strings(
        dataset_profile.hidden_key_candidates
        + dataset_profile.suspicious_columns
        + _string_list(domain_brief.get("forbidden_features"))
    )
    guardrails = [
        "exclude hidden keys and suspicious columns from executable feature sets",
        "respect temporal order whenever a timestamped route is active",
        "treat feature ideas as hypotheses until they survive split-safe evaluation",
    ]
    notes = [
        f"Primary focus is `{focus_profile.primary_objective}`.",
        f"Preferred feature families: {', '.join(_dedupe_strings(preferred_feature_families)) or 'raw_auditable_features'}.",
        str(expert_priors.get("summary", "")).strip(),
    ]
    return FeatureStrategyProfile(
        schema_version=FEATURE_STRATEGY_PROFILE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        prioritize_lag_features=prioritize_lag_features,
        prioritize_interactions=prioritize_interactions,
        prioritize_missingness_indicators=prioritize_missingness_indicators,
        prioritize_stability_features=prioritize_stability_features,
        prioritize_simple_features=prioritize_simple_features,
        preferred_feature_families=_dedupe_strings(preferred_feature_families) or ["raw_auditable_features"],
        de_emphasized_feature_families=_dedupe_strings(de_emphasized_feature_families),
        excluded_columns=excluded_columns,
        guardrails=guardrails,
        notes=notes,
        trace=focus_trace,
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items = [str(item).strip() for item in value]
    return [item for item in items if item]


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered

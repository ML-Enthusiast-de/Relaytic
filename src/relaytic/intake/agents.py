"""Slice 04 intake specialists and translation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from pathlib import Path
from typing import Any

from relaytic.analytics import assess_task_profile, normalize_task_type_hint
from relaytic.context import (
    ContextControl,
    DataOrigin,
    DomainBrief,
    TaskBrief,
    build_context_controls_from_policy,
)
from relaytic.integrations import validate_frame_contract
from relaytic.ingestion import load_tabular_data
from relaytic.mandate import (
    LabMandate,
    MandateControl,
    RunBrief,
    WorkPreferences,
    build_mandate_controls_from_policy,
)

from .models import (
    ASSUMPTION_LOG_SCHEMA_VERSION,
    AUTONOMY_MODE_SCHEMA_VERSION,
    CLARIFICATION_QUEUE_SCHEMA_VERSION,
    CONTEXT_CONSTRAINTS_SCHEMA_VERSION,
    CONTEXT_INTERPRETATION_SCHEMA_VERSION,
    INTAKE_RECORD_SCHEMA_VERSION,
    SEMANTIC_MAPPING_SCHEMA_VERSION,
    AssumptionEntry,
    AssumptionLog,
    AutonomyMode,
    ClarificationItem,
    ClarificationQueue,
    ContextConstraints,
    ContextInterpretation,
    IntakeBundle,
    IntakeControls,
    IntakeRecord,
    InterpretationTrace,
    SemanticMapping,
    SemanticMatch,
    build_intake_controls_from_policy,
)
from .semantic import build_local_advisor


TARGET_PATTERNS = (
    re.compile(
        r"\b(?:predict|forecast|estimate|model|classify|detect|identify|explain)\s+"
        r"(?P<target>[a-z0-9_][a-z0-9_ \-/]{1,80})",
        re.IGNORECASE,
    ),
    re.compile(
        r"\btarget(?:\s+column)?\s+is\s+(?P<target>[a-z0-9_][a-z0-9_ \-/]{1,80})",
        re.IGNORECASE,
    ),
)

FORBIDDEN_PATTERNS = (
    re.compile(r"\bdo not use\s+(?P<value>[^.;\n]+)", re.IGNORECASE),
    re.compile(r"\bdon't use\s+(?P<value>[^.;\n]+)", re.IGNORECASE),
    re.compile(r"\bwithout using\s+(?P<value>[^.;\n]+)", re.IGNORECASE),
    re.compile(r"\bexclude\s+(?P<value>[^.;\n]+)", re.IGNORECASE),
    re.compile(r"\bavoid using\s+(?P<value>[^.;\n]+)", re.IGNORECASE),
)

SOURCE_PATTERNS = (
    re.compile(r"\bdata (?:comes )?from\s+(?P<value>[^.;\n]+)", re.IGNORECASE),
    re.compile(r"\bsource(?:\s+name)?\s+is\s+(?P<value>[^.;\n]+)", re.IGNORECASE),
)

SYSTEM_PATTERNS = (
    re.compile(r"\bsystem(?:\s+name)?\s+is\s+(?P<value>[^.;\n]+)", re.IGNORECASE),
    re.compile(r"\bfrom the\s+(?P<value>[a-z0-9_ \-/]{2,80})\s+system\b", re.IGNORECASE),
)

HORIZON_PATTERNS = (
    re.compile(r"\bnext\s+(?P<value>shift|hour|day|week|batch)\b", re.IGNORECASE),
    re.compile(r"\bwithin\s+(?P<value>\d+\s*(?:minutes?|hours?|days?))\b", re.IGNORECASE),
    re.compile(r"\b(?P<value>\d+\s*(?:minutes?|hours?|days?))\s+ahead\b", re.IGNORECASE),
)

ACTOR_TYPES = {"user", "operator", "agent"}

STRUCTURED_TEMPLATE_FIELDS = {
    "target": "task_target_column",
    "target_column": "task_target_column",
    "task_target": "task_target_column",
    "task_target_column": "task_target_column",
    "problem_statement": "problem_statement",
    "task_problem_statement": "problem_statement",
    "prediction_horizon": "prediction_horizon",
    "decision_type": "decision_type",
    "task_type": "task_type_hint",
    "task_type_hint": "task_type_hint",
    "domain_archetype": "domain_archetype_hint",
    "domain_archetype_hint": "domain_archetype_hint",
    "primary_stakeholder": "primary_stakeholder",
    "success_criteria": "task_success_criteria",
    "task_success_criteria": "task_success_criteria",
    "failure_costs": "failure_costs",
    "failure_cost": "failure_costs",
    "task_notes": "task_notes",
    "source": "source_name",
    "source_name": "source_name",
    "source_type": "source_type",
    "acquisition_notes": "acquisition_notes",
    "owner": "owner",
    "contains_pii": "contains_pii",
    "access_constraints": "access_constraints",
    "access_constraint": "access_constraints",
    "refresh_cadence": "refresh_cadence",
    "system": "system_name",
    "system_name": "system_name",
    "domain_summary": "domain_summary",
    "summary": "domain_summary",
    "target_meaning": "target_meaning",
    "known_caveats": "known_caveats",
    "known_caveat": "known_caveats",
    "suspicious_columns": "suspicious_columns",
    "suspicious_column": "suspicious_columns",
    "forbidden_features": "forbidden_features",
    "forbidden_feature": "forbidden_features",
    "domain_binding_constraints": "domain_binding_constraints",
    "domain_binding_constraint": "domain_binding_constraints",
    "domain_assumptions": "domain_assumptions",
    "domain_assumption": "domain_assumptions",
    "lab_values": "lab_values",
    "lab_value": "lab_values",
    "hard_constraints": "hard_constraints",
    "hard_constraint": "hard_constraints",
    "soft_preferences": "soft_preferences",
    "soft_preference": "soft_preferences",
    "prohibited_actions": "prohibited_actions",
    "prohibited_action": "prohibited_actions",
    "objective": "objective",
    "deployment_target": "deployment_target",
    "run_success_criteria": "run_success_criteria",
    "binding_constraints": "binding_constraints",
    "binding_constraint": "binding_constraints",
    "work_execution_mode": "work_execution_mode",
    "execution_mode": "work_execution_mode",
    "work_operation_mode": "work_operation_mode",
    "operation_mode": "work_operation_mode",
    "report_style": "report_style",
    "effort_tier": "effort_tier",
    "work_notes": "work_notes",
}

LIST_VALUE_FIELDS = {
    "task_success_criteria",
    "failure_costs",
    "access_constraints",
    "known_caveats",
    "suspicious_columns",
    "forbidden_features",
    "domain_binding_constraints",
    "domain_assumptions",
    "lab_values",
    "hard_constraints",
    "soft_preferences",
    "prohibited_actions",
    "run_success_criteria",
    "binding_constraints",
}

PLACEHOLDER_PREFIXES = (
    "No domain brief provided.",
    "No data-origin notes provided.",
    "No task brief provided.",
    "Default Relaytic mandate scaffold.",
)

CONSTRAINT_KEYWORDS = {
    "local-first execution": ("local-first", "stay local", "offline", "on-device", "on device"),
    "do not require remote APIs by default": ("no remote api", "no remote apis", "no cloud", "offline only"),
    "do not bypass safety, policy, or budget controls": ("must be auditable", "must be reproducible"),
}

PROHIBITED_ACTION_KEYWORDS = {
    "persist raw secrets into artifacts": ("no secrets", "do not store secrets", "never persist secrets"),
    "silently enable non-local backends": ("no remote backend", "do not upload", "no cloud backend"),
}

OVERRIDABLE_BASELINE_DEFAULTS = {
    ("work_preferences", "preferred_report_style"): {"concise"},
    ("work_preferences", "preferred_effort_tier"): {"standard"},
    ("work_preferences", "execution_mode_preference"): {"guided"},
    ("work_preferences", "operation_mode_preference"): {"session"},
    ("run_brief", "objective"): {"best_robust_pareto_front"},
    ("data_origin", "source_type"): {"snapshot"},
}

AUTONOMY_SIGNAL_PHRASES = (
    "do everything on your own",
    "handle everything on your own",
    "find out",
    "figure it out",
    "you decide",
    "go ahead on your own",
    "work autonomously",
    "handle it autonomously",
    "fully automatic",
    "fully autonomous",
)

AUTONOMY_QUESTION_POLICY = "optional_non_blocking_with_assumptions"


@dataclass(frozen=True)
class IntakeResolution:
    """Resolved Slice 04 outputs plus updated foundation objects."""

    intake_bundle: IntakeBundle
    lab_mandate: LabMandate
    work_preferences: WorkPreferences
    run_brief: RunBrief
    data_origin: DataOrigin
    domain_brief: DomainBrief
    task_brief: TaskBrief


@dataclass(frozen=True)
class _ParsedInput:
    actor_type: str
    actor_name: str | None
    channel: str
    message: str
    source_format: str
    explicit_fields: dict[str, list[str]]
    sentences: list[str]
    normalized_text: str
    schema_columns: list[str]
    dataset_frame: Any | None
    dataset_path: str | None
    selected_sheet: str | None
    header_row: int | None
    data_start_row: int | None


class StewardAgent:
    """Interprets mandate, work-style, and run-level intent from intake."""

    def __init__(self, controls: IntakeControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        parsed: _ParsedInput,
    ) -> dict[str, Any]:
        lab_updates: dict[str, Any] = {}
        work_updates: dict[str, Any] = {}
        run_updates: dict[str, Any] = {}
        field_matches: list[SemanticMatch] = []
        evidence: list[str] = []

        lab_values = _explicit_list(parsed, "lab_values")
        if lab_values:
            lab_updates["values"] = lab_values
            field_matches.extend(
                _build_explicit_matches("lab_mandate.values", lab_values, source="template")
            )

        hard_constraints = _explicit_list(parsed, "hard_constraints")
        hard_constraints.extend(_keyword_constraints(parsed.normalized_text))
        if _contains_any(parsed.normalized_text, ("offline only", "must stay local", "local only")):
            hard_constraints.append("do not require remote APIs by default")
            evidence.append("Detected local-only constraint from intake.")
        if hard_constraints:
            lab_updates["hard_constraints"] = _dedupe_strings(hard_constraints)

        soft_preferences = _explicit_list(parsed, "soft_preferences")
        if _contains_any(parsed.normalized_text, ("interpretable", "explainable", "auditable")):
            soft_preferences.append("prefer inspectable behavior over hidden automation")
            evidence.append("Detected interpretability preference from intake.")
        if soft_preferences:
            lab_updates["soft_preferences"] = _dedupe_strings(soft_preferences)

        prohibited_actions = _explicit_list(parsed, "prohibited_actions")
        prohibited_actions.extend(_keyword_prohibited_actions(parsed.normalized_text))
        if prohibited_actions:
            lab_updates["prohibited_actions"] = _dedupe_strings(prohibited_actions)

        objective = _explicit_scalar(parsed, "objective")
        if objective:
            run_updates["objective"] = objective
            field_matches.append(
                SemanticMatch(
                    field="run_brief.objective",
                    value=objective,
                    confidence=0.99,
                    evidence="Explicit objective template field.",
                    source="template",
                )
            )

        deployment_target = _explicit_scalar(parsed, "deployment_target") or _infer_deployment_target(
            parsed.normalized_text
        )
        if deployment_target:
            run_updates["deployment_target"] = deployment_target
            field_matches.append(
                SemanticMatch(
                    field="run_brief.deployment_target",
                    value=deployment_target,
                    confidence=0.9 if _explicit_scalar(parsed, "deployment_target") else 0.78,
                    evidence="Explicit deployment target."
                    if _explicit_scalar(parsed, "deployment_target")
                    else "Detected deployment keywords in intake.",
                    source="template" if _explicit_scalar(parsed, "deployment_target") else "deterministic",
                )
            )

        binding_constraints = _explicit_list(parsed, "binding_constraints")
        binding_constraints.extend(_binding_constraint_sentences(parsed.sentences))
        if binding_constraints:
            run_updates["binding_constraints"] = _dedupe_strings(binding_constraints)

        run_success = _explicit_list(parsed, "run_success_criteria")
        run_success.extend(_success_criteria_sentences(parsed.sentences))
        if run_success:
            run_updates["success_criteria"] = _dedupe_strings(run_success)

        report_style = _explicit_scalar(parsed, "report_style") or _infer_report_style(parsed.normalized_text)
        if report_style:
            work_updates["preferred_report_style"] = report_style
        effort_tier = _explicit_scalar(parsed, "effort_tier") or _infer_effort_tier(parsed.normalized_text)
        if effort_tier:
            work_updates["preferred_effort_tier"] = effort_tier
        execution_mode = _explicit_scalar(parsed, "work_execution_mode") or _infer_execution_mode(
            parsed.normalized_text
        )
        if execution_mode:
            work_updates["execution_mode_preference"] = execution_mode
        operation_mode = _explicit_scalar(parsed, "work_operation_mode") or _infer_operation_mode(
            parsed.normalized_text
        )
        if operation_mode:
            work_updates["operation_mode_preference"] = operation_mode
        work_notes = _explicit_scalar(parsed, "work_notes")
        if work_notes:
            work_updates["notes"] = work_notes

        return {
            "lab_mandate_updates": lab_updates,
            "work_preference_updates": work_updates,
            "run_brief_updates": run_updates,
            "field_matches": field_matches,
            "clarification_questions": [],
            "conflicts": [],
            "evidence": evidence,
        }


class ContextInterpreterAgent:
    """Interprets data origin, domain framing, and task intent from intake."""

    def __init__(self, controls: IntakeControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        parsed: _ParsedInput,
    ) -> dict[str, Any]:
        data_origin_updates: dict[str, Any] = {}
        domain_brief_updates: dict[str, Any] = {}
        task_brief_updates: dict[str, Any] = {}
        field_matches: list[SemanticMatch] = []
        clarification_questions: list[str] = []
        evidence: list[str] = []
        unmatched_terms: list[str] = []

        source_name = _explicit_scalar(parsed, "source_name") or _first_pattern_value(parsed.message, SOURCE_PATTERNS)
        if source_name:
            source_name = _clean_phrase(source_name)
            data_origin_updates["source_name"] = source_name
            field_matches.append(
                SemanticMatch(
                    field="data_origin.source_name",
                    value=source_name,
                    confidence=0.99 if _explicit_scalar(parsed, "source_name") else 0.72,
                    evidence="Explicit source name."
                    if _explicit_scalar(parsed, "source_name")
                    else "Detected source phrase in intake.",
                    source="template" if _explicit_scalar(parsed, "source_name") else "deterministic",
                )
            )

        source_type = _explicit_scalar(parsed, "source_type") or _infer_source_type(parsed.normalized_text)
        if source_type:
            data_origin_updates["source_type"] = source_type

        acquisition_notes = _explicit_scalar(parsed, "acquisition_notes")
        if acquisition_notes:
            data_origin_updates["acquisition_notes"] = acquisition_notes
        owner = _explicit_scalar(parsed, "owner")
        if owner:
            data_origin_updates["owner"] = owner
        contains_pii = _explicit_bool(parsed, "contains_pii")
        if contains_pii is None and _contains_any(parsed.normalized_text, ("pii", "personal data", "customer names")):
            contains_pii = True
        if contains_pii is not None:
            data_origin_updates["contains_pii"] = contains_pii
        access_constraints = _explicit_list(parsed, "access_constraints")
        if access_constraints:
            data_origin_updates["access_constraints"] = access_constraints
        refresh_cadence = _explicit_scalar(parsed, "refresh_cadence") or _infer_refresh_cadence(
            parsed.normalized_text
        )
        if refresh_cadence:
            data_origin_updates["refresh_cadence"] = refresh_cadence

        system_name = _explicit_scalar(parsed, "system_name") or _first_pattern_value(parsed.message, SYSTEM_PATTERNS)
        if system_name:
            domain_brief_updates["system_name"] = _clean_phrase(system_name)

        domain_summary = _explicit_scalar(parsed, "domain_summary")
        if domain_summary:
            domain_brief_updates["summary"] = domain_summary
        target_meaning = _explicit_scalar(parsed, "target_meaning")
        if target_meaning:
            domain_brief_updates["target_meaning"] = target_meaning
        known_caveats = _explicit_list(parsed, "known_caveats")
        if known_caveats:
            domain_brief_updates["known_caveats"] = known_caveats
        suspicious_columns = _resolve_columns(
            raw_values=_explicit_list(parsed, "suspicious_columns"),
            schema_columns=parsed.schema_columns,
            field="domain_brief.suspicious_columns",
            field_matches=field_matches,
            unmatched_terms=unmatched_terms,
            source="template",
        )
        auto_suspicious = [
            column
            for column in parsed.schema_columns
            if _normalize_text(column).startswith(("future", "post_", "after_"))
        ]
        suspicious_columns = _dedupe_strings(suspicious_columns + auto_suspicious)
        if suspicious_columns:
            domain_brief_updates["suspicious_columns"] = suspicious_columns

        forbidden_features = _resolve_columns(
            raw_values=_explicit_list(parsed, "forbidden_features"),
            schema_columns=parsed.schema_columns,
            field="domain_brief.forbidden_features",
            field_matches=field_matches,
            unmatched_terms=unmatched_terms,
            source="template",
        )
        inferred_forbidden, forbidden_questions = _infer_forbidden_features(parsed)
        forbidden_features = _dedupe_strings(forbidden_features + inferred_forbidden)
        clarification_questions.extend(forbidden_questions)
        if forbidden_features:
            domain_brief_updates["forbidden_features"] = forbidden_features

        domain_binding = _explicit_list(parsed, "domain_binding_constraints")
        if domain_binding:
            domain_brief_updates["binding_constraints"] = domain_binding
        domain_assumptions = _explicit_list(parsed, "domain_assumptions")
        if domain_assumptions:
            domain_brief_updates["assumptions"] = domain_assumptions

        problem_statement = _explicit_scalar(parsed, "problem_statement") or _infer_problem_statement(
            parsed.sentences
        )
        if problem_statement:
            task_brief_updates["problem_statement"] = problem_statement

        target_result = _infer_target_column(parsed)
        if target_result is not None:
            target_value = str(target_result["value"])
            task_brief_updates["target_column"] = target_value
            field_matches.append(
                SemanticMatch(
                    field="task_brief.target_column",
                    value=target_value,
                    confidence=float(target_result["confidence"]),
                    evidence=str(target_result["evidence"]),
                    source=str(target_result.get("source", "deterministic")),
                    matched_column=target_result.get("matched_column"),
                )
            )
            if target_result.get("matched_column") is None and parsed.schema_columns:
                unmatched_terms.append(target_value)
        else:
            clarification_questions.append(
                "Which dataset column should be treated as the primary outcome or target?"
            )

        prediction_horizon = _explicit_scalar(parsed, "prediction_horizon") or _infer_prediction_horizon(
            parsed.message
        )
        if prediction_horizon:
            task_brief_updates["prediction_horizon"] = prediction_horizon
        decision_type = _explicit_scalar(parsed, "decision_type") or _infer_decision_type(parsed.normalized_text)
        if decision_type:
            task_brief_updates["decision_type"] = decision_type
        explicit_task_type_hint = normalize_task_type_hint(_explicit_scalar(parsed, "task_type_hint"))
        target_column = str(task_brief_updates.get("target_column") or "")
        dataset_task_type_hint = None
        if explicit_task_type_hint in {None, "auto"}:
            dataset_task_type_hint = _infer_task_type_hint_from_data(
                parsed=parsed,
                target_column=target_column,
            )
        task_type_hint = (
            explicit_task_type_hint
            or dataset_task_type_hint
            or _infer_task_type_hint(
                normalized_text=parsed.normalized_text,
                target_column=target_column,
            )
        )
        if task_type_hint and task_type_hint != "auto":
            task_brief_updates["task_type_hint"] = task_type_hint
            if dataset_task_type_hint:
                evidence.append(
                    f"Resolved task type from dataset evidence for target `{target_column}` as `{task_type_hint}`."
                )
        domain_archetype_hint = _explicit_scalar(parsed, "domain_archetype_hint") or _infer_domain_archetype_hint(
            normalized_text=parsed.normalized_text,
            target_column=str(task_brief_updates.get("target_column") or ""),
        )
        if domain_archetype_hint:
            task_brief_updates["domain_archetype_hint"] = domain_archetype_hint
        primary_stakeholder = _explicit_scalar(parsed, "primary_stakeholder") or _infer_primary_stakeholder(
            parsed.message
        )
        if primary_stakeholder:
            task_brief_updates["primary_stakeholder"] = primary_stakeholder

        task_success = _explicit_list(parsed, "task_success_criteria")
        task_success.extend(_success_criteria_sentences(parsed.sentences))
        if task_success:
            task_brief_updates["success_criteria"] = _dedupe_strings(task_success)

        failure_costs = _explicit_list(parsed, "failure_costs")
        failure_costs.extend(_failure_cost_sentences(parsed.sentences))
        if failure_costs:
            task_brief_updates["failure_costs"] = _dedupe_strings(failure_costs)

        task_notes = _explicit_scalar(parsed, "task_notes")
        if task_notes:
            task_brief_updates["notes"] = task_notes

        if not task_brief_updates.get("target_column") and parsed.schema_columns:
            candidate_columns = _candidate_target_columns(parsed.schema_columns)
            if len(candidate_columns) > 1:
                clarification_questions.append(
                    f"Several plausible target columns were found: {', '.join(candidate_columns[:3])}. Which one is primary?"
                )
        if forbidden_questions:
            evidence.append("Detected generic forbidden-feature language that needs column-level clarification.")

        return {
            "data_origin_updates": data_origin_updates,
            "domain_brief_updates": domain_brief_updates,
            "task_brief_updates": task_brief_updates,
            "field_matches": field_matches,
            "clarification_questions": _dedupe_strings(clarification_questions),
            "conflicts": [],
            "evidence": evidence,
            "unmatched_terms": _dedupe_strings(unmatched_terms),
        }


def run_intake_interpretation(
    *,
    message: str,
    actor_type: str,
    actor_name: str | None,
    channel: str,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    config_path: str | None = None,
    data_path: str | None = None,
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
) -> IntakeResolution:
    """Interpret free-form intake into Slice 04 artifacts and updated foundation objects."""
    if actor_type not in ACTOR_TYPES:
        raise ValueError(f"Unsupported actor type '{actor_type}'. Use one of {sorted(ACTOR_TYPES)}.")
    normalized_message = message.strip()
    if not normalized_message:
        raise ValueError("Intake message must not be empty.")

    controls = build_intake_controls_from_policy(policy)
    schema_info = _load_schema_info(
        data_path=data_path,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
    )
    explicit_fields = _parse_template_fields(normalized_message)
    parsed = _ParsedInput(
        actor_type=actor_type,
        actor_name=actor_name,
        channel=channel,
        message=normalized_message,
        source_format=_resolve_source_format(explicit_fields=explicit_fields, raw_text=normalized_message),
        explicit_fields=explicit_fields,
        sentences=_split_sentences(normalized_message),
        normalized_text=_normalize_text(normalized_message),
        schema_columns=schema_info["schema_columns"],
        dataset_frame=schema_info["dataset_frame"],
        dataset_path=schema_info["dataset_path"],
        selected_sheet=schema_info["selected_sheet"],
        header_row=schema_info["header_row"],
        data_start_row=schema_info["data_start_row"],
    )

    steward = StewardAgent(controls)
    context_interpreter = ContextInterpreterAgent(controls)
    steward_result = steward.run(parsed=parsed)
    context_result = context_interpreter.run(parsed=parsed)
    autonomy_signal = _find_operator_autonomy_signal(parsed.normalized_text)
    if autonomy_signal and "execution_mode_preference" not in steward_result["work_preference_updates"]:
        steward_result["work_preference_updates"]["execution_mode_preference"] = "autonomous"
        steward_result["evidence"].append(
            f"Detected operator autonomy signal `{autonomy_signal}` and enabled autonomous execution preference."
        )

    llm_advisory: dict[str, Any] | None = None
    llm_status = "not_requested"
    advisory_notes: list[str] = []
    local_advisor = build_local_advisor(controls=controls, config_path=config_path)
    if local_advisor is not None:
        advisory = local_advisor.complete_json(
            task_name="intake",
            system_prompt=(
                "You are Relaytic's intake translation advisory module. "
                "Read the free-form input, the dataset schema, and the deterministic interpretation. "
                "Return JSON with keys lab_mandate_updates, work_preference_updates, run_brief_updates, "
                "data_origin_updates, domain_brief_updates, task_brief_updates, clarification_questions, "
                "conflicts, and context_constraints. context_constraints may contain binding_constraints, "
                "forbidden_features, hard_constraints, soft_preferences, prohibited_actions, success_criteria, "
                "and failure_costs. Prefer filling blanks and clarifying ambiguity over guessing."
            ),
            payload={
                "message": parsed.message,
                "actor_type": parsed.actor_type,
                "actor_name": parsed.actor_name,
                "channel": parsed.channel,
                "source_format": parsed.source_format,
                "schema_columns": parsed.schema_columns,
                "deterministic": {
                    "steward": {
                        "lab_mandate_updates": steward_result["lab_mandate_updates"],
                        "work_preference_updates": steward_result["work_preference_updates"],
                        "run_brief_updates": steward_result["run_brief_updates"],
                    },
                    "context": {
                        "data_origin_updates": context_result["data_origin_updates"],
                        "domain_brief_updates": context_result["domain_brief_updates"],
                        "task_brief_updates": context_result["task_brief_updates"],
                    },
                },
            },
        )
        llm_status = "advisory_used" if advisory.status == "ok" and advisory.payload else advisory.status
        advisory_notes.extend(advisory.notes)
        if advisory.payload:
            llm_advisory = advisory.payload
            _merge_advisory(steward_result, context_result, advisory.payload, parsed.schema_columns)

    resolved = _resolve_updates_against_existing(
        steward_result=steward_result,
        context_result=context_result,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    )

    generated_at = datetime.now(timezone.utc).isoformat()
    combined_questions = _dedupe_strings(
        resolved["clarification_questions"]
        + _string_list((llm_advisory or {}).get("clarification_questions"))
    )
    combined_conflicts = _dedupe_strings(
        resolved["conflicts"] + _string_list((llm_advisory or {}).get("conflicts"))
    )
    trace = InterpretationTrace(
        agent="intake_translator",
        operating_mode="deterministic_plus_local_llm" if llm_advisory else "deterministic",
        llm_used=llm_advisory is not None,
        llm_status=llm_status,
        deterministic_evidence=list(steward_result["evidence"]) + list(context_result["evidence"]),
        advisory_notes=advisory_notes,
    )

    intake_record = IntakeRecord(
        schema_version=INTAKE_RECORD_SCHEMA_VERSION,
        captured_at=generated_at,
        controls=controls,
        actor_type=parsed.actor_type,
        actor_name=parsed.actor_name,
        channel=parsed.channel,
        source_format=parsed.source_format,
        message=parsed.message,
        dataset_path=parsed.dataset_path,
        selected_sheet=parsed.selected_sheet,
        header_row=parsed.header_row,
        data_start_row=parsed.data_start_row,
        schema_validation=[],
    )

    if parsed.dataset_frame is not None:
        schema_validation = validate_frame_contract(
            frame=parsed.dataset_frame,
            required_columns=parsed.schema_columns,
            target_column=str(resolved["task_brief_updates"].get("target_column", "")).strip() or None,
            surface="intake",
        )
        intake_record = IntakeRecord(
            schema_version=intake_record.schema_version,
            captured_at=intake_record.captured_at,
            controls=intake_record.controls,
            actor_type=intake_record.actor_type,
            actor_name=intake_record.actor_name,
            channel=intake_record.channel,
            source_format=intake_record.source_format,
            message=intake_record.message,
            dataset_path=intake_record.dataset_path,
            selected_sheet=intake_record.selected_sheet,
            header_row=intake_record.header_row,
            data_start_row=intake_record.data_start_row,
            schema_validation=[schema_validation],
        )
        if schema_validation.get("status") == "validation_failed":
            combined_conflicts.append(
                "Pandera validation flagged the current dataset contract; review intake target and schema assumptions."
            )
        if schema_validation.get("status") in {"ok", "validation_failed"}:
            trace.deterministic_evidence.append(
                f"Pandera schema validation returned `{schema_validation.get('status')}` for the current intake frame."
            )

    field_matches = _dedupe_matches(
        list(steward_result["field_matches"]) + list(context_result["field_matches"])
    )
    semantic_mapping = SemanticMapping(
        schema_version=SEMANTIC_MAPPING_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        schema_columns=parsed.schema_columns,
        field_matches=field_matches,
        unmatched_terms=_dedupe_strings(context_result["unmatched_terms"]),
        summary=_build_semantic_mapping_summary(field_matches, parsed.schema_columns),
        trace=trace,
    )
    autonomy_mode = _build_autonomy_mode(
        parsed=parsed,
        controls=controls,
        generated_at=generated_at,
        trace=trace,
        resolved=resolved,
        mandate_bundle=mandate_bundle,
        operator_signal=autonomy_signal,
    )
    clarification_queue = _build_clarification_queue(
        controls=controls,
        generated_at=generated_at,
        trace=trace,
        questions=combined_questions,
        resolved=resolved,
        schema_columns=parsed.schema_columns,
        autonomy_mode=autonomy_mode,
    )
    assumption_log = _build_assumption_log(
        controls=controls,
        generated_at=generated_at,
        trace=trace,
        autonomy_mode=autonomy_mode,
        clarification_queue=clarification_queue,
        resolved=resolved,
        field_matches=field_matches,
        parsed=parsed,
        context_bundle=context_bundle,
        mandate_bundle=mandate_bundle,
    )
    assumptions = [entry.assumption for entry in assumption_log.entries]

    context_constraints = ContextConstraints(
        schema_version=CONTEXT_CONSTRAINTS_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        binding_constraints=_dedupe_strings(_string_list(resolved["run_brief_updates"].get("binding_constraints"))),
        forbidden_features=_dedupe_strings(_string_list(resolved["domain_brief_updates"].get("forbidden_features"))),
        suspicious_columns=_dedupe_strings(_string_list(resolved["domain_brief_updates"].get("suspicious_columns"))),
        hard_constraints=_dedupe_strings(_string_list(resolved["lab_mandate_updates"].get("hard_constraints"))),
        soft_preferences=_dedupe_strings(_string_list(resolved["lab_mandate_updates"].get("soft_preferences"))),
        prohibited_actions=_dedupe_strings(_string_list(resolved["lab_mandate_updates"].get("prohibited_actions"))),
        success_criteria=_dedupe_strings(
            _string_list(resolved["run_brief_updates"].get("success_criteria"))
            + _string_list(resolved["task_brief_updates"].get("success_criteria"))
        ),
        failure_costs=_dedupe_strings(_string_list(resolved["task_brief_updates"].get("failure_costs"))),
        clarification_questions=combined_questions,
        assumptions=assumptions,
        trace=trace,
    )

    context_interpretation = ContextInterpretation(
        schema_version=CONTEXT_INTERPRETATION_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        lab_mandate_updates=resolved["lab_mandate_updates"],
        work_preference_updates=resolved["work_preference_updates"],
        run_brief_updates=resolved["run_brief_updates"],
        data_origin_updates=resolved["data_origin_updates"],
        domain_brief_updates=resolved["domain_brief_updates"],
        task_brief_updates=resolved["task_brief_updates"],
        clarification_questions=combined_questions,
        assumptions=assumptions,
        conflicts=combined_conflicts,
        llm_advisory=llm_advisory,
        summary=_build_interpretation_summary(
            resolved=resolved,
            clarification_questions=combined_questions,
            conflicts=combined_conflicts,
            assumption_count=len(assumptions),
            suppressed_questions=clarification_queue.suppressed_count,
        ),
        trace=trace,
    )

    mandate_controls = _resolve_mandate_controls(mandate_bundle, policy)
    context_controls = _resolve_context_controls(context_bundle, policy)
    lab_mandate = _apply_lab_mandate_updates(
        controls=mandate_controls,
        existing=mandate_bundle.get("lab_mandate", {}),
        updates=resolved["lab_mandate_updates"],
    )
    work_preferences = _apply_work_preference_updates(
        controls=mandate_controls,
        existing=mandate_bundle.get("work_preferences", {}),
        updates=resolved["work_preference_updates"],
    )
    run_brief = _apply_run_brief_updates(
        controls=mandate_controls,
        existing=mandate_bundle.get("run_brief", {}),
        updates=resolved["run_brief_updates"],
        task_updates=resolved["task_brief_updates"],
    )
    data_origin = _apply_data_origin_updates(
        controls=context_controls,
        existing=context_bundle.get("data_origin", {}),
        updates=resolved["data_origin_updates"],
    )
    domain_brief = _apply_domain_brief_updates(
        controls=context_controls,
        existing=context_bundle.get("domain_brief", {}),
        updates=resolved["domain_brief_updates"],
    )
    task_brief = _apply_task_brief_updates(
        controls=context_controls,
        existing=context_bundle.get("task_brief", {}),
        updates=resolved["task_brief_updates"],
    )
    return IntakeResolution(
        intake_bundle=IntakeBundle(
            intake_record=intake_record,
            autonomy_mode=autonomy_mode,
            clarification_queue=clarification_queue,
            assumption_log=assumption_log,
            context_interpretation=context_interpretation,
            context_constraints=context_constraints,
            semantic_mapping=semantic_mapping,
        ),
        lab_mandate=lab_mandate,
        work_preferences=work_preferences,
        run_brief=run_brief,
        data_origin=data_origin,
        domain_brief=domain_brief,
        task_brief=task_brief,
    )


def _load_schema_info(
    *,
    data_path: str | None,
    sheet_name: str | None,
    header_row: int | None,
    data_start_row: int | None,
) -> dict[str, Any]:
    if not data_path:
        return {
            "schema_columns": [],
            "dataset_frame": None,
            "dataset_path": None,
            "selected_sheet": None,
            "header_row": header_row,
            "data_start_row": data_start_row,
        }
    ingestion = load_tabular_data(
        data_path,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
    )
    return {
        "schema_columns": [str(column) for column in ingestion.frame.columns],
        "dataset_frame": ingestion.frame.copy(),
        "dataset_path": str(Path(data_path)),
        "selected_sheet": ingestion.selected_sheet,
        "header_row": int(ingestion.inferred_header.header_row),
        "data_start_row": int(ingestion.inferred_header.data_start_row),
    }


def _parse_template_fields(raw_text: str) -> dict[str, list[str]]:
    parsed: dict[str, list[str]] = {}
    for line in raw_text.splitlines():
        stripped = line.strip().lstrip("-*").strip()
        if not stripped:
            continue
        separator = ":" if ":" in stripped else "=" if "=" in stripped else None
        if separator is None:
            continue
        key, value = stripped.split(separator, 1)
        normalized_key = _normalize_text(key).replace(" ", "_")
        canonical_key = STRUCTURED_TEMPLATE_FIELDS.get(normalized_key)
        if not canonical_key:
            continue
        values = _split_list_value(value) if canonical_key in LIST_VALUE_FIELDS else [value.strip()]
        if not values:
            continue
        parsed.setdefault(canonical_key, []).extend(values)
    return {key: _dedupe_strings(value) for key, value in parsed.items()}


def _resolve_source_format(*, explicit_fields: dict[str, list[str]], raw_text: str) -> str:
    if explicit_fields and len(raw_text.splitlines()) > len(explicit_fields):
        return "mixed"
    if explicit_fields:
        return "field_templates"
    return "free_text"


def _split_sentences(raw_text: str) -> list[str]:
    collapsed = raw_text.replace("\r", "\n")
    pieces = re.split(r"[.;\n]+", collapsed)
    return [piece.strip() for piece in pieces if piece and piece.strip()]


def _explicit_list(parsed: _ParsedInput, key: str) -> list[str]:
    return list(parsed.explicit_fields.get(key, []))


def _explicit_scalar(parsed: _ParsedInput, key: str) -> str | None:
    values = parsed.explicit_fields.get(key) or []
    return str(values[0]).strip() if values else None


def _explicit_bool(parsed: _ParsedInput, key: str) -> bool | None:
    value = _explicit_scalar(parsed, key)
    if value is None:
        return None
    normalized = _normalize_text(value)
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    return None


def _first_pattern_value(text: str, patterns: tuple[re.Pattern[str], ...]) -> str | None:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return str(match.group("value")).strip()
    return None


def _infer_target_column(parsed: _ParsedInput) -> dict[str, Any] | None:
    explicit_target = _explicit_scalar(parsed, "task_target_column")
    if explicit_target:
        matched_column, confidence = _match_column(explicit_target, parsed.schema_columns)
        return {
            "value": matched_column or explicit_target,
            "matched_column": matched_column,
            "confidence": 0.99 if matched_column or not parsed.schema_columns else max(0.9, confidence),
            "evidence": "Explicit target template field.",
            "source": "template",
        }
    for sentence in parsed.sentences:
        for pattern in TARGET_PATTERNS:
            match = pattern.search(sentence)
            if not match:
                continue
            phrase = _clean_phrase(match.group("target"))
            if not phrase:
                continue
            matched_column, confidence = _match_column(phrase, parsed.schema_columns)
            if matched_column:
                return {
                    "value": matched_column,
                    "matched_column": matched_column,
                    "confidence": max(0.75, confidence),
                    "evidence": f"Matched target phrase `{phrase}` to dataset schema.",
                    "source": "deterministic",
                }
            return {
                "value": phrase,
                "matched_column": None,
                "confidence": 0.66,
                "evidence": f"Detected target phrase `{phrase}` in intake.",
                "source": "deterministic",
            }
    return None


def _infer_forbidden_features(parsed: _ParsedInput) -> tuple[list[str], list[str]]:
    resolved: list[str] = []
    questions: list[str] = []
    for sentence in parsed.sentences:
        for pattern in FORBIDDEN_PATTERNS:
            match = pattern.search(sentence)
            if not match:
                continue
            raw_value = _clean_phrase(match.group("value"))
            if not raw_value:
                continue
            local_field_matches: list[SemanticMatch] = []
            local_unmatched: list[str] = []
            columns = _resolve_columns(
                raw_values=_split_list_value(raw_value),
                schema_columns=parsed.schema_columns,
                field="domain_brief.forbidden_features",
                field_matches=local_field_matches,
                unmatched_terms=local_unmatched,
                source="deterministic",
            )
            if columns:
                resolved.extend(columns)
            else:
                questions.append(
                    f"Which concrete dataset columns correspond to the constraint '{raw_value.rstrip('.')}'?"
                )
    return _dedupe_strings(resolved), _dedupe_strings(questions)


def _infer_problem_statement(sentences: list[str]) -> str | None:
    for sentence in sentences:
        normalized = _normalize_text(sentence)
        if any(
            verb in normalized
            for verb in ("predict", "forecast", "estimate", "classify", "detect", "identify")
        ):
            return sentence.strip()
    return None


def _infer_prediction_horizon(message: str) -> str | None:
    for pattern in HORIZON_PATTERNS:
        match = pattern.search(message)
        if match:
            return _clean_phrase(match.group("value"))
    return None


def _infer_decision_type(normalized_text: str) -> str | None:
    if "classify" in normalized_text or "binary" in normalized_text:
        return "classification"
    if "forecast" in normalized_text or "time series" in normalized_text:
        return "forecasting"
    if "detect" in normalized_text or "anomaly" in normalized_text:
        return "detection"
    if "estimate" in normalized_text or "regression" in normalized_text:
        return "regression"
    return None


def _infer_task_type_hint(*, normalized_text: str, target_column: str) -> str | None:
    combined = f"{normalized_text} {str(target_column).strip().lower()}".strip()
    if any(token in combined for token in ("fraud", "chargeback", "scam", "abuse")):
        return "fraud_detection"
    if any(token in combined for token in ("anomaly", "outlier", "fault", "alert", "attack")):
        return "anomaly_detection"
    if any(token in combined for token in ("multiclass", "multi class", "multi-class")):
        return "multiclass_classification"
    if any(token in combined for token in ("classify", "classification", "binary", "label", "status", "flag")):
        return "binary_classification"
    if any(token in combined for token in ("forecast", "estimate", "regression", "amount", "score", "price", "revenue")):
        return "regression"
    return None


def _infer_task_type_hint_from_data(*, parsed: _ParsedInput, target_column: str) -> str | None:
    if not target_column or parsed.dataset_frame is None or target_column not in parsed.dataset_frame.columns:
        return None
    try:
        profile = assess_task_profile(
            frame=parsed.dataset_frame,
            target_column=target_column,
            data_mode="steady_state",
        )
    except Exception:
        return None
    return str(profile.task_type).strip() or None


def _infer_domain_archetype_hint(*, normalized_text: str, target_column: str) -> str | None:
    combined = f"{normalized_text} {str(target_column).strip().lower()}".strip()
    if any(token in combined for token in ("fraud", "chargeback", "abuse", "scam", "transaction")):
        return "fraud_risk"
    if any(token in combined for token in ("anomaly", "outlier", "fault", "alert", "attack")):
        return "anomaly_monitoring"
    if any(token in combined for token in ("quality", "yield", "scrap", "defect", "off-spec", "batch", "lot", "sensor", "line")):
        return "manufacturing_quality"
    if any(token in combined for token in ("churn", "attrition", "retention", "cancel", "unsubscribe")):
        return "churn_retention"
    if any(token in combined for token in ("forecast", "demand", "inventory", "sales", "orders", "volume")):
        return "demand_forecasting"
    if any(token in combined for token in ("price", "pricing", "quote", "revenue", "margin", "cost")):
        return "pricing_estimation"
    return None


def _infer_primary_stakeholder(message: str) -> str | None:
    match = re.search(r"\bfor\s+([a-z0-9][a-z0-9 \-/]{2,60})", message, flags=re.IGNORECASE)
    return _clean_phrase(match.group(1)) if match else None


def _infer_source_type(normalized_text: str) -> str | None:
    if "stream" in normalized_text or "real-time" in normalized_text or "realtime" in normalized_text:
        return "stream"
    if "table" in normalized_text:
        return "table"
    if "snapshot" in normalized_text or "historical" in normalized_text:
        return "snapshot"
    return None


def _infer_refresh_cadence(normalized_text: str) -> str | None:
    if "hourly" in normalized_text:
        return "hourly"
    if "daily" in normalized_text:
        return "daily"
    if "weekly" in normalized_text:
        return "weekly"
    if "real-time" in normalized_text or "realtime" in normalized_text:
        return "real-time"
    return None


def _infer_deployment_target(normalized_text: str) -> str | None:
    parts: list[str] = []
    if "laptop" in normalized_text:
        parts.append("laptop")
    if "cpu" in normalized_text:
        parts.append("cpu")
    if "edge" in normalized_text:
        parts.append("edge")
    if "low latency" in normalized_text or "realtime" in normalized_text or "real-time" in normalized_text:
        parts.append("low_latency")
    if "batch" in normalized_text:
        parts.append("batch")
    return " ".join(_dedupe_strings(parts)) if parts else None


def _infer_report_style(normalized_text: str) -> str | None:
    if "detailed report" in normalized_text or "detailed summary" in normalized_text:
        return "detailed"
    if "concise" in normalized_text or "brief report" in normalized_text:
        return "concise"
    return None


def _infer_effort_tier(normalized_text: str) -> str | None:
    if "quick" in normalized_text or "lightweight" in normalized_text or "fast pass" in normalized_text:
        return "light"
    if "deep" in normalized_text or "thorough" in normalized_text or "high effort" in normalized_text:
        return "deep"
    return None


def _infer_execution_mode(normalized_text: str) -> str | None:
    if "guided" in normalized_text:
        return "guided"
    if "autonomous" in normalized_text or "fully automatic" in normalized_text:
        return "autonomous"
    return None


def _infer_operation_mode(normalized_text: str) -> str | None:
    if "daemon" in normalized_text:
        return "daemon"
    if "session" in normalized_text:
        return "session"
    return None


def _success_criteria_sentences(sentences: list[str]) -> list[str]:
    matches: list[str] = []
    for sentence in sentences:
        normalized = _normalize_text(sentence)
        if any(token in normalized for token in ("success means", "optimize", "maximize", "minimize", "must")):
            matches.append(sentence.strip())
    return _dedupe_strings(matches)


def _failure_cost_sentences(sentences: list[str]) -> list[str]:
    matches: list[str] = []
    for sentence in sentences:
        normalized = _normalize_text(sentence)
        if any(token in normalized for token in ("failure means", "if we miss", "cost", "can't afford", "cannot afford")):
            matches.append(sentence.strip())
    return _dedupe_strings(matches)


def _binding_constraint_sentences(sentences: list[str]) -> list[str]:
    matches: list[str] = []
    for sentence in sentences:
        normalized = _normalize_text(sentence)
        if any(token in normalized for token in ("do not", "don't", "must stay", "without using", "offline only")):
            matches.append(sentence.strip())
    return _dedupe_strings(matches)


def _candidate_target_columns(schema_columns: list[str]) -> list[str]:
    keywords = ("target", "label", "outcome", "yield", "quality", "failure", "score")
    return [column for column in schema_columns if any(keyword in _normalize_text(column) for keyword in keywords)]


def _keyword_constraints(normalized_text: str) -> list[str]:
    resolved: list[str] = []
    for constraint, phrases in CONSTRAINT_KEYWORDS.items():
        if _contains_any(normalized_text, phrases):
            resolved.append(constraint)
    return resolved


def _keyword_prohibited_actions(normalized_text: str) -> list[str]:
    resolved: list[str] = []
    for action, phrases in PROHIBITED_ACTION_KEYWORDS.items():
        if _contains_any(normalized_text, phrases):
            resolved.append(action)
    return resolved


def _resolve_columns(
    *,
    raw_values: list[str],
    schema_columns: list[str],
    field: str,
    field_matches: list[SemanticMatch],
    unmatched_terms: list[str],
    source: str,
) -> list[str]:
    resolved: list[str] = []
    for raw in raw_values:
        if not raw:
            continue
        matched_column, confidence = _match_column(raw, schema_columns)
        if matched_column:
            resolved.append(matched_column)
            field_matches.append(
                SemanticMatch(
                    field=field,
                    value=matched_column,
                    confidence=max(0.72, confidence),
                    evidence=f"Matched `{raw}` against dataset schema.",
                    source=source,
                    matched_column=matched_column,
                )
            )
        elif schema_columns:
            unmatched_terms.append(raw)
        else:
            resolved.append(raw)
            field_matches.append(
                SemanticMatch(
                    field=field,
                    value=raw,
                    confidence=0.7,
                    evidence="Accepted raw value without schema alignment.",
                    source=source,
                )
            )
    return _dedupe_strings(resolved)


def _build_explicit_matches(field: str, values: list[str], *, source: str) -> list[SemanticMatch]:
    return [
        SemanticMatch(
            field=field,
            value=str(value),
            confidence=0.99,
            evidence="Explicit template field.",
            source=source,
        )
        for value in values
        if str(value).strip()
    ]


def _match_column(raw_value: str, schema_columns: list[str]) -> tuple[str | None, float]:
    if not schema_columns:
        return None, 0.0
    normalized_value = _normalize_text(raw_value)
    value_tokens = set(normalized_value.split())
    best_column: str | None = None
    best_score = 0.0
    for column in schema_columns:
        normalized_column = _normalize_text(column)
        if normalized_column == normalized_value:
            return column, 1.0
        if normalized_value and normalized_value in normalized_column:
            score = 0.92
        else:
            column_tokens = set(normalized_column.split())
            if not value_tokens or not column_tokens:
                score = 0.0
            else:
                overlap = len(value_tokens & column_tokens)
                score = overlap / max(len(value_tokens), len(column_tokens))
                if value_tokens <= column_tokens or column_tokens <= value_tokens:
                    score = max(score, 0.84)
        if score > best_score:
            best_score = score
            best_column = column
    return (best_column, best_score) if best_score >= 0.55 else (None, 0.0)


def _merge_advisory(
    steward_result: dict[str, Any],
    context_result: dict[str, Any],
    advisory_payload: dict[str, Any],
    schema_columns: list[str],
) -> None:
    _merge_section_dict(steward_result["lab_mandate_updates"], dict(advisory_payload.get("lab_mandate_updates", {})))
    _merge_section_dict(
        steward_result["work_preference_updates"],
        dict(advisory_payload.get("work_preference_updates", {})),
    )
    _merge_section_dict(steward_result["run_brief_updates"], dict(advisory_payload.get("run_brief_updates", {})))
    _merge_section_dict(context_result["data_origin_updates"], dict(advisory_payload.get("data_origin_updates", {})))
    _merge_section_dict(
        context_result["domain_brief_updates"],
        dict(advisory_payload.get("domain_brief_updates", {})),
    )
    _merge_section_dict(context_result["task_brief_updates"], dict(advisory_payload.get("task_brief_updates", {})))
    context_result["clarification_questions"] = _dedupe_strings(
        list(context_result["clarification_questions"])
        + _string_list(advisory_payload.get("clarification_questions"))
    )
    context_result["conflicts"] = _dedupe_strings(
        list(context_result["conflicts"]) + _string_list(advisory_payload.get("conflicts"))
    )
    constraints = dict(advisory_payload.get("context_constraints", {}))
    for key, target in (
        ("binding_constraints", steward_result["run_brief_updates"]),
        ("success_criteria", steward_result["run_brief_updates"]),
        ("failure_costs", context_result["task_brief_updates"]),
        ("forbidden_features", context_result["domain_brief_updates"]),
        ("hard_constraints", steward_result["lab_mandate_updates"]),
        ("soft_preferences", steward_result["lab_mandate_updates"]),
        ("prohibited_actions", steward_result["lab_mandate_updates"]),
    ):
        if key in constraints:
            target[key] = _dedupe_strings(_string_list(target.get(key)) + _string_list(constraints.get(key)))
    llm_target = str(dict(advisory_payload.get("task_brief_updates", {})).get("target_column", "")).strip()
    if llm_target and "target_column" not in context_result["task_brief_updates"]:
        matched_column, confidence = _match_column(llm_target, schema_columns)
        context_result["task_brief_updates"]["target_column"] = matched_column or llm_target
        context_result["field_matches"].append(
            SemanticMatch(
                field="task_brief.target_column",
                value=matched_column or llm_target,
                confidence=max(0.62, confidence),
                evidence="Optional local-LLM advisory target suggestion.",
                source="local_llm",
                matched_column=matched_column,
            )
        )


def _merge_section_dict(target: dict[str, Any], incoming: dict[str, Any]) -> None:
    for key, value in incoming.items():
        if value in (None, "", []):
            continue
        if isinstance(value, list):
            target[key] = _dedupe_strings(_string_list(target.get(key)) + _string_list(value))
        elif key not in target or _is_blankish(target.get(key)):
            target[key] = value


def _resolve_updates_against_existing(
    *,
    steward_result: dict[str, Any],
    context_result: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
) -> dict[str, Any]:
    conflicts: list[str] = []
    lab_updates = _resolve_section_updates(
        existing=mandate_bundle.get("lab_mandate", {}),
        updates=dict(steward_result["lab_mandate_updates"]),
        conflicts=conflicts,
        section_name="lab_mandate",
    )
    work_updates = _resolve_section_updates(
        existing=mandate_bundle.get("work_preferences", {}),
        updates=dict(steward_result["work_preference_updates"]),
        conflicts=conflicts,
        section_name="work_preferences",
    )
    run_updates = _resolve_section_updates(
        existing=mandate_bundle.get("run_brief", {}),
        updates=dict(steward_result["run_brief_updates"]),
        conflicts=conflicts,
        section_name="run_brief",
    )
    data_origin_updates = _resolve_section_updates(
        existing=context_bundle.get("data_origin", {}),
        updates=dict(context_result["data_origin_updates"]),
        conflicts=conflicts,
        section_name="data_origin",
    )
    domain_updates = _resolve_section_updates(
        existing=context_bundle.get("domain_brief", {}),
        updates=dict(context_result["domain_brief_updates"]),
        conflicts=conflicts,
        section_name="domain_brief",
    )
    task_updates = _resolve_section_updates(
        existing=context_bundle.get("task_brief", {}),
        updates=dict(context_result["task_brief_updates"]),
        conflicts=conflicts,
        section_name="task_brief",
    )
    if task_updates.get("target_column") and "target_column" not in run_updates:
        run_updates["target_column"] = task_updates["target_column"]
    return {
        "lab_mandate_updates": lab_updates,
        "work_preference_updates": work_updates,
        "run_brief_updates": run_updates,
        "data_origin_updates": data_origin_updates,
        "domain_brief_updates": domain_updates,
        "task_brief_updates": task_updates,
        "clarification_questions": _dedupe_strings(
            list(steward_result["clarification_questions"]) + list(context_result["clarification_questions"])
        ),
        "conflicts": _dedupe_strings(conflicts),
    }


def _resolve_section_updates(
    *,
    existing: dict[str, Any],
    updates: dict[str, Any],
    conflicts: list[str],
    section_name: str,
) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, candidate in updates.items():
        if candidate in (None, "", []):
            continue
        existing_value = existing.get(key)
        if isinstance(candidate, list):
            merged = _dedupe_strings(_string_list(existing_value) + _string_list(candidate))
            if merged:
                resolved[key] = merged
            continue
        if _is_blankish(existing_value) or _is_overridable_default(
            section_name=section_name,
            key=key,
            existing_value=existing_value,
        ):
            resolved[key] = candidate
        elif str(existing_value).strip() == str(candidate).strip():
            resolved[key] = existing_value
        else:
            conflicts.append(
                f"{section_name}.{key} already had value `{existing_value}`; intake suggestion `{candidate}` was not auto-applied."
            )
    return resolved


def _resolve_mandate_controls(mandate_bundle: dict[str, Any], policy: dict[str, Any]) -> MandateControl:
    payload = dict(mandate_bundle.get("lab_mandate", {})).get("controls")
    if isinstance(payload, dict) and payload:
        return MandateControl(
            enabled=bool(payload.get("enabled", True)),
            influence_mode=str(payload.get("influence_mode", "weighted")),
            allow_agent_challenges=bool(payload.get("allow_agent_challenges", True)),
            require_disagreement_logging=bool(payload.get("require_disagreement_logging", True)),
            allow_soft_preference_override_with_evidence=bool(
                payload.get("allow_soft_preference_override_with_evidence", True)
            ),
        )
    return build_mandate_controls_from_policy(policy)


def _resolve_context_controls(context_bundle: dict[str, Any], policy: dict[str, Any]) -> ContextControl:
    payload = dict(context_bundle.get("data_origin", {})).get("controls")
    if isinstance(payload, dict) and payload:
        return ContextControl(
            enabled=bool(payload.get("enabled", True)),
            external_retrieval_allowed=bool(payload.get("external_retrieval_allowed", False)),
            allow_uploaded_docs=bool(payload.get("allow_uploaded_docs", True)),
            require_provenance=bool(payload.get("require_provenance", True)),
            semantic_task_enabled=bool(payload.get("semantic_task_enabled", True)),
        )
    return build_context_controls_from_policy(policy)


def _apply_lab_mandate_updates(
    *,
    controls: MandateControl,
    existing: dict[str, Any],
    updates: dict[str, Any],
) -> LabMandate:
    return LabMandate(
        controls=controls,
        values=_merge_list(existing.get("values"), updates.get("values")),
        hard_constraints=_merge_list(existing.get("hard_constraints"), updates.get("hard_constraints")),
        soft_preferences=_merge_list(existing.get("soft_preferences"), updates.get("soft_preferences")),
        prohibited_actions=_merge_list(existing.get("prohibited_actions"), updates.get("prohibited_actions")),
        notes=_merge_scalar(existing.get("notes"), updates.get("notes"), default=""),
    )


def _apply_work_preference_updates(
    *,
    controls: MandateControl,
    existing: dict[str, Any],
    updates: dict[str, Any],
) -> WorkPreferences:
    return WorkPreferences(
        controls=controls,
        execution_mode_preference=_merge_scalar(
            existing.get("execution_mode_preference"), updates.get("execution_mode_preference")
        ),
        operation_mode_preference=_merge_scalar(
            existing.get("operation_mode_preference"), updates.get("operation_mode_preference")
        ),
        preferred_report_style=_merge_scalar(
            existing.get("preferred_report_style"), updates.get("preferred_report_style"), default="concise"
        )
        or "concise",
        preferred_effort_tier=_merge_scalar(
            existing.get("preferred_effort_tier"), updates.get("preferred_effort_tier"), default="standard"
        )
        or "standard",
        notes=_merge_scalar(existing.get("notes"), updates.get("notes"), default=""),
    )


def _apply_run_brief_updates(
    *,
    controls: MandateControl,
    existing: dict[str, Any],
    updates: dict[str, Any],
    task_updates: dict[str, Any],
) -> RunBrief:
    target_column = _merge_scalar(existing.get("target_column"), updates.get("target_column"))
    if not target_column:
        target_column = str(task_updates.get("target_column") or "").strip() or None
    return RunBrief(
        controls=controls,
        objective=_merge_scalar(
            existing.get("objective"), updates.get("objective"), default="best_robust_pareto_front"
        )
        or "best_robust_pareto_front",
        target_column=target_column,
        deployment_target=_merge_scalar(existing.get("deployment_target"), updates.get("deployment_target")),
        success_criteria=_merge_list(existing.get("success_criteria"), updates.get("success_criteria")),
        binding_constraints=_merge_list(existing.get("binding_constraints"), updates.get("binding_constraints")),
        notes=_merge_scalar(existing.get("notes"), updates.get("notes"), default=""),
    )


def _apply_data_origin_updates(
    *,
    controls: ContextControl,
    existing: dict[str, Any],
    updates: dict[str, Any],
) -> DataOrigin:
    return DataOrigin(
        controls=controls,
        source_name=_merge_scalar(existing.get("source_name"), updates.get("source_name"), default="unspecified")
        or "unspecified",
        source_type=_merge_scalar(existing.get("source_type"), updates.get("source_type"), default="snapshot")
        or "snapshot",
        acquisition_notes=_merge_scalar(
            existing.get("acquisition_notes"),
            updates.get("acquisition_notes"),
            default="No data-origin notes provided.",
        )
        or "No data-origin notes provided.",
        owner=_merge_scalar(existing.get("owner"), updates.get("owner")),
        contains_pii=_merge_bool(existing.get("contains_pii"), updates.get("contains_pii")),
        access_constraints=_merge_list(existing.get("access_constraints"), updates.get("access_constraints")),
        refresh_cadence=_merge_scalar(existing.get("refresh_cadence"), updates.get("refresh_cadence")),
    )


def _apply_domain_brief_updates(
    *,
    controls: ContextControl,
    existing: dict[str, Any],
    updates: dict[str, Any],
) -> DomainBrief:
    return DomainBrief(
        controls=controls,
        system_name=_merge_scalar(existing.get("system_name"), updates.get("system_name"), default="unspecified")
        or "unspecified",
        summary=_merge_scalar(
            existing.get("summary"),
            updates.get("summary"),
            default="No domain brief provided. Relaytic should proceed in ungrounded mode until more context is available.",
        )
        or "No domain brief provided. Relaytic should proceed in ungrounded mode until more context is available.",
        target_meaning=_merge_scalar(existing.get("target_meaning"), updates.get("target_meaning")),
        known_caveats=_merge_list(existing.get("known_caveats"), updates.get("known_caveats")),
        suspicious_columns=_merge_list(existing.get("suspicious_columns"), updates.get("suspicious_columns")),
        forbidden_features=_merge_list(existing.get("forbidden_features"), updates.get("forbidden_features")),
        binding_constraints=_merge_list(existing.get("binding_constraints"), updates.get("binding_constraints")),
        assumptions=_merge_list(existing.get("assumptions"), updates.get("assumptions")),
    )


def _apply_task_brief_updates(
    *,
    controls: ContextControl,
    existing: dict[str, Any],
    updates: dict[str, Any],
) -> TaskBrief:
    return TaskBrief(
        controls=controls,
        problem_statement=_merge_scalar(
            existing.get("problem_statement"),
            updates.get("problem_statement"),
            default="No task brief provided. Relaytic should infer a working task from dataset evidence and explicit operator instructions.",
        )
        or "No task brief provided. Relaytic should infer a working task from dataset evidence and explicit operator instructions.",
        target_column=_merge_scalar(existing.get("target_column"), updates.get("target_column")),
        prediction_horizon=_merge_scalar(existing.get("prediction_horizon"), updates.get("prediction_horizon")),
        decision_type=_merge_scalar(existing.get("decision_type"), updates.get("decision_type")),
        task_type_hint=_merge_scalar(existing.get("task_type_hint"), updates.get("task_type_hint")),
        domain_archetype_hint=_merge_scalar(
            existing.get("domain_archetype_hint"),
            updates.get("domain_archetype_hint"),
        ),
        primary_stakeholder=_merge_scalar(
            existing.get("primary_stakeholder"), updates.get("primary_stakeholder")
        ),
        success_criteria=_merge_list(existing.get("success_criteria"), updates.get("success_criteria")),
        failure_costs=_merge_list(existing.get("failure_costs"), updates.get("failure_costs")),
        notes=_merge_scalar(existing.get("notes"), updates.get("notes"), default="") or "",
    )


def _merge_scalar(existing: Any, update: Any, *, default: str | None = None) -> str | None:
    if not _is_blankish(update):
        return str(update).strip()
    if not _is_blankish(existing):
        return str(existing).strip() or default
    return default


def _merge_bool(existing: Any, update: Any) -> bool | None:
    if update is not None:
        return bool(update)
    if existing is not None:
        return bool(existing)
    return None


def _merge_list(existing: Any, update: Any) -> list[str]:
    return _dedupe_strings(_string_list(existing) + _string_list(update))


def _build_semantic_mapping_summary(field_matches: list[SemanticMatch], schema_columns: list[str]) -> str:
    if not field_matches:
        return "No field-level mappings were extracted from the intake."
    mapped_fields = sorted({item.field for item in field_matches})
    schema_note = f" against {len(schema_columns)} schema columns" if schema_columns else ""
    return (
        f"Resolved {len(field_matches)} field mappings{schema_note} across "
        f"{len(mapped_fields)} normalized Relaytic fields."
    )


def _build_interpretation_summary(
    *,
    resolved: dict[str, Any],
    clarification_questions: list[str],
    conflicts: list[str],
    assumption_count: int,
    suppressed_questions: int,
) -> str:
    update_sections = sum(
        1
        for key in (
            "lab_mandate_updates",
            "work_preference_updates",
            "run_brief_updates",
            "data_origin_updates",
            "domain_brief_updates",
            "task_brief_updates",
        )
        if resolved.get(key)
    )
    return (
        f"Translated intake into {update_sections} foundation sections with "
        f"{len(clarification_questions)} optional clarification question(s), "
        f"{assumption_count} logged assumption(s), {suppressed_questions} suppressed question(s), "
        f"and {len(conflicts)} conflict(s)."
    )


def _contains_any(text: str, phrases: tuple[str, ...] | list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _find_operator_autonomy_signal(normalized_text: str) -> str | None:
    for phrase in AUTONOMY_SIGNAL_PHRASES:
        normalized_phrase = _normalize_text(phrase)
        if normalized_phrase and normalized_phrase in normalized_text:
            return phrase
    return None


def _build_autonomy_mode(
    *,
    parsed: _ParsedInput,
    controls: IntakeControls,
    generated_at: str,
    trace: InterpretationTrace,
    resolved: dict[str, Any],
    mandate_bundle: dict[str, Any],
    operator_signal: str | None,
) -> AutonomyMode:
    existing_work = dict(mandate_bundle.get("work_preferences", {}))
    resolved_mode = str(resolved["work_preference_updates"].get("execution_mode_preference") or "").strip().lower()
    existing_mode = str(existing_work.get("execution_mode_preference") or "").strip().lower()
    requested_mode = resolved_mode or existing_mode or "guided"
    if operator_signal and requested_mode not in {"guided", "autonomous"}:
        requested_mode = "autonomous"
    suppress_noncritical_questions = bool(operator_signal) or requested_mode == "autonomous"
    proceed_without_answers = True
    hard_stop_reasons: list[str] = []
    summary = (
        "Operator requested autonomous progress; Relaytic will continue without waiting for non-critical answers."
        if operator_signal
        else "Relaytic will continue with evidence-backed assumptions when optional clarification is unanswered."
    )
    return AutonomyMode(
        schema_version=AUTONOMY_MODE_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        requested_mode=requested_mode,
        proceed_without_answers=proceed_without_answers,
        suppress_noncritical_questions=suppress_noncritical_questions,
        question_policy=AUTONOMY_QUESTION_POLICY,
        operator_signal=operator_signal,
        hard_stop_required=bool(hard_stop_reasons),
        hard_stop_reasons=hard_stop_reasons,
        summary=summary,
        trace=trace,
    )


def _build_clarification_queue(
    *,
    controls: IntakeControls,
    generated_at: str,
    trace: InterpretationTrace,
    questions: list[str],
    resolved: dict[str, Any],
    schema_columns: list[str],
    autonomy_mode: AutonomyMode,
) -> ClarificationQueue:
    items: list[ClarificationItem] = []
    for index, question in enumerate(_dedupe_strings(questions), start=1):
        items.append(
            ClarificationItem(
                id=f"clarification_{index:03d}",
                question=question,
                optional=True,
                blocking_class="never",
                default_resolution=_default_resolution_for_question(
                    question=question,
                    resolved=resolved,
                    schema_columns=schema_columns,
                ),
                confidence_impact=_confidence_impact_for_question(question),
                affected_artifacts=_affected_artifacts_for_question(question),
                status="suppressed_by_autonomy" if autonomy_mode.suppress_noncritical_questions else "active_optional",
            )
        )
    active_count = sum(1 for item in items if item.status == "active_optional")
    suppressed_count = sum(1 for item in items if item.status == "suppressed_by_autonomy")
    if not items:
        summary = "No clarification items were needed; intake produced enough evidence to continue autonomously."
    else:
        summary = (
            f"Generated {len(items)} optional clarification item(s); "
            f"{suppressed_count} are suppressed by autonomous mode and {active_count} remain visible for refinement."
        )
    return ClarificationQueue(
        schema_version=CLARIFICATION_QUEUE_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        items=items,
        active_count=active_count,
        suppressed_count=suppressed_count,
        summary=summary,
        trace=trace,
    )


def _build_assumption_log(
    *,
    controls: IntakeControls,
    generated_at: str,
    trace: InterpretationTrace,
    autonomy_mode: AutonomyMode,
    clarification_queue: ClarificationQueue,
    resolved: dict[str, Any],
    field_matches: list[SemanticMatch],
    parsed: _ParsedInput,
    context_bundle: dict[str, Any],
    mandate_bundle: dict[str, Any],
) -> AssumptionLog:
    entries: list[AssumptionEntry] = []
    if autonomy_mode.operator_signal:
        entries.append(
            AssumptionEntry(
                id="assumption_autonomous_progress",
                category="operating_mode",
                assumption="Continue autonomously and do not wait for non-critical clarification answers.",
                rationale=f"Detected operator autonomy signal `{autonomy_mode.operator_signal}` in the intake.",
                confidence=0.99,
                source="operator_signal",
                affected_artifacts=["autonomy_mode.json", "clarification_queue.json"],
            )
        )

    if autonomy_mode.proceed_without_answers:
        for item in clarification_queue.items:
            entries.append(
                AssumptionEntry(
                    id=f"assumption_{item.id}",
                    category=_assumption_category_for_question(item.question),
                    assumption=item.default_resolution,
                    rationale=(
                        "Clarification is optional in Relaytic's intake contract, so the run proceeds with the "
                        "highest-confidence deterministic fallback."
                    ),
                    confidence=_assumption_confidence_for_question(item.question, resolved, field_matches),
                    source="deterministic_fallback",
                    affected_artifacts=item.affected_artifacts,
                    derived_from_question_id=item.id,
                )
            )

    inferred_target = str(resolved["task_brief_updates"].get("target_column") or "").strip()
    explicit_target = _explicit_scalar(parsed, "task_target_column")
    if inferred_target and not explicit_target and not any(entry.category == "target_selection" for entry in entries):
        target_match = _best_match_for_field(field_matches, "task_brief.target_column")
        entries.append(
            AssumptionEntry(
                id="assumption_inferred_target",
                category="target_selection",
                assumption=f"Treat `{inferred_target}` as the provisional primary target until stronger evidence appears.",
                rationale=target_match.evidence if target_match is not None else "Target-like language and schema evidence aligned.",
                confidence=round(float(target_match.confidence), 2) if target_match is not None else 0.7,
                source=target_match.source if target_match is not None else "deterministic",
                affected_artifacts=["task_brief.json", "run_brief.json", "context_interpretation.json"],
            )
        )

    existing_source = str(dict(context_bundle.get("data_origin", {})).get("source_name") or "").strip()
    inferred_source = str(resolved["data_origin_updates"].get("source_name") or "").strip()
    if not inferred_source and existing_source.lower() in {"", "unspecified"}:
        entries.append(
            AssumptionEntry(
                id="assumption_unspecified_source",
                category="data_origin",
                assumption="Proceed without a named data source and rely on dataset-grounded evidence until source metadata is provided.",
                rationale="Neither the intake nor the existing foundation bundle specified a source name.",
                confidence=0.61,
                source="deterministic_fallback",
                affected_artifacts=["data_origin.json", "context_interpretation.json"],
            )
        )

    existing_summary = str(dict(context_bundle.get("domain_brief", {})).get("summary") or "").strip()
    if not str(resolved["domain_brief_updates"].get("summary") or "").strip() and any(
        existing_summary.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES
    ):
        entries.append(
            AssumptionEntry(
                id="assumption_ungrounded_domain_mode",
                category="domain_context",
                assumption="Proceed in ungrounded mode until richer domain context is available.",
                rationale="The run still relies on the default placeholder domain summary.",
                confidence=0.58,
                source="deterministic_fallback",
                affected_artifacts=["domain_brief.json", "context_interpretation.json"],
            )
        )

    entries = _dedupe_assumption_entries(entries)
    summary = (
        "No additional assumptions were needed."
        if not entries
        else f"Logged {len(entries)} explicit assumption(s) so Relaytic can continue without waiting for answers."
    )
    return AssumptionLog(
        schema_version=ASSUMPTION_LOG_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        entries=entries,
        summary=summary,
        trace=trace,
    )


def _default_resolution_for_question(
    *,
    question: str,
    resolved: dict[str, Any],
    schema_columns: list[str],
) -> str:
    normalized = _normalize_text(question)
    target_column = str(resolved["task_brief_updates"].get("target_column") or "").strip()
    forbidden_features = _dedupe_strings(
        _string_list(resolved["domain_brief_updates"].get("forbidden_features"))
        + _string_list(resolved["domain_brief_updates"].get("suspicious_columns"))
    )
    candidate_targets = _candidate_target_columns(schema_columns)
    if "target" in normalized or "outcome" in normalized or "primary" in normalized:
        if target_column:
            return f"Use `{target_column}` as the provisional primary target and continue."
        if candidate_targets:
            return f"Use `{candidate_targets[0]}` as the provisional primary target and continue."
        return "Infer the working target from the strongest target-like schema column during planning."
    if "constraint" in normalized or "forbidden" in normalized or "column" in normalized:
        if forbidden_features:
            joined = ", ".join(f"`{item}`" for item in forbidden_features[:3])
            return f"Treat {joined} as provisional forbidden features and continue."
        return "Treat future-looking and post-outcome columns as provisional forbidden features and continue."
    if "intervention" in normalized:
        return "Proceed with an early-warning framing and keep intervention details unspecified."
    if "stakeholder" in normalized:
        return "Assume operations is the primary stakeholder until stronger evidence appears."
    return "Proceed with the highest-confidence interpretation from the intake and dataset evidence."


def _confidence_impact_for_question(question: str) -> str:
    normalized = _normalize_text(question)
    if "target" in normalized or "outcome" in normalized:
        return "high"
    if "constraint" in normalized or "forbidden" in normalized or "intervention" in normalized:
        return "medium"
    return "low"


def _affected_artifacts_for_question(question: str) -> list[str]:
    normalized = _normalize_text(question)
    if "target" in normalized or "outcome" in normalized:
        return ["task_brief.json", "run_brief.json", "context_interpretation.json"]
    if "constraint" in normalized or "forbidden" in normalized or "column" in normalized:
        return ["domain_brief.json", "context_constraints.json", "context_interpretation.json"]
    if "deployment" in normalized or "cpu" in normalized or "laptop" in normalized:
        return ["run_brief.json", "work_preferences.json", "context_constraints.json"]
    return ["context_interpretation.json", "context_constraints.json"]


def _assumption_category_for_question(question: str) -> str:
    normalized = _normalize_text(question)
    if "target" in normalized or "outcome" in normalized:
        return "target_selection"
    if "constraint" in normalized or "forbidden" in normalized or "column" in normalized:
        return "feature_constraints"
    if "deployment" in normalized or "cpu" in normalized or "laptop" in normalized:
        return "execution_constraints"
    return "clarification_fallback"


def _assumption_confidence_for_question(
    question: str,
    resolved: dict[str, Any],
    field_matches: list[SemanticMatch],
) -> float:
    normalized = _normalize_text(question)
    if "target" in normalized or "outcome" in normalized:
        match = _best_match_for_field(field_matches, "task_brief.target_column")
        if match is not None:
            return round(float(match.confidence), 2)
        return 0.66
    if "constraint" in normalized or "forbidden" in normalized or "column" in normalized:
        confidences = [
            float(item.confidence)
            for item in field_matches
            if item.field == "domain_brief.forbidden_features"
        ]
        if confidences:
            return round(max(confidences), 2)
        if _string_list(resolved["domain_brief_updates"].get("suspicious_columns")):
            return 0.7
        return 0.62
    if "intervention" in normalized:
        return 0.55
    return 0.68


def _best_match_for_field(field_matches: list[SemanticMatch], field: str) -> SemanticMatch | None:
    candidates = [item for item in field_matches if item.field == field]
    if not candidates:
        return None
    return max(candidates, key=lambda item: float(item.confidence))


def _dedupe_assumption_entries(entries: list[AssumptionEntry]) -> list[AssumptionEntry]:
    seen: set[tuple[str, str]] = set()
    result: list[AssumptionEntry] = []
    for entry in entries:
        key = (entry.category.casefold(), entry.assumption.casefold())
        if key in seen:
            continue
        seen.add(key)
        result.append(entry)
    return result


def _split_list_value(raw_value: str) -> list[str]:
    normalized = re.sub(r"\s+\b(?:or|and)\b\s+", ",", raw_value, flags=re.IGNORECASE)
    items = re.split(r"[,\n;|]+", normalized)
    return [item.strip().strip("\"'") for item in items if item and item.strip()]


def _clean_phrase(value: str) -> str:
    cleaned = re.split(r"\b(?:from|using|with|for|before|after|while)\b", value, maxsplit=1)[0]
    return cleaned.strip().strip("\"'").rstrip(".")


def _normalize_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


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


def _dedupe_matches(matches: list[SemanticMatch]) -> list[SemanticMatch]:
    seen: set[tuple[str, str, str | None, str]] = set()
    result: list[SemanticMatch] = []
    for match in matches:
        key = (match.field, match.value, match.matched_column, match.source)
        if key in seen:
            continue
        seen.add(key)
        result.append(match)
    return result


def _is_blankish(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return True
        if stripped.lower() == "unspecified":
            return True
        return any(stripped.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES)
    if isinstance(value, list):
        return len(_string_list(value)) == 0
    return False


def _is_overridable_default(*, section_name: str, key: str, existing_value: Any) -> bool:
    allowed = OVERRIDABLE_BASELINE_DEFAULTS.get((section_name, key))
    if not allowed:
        return False
    return str(existing_value).strip().casefold() in {item.casefold() for item in allowed}

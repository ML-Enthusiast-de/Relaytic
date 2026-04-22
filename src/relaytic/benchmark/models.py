"""Typed artifact models for Slice 11 benchmark parity work."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


BENCHMARK_CONTROLS_SCHEMA_VERSION = "relaytic.benchmark_controls.v1"
REFERENCE_APPROACH_MATRIX_SCHEMA_VERSION = "relaytic.reference_approach_matrix.v1"
BENCHMARK_GAP_REPORT_SCHEMA_VERSION = "relaytic.benchmark_gap_report.v1"
BENCHMARK_PARITY_REPORT_SCHEMA_VERSION = "relaytic.benchmark_parity_report.v1"
EXTERNAL_CHALLENGER_MANIFEST_SCHEMA_VERSION = "relaytic.external_challenger_manifest.v1"
EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION = "relaytic.external_challenger_evaluation.v1"
INCUMBENT_PARITY_REPORT_SCHEMA_VERSION = "relaytic.incumbent_parity_report.v1"
BEAT_TARGET_CONTRACT_SCHEMA_VERSION = "relaytic.beat_target_contract.v1"
PAPER_BENCHMARK_MANIFEST_SCHEMA_VERSION = "relaytic.paper_benchmark_manifest.v1"
PAPER_BENCHMARK_TABLE_SCHEMA_VERSION = "relaytic.paper_benchmark_table.v1"
BENCHMARK_ABLATION_MATRIX_SCHEMA_VERSION = "relaytic.benchmark_ablation_matrix.v1"
RERUN_VARIANCE_REPORT_SCHEMA_VERSION = "relaytic.rerun_variance_report.v1"
BENCHMARK_CLAIMS_REPORT_SCHEMA_VERSION = "relaytic.benchmark_claims_report.v1"
SHADOW_TRIAL_MANIFEST_SCHEMA_VERSION = "relaytic.shadow_trial_manifest.v1"
SHADOW_TRIAL_SCORECARD_SCHEMA_VERSION = "relaytic.shadow_trial_scorecard.v1"
CANDIDATE_QUARANTINE_SCHEMA_VERSION = "relaytic.candidate_quarantine.v1"
PROMOTION_READINESS_REPORT_SCHEMA_VERSION = "relaytic.promotion_readiness_report.v1"
BENCHMARK_TRUTH_AUDIT_SCHEMA_VERSION = "relaytic.benchmark_truth_audit.v1"
PAPER_CLAIM_GUARD_REPORT_SCHEMA_VERSION = "relaytic.paper_claim_guard_report.v1"
BENCHMARK_RELEASE_GATE_SCHEMA_VERSION = "relaytic.benchmark_release_gate.v1"
DATASET_LEAKAGE_AUDIT_SCHEMA_VERSION = "relaytic.dataset_leakage_audit.v1"
TEMPORAL_BENCHMARK_RECOVERY_REPORT_SCHEMA_VERSION = "relaytic.temporal_benchmark_recovery_report.v1"
BENCHMARK_PACK_PARTITION_SCHEMA_VERSION = "relaytic.benchmark_pack_partition.v1"
HOLDOUT_CLAIM_POLICY_SCHEMA_VERSION = "relaytic.holdout_claim_policy.v1"
BENCHMARK_GENERALIZATION_AUDIT_SCHEMA_VERSION = "relaytic.benchmark_generalization_audit.v1"
AML_BENCHMARK_MANIFEST_SCHEMA_VERSION = "relaytic.aml_benchmark_manifest.v1"
AML_HOLDOUT_CLAIM_REPORT_SCHEMA_VERSION = "relaytic.aml_holdout_claim_report.v1"
AML_DEMO_SCORECARD_SCHEMA_VERSION = "relaytic.aml_demo_scorecard.v1"
AML_PUBLIC_CLAIM_GUARD_SCHEMA_VERSION = "relaytic.aml_public_claim_guard.v1"
AML_FAILURE_REPORT_SCHEMA_VERSION = "relaytic.aml_failure_report.v1"


@dataclass(frozen=True)
class BenchmarkControls:
    schema_version: str = BENCHMARK_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    require_same_split_contract: bool = True
    require_same_metric_contract: bool = True
    use_optional_flaml_reference: bool = False
    allow_time_series_references: bool = True
    max_reference_models: int = 3
    near_parity_absolute_delta: float = 0.03
    near_parity_relative_delta: float = 0.08

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReferenceApproachMatrix:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    task_type: str
    data_mode: str
    primary_metric: str
    comparison_metric: str
    metric_direction: str
    relaytic_reference: dict[str, Any]
    references: list[dict[str, Any]]
    winning_reference_family: str | None
    same_contract_guarantees: list[str]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkGapReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    comparison_metric: str
    metric_direction: str
    relaytic_family: str | None
    best_reference_family: str | None
    relaytic_rank: int | None
    total_compared_routes: int
    validation_gap: float | None
    test_gap: float | None
    validation_relative_gap: float | None
    test_relative_gap: float | None
    relaytic_beats_best_reference: bool
    near_parity: bool
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkParityReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    benchmark_expected: bool
    parity_status: str
    comparison_metric: str
    recommended_action: str
    winning_family: str | None
    relaytic_family: str | None
    reference_count: int
    strong_reference_available: bool
    incumbent_present: bool
    incumbent_name: str | None
    beat_target_state: str | None
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ExternalChallengerManifest:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    incumbent_name: str | None
    incumbent_kind: str | None
    adapter_family: str | None
    source_path: str | None
    executable_locally: bool
    reduced_claim: bool
    same_contract_possible: bool
    evaluation_scope: str
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ExternalChallengerEvaluation:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    incumbent_name: str | None
    incumbent_kind: str | None
    evaluation_mode: str
    comparison_metric: str | None
    metric_direction: str | None
    reevaluated_locally: bool
    reduced_claim: bool
    evaluation_scope: str
    train_metric: dict[str, Any]
    validation_metric: dict[str, Any]
    test_metric: dict[str, Any]
    decision_threshold: float | None
    reason_codes: list[str]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class IncumbentParityReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    incumbent_present: bool
    incumbent_name: str | None
    incumbent_kind: str | None
    parity_status: str
    comparison_metric: str | None
    recommended_action: str
    relaytic_beats_incumbent: bool
    incumbent_stronger: bool
    reduced_claim: bool
    test_gap: float | None
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BeatTargetContract:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    target_name: str | None
    target_kind: str
    comparison_metric: str | None
    metric_direction: str | None
    target_metric_value: float | None
    relaytic_metric_value: float | None
    contract_state: str
    recommended_action: str
    reduced_claim: bool
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PaperBenchmarkManifest:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    dataset_label: str
    dataset_source_name: str | None
    dataset_source_type: str | None
    source_url: str | None
    data_path: str
    task_type: str
    data_mode: str
    target_column: str
    row_count: int
    column_count: int
    comparison_metric: str
    metric_direction: str
    selected_model_family: str | None
    selected_hyperparameters: dict[str, Any]
    benchmark_expected: bool
    horizon_type: str | None
    timestamp_cadence_quality: str | None
    lagged_baseline_family: str | None
    lagged_baseline_metric: float | None
    sequence_candidate_status: str | None
    sequence_candidate_reason: str | None
    summary: str
    trace: BenchmarkTrace
    claim_gate_status: str | None = None
    safe_to_cite_publicly: bool | None = None
    claim_gate_reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PaperBenchmarkTable:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    comparison_metric: str
    metric_direction: str
    relaytic_rank: int | None
    reference_count: int
    rows: list[dict[str, Any]]
    summary: str
    trace: BenchmarkTrace
    claim_gate_status: str | None = None
    safe_to_cite_publicly: bool | None = None
    claim_gate_reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkAblationMatrix:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    comparison_metric: str
    metric_direction: str
    rows: list[dict[str, Any]]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RerunVarianceReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    comparison_metric: str
    metric_direction: str
    matching_run_count: int
    run_ids: list[str]
    metric_values: list[float]
    mean_metric_value: float | None
    min_metric_value: float | None
    max_metric_value: float | None
    stddev_metric_value: float | None
    coefficient_of_variation: float | None
    stability_band: str
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkClaimsReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    competitiveness_claim: str
    deployment_claim: str
    below_reference: bool
    benchmark_vs_deploy_split: bool
    claim_boundaries: list[str]
    weak_spots: list[str]
    not_claiming: list[str]
    why_below_reference: str | None
    temporal_posture: dict[str, Any]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ShadowTrialManifest:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    candidate_count: int
    runnable_candidate_count: int
    replay_only_count: int
    temporal_candidate_count: int
    comparison_metric: str | None
    baseline_family: str | None
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ShadowTrialScorecard:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    comparison_metric: str | None
    metric_direction: str | None
    rows: list[dict[str, Any]]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class CandidateQuarantine:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    quarantined_count: int
    quarantined_candidates: list[dict[str, Any]]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PromotionReadinessReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    promotion_ready_count: int
    candidate_available_count: int
    quarantined_count: int
    rows: list[dict[str, Any]]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DatasetLeakageAudit:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    leakage_risk_level: str
    blocked_finding_count: int
    warning_finding_count: int
    blocked_reason_codes: list[str]
    findings: list[dict[str, Any]]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkTruthAudit:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    safe_to_cite_publicly: bool
    truth_precheck_status: str | None
    protocol_status: str | None
    security_status: str | None
    trace_identity_status: str | None
    eval_surface_parity_status: str | None
    leakage_status: str | None
    blocked_reason_codes: list[str]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PaperClaimGuardReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    safe_to_cite_publicly: bool
    blocked_reason_codes: list[str]
    claim_boundaries: list[str]
    required_fixes: list[str]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkReleaseGate:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    safe_to_cite_publicly: bool
    demo_safe: bool
    blocked_reason_codes: list[str]
    required_fixes: list[str]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class TemporalBenchmarkRecoveryReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    applies_to_temporal_classification: bool
    comparison_contract_ready: bool
    fold_health_status: str | None
    blocked_reason_codes: list[str]
    recovery_state: str
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkPackPartition:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    partition_name: str
    dataset_fingerprint: str
    claim_origin: str
    partition_reason: str
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class HoldoutClaimPolicy:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    current_partition: str
    requires_holdout_for_paper_primary: bool
    development_claim_allowed: bool
    paper_primary_claim_allowed: bool
    claim_origin: str
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkGeneralizationAudit:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    identity_branching_detected: bool
    audited_artifacts: list[str]
    finding_count: int
    findings: list[dict[str, Any]]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AMLBenchmarkManifest:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    dataset_family: str
    benchmark_track: str
    task_type: str
    data_mode: str
    comparison_metric: str
    metric_direction: str
    selected_model_family: str | None
    current_partition: str
    supporting_public_claim_allowed: bool
    paper_primary_claim_allowed: bool
    required_track_families: list[str]
    covered_track_families: list[str]
    required_track_coverage_met: bool
    relaytic_rank: int | None
    public_table_rows: list[dict[str, Any]]
    top_case_entity: str | None
    top_typology: str | None
    drift_trigger_action: str | None
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AMLHoldoutClaimReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    dataset_family: str
    current_partition: str
    supporting_public_claim_allowed: bool
    paper_primary_claim_allowed: bool
    required_track_coverage_met: bool
    broader_flagship_claim_allowed: bool
    claim_origin: str
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AMLDemoScorecard:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    demo_safe: bool
    current_run_story: str | None
    ready_demo_count: int
    scored_demos: list[dict[str, Any]]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AMLPublicClaimGuard:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    supporting_public_claim_allowed: bool
    paper_primary_claim_allowed: bool
    broader_flagship_claim_allowed: bool
    required_track_coverage_met: bool
    blocked_reason_codes: list[str]
    allowed_claims: list[str]
    claim_boundaries: list[str]
    required_fixes: list[str]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AMLFailureReport:
    schema_version: str
    generated_at: str
    controls: BenchmarkControls
    status: str
    primary_failure_kind: str | None
    severity: str
    public_safe_to_discuss: bool
    recommended_next_step: str | None
    evidence_refs: list[str]
    summary: str
    trace: BenchmarkTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkBundle:
    reference_approach_matrix: ReferenceApproachMatrix
    benchmark_gap_report: BenchmarkGapReport
    benchmark_parity_report: BenchmarkParityReport
    external_challenger_manifest: ExternalChallengerManifest
    external_challenger_evaluation: ExternalChallengerEvaluation
    incumbent_parity_report: IncumbentParityReport
    beat_target_contract: BeatTargetContract
    paper_benchmark_manifest: PaperBenchmarkManifest
    paper_benchmark_table: PaperBenchmarkTable
    benchmark_ablation_matrix: BenchmarkAblationMatrix
    rerun_variance_report: RerunVarianceReport
    benchmark_claims_report: BenchmarkClaimsReport
    shadow_trial_manifest: ShadowTrialManifest
    shadow_trial_scorecard: ShadowTrialScorecard
    candidate_quarantine: CandidateQuarantine
    promotion_readiness_report: PromotionReadinessReport
    benchmark_truth_audit: BenchmarkTruthAudit
    paper_claim_guard_report: PaperClaimGuardReport
    benchmark_release_gate: BenchmarkReleaseGate
    dataset_leakage_audit: DatasetLeakageAudit
    temporal_benchmark_recovery_report: TemporalBenchmarkRecoveryReport
    benchmark_pack_partition: BenchmarkPackPartition
    holdout_claim_policy: HoldoutClaimPolicy
    benchmark_generalization_audit: BenchmarkGeneralizationAudit
    aml_benchmark_manifest: AMLBenchmarkManifest
    aml_holdout_claim_report: AMLHoldoutClaimReport
    aml_demo_scorecard: AMLDemoScorecard
    aml_public_claim_guard: AMLPublicClaimGuard
    aml_failure_report: AMLFailureReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_approach_matrix": self.reference_approach_matrix.to_dict(),
            "benchmark_gap_report": self.benchmark_gap_report.to_dict(),
            "benchmark_parity_report": self.benchmark_parity_report.to_dict(),
            "external_challenger_manifest": self.external_challenger_manifest.to_dict(),
            "external_challenger_evaluation": self.external_challenger_evaluation.to_dict(),
            "incumbent_parity_report": self.incumbent_parity_report.to_dict(),
            "beat_target_contract": self.beat_target_contract.to_dict(),
            "paper_benchmark_manifest": self.paper_benchmark_manifest.to_dict(),
            "paper_benchmark_table": self.paper_benchmark_table.to_dict(),
            "benchmark_ablation_matrix": self.benchmark_ablation_matrix.to_dict(),
            "rerun_variance_report": self.rerun_variance_report.to_dict(),
            "benchmark_claims_report": self.benchmark_claims_report.to_dict(),
            "shadow_trial_manifest": self.shadow_trial_manifest.to_dict(),
            "shadow_trial_scorecard": self.shadow_trial_scorecard.to_dict(),
            "candidate_quarantine": self.candidate_quarantine.to_dict(),
            "promotion_readiness_report": self.promotion_readiness_report.to_dict(),
            "benchmark_truth_audit": self.benchmark_truth_audit.to_dict(),
            "paper_claim_guard_report": self.paper_claim_guard_report.to_dict(),
            "benchmark_release_gate": self.benchmark_release_gate.to_dict(),
            "dataset_leakage_audit": self.dataset_leakage_audit.to_dict(),
            "temporal_benchmark_recovery_report": self.temporal_benchmark_recovery_report.to_dict(),
            "benchmark_pack_partition": self.benchmark_pack_partition.to_dict(),
            "holdout_claim_policy": self.holdout_claim_policy.to_dict(),
            "benchmark_generalization_audit": self.benchmark_generalization_audit.to_dict(),
            "aml_benchmark_manifest": self.aml_benchmark_manifest.to_dict(),
            "aml_holdout_claim_report": self.aml_holdout_claim_report.to_dict(),
            "aml_demo_scorecard": self.aml_demo_scorecard.to_dict(),
            "aml_public_claim_guard": self.aml_public_claim_guard.to_dict(),
            "aml_failure_report": self.aml_failure_report.to_dict(),
        }


def build_benchmark_controls_from_policy(policy: dict[str, Any]) -> BenchmarkControls:
    benchmark_cfg = dict(policy.get("benchmark", {}))
    try:
        max_reference_models = int(benchmark_cfg.get("max_reference_models", 3) or 3)
    except (TypeError, ValueError):
        max_reference_models = 3
    try:
        near_abs = float(benchmark_cfg.get("near_parity_absolute_delta", 0.03) or 0.03)
    except (TypeError, ValueError):
        near_abs = 0.03
    try:
        near_rel = float(benchmark_cfg.get("near_parity_relative_delta", 0.08) or 0.08)
    except (TypeError, ValueError):
        near_rel = 0.08
    return BenchmarkControls(
        enabled=bool(benchmark_cfg.get("enabled", True)),
        require_same_split_contract=bool(benchmark_cfg.get("require_same_split_contract", True)),
        require_same_metric_contract=bool(benchmark_cfg.get("require_same_metric_contract", True)),
        use_optional_flaml_reference=bool(benchmark_cfg.get("use_optional_flaml_reference", False)),
        allow_time_series_references=bool(benchmark_cfg.get("allow_time_series_references", True)),
        max_reference_models=max(2, min(6, max_reference_models)),
        near_parity_absolute_delta=max(0.0, min(0.25, near_abs)),
        near_parity_relative_delta=max(0.0, min(0.5, near_rel)),
    )

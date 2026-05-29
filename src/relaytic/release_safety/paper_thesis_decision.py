"""Paper Track P8-D thesis narrowing and evidence-role decision."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_THESIS_DECISION_SCHEMA_VERSION = "relaytic.paper_p8d_thesis_decision.v1"
PAPER_THESIS_DECISION_REPORT_DIR = Path("docs") / "reports"
PAPER_THESIS_DECISION_FILENAMES = {
    "paper_p8d_thesis_decision": "paper_p8d_thesis_decision.json",
    "paper_p8d_evidence_role_matrix": "paper_p8d_evidence_role_matrix.json",
    "paper_p8d_reprovisioning_decision": "paper_p8d_reprovisioning_decision.json",
    "paper_p8d_claim_rewrite_plan": "paper_p8d_claim_rewrite_plan.json",
}

ROUTE_NARROW = "narrow_first_paper_to_claim_gated_evaluation_environment"
ROUTE_REPROVISION = "reprovision_faithful_revclassify_parity_before_p9"
ROUTE_BLOCKED = "no_accepted_thesis_route"


def build_paper_p8d_thesis_pack(
    project_root: str | Path,
    *,
    route: str = "narrow",
) -> dict[str, Any]:
    """Build P8-D thesis-decision artifacts from committed P8-B/P8-C gates."""
    root = Path(project_root)
    gate_inputs = _collect_gate_inputs(root)
    thesis_decision = _build_thesis_decision(gate_inputs=gate_inputs, route=route)
    evidence_role_matrix = _build_evidence_role_matrix(
        gate_inputs=gate_inputs,
        thesis_decision=thesis_decision,
    )
    reprovisioning_decision = _build_reprovisioning_decision(
        gate_inputs=gate_inputs,
        thesis_decision=thesis_decision,
    )
    claim_rewrite_plan = _build_claim_rewrite_plan(
        gate_inputs=gate_inputs,
        thesis_decision=thesis_decision,
    )
    return {
        "paper_p8d_thesis_decision": thesis_decision,
        "paper_p8d_evidence_role_matrix": evidence_role_matrix,
        "paper_p8d_reprovisioning_decision": reprovisioning_decision,
        "paper_p8d_claim_rewrite_plan": claim_rewrite_plan,
    }


def sync_paper_p8d_thesis_pack(
    project_root: str | Path,
    *,
    route: str = "narrow",
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P8-D thesis-decision artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_THESIS_DECISION_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paper_p8d_thesis_pack(root, route=route)
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in PAPER_THESIS_DECISION_FILENAMES.items()
    }


def render_paper_p8d_thesis_markdown(pack: dict[str, Any]) -> str:
    decision = dict(pack.get("paper_p8d_thesis_decision", {}))
    reprovision = dict(pack.get("paper_p8d_reprovisioning_decision", {}))
    claims = dict(pack.get("paper_p8d_claim_rewrite_plan", {}))
    return "\n".join(
        [
            "# Paper P8-D Thesis Decision",
            "",
            f"- Status: `{decision.get('status') or 'unknown'}`",
            f"- Selected route: `{decision.get('selected_route') or 'unknown'}`",
            f"- P9 allowed: `{decision.get('p9_allowed')}`",
            f"- Elliptic2 performance contribution allowed: `{decision.get('elliptic2_performance_contribution_allowed')}`",
            f"- Reprovisioning strategy: `{reprovision.get('selected_strategy') or 'unknown'}`",
            f"- Claim language updated: `{claims.get('claim_language_updated')}`",
            f"- Next slice: `{decision.get('next_slice') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _collect_gate_inputs(root: Path) -> dict[str, Any]:
    report_dir = root / PAPER_THESIS_DECISION_REPORT_DIR
    p8b_gate = _load_artifact(report_dir / "elliptic2_publishability_gate.json")
    p8c_gate = _load_artifact(report_dir / "elliptic2_reference_parity_gate.json")
    p8c_split = _load_artifact(report_dir / "elliptic2_entity_disjoint_split_report.json")
    p8c_cohort = _load_artifact(report_dir / "elliptic2_evaluable_cohort_reconciliation.json")
    p8c_neural = _load_artifact(report_dir / "elliptic2_neural_candidate_scorecard.json")
    p8b_repeated = _load_artifact(report_dir / "elliptic2_repeated_seed_scorecard.json")
    return {
        "p8b_gate": p8b_gate,
        "p8c_gate": p8c_gate,
        "p8c_split": p8c_split,
        "p8c_cohort": p8c_cohort,
        "p8c_neural": p8c_neural,
        "p8b_repeated": p8b_repeated,
    }


def _build_thesis_decision(*, gate_inputs: dict[str, Any], route: str) -> dict[str, Any]:
    normalized_route = _normalize_route(route)
    p8b = _payload(gate_inputs["p8b_gate"])
    p8c = _payload(gate_inputs["p8c_gate"])
    split = _payload(gate_inputs["p8c_split"])
    cohort = _payload(gate_inputs["p8c_cohort"])
    neural = _payload(gate_inputs["p8c_neural"])
    p8b_recorded = _is_expected_slice(gate_inputs["p8b_gate"], "Paper Track P8-B")
    p8c_recorded = _is_expected_slice(gate_inputs["p8c_gate"], "Paper Track P8-C")
    p8b_supporting = bool(p8b.get("supporting_paper_row_allowed"))
    p8c_blocks_parity = p8c_recorded and not bool(p8c.get("reference_parity_claim_allowed"))
    p8c_supporting = bool(p8c.get("supporting_modern_context_row_allowed"))
    accepted_narrowing = (
        normalized_route == ROUTE_NARROW
        and p8b_recorded
        and p8b_supporting
        and p8c_recorded
        and p8c_blocks_parity
        and p8c_supporting
    )
    accepted_reprovision = normalized_route == ROUTE_REPROVISION and p8c_recorded
    route_accepted = accepted_narrowing or accepted_reprovision
    p9_allowed = accepted_narrowing
    status = (
        "accepted_thesis_narrowing"
        if accepted_narrowing
        else "accepted_reprovision_before_p9"
        if accepted_reprovision
        else "blocked_pending_p8b_p8c_gate_truth"
    )
    direct_gate_consumption = _direct_gate_consumption(gate_inputs)
    return {
        "schema_version": PAPER_THESIS_DECISION_SCHEMA_VERSION,
        "slice": "Paper Track P8-D",
        "status": status,
        "selected_route": normalized_route if route_accepted else ROUTE_BLOCKED,
        "route_requested": route,
        "route_accepted": route_accepted,
        "p9_allowed": p9_allowed,
        "next_slice": (
            "Paper Track P9 - operational AML evaluation layer"
            if p9_allowed
            else "Paper Track P8-D follow-up - reprovision or accept thesis route before P9"
        ),
        "direct_gate_consumption": direct_gate_consumption,
        "minimum_proof_checks": {
            "p8b_gate_consumed": p8b_recorded,
            "p8c_gate_consumed": p8c_recorded,
            "explicit_route_chosen": route_accepted,
            "allowed_blocked_claim_language_updated": p9_allowed,
            "future_modern_subgraph_parity_option_preserved": True,
        },
        "gate_summary": {
            "p8b": {
                "artifact_ref": "docs/reports/elliptic2_publishability_gate.json",
                "exists": gate_inputs["p8b_gate"]["exists"],
                "status": p8b.get("status"),
                "supporting_paper_row_allowed": p8b_supporting,
                "reference_parity_claim_allowed": bool(p8b.get("reference_parity_claim_allowed")),
                "headline_or_sota_claim_allowed": bool(p8b.get("headline_or_sota_claim_allowed")),
                "selected_official_test_pr_auc_mean": p8b.get("selected_official_test_pr_auc_mean"),
                "published_reference_pr_auc": p8b.get("published_reference_pr_auc"),
                "official_gap_to_published_revclassify_ds": p8b.get("official_gap_to_published_revclassify_ds"),
            },
            "p8c": {
                "artifact_ref": "docs/reports/elliptic2_reference_parity_gate.json",
                "exists": gate_inputs["p8c_gate"]["exists"],
                "status": p8c.get("status"),
                "supporting_modern_context_row_allowed": p8c_supporting,
                "reference_parity_claim_allowed": bool(p8c.get("reference_parity_claim_allowed")),
                "headline_or_sota_claim_allowed": bool(p8c.get("headline_or_sota_claim_allowed")),
                "full_core_modern_subgraph_claim_allowed": bool(
                    p8c.get("full_core_modern_subgraph_claim_allowed")
                ),
                "p9_allowed_before_p8d": bool(p8c.get("p9_allowed")),
                "paper_strategy_decision": p8c.get("paper_strategy_decision"),
            },
            "cohort": {
                "artifact_ref": "docs/reports/elliptic2_evaluable_cohort_reconciliation.json",
                "exists": gate_inputs["p8c_cohort"]["exists"],
                "revtrack_evaluable_row_count": cohort.get("revtrack_evaluable_row_count"),
                "official_core_subgraph_count": cohort.get("official_core_subgraph_count"),
                "full_core_equivalence_proven": bool(cohort.get("full_core_equivalence_proven")),
            },
            "entity_split": {
                "artifact_ref": "docs/reports/elliptic2_entity_disjoint_split_report.json",
                "exists": gate_inputs["p8c_split"]["exists"],
                "status": split.get("status"),
                "strict_entity_disjoint_split_viable": bool(split.get("strict_entity_disjoint_split_viable")),
                "largest_component_row_fraction": _largest_component_fraction(split),
                "largest_component_row_count": _largest_component_row_count(split),
            },
            "neural_replay": {
                "artifact_ref": "docs/reports/elliptic2_neural_candidate_scorecard.json",
                "exists": gate_inputs["p8c_neural"]["exists"],
                "status": neural.get("status"),
                "run_neural_requested": neural.get("run_neural_requested"),
                "neural_reference_parity_met": bool(neural.get("neural_reference_parity_met")),
                "best_local_neural_pr_auc_mean": neural.get("best_local_neural_pr_auc_mean"),
            },
        },
        "accepted_first_paper_thesis": (
            "Relaytic-AML is a local-first, claim-gated evaluation environment for AML-relevant temporal, graph, "
            "operational, and reproducibility evidence; it is not presented as a modern subgraph SOTA model paper."
            if accepted_narrowing
            else None
        ),
        "elliptic2_role_after_decision": (
            "supporting_context_and_limitation_only"
            if accepted_narrowing
            else "blocked_pending_reprovision"
            if accepted_reprovision
            else "blocked_pending_thesis_decision"
        ),
        "elliptic2_performance_contribution_allowed": False,
        "headline_or_sota_claim_allowed": False,
        "hard_aml_claim_allowed": False,
        "reference_parity_claim_allowed": False,
        "claim_boundary": {
            "allowed": [
                "claim_gated_aml_evaluation_environment",
                "benchmark_track_discipline_with_explicit_supporting_proxy_and_blocked_roles",
                "p8b_as_modern_context_supporting_evidence_only",
                "p8c_as_auditable_limitation_and_claim-firewall_evidence",
                "p9_operational_metrics_after_their_own_assumption_and_claim_guards_pass",
            ] if accepted_narrowing else [],
            "blocked": [
                "elliptic2_or_modern_subgraph_sota_claim",
                "revclassify_reference_parity_claim",
                "full_current_core_elliptic2_claim",
                "entity_disjoint_generalization_claim",
                "hard_real_world_aml_superiority_claim",
                "end_to_end_relaytic_superiority_on_elliptic2",
                "elliptic2_primary_performance_contribution_in_first_paper",
            ],
        },
        "future_return_path": {
            "modern_subgraph_parity_can_return": True,
            "return_condition": (
                "Run a faithful RevClassify BP/DS replay or stronger candidate under an accepted cohort protocol, "
                "three or more seeds, no test-selection leakage, and a compute/dependency environment recorded outside git."
            ),
            "first_paper_blocked_by_return_path": False if accepted_narrowing else True,
        },
        "summary": (
            "P8-D accepts the narrowed first-paper thesis: P8-B remains supporting modern-context evidence, P8-C "
            "is used as a claim-firewall and limitation, and P9 may now add operational AML metrics without "
            "presenting Elliptic2 as a performance contribution."
            if accepted_narrowing
            else "P8-D did not accept thesis narrowing; P9 remains blocked until reprovisioning or another thesis route passes."
        ),
    }


def _build_evidence_role_matrix(
    *,
    gate_inputs: dict[str, Any],
    thesis_decision: dict[str, Any],
) -> dict[str, Any]:
    p8b = _payload(gate_inputs["p8b_gate"])
    p8c = _payload(gate_inputs["p8c_gate"])
    split = _payload(gate_inputs["p8c_split"])
    p9_allowed = bool(thesis_decision.get("p9_allowed"))
    return {
        "schema_version": PAPER_THESIS_DECISION_SCHEMA_VERSION,
        "slice": "Paper Track P8-D",
        "status": "evidence_roles_frozen" if p9_allowed else "blocked_pending_accepted_route",
        "selected_route": thesis_decision.get("selected_route"),
        "p9_allowed": p9_allowed,
        "rows": [
            _role_row(
                evidence_id="paysim_competitive_p6a",
                track_id="paysim_temporal_transaction_fraud",
                role="supporting_temporal_proxy_numeric_and_operational_seed",
                artifact_refs=[
                    "docs/reports/paysim_publishability_gate.json",
                    "docs/reports/paysim_competitive_baseline_table.json",
                    "docs/reports/paysim_competitive_budget_contract.json",
                ],
                paper_table_eligibility="supporting_numeric_table_candidate",
                claim_level="proxy_supporting_only",
                performance_contribution_allowed=False,
                operational_metric_candidate=True,
                can_appear_in_headline=False,
                rationale="Useful temporal rare-event proxy evidence, but synthetic PaySim cannot carry hard real-world AML superiority.",
            ),
            _role_row(
                evidence_id="elliptic_raw_graph_p7",
                track_id="elliptic_flattened_graph_aml",
                role="supporting_temporal_graph_numeric_candidate",
                artifact_refs=[
                    "docs/reports/paper_graph_publishability_gate.json",
                    "docs/reports/paper_graph_feature_table.json",
                    "docs/reports/paper_graph_budget_contract.json",
                ],
                paper_table_eligibility="supporting_graph_table_candidate",
                claim_level="supporting_only",
                performance_contribution_allowed=False,
                operational_metric_candidate=True,
                can_appear_in_headline=False,
                rationale="P7 records real raw-graph provenance and a strong classical graph-feature baseline, but graph-neural/SOTA claims remain blocked.",
            ),
            _role_row(
                evidence_id="elliptic2_modern_context_p8b",
                track_id="elliptic2_subgraph_aml",
                role="modern_subgraph_context_only",
                artifact_refs=[
                    "docs/reports/elliptic2_publishability_gate.json",
                    "docs/reports/elliptic2_repeated_seed_scorecard.json",
                    "docs/reports/elliptic2_split_robustness_report.json",
                ],
                paper_table_eligibility="context_or_limitations_table_only",
                claim_level="supporting_context_only",
                performance_contribution_allowed=False,
                operational_metric_candidate=False,
                can_appear_in_headline=False,
                rationale=(
                    "P8-B is stable and relevant but below reported RevClassifyDS, consumes official preprocessing, "
                    "and does not prove full-core or entity-disjoint generalization."
                ),
                supporting_metric_snapshot={
                    "official_partition_pr_auc_mean": p8b.get("selected_official_test_pr_auc_mean"),
                    "published_reference_pr_auc": p8b.get("published_reference_pr_auc"),
                    "gap_to_published_reference": p8b.get("official_gap_to_published_revclassify_ds"),
                },
            ),
            _role_row(
                evidence_id="elliptic2_reference_parity_blocker_p8c",
                track_id="elliptic2_subgraph_aml",
                role="limitation_and_claim_firewall",
                artifact_refs=[
                    "docs/reports/elliptic2_reference_parity_gate.json",
                    "docs/reports/elliptic2_entity_disjoint_split_report.json",
                    "docs/reports/elliptic2_evaluable_cohort_reconciliation.json",
                ],
                paper_table_eligibility="limitations_or_methodology_table_only",
                claim_level="blocked_claim_evidence",
                performance_contribution_allowed=False,
                operational_metric_candidate=False,
                can_appear_in_headline=False,
                rationale=(
                    "P8-C directly blocks reference parity, SOTA, full-core, and entity-disjoint claims; it is "
                    "evidence of claim discipline, not a performance win."
                ),
                supporting_metric_snapshot={
                    "p8c_status": p8c.get("status"),
                    "strict_entity_disjoint_split_viable": bool(split.get("strict_entity_disjoint_split_viable")),
                    "largest_component_row_fraction": _largest_component_fraction(split),
                },
            ),
            _role_row(
                evidence_id="amlsim_p8",
                track_id="amlsim_synthetic_bank_graph",
                role="future_synthetic_typology_proxy",
                artifact_refs=[
                    "docs/reports/amlsim_generation_manifest.json",
                    "docs/reports/amlsim_typology_manifest.json",
                ],
                paper_table_eligibility="blocked_until_reproducible_generation_or_proxy_appendix_only",
                claim_level="blocked_or_proxy_future",
                performance_contribution_allowed=False,
                operational_metric_candidate=True,
                can_appear_in_headline=False,
                rationale="AMLSim can support typology/workflow proof only after seeded generation, hashes, license, and typology distribution are frozen.",
            ),
            _role_row(
                evidence_id="generic_structured_support_pack",
                track_id="generic_structured_supporting_pack",
                role="breadth_and_sanity_context",
                artifact_refs=[
                    "docs/specs/paper_benchmark_pack.md",
                    "tests/test_paper_benchmark_pack.py",
                ],
                paper_table_eligibility="supporting_appendix_only",
                claim_level="supporting_breadth_only",
                performance_contribution_allowed=False,
                operational_metric_candidate=False,
                can_appear_in_headline=False,
                rationale="Generic structured-data evidence supports breadth and reliability context, not the flagship AML proof.",
            ),
        ],
        "table_rules": {
            "primary_performance_table_can_include_elliptic2": False,
            "elliptic2_allowed_table_context": "supporting context, blocker, limitation, or appendix only",
            "all_numeric_rows_need_budget_split_leakage_and_gate_refs": True,
            "operational_rows_require_p9_claim_guard": True,
        },
    }


def _build_reprovisioning_decision(
    *,
    gate_inputs: dict[str, Any],
    thesis_decision: dict[str, Any],
) -> dict[str, Any]:
    p8c = _payload(gate_inputs["p8c_gate"])
    split = _payload(gate_inputs["p8c_split"])
    neural = _payload(gate_inputs["p8c_neural"])
    p9_allowed = bool(thesis_decision.get("p9_allowed"))
    selected_strategy = (
        "defer_faithful_revclassify_reprovisioning_for_first_paper"
        if p9_allowed
        else "reprovision_before_p9"
        if thesis_decision.get("selected_route") == ROUTE_REPROVISION
        else "no_strategy_accepted"
    )
    return {
        "schema_version": PAPER_THESIS_DECISION_SCHEMA_VERSION,
        "slice": "Paper Track P8-D",
        "status": "reprovisioning_deferred_with_return_path" if p9_allowed else "p9_blocked_pending_reprovision",
        "selected_strategy": selected_strategy,
        "p9_unblocked_by_thesis_narrowing": p9_allowed,
        "reprovision_now": thesis_decision.get("selected_route") == ROUTE_REPROVISION,
        "why_not_reprovision_before_first_paper": [
            "P8-C already records missing faithful RevClassify local preconditions.",
            "The pinned public repository does not distribute RevClassify classification checkpoints.",
            "The current local environment lacks a CUDA-class accelerator for the reference-scale budget.",
            "The RevTrack-evaluable cohort is not proven equivalent to the audited current official core.",
            "The strict component-grouped entity-disjoint split degenerates and is not a meaningful evaluation protocol.",
            "Waiting for reprovisioning would block operational-evaluation evidence that is central to the narrower paper thesis.",
        ] if p9_allowed else [],
        "direct_blocker_refs": {
            "p8c_gate_status": p8c.get("status"),
            "p8c_blocked_reason_codes": p8c.get("blocked_reason_codes", []),
            "neural_scorecard_status": neural.get("status"),
            "entity_split_status": split.get("status"),
            "largest_component_row_fraction": _largest_component_fraction(split),
        },
        "future_reprovision_requirements": [
            "Record a GPU/dependency environment capable of faithful RevClassify BP and DS replay.",
            "Install and version the official Lightning, Hydra, OmegaConf, TorchMetrics, PyTorch, and graph dependency stack outside git.",
            "Obtain or train reference classification checkpoints under a declared budget; never commit raw checkpoints if license or size disallows it.",
            "Run at least three seeds for the accepted reference and Relaytic candidate paths.",
            "Predeclare the cohort mapping from RevTrack rows to the current official Elliptic2 core, or explicitly define a defensible fixed cohort.",
            "Use validation-only model and threshold selection; keep the official test partition out of candidate selection.",
            "Adopt a leakage-resistant split protocol that is meaningful for the observed identity-component structure.",
            "Emit a new publishability gate before any modern-subgraph performance contribution is allowed.",
        ],
        "return_path_name": "post_first_paper_modern_subgraph_parity_extension",
        "first_paper_dependency": "not_required" if p9_allowed else "required_before_p9",
    }


def _build_claim_rewrite_plan(
    *,
    gate_inputs: dict[str, Any],
    thesis_decision: dict[str, Any],
) -> dict[str, Any]:
    p9_allowed = bool(thesis_decision.get("p9_allowed"))
    return {
        "schema_version": PAPER_THESIS_DECISION_SCHEMA_VERSION,
        "slice": "Paper Track P8-D",
        "status": "claim_rewrite_ready" if p9_allowed else "claim_rewrite_blocked_pending_route",
        "claim_language_updated": p9_allowed,
        "selected_route": thesis_decision.get("selected_route"),
        "p9_allowed": p9_allowed,
        "allowed_claim_language": [
            "Relaytic-AML is a claim-gated AML evaluation environment that binds benchmark evidence, operational metrics, reproducibility, and public-claim boundaries to local artifacts.",
            "P8-B provides stable supporting modern-context Elliptic2 evidence on the pinned RevTrack-evaluable cohort.",
            "P8-C documents why modern-subgraph reference parity, full-core, and entity-disjoint claims are not currently supported.",
            "P9 may evaluate review capacity, case-packet completeness, false-positive burden, and analyst-facing utility as primary paper axes after its own gates pass.",
        ] if p9_allowed else [],
        "blocked_claim_language": [
            "Relaytic-AML is state of the art on Elliptic2.",
            "Relaytic matches or beats RevClassifyDS on the official Elliptic2 benchmark.",
            "Relaytic proves full-current-core Elliptic2 performance.",
            "Relaytic proves entity-disjoint modern-subgraph generalization.",
            "Relaytic has hard real-world AML superiority evidence.",
            "The P8-B Elliptic2 number is a primary performance contribution.",
        ],
        "section_rewrite_plan": [
            {
                "paper_section": "title_and_abstract",
                "rewrite_action": "center claim-gated evaluation environments and operational AML evidence; avoid model-SOTA framing",
            },
            {
                "paper_section": "results",
                "rewrite_action": "separate supporting proxy/graph numbers from blocked modern-subgraph parity claims",
            },
            {
                "paper_section": "tables",
                "rewrite_action": "label every row by evidence role, budget tier, leakage posture, and publishability gate; keep Elliptic2 out of primary performance-contribution columns",
            },
            {
                "paper_section": "limitations",
                "rewrite_action": "state the P8-C faithful-replay, cohort-equivalence, and entity-disjoint blockers explicitly",
            },
            {
                "paper_section": "future_work",
                "rewrite_action": "describe a GPU-backed RevClassify parity/reprovisioning extension without making it a first-paper dependency",
            },
        ],
        "claim_lint_rules": [
            {
                "rule_id": "no_unqualified_sota",
                "blocked_terms": ["SOTA", "state-of-the-art", "best", "beats RevClassify"],
                "allowed_context": "Only allowed when the same sentence says the claim is blocked or unsupported.",
            },
            {
                "rule_id": "elliptic2_context_only",
                "blocked_terms": ["Elliptic2 performance contribution", "official Elliptic2 winner"],
                "allowed_context": "Only context, limitation, or appendix wording is permitted before a later parity gate passes.",
            },
            {
                "rule_id": "operational_claims_need_p9",
                "blocked_terms": ["analyst-hour savings", "false-positive reduction", "review-capacity gain"],
                "allowed_context": "Allowed only when backed by P9 operational artifacts and assumptions.",
            },
        ],
        "downstream_consumers": [
            "Paper Track P9 operational metric gate",
            "Paper Track P10 reproducible table generator",
            "Paper Track P11 claim-linted paper draft",
            "Paper Track P12 external dry run",
        ],
        "source_gate_refs": _direct_gate_consumption(gate_inputs),
    }


def _load_artifact(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"artifact_ref": _as_report_ref(path), "exists": False, "payload": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        payload = {"status": "unreadable", "error": str(exc)}
    return {"artifact_ref": _as_report_ref(path), "exists": True, "payload": payload}


def _as_report_ref(path: Path) -> str:
    parts = path.parts
    if "docs" in parts:
        return Path(*parts[parts.index("docs"):]).as_posix()
    return path.as_posix()


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload", {})
    return dict(payload) if isinstance(payload, dict) else {}


def _is_expected_slice(artifact: dict[str, Any], expected: str) -> bool:
    return bool(artifact.get("exists")) and _payload(artifact).get("slice") == expected


def _normalize_route(route: str) -> str:
    normalized = str(route or "").strip().lower().replace("-", "_")
    if normalized in {"narrow", "narrow_first_paper", ROUTE_NARROW}:
        return ROUTE_NARROW
    if normalized in {"reprovision", "reprovision_before_p9", ROUTE_REPROVISION}:
        return ROUTE_REPROVISION
    return ROUTE_BLOCKED


def _largest_component_fraction(split: dict[str, Any]) -> float | None:
    value = (
        dict(dict(split.get("strict_component_protocol", {})).get("all_role_entity_components", {}))
        .get("largest_component_row_fraction")
    )
    return float(value) if isinstance(value, int | float) else None


def _largest_component_row_count(split: dict[str, Any]) -> int | None:
    value = (
        dict(dict(split.get("strict_component_protocol", {})).get("all_role_entity_components", {}))
        .get("largest_component_row_count")
    )
    return int(value) if isinstance(value, int | float) else None


def _direct_gate_consumption(gate_inputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    expected = {
        "p8b_gate": "Paper Track P8-B",
        "p8c_gate": "Paper Track P8-C",
        "p8c_split": "Paper Track P8-C",
        "p8c_cohort": "Paper Track P8-C",
        "p8c_neural": "Paper Track P8-C",
    }
    for key, artifact in gate_inputs.items():
        payload = _payload(artifact)
        rows.append(
            {
                "input_id": key,
                "artifact_ref": artifact.get("artifact_ref"),
                "exists": bool(artifact.get("exists")),
                "expected_slice": expected.get(key),
                "observed_slice": payload.get("slice"),
                "status": payload.get("status"),
                "used_as_gate_input": key in expected,
            }
        )
    return rows


def _role_row(
    *,
    evidence_id: str,
    track_id: str,
    role: str,
    artifact_refs: list[str],
    paper_table_eligibility: str,
    claim_level: str,
    performance_contribution_allowed: bool,
    operational_metric_candidate: bool,
    can_appear_in_headline: bool,
    rationale: str,
    supporting_metric_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "evidence_id": evidence_id,
        "track_id": track_id,
        "role": role,
        "artifact_refs": artifact_refs,
        "paper_table_eligibility": paper_table_eligibility,
        "claim_level": claim_level,
        "performance_contribution_allowed": performance_contribution_allowed,
        "operational_metric_candidate": operational_metric_candidate,
        "can_appear_in_headline": can_appear_in_headline,
        "rationale": rationale,
        "supporting_metric_snapshot": supporting_metric_snapshot or {},
    }

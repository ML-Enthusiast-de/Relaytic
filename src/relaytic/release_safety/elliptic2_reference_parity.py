"""Reference-parity and leakage-resistance gate for Elliptic2 Paper Track P8-C."""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from importlib import metadata as importlib_metadata
import importlib.util
import json
from pathlib import Path
import platform
from typing import Any

import numpy as np
import pandas as pd

from relaytic.core.json_utils import write_json

from . import elliptic2_competitive as competitive
from . import elliptic2_recovery as recovery


ELLIPTIC2_REFERENCE_PARITY_SCHEMA_VERSION = "relaytic.elliptic2_reference_parity.v1"
ELLIPTIC2_REFERENCE_PARITY_REPORT_DIR = Path("docs") / "reports"
ELLIPTIC2_REFERENCE_PARITY_FILENAMES = {
    "elliptic2_neural_reference_parity_contract": "elliptic2_neural_reference_parity_contract.json",
    "elliptic2_evaluable_cohort_reconciliation": "elliptic2_evaluable_cohort_reconciliation.json",
    "elliptic2_entity_disjoint_split_report": "elliptic2_entity_disjoint_split_report.json",
    "elliptic2_neural_candidate_scorecard": "elliptic2_neural_candidate_scorecard.json",
    "elliptic2_reference_parity_gate": "elliptic2_reference_parity_gate.json",
}
ELLIPTIC2_REFERENCE_PARITY_MARGIN = competitive.ELLIPTIC2_PARITY_MARGIN
ELLIPTIC2_ENTITY_COLUMNS = ["senders", "source", "sink", "receivers", "node_ids"]
ELLIPTIC2_BOUNDARY_ENTITY_COLUMNS = ["senders", "receivers"]
ELLIPTIC2_REFERENCE_CANDIDATES = [
    {
        "candidate_id": "official_revclassify_bp_full_shot",
        "family": "RevClassifyBP",
        "configuration_path": "configurations/sweep/subgraph_classification/full_shot/BP.yaml",
        "reported_pr_auc": competitive.ELLIPTIC2_PUBLISHED_REFERENCE["RevClassify_BP"]["pr_auc"],
        "reported_f1": competitive.ELLIPTIC2_PUBLISHED_REFERENCE["RevClassify_BP"]["f1"],
    },
    {
        "candidate_id": "official_revclassify_ds_full_shot",
        "family": "RevClassifyDS",
        "configuration_path": "configurations/sweep/subgraph_classification/full_shot/DS.yaml",
        "reported_pr_auc": competitive.ELLIPTIC2_PUBLISHED_REFERENCE["RevClassify_DS"]["pr_auc"],
        "reported_f1": competitive.ELLIPTIC2_PUBLISHED_REFERENCE["RevClassify_DS"]["f1"],
    },
]


def build_elliptic2_reference_parity_pack(
    project_root: str | Path,
    *,
    core_data_dir: str | Path | None = None,
    revtrack_dir: str | Path | None = None,
    run_neural: bool = False,
) -> dict[str, Any]:
    """Build P8-C artifacts with fail-closed neural, cohort, and leakage claims."""
    root = Path(project_root)
    resolved_revtrack_dir = _resolve_dir(root, revtrack_dir, recovery.DEFAULT_REVTRACK_DIR)
    modern = recovery._build_modern_reference_contract(  # noqa: SLF001 - same bounded release-safety package
        root=root,
        revtrack_dir=resolved_revtrack_dir,
        extraction_report=None,
        hash_large_assets=False,
    )
    core_audit = _load_core_audit(root=root, core_data_dir=core_data_dir)
    data = _load_revtrack_data(resolved_revtrack_dir, modern)
    p8b_gate = _read_json(root / "docs" / "reports" / "elliptic2_publishability_gate.json")
    p8b_repeated = _read_json(root / "docs" / "reports" / "elliptic2_repeated_seed_scorecard.json")

    contract = _build_neural_reference_parity_contract(
        root=root,
        revtrack_dir=resolved_revtrack_dir,
        modern=modern,
        run_neural=run_neural,
    )
    cohort = _build_cohort_reconciliation(
        data=data,
        core_audit=core_audit,
        modern=modern,
    )
    split = _build_entity_disjoint_split_report(data=data, modern=modern)
    neural = _build_neural_candidate_scorecard(
        contract=contract,
        p8b_gate=p8b_gate,
        p8b_repeated=p8b_repeated,
        run_neural=run_neural,
    )
    gate = _build_reference_parity_gate(
        contract=contract,
        cohort=cohort,
        split=split,
        neural=neural,
        p8b_gate=p8b_gate,
    )
    return {
        "elliptic2_neural_reference_parity_contract": contract,
        "elliptic2_evaluable_cohort_reconciliation": cohort,
        "elliptic2_entity_disjoint_split_report": split,
        "elliptic2_neural_candidate_scorecard": neural,
        "elliptic2_reference_parity_gate": gate,
    }


def sync_elliptic2_reference_parity_pack(
    project_root: str | Path,
    *,
    core_data_dir: str | Path | None = None,
    revtrack_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    run_neural: bool = False,
) -> dict[str, Path]:
    """Write P8-C reference-parity artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / ELLIPTIC2_REFERENCE_PARITY_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_elliptic2_reference_parity_pack(
        root,
        core_data_dir=core_data_dir,
        revtrack_dir=revtrack_dir,
        run_neural=run_neural,
    )
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in ELLIPTIC2_REFERENCE_PARITY_FILENAMES.items()
    }


def render_elliptic2_reference_parity_markdown(pack: dict[str, Any]) -> str:
    contract = dict(pack.get("elliptic2_neural_reference_parity_contract", {}))
    cohort = dict(pack.get("elliptic2_evaluable_cohort_reconciliation", {}))
    split = dict(pack.get("elliptic2_entity_disjoint_split_report", {}))
    neural = dict(pack.get("elliptic2_neural_candidate_scorecard", {}))
    gate = dict(pack.get("elliptic2_reference_parity_gate", {}))
    component = dict(split.get("strict_component_protocol", {})).get("all_role_entity_components", {})
    return "\n".join(
        [
            "# Elliptic2 Reference Parity And Leakage Gate",
            "",
            f"- Gate: `{gate.get('status') or 'unknown'}`",
            f"- Faithful neural execution ready: `{contract.get('faithful_neural_execution_preconditions_met')}`",
            f"- Full-core cohort equivalence proven: `{cohort.get('full_core_equivalence_proven')}`",
            f"- RevTrack-evaluable rows: `{cohort.get('revtrack_evaluable_row_count')}`",
            f"- Largest strict entity component fraction: `{component.get('largest_component_row_fraction')}`",
            f"- Entity-disjoint split viable: `{split.get('strict_entity_disjoint_split_viable')}`",
            f"- Neural scorecard status: `{neural.get('status') or 'unknown'}`",
            f"- Reference parity claim allowed: `{gate.get('reference_parity_claim_allowed')}`",
            f"- Next slice: `{gate.get('next_slice') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _build_neural_reference_parity_contract(
    *,
    root: Path,
    revtrack_dir: Path,
    modern: dict[str, Any],
    run_neural: bool,
) -> dict[str, Any]:
    package_matrix = {
        row["package_id"]: row
        for row in [
            _package_state("torch"),
            _package_state("lightning", module_name="lightning"),
            _package_state("hydra-core", module_name="hydra"),
            _package_state("omegaconf", module_name="omegaconf"),
            _package_state("torchmetrics", module_name="torchmetrics"),
            _package_state("torch-geometric", module_name="torch_geometric"),
            _package_state("torch-scatter", module_name="torch_scatter"),
            _package_state("torch-sparse", module_name="torch_sparse"),
            _package_state("wandb", module_name="wandb"),
        ]
    }
    torch_runtime = _torch_runtime()
    config_checks = [
        _file_check(root, revtrack_dir / candidate["configuration_path"])
        for candidate in ELLIPTIC2_REFERENCE_CANDIDATES
    ]
    classification_checkpoints = sorted(
        [
            path
            for path in (revtrack_dir / "checkpoints").glob("RevClassify*/*.ckpt")
            if path.is_file()
        ]
    ) if (revtrack_dir / "checkpoints").is_dir() else []
    recommendation_checkpoints = sorted(
        [
            path
            for family in ["RevTrack", "LightGCN", "NGCF", "MLP"]
            for path in (revtrack_dir / "checkpoints" / family).glob("*.ckpt")
            if path.is_file()
        ]
    ) if (revtrack_dir / "checkpoints").is_dir() else []
    required_missing = [
        package_id
        for package_id in ["torch", "lightning", "hydra-core", "omegaconf", "torchmetrics"]
        if not package_matrix[package_id]["available"]
    ]
    blockers: list[str] = []
    if modern.get("status") != "ready_for_context_pilot":
        blockers.append("pinned_modern_reference_assets_not_ready")
    if required_missing:
        blockers.extend(f"official_revclassify_dependency_{name}_missing" for name in required_missing)
    if not all(row["exists"] for row in config_checks):
        blockers.append("official_revclassify_full_shot_configs_missing")
    if int(torch_runtime.get("cuda_device_count") or 0) < 1:
        blockers.append("local_accelerator_not_available_for_faithful_revclassify_budget")
    if not classification_checkpoints:
        blockers.append("official_revclassify_classification_checkpoints_not_distributed")
    if not run_neural:
        blockers.append("faithful_neural_execution_not_requested")
    executable = not [code for code in blockers if code != "faithful_neural_execution_not_requested"]
    return {
        "schema_version": ELLIPTIC2_REFERENCE_PARITY_SCHEMA_VERSION,
        "slice": "Paper Track P8-C",
        "status": "ready_to_execute" if executable and run_neural else "blocked_or_not_requested",
        "reference_id": competitive.ELLIPTIC2_PUBLISHED_REFERENCE["reference_id"],
        "published_reference": competitive.ELLIPTIC2_PUBLISHED_REFERENCE,
        "reference_repository": {
            "url": "https://github.com/MITIBMxGraph/RevTrack",
            "commit": recovery.PINNED_REVTRACK_COMMIT,
            "source_path": _display_path(root, revtrack_dir),
            "official_full_shot_configuration_checks": config_checks,
            "classification_checkpoint_count": len(classification_checkpoints),
            "recommendation_checkpoint_count": len(recommendation_checkpoints),
        },
        "required_reference_candidates": ELLIPTIC2_REFERENCE_CANDIDATES,
        "faithful_execution_budget_contract": {
            "required_metric": "final_test/prauc",
            "selection_surface": "official validation/prauc only; test is not a tuning surface",
            "minimum_seed_count_for_claim": 3,
            "reference_parity_margin": ELLIPTIC2_REFERENCE_PARITY_MARGIN,
            "expected_accelerator": "CUDA-class GPU; paper describes single-V100 experiments",
            "local_run_requested": run_neural,
            "official_command_templates": [
                "python main.py --multirun +sweep=subgraph_classification/full_shot/BP",
                "python main.py --multirun +sweep=subgraph_classification/full_shot/DS",
            ],
        },
        "runtime_environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": torch_runtime,
            "package_matrix": package_matrix,
        },
        "faithful_neural_execution_preconditions_met": executable,
        "blocked_reason_codes": sorted(set(blockers)),
        "claim_scope": "reference_parity_contract_only_until_faithful_neural_execution_and_split_gate_pass",
    }


def _build_cohort_reconciliation(
    *,
    data: pd.DataFrame | None,
    core_audit: dict[str, Any],
    modern: dict[str, Any],
) -> dict[str, Any]:
    official_rows = int(core_audit.get("subgraph_count") or 0)
    official_positives = int(dict(core_audit.get("label_counts", {})).get("suspicious") or 0)
    if data is not None:
        revtrack_rows = int(len(data))
        revtrack_positives = int(data["labels"].sum())
        columns = list(data.columns)
        subg_examples = [str(value) for value in data["subg"].head(5).tolist()] if "subg" in data.columns else []
    else:
        partition = dict(modern.get("partition_summary", {}) or {})
        split_rows = dict(partition.get("split_rows", {}) or {})
        revtrack_rows = int(partition.get("row_count") or 0)
        revtrack_positives = sum(int(dict(row).get("positive_count") or 0) for row in split_rows.values())
        columns = []
        subg_examples = []
    row_gap = official_rows - revtrack_rows if official_rows and revtrack_rows else None
    positive_gap = official_positives - revtrack_positives if official_positives and revtrack_positives else None
    core_id_columns = [name for name in ["ccId", "component_id", "connected_component_id"] if name in columns]
    subg_is_direct_core_id = False
    blockers: list[str] = []
    if not official_rows:
        blockers.append("official_core_audit_missing")
    if not revtrack_rows:
        blockers.append("revtrack_evaluable_table_missing")
    if row_gap not in (0, None):
        blockers.append("revtrack_evaluable_cohort_smaller_than_current_official_core")
    if positive_gap not in (0, None):
        blockers.append("revtrack_positive_count_differs_from_current_official_core")
    if not core_id_columns and columns:
        blockers.append("revtrack_table_does_not_expose_official_component_ids")
    if not subg_is_direct_core_id:
        blockers.append("full_core_row_mapping_not_proven")
    narrowed = bool(revtrack_rows) and not not columns
    return {
        "schema_version": ELLIPTIC2_REFERENCE_PARITY_SCHEMA_VERSION,
        "slice": "Paper Track P8-C",
        "status": "narrowed_to_revtrack_evaluable_cohort" if narrowed else "blocked",
        "official_core_subgraph_count": official_rows or None,
        "official_core_positive_count": official_positives or None,
        "revtrack_evaluable_row_count": revtrack_rows or None,
        "revtrack_evaluable_positive_count": revtrack_positives or None,
        "row_gap_current_core_minus_revtrack": row_gap,
        "positive_gap_current_core_minus_revtrack": positive_gap,
        "row_coverage_fraction": _ratio(revtrack_rows, official_rows),
        "positive_coverage_fraction": _ratio(revtrack_positives, official_positives),
        "revtrack_table_columns": columns,
        "revtrack_subg_examples": subg_examples,
        "direct_official_component_id_columns": core_id_columns,
        "full_core_equivalence_proven": False,
        "claims_permanently_narrowed_to_revtrack_evaluable_cohort": narrowed,
        "blocked_reason_codes": sorted(set(blockers)),
        "finding": (
            "The pinned RevTrack table is evaluable and stable, but it is smaller than the audited current official core and does not expose original component IDs; claims must be narrowed to the RevTrack-evaluable cohort unless a future mapping proof is added."
            if narrowed
            else "The RevTrack-evaluable cohort could not be loaded, so no modern-subgraph cohort claim is allowed."
        ),
    }


def _build_entity_disjoint_split_report(
    *,
    data: pd.DataFrame | None,
    modern: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "schema_version": ELLIPTIC2_REFERENCE_PARITY_SCHEMA_VERSION,
        "slice": "Paper Track P8-C",
        "split_contract_id": "p8c_component_grouped_entity_disjoint_v1",
        "claim_scope": "strict_entity_disjoint_feasibility_audit_not_a_performance_row",
    }
    if data is None or modern.get("status") != "ready_for_context_pilot":
        return {
            **base,
            "status": "blocked",
            "blocked_reason_codes": ["revtrack_evaluable_table_missing_or_not_verified"],
            "strict_entity_disjoint_split_viable": False,
        }
    boundary_components = _identity_component_summary(data, ELLIPTIC2_BOUNDARY_ENTITY_COLUMNS)
    all_role_components = _identity_component_summary(data, ELLIPTIC2_ENTITY_COLUMNS)
    assignments = _assign_component_splits(data, all_role_components["row_to_component"])
    masks = _split_masks(assignments)
    split_summary = _mask_summary(data, masks)
    overlap = _entity_overlap_report(data=data, masks=masks, columns=ELLIPTIC2_ENTITY_COLUMNS)
    min_eval_positives = 1 if len(data) < 1000 else 50
    train_fraction = split_summary["train"]["row_fraction"]
    checks = {
        "component_grouping_entity_overlap_is_zero": all(
            value["overlap_entity_count"] == 0 for value in overlap.values()
        ),
        "largest_component_fits_train_budget": all_role_components["largest_component_row_fraction"] <= 0.8,
        "validation_positive_minimum_met": split_summary["validation"]["positive_count"] >= min_eval_positives,
        "test_positive_minimum_met": split_summary["test"]["positive_count"] >= min_eval_positives,
        "train_fraction_reasonable": 0.7 <= train_fraction <= 0.9,
    }
    viable = all(checks.values())
    blockers = [key for key, passed in checks.items() if not passed]
    return {
        **base,
        "status": "pass" if viable else "blocked_degenerate_component_structure",
        "identity_columns": ELLIPTIC2_ENTITY_COLUMNS,
        "boundary_entity_columns": ELLIPTIC2_BOUNDARY_ENTITY_COLUMNS,
        "strict_component_protocol": {
            "boundary_entity_components": _public_component_summary(boundary_components),
            "all_role_entity_components": _public_component_summary(all_role_components),
        },
        "candidate_component_grouped_split": {
            "assignment_rule": "deterministic largest-components-first greedy allocation after grouping rows by shared entity identity; no row can cross splits if it shares a grouped entity",
            "row_summary": split_summary,
            "train_to_eval_entity_overlap": overlap,
            "minimum_eval_positive_count": min_eval_positives,
        },
        "strict_entity_disjoint_split_viable": viable,
        "protocol_checks": checks,
        "blocked_reason_codes": blockers,
        "finding": (
            "A strict component-grouped split is feasible on this cohort."
            if viable
            else "Strict entity-disjoint splitting is not meaningful on the pinned RevTrack-evaluable table because nearly all rows collapse into one shared-identity component; any component-grouped holdout would have too little evaluation support."
        ),
    }


def _build_neural_candidate_scorecard(
    *,
    contract: dict[str, Any],
    p8b_gate: dict[str, Any],
    p8b_repeated: dict[str, Any],
    run_neural: bool,
) -> dict[str, Any]:
    baseline_official = dict(p8b_repeated.get("official_partition", {}) or {})
    baseline_robust = dict(p8b_repeated.get("robustness_partition", {}) or {})
    candidate_rows = []
    for candidate in ELLIPTIC2_REFERENCE_CANDIDATES:
        candidate_rows.append(
            {
                **candidate,
                "local_execution_status": "blocked",
                "local_repeated_seed_pr_auc_mean": None,
                "local_repeated_seed_pr_auc_std": None,
                "blocked_reason_codes": contract["blocked_reason_codes"],
            }
        )
    return {
        "schema_version": ELLIPTIC2_REFERENCE_PARITY_SCHEMA_VERSION,
        "slice": "Paper Track P8-C",
        "status": (
            "not_run_ready_for_faithful_environment"
            if contract.get("faithful_neural_execution_preconditions_met") and not run_neural
            else "blocked_resource_or_protocol_gap"
        ),
        "run_neural_requested": run_neural,
        "metric": "pr_auc",
        "selection_policy": "no P8-C candidate is selected from the already exposed official test partition",
        "reference_candidates": candidate_rows,
        "best_local_neural_official_test_pr_auc_mean": None,
        "published_revclassify_ds_pr_auc": competitive.ELLIPTIC2_PUBLISHED_REFERENCE["RevClassify_DS"]["pr_auc"],
        "p8b_supporting_context_baseline": {
            "candidate_family": "LightGBM over official RevTrack embeddings",
            "supporting_paper_row_allowed": p8b_gate.get("supporting_paper_row_allowed"),
            "official_test_pr_auc_mean": baseline_official.get("test_pr_auc_mean"),
            "official_test_pr_auc_std": baseline_official.get("test_pr_auc_std"),
            "hash_split_test_pr_auc_mean": baseline_robust.get("test_pr_auc_mean"),
            "reference_gap": p8b_gate.get("official_gap_to_published_revclassify_ds"),
            "claim_scope": "supporting_modern_context_baseline_only",
        },
        "blocked_reason_codes": sorted(set(contract["blocked_reason_codes"])),
        "finding": "Faithful RevClassifyBP/DS parity was not executed locally; P8-B remains the only numeric modern-context evidence and stays supporting-only.",
    }


def _build_reference_parity_gate(
    *,
    contract: dict[str, Any],
    cohort: dict[str, Any],
    split: dict[str, Any],
    neural: dict[str, Any],
    p8b_gate: dict[str, Any],
) -> dict[str, Any]:
    reference_pr = competitive.ELLIPTIC2_PUBLISHED_REFERENCE["RevClassify_DS"]["pr_auc"]
    neural_pr = neural.get("best_local_neural_official_test_pr_auc_mean")
    checks = {
        "p8b_supporting_context_evidence_available": bool(p8b_gate.get("supporting_paper_row_allowed")),
        "faithful_revclassify_execution_preconditions_met": bool(
            contract.get("faithful_neural_execution_preconditions_met")
        ),
        "neural_repeated_seed_scorecard_available": neural_pr is not None,
        "neural_reference_parity_met": neural_pr is not None
        and float(neural_pr) >= float(reference_pr) - ELLIPTIC2_REFERENCE_PARITY_MARGIN,
        "full_core_equivalence_proven": bool(cohort.get("full_core_equivalence_proven")),
        "claims_narrowed_to_revtrack_evaluable_cohort_recorded": bool(
            cohort.get("claims_permanently_narrowed_to_revtrack_evaluable_cohort")
        ),
        "strict_entity_disjoint_split_viable": bool(split.get("strict_entity_disjoint_split_viable")),
        "official_test_not_used_for_p8c_selection": neural.get("selection_policy")
        == "no P8-C candidate is selected from the already exposed official test partition",
    }
    reference_parity = all(
        checks[key]
        for key in [
            "faithful_revclassify_execution_preconditions_met",
            "neural_repeated_seed_scorecard_available",
            "neural_reference_parity_met",
            "strict_entity_disjoint_split_viable",
            "official_test_not_used_for_p8c_selection",
        ]
    ) and (checks["full_core_equivalence_proven"] or checks["claims_narrowed_to_revtrack_evaluable_cohort_recorded"])
    blockers = [key for key, value in checks.items() if not value]
    blockers.extend(contract.get("blocked_reason_codes", []))
    blockers.extend(cohort.get("blocked_reason_codes", []))
    blockers.extend(split.get("blocked_reason_codes", []))
    return {
        "schema_version": ELLIPTIC2_REFERENCE_PARITY_SCHEMA_VERSION,
        "slice": "Paper Track P8-C",
        "status": "pass_reference_parity" if reference_parity else "blocked_supporting_only_thesis_narrowing_required",
        "protocol_checks": checks,
        "supporting_modern_context_row_allowed": bool(p8b_gate.get("supporting_paper_row_allowed")),
        "reference_parity_claim_allowed": reference_parity,
        "headline_or_sota_claim_allowed": False,
        "end_to_end_relaytic_superiority_claim_allowed": False,
        "full_core_modern_subgraph_claim_allowed": bool(reference_parity and checks["full_core_equivalence_proven"]),
        "hard_aml_claim_allowed": False,
        "p9_allowed": False,
        "published_reference_pr_auc": reference_pr,
        "best_local_neural_pr_auc_mean": neural_pr,
        "blocked_reason_codes": sorted(set(blockers)),
        "allowed_wording": (
            "Relaytic has faithful repeated-seed RevClassify parity evidence on a leakage-resistant cohort protocol."
            if reference_parity
            else "Relaytic may report P8-B as stable supporting modern-context evidence on the pinned RevTrack-evaluable cohort, but P8-C blocks reference-parity, SOTA, full-core, entity-disjoint, and end-to-end superiority claims."
        ),
        "paper_strategy_decision": "narrow_or_reprovision_before_p9",
        "next_slice": "Paper Track P8-D - paper thesis narrowing and alternative evidence decision",
        "summary": "P8-C converts modern-subgraph ambition into an auditable gate: faithful neural parity, cohort reconciliation, and leakage-resistant split proof must pass before broad claims are allowed.",
    }


def _load_core_audit(*, root: Path, core_data_dir: str | Path | None) -> dict[str, Any]:
    if core_data_dir is not None:
        core_dir = _resolve_dir(root, core_data_dir, recovery.DEFAULT_ELLIPTIC2_CORE_DIR)
        return recovery._build_schema_overlap_audit(root=root, core_dir=core_dir)  # noqa: SLF001
    existing = _read_json(root / "docs" / "reports" / "elliptic2_schema_overlap_audit.json")
    if existing:
        return existing
    return recovery._build_schema_overlap_audit(  # noqa: SLF001
        root=root,
        core_dir=root / recovery.DEFAULT_ELLIPTIC2_CORE_DIR,
    )


def _load_revtrack_data(revtrack_dir: Path, modern: dict[str, Any]) -> pd.DataFrame | None:
    if modern.get("status") != "ready_for_context_pilot":
        return None
    try:
        data = pd.read_pickle(revtrack_dir / recovery.REVTRACK_RAW_RELATIVE_DIR / "data_df.pkl")
    except (OSError, ValueError, ImportError):
        return None
    return data if isinstance(data, pd.DataFrame) else None


def _identity_component_summary(data: pd.DataFrame, columns: list[str]) -> dict[str, Any]:
    parent = list(range(len(data)))
    size = [1] * len(data)

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root == right_root:
            return
        if size[left_root] < size[right_root]:
            left_root, right_root = right_root, left_root
        parent[right_root] = left_root
        size[left_root] += size[right_root]

    first_seen: dict[tuple[str, int], int] = {}
    for row_index, row in enumerate(data.itertuples(index=False)):
        for key in _row_identity_keys(row, columns):
            previous = first_seen.get(key)
            if previous is None:
                first_seen[key] = row_index
            else:
                union(row_index, previous)
    roots = [find(index) for index in range(len(data))]
    row_counts = Counter(roots)
    labels = data["labels"].to_numpy(dtype=np.int64)
    positive_counts: dict[int, int] = defaultdict(int)
    for index, root in enumerate(roots):
        positive_counts[root] += int(labels[index])
    components = [
        {
            "component_id": sha256(f"{root}:{row_counts[root]}".encode("utf-8")).hexdigest()[:12],
            "root": root,
            "row_count": int(row_counts[root]),
            "positive_count": int(positive_counts[root]),
        }
        for root in row_counts
    ]
    components.sort(key=lambda row: (-row["row_count"], -row["positive_count"], row["root"]))
    row_to_component = {index: roots[index] for index in range(len(roots))}
    largest = components[0] if components else {"row_count": 0, "positive_count": 0}
    return {
        "identity_columns": columns,
        "row_count": int(len(data)),
        "positive_count": int(labels.sum()),
        "component_count": len(components),
        "largest_component_row_count": int(largest["row_count"]),
        "largest_component_positive_count": int(largest["positive_count"]),
        "largest_component_row_fraction": _ratio(int(largest["row_count"]), len(data)),
        "singleton_component_count": sum(1 for row in components if row["row_count"] == 1),
        "positive_component_count": sum(1 for row in components if row["positive_count"] > 0),
        "top_components": [
            {
                key: value
                for key, value in row.items()
                if key in {"component_id", "row_count", "positive_count"}
            }
            for row in components[:10]
        ],
        "components": components,
        "row_to_component": row_to_component,
    }


def _row_identity_keys(row: Any, columns: list[str]) -> list[tuple[str, int]]:
    keys: list[tuple[str, int]] = []
    for column in columns:
        values = getattr(row, column)
        namespace = "account" if column in {"senders", "receivers", "node_ids"} else "transfer"
        for value in values:
            keys.append((namespace, int(value)))
    return keys


def _public_component_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in summary.items()
        if key not in {"components", "row_to_component"}
    }


def _assign_component_splits(data: pd.DataFrame, row_to_component: dict[int, int]) -> np.ndarray:
    labels = data["labels"].to_numpy(dtype=np.int64)
    component_rows: dict[int, list[int]] = defaultdict(list)
    for index, component in row_to_component.items():
        component_rows[component].append(index)
    components = [
        {
            "component": component,
            "rows": rows,
            "row_count": len(rows),
            "positive_count": int(labels[rows].sum()),
        }
        for component, rows in component_rows.items()
    ]
    components.sort(key=lambda row: (-row["row_count"], -row["positive_count"], row["component"]))
    total_rows = len(data)
    targets = {"TRN": total_rows * 0.8, "VAL": total_rows * 0.1, "TST": total_rows * 0.1}
    split_rows = {"TRN": 0, "VAL": 0, "TST": 0}
    assignments = np.empty(total_rows, dtype=object)
    for component in components:
        if component["row_count"] > targets["TRN"]:
            split = "TRN"
        else:
            split = min(split_rows, key=lambda name: split_rows[name] / max(targets[name], 1.0))
        for index in component["rows"]:
            assignments[index] = split
        split_rows[split] += component["row_count"]
    return assignments


def _entity_overlap_report(*, data: pd.DataFrame, masks: dict[str, np.ndarray], columns: list[str]) -> dict[str, Any]:
    split_entities: dict[str, set[tuple[str, int]]] = {}
    for split, mask in masks.items():
        entities: set[tuple[str, int]] = set()
        for row in data.loc[mask].itertuples(index=False):
            entities.update(_row_identity_keys(row, columns))
        split_entities[split] = entities
    train_entities = split_entities["train"]
    output: dict[str, Any] = {}
    for split in ["validation", "test"]:
        entities = split_entities[split]
        overlap = train_entities & entities
        output[f"train_to_{split}"] = {
            "evaluation_entity_count": len(entities),
            "overlap_entity_count": len(overlap),
            "overlap_fraction": _ratio(len(overlap), len(entities)),
        }
    return output


def _mask_summary(data: pd.DataFrame, masks: dict[str, np.ndarray]) -> dict[str, Any]:
    y = data["labels"].to_numpy(dtype=np.int64)
    total = int(len(data))
    name_map = {"train": "TRN", "validation": "VAL", "test": "TST"}
    return {
        split: {
            "row_count": int(mask.sum()),
            "row_fraction": _ratio(int(mask.sum()), total),
            "positive_count": int(y[mask].sum()),
            "positive_rate": round(float(y[mask].mean()), 8) if mask.any() else None,
            "official_split_labels_present": dict(
                sorted(data.loc[mask, "split"].value_counts().to_dict().items())
            ) if "split" in data.columns and mask.any() else {},
            "component_split_label": name_map[split],
        }
        for split, mask in masks.items()
    }


def _split_masks(assignments: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "train": assignments == "TRN",
        "validation": assignments == "VAL",
        "test": assignments == "TST",
    }


def _package_state(package_id: str, *, module_name: str | None = None) -> dict[str, Any]:
    module = module_name or package_id.replace("-", "_")
    available = importlib.util.find_spec(module) is not None
    return {
        "package_id": package_id,
        "module": module,
        "available": available,
        "version": _package_version(package_id) if available else None,
    }


def _torch_runtime() -> dict[str, Any]:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - defensive for broken local installs
        return {"available": False, "import_error": f"{type(exc).__name__}: {exc}"}
    cuda_available = bool(torch.cuda.is_available())
    return {
        "available": True,
        "version": getattr(torch, "__version__", None),
        "cuda_available": cuda_available,
        "cuda_device_count": int(torch.cuda.device_count()) if cuda_available else 0,
        "mps_available": bool(getattr(getattr(torch.backends, "mps", None), "is_available", lambda: False)()),
    }


def _file_check(root: Path, path: Path) -> dict[str, Any]:
    return {
        "path": _display_path(root, path),
        "exists": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else None,
    }


def _package_version(package_name: str) -> str | None:
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        return None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _resolve_dir(root: Path, supplied: str | Path | None, default: Path) -> Path:
    value = Path(supplied) if supplied is not None else root / default
    return value if value.is_absolute() else root / value


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        parts = list(path.resolve().parts)
        for anchor in ["official_repo", "elliptic2_revtrack", "elliptic2"]:
            if anchor in parts:
                return "<external-local-source>/" + "/".join(parts[parts.index(anchor) :])
        return f"<external-local-source>/{path.name}"


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(float(numerator / denominator), 8) if denominator else None

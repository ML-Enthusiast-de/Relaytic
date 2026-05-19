"""Paper/release freeze artifacts for Relaytic-AML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_FREEZE_SCHEMA_VERSION = "relaytic.paper_release_freeze.v1"
PAPER_FREEZE_REPORT_DIR = Path("docs") / "reports"
PAPER_FREEZE_FILENAMES = {
    "paper_release_freeze_manifest": "paper_release_freeze_manifest.json",
    "aml_relevant_benchmark_catalog": "aml_relevant_benchmark_catalog.json",
    "paper_benchmark_runbook": "paper_benchmark_runbook.md",
    "paper_result_table": "paper_result_table.json",
    "paper_claim_boundary_report": "paper_claim_boundary_report.json",
    "reproducibility_attestation": "reproducibility_attestation.json",
    "release_attention_pack_manifest": "release_attention_pack_manifest.json",
}

TRACK_LABELS = {"dev", "holdout", "paper", "proxy", "blocked"}
CLAIM_BOUNDARIES = {"hard", "supporting-only", "blocked"}


def build_paper_freeze_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, dict[str, Any] | str]:
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_FREEZE_REPORT_DIR
    catalog = _build_relevant_benchmark_catalog()
    result_table = _build_paper_result_table(catalog)
    claim_boundary_report = _build_claim_boundary_report()
    reproducibility_attestation = _build_reproducibility_attestation(catalog)
    attention_pack = _build_release_attention_pack_manifest(claim_boundary_report, catalog)
    manifest = _build_paper_release_freeze_manifest(
        catalog=catalog,
        result_table=result_table,
        claim_boundary_report=claim_boundary_report,
        reproducibility_attestation=reproducibility_attestation,
        attention_pack=attention_pack,
        report_dir=report_dir,
        project_root=root,
    )
    pack: dict[str, dict[str, Any] | str] = {
        "paper_release_freeze_manifest": manifest,
        "aml_relevant_benchmark_catalog": catalog,
        "paper_result_table": result_table,
        "paper_claim_boundary_report": claim_boundary_report,
        "reproducibility_attestation": reproducibility_attestation,
        "release_attention_pack_manifest": attention_pack,
    }
    pack["paper_benchmark_runbook"] = render_paper_freeze_runbook(pack)
    return pack


def sync_paper_freeze_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_FREEZE_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_freeze_pack(root, output_dir=report_dir)
    written: dict[str, Path] = {}
    for key, filename in PAPER_FREEZE_FILENAMES.items():
        path = report_dir / filename
        payload = pack[key]
        if key == "paper_benchmark_runbook":
            path.write_text(str(payload), encoding="utf-8")
        else:
            write_json(path, payload, indent=2, sort_keys=True)
        written[key] = path
    return written


def render_paper_freeze_markdown(pack: dict[str, dict[str, Any] | str]) -> str:
    manifest = dict(pack.get("paper_release_freeze_manifest", {}))
    catalog = dict(pack.get("aml_relevant_benchmark_catalog", {}))
    attention = dict(pack.get("release_attention_pack_manifest", {}))
    tracks = list(catalog.get("tracks", [])) if isinstance(catalog.get("tracks"), list) else []
    track_lines = [
        f"- {item.get('track_id')}: `{item.get('label')}` ({item.get('track_type')})"
        for item in tracks
        if isinstance(item, dict)
    ]
    return "\n".join(
        [
            "# Relaytic-AML Paper Release Freeze",
            "",
            f"Status: `{manifest.get('status', 'unknown')}`",
            f"Hard performance claims allowed: `{manifest.get('hard_performance_claims_allowed', False)}`",
            "",
            "## Benchmark Tracks",
            *track_lines,
            "",
            "## Safe Attention Angle",
            str(attention.get("primary_attention_angle", "")),
            "",
            "Regenerate with:",
            "",
            "```powershell",
            "relaytic release-safety paper-freeze --format json",
            "```",
        ]
    ).strip() + "\n"


def render_paper_freeze_runbook(pack: dict[str, dict[str, Any] | str]) -> str:
    catalog = dict(pack["aml_relevant_benchmark_catalog"])
    attestation = dict(pack["reproducibility_attestation"])
    tracks = [dict(item) for item in catalog.get("tracks", []) if isinstance(item, dict)]
    commands = [dict(item) for item in attestation.get("commands", []) if isinstance(item, dict)]
    lines = [
        "# Relaytic-AML Paper Freeze Runbook",
        "",
        "This generated runbook is the Slice 15Z-R machine-aligned release-freeze runbook.",
        "It records the relevant benchmark families, the allowed claim posture, and the commands reviewers should use before treating a result as public evidence.",
        "",
        "## Track Status",
        "",
        "| Track | Type | Label | Hard claim | Current evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for track in tracks:
        lines.append(
            "| {track_id} | {track_type} | `{label}` | `{hard}` | {evidence} |".format(
                track_id=track["track_id"],
                track_type=track["track_type"],
                label=track["label"],
                hard=track["hard_claim_allowed"],
                evidence=track["evidence_state"],
            )
        )
    lines.extend(
        [
            "",
            "## Reproducibility Commands",
            "",
        ]
    )
    for item in commands:
        lines.extend(
            [
                f"### {item['command_id']}",
                "",
                "```powershell",
                str(item["command"]),
                "```",
                "",
                str(item["purpose"]),
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Rule",
            "",
            "Hard AML performance or SOTA claims remain blocked unless the catalog row is labeled `paper`, the result table has numeric holdout metrics, the environment scorecard passes, and release-safety is clean.",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _build_relevant_benchmark_catalog() -> dict[str, Any]:
    tracks = [
        {
            "track_id": "paysim_temporal_transaction_fraud",
            "track_type": "transaction_fraud_temporal",
            "label": "proxy",
            "dataset_source_posture": "public_synthetic_schema_or_local_equivalent",
            "benchmark_relevance": "high_for_transaction_monitoring_shape",
            "evidence_state": "dev_fixture_and_cli_path_supported",
            "hard_claim_allowed": False,
            "hard_claim_blocked_reason": "PaySim-style evidence is synthetic/proxy until a frozen holdout partition and release gate pass.",
            "commands": [
                "relaytic run --run-dir artifacts/aml_benchmark_run --data-path <paysim_like.csv> --timestamp-column step --format json",
                "relaytic benchmark run --run-dir artifacts/aml_benchmark_run --data-path <paysim_like.csv> --format json",
                "relaytic aml temporal --run-dir artifacts/aml_benchmark_run --format json",
                "relaytic aml environment --run-dir artifacts/aml_benchmark_run --format json",
            ],
            "required_artifacts": [
                "aml_benchmark_manifest.json",
                "aml_temporal_benchmark_claim_report.json",
                "aml_time_window_scorecard.json",
                "aml_environment_scorecard.json",
            ],
        },
        {
            "track_id": "elliptic_flattened_graph_aml",
            "track_type": "graph_aml",
            "label": "proxy",
            "dataset_source_posture": "flattened_public_graph_snapshot_or_local_equivalent",
            "benchmark_relevance": "high_for_temporal_graph_aml_shape",
            "evidence_state": "flattened_graph_and_graph_loader_paths_supported",
            "hard_claim_allowed": False,
            "hard_claim_blocked_reason": "Flattened graph evidence is proxy until raw graph provenance, holdout posture, and claim scope pass together.",
            "commands": [
                "relaytic run --run-dir artifacts/aml_graph_benchmark_run --data-path <elliptic_flattened.csv> --timestamp-column time_step --format json",
                "relaytic aml graph-loader --run-dir artifacts/aml_graph_benchmark_run --graph-path <graph_bundle_or_subgraph_pack> --format json",
                "relaytic aml baselines --run-dir artifacts/aml_graph_benchmark_run --format json",
                "relaytic aml environment --run-dir artifacts/aml_graph_benchmark_run --format json",
            ],
            "required_artifacts": [
                "aml_graph_loader_manifest.json",
                "aml_graph_provenance_report.json",
                "aml_graph_claim_scope.json",
                "aml_benchmark_relevance_scorecard.json",
            ],
        },
        {
            "track_id": "elliptic2_subgraph_aml",
            "track_type": "subgraph_aml",
            "label": "blocked",
            "dataset_source_posture": "not_yet_frozen_for_local_release_profile",
            "benchmark_relevance": "high_but_not_currently_claimable",
            "evidence_state": "blocked_until_loader_data_access_and_claim_scope_are_reproducible",
            "hard_claim_allowed": False,
            "hard_claim_blocked_reason": "Subgraph-centric paper claims need explicit data access posture, loader support, and rerunnable holdout evidence.",
            "commands": [
                "relaytic aml graph-loader --run-dir artifacts/aml_subgraph_benchmark_run --graph-path <subgraph_pack> --format json"
            ],
            "required_artifacts": [
                "aml_subgraph_task_manifest.json",
                "aml_public_graph_benchmark_catalog.json",
                "aml_environment_failure_report.json",
            ],
        },
        {
            "track_id": "amlsim_synthetic_bank_graph",
            "track_type": "synthetic_bank_graph_aml",
            "label": "blocked",
            "dataset_source_posture": "generator_not_yet_frozen_in_release_profile",
            "benchmark_relevance": "medium_to_high_for_typology_and_queue_workflow",
            "evidence_state": "blocked_until_reproducible_generation_and_source_manifest_exist",
            "hard_claim_allowed": False,
            "hard_claim_blocked_reason": "Synthetic-bank graph evidence needs a frozen generator command and typology manifest before it can support even proxy benchmark claims.",
            "commands": [
                "relaytic aml graph-loader --run-dir artifacts/amlsim_benchmark_run --graph-path <generated_amlsim_bundle> --format json"
            ],
            "required_artifacts": [
                "aml_public_graph_benchmark_catalog.json",
                "entity_graph_profile.json",
                "subgraph_risk_report.json",
                "case_packet.json",
            ],
        },
        {
            "track_id": "generic_structured_supporting_pack",
            "track_type": "generic_supporting_structured_data",
            "label": "dev",
            "dataset_source_posture": "bundled_or_public_structured_data_fixture",
            "benchmark_relevance": "supporting_only_for_general_structured_data_competence",
            "evidence_state": "supported_as_non_flagship_breadth_evidence",
            "hard_claim_allowed": False,
            "hard_claim_blocked_reason": "Generic structured-data wins cannot substitute for AML-specific temporal, graph, and operational evidence.",
            "commands": [
                "relaytic benchmark run --run-dir artifacts/generic_supporting_benchmark --data-path <structured_dataset.csv> --format json"
            ],
            "required_artifacts": [
                "paper_benchmark_manifest.json",
                "paper_benchmark_table.json",
                "benchmark_release_gate.json",
            ],
        },
    ]
    return {
        "schema_version": PAPER_FREEZE_SCHEMA_VERSION,
        "slice": "15Z-R",
        "status": "frozen_with_blocked_hard_performance_claims",
        "allowed_labels": sorted(TRACK_LABELS),
        "track_count": len(tracks),
        "tracks": tracks,
    }


def _build_paper_result_table(catalog: dict[str, Any]) -> dict[str, Any]:
    rows = []
    claim_refs = {
        "paysim_temporal_transaction_fraud": "claim_paysim_temporal_transaction_fraud",
        "elliptic_flattened_graph_aml": "claim_elliptic_flattened_graph_aml",
        "elliptic2_subgraph_aml": "claim_subgraph_or_synthetic_bank_graph",
        "amlsim_synthetic_bank_graph": "claim_subgraph_or_synthetic_bank_graph",
        "generic_structured_supporting_pack": "claim_generic_structured_supporting_pack",
    }
    for track in catalog["tracks"]:
        label = str(track["label"])
        public_claim_status = "blocked" if label == "blocked" else "supporting-only"
        rows.append(
            {
                "track_id": track["track_id"],
                "track_type": track["track_type"],
                "track_label": label,
                "result_state": "blocked_rerun_reason_recorded" if label == "blocked" else "numeric_holdout_rerun_required",
                "model_metrics": {
                    "primary_metric": "pr_auc" if "aml" in str(track["track_type"]) or "fraud" in str(track["track_type"]) else "task_metric",
                    "pr_auc": None,
                    "precision_at_k": None,
                    "recall_at_review_budget": None,
                    "source_artifact": "benchmark_release_gate.json",
                    "metric_state": "not_frozen_as_numeric_public_result",
                },
                "operational_metrics": {
                    "review_capacity_metric": None,
                    "analyst_hour_savings": None,
                    "false_positive_reduction": None,
                    "source_artifacts": [
                        "review_capacity_metric_report.json",
                        "aml_business_value_report.json",
                        "operational_metric_guard.json",
                    ],
                    "metric_state": "required_for_hard_claim",
                },
                "ablation_posture": {
                    "source_artifact": "aml_ablation_matrix.json",
                    "status": "required_for_aml_claim" if label != "blocked" else "blocked_until_track_available",
                },
                "environment_score": {
                    "source_artifact": "aml_environment_scorecard.json",
                    "value": None,
                    "status": "required_pass_for_public_claim",
                },
                "public_claim_status": public_claim_status,
                "claim_boundary_ref": f"paper_claim_boundary_report.json#{claim_refs[str(track['track_id'])]}",
            }
        )
    return {
        "schema_version": PAPER_FREEZE_SCHEMA_VERSION,
        "slice": "15Z-R",
        "status": "no_hard_numeric_performance_claims_frozen",
        "metric_columns_required_for_hard_claim": [
            "model_metrics",
            "operational_metrics",
            "ablation_posture",
            "environment_score",
            "public_claim_status",
        ],
        "rows": rows,
    }


def _build_claim_boundary_report() -> dict[str, Any]:
    claims = [
        {
            "claim_id": "claim_release_freeze_pack_exists",
            "claim_text": "Relaytic-AML emits a reproducible local paper/release freeze pack with explicit claim gates.",
            "boundary": "hard",
            "artifact_paths": [
                "docs/reports/paper_release_freeze_manifest.json",
                "docs/reports/reproducibility_attestation.json",
                "docs/reports/release_attention_pack_manifest.json",
            ],
            "allowed_public_wording": "Relaytic-AML includes a local release-freeze pack that records benchmark relevance, reproducibility posture, and blocked claims.",
            "rationale": "This is a product-surface claim about artifacts generated by the repository, not a model-performance claim.",
        },
        {
            "claim_id": "claim_paysim_temporal_transaction_fraud",
            "claim_text": "Relaytic-AML can run a PaySim-style temporal transaction-fraud workflow and emit AML temporal/environment gates.",
            "boundary": "supporting-only",
            "artifact_paths": [
                "docs/reports/aml_relevant_benchmark_catalog.json",
                "tests/test_cli_aml_realworld.py",
                "aml_temporal_benchmark_claim_report.json",
                "aml_environment_scorecard.json",
            ],
            "allowed_public_wording": "PaySim-style evidence is a relevant proxy/dev workflow, not a hard real-world AML superiority result.",
            "rationale": "The workflow shape is covered, but synthetic/proxy source posture blocks hard claims.",
        },
        {
            "claim_id": "claim_elliptic_flattened_graph_aml",
            "claim_text": "Relaytic-AML can run flattened Elliptic-style graph AML evidence and expose graph claim-scope artifacts.",
            "boundary": "supporting-only",
            "artifact_paths": [
                "docs/reports/aml_relevant_benchmark_catalog.json",
                "tests/test_cli_aml_realworld.py",
                "aml_graph_loader_manifest.json",
                "aml_graph_claim_scope.json",
            ],
            "allowed_public_wording": "Flattened Elliptic-style evidence is supporting proxy graph AML evidence until raw graph/holdout gates pass.",
            "rationale": "Flattened graph compatibility is useful but not a raw graph paper claim.",
        },
        {
            "claim_id": "claim_sota_or_hard_aml_superiority",
            "claim_text": "Relaytic-AML is a SOTA or hard public AML benchmark winner.",
            "boundary": "blocked",
            "artifact_paths": [
                "docs/reports/paper_result_table.json",
                "docs/reports/aml_relevant_benchmark_catalog.json",
                "docs/reports/reproducibility_attestation.json",
            ],
            "allowed_public_wording": "Hard AML performance claims are blocked until a frozen holdout/paper track reports numeric evidence and all claim gates pass.",
            "rationale": "The current freeze pack records the absence of hard numeric holdout evidence rather than manufacturing a leaderboard claim.",
        },
        {
            "claim_id": "claim_generic_structured_supporting_pack",
            "claim_text": "Relaytic has generic structured-data benchmark evidence that can support the AML story as breadth context.",
            "boundary": "supporting-only",
            "artifact_paths": [
                "docs/reports/aml_relevant_benchmark_catalog.json",
                "benchmark_release_gate.json",
                "paper_benchmark_table.json",
            ],
            "allowed_public_wording": "Generic structured-data benchmark evidence is supporting breadth context and is not the flagship AML proof.",
            "rationale": "Generic tabular results are useful context but cannot replace AML temporal, graph, and operational evidence.",
        },
        {
            "claim_id": "claim_subgraph_or_synthetic_bank_graph",
            "claim_text": "Relaytic-AML has paper-ready subgraph AML or AMLSim-style synthetic-bank graph evidence.",
            "boundary": "blocked",
            "artifact_paths": [
                "docs/reports/aml_relevant_benchmark_catalog.json",
                "aml_subgraph_task_manifest.json",
                "aml_public_graph_benchmark_catalog.json",
            ],
            "allowed_public_wording": "Subgraph and synthetic-bank graph tracks are cataloged and blocked until data access, loader support, and reproducible generation are frozen.",
            "rationale": "Relevant future tracks are named, but substitution with weaker evidence is explicitly disallowed.",
        },
    ]
    return {
        "schema_version": PAPER_FREEZE_SCHEMA_VERSION,
        "slice": "15Z-R",
        "status": "claim_boundaries_frozen",
        "allowed_boundaries": sorted(CLAIM_BOUNDARIES),
        "claims": claims,
    }


def _build_reproducibility_attestation(catalog: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PAPER_FREEZE_SCHEMA_VERSION,
        "slice": "15Z-R",
        "status": "rerunnable_with_blocked_claim_fallbacks",
        "install_profile": {
            "python_versions": ["3.10", "3.11"],
            "dependency_profile": ".[full]",
            "ci_workflow": ".github/workflows/ci.yml",
            "local_first_required": True,
        },
        "commands": [
            {
                "command_id": "install_full_profile",
                "command": 'python -m pip install -e ".[full]"',
                "purpose": "Install the same full dependency profile used by CI.",
                "output_artifacts": [],
            },
            {
                "command_id": "generate_release_freeze_pack",
                "command": "relaytic release-safety paper-freeze --format json",
                "purpose": "Regenerate the machine-readable paper/release freeze artifacts.",
                "output_artifacts": list(PAPER_FREEZE_FILENAMES.values()),
            },
            {
                "command_id": "run_release_safety_scan",
                "command": "relaytic release-safety scan --format json",
                "purpose": "Verify release-safety posture before public use.",
                "output_artifacts": ["release_safety_scan.json"],
            },
            {
                "command_id": "run_aml_demo_path",
                "command": "relaytic demo aml-review-queue --run-dir artifacts/relaytic_aml_demo --format json",
                "purpose": "Regenerate the public-safe demo path that anchors the product story.",
                "output_artifacts": ["aml_demo_bundle_manifest.json", "aml_investigation_board.json"],
            },
            {
                "command_id": "run_aml_environment_gate",
                "command": "relaytic aml environment --run-dir artifacts/relaytic_aml_demo --format json",
                "purpose": "Regenerate model/environment score separation and benchmark-environment posture.",
                "output_artifacts": ["aml_environment_scorecard.json", "aml_benchmark_environment_scorecard.json"],
            },
        ],
        "dataset_source_posture": [
            {
                "track_id": track["track_id"],
                "label": track["label"],
                "source_posture": track["dataset_source_posture"],
                "hard_claim_allowed": track["hard_claim_allowed"],
            }
            for track in catalog["tracks"]
        ],
        "host_assumptions": {
            "network_required_for_freeze_command": False,
            "tokens_or_api_keys_required": False,
            "cpu_safe_profile": True,
            "optional_adapters_must_not_pollute_json_stdout": True,
        },
        "runtime_budget": {
            "release_freeze_pack": "seconds",
            "targeted_slice_tests": "under_two_minutes",
            "prepush_profile": "can_be_long_when_optional_model_adapters_are_installed",
        },
        "release_safety_scan_state": {
            "required_before_public_use": True,
            "clean_state_required": True,
            "command": "relaytic release-safety scan --format json",
        },
        "rerun_policy": {
            "clean_local_rerun_command": "relaytic release-safety paper-freeze --format json",
            "reproduces_report_table_or_blocks": True,
            "deterministic_blocked_rerun_reasons": [
                "dataset_unavailable_or_license_unclear",
                "loader_not_supported_for_track",
                "holdout_partition_not_frozen",
                "claim_gate_or_environment_gate_failed",
                "release_safety_scan_not_clean",
            ],
        },
    }


def _build_release_attention_pack_manifest(
    claim_boundary_report: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": PAPER_FREEZE_SCHEMA_VERSION,
        "slice": "15Z-R",
        "status": "safe_attention_pack_ready",
        "primary_attention_angle": (
            "Relaytic-AML is a local-first AML investigation system with explicit benchmark relevance, "
            "environment scoring, operational-value gates, and blocked-claim discipline."
        ),
        "safe_public_assets": [
            "README.md",
            "docs/why_relaytic_aml.md",
            "docs/product_story.md",
            "docs/paper_benchmark_runbook.md",
            "docs/reports/paper_release_freeze_manifest.json",
            "docs/reports/paper_claim_boundary_report.json",
            "docs/reports/reproducibility_attestation.json",
        ],
        "allowed_outreach_claims": [
            item["claim_id"]
            for item in claim_boundary_report["claims"]
            if item["boundary"] in {"hard", "supporting-only"}
        ],
        "blocked_outreach_claims": [
            item["claim_id"]
            for item in claim_boundary_report["claims"]
            if item["boundary"] == "blocked"
        ],
        "benchmark_track_count": len(catalog["tracks"]),
        "hard_performance_claims_allowed": False,
    }


def _build_paper_release_freeze_manifest(
    *,
    catalog: dict[str, Any],
    result_table: dict[str, Any],
    claim_boundary_report: dict[str, Any],
    reproducibility_attestation: dict[str, Any],
    attention_pack: dict[str, Any],
    report_dir: Path,
    project_root: Path,
) -> dict[str, Any]:
    tracks = [dict(item) for item in catalog["tracks"]]
    track_types = {str(item["track_type"]) for item in tracks}
    labels = {str(item["label"]) for item in tracks}
    claims = [dict(item) for item in claim_boundary_report["claims"]]
    result_rows = [dict(item) for item in result_table["rows"]]
    required_result_columns = set(result_table["metric_columns_required_for_hard_claim"])
    return {
        "schema_version": PAPER_FREEZE_SCHEMA_VERSION,
        "slice": "15Z-R",
        "status": "frozen_supporting_release_pack",
        "release_posture": "safe_for_attention_without_hard_performance_claims",
        "hard_performance_claims_allowed": False,
        "artifact_paths": {
            key: _artifact_path(report_dir / filename, project_root)
            for key, filename in PAPER_FREEZE_FILENAMES.items()
        },
        "acceptance_status": {
            "relevant_catalog_coverage": {
                "transaction_fraud_temporal": "transaction_fraud_temporal" in track_types,
                "graph_aml": "graph_aml" in track_types,
                "subgraph_or_synthetic_bank_graph": bool(
                    {"subgraph_aml", "synthetic_bank_graph_aml"} & track_types
                ),
                "generic_supporting_structured_data": "generic_supporting_structured_data" in track_types,
                "all_labels_allowed": labels <= TRACK_LABELS,
            },
            "result_table_multidimensional": all(
                required_result_columns <= set(row)
                for row in result_rows
            ),
            "claim_boundaries_complete": all(
                str(item.get("boundary")) in CLAIM_BOUNDARIES and bool(item.get("artifact_paths"))
                for item in claims
            ),
            "reproducibility_attestation_complete": bool(reproducibility_attestation.get("commands"))
            and bool(reproducibility_attestation.get("dataset_source_posture"))
            and bool(reproducibility_attestation.get("runtime_budget")),
            "release_attention_pack_safe": attention_pack.get("hard_performance_claims_allowed") is False,
            "rerun_contract_present": bool(
                dict(reproducibility_attestation.get("rerun_policy", {})).get("reproduces_report_table_or_blocks")
            ),
        },
    }


def _artifact_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()

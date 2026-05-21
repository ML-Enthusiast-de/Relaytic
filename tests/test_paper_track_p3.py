from __future__ import annotations

import json
from pathlib import Path

from relaytic.release_safety import (
    PAPER_DATASET_REGISTRY_FILENAMES,
    build_paper_dataset_registry_pack,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def _by_dataset(items: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(item["dataset_id"]): item for item in items}


def test_paper_track_p3_registry_freezes_core_dataset_posture() -> None:
    generated = build_paper_dataset_registry_pack(PROJECT_ROOT)
    registry = generated["paper_dataset_registry"]
    datasets = _by_dataset(registry["datasets"])

    assert registry["schema_version"] == "relaytic.paper_dataset_registry.v1"
    assert registry["slice"] == "Paper Track P3"
    assert registry["status"] == "dataset_registry_frozen"
    assert registry["next_slice"] == "Paper Track P4"
    assert registry["registry_agrees_with_p2_core_tracks"] is True
    assert registry["hard_performance_claims_allowed"] is False

    assert {
        "paysim_temporal_transaction_fraud",
        "elliptic_bitcoin_flattened_graph_aml",
        "elliptic2_subgraph_aml",
        "amlsim_synthetic_bank_graph",
        "generic_structured_support_pack",
    } <= set(datasets)

    assert datasets["paysim_temporal_transaction_fraud"]["paper_claim_posture"] == "supporting-only"
    assert datasets["elliptic_bitcoin_flattened_graph_aml"]["paper_claim_posture"] == "supporting-only"
    assert datasets["elliptic2_subgraph_aml"]["paper_claim_posture"] == "blocked"
    assert datasets["amlsim_synthetic_bank_graph"]["paper_claim_posture"] == "blocked"
    assert datasets["dgraph_finance_graph_context"]["paper_claim_posture"] == "blocked-context-only"


def test_paper_track_p3_access_manifest_records_license_and_local_readiness() -> None:
    generated = build_paper_dataset_registry_pack(PROJECT_ROOT)
    manifest = generated["paper_dataset_access_manifest"]
    entries = _by_dataset(manifest["access_entries"])

    assert manifest["status"] == "dataset_access_manifest_frozen"
    assert manifest["policy"]["no_secret_storage"] is True
    assert manifest["policy"]["no_auto_download_from_authenticated_sources"] is True
    assert manifest["policy"]["raw_dataset_files_not_committed_by_default"] is True

    assert entries["paysim_temporal_transaction_fraud"]["license"]["spdx_or_name"] == "CC-BY-SA-4.0"
    assert entries["elliptic_bitcoin_flattened_graph_aml"]["license"]["spdx_or_name"] == "CC-BY-NC-ND-4.0"
    assert entries["elliptic2_subgraph_aml"]["license"]["spdx_or_name"] == "CC-BY-NC-ND-4.0"
    assert entries["amlsim_synthetic_bank_graph"]["license"]["spdx_or_name"] == "Apache-2.0 for generator code"
    assert entries["dgraph_finance_graph_context"]["license"]["spdx_or_name"] == "custom_noncommercial"

    assert entries["generic_structured_support_pack"]["local_source_ready"] is True
    assert entries["generic_structured_support_pack"]["manual_action_required"] is False
    generic_checks = entries["generic_structured_support_pack"]["required_file_checks"]
    assert all(check["exists"] and check["sha256"] for check in generic_checks)

    assert entries["paysim_temporal_transaction_fraud"]["local_source_ready"] is False
    assert "paysim_temporal_transaction_fraud" in manifest["manual_action_required_dataset_ids"]
    assert "elliptic2_subgraph_aml" in manifest["kaggle_or_account_gated_dataset_ids"]


def test_paper_track_p3_split_contracts_prevent_leaky_benchmark_rows() -> None:
    generated = build_paper_dataset_registry_pack(PROJECT_ROOT)
    contracts = {
        item["split_contract_id"]: item
        for item in generated["paper_split_contracts"]["contracts"]
    }

    paysim = contracts["split_paysim_chronological_step_v1"]
    assert paysim["split_type"] == "chronological_by_step"
    assert "random_row_shuffle" in paysim["forbidden_split_methods"]
    assert "oldbalanceOrg" in paysim["forbidden_feature_fields"]
    assert "newbalanceOrig" in paysim["forbidden_feature_fields"]

    elliptic = contracts["split_elliptic_temporal_step_v1"]
    assert elliptic["split_type"] == "temporal_graph_by_time_step"
    assert "edge_leaking_future_to_train" in elliptic["forbidden_split_methods"]
    assert "raw_vs_flattened_claim_scope" in elliptic["required_audits"]

    elliptic2 = contracts["split_elliptic2_subgraph_fixed_seed_v1"]
    assert elliptic2["paper_readiness"] == "blocked"
    assert "node_level_split_for_subgraph_task" in elliptic2["forbidden_split_methods"]

    assert generated["paper_split_contracts"]["global_split_doctrine"][
        "each_table_cell_must_record_dataset_split_command_artifact_and_claim_posture"
    ] is True


def test_paper_track_p3_blockers_keep_hard_claims_blocked() -> None:
    generated = build_paper_dataset_registry_pack(PROJECT_ROOT)
    blockers = generated["paper_dataset_blockers"]
    by_dataset = _by_dataset(blockers["dataset_blockers"])

    assert blockers["status"] == "dataset_blockers_frozen"
    assert blockers["hard_performance_claims_allowed"] is False
    assert blockers["next_slice"] == "Paper Track P4"

    assert by_dataset["generic_structured_support_pack"]["blocked"] is False
    assert by_dataset["paysim_temporal_transaction_fraud"]["blocked"] is True
    assert by_dataset["elliptic2_subgraph_aml"]["blocked"] is True
    assert by_dataset["amlsim_synthetic_bank_graph"]["blocked"] is True

    global_ids = {item["blocker_id"] for item in blockers["global_blockers"]}
    assert "no_numeric_holdout_paper_rows_yet" in global_ids
    assert "hard_aml_claims_still_blocked" in global_ids


def test_paper_track_p3_committed_artifacts_match_generated_pack() -> None:
    generated = build_paper_dataset_registry_pack(PROJECT_ROOT)
    for key, filename in PAPER_DATASET_REGISTRY_FILENAMES.items():
        committed = _load_report(filename)
        assert committed == generated[key], filename

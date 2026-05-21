"""Paper dataset registry and access artifacts for Paper Track P3."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_DATASET_REGISTRY_SCHEMA_VERSION = "relaytic.paper_dataset_registry.v1"
PAPER_DATASET_REGISTRY_REPORT_DIR = Path("docs") / "reports"
PAPER_DATASET_REGISTRY_FILENAMES = {
    "paper_dataset_registry": "paper_dataset_registry.json",
    "paper_dataset_access_manifest": "paper_dataset_access_manifest.json",
    "paper_split_contracts": "paper_split_contracts.json",
    "paper_dataset_blockers": "paper_dataset_blockers.json",
}
SOURCE_REVIEW_DATE = "2026-05-21"

CORE_DATASET_IDS = [
    "paysim_temporal_transaction_fraud",
    "elliptic_bitcoin_flattened_graph_aml",
    "elliptic2_subgraph_aml",
    "amlsim_synthetic_bank_graph",
    "generic_structured_support_pack",
]


DATASET_SPECS: list[dict[str, Any]] = [
    {
        "dataset_id": "paysim_temporal_transaction_fraud",
        "track_id": "paysim_temporal_transaction_fraud",
        "display_name": "PaySim synthetic mobile-money transaction fraud",
        "track_group": "core_proxy_temporal",
        "benchmark_role": "proxy temporal transaction-fraud workflow",
        "source_posture": "synthetic_proxy_dataset",
        "access_posture": "manual_kaggle_download_required",
        "paper_claim_posture": "supporting-only",
        "claim_id": "claim_paysim_temporal_transaction_fraud",
        "license": {
            "spdx_or_name": "CC-BY-SA-4.0",
            "commercial_use": "allowed_with_sharealike_constraints",
            "redistribution": "allowed_with_attribution_and_sharealike",
            "requires_legal_review_before_bundling": True,
        },
        "source_urls": {
            "dataset_landing": "https://www.kaggle.com/datasets/ealaxi/paysim1/data",
            "paper_or_record": "https://www.diva-portal.org/smash/record.jsf?pid=diva2:1058442",
        },
        "known_source_facts": {
            "source_type": "mobile-money simulator output",
            "approx_rows": 6362620,
            "time_field": "step",
            "target_field": "isFraud",
            "source_caveat": "Synthetic mobile-money proxy; not real-world AML superiority evidence.",
        },
        "expected_local_root": "data/paper_benchmarks/paysim",
        "required_files": [
            "data/paper_benchmarks/paysim/PS_20174392719_1491204439457_log.csv"
        ],
        "optional_files": [
            "data/paper_benchmarks/paysim/dataset-metadata.json",
            "data/paper_benchmarks/paysim/README.md",
        ],
        "setup_steps": [
            "Create or authenticate a Kaggle account/API token outside the repository.",
            "Download `ealaxi/paysim1` into `data/paper_benchmarks/paysim` and unzip locally.",
            "Keep raw source files out of git unless their license and file size are explicitly approved.",
        ],
        "split_contract_id": "split_paysim_chronological_step_v1",
    },
    {
        "dataset_id": "elliptic_bitcoin_flattened_graph_aml",
        "track_id": "elliptic_flattened_graph_aml",
        "display_name": "Elliptic Bitcoin transaction graph",
        "track_group": "core_graph_aml",
        "benchmark_role": "flattened or raw temporal graph AML evidence",
        "source_posture": "real_blockchain_graph_with_anonymized_features",
        "access_posture": "manual_kaggle_download_required",
        "paper_claim_posture": "supporting-only",
        "claim_id": "claim_elliptic_flattened_graph_aml",
        "license": {
            "spdx_or_name": "CC-BY-NC-ND-4.0",
            "commercial_use": "not_allowed",
            "redistribution": "no_derivatives_noncommercial_only",
            "requires_legal_review_before_bundling": True,
        },
        "source_urls": {
            "dataset_landing": "https://www.kaggle.com/datasets/ellipticco/elliptic-data-set/data",
            "paper": "https://arxiv.org/abs/1908.02591",
            "release_note": "https://www.elliptic.co/media-center/elliptic-releases-bitcoin-transactions-data",
        },
        "known_source_facts": {
            "nodes": 203769,
            "edges": 234355,
            "features_per_node": 166,
            "time_steps": 49,
            "task": "classify licit versus illicit labeled transaction nodes",
            "source_caveat": "Unknown labels and anonymized features require careful metric scope.",
        },
        "expected_local_root": "data/paper_benchmarks/elliptic",
        "required_files": [
            "data/paper_benchmarks/elliptic/elliptic_txs_classes.csv",
            "data/paper_benchmarks/elliptic/elliptic_txs_edgelist.csv",
            "data/paper_benchmarks/elliptic/elliptic_txs_features.csv",
        ],
        "optional_files": [
            "data/paper_benchmarks/elliptic/dataset-metadata.json",
            "data/paper_benchmarks/elliptic/README.md",
        ],
        "setup_steps": [
            "Create or authenticate a Kaggle account/API token outside the repository.",
            "Download `ellipticco/elliptic-data-set` into `data/paper_benchmarks/elliptic` and unzip locally.",
            "Do not redistribute raw files in the repository; cite the source and record local hashes.",
        ],
        "split_contract_id": "split_elliptic_temporal_step_v1",
    },
    {
        "dataset_id": "elliptic2_subgraph_aml",
        "track_id": "elliptic2_subgraph_aml",
        "display_name": "Elliptic2 large Bitcoin subgraph AML dataset",
        "track_group": "core_subgraph_aml_blocked_until_loader",
        "benchmark_role": "subgraph AML and scalability pressure track",
        "source_posture": "real_blockchain_subgraph_dataset",
        "access_posture": "manual_kaggle_download_required_large_dataset",
        "paper_claim_posture": "blocked",
        "claim_id": "claim_subgraph_or_synthetic_bank_graph",
        "license": {
            "spdx_or_name": "CC-BY-NC-ND-4.0",
            "commercial_use": "not_allowed",
            "redistribution": "no_derivatives_noncommercial_only",
            "code_license": "Apache-2.0 for the official guide repository",
            "requires_legal_review_before_bundling": True,
        },
        "source_urls": {
            "dataset_landing": "https://www.kaggle.com/datasets/ellipticco/elliptic2-data-set",
            "paper": "https://arxiv.org/abs/2404.19109",
            "official_guide": "https://github.com/MITIBMxGraph/Elliptic2",
        },
        "known_source_facts": {
            "labeled_subgraphs": 122000,
            "background_node_clusters": 49000000,
            "background_edge_transactions": 196000000,
            "task": "binary suspicious-versus-licit subgraph classification",
            "source_caveat": "Large subgraph workload; paper claim remains blocked until loader, split, and resource gates are frozen.",
        },
        "expected_local_root": "data/paper_benchmarks/elliptic2",
        "required_files": [
            "data/paper_benchmarks/elliptic2/background_edges.csv",
            "data/paper_benchmarks/elliptic2/background_nodes.csv",
            "data/paper_benchmarks/elliptic2/connected_components.csv",
            "data/paper_benchmarks/elliptic2/edges.csv",
            "data/paper_benchmarks/elliptic2/nodes.csv",
        ],
        "optional_files": [
            "data/paper_benchmarks/elliptic2/dataset-metadata.json",
            "data/paper_benchmarks/elliptic2/README.md",
        ],
        "setup_steps": [
            "Create or authenticate a Kaggle account/API token outside the repository.",
            "Download `ellipticco/elliptic2-data-set` into `data/paper_benchmarks/elliptic2` and unzip locally.",
            "Run only after a resource budget and subgraph-loader contract are accepted.",
        ],
        "split_contract_id": "split_elliptic2_subgraph_fixed_seed_v1",
    },
    {
        "dataset_id": "amlsim_synthetic_bank_graph",
        "track_id": "amlsim_synthetic_bank_graph",
        "display_name": "AMLSim synthetic banking transaction generator",
        "track_group": "core_synthetic_bank_graph_blocked_until_generator",
        "benchmark_role": "seeded synthetic-bank AML graph and typology workflow",
        "source_posture": "generator_not_static_dataset",
        "access_posture": "public_git_repository_generator_required",
        "paper_claim_posture": "blocked",
        "claim_id": "claim_subgraph_or_synthetic_bank_graph",
        "license": {
            "spdx_or_name": "Apache-2.0 for generator code",
            "commercial_use": "allowed_for_code_under_apache_2_0",
            "redistribution": "code_redistribution_allowed_with_notice",
            "generated_data_license": "must_be_recorded_for_each_generated_release_pack",
            "requires_legal_review_before_bundling": False,
        },
        "source_urls": {
            "generator_repository": "https://github.com/IBM/AMLSim",
            "ibm_paper": "https://research.ibm.com/publications/realistic-synthetic-financial-transactions-for-anti-money-laundering-models",
            "paper": "https://arxiv.org/abs/2306.16424",
        },
        "known_source_facts": {
            "source_type": "multi-agent banking transaction simulator",
            "target_outputs": ["transaction_log", "alert_transactions", "sar_accounts"],
            "source_caveat": "Synthetic generator evidence is workflow proof unless generated configs, seeds, and outputs are frozen.",
        },
        "expected_local_root": "data/paper_benchmarks/amlsim",
        "required_files": [
            "data/paper_benchmarks/amlsim/conf.json",
            "data/paper_benchmarks/amlsim/tx_log.csv",
            "data/paper_benchmarks/amlsim/alert_transactions.csv",
            "data/paper_benchmarks/amlsim/sar_accounts.csv",
        ],
        "optional_files": [
            "data/paper_benchmarks/amlsim/generator_commit.txt",
            "data/paper_benchmarks/amlsim/generated_dataset_manifest.json",
        ],
        "setup_steps": [
            "Clone or vendor the AMLSim generator outside committed source unless license review approves vendoring.",
            "Freeze `conf.json`, generator commit, random seed, and generated output hashes.",
            "Keep generated data local until a release-pack license decision is recorded.",
        ],
        "split_contract_id": "split_amlsim_seeded_temporal_v1",
    },
    {
        "dataset_id": "generic_structured_support_pack",
        "track_id": "generic_structured_supporting_pack",
        "display_name": "Relaytic repo-local public structured support fixtures",
        "track_group": "supporting_breadth",
        "benchmark_role": "generic structured-data breadth and smoke coverage",
        "source_posture": "repo_local_public_fixture",
        "access_posture": "local_ready_if_files_present",
        "paper_claim_posture": "supporting-only",
        "claim_id": "claim_generic_structured_supporting_pack",
        "license": {
            "spdx_or_name": "repository_license",
            "commercial_use": "inherits_repository_terms",
            "redistribution": "already_repo_local",
            "requires_legal_review_before_bundling": False,
        },
        "source_urls": {
            "repository_path": "data/public",
        },
        "known_source_facts": {
            "source_type": "small local fixtures for smoke and breadth tests",
            "source_caveat": "Useful for framework breadth only; cannot replace AML temporal, graph, or operational evidence.",
        },
        "expected_local_root": "data/public",
        "required_files": [
            "data/public/public_fraud_screening_dataset.csv",
            "data/public/public_binary_classification_dataset.csv",
            "data/public/public_testbench_dataset_20k_minmax.csv",
            "data/public/public_testbench_dataset_20k_minmax.meta.json",
        ],
        "optional_files": [],
        "setup_steps": [
            "No external setup required when repository public fixture files are present.",
        ],
        "split_contract_id": "split_generic_repo_fixture_deterministic_v1",
    },
    {
        "dataset_id": "dgraph_finance_graph_context",
        "track_id": "dgraph_finance_graph_context",
        "display_name": "DGraphFin large dynamic financial fraud graph",
        "track_group": "adjacent_context_only",
        "benchmark_role": "scale and dynamic financial-graph context",
        "source_posture": "real_financial_dynamic_graph",
        "access_posture": "account_gated_noncommercial_download_required",
        "paper_claim_posture": "blocked-context-only",
        "claim_id": None,
        "license": {
            "spdx_or_name": "custom_noncommercial",
            "commercial_use": "not_allowed_or_requires_separate_permission",
            "redistribution": "restricted_by_official_terms",
            "requires_legal_review_before_bundling": True,
        },
        "source_urls": {
            "openreview": "https://openreview.net/forum?id=2rQPxsmjKF",
            "dataset_landing": "https://dgraph.xinye.com",
            "paper": "https://arxiv.org/abs/2207.03579",
        },
        "known_source_facts": {
            "nodes_about": 3000000,
            "edges_about": 4000000,
            "ground_truth_nodes_about": 1000000,
            "source_caveat": "Relevant financial graph benchmark, but not part of the first P2 core claim contract.",
        },
        "expected_local_root": "data/paper_benchmarks/dgraphfin",
        "required_files": [
            "data/paper_benchmarks/dgraphfin/dgraphfin.npz",
        ],
        "optional_files": [
            "data/paper_benchmarks/dgraphfin/license_or_terms_snapshot.txt",
            "data/paper_benchmarks/dgraphfin/README.md",
        ],
        "setup_steps": [
            "Register on the official DGraph site if legal/research use permits it.",
            "Record the non-commercial terms snapshot and local file hash before using as context evidence.",
            "Keep this as context-only unless the paper claim contract is expanded deliberately.",
        ],
        "split_contract_id": "split_dgraphfin_official_or_blocked_v1",
    },
]


SPLIT_CONTRACT_SPECS: list[dict[str, Any]] = [
    {
        "split_contract_id": "split_paysim_chronological_step_v1",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "split_type": "chronological_by_step",
        "required_order_fields": ["step"],
        "label_fields": ["isFraud"],
        "train_window": "earliest 60 percent of ordered steps",
        "validation_window": "next 20 percent of ordered steps",
        "test_window": "latest 20 percent of ordered steps",
        "forbidden_split_methods": ["random_row_shuffle", "stratified_random_without_time"],
        "forbidden_feature_fields": [
            "oldbalanceOrg",
            "newbalanceOrig",
            "oldbalanceDest",
            "newbalanceDest",
        ],
        "primary_metrics": ["pr_auc", "precision_at_k", "recall_at_review_budget"],
        "required_audits": ["temporal_order_check", "rare_event_rate_by_window", "forbidden_feature_check"],
    },
    {
        "split_contract_id": "split_elliptic_temporal_step_v1",
        "dataset_id": "elliptic_bitcoin_flattened_graph_aml",
        "split_type": "temporal_graph_by_time_step",
        "required_order_fields": ["time_step"],
        "label_fields": ["class"],
        "train_window": "early time steps only; exact cut frozen by P5 runner",
        "validation_window": "middle time steps only; exact cut frozen by P5 runner",
        "test_window": "later time steps only; exact cut frozen by P5 runner",
        "forbidden_split_methods": ["random_node_split_across_time", "edge_leaking_future_to_train"],
        "forbidden_feature_fields": [],
        "primary_metrics": ["pr_auc", "precision_at_k", "fixed_fpr_recall"],
        "required_audits": ["time_step_integrity", "unknown_label_scope", "raw_vs_flattened_claim_scope"],
    },
    {
        "split_contract_id": "split_elliptic2_subgraph_fixed_seed_v1",
        "dataset_id": "elliptic2_subgraph_aml",
        "split_type": "subgraph_level_fixed_seed_or_official",
        "required_order_fields": [],
        "label_fields": ["subgraph_label"],
        "train_window": "blocked until official guide split or deterministic seed contract is frozen",
        "validation_window": "blocked until official guide split or deterministic seed contract is frozen",
        "test_window": "blocked until official guide split or deterministic seed contract is frozen",
        "forbidden_split_methods": ["node_level_split_for_subgraph_task", "subgraph_overlap_without_audit"],
        "forbidden_feature_fields": [],
        "primary_metrics": ["pr_auc", "precision_at_k", "fixed_fpr_recall"],
        "required_audits": ["subgraph_overlap_audit", "resource_budget_audit", "loader_provenance"],
    },
    {
        "split_contract_id": "split_amlsim_seeded_temporal_v1",
        "dataset_id": "amlsim_synthetic_bank_graph",
        "split_type": "seeded_generator_temporal",
        "required_order_fields": ["step", "timestamp"],
        "label_fields": ["is_sar", "alert_type"],
        "train_window": "earliest generated time window for each frozen seed",
        "validation_window": "middle generated time window for each frozen seed",
        "test_window": "latest generated time window for each frozen seed",
        "forbidden_split_methods": ["different_generator_configs_across_splits", "unrecorded_random_seed"],
        "forbidden_feature_fields": [],
        "primary_metrics": ["pr_auc", "precision_at_k", "recall_at_review_budget"],
        "required_audits": ["generator_commit", "config_hash", "seed_manifest", "typology_distribution"],
    },
    {
        "split_contract_id": "split_generic_repo_fixture_deterministic_v1",
        "dataset_id": "generic_structured_support_pack",
        "split_type": "deterministic_fixture_split",
        "required_order_fields": [],
        "label_fields": ["target", "label", "is_fraud"],
        "train_window": "deterministic local split according to existing benchmark contract",
        "validation_window": "deterministic local split according to existing benchmark contract",
        "test_window": "deterministic local split according to existing benchmark contract",
        "forbidden_split_methods": ["non_reproducible_random_state"],
        "forbidden_feature_fields": [],
        "primary_metrics": ["pr_auc", "roc_auc", "log_loss"],
        "required_audits": ["fixture_hash", "split_seed", "claim_scope_supporting_only"],
    },
    {
        "split_contract_id": "split_dgraphfin_official_or_blocked_v1",
        "dataset_id": "dgraph_finance_graph_context",
        "split_type": "official_split_or_blocked",
        "required_order_fields": ["edge_time"],
        "label_fields": ["label"],
        "train_window": "official split only, otherwise blocked",
        "validation_window": "official split only, otherwise blocked",
        "test_window": "official split only, otherwise blocked",
        "forbidden_split_methods": ["unofficial_random_resplit_for_public_claim"],
        "forbidden_feature_fields": [],
        "primary_metrics": ["roc_auc", "pr_auc", "fixed_fpr_recall"],
        "required_audits": ["license_terms_snapshot", "official_split_provenance", "context_only_claim_scope"],
    },
]


def build_paper_dataset_registry_pack(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root)
    p2_contract = _read_json(root / "docs" / "reports" / "paper_thesis_contract.json")
    claim_taxonomy = _read_json(root / "docs" / "reports" / "paper_claim_taxonomy.json")
    datasets = [_materialize_dataset_spec(root, spec, claim_taxonomy) for spec in DATASET_SPECS]
    split_contracts = _build_split_contracts(datasets)
    registry = _build_registry(p2_contract, datasets)
    access_manifest = _build_access_manifest(datasets)
    blockers = _build_blockers(datasets, split_contracts)
    return {
        "paper_dataset_registry": registry,
        "paper_dataset_access_manifest": access_manifest,
        "paper_split_contracts": split_contracts,
        "paper_dataset_blockers": blockers,
    }


def sync_paper_dataset_registry_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_DATASET_REGISTRY_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paper_dataset_registry_pack(root)
    written: dict[str, Path] = {}
    for key, filename in PAPER_DATASET_REGISTRY_FILENAMES.items():
        written[key] = write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
    return written


def _build_registry(p2_contract: dict[str, Any], datasets: list[dict[str, Any]]) -> dict[str, Any]:
    p2_tracks = {item["track_id"] for item in p2_contract.get("benchmark_tracks", [])}
    registered_core_tracks = {
        item["track_id"] for item in datasets if item["dataset_id"] in CORE_DATASET_IDS
    }
    local_ready_ids = [item["dataset_id"] for item in datasets if item["local_source_ready"]]
    blocked_ids = [
        item["dataset_id"]
        for item in datasets
        if item["paper_readiness"] in {"blocked", "blocked_context_only"}
    ]
    return {
        "schema_version": PAPER_DATASET_REGISTRY_SCHEMA_VERSION,
        "slice": "Paper Track P3",
        "status": "dataset_registry_frozen",
        "source_review_date": SOURCE_REVIEW_DATE,
        "source_contract_refs": {
            "paper_thesis_contract": "docs/reports/paper_thesis_contract.json",
            "paper_claim_taxonomy": "docs/reports/paper_claim_taxonomy.json",
        },
        "registry_agrees_with_p2_core_tracks": p2_tracks <= registered_core_tracks,
        "hard_performance_claims_allowed": False,
        "datasets": datasets,
        "dataset_count": len(datasets),
        "core_dataset_ids": CORE_DATASET_IDS,
        "local_ready_dataset_ids": local_ready_ids,
        "blocked_or_missing_dataset_ids": [
            item["dataset_id"] for item in datasets if not item["local_source_ready"]
        ],
        "blocked_claim_dataset_ids": blocked_ids,
        "next_slice": "Paper Track P4",
    }


def _build_access_manifest(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for dataset in datasets:
        entries.append(
            {
                "dataset_id": dataset["dataset_id"],
                "display_name": dataset["display_name"],
                "access_posture": dataset["access_posture"],
                "paper_readiness": dataset["paper_readiness"],
                "source_urls": dataset["source_urls"],
                "license": dataset["license"],
                "expected_local_root": dataset["expected_local_root"],
                "local_source_ready": dataset["local_source_ready"],
                "required_file_checks": dataset["required_file_checks"],
                "optional_file_checks": dataset["optional_file_checks"],
                "setup_steps": dataset["setup_steps"],
                "relaytic_auto_download_allowed": False,
                "manual_action_required": not dataset["local_source_ready"],
            }
        )
    return {
        "schema_version": PAPER_DATASET_REGISTRY_SCHEMA_VERSION,
        "slice": "Paper Track P3",
        "status": "dataset_access_manifest_frozen",
        "source_review_date": SOURCE_REVIEW_DATE,
        "access_entries": entries,
        "local_ready_dataset_ids": [
            item["dataset_id"] for item in datasets if item["local_source_ready"]
        ],
        "manual_action_required_dataset_ids": [
            item["dataset_id"] for item in datasets if not item["local_source_ready"]
        ],
        "kaggle_or_account_gated_dataset_ids": [
            item["dataset_id"]
            for item in datasets
            if "kaggle" in item["access_posture"] or "account_gated" in item["access_posture"]
        ],
        "policy": {
            "no_secret_storage": True,
            "no_auto_download_from_authenticated_sources": True,
            "raw_dataset_files_not_committed_by_default": True,
        },
    }


def _build_split_contracts(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    dataset_readiness = {item["dataset_id"]: item["paper_readiness"] for item in datasets}
    contracts = []
    for spec in SPLIT_CONTRACT_SPECS:
        contract = dict(spec)
        contract["paper_readiness"] = dataset_readiness.get(spec["dataset_id"], "unknown")
        contract["claim_posture"] = _claim_posture_for_dataset(spec["dataset_id"], datasets)
        contracts.append(contract)
    return {
        "schema_version": PAPER_DATASET_REGISTRY_SCHEMA_VERSION,
        "slice": "Paper Track P3",
        "status": "split_contracts_frozen",
        "source_review_date": SOURCE_REVIEW_DATE,
        "contracts": contracts,
        "contract_count": len(contracts),
        "global_split_doctrine": {
            "temporal_or_graph_tasks_must_not_randomly_shuffle_across_time": True,
            "proxy_synthetic_and_real_graph_splits_must_not_be_conflated": True,
            "each_table_cell_must_record_dataset_split_command_artifact_and_claim_posture": True,
            "holdout_claims_require_frozen_local_source_hashes": True,
        },
    }


def _build_blockers(
    datasets: list[dict[str, Any]],
    split_contracts: dict[str, Any],
) -> dict[str, Any]:
    dataset_blockers = []
    for dataset in datasets:
        blockers = list(dataset["blocked_reasons"])
        if not dataset["local_source_ready"]:
            missing = [item["path"] for item in dataset["required_file_checks"] if not item["exists"]]
            blockers.append(
                {
                    "blocker_id": f"{dataset['dataset_id']}_local_source_missing",
                    "severity": "blocking",
                    "reason": "Required local source files are missing.",
                    "missing_paths": missing,
                    "repair": "Follow dataset setup steps and rerun the registry sync.",
                }
            )
        dataset_blockers.append(
            {
                "dataset_id": dataset["dataset_id"],
                "paper_readiness": dataset["paper_readiness"],
                "paper_claim_posture": dataset["paper_claim_posture"],
                "blockers": blockers,
                "blocked": bool(blockers) or dataset["paper_readiness"].startswith("blocked"),
            }
        )
    return {
        "schema_version": PAPER_DATASET_REGISTRY_SCHEMA_VERSION,
        "slice": "Paper Track P3",
        "status": "dataset_blockers_frozen",
        "source_review_date": SOURCE_REVIEW_DATE,
        "hard_performance_claims_allowed": False,
        "dataset_blockers": dataset_blockers,
        "global_blockers": [
            {
                "blocker_id": "no_numeric_holdout_paper_rows_yet",
                "severity": "blocking",
                "reason": "P3 only freezes dataset access and split posture; benchmark rows start in P4.",
                "repair": "Implement P4 and P5 runners only for datasets whose source and split contracts pass.",
            },
            {
                "blocker_id": "hard_aml_claims_still_blocked",
                "severity": "blocking",
                "reason": "The P2/P3 claim contracts do not allow hard AML or SOTA superiority claims.",
                "repair": "Do not change public claims until P10-P12 provide reproducible tables and dry-run proof.",
            },
        ],
        "split_contract_count": split_contracts["contract_count"],
        "next_slice": "Paper Track P4",
    }


def _materialize_dataset_spec(
    root: Path,
    spec: dict[str, Any],
    claim_taxonomy: dict[str, Any],
) -> dict[str, Any]:
    dataset = dict(spec)
    required_checks = [_file_check(root, Path(path)) for path in spec["required_files"]]
    optional_checks = [_file_check(root, Path(path)) for path in spec.get("optional_files", [])]
    local_source_ready = all(item["exists"] for item in required_checks)
    claim_boundary = _claim_boundary(spec.get("claim_id"), claim_taxonomy)
    paper_readiness = _paper_readiness(spec, local_source_ready, claim_boundary)
    dataset["required_file_checks"] = required_checks
    dataset["optional_file_checks"] = optional_checks
    dataset["local_source_ready"] = local_source_ready
    dataset["claim_boundary_from_taxonomy"] = claim_boundary
    dataset["paper_readiness"] = paper_readiness
    dataset["blocked_reasons"] = _static_blockers(spec, paper_readiness, local_source_ready)
    return dataset


def _paper_readiness(spec: dict[str, Any], local_source_ready: bool, claim_boundary: str | None) -> str:
    if spec["paper_claim_posture"] == "blocked-context-only":
        return "blocked_context_only"
    if claim_boundary == "blocked":
        return "blocked"
    if not local_source_ready:
        return "source_missing"
    if spec["paper_claim_posture"] == "supporting-only":
        return "supporting_ready"
    return "ready"


def _static_blockers(
    spec: dict[str, Any],
    paper_readiness: str,
    local_source_ready: bool,
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    if spec["paper_claim_posture"] == "blocked":
        blockers.append(
            {
                "blocker_id": f"{spec['dataset_id']}_claim_boundary_blocked",
                "severity": "blocking",
                "reason": "P2 claim taxonomy blocks this dataset from paper-ready claims until later gates pass.",
                "repair": "Implement the corresponding loader/generator, split proof, and claim-scope report first.",
            }
        )
    if spec["paper_claim_posture"] == "blocked-context-only":
        blockers.append(
            {
                "blocker_id": f"{spec['dataset_id']}_context_only",
                "severity": "blocking",
                "reason": "Dataset is adjacent context, not part of the P2 core paper claim contract.",
                "repair": "Keep out of flagship result tables unless a later claim-contract revision adds it.",
            }
        )
    if spec["license"].get("requires_legal_review_before_bundling"):
        blockers.append(
            {
                "blocker_id": f"{spec['dataset_id']}_license_bundling_review",
                "severity": "gating",
                "reason": "Raw source files must not be bundled without explicit license review.",
                "repair": "Store only local hashes, setup instructions, and source citations in the repo.",
            }
        )
    if paper_readiness == "supporting_ready" and local_source_ready:
        return []
    return blockers


def _claim_boundary(claim_id: str | None, claim_taxonomy: dict[str, Any]) -> str | None:
    if claim_id is None:
        return None
    for claim in claim_taxonomy.get("claims", []):
        if claim.get("claim_id") == claim_id:
            return str(claim.get("boundary"))
    return None


def _claim_posture_for_dataset(dataset_id: str, datasets: list[dict[str, Any]]) -> str:
    for dataset in datasets:
        if dataset["dataset_id"] == dataset_id:
            return str(dataset["paper_claim_posture"])
    return "unknown"


def _file_check(root: Path, relative_path: Path) -> dict[str, Any]:
    path = root / relative_path
    exists = path.exists() and path.is_file()
    result: dict[str, Any] = {
        "path": relative_path.as_posix(),
        "exists": exists,
        "size_bytes": None,
        "sha256": None,
    }
    if exists:
        result["size_bytes"] = path.stat().st_size
        result["sha256"] = _sha256(path)
    return result


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

from __future__ import annotations

from pathlib import Path

from relaytic.analytics import sync_architecture_routing_artifacts
from relaytic.compiler import build_compiler_outputs


def test_compiler_builds_research_imported_architecture_registry(tmp_path: Path) -> None:
    run_dir = tmp_path / "compiler_imports"
    planning_bundle = {
        "plan": {
            "task_type": "binary_classification",
            "data_mode": "steady_state",
            "feature_columns": ["feature_a", "feature_b"],
            "task_profile": {
                "task_type": "binary_classification",
                "data_mode": "steady_state",
                "class_count": 2,
            },
            "execution_summary": {
                "selected_model_family": "logistic_regression",
            },
        }
    }
    investigation_bundle = {
        "dataset_profile": {
            "row_count": 320,
            "column_count": 3,
            "numeric_columns": ["feature_a", "feature_b"],
            "categorical_columns": [],
        },
        "optimization_profile": {},
    }
    sync_architecture_routing_artifacts(
        run_dir,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        route_prior_context={},
        benchmark_bundle={},
    )
    research_bundle = {
        "method_transfer_report": {
            "accepted_candidates": [
                {
                    "candidate_kind": "challenger_family",
                    "value": "tabpfn_classifier",
                    "support_reason": "A small-data paper suggested TabPFN as a strong fit.",
                    "source": {
                        "provider": "semantic_scholar",
                        "title": "TabPFN for small tabular classification",
                        "url": "https://example.com/tabpfn",
                        "year": 2025,
                    },
                },
                {
                    "candidate_kind": "challenger_family",
                    "value": "hist_gradient_boosting_classifier",
                    "support_reason": "A benchmark paper suggested histogram gradient boosting.",
                    "source": {
                        "provider": "crossref",
                        "title": "Histogram gradient boosting for structured data",
                        "url": "https://example.com/hgb",
                        "year": 2024,
                    },
                },
            ],
            "advisory_candidates": [
                {
                    "candidate_kind": "challenger_family",
                    "value": "sequence_lstm_candidate",
                    "support_reason": "A temporal paper mentioned LSTM-style sequence baselines.",
                    "source": {
                        "provider": "semantic_scholar",
                        "title": "Temporal sequence models",
                        "url": "https://example.com/lstm",
                        "year": 2023,
                    },
                }
            ],
            "rejected_candidates": [],
        }
    }

    (
        _report,
        _challengers,
        _features,
        _benchmark,
        method_import_report,
        architecture_candidate_registry,
    ) = build_compiler_outputs(
        run_dir=run_dir,
        policy={},
        planning_bundle=planning_bundle,
        investigation_bundle=investigation_bundle,
        research_bundle=research_bundle,
        memory_bundle={},
        benchmark_bundle={},
        decision_world_model={},
        join_candidate_report={},
    )

    assert method_import_report.status == "ok"
    assert method_import_report.imported_family_count == 3
    assert architecture_candidate_registry.candidate_count == 3
    tabpfn = next(
        item
        for item in architecture_candidate_registry.candidates
        if item["family_id"] == "tabpfn_classifier"
    )
    assert tabpfn["source_provider"] == "semantic_scholar"
    assert tabpfn["source_title"] == "TabPFN for small tabular classification"
    assert tabpfn["required_proof_steps"] == ["offline_replay", "shadow_trial", "promotion_readiness_review"]

    lstm = next(
        item
        for item in architecture_candidate_registry.candidates
        if item["family_id"] == "sequence_lstm_candidate"
    )
    assert lstm["shadow_policy"] in {"offline_replay_only", "shadow_only"}
    assert lstm["temporal_gate_required"] is True

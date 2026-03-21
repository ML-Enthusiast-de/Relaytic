from __future__ import annotations

from pathlib import Path

from relaytic.research import run_research_review

from tests.research_test_server import ResearchTestServer


def test_run_research_review_redacts_queries_and_rejects_accuracy_for_rare_event_task(tmp_path: Path) -> None:
    semantic_payload = {
        "data": [
            {
                "title": "Accuracy-focused evaluation for imbalanced fraud detection",
                "abstract": "Accuracy is often reported in fraud detection studies.",
                "year": 2024,
                "url": "https://example.org/fraud-accuracy",
                "citationCount": 12,
                "publicationTypes": ["JournalArticle"],
            },
            {
                "title": "Random forest benchmark for fraud detection",
                "abstract": "Random forest methods remain strong challengers for tabular fraud risk tasks.",
                "year": 2025,
                "url": "https://example.org/fraud-rf",
                "citationCount": 19,
                "publicationTypes": ["JournalArticle"],
            },
        ]
    }
    crossref_payload = {
        "message": {
            "items": [
                {
                    "title": ["Fraud benchmark dataset and baselines"],
                    "URL": "https://example.org/fraud-benchmark",
                    "type": "journal-article",
                    "container-title": ["Journal of Benchmarking"],
                    "issued": {"date-parts": [[2024]]},
                    "is-referenced-by-count": 7,
                }
            ]
        }
    }
    with ResearchTestServer(semantic_payload=semantic_payload, crossref_payload=crossref_payload) as server:
        result = run_research_review(
            run_dir=tmp_path / "research_unit",
            policy={
                "privacy": {"api_calls_allowed": True},
                "runtime": {"semantic_rowless_default": True, "timeout_seconds": 5},
                "research": {
                    "enabled": True,
                    "semantic_scholar_endpoint": server.semantic_url,
                    "crossref_endpoint": server.crossref_url,
                },
            },
            mandate_bundle={"run_brief": {"objective": "Improve fraud detection quality and benchmark against literature."}},
            context_bundle={
                "task_brief": {
                    "task_type_hint": "fraud_detection",
                    "target_column": "customer_ssn_fraud_flag",
                    "problem_statement": "Predict fraud events from transaction history.",
                    "success_criteria": "Strong benchmark posture.",
                }
            },
            investigation_bundle={
                "dataset_profile": {
                    "data_mode": "steady_state",
                    "row_count": 2400,
                    "minority_fraction": 0.03,
                },
                "domain_memo": {"domain_archetype": "fraud_risk"},
                "optimization_profile": {"primary_metric": "pr_auc"},
            },
            planning_bundle={"plan": {"task_type": "fraud_detection", "primary_metric": "pr_auc", "split_strategy": "stratified_holdout"}},
            evidence_bundle={"audit_report": {"readiness_level": "conditional", "provisional_recommendation": "continue_experimentation"}},
        )

    payload = result.bundle.to_dict()
    audit = payload["external_research_audit"]
    transfers = payload["method_transfer_report"]

    assert audit["raw_rows_exported"] is False
    assert audit["identifier_leak_detected"] is False
    assert all("customer_ssn" not in item["query_text"] for item in payload["research_query_plan"]["queries"])
    assert transfers["rejected_candidates"]
    assert any(item["value"] == "accuracy" for item in transfers["rejected_candidates"])
    assert any(item["candidate_kind"] == "challenger_family" for item in transfers["accepted_candidates"])


def test_run_research_review_stays_local_when_privacy_blocks_network(tmp_path: Path) -> None:
    result = run_research_review(
        run_dir=tmp_path / "research_policy_blocked",
        policy={
            "privacy": {"api_calls_allowed": False},
            "runtime": {"semantic_rowless_default": True, "timeout_seconds": 5},
            "research": {"enabled": True},
        },
        mandate_bundle={"run_brief": {"objective": "Benchmark classification quality safely."}},
        context_bundle={
            "task_brief": {
                "task_type_hint": "binary_classification",
                "target_column": "diagnosis_flag",
                "problem_statement": "Classify diagnosis outcomes from measurements.",
                "success_criteria": "Strong benchmark posture.",
            }
        },
        investigation_bundle={
            "dataset_profile": {
                "data_mode": "steady_state",
                "row_count": 569,
                "positive_fraction": 0.37,
            },
            "domain_memo": {"domain_archetype": "medical_diagnosis"},
            "optimization_profile": {"primary_metric": "f1"},
        },
        planning_bundle={"plan": {"task_type": "binary_classification", "primary_metric": "f1", "split_strategy": "stratified_holdout"}},
        evidence_bundle={"audit_report": {"readiness_level": "conditional", "provisional_recommendation": "continue_experimentation"}},
    )

    payload = result.bundle.to_dict()
    inventory = payload["research_source_inventory"]
    brief = payload["research_brief"]
    audit = payload["external_research_audit"]

    assert inventory["status"] == "policy_blocked"
    assert inventory["source_counts"]["total_sources"] == 0
    assert brief["recommended_followup_action"] == "continue_with_local_evidence"
    assert audit["network_allowed"] is False
    assert audit["network_attempted"] is False
    assert audit["raw_rows_exported"] is False
    assert audit["identifier_leak_detected"] is False

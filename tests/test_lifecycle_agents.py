import csv
from pathlib import Path

from relaytic.completion import run_completion_review
from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.evidence import run_evidence_review
from relaytic.investigation import run_investigation
from relaytic.lifecycle import read_lifecycle_bundle, run_lifecycle_review, write_lifecycle_bundle
from relaytic.mandate import (
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
)
from relaytic.planning import execute_planned_route, run_planning
from relaytic.policies import load_policy


def _write_dataset(path: Path) -> Path:
    rows = [
        ["timestamp", "sensor_a", "sensor_b", "failure_flag", "future_failure_flag", "post_inspection_flag"],
        ["2025-01-01T00:00:00", 10.0, 100.0, 0, 0, 0],
        ["2025-01-01T00:01:00", 11.0, 102.0, 0, 0, 0],
        ["2025-01-01T00:02:00", 12.0, 101.0, 1, 1, 1],
        ["2025-01-01T00:03:00", 13.0, 103.0, 0, 0, 0],
        ["2025-01-01T00:04:00", 14.0, 105.0, 1, 1, 1],
        ["2025-01-01T00:05:00", 15.0, 104.0, 0, 0, 0],
        ["2025-01-01T00:06:00", 16.0, 106.0, 1, 1, 1],
        ["2025-01-01T00:07:00", 17.0, 108.0, 0, 0, 0],
        ["2025-01-01T00:08:00", 18.0, 107.0, 1, 1, 1],
        ["2025-01-01T00:09:00", 19.0, 109.0, 0, 0, 0],
        ["2025-01-01T00:10:00", 20.0, 110.0, 1, 1, 1],
        ["2025-01-01T00:11:00", 21.0, 111.0, 0, 0, 0],
        ["2025-01-01T00:12:00", 22.0, 112.0, 1, 1, 1],
        ["2025-01-01T00:13:00", 23.0, 113.0, 0, 0, 0],
        ["2025-01-01T00:14:00", 24.0, 114.0, 1, 1, 1],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    return path


def _build_foundation(policy: dict) -> tuple[dict, dict, dict]:
    mandate_controls = build_mandate_controls_from_policy(policy)
    context_controls = build_context_controls_from_policy(policy)
    mandate_bundle = {
        "lab_mandate": default_lab_mandate(mandate_controls).to_dict(),
        "work_preferences": build_work_preferences(
            mandate_controls,
            policy=policy,
            execution_mode_preference="autonomous",
        ).to_dict(),
        "run_brief": build_run_brief(
            mandate_controls,
            policy=policy,
            objective="best_robust_pareto_front",
            target_column="failure_flag",
            success_criteria=["Catch failures before scrap decisions."],
            binding_constraints=["Do not use future or post-inspection features."],
        ).to_dict(),
    }
    context_bundle = {
        "data_origin": default_data_origin(
            context_controls,
            source_name="line_alarm_history",
            source_type="historical_snapshot",
        ).to_dict(),
        "domain_brief": default_domain_brief(
            context_controls,
            system_name="production_line",
            summary="Predict likely failures early enough to intervene before scrap is created.",
            forbidden_features=["future_failure_flag", "post_inspection_flag"],
        ).to_dict(),
        "task_brief": default_task_brief(
            context_controls,
            problem_statement="Predict failure flags from upstream process sensors.",
            target_column="failure_flag",
            success_criteria=["Maximize useful early warning value."],
            failure_costs=["Missed failures lead to scrap and avoidable downtime."],
        ).to_dict(),
    }
    intake_bundle = {
        "autonomy_mode": {
            "requested_mode": "autonomous",
            "operator_signal": "do everything on your own",
        },
        "clarification_queue": {"active_count": 0},
        "assumption_log": {"entries": [{"assumption": "autonomous default request"}]},
    }
    return mandate_bundle, context_bundle, intake_bundle


def _build_run_payloads(tmp_path: Path) -> tuple[Path, Path, dict, dict, dict, dict, dict, dict]:
    data_path = _write_dataset(tmp_path / "slice08.csv")
    run_dir = tmp_path / "run_slice08"
    policy = load_policy().policy
    mandate_bundle, context_bundle, intake_bundle = _build_foundation(policy)
    investigation_bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    ).to_dict()
    planning_bundle = run_planning(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
    )
    execution = execute_planned_route(
        run_dir=run_dir,
        data_path=str(data_path),
        planning_bundle=planning_bundle,
    )
    evidence_result = run_evidence_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=execution.planning_bundle.to_dict(),
    )
    completion_result = run_completion_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=execution.planning_bundle.to_dict(),
        evidence_bundle=evidence_result.bundle.to_dict(),
    )
    return (
        data_path,
        run_dir,
        policy,
        mandate_bundle,
        context_bundle,
        investigation_bundle,
        execution.planning_bundle.to_dict(),
        {
            "evidence_bundle": evidence_result.bundle.to_dict(),
            "completion_bundle": completion_result.bundle.to_dict(),
        },
    )


def test_run_lifecycle_review_prefers_recalibration_over_retraining(tmp_path: Path, monkeypatch) -> None:
    data_path, run_dir, policy, mandate_bundle, context_bundle, investigation_bundle, planning_bundle, payloads = _build_run_payloads(tmp_path)

    def fake_inference(**_: object) -> dict[str, object]:
        return {
            "status": "ok",
            "evaluation": {
                "available": True,
                "metrics": {
                    "accuracy": 0.84,
                    "f1": 0.83,
                    "log_loss": 0.71,
                    "precision": 0.82,
                    "recall": 0.84,
                },
            },
            "drift_summary": {"overall_drift_score": 0.34},
            "ood_summary": {"overall_ood_fraction": 0.01},
            "recommendations": [],
        }

    monkeypatch.setattr("relaytic.lifecycle.agents.run_inference_from_artifacts", fake_inference)

    result = run_lifecycle_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=payloads["evidence_bundle"],
        completion_bundle=payloads["completion_bundle"],
    )

    assert result.bundle.recalibration_decision.action == "recalibrate"
    assert result.bundle.retrain_decision.action == "no_retrain"


def test_run_lifecycle_review_promotes_superior_challenger_when_stable(tmp_path: Path, monkeypatch) -> None:
    data_path, run_dir, policy, mandate_bundle, context_bundle, investigation_bundle, planning_bundle, payloads = _build_run_payloads(tmp_path)
    evidence_bundle = dict(payloads["evidence_bundle"])
    evidence_bundle["challenger_report"] = {
        **dict(evidence_bundle["challenger_report"]),
        "winner": "challenger",
        "delta_to_champion": 0.07,
        "comparison": {
            **dict(dict(evidence_bundle["challenger_report"]).get("comparison") or {}),
            "challenger_model_family": "boosted_tree_classifier",
            "challenger_metric_value": 0.91,
        },
    }
    evidence_bundle["audit_report"] = {
        **dict(evidence_bundle["audit_report"]),
        "readiness_level": "strong",
    }

    def fake_inference(**_: object) -> dict[str, object]:
        return {
            "status": "ok",
            "evaluation": {"available": True, "metrics": {"accuracy": 0.88, "f1": 0.88, "log_loss": 0.32}},
            "drift_summary": {"overall_drift_score": 0.08},
            "ood_summary": {"overall_ood_fraction": 0.0},
            "recommendations": [],
        }

    monkeypatch.setattr("relaytic.lifecycle.agents.run_inference_from_artifacts", fake_inference)

    result = run_lifecycle_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        completion_bundle=payloads["completion_bundle"],
    )

    assert result.bundle.promotion_decision.action == "promote_challenger"
    assert result.bundle.promotion_decision.selected_model_family == "boosted_tree_classifier"


def test_run_lifecycle_review_requires_rollback_when_route_is_not_trustworthy(tmp_path: Path, monkeypatch) -> None:
    data_path, run_dir, policy, mandate_bundle, context_bundle, investigation_bundle, planning_bundle, payloads = _build_run_payloads(tmp_path)

    def fake_inference(**_: object) -> dict[str, object]:
        return {
            "status": "ok",
            "evaluation": {
                "available": True,
                "metrics": {
                    "accuracy": 0.51,
                    "f1": 0.42,
                    "log_loss": 1.24,
                    "precision": 0.45,
                    "recall": 0.40,
                },
            },
            "drift_summary": {"overall_drift_score": 0.79},
            "ood_summary": {"overall_ood_fraction": 0.12},
            "recommendations": [],
        }

    monkeypatch.setattr("relaytic.lifecycle.agents.run_inference_from_artifacts", fake_inference)

    result = run_lifecycle_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=payloads["evidence_bundle"],
        completion_bundle=payloads["completion_bundle"],
    )
    written = write_lifecycle_bundle(run_dir, bundle=result.bundle)
    bundle = read_lifecycle_bundle(run_dir)

    assert result.bundle.retrain_decision.action == "retrain"
    assert result.bundle.rollback_decision.action == "rollback_required"
    assert Path(written["rollback_decision"]).exists()
    assert "rollback_decision" in bundle

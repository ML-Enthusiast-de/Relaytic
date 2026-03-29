from __future__ import annotations

from pathlib import Path

from relaytic.core.json_utils import write_json
from relaytic.policies import load_policy
from relaytic.pulse import run_pulse_review, write_pulse_bundle


def _write_run_summary(
    run_dir: Path,
    *,
    stage_completed: str = "autonomy_reviewed",
    benchmark: dict | None = None,
    research: dict | None = None,
    completion: dict | None = None,
) -> None:
    write_json(
        run_dir / "run_summary.json",
        {
            "schema_version": "relaytic.run_summary.v1",
            "generated_at": "2026-03-29T00:00:00+00:00",
            "product": "Relaytic",
            "run_id": run_dir.name,
            "run_dir": str(run_dir),
            "status": "ok",
            "stage_completed": stage_completed,
            "intent": {
                "objective": "classify diagnosis_flag from measurement columns",
                "domain_archetype": "screening_risk",
                "autonomy_mode": "autonomous",
            },
            "decision": {
                "task_type": "binary_classification",
                "target_column": "diagnosis_flag",
                "primary_metric": "pr_auc",
                "selected_model_family": "bagged_tree_classifier",
            },
            "benchmark": benchmark or {},
            "research": research or {},
            "completion": completion or {},
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def test_run_pulse_review_skips_when_nothing_useful_is_pending(tmp_path: Path) -> None:
    policy = load_policy().policy
    policy["pulse"]["allow_innovation_watch"] = False
    policy["pulse"]["allow_memory_maintenance"] = False
    policy["pulse"]["allow_queue_refresh"] = False

    result = run_pulse_review(run_dir=tmp_path / "pulse_skip", policy=policy, trigger_kind="scheduled")

    assert result.bundle.pulse_run_report.status == "skipped"
    assert result.bundle.pulse_skip_report.skip_reason == "nothing_useful_pending"
    assert result.bundle.challenge_watchlist.items == []
    assert result.bundle.pulse_recommendations.recommendations == []
    assert "# Relaytic Lab Pulse" in result.review_markdown


def test_run_pulse_review_throttles_non_manual_runs(tmp_path: Path) -> None:
    policy = load_policy().policy
    policy["pulse"]["allow_innovation_watch"] = False
    policy["pulse"]["allow_memory_maintenance"] = False
    policy["pulse"]["allow_queue_refresh"] = False
    policy["pulse"]["throttle_minutes"] = 240
    policy["pulse"]["schedule_minutes"] = 240

    run_dir = tmp_path / "pulse_throttle"
    first = run_pulse_review(run_dir=run_dir, policy=policy, trigger_kind="manual")
    write_pulse_bundle(run_dir, bundle=first.bundle)

    second = run_pulse_review(run_dir=run_dir, policy=policy, trigger_kind="scheduled")

    assert second.bundle.pulse_schedule.throttled is True
    assert second.bundle.pulse_run_report.status == "skipped"
    assert second.bundle.pulse_skip_report.skip_reason == "pulse_throttled"


def test_run_pulse_review_writes_watchlist_and_rowless_innovation_recommendations(tmp_path: Path) -> None:
    policy = load_policy().policy
    run_dir = tmp_path / "pulse_propose"
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_run_summary(
        run_dir,
        benchmark={"beat_target_state": "unmet", "reference_count": 1},
        research={"network_allowed": True},
    )
    write_json(
        run_dir / "beat_target_contract.json",
        {
            "contract_state": "unmet",
            "summary": "Imported incumbent remains stronger than the current Relaytic route.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    result = run_pulse_review(run_dir=run_dir, policy=policy, trigger_kind="manual")

    assert result.bundle.pulse_run_report.status == "ok"
    assert result.bundle.challenge_watchlist.items
    assert result.bundle.innovation_watch_report.leads
    assert result.bundle.innovation_watch_report.raw_rows_exported is False
    assert result.bundle.innovation_watch_report.identifier_leak_detected is False
    assert result.bundle.innovation_watch_report.rowless_query["rowless"] is True
    assert result.bundle.pulse_recommendations.queued_actions
    assert result.bundle.pulse_recommendations.recommendations[0]["action_kind"] == "refresh_benchmark_review"


def test_run_pulse_review_bounded_execute_pins_memory_for_later_retrieval(tmp_path: Path) -> None:
    policy = load_policy().policy
    policy["pulse"]["mode"] = "bounded_execute"
    run_dir = tmp_path / "pulse_bounded"
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_run_summary(
        run_dir,
        completion={"blocking_layer": "missing_memory_support"},
    )
    write_json(
        run_dir / "reflection_memory.json",
        {
            "summary": "Bagged trees remained stable on this dataset family when route breadth stayed narrow.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "causal_memory_index.json",
        {
            "similar_harmful_override_count": 2,
            "patterns": ["forced unsafe override"],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "method_memory_index.json",
        {
            "entries": [{"method": "calibration_review", "outcome": "helpful"}],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    result = run_pulse_review(run_dir=run_dir, policy=policy, trigger_kind="manual")

    assert result.bundle.pulse_run_report.status == "ok"
    assert result.bundle.memory_compaction_report.executed is True
    assert result.bundle.memory_pinning_index.pin_count >= 3
    assert any(
        item["action_id"] == "memory_compaction_and_pinning"
        for item in result.bundle.pulse_run_report.executed_actions
    )

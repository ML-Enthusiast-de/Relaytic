from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset, write_public_diabetes_dataset


def _write_slice15_config(path: Path, *, run_dir: Path | None = None) -> Path:
    lines = [
        "policy:",
        "  permissions:",
        "    default_mode: review",
        "remote_control:",
        "  enabled: true",
        "  transport_kind: filesystem_sync",
        "  transport_scope: local_only",
    ]
    if run_dir is not None:
        lines.extend(
            [
                "communication:",
                f"  adaptive_onboarding_default_run_dir: {run_dir.as_posix()}",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_cli_slice15_mission_control_spans_two_runs_and_datasets(tmp_path: Path, capsys) -> None:
    config_path = _write_slice15_config(tmp_path / "slice15_config.yaml")
    first_run = tmp_path / "slice15_first_run"
    second_run = tmp_path / "slice15_second_run"
    first_data = write_public_breast_cancer_dataset(tmp_path / "slice15_breast_cancer.csv")
    second_data = write_public_diabetes_dataset(tmp_path / "slice15_diabetes.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(first_run),
            "--data-path",
            str(first_data),
            "--text",
            "Do everything on your own. Predict diagnosis_flag from the provided features.",
            "--config",
            str(config_path),
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "run",
            "--run-dir",
            str(second_run),
            "--data-path",
            str(second_data),
            "--text",
            "Do everything on your own. Predict disease_progression from the provided features and keep the reasoning explainable.",
            "--config",
            str(config_path),
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "permissions",
            "check",
            "--run-dir",
            str(second_run),
            "--action",
            "relaytic_run_autonomy",
            "--mode",
            "review",
            "--config",
            str(config_path),
            "--format",
            "json",
        ]
    ) == 0
    permission_payload = json.loads(capsys.readouterr().out)
    assert permission_payload["decision"]["request_id"]

    assert main(
        [
            "mission-control",
            "show",
            "--run-dir",
            str(second_run),
            "--config",
            str(config_path),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    mission_control = dict(payload["mission_control"])
    bundle = dict(payload["bundle"])
    run_summary = json.loads((second_run / "run_summary.json").read_text(encoding="utf-8"))

    assert run_summary["decision"]["target_column"] == "disease_progression"
    assert run_summary["workspace"]["lineage_run_count"] >= 2
    assert mission_control["overall_confidence"] is not None
    assert mission_control["branch_count"] >= 1
    assert mission_control["background_job_count"] is not None
    assert mission_control["permission_mode"] in {"review", "bounded_autonomy"}
    assert mission_control["pending_approval_count"] >= 1
    assert mission_control["release_health_status"] in {"preflight_only", "safe_to_ship", "needs_attention"}
    assert mission_control["demo_story_count"] >= 4
    card_ids = {str(item.get("card_id")) for item in bundle["mission_control_state"]["cards"]}
    assert {"confidence_map", "branch_replay", "release_health", "demo_pack"}.issubset(card_ids)

    assert bundle["branch_dag"]["branch_count"] >= 1
    assert bundle["confidence_map"]["overall_confidence"] is not None
    assert bundle["change_attribution_report"]["status"] in {"ok", "stable"}
    assert bundle["trace_explorer_state"]["span_count"] > 0
    assert bundle["branch_replay_index"]["replay_count"] >= 1
    assert bundle["approval_timeline"]["pending_count"] >= 1
    assert bundle["background_job_view"]["status"] in {"ok", "idle", "needs_attention"}
    assert isinstance(bundle["background_job_view"]["recent_events"], list)
    assert bundle["permission_mode_card"]["current_mode"] in {"review", "bounded_autonomy"}
    assert bundle["release_health_report"]["status"] in {"preflight_only", "safe_to_ship", "needs_attention"}
    assert bundle["demo_pack_manifest"]["demo_count"] >= 4
    assert bundle["flagship_demo_scorecard"]["status"] in {"ready", "partial"}
    assert bundle["human_factors_eval_report"]["explanation_quality"] in {"strong", "developing"}
    assert bundle["onboarding_success_report"]["status"] in {"ready", "watch"}

    for artifact_name in (
        "branch_dag.json",
        "confidence_map.json",
        "change_attribution_report.json",
        "trace_explorer_state.json",
        "branch_replay_index.json",
        "approval_timeline.json",
        "background_job_view.json",
        "permission_mode_card.json",
        "release_health_report.json",
        "demo_pack_manifest.json",
        "flagship_demo_scorecard.json",
        "human_factors_eval_report.json",
        "onboarding_success_report.json",
    ):
        assert (second_run / artifact_name).exists(), artifact_name


def test_cli_slice15_user_chat_flow_handles_regression_dataset(tmp_path: Path, capsys, monkeypatch) -> None:
    output_dir = tmp_path / "slice15_chat_output"
    run_dir = tmp_path / "slice15_chat_run"
    data_path = write_public_diabetes_dataset(tmp_path / "slice15_chat_diabetes.csv")
    config_path = _write_slice15_config(tmp_path / "slice15_chat_config.yaml", run_dir=run_dir)
    prompts = iter(
        [
            str(data_path),
            "predict disease_progression and keep it easy to understand",
            "yes",
            "what can you do now?",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    assert main(
        [
            "mission-control",
            "chat",
            "--output-dir",
            str(output_dir),
            "--config",
            str(config_path),
            "--expected-profile",
            "full",
            "--max-turns",
            "4",
        ]
    ) == 0
    output = capsys.readouterr().out
    session = json.loads((output_dir / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))
    created_run_dir = Path(str(session["created_run_dir"]))
    run_summary = json.loads((created_run_dir / "run_summary.json").read_text(encoding="utf-8"))

    assert "I found a dataset path" in output
    assert "I've started a governed run" in output
    assert "Relaytic is now in run-specific mode" in output
    assert session["created_run_dir"]
    assert run_summary["decision"]["target_column"] == "disease_progression"

    assert main(
        [
            "mission-control",
            "show",
            "--run-dir",
            str(created_run_dir),
            "--config",
            str(config_path),
            "--format",
            "json",
        ]
    ) == 0
    mission_payload = json.loads(capsys.readouterr().out)
    mission_control = dict(mission_payload["mission_control"])
    bundle = dict(mission_payload["bundle"])

    assert mission_control["overall_confidence"] is not None
    assert mission_control["trace_winning_action"] is not None
    assert mission_control["onboarding_ready_for_first_time_user"] is True
    assert bundle["human_factors_eval_report"]["first_run_success_ready"] is True
    assert bundle["onboarding_success_report"]["supports_analysis_first"] is True
    assert bundle["demo_pack_manifest"]["demo_count"] >= 4

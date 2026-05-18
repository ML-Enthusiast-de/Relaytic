from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.ui.cli import main


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _write_partial_run_summary(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        run_dir / "run_summary.json",
        {
            "schema_version": "relaytic.run_summary.v1",
            "run_id": "slice15v_a_partial",
            "status": "initialized",
            "stage_completed": "profiles_reviewed",
            "headline": "Relaytic prepared a partial run and is waiting for more evidence.",
            "request": {
                "actor_type": "user",
                "channel": "cli",
                "text_preview": "Review /private/local/data.csv without exposing raw rows.",
            },
            "intent": {
                "objective": "classify suspicious transactions",
                "domain_archetype": "aml",
                "problem_statement": "Find a safe next modeling step.",
                "autonomy_mode": "assisted",
            },
            "decision": {
                "task_type": "classification",
                "target_column": "label",
                "selected_model_family": None,
                "primary_metric": "pr_auc",
                "split_strategy": "temporal",
            },
            "completion": {},
            "handoff": {},
            "lifecycle": {},
            "result_contract": {
                "status": "provisional",
                "recommended_direction": "same_data",
                "overall_confidence": "low",
            },
            "benchmark": {},
            "data": {
                "row_count": 12,
                "column_count": 5,
                "source_format": "csv",
                "copy_enforced": True,
                "immutable_working_copies": True,
            },
        },
    )


def test_cli_guide_onboarding_writes_no_lost_artifacts(tmp_path: Path, capsys: Any) -> None:
    state_dir = tmp_path / "guide_onboarding"

    assert main(["guide", "--output-dir", str(state_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["guide"]["current_state"] == "onboarding"
    assert payload["guide"]["safe_command_count"] >= 3
    assert (state_dir / "guide_state.json").exists()
    assert (state_dir / "guide_action_menu.json").exists()
    actions = payload["bundle"]["guide_action_menu"]["actions"]
    assert any(item["action_id"] == "mission_control_chat" for item in actions)
    assert any("what kind of data" in question for question in payload["bundle"]["guide_question_starters"]["questions"])


def test_cli_status_falls_back_to_guide_for_partial_run(tmp_path: Path, capsys: Any) -> None:
    run_dir = tmp_path / "partial_run"
    _write_partial_run_summary(run_dir)

    assert main(["status", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "partial"
    assert payload["fallback_source"] == "guide"
    assert payload["guide"]["current_state"] == "partial_run"
    assert payload["guide"]["missing_evidence_count"] >= 1
    assert (run_dir / "guide_state.json").exists()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest_paths = {item["path"] for item in manifest["entries"]}
    assert "guide_state.json" in manifest_paths


def test_cli_guide_export_context_pack_is_rowless_and_redacted(tmp_path: Path, capsys: Any) -> None:
    run_dir = tmp_path / "partial_run_export"
    _write_partial_run_summary(run_dir)

    assert main(["guide", "export-context", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["external_context_pack"]["raw_rows_included"] is False
    context_path = run_dir / "external_llm_context_pack.json"
    redaction_path = run_dir / "external_llm_redaction_report.json"
    assert context_path.exists()
    assert redaction_path.exists()

    context_text = context_path.read_text(encoding="utf-8")
    redaction_report = json.loads(redaction_path.read_text(encoding="utf-8"))
    assert str(tmp_path).replace("\\", "/") not in context_text.replace("\\", "/")
    assert "/private/local/data.csv" not in context_text
    assert "<redacted_path:" in context_text
    assert redaction_report["raw_rows_included"] is False
    assert redaction_report["redaction_count"] >= 1

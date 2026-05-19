from __future__ import annotations

import json
from pathlib import Path

import pytest

from relaytic.release_safety import (
    REPO_CREDIBILITY_FILENAMES,
    build_repo_credibility_reports,
)
from relaytic.ui.aml_environment import aml_environment_surface_summary
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def _load_report(key: str) -> dict[str, object]:
    path = REPORT_DIR / REPO_CREDIBILITY_FILENAMES[key]
    return json.loads(path.read_text(encoding="utf-8"))


def test_slice15z_repo_credibility_reports_exist() -> None:
    for filename in REPO_CREDIBILITY_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    reports = build_repo_credibility_reports(PROJECT_ROOT)
    assert set(reports) == set(REPO_CREDIBILITY_FILENAMES)

    audit = _load_report("pre_academy_repo_audit")
    acceptance = dict(audit["acceptance_status"])
    assert acceptance["oversized_module_split"] is True
    assert acceptance["retained_oversized_modules_documented"] is True
    assert acceptance["public_surface_inventory_clean"] is True
    assert acceptance["benchmark_cleanup_debt_listed"] is True


def test_slice15z_import_boundary_smoke(capsys: pytest.CaptureFixture[str]) -> None:
    summary = aml_environment_surface_summary(
        {
            "aml_environment_scorecard": {
                "overall_environment_status": "pass",
                "environment_score": 0.91,
                "model_quality_score": 0.88,
                "model_score_and_environment_score_separate": True,
            },
            "aml_workflow_task_matrix": {
                "rows": [{"task_id": "unsafe_steering_rejection", "status": "pass"}],
            },
        }
    )

    assert summary["status"] == "pass"
    assert summary["environment_score"] == 0.91
    assert summary["task_statuses"] == {"unsafe_steering_rejection": "pass"}

    with pytest.raises(SystemExit) as exc:
        main(["aml", "environment", "--help"])
    assert exc.value.code == 0
    assert "relaytic aml environment" in capsys.readouterr().out


def test_slice15z_public_surface_inventory_is_clean() -> None:
    inventory = _load_report("public_surface_inventory")
    commands = {str(item["command"]): dict(item) for item in inventory["commands"]}  # type: ignore[index]

    required_commands = {
        "relaytic benchmark run",
        "relaytic benchmark show",
        "relaytic demo aml-review-queue",
        "relaytic aml graph-loader",
        "relaytic aml business-value",
        "relaytic aml baselines",
        "relaytic aml temporal",
        "relaytic aml environment",
        "relaytic guide export-context",
        "relaytic release-safety scan",
        "relaytic release-safety paper-freeze",
        "relaytic trace show",
        "relaytic evals run",
    }
    assert required_commands <= set(commands)

    for command, row in commands.items():
        serialized = json.dumps(row, sort_keys=True).lower()
        assert row["stale_surface_language_detected"] is False, command
        assert "corr2surrogate" not in serialized, command
        assert "prototype" not in serialized, command
        assert row["public_name"] == "Relaytic", command
        assert row["package_name"] == "relaytic", command


def test_slice15z_module_split_and_retained_debt_are_documented() -> None:
    split = _load_report("module_split_report")
    split_rows = list(split["split_modules"])  # type: ignore[arg-type]
    assert split_rows
    first_split = dict(split_rows[0])
    assert first_split["source_module"] == "src/relaytic/ui/cli.py"
    assert first_split["extracted_module"] == "src/relaytic/ui/aml_environment.py"
    assert first_split["public_behavior_preserved"] is True
    assert (PROJECT_ROOT / str(first_split["extracted_module"])).exists()
    assert int(first_split["extracted_module_lines"]) >= 100
    assert "relaytic aml environment" in first_split["public_commands_preserved"]

    reports = build_repo_credibility_reports(PROJECT_ROOT)
    oversized = reports["pre_academy_repo_audit"]["module_size_audit"]["oversized_modules"]
    assert any(item["path"] == "src/relaytic/ui/cli.py" for item in oversized)
    assert all(str(item.get("next_extraction_boundary", "")).strip() for item in oversized)

    cleanup = _load_report("benchmark_surface_cleanup_report")
    debts = list(cleanup["retained_cleanup_debt"])  # type: ignore[arg-type]
    assert {dict(item)["debt_id"] for item in debts} >= {
        "paper_freeze_not_yet_materialized",
        "benchmark_agents_still_oversized",
        "cli_entrypoint_still_oversized",
    }

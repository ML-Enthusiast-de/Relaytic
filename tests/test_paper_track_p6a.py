from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAYSIM_COMPETITIVE_FILENAMES,
    build_paysim_competitive_pack,
    sync_paysim_competitive_pack,
)
from relaytic.ui.cli import main
from tests.aml_workload_fixtures import write_paysim_like_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p6a_runs_smoke_competitive_contract_without_test_search(tmp_path: Path) -> None:
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")

    pack = build_paysim_competitive_pack(PROJECT_ROOT, data_path=data_path, budget_tier="smoke")

    manifest = pack["paysim_competitive_benchmark_manifest"]
    budget = pack["paysim_competitive_budget_contract"]
    trace = pack["paysim_competitive_search_trace"]
    features = pack["paysim_leakage_safe_feature_report"]
    table = pack["paysim_competitive_baseline_table"]
    gate = pack["paysim_publishability_gate"]

    assert manifest["schema_version"] == "relaytic.paysim_competitive_benchmark.v1"
    assert manifest["slice"] == "Paper Track P6-A"
    assert manifest["status"] == "ok"
    assert manifest["effective_budget_tier"] == "smoke"
    assert manifest["next_slice"] == "Paper Track P7"
    assert manifest["hpo_trial_count"] >= 3
    assert manifest["finalist_family_count"] >= 3

    assert budget["test_evaluation_policy"] == "only_validation_selected_finalist_is_evaluated_on_test"
    assert budget["threshold_policy"] == "validation_operating_partition_only_then_fixed_test_application"
    assert trace["hpo_trial_count"] >= 3
    assert trace["calibration_trace"]["test_used_for_calibration_or_selection"] is False
    assert trace["selected_finalist"]["selection_surface"] == "validation_pr_auc_only_before_test_evaluation"

    assert features["status"] == "pass"
    assert features["balance_fields_used"] is False
    assert features["raw_identifier_encoding_used"] is False
    assert features["state_key_source_fields"] == ["nameDest"]
    assert features["same_step_entity_information_used"] is False
    assert "log1p_destination_prior_transaction_count" in features["feature_columns"]

    selected_rows = [row for row in table["rows"] if row.get("selected_for_test_evaluation")]
    evaluated_rows = [row for row in table["rows"] if row.get("test_evaluated")]
    assert len(selected_rows) == 1
    assert len(evaluated_rows) == 1
    assert table["validation_selected_competitive_model"]["test_pr_auc"] is not None

    assert gate["status"] == "blocked"
    assert gate["supporting_paper_table_candidate_allowed"] is False
    assert gate["headline_performance_claim_allowed"] is False
    assert "competitive_budget_not_executed" in gate["blocked_reason_codes"]


def test_paper_track_p6a_missing_source_blocks_without_claims(tmp_path: Path) -> None:
    pack = build_paysim_competitive_pack(PROJECT_ROOT, data_path=tmp_path / "missing.csv")

    manifest = pack["paysim_competitive_benchmark_manifest"]
    gate = pack["paysim_publishability_gate"]

    assert manifest["status"] == "blocked"
    assert "p6a_paysim_source_file_missing" in manifest["blocked_reason_codes"]
    assert any("paysim-competitive" in item for item in manifest["recovery_instructions"])
    assert manifest["hard_performance_claims_allowed"] is False
    assert gate["supporting_paper_table_candidate_allowed"] is False


def test_paper_track_p6a_sync_writes_required_artifacts(tmp_path: Path) -> None:
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")
    output_dir = tmp_path / "reports"

    written = sync_paysim_competitive_pack(
        PROJECT_ROOT,
        data_path=data_path,
        output_dir=output_dir,
        budget_tier="smoke",
    )

    assert set(written) == set(PAYSIM_COMPETITIVE_FILENAMES)
    for path in written.values():
        assert path.exists()
    manifest = json.loads((output_dir / "paysim_competitive_benchmark_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ok"


def test_paper_track_p6a_cli_exposes_machine_readable_surface(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: Any,
) -> None:
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")
    output_dir = tmp_path / "cli_reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paysim-competitive",
            "--data-path",
            str(data_path),
            "--output-dir",
            str(output_dir),
            "--budget-tier",
            "smoke",
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["paysim_competitive"]["next_slice"] == "Paper Track P7"
    assert (output_dir / "paysim_publishability_gate.json").exists()


def test_paper_track_p6a_committed_artifacts_keep_claim_scope_honest() -> None:
    for filename in PAYSIM_COMPETITIVE_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paysim_competitive_benchmark_manifest.json")
    table = _load_report("paysim_competitive_baseline_table.json")
    features = _load_report("paysim_leakage_safe_feature_report.json")
    gate = _load_report("paysim_publishability_gate.json")

    assert manifest["schema_version"] == "relaytic.paysim_competitive_benchmark.v1"
    assert manifest["effective_budget_tier"] == "competitive"
    assert table["validation_selected_competitive_model"]["test_pr_auc"] is not None
    assert features["balance_fields_used"] is False
    assert features["raw_identifier_encoding_used"] is False
    assert gate["headline_performance_claim_allowed"] is False
    assert gate["paper_primary_claim_allowed"] is False
    assert gate["hard_performance_claims_allowed"] is False

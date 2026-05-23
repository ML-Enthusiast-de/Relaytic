from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.release_safety import (
    PAPER_BASELINE_FILENAMES,
    build_paper_baseline_suite_pack,
    sync_paper_baseline_suite_pack,
)
from relaytic.ui.cli import main
from tests.aml_workload_fixtures import write_paysim_like_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p6_runs_clean_smoke_baseline_suite(tmp_path: Path) -> None:
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")

    pack = build_paper_baseline_suite_pack(PROJECT_ROOT, data_path=data_path, budget_tier="smoke")

    manifest = pack["paper_baseline_suite_manifest"]
    table = pack["paper_tabular_baseline_table"]
    versions = pack["paper_baseline_version_matrix"]
    feature_report = pack["paper_leakage_safe_feature_report"]
    budget = pack["paper_benchmark_budget_contract"]
    trace = pack["paper_competitive_search_trace"]
    gate = pack["paper_publishability_gate"]

    assert manifest["schema_version"] == "relaytic.paper_tabular_baseline_suite.v1"
    assert manifest["slice"] == "Paper Track P6"
    assert manifest["status"] == "ok"
    assert manifest["effective_budget_tier"] == "smoke"
    assert manifest["executed_family_count"] >= 3
    assert manifest["next_slice"] == "Paper Track P6-A"

    assert table["status"] == "ok"
    assert table["split_contract_id"] == "split_paysim_chronological_step_v1"
    assert table["headline_table_eligible"] is False
    assert table["validation_selected_baseline"]["selection_surface"] == "validation_pr_auc_only"
    assert {row["budget_tier"] for row in table["rows"]} == {"smoke"}
    assert all(row["threshold_selection_surface"] == "validation_only" for row in table["rows"])
    assert "deterministic_transfer_cashout_rule" in {row["family_id"] for row in table["rows"]}

    matrix_by_family = {row["family_id"]: row for row in versions["rows"]}
    assert matrix_by_family["sklearn_hist_gradient_boosting"]["execution_state"] == "ran"
    assert "lightgbm_classifier" in matrix_by_family
    assert "catboost_classifier" in matrix_by_family

    assert feature_report["status"] == "pass"
    assert feature_report["balance_fields_used"] is False
    assert feature_report["validation_or_test_fit_state_used"] is False
    assert feature_report["forbidden_model_columns_used"] == []
    assert "oldbalanceOrg" in feature_report["forbidden_source_columns_present_but_excluded"]

    assert budget["effective_budget_tier"] == "smoke"
    assert any(row["budget_tier"] == "competitive" and row["execution_state"] == "reserved_for_p6_a" for row in budget["tiers"])
    assert trace["hpo_trial_count"] == 0
    assert trace["status"] == "baseline_executed_competitive_reserved"

    assert gate["status"] == "blocked"
    assert gate["baseline_protocol_clean"] is True
    assert gate["headline_performance_claim_allowed"] is False
    assert gate["paper_primary_claim_allowed"] is False
    assert "competitive_budget_not_executed_p6_a_required" in gate["blocked_reason_codes"]


def test_paper_track_p6_missing_source_blocks_without_claims(tmp_path: Path) -> None:
    pack = build_paper_baseline_suite_pack(PROJECT_ROOT, data_path=tmp_path / "missing.csv")

    manifest = pack["paper_baseline_suite_manifest"]
    table = pack["paper_tabular_baseline_table"]
    gate = pack["paper_publishability_gate"]

    assert manifest["status"] == "blocked"
    assert "p6_paysim_source_file_missing" in manifest["blocked_reason_codes"]
    assert manifest["headline_performance_claim_allowed"] is False
    assert any("tabular-baselines" in item for item in manifest["recovery_instructions"])
    assert table["rows"] == []
    assert gate["hard_performance_claims_allowed"] is False


def test_paper_track_p6_sync_writes_required_artifacts(tmp_path: Path) -> None:
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")
    output_dir = tmp_path / "reports"

    written = sync_paper_baseline_suite_pack(
        PROJECT_ROOT,
        data_path=data_path,
        output_dir=output_dir,
        budget_tier="smoke",
    )

    assert set(written) == set(PAPER_BASELINE_FILENAMES)
    for path in written.values():
        assert path.exists()
    manifest = json.loads((output_dir / "paper_baseline_suite_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ok"


def test_paper_track_p6_cli_exposes_machine_readable_surface(
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
            "tabular-baselines",
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
    assert payload["paper_tabular_baselines"]["executed_family_count"] >= 3
    assert (output_dir / "paper_publishability_gate.json").exists()


def test_paper_track_p6_committed_artifacts_block_headline_claims() -> None:
    for filename in PAPER_BASELINE_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_baseline_suite_manifest.json")
    table = _load_report("paper_tabular_baseline_table.json")
    feature_report = _load_report("paper_leakage_safe_feature_report.json")
    gate = _load_report("paper_publishability_gate.json")

    assert manifest["schema_version"] == "relaytic.paper_tabular_baseline_suite.v1"
    assert manifest["status"] in {"ok", "blocked"}
    assert manifest["hard_performance_claims_allowed"] is False
    assert table["headline_table_eligible"] is False
    assert feature_report["balance_fields_used"] is False
    assert gate["headline_performance_claim_allowed"] is False
    assert gate["paper_primary_claim_allowed"] is False

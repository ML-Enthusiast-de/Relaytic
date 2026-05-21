from __future__ import annotations

import json
from pathlib import Path

from relaytic.release_safety import (
    PAYSIM_BENCHMARK_FILENAMES,
    build_paysim_benchmark_pack,
    sync_paysim_benchmark_pack,
)
from tests.aml_workload_fixtures import write_paysim_like_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p4_runs_chronological_paysim_fixture(tmp_path: Path) -> None:
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")
    pack = build_paysim_benchmark_pack(tmp_path, data_path=data_path)

    manifest = pack["paysim_benchmark_manifest"]
    split = pack["paysim_temporal_split_report"]
    operating_points = pack["paysim_operating_point_table"]
    result_row = pack["paysim_paper_result_row"]

    assert manifest["schema_version"] == "relaytic.paysim_temporal_benchmark.v1"
    assert manifest["slice"] == "Paper Track P4"
    assert manifest["status"] == "ok"
    assert manifest["next_slice"] == "Paper Track P5"
    assert manifest["threshold_selection_surface"] == "validation_only"
    assert manifest["paper_primary_claim_allowed"] is False
    assert manifest["hard_performance_claims_allowed"] is False

    assert split["status"] == "ok"
    assert split["chronological_order_ok"] is True
    assert split["class_coverage_ok"] is True
    assert split["forbidden_feature_check_passed"] is True
    assert "oldbalanceOrg" not in split["model_feature_columns"]
    assert "nameOrig" not in split["model_feature_columns"]

    selected = operating_points["selected_operating_point"]
    assert selected["selection_surface"] == "validation_only"
    assert selected["test_threshold_policy"] == "fixed_from_validation"
    assert selected["validation_threshold"] is not None
    assert 0.0 <= selected["test"]["precision_at_k"] <= 1.0
    assert 0.0 <= selected["test"]["recall_at_review_budget"] <= 1.0
    assert operating_points["fixed_fpr"]["target_fpr"] == 0.001

    assert result_row["status"] == "ok"
    assert result_row["claim_posture"] == "supporting-only"
    assert result_row["supporting_public_claim_allowed"] is False
    assert result_row["paper_primary_claim_allowed"] is False
    assert result_row["hard_performance_claims_allowed"] is False
    assert result_row["metrics"]["test_pr_auc"] is not None


def test_paper_track_p4_missing_source_blocks_without_claims(tmp_path: Path) -> None:
    pack = build_paysim_benchmark_pack(tmp_path, data_path=tmp_path / "missing.csv")

    manifest = pack["paysim_benchmark_manifest"]
    result_row = pack["paysim_paper_result_row"]

    assert manifest["status"] == "blocked"
    assert "paysim_source_file_missing" in manifest["blocked_reason_codes"]
    assert manifest["paper_primary_claim_allowed"] is False
    assert manifest["hard_performance_claims_allowed"] is False
    assert result_row["status"] == "blocked"
    assert result_row["supporting_public_claim_allowed"] is False
    assert result_row["paper_primary_claim_allowed"] is False


def test_paper_track_p4_sync_writes_required_artifacts(tmp_path: Path) -> None:
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")
    output_dir = tmp_path / "reports"

    written = sync_paysim_benchmark_pack(tmp_path, data_path=data_path, output_dir=output_dir)

    assert set(written) == set(PAYSIM_BENCHMARK_FILENAMES)
    for path in written.values():
        assert path.exists()
    manifest = json.loads((output_dir / "paysim_benchmark_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ok"


def test_paper_track_p4_committed_artifacts_have_supporting_claim_posture() -> None:
    for filename in PAYSIM_BENCHMARK_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paysim_benchmark_manifest.json")
    split = _load_report("paysim_temporal_split_report.json")
    operating_points = _load_report("paysim_operating_point_table.json")
    row = _load_report("paysim_paper_result_row.json")

    assert manifest["schema_version"] == "relaytic.paysim_temporal_benchmark.v1"
    assert manifest["status"] in {"ok", "blocked"}
    assert manifest["hard_performance_claims_allowed"] is False
    assert split["split_contract_id"] == "split_paysim_chronological_step_v1"
    assert operating_points["status"] in {"ok", "blocked"}
    assert row["claim_posture"] == "supporting-only"
    assert row["paper_primary_claim_allowed"] is False
    assert row["hard_performance_claims_allowed"] is False

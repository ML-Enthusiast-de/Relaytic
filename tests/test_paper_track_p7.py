from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_GRAPH_FILENAMES,
    build_paper_graph_baseline_pack,
    sync_paper_graph_baseline_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _write_elliptic_snapshot_fixture(root: Path) -> Path:
    data_dir = root / "elliptic_snapshot_fixture"
    data_dir.mkdir(parents=True, exist_ok=True)
    feature_rows: list[str] = []
    class_rows = ["txId,class"]
    edge_rows = ["txId1,txId2"]
    for time_step in range(1, 7):
        txids = [f"t{time_step}_{suffix}" for suffix in ["bad", "good", "neighbor", "unknown"]]
        labels = ["1", "2", "2", "unknown"]
        for index, (txid, label) in enumerate(zip(txids, labels), start=1):
            fraud_signal = 0.95 if label == "1" else 0.05
            feature_rows.append(f"{txid},{time_step},{fraud_signal:.2f},{index / 10:.2f},{time_step / 10:.2f}")
            class_rows.append(f"{txid},{label}")
        edge_rows.extend(
            [
                f"{txids[0]},{txids[2]}",
                f"{txids[2]},{txids[0]}",
                f"{txids[1]},{txids[3]}",
            ]
        )
    (data_dir / "elliptic_txs_features.csv").write_text("\n".join(feature_rows) + "\n", encoding="utf-8")
    (data_dir / "elliptic_txs_classes.csv").write_text("\n".join(class_rows) + "\n", encoding="utf-8")
    (data_dir / "elliptic_txs_edgelist.csv").write_text("\n".join(edge_rows) + "\n", encoding="utf-8")
    return data_dir


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p7_runs_same_snapshot_graph_baseline_fixture(tmp_path: Path) -> None:
    data_dir = _write_elliptic_snapshot_fixture(tmp_path)

    pack = build_paper_graph_baseline_pack(PROJECT_ROOT, data_dir=data_dir, budget_tier="smoke")

    manifest = pack["paper_graph_baseline_manifest"]
    table = pack["paper_graph_feature_table"]
    scorecard = pack["paper_graph_model_shadow_scorecard"]
    budget = pack["paper_graph_budget_contract"]
    gate = pack["paper_graph_publishability_gate"]

    assert manifest["schema_version"] == "relaytic.paper_graph_baseline_suite.v1"
    assert manifest["slice"] == "Paper Track P7"
    assert manifest["status"] == "ok"
    assert manifest["effective_budget_tier"] == "smoke"
    assert manifest["same_step_edge_count"] == 18
    assert manifest["excluded_cross_step_edge_count"] == 0
    assert len(manifest["source_files"]) == 3
    assert all(item["sha256"] for item in manifest["source_files"])
    assert manifest["runtime_environment"]["python"]
    assert manifest["next_slice"] == "Paper Track P8"

    assert table["evaluation_protocol"] == "time_step_batch_snapshot_inductive_evaluation"
    assert table["predeclared_structural_floor"]["test_evaluated"] is True
    assert table["validation_selected_competitive_baseline"]["test_pr_auc"] is not None
    assert budget["test_evaluation_policy"] == "predeclared_structural_floor_plus_one_validation_selected_winner_per_predeclared_feature_view"
    assert len(table["validation_selected_view_rows"]) >= 3
    assert scorecard["graph_model_execution_state"] in {"eligible_not_run", "fallback"}
    assert gate["supporting_graph_table_candidate_allowed"] is False
    assert gate["headline_graph_claim_allowed"] is False


def test_paper_track_p7_missing_source_blocks_claims(tmp_path: Path) -> None:
    pack = build_paper_graph_baseline_pack(PROJECT_ROOT, data_dir=tmp_path / "missing")

    manifest = pack["paper_graph_baseline_manifest"]
    gate = pack["paper_graph_publishability_gate"]

    assert manifest["status"] == "blocked"
    assert "p7_elliptic_provenance_or_split_not_ready" in manifest["blocked_reason_codes"]
    assert any("graph-baselines" in item for item in manifest["recovery_instructions"])
    assert gate["supporting_graph_table_candidate_allowed"] is False
    assert gate["graph_neural_model_claim_allowed"] is False


def test_paper_track_p7_sync_writes_required_artifacts(tmp_path: Path) -> None:
    data_dir = _write_elliptic_snapshot_fixture(tmp_path)
    output_dir = tmp_path / "reports"

    written = sync_paper_graph_baseline_pack(
        PROJECT_ROOT,
        data_dir=data_dir,
        output_dir=output_dir,
        budget_tier="smoke",
    )

    assert set(written) == set(PAPER_GRAPH_FILENAMES)
    assert all(path.exists() for path in written.values())
    manifest = json.loads((output_dir / "paper_graph_baseline_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ok"


def test_paper_track_p7_cli_exposes_machine_readable_surface(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: Any,
) -> None:
    data_dir = _write_elliptic_snapshot_fixture(tmp_path)
    output_dir = tmp_path / "cli_reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "graph-baselines",
            "--data-dir",
            str(data_dir),
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
    assert payload["paper_graph_baselines"]["next_slice"] == "Paper Track P8"
    assert (output_dir / "paper_graph_publishability_gate.json").exists()


def test_paper_track_p7_committed_artifacts_keep_graph_claims_separate() -> None:
    for filename in PAPER_GRAPH_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_graph_baseline_manifest.json")
    table = _load_report("paper_graph_feature_table.json")
    scorecard = _load_report("paper_graph_model_shadow_scorecard.json")
    gate = _load_report("paper_graph_publishability_gate.json")

    assert manifest["schema_version"] == "relaytic.paper_graph_baseline_suite.v1"
    assert manifest["effective_budget_tier"] == "competitive"
    assert manifest["excluded_cross_step_edge_count"] == 0
    assert len(manifest["source_files"]) == 3
    assert all(item["sha256"] for item in manifest["source_files"])
    assert table["validation_selected_competitive_baseline"]["test_pr_auc"] is not None
    assert scorecard["graph_neural_claim_allowed"] is False
    assert gate["headline_graph_claim_allowed"] is False
    assert gate["graph_sota_claim_allowed"] is False
    assert gate["hard_performance_claims_allowed"] is False

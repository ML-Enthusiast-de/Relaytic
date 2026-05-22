from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.release_safety import (
    ELLIPTIC_GRAPH_FILENAMES,
    build_elliptic_graph_pack,
    sync_elliptic_graph_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def _write_elliptic_raw_fixture(root: Path) -> Path:
    data_dir = root / "elliptic_fixture"
    data_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        ("a1", 1, "1"),
        ("a2", 1, "2"),
        ("a3", 2, "unknown"),
        ("a4", 3, "2"),
        ("b1", 4, "1"),
        ("b2", 4, "2"),
        ("c1", 5, "1"),
        ("c2", 5, "2"),
        ("c3", 6, "unknown"),
    ]
    features = [
        f"{txid},{time_step},{index / 10:.1f},{index / 20:.2f}"
        for index, (txid, time_step, _) in enumerate(rows, start=1)
    ]
    (data_dir / "elliptic_txs_features.csv").write_text("\n".join(features) + "\n", encoding="utf-8")
    classes = ["txId,class", *(f"{txid},{label}" for txid, _, label in rows)]
    (data_dir / "elliptic_txs_classes.csv").write_text("\n".join(classes) + "\n", encoding="utf-8")
    edges = [
        "txId1,txId2",
        "a1,a2",
        "a2,a4",
        "a4,b1",
        "b1,b2",
        "b2,c1",
        "c1,c2",
        "a3,c3",
    ]
    (data_dir / "elliptic_txs_edgelist.csv").write_text("\n".join(edges) + "\n", encoding="utf-8")
    return data_dir


def test_paper_track_p5_builds_elliptic_graph_provenance_fixture(tmp_path: Path) -> None:
    data_dir = _write_elliptic_raw_fixture(tmp_path)

    pack = build_elliptic_graph_pack(PROJECT_ROOT, data_dir=data_dir)

    manifest = pack["elliptic_graph_loader_manifest"]
    provenance = pack["elliptic_graph_provenance_report"]
    split = pack["elliptic_temporal_split_report"]
    claim_scope = pack["elliptic_graph_claim_scope"]
    result_row = pack["elliptic_paper_result_row"]

    assert manifest["schema_version"] == "relaytic.elliptic_graph_provenance.v1"
    assert manifest["slice"] == "Paper Track P5"
    assert manifest["status"] == "ok"
    assert manifest["raw_graph_bundle_ready"] is True
    assert manifest["next_slice"] == "Paper Track P6"
    assert manifest["paper_primary_claim_allowed"] is False
    assert manifest["hard_performance_claims_allowed"] is False

    assert provenance["status"] == "ok"
    assert provenance["graph_input_mode"] == "raw_graph_bundle"
    assert provenance["graph_lineage"]["node_count"] == 9
    assert provenance["graph_lineage"]["edge_count"] == 7

    assert split["status"] == "ok"
    assert split["split_contract_id"] == "split_elliptic_temporal_step_v1"
    assert split["chronological_order_ok"] is True
    assert split["class_coverage_ok"] is True
    assert split["unique_time_step_count"] == 6
    assert split["unknown_label_count"] == 2
    assert "random_node_split_across_time" in split["forbidden_split_methods_avoided"]
    assert split["edge_report"]["future_to_train_leakage_prevented"] is True
    assert split["edge_report"]["cross_window_edge_count"] > 0

    assert claim_scope["claim_boundary_from_taxonomy"] == "supporting-only"
    assert claim_scope["raw_graph_loader_claim_allowed"] is True
    assert claim_scope["graph_benchmark_performance_claim_allowed"] is False
    assert claim_scope["graph_sota_claim_allowed"] is False
    assert claim_scope["hard_performance_claims_allowed"] is False

    assert result_row["status"] == "ok"
    assert result_row["claim_posture"] == "supporting-only"
    assert result_row["numeric_model_metrics_available"] is False
    assert result_row["publishable_performance_row_allowed"] is False
    assert result_row["paper_table_role"] == "graph_provenance_and_temporal_split_row"


def test_paper_track_p5_missing_source_blocks_with_recovery_instructions(tmp_path: Path) -> None:
    pack = build_elliptic_graph_pack(PROJECT_ROOT, data_dir=tmp_path / "missing")

    manifest = pack["elliptic_graph_loader_manifest"]
    claim_scope = pack["elliptic_graph_claim_scope"]
    result_row = pack["elliptic_paper_result_row"]

    assert manifest["status"] == "blocked"
    assert "elliptic_required_source_files_missing" in manifest["blocked_reason_codes"]
    assert manifest["raw_graph_loader_claim_allowed"] is False
    assert manifest["graph_sota_claim_allowed"] is False
    assert "elliptic_txs_features.csv" in manifest["missing_required_files"]
    assert any("relaytic release-safety elliptic-graph" in item for item in manifest["recovery_instructions"])
    assert claim_scope["raw_graph_loader_claim_allowed"] is False
    assert claim_scope["flattened_graph_proxy_claim_allowed"] is False
    assert result_row["paper_primary_claim_allowed"] is False
    assert result_row["publishable_performance_row_allowed"] is False


def test_paper_track_p5_sync_writes_required_artifacts(tmp_path: Path) -> None:
    data_dir = _write_elliptic_raw_fixture(tmp_path)
    output_dir = tmp_path / "reports"

    written = sync_elliptic_graph_pack(PROJECT_ROOT, data_dir=data_dir, output_dir=output_dir)

    assert set(written) == set(ELLIPTIC_GRAPH_FILENAMES)
    for path in written.values():
        assert path.exists()
    manifest = json.loads((output_dir / "elliptic_graph_loader_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ok"


def test_paper_track_p5_cli_writes_json_surface(tmp_path: Path, capsys: Any, monkeypatch: Any) -> None:
    data_dir = _write_elliptic_raw_fixture(tmp_path)
    output_dir = tmp_path / "cli_reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "elliptic-graph",
            "--data-dir",
            str(data_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["elliptic_graph"]["raw_graph_bundle_ready"] is True
    assert (output_dir / "elliptic_graph_claim_scope.json").exists()


def test_paper_track_p5_committed_artifacts_have_supporting_claim_posture() -> None:
    for filename in ELLIPTIC_GRAPH_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("elliptic_graph_loader_manifest.json")
    provenance = _load_report("elliptic_graph_provenance_report.json")
    split = _load_report("elliptic_temporal_split_report.json")
    claim_scope = _load_report("elliptic_graph_claim_scope.json")
    row = _load_report("elliptic_paper_result_row.json")

    assert manifest["schema_version"] == "relaytic.elliptic_graph_provenance.v1"
    assert manifest["status"] in {"ok", "blocked"}
    assert manifest["hard_performance_claims_allowed"] is False
    assert provenance["graph_input_mode"] == "raw_graph_bundle"
    assert split["split_contract_id"] == "split_elliptic_temporal_step_v1"
    assert claim_scope["claim_posture"] == "supporting-only"
    assert claim_scope["graph_sota_claim_allowed"] is False
    assert row["paper_primary_claim_allowed"] is False
    assert row["hard_performance_claims_allowed"] is False

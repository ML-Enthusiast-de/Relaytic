from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.aml import build_aml_graph_loader_artifacts
from relaytic.ui.cli import main


SLICE15V_ARTIFACTS = (
    "aml_graph_loader_manifest.json",
    "aml_graph_provenance_report.json",
    "aml_subgraph_task_manifest.json",
    "aml_graph_claim_scope.json",
    "aml_public_graph_benchmark_catalog.json",
)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_raw_elliptic_fixture(root: Path) -> Path:
    _write(
        root / "elliptic_txs_edgelist.csv",
        "\n".join(
            [
                "txId1,txId2",
                "tx_001,tx_002",
                "tx_002,tx_003",
                "tx_003,tx_004",
                "tx_004,tx_001",
            ]
        )
        + "\n",
    )
    _write(
        root / "elliptic_txs_features.csv",
        "\n".join(
            [
                "txId,time_step,feature_1,feature_2",
                "tx_001,1,0.4,0.1",
                "tx_002,1,0.5,0.2",
                "tx_003,2,0.9,0.3",
                "tx_004,2,0.7,0.4",
            ]
        )
        + "\n",
    )
    _write(
        root / "elliptic_txs_classes.csv",
        "\n".join(
            [
                "txId,class",
                "tx_001,1",
                "tx_002,unknown",
                "tx_003,2",
                "tx_004,1",
            ]
        )
        + "\n",
    )
    return root


def test_slice15v_raw_graph_loader_builds_provenance_claim_scope_and_catalog(tmp_path: Path) -> None:
    run_dir = tmp_path / "slice15v_unit"
    raw_dir = _write_raw_elliptic_fixture(tmp_path / "elliptic_raw_bundle")

    bundle = build_aml_graph_loader_artifacts(run_dir=run_dir, graph_path=raw_dir)

    manifest = bundle["aml_graph_loader_manifest"]
    provenance = bundle["aml_graph_provenance_report"]
    subgraph = bundle["aml_subgraph_task_manifest"]
    claim_scope = bundle["aml_graph_claim_scope"]
    catalog = bundle["aml_public_graph_benchmark_catalog"]
    rows = {row["benchmark_family"]: row for row in catalog["rows"]}

    assert manifest["status"] == "raw_graph_ready"
    assert manifest["graph_input_mode"] == "raw_graph_bundle"
    assert manifest["loader_can_construct_graph"] is True
    assert manifest["benchmark_label_provenance_ready"] is True
    assert {"edges", "features", "labels"}.issubset(set(manifest["present_roles"]))
    assert provenance["source_file_count"] == 3
    assert subgraph["status"] == "ego_subgraph_proxy_ready"
    assert claim_scope["raw_graph_loader_claim_allowed"] is True
    assert claim_scope["raw_graph_benchmark_claim_allowed"] is False
    assert "raw_graph_benchmark_not_run_or_not_claim_gated" in claim_scope["blocked_reason_codes"]
    assert rows["elliptic_style_raw_graph_aml"]["support_level"] == "supported"
    assert rows["elliptic2_style_subgraph_aml"]["support_level"] == "proxy"


def test_cli_slice15v_writes_raw_loader_existing_graph_and_manifest(
    tmp_path: Path,
    capsys: Any,
) -> None:
    run_dir = tmp_path / "slice15v_cli"
    run_dir.mkdir()
    raw_dir = _write_raw_elliptic_fixture(tmp_path / "elliptic_raw_bundle")

    assert main(
        [
            "aml",
            "graph-loader",
            "--run-dir",
            str(run_dir),
            "--graph-path",
            str(raw_dir),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["aml_graph_loader"]["status"] == "raw_graph_ready"
    assert payload["aml_graph_loader"]["benchmark_support_levels"]["elliptic_style_raw_graph_aml"] == "supported"
    assert payload["aml_graph_loader"]["graph_sota_claim_allowed"] is False

    for artifact_name in SLICE15V_ARTIFACTS:
        assert (run_dir / artifact_name).exists(), artifact_name

    graph_profile = _read_json(run_dir / "entity_graph_profile.json")
    assert graph_profile["status"] == "active"
    assert graph_profile["node_count"] >= 4
    assert graph_profile["edge_count"] >= 4

    manifest = _read_json(run_dir / "manifest.json")
    manifest_paths = {item["path"] for item in manifest["entries"]}
    for artifact_name in SLICE15V_ARTIFACTS:
        assert artifact_name in manifest_paths


def test_slice15v_incomplete_bundle_fails_safely(tmp_path: Path) -> None:
    run_dir = tmp_path / "slice15v_incomplete"
    raw_dir = tmp_path / "incomplete_elliptic_bundle"
    _write(raw_dir / "elliptic_txs_edgelist.csv", "txId1,txId2\ntx_001,tx_002\n")

    bundle = build_aml_graph_loader_artifacts(run_dir=run_dir, graph_path=raw_dir)
    manifest = bundle["aml_graph_loader_manifest"]
    catalog = bundle["aml_public_graph_benchmark_catalog"]

    assert manifest["status"] == "incomplete_graph_bundle"
    assert manifest["loader_can_construct_graph"] is False
    assert {"features", "labels", "time"}.issubset(set(manifest["missing_required_roles"]))
    assert manifest["recovery_instructions"]
    rows = {row["benchmark_family"]: row for row in catalog["rows"]}
    assert rows["elliptic_style_raw_graph_aml"]["support_level"] == "blocked"


def test_slice15v_flattened_graph_compatibility_is_proxy_labeled(tmp_path: Path) -> None:
    run_dir = tmp_path / "slice15v_flattened"
    data_path = _write(
        tmp_path / "elliptic_flattened.csv",
        "\n".join(
            [
                "src,dst,time_step,y,amount",
                "tx_001,tx_002,1,1,10.0",
                "tx_002,tx_003,2,0,20.0",
                "tx_003,tx_004,3,1,30.0",
            ]
        )
        + "\n",
    )

    bundle = build_aml_graph_loader_artifacts(run_dir=run_dir, data_path=data_path)
    manifest = bundle["aml_graph_loader_manifest"]
    claim_scope = bundle["aml_graph_claim_scope"]
    catalog = bundle["aml_public_graph_benchmark_catalog"]
    rows = {row["benchmark_family"]: row for row in catalog["rows"]}

    assert manifest["status"] == "flattened_graph_ready"
    assert manifest["graph_input_mode"] == "flattened_graph_snapshot"
    assert manifest["flattened_graph_ready"] is True
    assert manifest["raw_graph_bundle_ready"] is False
    assert claim_scope["flattened_graph_proxy_claim_allowed"] is True
    assert claim_scope["raw_graph_benchmark_claim_allowed"] is False
    assert rows["elliptic_style_flattened_graph_aml"]["support_level"] == "supported"
    assert rows["elliptic_style_raw_graph_aml"]["support_level"] == "blocked"

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest
import torch

import relaytic.release_safety.elliptic2_recovery as recovery
from relaytic.release_safety import ELLIPTIC2_RECOVERY_FILENAMES, build_elliptic2_recovery_pack
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_core_fixture(root: Path) -> Path:
    directory = root / "official_core"
    directory.mkdir(parents=True, exist_ok=True)
    components = pd.DataFrame(
        {"ccId": list(range(12)), "ccLabel": ["licit"] * 8 + ["suspicious"] * 4}
    )
    nodes = pd.DataFrame(
        {"clId": list(range(24)), "ccId": [value for value in range(12) for _ in range(2)]}
    )
    edges = pd.DataFrame(
        {
            "clId1": [value * 2 for value in range(12)],
            "clId2": [value * 2 + 1 for value in range(12)],
            "txId": list(range(12)),
        }
    )
    components.to_csv(directory / "connected_components.csv", index=False)
    nodes.to_csv(directory / "nodes.csv", index=False)
    edges.to_csv(directory / "edges.csv", index=False)
    return directory


def _write_revtrack_fixture(root: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    directory = root / "revtrack"
    raw_dir = directory / "data" / "elliptic" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for split in ["TRN", "VAL", "TST"]:
        for index in range(80):
            positive = int(index % 4 == 0)
            source = 0 if positive else 2
            receiver = 1 if positive else 3
            rows.append(
                {
                    "senders_mapped": [source],
                    "receivers_mapped": [receiver],
                    "senders_len": 1,
                    "source_len": 1,
                    "sink_len": 1,
                    "receivers_len": 1,
                    "labels": positive,
                    "split": split,
                }
            )
    data = pd.DataFrame(rows)
    data.to_pickle(raw_dir / "data_df.pkl")
    torch.save(torch.arange(4), raw_dir / "node_idx_map.pt")
    (raw_dir / "raw_emb.pt").write_bytes(b"official-asset-present-for-fixture")
    cache_path = raw_dir / "selected_emb_numpy.npy"
    np.save(
        cache_path,
        np.asarray([[5.0, 4.0], [4.0, 5.0], [-5.0, -4.0], [-4.0, -5.0]], dtype=np.float32),
    )
    provenance = {
        "status": "ok",
        "raw_source_size_bytes": (raw_dir / "raw_emb.pt").stat().st_size,
        "node_idx_sha256": _hash(raw_dir / "node_idx_map.pt"),
        "output_sha256": _hash(cache_path),
    }
    (raw_dir / "selected_emb_provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
    monkeypatch.setattr(recovery, "PINNED_REVTRACK_DATA_DF_SHA256", _hash(raw_dir / "data_df.pkl"))
    monkeypatch.setattr(recovery, "PINNED_REVTRACK_NODE_INDEX_SHA256", _hash(raw_dir / "node_idx_map.pt"))
    return directory


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p8a_audits_official_core_without_exposing_external_path(tmp_path: Path) -> None:
    core_dir = _write_core_fixture(tmp_path)

    pack = build_elliptic2_recovery_pack(PROJECT_ROOT, core_data_dir=core_dir, revtrack_dir=tmp_path / "missing")
    audit = pack["elliptic2_schema_overlap_audit"]
    gate = pack["elliptic2_recovery_gate"]

    assert audit["status"] == "core_ready"
    assert audit["subgraph_count"] == 12
    assert audit["nodes_in_multiple_components"] == 0
    assert audit["cross_component_edge_count"] == 0
    assert str(tmp_path) not in json.dumps(audit)
    assert audit["source_path"].startswith("<external-local-source>")
    assert gate["status"] == "blocked"
    assert gate["paper_performance_row_allowed"] is False


def test_paper_track_p8a_blocks_missing_or_malformed_core_source(tmp_path: Path) -> None:
    pack = build_elliptic2_recovery_pack(
        PROJECT_ROOT,
        core_data_dir=tmp_path / "missing",
        revtrack_dir=tmp_path / "missing_reference",
    )

    audit = pack["elliptic2_schema_overlap_audit"]
    assert audit["status"] == "blocked"
    assert "official_labeled_subgraph_core_missing" in audit["blocked_reason_codes"]


def test_paper_track_p8a_runs_pilot_only_on_pinned_modern_reference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    core_dir = _write_core_fixture(tmp_path)
    revtrack_dir = _write_revtrack_fixture(tmp_path, monkeypatch)

    pack = build_elliptic2_recovery_pack(
        PROJECT_ROOT,
        core_data_dir=core_dir,
        revtrack_dir=revtrack_dir,
        run_pilot=True,
    )
    modern = pack["elliptic2_modern_reference_contract"]
    pilot = pack["elliptic2_context_pilot_result"]
    gate = pack["elliptic2_recovery_gate"]

    assert modern["status"] == "ready_for_context_pilot"
    assert pilot["status"] == "pilot_complete"
    assert pilot["primary_pilot_result"]["test_pr_auc"] == pytest.approx(1.0)
    assert pilot["paper_table_candidate_allowed"] is False
    assert gate["status"] == "pass_pilot_only"
    assert gate["headline_or_sota_claim_allowed"] is False
    assert gate["mandatory_next_slice"].startswith("Paper Track P8-B")


def test_paper_track_p8a_cli_exposes_machine_readable_recovery_surface(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core_dir = _write_core_fixture(tmp_path)
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "elliptic2-recovery",
            "--core-data-dir",
            str(core_dir),
            "--revtrack-dir",
            str(tmp_path / "missing_reference"),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["elliptic2_recovery"]["mandatory_next_slice"].startswith("Paper Track P8-B")
    assert (output_dir / "elliptic2_protocol_audit.json").exists()


def test_paper_track_p8a_committed_reports_preserve_pilot_claim_boundary() -> None:
    for filename in ELLIPTIC2_RECOVERY_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    schema = _load_report("elliptic2_schema_overlap_audit.json")
    pilot = _load_report("elliptic2_context_pilot_result.json")
    gate = _load_report("elliptic2_recovery_gate.json")

    assert schema["subgraph_count"] == 121810
    assert schema["label_counts"]["suspicious"] == 2763
    assert pilot["status"] == "pilot_complete"
    assert pilot["primary_pilot_result"]["test_pr_auc"] > 0.9
    assert gate["status"] == "pass_pilot_only"
    assert gate["paper_performance_row_allowed"] is False

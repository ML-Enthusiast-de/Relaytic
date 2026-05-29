from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

import relaytic.release_safety.elliptic2_recovery as recovery
from relaytic.release_safety import (
    ELLIPTIC2_REFERENCE_PARITY_FILENAMES,
    build_elliptic2_reference_parity_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_fixture_root(root: Path, monkeypatch: pytest.MonkeyPatch, *, degenerate: bool = True) -> Path:
    torch = pytest.importorskip("torch")
    reports = root / "docs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "elliptic2_schema_overlap_audit.json").write_text(
        json.dumps(
            {
                "status": "core_ready",
                "subgraph_count": 30,
                "label_counts": {"licit": 24, "suspicious": 6},
                "subgraph_core_pilot_allowed": True,
            }
        ),
        encoding="utf-8",
    )
    (reports / "elliptic2_publishability_gate.json").write_text(
        json.dumps(
            {
                "slice": "Paper Track P8-B",
                "status": "pass_supporting_modern_context_only",
                "supporting_paper_row_allowed": True,
                "reference_parity_claim_allowed": False,
                "official_gap_to_published_revclassify_ds": -0.03,
            }
        ),
        encoding="utf-8",
    )
    (reports / "elliptic2_repeated_seed_scorecard.json").write_text(
        json.dumps(
            {
                "official_partition": {"test_pr_auc_mean": 0.94, "test_pr_auc_std": 0.001},
                "robustness_partition": {"test_pr_auc_mean": 0.92, "test_pr_auc_std": 0.002},
            }
        ),
        encoding="utf-8",
    )

    directory = root / "revtrack"
    raw_dir = directory / "data" / "elliptic" / "raw"
    config_dir = directory / "configurations" / "sweep" / "subgraph_classification" / "full_shot"
    raw_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "BP.yaml").write_text("program: main.py\n", encoding="utf-8")
    (config_dir / "DS.yaml").write_text("program: main.py\n", encoding="utf-8")

    rows: list[dict[str, object]] = []
    splits = ["TRN"] * 12 + ["VAL"] * 3 + ["TST"] * 3
    for index, split in enumerate(splits):
        positive = int(index % 5 == 0)
        if degenerate:
            sender, receiver = 100, 200 if index < len(splits) - 1 else 201
        else:
            sender, receiver = 1000 + index * 2, 1001 + index * 2
        rows.append(
            {
                "senders": {sender},
                "source": [5000 + index],
                "sink": [6000 + index],
                "receivers": {receiver},
                "subg": f"{split}{index}",
                "labels": positive,
                "senders_len": 1,
                "source_len": 1,
                "sink_len": 1,
                "receivers_len": 1,
                "node_ids": [sender, receiver],
                "split": split,
                "senders_mapped": [0],
                "receivers_mapped": [1],
                "node_ids_mapped": [0, 1],
                "edge_index_mapped": [[0, 1]],
                "edge_index": [[sender, receiver]],
            }
        )
    pd.DataFrame(rows).to_pickle(raw_dir / "data_df.pkl")
    torch.save(torch.arange(2), raw_dir / "node_idx_map.pt")
    (raw_dir / "raw_emb.pt").write_bytes(b"p8c-fixture-raw-embedding-placeholder")
    cache_path = raw_dir / "selected_emb_numpy.npy"
    np.save(cache_path, np.asarray([[1.0, 0.5], [0.5, 1.0]], dtype=np.float32))
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


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p8c_blocks_when_assets_are_missing(tmp_path: Path) -> None:
    pack = build_elliptic2_reference_parity_pack(tmp_path, revtrack_dir=tmp_path / "missing", run_neural=True)

    gate = pack["elliptic2_reference_parity_gate"]
    split = pack["elliptic2_entity_disjoint_split_report"]

    assert gate["status"] == "blocked_supporting_only_thesis_narrowing_required"
    assert gate["reference_parity_claim_allowed"] is False
    assert gate["headline_or_sota_claim_allowed"] is False
    assert split["strict_entity_disjoint_split_viable"] is False


def test_paper_track_p8c_reconciles_and_blocks_degenerate_entity_split(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    revtrack_dir = _write_fixture_root(tmp_path, monkeypatch, degenerate=True)

    pack = build_elliptic2_reference_parity_pack(tmp_path, revtrack_dir=revtrack_dir, run_neural=True)
    contract = pack["elliptic2_neural_reference_parity_contract"]
    cohort = pack["elliptic2_evaluable_cohort_reconciliation"]
    split = pack["elliptic2_entity_disjoint_split_report"]
    neural = pack["elliptic2_neural_candidate_scorecard"]
    gate = pack["elliptic2_reference_parity_gate"]

    assert contract["reference_repository"]["classification_checkpoint_count"] == 0
    assert contract["faithful_neural_execution_preconditions_met"] is False
    assert cohort["revtrack_evaluable_row_count"] == 18
    assert cohort["official_core_subgraph_count"] == 30
    assert cohort["full_core_equivalence_proven"] is False
    assert split["strict_entity_disjoint_split_viable"] is False
    assert split["strict_component_protocol"]["all_role_entity_components"]["largest_component_row_fraction"] > 0.8
    assert neural["run_neural_requested"] is True
    assert gate["supporting_modern_context_row_allowed"] is True
    assert gate["reference_parity_claim_allowed"] is False
    assert gate["next_slice"].startswith("Paper Track P8-D")


def test_paper_track_p8c_default_cli_preview_does_not_write_canonical_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = main(["release-safety", "elliptic2-reference-parity", "--format", "json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert "artifacts" in payload["output_dir"]
    assert (
        tmp_path
        / "artifacts"
        / "release_safety"
        / "elliptic2_reference_parity_preview"
        / "elliptic2_reference_parity_gate.json"
    ).exists()
    assert not (tmp_path / "docs" / "reports" / "elliptic2_reference_parity_gate.json").exists()


def test_paper_track_p8c_committed_reports_remain_fail_closed() -> None:
    for filename in ELLIPTIC2_REFERENCE_PARITY_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    contract = _load_report("elliptic2_neural_reference_parity_contract.json")
    cohort = _load_report("elliptic2_evaluable_cohort_reconciliation.json")
    split = _load_report("elliptic2_entity_disjoint_split_report.json")
    neural = _load_report("elliptic2_neural_candidate_scorecard.json")
    gate = _load_report("elliptic2_reference_parity_gate.json")

    assert contract["faithful_execution_budget_contract"]["local_run_requested"] is True
    assert contract["faithful_neural_execution_preconditions_met"] is False
    assert contract["reference_repository"]["classification_checkpoint_count"] == 0
    assert cohort["revtrack_evaluable_row_count"] == 110902
    assert cohort["official_core_subgraph_count"] == 121810
    assert cohort["full_core_equivalence_proven"] is False
    assert split["strict_entity_disjoint_split_viable"] is False
    assert split["strict_component_protocol"]["all_role_entity_components"]["largest_component_row_count"] == 110889
    assert neural["p8b_supporting_context_baseline"]["official_test_pr_auc_mean"] == pytest.approx(0.94324)
    assert gate["supporting_modern_context_row_allowed"] is True
    assert gate["reference_parity_claim_allowed"] is False
    assert gate["headline_or_sota_claim_allowed"] is False
    assert gate["p9_allowed"] is False
    assert gate["next_slice"].startswith("Paper Track P8-D")

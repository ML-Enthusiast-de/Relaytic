from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

import relaytic.release_safety.elliptic2_competitive as competitive
import relaytic.release_safety.elliptic2_recovery as recovery
from relaytic.release_safety import ELLIPTIC2_COMPETITIVE_FILENAMES, build_elliptic2_competitive_pack
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_revtrack_fixture(root: Path, monkeypatch: pytest.MonkeyPatch, rows_per_split: int = 80) -> Path:
    torch = pytest.importorskip("torch")
    directory = root / "revtrack"
    raw_dir = directory / "data" / "elliptic" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    next_node_id = 1000
    for split in ["TRN", "VAL", "TST"]:
        for index in range(rows_per_split):
            positive = int(index % 4 == 0)
            mapped_sender, mapped_receiver = (0, 1) if positive else (2, 3)
            sender, receiver = next_node_id, next_node_id + 1
            next_node_id += 2
            rows.append(
                {
                    "senders": [sender],
                    "source": [sender],
                    "sink": [receiver],
                    "receivers": [receiver],
                    "subg": f"{split}{index}",
                    "labels": positive,
                    "senders_len": 1,
                    "source_len": 1,
                    "sink_len": 1,
                    "receivers_len": 1,
                    "node_ids": [sender, receiver],
                    "split": split,
                    "senders_mapped": [mapped_sender],
                    "receivers_mapped": [mapped_receiver],
                    "node_ids_mapped": [mapped_sender, mapped_receiver],
                    "edge_index_mapped": [[mapped_sender, mapped_receiver]],
                    "edge_index": [[sender, receiver]],
                }
            )
    pd.DataFrame(rows).to_pickle(raw_dir / "data_df.pkl")
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
    short_config = {
        **competitive._BASE_CONFIG,
        "n_estimators": 25,
        "early_stopping_rounds": 5,
        "num_leaves": 7,
    }
    monkeypatch.setattr(
        competitive,
        "ELLIPTIC2_CANDIDATE_SPECS",
        [
            {
                "candidate_id": "fixture_context_lgbm",
                "feature_view_id": "pooled_mean_max_counts",
                "feature_contract": "fixture",
                "configuration": short_config,
            }
        ],
    )
    return directory


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p8b_blocks_when_execution_or_assets_are_missing(tmp_path: Path) -> None:
    pack = build_elliptic2_competitive_pack(PROJECT_ROOT, revtrack_dir=tmp_path / "missing")

    gate = pack["elliptic2_publishability_gate"]
    reference = pack["elliptic2_revclassify_reference_scorecard"]

    assert gate["status"] == "blocked"
    assert gate["supporting_paper_row_allowed"] is False
    assert gate["headline_or_sota_claim_allowed"] is False
    assert reference["reference"]["RevClassify_DS"]["pr_auc"] == pytest.approx(0.974)


def test_paper_track_p8b_smoke_runs_validation_selection_and_hash_split(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    revtrack_dir = _write_revtrack_fixture(tmp_path, monkeypatch)

    pack = build_elliptic2_competitive_pack(
        PROJECT_ROOT,
        revtrack_dir=revtrack_dir,
        budget_tier="smoke",
        run_suite=True,
    )
    trace = pack["elliptic2_relaytic_candidate_search_trace"]
    repeated = pack["elliptic2_repeated_seed_scorecard"]
    robustness = pack["elliptic2_split_robustness_report"]
    gate = pack["elliptic2_publishability_gate"]

    assert trace["status"] == "candidate_search_complete"
    assert trace["prior_test_exposure_disclosed"] is True
    assert trace["validation_selected_candidate"]["test_pr_auc"] == pytest.approx(1.0)
    assert repeated["official_partition"]["seed_count"] == 1
    assert robustness["robustness_partition"]["row_order_independent"] is True
    assert gate["supporting_paper_row_allowed"] is False
    assert "competitive_budget_executed" in gate["blocked_reason_codes"]


def test_paper_track_p8b_gate_can_promote_only_a_repeated_robust_supporting_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    revtrack_dir = _write_revtrack_fixture(tmp_path, monkeypatch, rows_per_split=400)
    monkeypatch.setattr(competitive, "ELLIPTIC2_SEEDS", [1, 2, 3])

    pack = build_elliptic2_competitive_pack(
        PROJECT_ROOT,
        revtrack_dir=revtrack_dir,
        budget_tier="competitive",
        run_suite=True,
    )
    gate = pack["elliptic2_publishability_gate"]

    assert gate["status"] == "pass_supporting_modern_context_only"
    assert gate["supporting_paper_row_allowed"] is True
    assert gate["reference_parity_claim_allowed"] is True
    assert gate["headline_or_sota_claim_allowed"] is False
    assert gate["p9_allowed"] is True


def test_paper_track_p8b_cli_exposes_machine_readable_gate(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    revtrack_dir = _write_revtrack_fixture(tmp_path, monkeypatch)
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "elliptic2-competitive",
            "--revtrack-dir",
            str(revtrack_dir),
            "--output-dir",
            str(output_dir),
            "--run-suite",
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["elliptic2_competitive"]["headline_or_sota_claim_allowed"] is False
    assert (output_dir / "elliptic2_split_robustness_report.json").exists()


def test_paper_track_p8b_default_cli_preview_does_not_write_canonical_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = main(["release-safety", "elliptic2-competitive", "--format", "json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert "artifacts" in payload["output_dir"]
    assert (tmp_path / "artifacts" / "release_safety" / "elliptic2_competitive_preview" / "elliptic2_publishability_gate.json").exists()
    assert not (tmp_path / "docs" / "reports" / "elliptic2_publishability_gate.json").exists()


def test_paper_track_p8b_committed_reports_remain_claim_gated() -> None:
    for filename in ELLIPTIC2_COMPETITIVE_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    reference = _load_report("elliptic2_revclassify_reference_scorecard.json")
    repeated = _load_report("elliptic2_repeated_seed_scorecard.json")
    robustness = _load_report("elliptic2_split_robustness_report.json")
    gate = _load_report("elliptic2_publishability_gate.json")

    assert reference["reference"]["RevClassify_DS"]["pr_auc"] == pytest.approx(0.974)
    assert reference["cohort_coverage"]["revtrack_evaluable_row_count"] == 110902
    assert reference["cohort_coverage"]["cohort_equivalence_proven"] is False
    assert repeated["official_partition"]["test_pr_auc_mean"] > 0.94
    assert repeated["robustness_partition"]["test_pr_auc_mean"] > 0.92
    assert robustness["robustness_partition"]["row_order_independent"] is True
    assert gate["supporting_paper_row_allowed"] is True
    assert gate["reference_parity_claim_allowed"] is False
    assert gate["headline_or_sota_claim_allowed"] is False
    assert gate["end_to_end_relaytic_superiority_claim_allowed"] is False
    assert gate["next_slice"].startswith("Paper Track P8-C")

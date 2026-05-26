from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_HARD_GRAPH_FILENAMES,
    build_paper_hard_graph_track_pack,
    sync_paper_hard_graph_track_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_amlsim_proxy_fixture(root: Path) -> Path:
    data_dir = root / "amlsim_fixture"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "conf.json").write_text('{"seed": 42, "simulation": "fixture"}\n', encoding="utf-8")
    (data_dir / "tx_log.csv").write_text(
        "timestamp,src,dst,amount\n1,a,b,10\n2,b,c,20\n",
        encoding="utf-8",
    )
    (data_dir / "alert_transactions.csv").write_text(
        "timestamp,alert_type,is_sar\n1,layering,1\n2,smurfing,1\n3,layering,1\n",
        encoding="utf-8",
    )
    (data_dir / "sar_accounts.csv").write_text("account_id\nb\nc\n", encoding="utf-8")
    (data_dir / "generator_commit.txt").write_text("abc123fixture\n", encoding="utf-8")
    generation = {
        "generator_commit": "abc123fixture",
        "random_seed": 42,
        "generated_data_license": "local_research_proxy_only",
        "config_sha256": _hash(data_dir / "conf.json"),
        "output_sha256": {
            filename: _hash(data_dir / filename)
            for filename in ["tx_log.csv", "alert_transactions.csv", "sar_accounts.csv"]
        },
    }
    (data_dir / "generated_dataset_manifest.json").write_text(
        json.dumps(generation, indent=2),
        encoding="utf-8",
    )
    return data_dir


def _write_elliptic2_file_presence_fixture(root: Path) -> Path:
    data_dir = root / "elliptic2_fixture"
    data_dir.mkdir(parents=True, exist_ok=True)
    for filename in [
        "background_edges.csv",
        "background_nodes.csv",
        "connected_components.csv",
        "edges.csv",
        "nodes.csv",
    ]:
        (data_dir / filename).write_text("id,value\n1,fixture\n", encoding="utf-8")
    return data_dir


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p8_blocks_missing_hard_sources_with_exact_actions(tmp_path: Path) -> None:
    pack = build_paper_hard_graph_track_pack(
        PROJECT_ROOT,
        elliptic2_dir=tmp_path / "missing_elliptic2",
        amlsim_dir=tmp_path / "missing_amlsim",
    )

    generation = pack["amlsim_generation_manifest"]
    access = pack["elliptic2_subgraph_access_report"]
    report = pack["subgraph_benchmark_blocker_report"]

    assert set(pack) == set(PAPER_HARD_GRAPH_FILENAMES)
    assert generation["support_level"] == "blocked"
    assert "amlsim_local_generated_bundle_missing" in generation["blocked_reason_codes"]
    assert access["support_level"] == "blocked"
    assert "elliptic2_local_source_missing" in access["blocked_reason_codes"]
    assert report["blocked_track_count"] == 2
    assert report["proxy_track_count"] == 0
    assert report["paper_can_continue_to_p9"] is False
    assert report["hard_performance_claims_allowed"] is False
    assert report["next_slice"].startswith("Paper Track P8-B")


def test_paper_track_p8_accepts_audited_amlsim_only_as_proxy(tmp_path: Path) -> None:
    amlsim_dir = _write_amlsim_proxy_fixture(tmp_path)

    pack = build_paper_hard_graph_track_pack(
        PROJECT_ROOT,
        elliptic2_dir=tmp_path / "missing_elliptic2",
        amlsim_dir=amlsim_dir,
    )

    generation = pack["amlsim_generation_manifest"]
    typology = pack["amlsim_typology_manifest"]
    report = pack["subgraph_benchmark_blocker_report"]

    assert generation["status"] == "proxy_ready"
    assert generation["support_level"] == "proxy"
    assert generation["public_performance_claim_allowed"] is False
    assert typology["support_level"] == "proxy"
    assert typology["typology_distribution"] == {"layering": 2, "smurfing": 1}
    assert report["proxy_track_count"] == 1
    assert report["blocked_track_count"] == 1
    assert report["track_decisions"][1]["first_paper_inclusion_decision"] == "supplementary_proxy_candidate"
    assert report["hard_performance_claims_allowed"] is False


def test_paper_track_p8_does_not_equate_elliptic2_files_with_benchmark_support(tmp_path: Path) -> None:
    elliptic2_dir = _write_elliptic2_file_presence_fixture(tmp_path)

    pack = build_paper_hard_graph_track_pack(
        PROJECT_ROOT,
        elliptic2_dir=elliptic2_dir,
        amlsim_dir=tmp_path / "missing_amlsim",
    )
    access = pack["elliptic2_subgraph_access_report"]

    assert access["local_source_ready"] is True
    assert access["access_state"] == "source_present_requires_loader_split_resource_proof"
    assert access["support_level"] == "blocked"
    assert "elliptic2_official_loader_not_validated" in access["blocked_reason_codes"]
    assert "elliptic2_split_and_overlap_audit_not_run" in access["blocked_reason_codes"]
    assert "elliptic2_resource_budget_not_frozen" in access["blocked_reason_codes"]


def test_paper_track_p8_sync_writes_required_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports"

    written = sync_paper_hard_graph_track_pack(
        PROJECT_ROOT,
        elliptic2_dir=tmp_path / "missing_elliptic2",
        amlsim_dir=tmp_path / "missing_amlsim",
        output_dir=output_dir,
    )

    assert set(written) == set(PAPER_HARD_GRAPH_FILENAMES)
    assert all(path.exists() for path in written.values())
    report = json.loads((output_dir / "subgraph_benchmark_blocker_report.json").read_text(encoding="utf-8"))
    assert report["decision_state"] == "hard_tracks_blocked_with_elliptic2_pilot_recovery_recorded"


def test_paper_track_p8_cli_exposes_machine_readable_surface(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: Any,
) -> None:
    output_dir = tmp_path / "cli_reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "hard-graph-tracks",
            "--elliptic2-dir",
            str(tmp_path / "missing_elliptic2"),
            "--amlsim-dir",
            str(tmp_path / "missing_amlsim"),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["paper_hard_graph_tracks"]["next_slice"].startswith("Paper Track P8-B")
    assert (output_dir / "elliptic2_subgraph_access_report.json").exists()


def test_paper_track_p8_committed_artifacts_keep_absent_hard_tracks_out_of_claims() -> None:
    for filename in PAPER_HARD_GRAPH_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    generation = _load_report("amlsim_generation_manifest.json")
    access = _load_report("elliptic2_subgraph_access_report.json")
    report = _load_report("subgraph_benchmark_blocker_report.json")

    assert generation["support_level"] == "blocked"
    assert access["support_level"] == "blocked"
    assert report["blocked_track_count"] == 2
    assert report["headline_or_sota_claim_allowed"] is False
    assert report["p7_context"]["supporting_graph_table_candidate_allowed"] is True
    assert report["subsequent_elliptic2_recovery"]["status"] == "pass_pilot_only"
    assert report["paper_can_continue_to_p9"] is False
    assert report["next_slice"].startswith("Paper Track P8-B")

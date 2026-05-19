from __future__ import annotations

import json
from pathlib import Path

import pytest

from relaytic.release_safety import PAPER_FREEZE_FILENAMES, build_paper_freeze_pack
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def _load_json_report(key: str) -> dict[str, object]:
    path = REPORT_DIR / PAPER_FREEZE_FILENAMES[key]
    return json.loads(path.read_text(encoding="utf-8"))


def test_slice15zr_release_freeze_reports_exist_and_manifest_accepts() -> None:
    for filename in PAPER_FREEZE_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    pack = build_paper_freeze_pack(PROJECT_ROOT)
    assert set(pack) == set(PAPER_FREEZE_FILENAMES)

    manifest = _load_json_report("paper_release_freeze_manifest")
    acceptance = dict(manifest["acceptance_status"])
    assert acceptance["result_table_multidimensional"] is True
    assert acceptance["claim_boundaries_complete"] is True
    assert acceptance["reproducibility_attestation_complete"] is True
    assert acceptance["rerun_contract_present"] is True
    assert manifest["hard_performance_claims_allowed"] is False


def test_slice15zr_relevant_benchmark_catalog_covers_required_tracks() -> None:
    catalog = _load_json_report("aml_relevant_benchmark_catalog")
    tracks = [dict(item) for item in catalog["tracks"]]  # type: ignore[index]
    by_type = {str(item["track_type"]): item for item in tracks}
    labels = {str(item["label"]) for item in tracks}

    assert "transaction_fraud_temporal" in by_type
    assert "graph_aml" in by_type
    assert {"subgraph_aml", "synthetic_bank_graph_aml"} & set(by_type)
    assert "generic_supporting_structured_data" in by_type
    assert labels <= {"dev", "holdout", "paper", "proxy", "blocked"}
    assert by_type["transaction_fraud_temporal"]["label"] == "proxy"
    assert by_type["graph_aml"]["label"] == "proxy"
    assert by_type["generic_supporting_structured_data"]["label"] == "dev"


def test_slice15zr_result_table_is_not_metric_only() -> None:
    result_table = _load_json_report("paper_result_table")
    rows = [dict(item) for item in result_table["rows"]]  # type: ignore[index]
    required = {
        "model_metrics",
        "operational_metrics",
        "ablation_posture",
        "environment_score",
        "public_claim_status",
    }

    assert rows
    for row in rows:
        assert required <= set(row), row["track_id"]
        assert isinstance(row["model_metrics"], dict)
        assert isinstance(row["operational_metrics"], dict)
        assert isinstance(row["ablation_posture"], dict)
        assert isinstance(row["environment_score"], dict)
        assert row["public_claim_status"] in {"supporting-only", "blocked"}
    assert any(row["public_claim_status"] == "blocked" for row in rows)


def test_slice15zr_claim_boundaries_cite_artifacts_and_block_overclaim() -> None:
    claim_report = _load_json_report("paper_claim_boundary_report")
    result_table = _load_json_report("paper_result_table")
    claims = {str(item["claim_id"]): dict(item) for item in claim_report["claims"]}  # type: ignore[index]
    row_claim_refs = {
        str(item["claim_boundary_ref"]).split("#", 1)[1]
        for item in result_table["rows"]  # type: ignore[index]
    }

    assert row_claim_refs <= set(claims)
    for claim_id, claim in claims.items():
        assert claim["boundary"] in {"hard", "supporting-only", "blocked"}, claim_id
        assert claim["artifact_paths"], claim_id
        assert claim["allowed_public_wording"], claim_id

    sota = claims["claim_sota_or_hard_aml_superiority"]
    assert sota["boundary"] == "blocked"
    assert "paper_result_table.json" in json.dumps(sota)


def test_slice15zr_reproducibility_attestation_records_rerun_contract() -> None:
    attestation = _load_json_report("reproducibility_attestation")
    commands = {str(item["command_id"]): dict(item) for item in attestation["commands"]}  # type: ignore[index]
    install = dict(attestation["install_profile"])  # type: ignore[arg-type]
    rerun = dict(attestation["rerun_policy"])  # type: ignore[arg-type]

    assert install["dependency_profile"] == ".[full]"
    assert {"3.10", "3.11"} <= set(install["python_versions"])
    assert "generate_release_freeze_pack" in commands
    assert commands["generate_release_freeze_pack"]["command"] == "relaytic release-safety paper-freeze --format json"
    assert "run_release_safety_scan" in commands
    assert attestation["dataset_source_posture"]
    assert dict(attestation["host_assumptions"])["tokens_or_api_keys_required"] is False  # type: ignore[arg-type]
    assert dict(attestation["runtime_budget"])["release_freeze_pack"] == "seconds"  # type: ignore[arg-type]
    assert rerun["reproduces_report_table_or_blocks"] is True
    assert "claim_gate_or_environment_gate_failed" in rerun["deterministic_blocked_rerun_reasons"]


def test_slice15zr_release_freeze_cli_smoke(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "paper_freeze"

    assert main(
        [
            "release-safety",
            "paper-freeze",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "frozen_supporting_release_pack"
    assert payload["paper_release_freeze"]["hard_performance_claims_allowed"] is False
    for filename in PAPER_FREEZE_FILENAMES.values():
        assert (output_dir / filename).exists(), filename

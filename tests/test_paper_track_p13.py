from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_FINAL_DRAFT_FILENAME,
    PAPER_REFERENCES_FILENAME,
    PAPER_RELEASE_FILENAMES,
    PAPER_RELEASE_TABLE_FILENAMES,
    PAPER_RELEASE_TABLE_MANIFEST_FILENAME,
    build_paper_release_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p13_builds_claim_safe_release_pack() -> None:
    pack = build_paper_release_pack(PROJECT_ROOT)

    manifest = pack["paper_release_manifest"]
    public_claims = pack["paper_public_claims_allowed"]
    draft = pack["paper_final_draft"]
    tables = pack["paper_tables"]
    references = pack["paper_references_bib"]

    assert manifest["status"] == "ready_for_claim_safe_arxiv_release"
    assert manifest["claim_safe_public_release_allowed"] is True
    assert manifest["arxiv_upload_ready"] is False
    assert manifest["submission_package_state"]["current_format"] == "claim_safe_markdown_draft_pack"
    assert manifest["next_slice"].startswith("Paper Track P14")
    assert manifest["hard_claims_allowed"] is False
    assert manifest["headline_claims_allowed"] is False
    assert manifest["release_tag_plan"]["tag"] == "relaytic-aml-paper-p13-claim-safe"
    assert public_claims["status"] == "claim_safe_public_wording_allowed"
    assert public_claims["wording_lint"]["status"] == "pass"
    assert "[@weber2019elliptic]" in draft
    assert "[@song2024revtrack]" in draft
    assert "[@chen2026transxion]" in draft
    assert "[@ye2026blazingaml]" in draft
    assert "operational anti-money laundering (AML)" in draft
    assert "PaySim synthetic temporal-fraud precision-recall area under the curve (PR-AUC) 0.638773" in draft
    assert "[@yang2026skillopt]" in draft
    assert "broad deployment superiority" in draft
    assert "SOTA" in "\n".join(public_claims["blocked_public_claims"])
    assert set(tables) == set(PAPER_RELEASE_TABLE_FILENAMES)
    assert "paper-cell:paysim_p6a_competitive_selected.test_pr_auc" in tables["evidence_summary"]
    assert "@misc{weber2019elliptic" in references
    assert "@misc{chen2026transxion" in references
    assert "@misc{deprez2025continualaml" in references
    assert "@misc{yang2026skillopt" in references
    assert any(item["citation_key"] == "song2024revtrack" for item in manifest["source_verification"])
    assert not manifest["failed_checks"]


def test_paper_track_p13_cli_writes_release_reports_and_paper_assets(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    paper_dir = tmp_path / "paper"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-release",
            "--paper-dir",
            str(paper_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_claim_safe_arxiv_release"
    assert payload["paper_public_claims_allowed"]["wording_lint"]["status"] == "pass"
    for filename in PAPER_RELEASE_FILENAMES.values():
        assert (output_dir / filename).exists(), filename
    assert (paper_dir / PAPER_FINAL_DRAFT_FILENAME).exists()
    assert (paper_dir / PAPER_REFERENCES_FILENAME).exists()
    assert (paper_dir / "tables" / PAPER_RELEASE_TABLE_MANIFEST_FILENAME).exists()
    for filename in PAPER_RELEASE_TABLE_FILENAMES.values():
        assert (paper_dir / "tables" / filename).exists(), filename


def test_paper_track_p13_fails_closed_without_gate_inputs(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "# Relaytic\n\n## Paper P13 Claim-Safe Release Status\n\nNo claims yet.\n",
        encoding="utf-8",
    )

    pack = build_paper_release_pack(tmp_path)
    manifest = pack["paper_release_manifest"]

    assert manifest["status"] == "blocked_pending_release_repairs"
    assert manifest["claim_safe_public_release_allowed"] is False
    assert any(check["check_id"] == "required_p13_inputs_present" and not check["passed"] for check in manifest["checks"])
    assert manifest["failed_checks"]


def test_paper_track_p13_committed_release_artifacts_are_ready() -> None:
    for filename in PAPER_RELEASE_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename
    assert (PAPER_DIR / PAPER_FINAL_DRAFT_FILENAME).exists()
    assert (PAPER_DIR / PAPER_REFERENCES_FILENAME).exists()
    assert (PAPER_DIR / "tables" / PAPER_RELEASE_TABLE_MANIFEST_FILENAME).exists()
    for filename in PAPER_RELEASE_TABLE_FILENAMES.values():
        assert (PAPER_DIR / "tables" / filename).exists(), filename

    manifest = _load_report("paper_release_manifest.json")
    claims = _load_report("paper_public_claims_allowed.json")
    draft = (PAPER_DIR / PAPER_FINAL_DRAFT_FILENAME).read_text(encoding="utf-8")
    attention = (REPORT_DIR / "paper_attention_pack.md").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_claim_safe_arxiv_release"
    assert manifest["claim_safe_public_release_allowed"] is True
    assert manifest["arxiv_upload_ready"] is False
    assert manifest["git_state_semantics"] == "generation_base_commit_not_manifest_self_hash"
    assert manifest["next_slice"].startswith("Paper Track P14")
    assert claims["status"] == "claim_safe_public_wording_allowed"
    assert claims["wording_lint"]["status"] == "pass"
    assert claims["hard_claims_allowed"] is False
    assert claims["headline_claims_allowed"] is False
    assert "Relaytic-AML: A Local-First Evaluation Lab" in draft
    assert "arXiv-ready draft" not in draft
    assert "## References" in draft
    assert "No SOTA or leaderboard-winner claim." in attention

    references = (PAPER_DIR / PAPER_REFERENCES_FILENAME).read_text(encoding="utf-8")
    cited_keys = set()
    for citation in re.findall(r"\[@([^\]]+)\]", draft):
        cited_keys.update(part.strip().lstrip("@") for part in citation.split(";"))
    bib_keys = set(re.findall(r"@\w+\{([^,\s]+)", references))
    assert cited_keys <= bib_keys

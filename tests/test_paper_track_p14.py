from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_ARXIV_MAIN_TEX_FILENAME,
    PAPER_ARXIV_REFERENCES_FILENAME,
    PAPER_ARXIV_SOURCE_DIRNAME,
    PAPER_ARXIV_SOURCE_FILENAMES,
    build_paper_arxiv_source_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
ARXIV_SOURCE_DIR = PAPER_DIR / PAPER_ARXIV_SOURCE_DIRNAME
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p14_builds_arxiv_source_release_candidate() -> None:
    pack = build_paper_arxiv_source_pack(PROJECT_ROOT)

    manifest = pack["paper_arxiv_source_manifest"]
    audit = pack["paper_submission_package_audit"]
    main_tex = pack["main_tex"]
    references = pack["references_bib"]
    figures = list(pack["pdf_figures"])

    assert manifest["status"] == "ready_for_source_release_candidate"
    assert manifest["source_release_candidate_ready"] is True
    assert manifest["arxiv_upload_ready"] is False
    assert manifest["arxiv_processor_contract"]["processor"] == "pdfLaTeX"
    assert manifest["arxiv_processor_contract"]["graphic_formats_used"] == [".pdf"]
    assert manifest["citation_audit"]["status"] == "pass"
    assert manifest["figure_audit"]["status"] == "pass"
    assert manifest["figure_audit"]["svg_references_remaining"] == []
    assert manifest["next_slice"].startswith("Paper Track P21")
    assert any(check["check_id"] == "p20_narrative_polish_passed" and check["passed"] for check in manifest["checks"])
    assert any(check["check_id"] == "p23_novelty_positioning_passed" and check["passed"] for check in manifest["checks"])
    assert "docs/reports/paper_novelty_positioning_manifest.json" in manifest["p23_novelty_refs"]
    assert not manifest["failed_checks"]

    assert audit["status"] == "pass"
    assert audit["violation_count"] == 0
    assert any(check["check_id"] == "author_and_pdf_metadata_present" and check["passed"] for check in audit["checks"])
    assert audit["upload_blockers_remaining"]
    assert "replace placeholder author" not in "\n".join(audit["upload_blockers_remaining"])
    assert "Tobias Gehra" in main_tex
    assert "t.gehra.ai@gmail.com" in main_tex
    assert "pdftitle=" in main_tex and "pdfauthor={Tobias Gehra}" in main_tex
    assert r"\begin{algorithm}" in main_tex
    assert ("TODO" + "_EVIDENCE") not in main_tex
    assert r"TODO\_EVIDENCE" not in main_tex
    assert "\\documentclass" in main_tex
    assert "\\bibliography{references}" in main_tex
    assert "\\includegraphics[width=\\linewidth]{figures/figure_1_claim_gate_flow.pdf}" in main_tex
    assert ".svg" not in main_tex
    assert "pending isolated" + " test" not in main_tex
    assert "This draft" not in main_tex
    assert "claim-safe Markdown draft" not in main_tex
    assert "@misc{weber2019elliptic" in references
    assert len(figures) == 4
    for figure in figures:
        payload = bytes.fromhex(str(figure["pdf_hex"]))
        assert payload.startswith(b"%PDF-1.4")
        assert figure["target_extension"] == ".pdf"


def test_paper_track_p14_cli_writes_source_reports_and_arxiv_tree(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    source_dir = tmp_path / "arxiv_src"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-arxiv-source",
            "--source-dir",
            str(source_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_source_release_candidate"
    assert payload["paper_submission_package_audit"]["status"] == "pass"
    for filename in PAPER_ARXIV_SOURCE_FILENAMES.values():
        assert (output_dir / filename).exists(), filename
    assert (source_dir / PAPER_ARXIV_MAIN_TEX_FILENAME).exists()
    assert (source_dir / PAPER_ARXIV_REFERENCES_FILENAME).exists()
    for figure_path in sorted((source_dir / "figures").glob("*.pdf")):
        assert figure_path.read_bytes().startswith(b"%PDF-1.4")
    assert len(list((source_dir / "figures").glob("*.pdf"))) == 4


def test_paper_track_p14_fails_closed_without_p13_inputs(tmp_path: Path) -> None:
    pack = build_paper_arxiv_source_pack(tmp_path)
    manifest = pack["paper_arxiv_source_manifest"]
    audit = pack["paper_submission_package_audit"]

    assert manifest["status"] == "blocked_pending_source_repairs"
    assert manifest["source_release_candidate_ready"] is False
    assert any(check["check_id"] == "required_p14_inputs_present" and not check["passed"] for check in manifest["checks"])
    assert audit["status"] == "fail"
    assert manifest["failed_checks"]


def test_paper_track_p14_committed_source_bundle_is_ready() -> None:
    for filename in PAPER_ARXIV_SOURCE_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename
    assert (ARXIV_SOURCE_DIR / PAPER_ARXIV_MAIN_TEX_FILENAME).exists()
    assert (ARXIV_SOURCE_DIR / PAPER_ARXIV_REFERENCES_FILENAME).exists()

    manifest = _load_report("paper_arxiv_source_manifest.json")
    audit = _load_report("paper_submission_package_audit.json")
    main_tex = (ARXIV_SOURCE_DIR / PAPER_ARXIV_MAIN_TEX_FILENAME).read_text(encoding="utf-8")
    references = (ARXIV_SOURCE_DIR / PAPER_ARXIV_REFERENCES_FILENAME).read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_source_release_candidate"
    assert manifest["source_release_candidate_ready"] is True
    assert manifest["arxiv_upload_ready"] is False
    assert manifest["citation_audit"]["status"] == "pass"
    assert manifest["figure_audit"]["status"] == "pass"
    assert any(check["check_id"] == "p20_narrative_polish_passed" and check["passed"] for check in manifest["checks"])
    assert any(check["check_id"] == "p23_novelty_positioning_passed" and check["passed"] for check in manifest["checks"])
    assert audit["status"] == "pass"
    assert audit["violation_count"] == 0
    assert any(check["check_id"] == "author_and_pdf_metadata_present" and check["passed"] for check in audit["checks"])
    assert ".svg" not in main_tex
    assert "pending isolated" + " test" not in main_tex
    assert "ML-Enthusiast" in main_tex
    assert ("TODO" + "_EVIDENCE") not in main_tex
    assert r"TODO\_EVIDENCE" not in main_tex
    assert (
        r"\author{Tobias Gehra\\Independent Researcher\\"
        r"\href{mailto:t.gehra.ai@gmail.com}{\texttt{t.gehra.ai@gmail.com}}}"
        in main_tex
    )
    assert r"GitHub: \texttt{ML-Enthusiast-de}" not in main_tex

    cited_keys = set()
    for citation in re.findall(r"\\citep?\{([^}]+)\}", main_tex):
        cited_keys.update(part.strip() for part in citation.split(","))
    bib_keys = set(re.findall(r"@\w+\{([^,\s]+)", references))
    assert cited_keys <= bib_keys

    figure_refs = manifest["source_tree"]["artifact_refs"]
    pdf_refs = [ref for ref in figure_refs if ref.endswith(".pdf")]
    assert len(pdf_refs) == 4
    for ref in pdf_refs:
        assert (PROJECT_ROOT / ref).read_bytes().startswith(b"%PDF-1.4")

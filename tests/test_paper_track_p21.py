from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any

import pytest

import relaytic.release_safety.paper_final_preflight as paper_final_preflight
from relaytic.release_safety import (
    LOCAL_PAPER_FINAL_BUILD_REFS,
    PAPER_FINAL_PREFLIGHT_FILENAMES,
    build_paper_final_preflight_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
ARXIV_SOURCE_DIR = PAPER_DIR / "arxiv_src"
pytestmark = pytest.mark.prepush


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _seed_p21_fixture(root: Path, *, include_local_build: bool = True) -> None:
    paper_dir = root / "docs" / "paper"
    source_dir = paper_dir / "arxiv_src"
    report_dir = root / "docs" / "reports"
    source_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    (root / "README.md").write_text("Relaytic-AML paper review starts here.\n", encoding="utf-8")
    (paper_dir / "relaytic_aml_arxiv_draft.md").write_text(
        "\n".join(
            [
                "# Relaytic-AML",
                "",
                "Table 9. Hosted external-score case study",
                "",
                "Repository: https://github.com/ML-Enthusiast-de/Relaytic. "
                "Public release tag: TODO before arXiv submission.",
                "",
                "```powershell",
                "py -3.11 -m relaytic.ui.cli release-safety paper-final-preflight --format json",
                "```",
                "",
                "## AI Assistance Disclosure",
                "",
                "LLM tools assisted with drafting and checks; final interpretation remains author responsibility.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (source_dir / "main.tex").write_text(
        "\\hypersetup{pdftitle={Relaytic-AML: Test},pdfauthor={ML-Enthusiast-de}}\n",
        encoding="utf-8",
    )
    (source_dir / "references.bib").write_text("@misc{fixture,title={Fixture}}\n", encoding="utf-8")

    for filename, payload in {
        "paper_release_manifest.json": {"status": "ready_for_claim_safe_arxiv_release"},
        "paper_narrative_polish_manifest.json": {"status": "ready_for_final_pdf_preflight"},
        "paper_arxiv_source_manifest.json": {"status": "ready_for_source_release_candidate"},
        "paper_submission_package_audit.json": {"status": "pass"},
    }.items():
        _write_json(report_dir / filename, payload)

    if include_local_build:
        pdf_bytes = b"%PDF-1.4\n" + (b"0" * 120_000)
        (source_dir / "main.pdf").write_bytes(pdf_bytes)
        (paper_dir / "relaytic_aml_arxiv_draft.pdf").write_bytes(pdf_bytes)
        (source_dir / "main.log").write_text("Output written on main.pdf.\n", encoding="utf-8")
        newer = time.time() + 2
        os.utime(source_dir / "main.pdf", (newer, newer))
        os.utime(source_dir / "main.log", (newer, newer))
        os.utime(paper_dir / "relaytic_aml_arxiv_draft.pdf", (newer, newer))


def test_paper_track_p21_builds_final_preflight_pack_from_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_p21_fixture(tmp_path)
    monkeypatch.setattr(
        paper_final_preflight,
        "_pdffonts_scan",
        lambda _path: {"status": "pass", "violation_count": 0, "violations": []},
    )

    pack = build_paper_final_preflight_pack(tmp_path)
    manifest = pack["paper_final_preflight_manifest"]
    source = pack["paper_final_source_preflight"]
    pdf = pack["paper_final_pdf_preflight"]

    assert manifest["status"] == "ready_for_author_review_not_tagged"
    assert manifest["source_pdf_review_ready"] is True
    assert manifest["arxiv_upload_ready"] is False
    assert manifest["next_slice"].startswith("Slice 16A")
    assert manifest["hard_claims_allowed"] is False
    assert manifest["headline_claims_allowed"] is False
    assert manifest["local_build_artifact_refs"] == LOCAL_PAPER_FINAL_BUILD_REFS
    assert source["status"] == "pass"
    assert pdf["status"] == "pass"
    assert not manifest["failed_checks"]


def test_paper_track_p21_cli_writes_final_preflight_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_p21_fixture(tmp_path)
    output_dir = tmp_path / "out"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        paper_final_preflight,
        "_pdffonts_scan",
        lambda _path: {"status": "pass", "violation_count": 0, "violations": []},
    )

    exit_code = main(
        [
            "release-safety",
            "paper-final-preflight",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_author_review_not_tagged"
    assert payload["paper_final_preflight_manifest"]["next_slice"].startswith("Slice 16A")
    for filename in PAPER_FINAL_PREFLIGHT_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p21_fails_closed_without_local_build_outputs(tmp_path: Path) -> None:
    _seed_p21_fixture(tmp_path, include_local_build=False)

    pack = build_paper_final_preflight_pack(tmp_path)
    manifest = pack["paper_final_preflight_manifest"]
    pdf = pack["paper_final_pdf_preflight"]

    assert manifest["status"] == "blocked_pending_final_preflight_repairs"
    assert pdf["status"] == "fail"
    assert any(check["check_id"] == "compiled_pdf_present" for check in pdf["failed_checks"])
    assert any(check["check_id"] == "pdf_preflight_passed" for check in manifest["failed_checks"])


def test_paper_track_p21_committed_preflight_reports_are_ready() -> None:
    for filename in PAPER_FINAL_PREFLIGHT_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = json.loads((REPORT_DIR / "paper_final_preflight_manifest.json").read_text(encoding="utf-8"))
    source = json.loads((REPORT_DIR / "paper_final_source_preflight.json").read_text(encoding="utf-8"))
    pdf = json.loads((REPORT_DIR / "paper_final_pdf_preflight.json").read_text(encoding="utf-8"))
    changelog = (REPORT_DIR / "paper_final_release_changelog.md").read_text(encoding="utf-8")
    draft = (PAPER_DIR / "relaytic_aml_arxiv_draft.md").read_text(encoding="utf-8")
    main_tex = (ARXIV_SOURCE_DIR / "main.tex").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_author_review_not_tagged"
    assert manifest["arxiv_upload_ready"] is False
    assert manifest["next_slice"].startswith("Slice 16A")
    assert manifest["local_build_artifact_refs"] == LOCAL_PAPER_FINAL_BUILD_REFS
    assert source["status"] == "pass"
    assert pdf["status"] == "pass"
    assert "Table 9. Hosted external-score case study" in draft
    assert "## AI Assistance Disclosure" in draft
    assert "\\section{AI Assistance Disclosure}" in main_tex
    assert "Use of AI Assistance" not in main_tex
    assert "Final Paper Preflight Changelog" in changelog
    assert (PAPER_DIR / "relaytic_aml_arxiv_draft.pdf").stat().st_size > 100_000

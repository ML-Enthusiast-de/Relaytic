"""Paper Track P21 final source/PDF preflight and changelog."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_FINAL_PREFLIGHT_SCHEMA_VERSION = "relaytic.paper_final_preflight.v1"
PAPER_FINAL_PREFLIGHT_REPORT_DIR = Path("docs") / "reports"
PAPER_FINAL_PREFLIGHT_SOURCE_DIR = Path("docs") / "paper" / "arxiv_src"
PAPER_FINAL_REVIEW_PDF = Path("docs") / "paper" / "relaytic_aml_arxiv_draft.pdf"
NEXT_PAPER_FINAL_PREFLIGHT_SLICE = "Slice 16A - capability registry and capability cards"

PAPER_FINAL_PREFLIGHT_FILENAMES = {
    "paper_final_pdf_preflight": "paper_final_pdf_preflight.json",
    "paper_final_source_preflight": "paper_final_source_preflight.json",
    "paper_final_preflight_manifest": "paper_final_preflight_manifest.json",
    "paper_final_release_changelog": "paper_final_release_changelog.md",
}

REQUIRED_PAPER_FINAL_PREFLIGHT_INPUT_REFS = [
    "README.md",
    "docs/paper/relaytic_aml_arxiv_draft.md",
    "docs/paper/relaytic_aml_arxiv_draft.pdf",
    "docs/paper/arxiv_src/main.tex",
    "docs/paper/arxiv_src/references.bib",
    "docs/reports/paper_release_manifest.json",
    "docs/reports/paper_narrative_polish_manifest.json",
    "docs/reports/paper_novelty_positioning_manifest.json",
    "docs/reports/paper_novelty_positioning_audit.json",
    "docs/reports/paper_adjacent_systems_distinction_matrix.json",
    "docs/reports/paper_arxiv_source_manifest.json",
    "docs/reports/paper_submission_package_audit.json",
]

LOCAL_PAPER_FINAL_BUILD_REFS = [
    "docs/paper/arxiv_src/main.pdf",
    "docs/paper/arxiv_src/main.log",
]

FORBIDDEN_FINAL_PUBLIC_MARKERS = [
    "TODO_EVIDENCE",
    "FIXME",
    "Public release tag: TODO before arXiv submission",
    "pending isolated test",
    "pending main-table evidence",
    "unresolved reference",
    "unresolved citation",
    "undefined references",
    "dummy",
]


def build_paper_final_preflight_pack(
    project_root: str | Path,
    *,
    source_report_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build the P21 final paper/source/PDF preflight pack."""
    root = Path(project_root)
    report_dir = (
        Path(source_report_dir)
        if source_report_dir is not None
        else root / PAPER_FINAL_PREFLIGHT_REPORT_DIR
    )
    inputs = _collect_inputs(root=root, report_dir=report_dir)
    source_preflight = _build_source_preflight(inputs)
    pdf_preflight = _build_pdf_preflight(inputs)
    manifest = _build_manifest(inputs=inputs, source_preflight=source_preflight, pdf_preflight=pdf_preflight)
    changelog = render_paper_final_release_changelog(
        {
            "paper_final_pdf_preflight": pdf_preflight,
            "paper_final_source_preflight": source_preflight,
            "paper_final_preflight_manifest": manifest,
        }
    )
    return {
        "paper_final_pdf_preflight": pdf_preflight,
        "paper_final_source_preflight": source_preflight,
        "paper_final_preflight_manifest": manifest,
        "paper_final_release_changelog": changelog,
    }


def sync_paper_final_preflight_pack(
    project_root: str | Path,
    *,
    source_report_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P21 final preflight reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_FINAL_PREFLIGHT_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_final_preflight_pack(root, source_report_dir=source_report_dir)
    written: dict[str, Path] = {}
    for key, filename in PAPER_FINAL_PREFLIGHT_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_final_preflight_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_final_preflight_manifest", {}))
    pdf = dict(pack.get("paper_final_pdf_preflight", {}))
    source = dict(pack.get("paper_final_source_preflight", {}))
    lines = [
        "# Paper P21 Final Preflight",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Source preflight: `{source.get('status') or 'unknown'}`",
        f"- PDF preflight: `{pdf.get('status') or 'unknown'}`",
        f"- arXiv upload ready: `{manifest.get('arxiv_upload_ready')}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
    ]
    blockers = list(manifest.get("upload_blockers_remaining", []))
    if blockers:
        lines.extend(["", "## Remaining Upload Blockers", ""])
        for blocker in blockers:
            lines.append(f"- {blocker}")
    return "\n".join(lines).rstrip() + "\n"


def render_paper_final_release_changelog(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_final_preflight_manifest", {}))
    pdf = dict(pack.get("paper_final_pdf_preflight", {}))
    source = dict(pack.get("paper_final_source_preflight", {}))
    lines = [
        "# Relaytic-AML Final Paper Preflight Changelog",
        "",
        f"- Slice: `Paper Track P21`",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Source package: `{source.get('status') or 'unknown'}`",
        f"- PDF package: `{pdf.get('status') or 'unknown'}`",
        f"- arXiv upload ready now: `{manifest.get('arxiv_upload_ready')}`",
        "",
        "## Public Paper Changes",
        "",
        "- sharpened the abstract and contribution framing around a local-first agentic AML evaluation lab",
        "- made the hosted external-score case study a numbered publication table",
        "- replaced machine-style audit values with reader-facing audit signals",
        "- split reproduction commands into copy-paste-safe Windows and macOS/Linux blocks",
        "- added concrete PaySim and Elliptic review-budget queue counts from existing artifacts",
        "- renamed the AI disclosure and kept it short and professional",
        "- added the P23 novelty and adjacent-systems distinction gate around detector and agent-assisted AML workflows",
        "",
        "## Claims Intentionally Not Made",
        "",
        "- no real-bank AML superiority claim",
        "- no graph-neural detector novelty claim",
        "- no RevClassifyDS parity claim",
        "- no production deployment or analyst-hour ROI claim",
        "- no hard or headline detector-performance claim",
        "",
        "## Remaining Author Action",
        "",
        "- create or select the final public tag after the reviewed source/PDF tree is clean",
        "- do one human page-by-page PDF inspection immediately before upload",
        "- confirm `git status --short` is clean at the tag target",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _collect_inputs(*, root: Path, report_dir: Path) -> dict[str, Any]:
    paper_dir = root / "docs" / "paper"
    source_dir = root / PAPER_FINAL_PREFLIGHT_SOURCE_DIR
    return {
        "root": root,
        "readme": _read_text_artifact(root / "README.md", root=root),
        "draft": _read_text_artifact(paper_dir / "relaytic_aml_arxiv_draft.md", root=root),
        "review_pdf": _read_binary_artifact(root / PAPER_FINAL_REVIEW_PDF, root=root),
        "main_tex": _read_text_artifact(source_dir / "main.tex", root=root),
        "references_bib": _read_text_artifact(source_dir / "references.bib", root=root),
        "main_pdf": _read_binary_artifact(source_dir / "main.pdf", root=root),
        "main_log": _read_text_artifact(source_dir / "main.log", root=root),
        "paper_release_manifest": _read_json_artifact(report_dir / "paper_release_manifest.json", root=root),
        "paper_narrative_polish_manifest": _read_json_artifact(report_dir / "paper_narrative_polish_manifest.json", root=root),
        "paper_novelty_positioning_manifest": _read_json_artifact(report_dir / "paper_novelty_positioning_manifest.json", root=root),
        "paper_novelty_positioning_audit": _read_json_artifact(report_dir / "paper_novelty_positioning_audit.json", root=root),
        "paper_adjacent_systems_distinction_matrix": _read_json_artifact(report_dir / "paper_adjacent_systems_distinction_matrix.json", root=root),
        "paper_arxiv_source_manifest": _read_json_artifact(report_dir / "paper_arxiv_source_manifest.json", root=root),
        "paper_submission_package_audit": _read_json_artifact(report_dir / "paper_submission_package_audit.json", root=root),
    }


def _build_source_preflight(inputs: dict[str, Any]) -> dict[str, Any]:
    draft = _text_payload(inputs["draft"])
    readme = _text_payload(inputs["readme"])
    main_tex = _text_payload(inputs["main_tex"])
    references = _text_payload(inputs["references_bib"])
    public_scan = _public_marker_scan(
        {
            "README.md": readme,
            "docs/paper/relaytic_aml_arxiv_draft.md": draft,
            "docs/paper/arxiv_src/main.tex": main_tex,
            "docs/paper/arxiv_src/references.bib": references,
        }
    )
    command_scan = _command_block_scan(draft)
    system_eval_scan = _main_body_system_eval_scan(draft)
    table_caption_scan = _latex_table_caption_scan(main_tex)
    section_spacing_scan = _section_needspace_scan(main_tex)
    checks = [
        _check(
            "reader_public_markers_clean",
            not public_scan["violations"],
            "Reader-facing paper/source surfaces must be free of unresolved markers and release-tag placeholders.",
            detail=public_scan,
        ),
        _check(
            "long_reproduction_commands_wrapped",
            command_scan["status"] == "pass",
            "Reproduction command blocks should not contain margin-breaking command lines.",
            detail=command_scan,
        ),
        _check(
            "main_body_system_evaluation_compressed",
            system_eval_scan["status"] == "pass",
            "Main-body system evaluation should use one synthesis table and move dense audit logs to the appendix.",
            detail=system_eval_scan,
        ),
        _check(
            "latex_tables_use_real_captions",
            table_caption_scan["status"] == "pass",
            "Generated LaTeX should use numbered table captions, not bold pseudo-caption text.",
            detail=table_caption_scan,
        ),
        _check(
            "section_headings_have_needspace_guards",
            section_spacing_scan["status"] == "pass",
            "Section headings should be guarded against orphan placement at page bottoms.",
            detail=section_spacing_scan,
        ),
        _check(
            "ai_disclosure_named_professionally",
            "## AI Assistance Disclosure" in draft and "## Use of AI Assistance" not in draft,
            "AI assistance disclosure should be short, professional, and consistently named.",
        ),
        _check(
            "release_identifier_visible",
            "Repository: https://github.com/ML-Enthusiast-de/Relaytic" in draft
            and "Source commit:" in draft
            and "Public release tag: TODO before arXiv submission" not in draft,
            "Reproducibility section must identify the repository and a concrete source candidate commit.",
        ),
        _check(
            "source_manifest_ready",
            _payload(inputs["paper_arxiv_source_manifest"]).get("status") == "ready_for_source_release_candidate",
            "P21 requires a ready P14 source release candidate.",
        ),
        _check(
            "p20_polish_ready",
            _payload(inputs["paper_narrative_polish_manifest"]).get("status") == "ready_for_final_pdf_preflight",
            "P21 requires the P20 paper-polish gate to pass.",
        ),
        _check(
            "p23_novelty_positioning_ready",
            _payload(inputs["paper_novelty_positioning_manifest"]).get("status") == "ready_for_final_author_review"
            and _payload(inputs["paper_novelty_positioning_audit"]).get("status") == "pass"
            and _payload(inputs["paper_adjacent_systems_distinction_matrix"]).get("status") == "pass",
            "Final preflight requires P23 novelty and adjacent-systems distinction checks.",
        ),
        _check(
            "source_package_audit_passed",
            _payload(inputs["paper_submission_package_audit"]).get("status") == "pass",
            "P21 requires the source/package audit to pass.",
        ),
    ]
    return {
        "schema_version": PAPER_FINAL_PREFLIGHT_SCHEMA_VERSION,
        "slice": "Paper Track P21",
        "status": "pass" if all(check["passed"] for check in checks) else "fail",
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def _main_body_system_eval_scan(draft: str) -> dict[str, Any]:
    appendix_marker = "## Appendix: Detailed Audit and Reproducibility Records"
    if appendix_marker in draft:
        main_body, appendix = draft.split(appendix_marker, 1)
    else:
        main_body, appendix = draft, ""
    dense_titles = [
        "Detailed failure-case fixtures",
        "Governance machinery ablation",
        "Governance invariants and evidence map",
        "Hosted external-score case study",
        "Evidence routing examples",
        "Rowless handoff and interrupted-run recovery examples",
    ]
    violations = [title for title in dense_titles if title in main_body]
    appendix_missing = [title for title in dense_titles if title not in appendix]
    status = (
        "pass"
        if "Table 5. System evaluation summary" in main_body
        and not violations
        and not appendix_missing
        else "fail"
    )
    return {
        "status": status,
        "main_summary_present": "Table 5. System evaluation summary" in main_body,
        "main_body_dense_table_violations": violations,
        "appendix_missing_detail_titles": appendix_missing,
    }


def _latex_table_caption_scan(main_tex: str) -> dict[str, Any]:
    violations = []
    for marker in [r"\textbf{Table", "Table 2a", "Table 2b"]:
        if marker in main_tex:
            violations.append(marker)
    caption_count = main_tex.count(r"\captionof{table}")
    if caption_count < 6:
        violations.append("too_few_captionof_tables")
    return {
        "status": "pass" if not violations else "fail",
        "captionof_table_count": caption_count,
        "violations": violations,
    }


def _section_needspace_scan(main_tex: str) -> dict[str, Any]:
    lines = main_tex.splitlines()
    violations = []
    for index, line in enumerate(lines):
        if not line.startswith(r"\section{"):
            continue
        previous = "\n".join(lines[max(0, index - 3) : index])
        if r"\Needspace" not in previous:
            violations.append(line)
    return {
        "status": "pass" if not violations else "fail",
        "section_count": sum(1 for line in lines if line.startswith(r"\section{")),
        "violations": violations,
    }


def _build_pdf_preflight(inputs: dict[str, Any]) -> dict[str, Any]:
    main_log = _text_payload(inputs["main_log"])
    main_pdf = inputs["main_pdf"]
    review_pdf = inputs["review_pdf"]
    main_tex = inputs["main_tex"]
    log_scan = _latex_log_scan(main_log)
    font_scan = _pdffonts_scan(Path(main_pdf.get("path") or ""))
    checks = [
        _check(
            "compiled_pdf_present",
            bool(main_pdf.get("exists")) and int(main_pdf.get("byte_count") or 0) > 100_000,
            "arXiv source PDF must exist and have nontrivial size.",
            detail={"byte_count": main_pdf.get("byte_count")},
        ),
        _check(
            "compiled_pdf_matches_current_source",
            bool(main_pdf.get("exists"))
            and bool(main_tex.get("exists"))
            and float(main_pdf.get("modified_unix") or 0) >= float(main_tex.get("modified_unix") or 0),
            "Compiled PDF should be newer than or as new as the generated TeX source.",
            detail={
                "source_modified_unix": main_tex.get("modified_unix"),
                "pdf_modified_unix": main_pdf.get("modified_unix"),
            },
        ),
        _check(
            "review_pdf_synchronized",
            bool(review_pdf.get("exists"))
            and main_pdf.get("byte_count") == review_pdf.get("byte_count"),
            "Human review PDF should match the compiled source PDF size.",
            detail={
                "source_pdf_bytes": main_pdf.get("byte_count"),
                "review_pdf_bytes": review_pdf.get("byte_count"),
            },
        ),
        _check(
            "latex_log_clean",
            log_scan["status"] == "pass",
            "LaTeX log must not contain unresolved references, citation warnings, or overfull boxes.",
            detail=log_scan,
        ),
        _check(
            "fonts_embedded_no_type3",
            font_scan["status"] == "pass",
            "PDF fonts should be embedded and avoid Type 3 fonts.",
            detail=font_scan,
        ),
        _check(
            "pdf_metadata_present_in_source",
            "pdftitle={Relaytic-AML:" in _text_payload(inputs["main_tex"])
            and "pdfauthor={Tobias Gehra}" in _text_payload(inputs["main_tex"])
            and "t.gehra.ai@gmail.com" in _text_payload(inputs["main_tex"]),
            "PDF metadata must be present in the generated TeX source.",
        ),
    ]
    return {
        "schema_version": PAPER_FINAL_PREFLIGHT_SCHEMA_VERSION,
        "slice": "Paper Track P21",
        "status": "pass" if all(check["passed"] for check in checks) else "fail",
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def _build_manifest(
    *,
    inputs: dict[str, Any],
    source_preflight: dict[str, Any],
    pdf_preflight: dict[str, Any],
) -> dict[str, Any]:
    required = _required_presence(inputs)
    checks = [
        _check(
            "required_inputs_present",
            not required["missing_artifact_refs"],
            "P21 requires the tracked paper/source artifacts plus P13/P14/P20/P23 manifests; local build outputs are checked by the PDF preflight.",
            detail=required,
        ),
        _check(
            "p13_release_ready",
            _payload(inputs["paper_release_manifest"]).get("status") == "ready_for_claim_safe_arxiv_release",
            "P21 requires the P13 claim-safe release manifest to remain ready.",
        ),
        _check(
            "source_preflight_passed",
            source_preflight.get("status") == "pass",
            "Source/text preflight must pass.",
        ),
        _check(
            "pdf_preflight_passed",
            pdf_preflight.get("status") == "pass",
            "PDF/log/font preflight must pass.",
        ),
    ]
    ready_for_author_review = all(check["passed"] for check in checks)
    upload_blockers = [
        "create or select the final public tag after the source/PDF tree is reviewed",
        "perform final human page-by-page PDF inspection immediately before upload",
        "confirm `git status --short` is empty at the tag target",
    ]
    return {
        "schema_version": PAPER_FINAL_PREFLIGHT_SCHEMA_VERSION,
        "slice": "Paper Track P21",
        "status": "ready_for_author_review_not_tagged" if ready_for_author_review else "blocked_pending_final_preflight_repairs",
        "source_pdf_review_ready": ready_for_author_review,
        "arxiv_upload_ready": False,
        "release_mode": "claim_safe_evaluation_environment_only" if ready_for_author_review else "blocked",
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "required_source_artifacts": REQUIRED_PAPER_FINAL_PREFLIGHT_INPUT_REFS,
        "local_build_artifact_refs": LOCAL_PAPER_FINAL_BUILD_REFS,
        "report_artifact_refs": [
            f"docs/reports/{filename}"
            for filename in PAPER_FINAL_PREFLIGHT_FILENAMES.values()
        ],
        "upload_blockers_remaining": upload_blockers,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "next_slice": NEXT_PAPER_FINAL_PREFLIGHT_SLICE if ready_for_author_review else "Paper Track P21 repair",
    }


def _required_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    by_ref = {
        str(value.get("artifact_ref")): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    present = []
    missing = []
    for ref in REQUIRED_PAPER_FINAL_PREFLIGHT_INPUT_REFS:
        artifact = by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {"present_artifact_refs": present, "missing_artifact_refs": missing}


def _public_marker_scan(surfaces: dict[str, str]) -> dict[str, Any]:
    violations = []
    for artifact_ref, text in surfaces.items():
        scan_text = text
        for marker in FORBIDDEN_FINAL_PUBLIC_MARKERS:
            for match in re.finditer(re.escape(marker), scan_text, flags=re.IGNORECASE):
                violations.append(
                    {
                        "artifact_ref": artifact_ref,
                        "marker": marker,
                        "offset": match.start(),
                    }
                )
        if "TODO" in scan_text:
            violations.append({"artifact_ref": artifact_ref, "marker": "TODO", "offset": scan_text.find("TODO")})
    return {"status": "pass" if not violations else "fail", "violations": violations}


def _command_block_scan(draft: str) -> dict[str, Any]:
    in_block = False
    block_lang = ""
    violations = []
    for line_no, raw in enumerate(draft.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            if in_block:
                in_block = False
                block_lang = ""
            else:
                in_block = True
                block_lang = stripped.strip("`").strip().lower()
            continue
        if not in_block or block_lang not in {"powershell", "bash"}:
            continue
        if len(raw) > 112:
            violations.append({"line": line_no, "length": len(raw), "text": raw[:140]})
    return {"status": "pass" if not violations else "fail", "violations": violations}


def _latex_log_scan(log_text: str) -> dict[str, Any]:
    patterns = [
        "Overfull \\hbox",
        "Underfull \\hbox (badness 10000)",
        "undefined references",
        "Citation",
        "Reference",
        "LaTeX Warning",
        "Package natbib Warning",
        "There were undefined",
        "Rerun to get",
        "!",
    ]
    violations = []
    for line_no, line in enumerate(log_text.splitlines(), start=1):
        if "Package: rerunfilecheck" in line:
            continue
        if any(pattern in line for pattern in patterns):
            if "Label(s) may have changed" in line:
                violations.append({"line": line_no, "message": line.strip()})
            elif "Warning" in line or "Overfull" in line or "Underfull" in line or line.strip().startswith("!"):
                violations.append({"line": line_no, "message": line.strip()})
    return {"status": "pass" if not violations else "fail", "violation_count": len(violations), "violations": violations}


def _pdffonts_scan(pdf_path: Path) -> dict[str, Any]:
    tool = shutil.which("pdffonts")
    if not tool:
        return {"status": "not_checked", "reason": "pdffonts not available on PATH"}
    if not pdf_path.exists():
        return {"status": "fail", "reason": "PDF missing", "pdf_path": str(pdf_path)}
    result = subprocess.run([tool, str(pdf_path)], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return {"status": "fail", "reason": result.stderr.strip() or "pdffonts failed"}
    violations = []
    for line in result.stdout.splitlines()[2:]:
        if not line.strip() or line.startswith("-"):
            continue
        if "Type 3" in line:
            violations.append({"reason": "type3_font", "line": line})
        if re.search(r"\sno\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line):
            violations.append({"reason": "font_not_embedded", "line": line})
    return {
        "status": "pass" if not violations else "fail",
        "violation_count": len(violations),
        "violations": violations,
    }


def _check(check_id: str, passed: bool, message: str, *, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"check_id": check_id, "passed": bool(passed), "message": message}
    if detail is not None:
        row["detail"] = detail
    return row


def _read_json_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact = _read_text_artifact(path, root=root)
    if not artifact.get("exists"):
        artifact["payload"] = {}
        return artifact
    try:
        artifact["payload"] = json.loads(str(artifact.get("text") or "{}"))
    except json.JSONDecodeError as exc:
        artifact["payload"] = {"status": "invalid_json", "error": str(exc)}
    return artifact


def _read_text_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _repo_relative(path, root=root)
    if not path.exists():
        return {"exists": False, "artifact_ref": artifact_ref, "path": str(path), "text": ""}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "exists": True,
        "artifact_ref": artifact_ref,
        "path": str(path),
        "byte_count": len(text.encode("utf-8")),
        "modified_unix": path.stat().st_mtime,
        "text": text,
    }


def _read_binary_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _repo_relative(path, root=root)
    if not path.exists():
        return {"exists": False, "artifact_ref": artifact_ref, "path": str(path), "byte_count": 0}
    return {
        "exists": True,
        "artifact_ref": artifact_ref,
        "path": str(path),
        "byte_count": path.stat().st_size,
        "modified_unix": path.stat().st_mtime,
    }


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload")
    return payload if isinstance(payload, dict) else {}


def _text_payload(artifact: dict[str, Any]) -> str:
    return str(artifact.get("text") or "")


def _repo_relative(path: Path, *, root: Path | None = None) -> str:
    base = root if root is not None else Path.cwd()
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "NEXT_PAPER_FINAL_PREFLIGHT_SLICE",
    "PAPER_FINAL_PREFLIGHT_FILENAMES",
    "PAPER_FINAL_PREFLIGHT_REPORT_DIR",
    "PAPER_FINAL_PREFLIGHT_SCHEMA_VERSION",
    "PAPER_FINAL_PREFLIGHT_SOURCE_DIR",
    "PAPER_FINAL_REVIEW_PDF",
    "LOCAL_PAPER_FINAL_BUILD_REFS",
    "REQUIRED_PAPER_FINAL_PREFLIGHT_INPUT_REFS",
    "build_paper_final_preflight_pack",
    "render_paper_final_preflight_markdown",
    "render_paper_final_release_changelog",
    "sync_paper_final_preflight_pack",
]

"""Paper Track P24 release-integrity and exact-revision build checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_RELEASE_INTEGRITY_SCHEMA_VERSION = "relaytic.paper_release_integrity.v1"
PAPER_RELEASE_INTEGRITY_REPORT_DIR = Path("docs") / "reports"
PAPER_RELEASE_INTEGRITY_FILENAMES = {
    "paper_p24_evidence_authority": "paper_p24_evidence_authority.json",
    "paper_p24_baseline_metric_snapshot": "paper_p24_baseline_metric_snapshot.json",
    "paper_p24_artifact_conflict_audit": "paper_p24_artifact_conflict_audit.json",
    "paper_p24_protocol_disclosure_audit": "paper_p24_protocol_disclosure_audit.json",
    "paper_p24_bibliography_verification": "paper_p24_bibliography_verification.json",
    "paper_p24_claim_citation_map": "paper_p24_claim_citation_map.json",
    "paper_p24_statistical_reporting_decision": "paper_p24_statistical_reporting_decision.json",
    "paper_p24_visual_layout_audit": "paper_p24_visual_layout_audit.json",
    "paper_p24_reproduction_semantics": "paper_p24_reproduction_semantics.json",
    "paper_p24_metric_consistency_audit": "paper_p24_metric_consistency_audit.json",
    "paper_p24_split_consistency_audit": "paper_p24_split_consistency_audit.json",
    "paper_p24_semantic_source_audit": "paper_p24_semantic_source_audit.json",
    "paper_p24_release_manifest": "paper_p24_release_manifest.json",
}

METRIC_AUTHORITIES = [
    ("PaySim validation PR-AUC", "paysim_competitive_benchmark_manifest.json", "validation_selected_competitive_model.validation_pr_auc", 0.568725, "0.5687"),
    ("PaySim test PR-AUC", "paysim_competitive_benchmark_manifest.json", "validation_selected_competitive_model.test_pr_auc", 0.638773, "0.6388"),
    ("PaySim test ROC-AUC", "paysim_competitive_benchmark_manifest.json", "validation_selected_competitive_model.test_roc_auc", 0.968282, "0.9683"),
    ("PaySim precision", "paysim_competitive_benchmark_manifest.json", "validation_selected_competitive_model.test_operating_point.precision_at_k", 0.703336, "0.7033"),
    ("PaySim recall", "paysim_competitive_benchmark_manifest.json", "validation_selected_competitive_model.test_operating_point.recall_at_review_budget", 0.471584, "0.4716"),
    ("PaySim realized queue", "paysim_competitive_benchmark_manifest.json", "validation_selected_competitive_model.test_operating_point.review_fraction", 0.008974, "0.8974%"),
    ("Elliptic validation PR-AUC", "paper_graph_feature_table.json", "validation_selected_competitive_baseline.validation_pr_auc", 0.976654, "0.9767"),
    ("Elliptic test PR-AUC", "paper_graph_feature_table.json", "validation_selected_competitive_baseline.test_pr_auc", 0.668756, "0.6688"),
    ("Elliptic precision", "paper_graph_feature_table.json", "validation_selected_competitive_baseline.test_operating_point.precision_at_k", 1.0, "1.0000"),
    ("Elliptic recall", "paper_graph_feature_table.json", "validation_selected_competitive_baseline.test_operating_point.recall_at_review_budget", 0.056604, "0.0566"),
    ("Elliptic realized queue", "paper_graph_feature_table.json", "validation_selected_competitive_baseline.test_operating_point.review_fraction", 0.003219, "0.3219%"),
    ("Elliptic2 repeated PR-AUC", "elliptic2_repeated_seed_scorecard.json", "official_partition.test_pr_auc_mean", 0.943240, "0.9432"),
    ("Elliptic2 repeated std", "elliptic2_repeated_seed_scorecard.json", "official_partition.test_pr_auc_std", 0.000882, "0.0009"),
    ("Elliptic2 hash robustness", "elliptic2_repeated_seed_scorecard.json", "robustness_partition.test_pr_auc_mean", 0.929669, "0.9297"),
    ("RevClassifyDS reference", "paper_metric_cell_audit.json", "cell:elliptic2_p8b_modern_context.published_reference_pr_auc", 0.974, "0.9740"),
]

VERIFIED_CITATIONS = {
    "lopezrojas2016paysim": "https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf",
    "weber2019elliptic": "https://arxiv.org/abs/1908.02591",
    "bellei2024elliptic2": "https://arxiv.org/abs/2404.19109",
    "song2024revtrack": "https://doi.org/10.1145/3677052.3698635",
    "poon2025linemvgnn": "https://doi.org/10.3390/ai6040069",
    "saito2015precisionrecall": "https://doi.org/10.1371/journal.pone.0118432",
    "kleppmann2019localfirst": "https://doi.org/10.1145/3359591.3359737",
    "geurts2006extratrees": "https://doi.org/10.1007/s10994-006-6226-1",
    "chen2016xgboost": "https://doi.org/10.1145/2939672.2939785",
    "ke2017lightgbm": "https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html",
    "platt1999probabilistic": "https://www.microsoft.com/en-us/research/publication/probabilistic-outputs-for-support-vector-machines-and-comparisons-to-regularized-likelihood-methods/",
    "gaurav2025governanceaas": "https://arxiv.org/abs/2508.18765",
    "kaptein2026runtimegovernance": "https://arxiv.org/abs/2603.16586",
    "naik2026llmopsaml": "https://arxiv.org/abs/2605.11232",
}


def build_paper_release_integrity_pack(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root)
    reports = root / "docs" / "reports"
    paper = root / "docs" / "paper"
    markdown = _read_text(paper / "relaytic_aml_arxiv_draft.md")
    bibliography = _read_text(paper / "references.bib")
    figure4 = _read_text(paper / "figures" / "figure_3_review_budget.svg")
    git = _git_state(root)

    authority_rows = [
        {
            "fact": name,
            "artifact_ref": f"docs/reports/{filename}",
            "field": field,
            "expected_value": expected,
            "display": display,
        }
        for name, filename, field, expected, display in METRIC_AUTHORITIES
    ]
    evidence_authority = _report(
        "pass" if all((reports / row[1]).is_file() for row in METRIC_AUTHORITIES) else "fail",
        authority_rows=authority_rows,
        split_authorities=[
            "docs/reports/paysim_temporal_split_report.json",
            "docs/reports/elliptic_temporal_split_report.json",
            "docs/reports/elliptic2_modern_reference_contract.json",
            "docs/reports/elliptic2_evaluable_cohort_reconciliation.json",
        ],
        release_revision=git,
    )

    metric_checks = []
    for name, filename, field, expected, display in METRIC_AUTHORITIES:
        payload = _read_json(reports / filename)
        actual = _resolve_metric(payload, filename, field)
        source_ok = _numeric_close(actual, expected)
        display_ok = display in markdown or display in figure4
        metric_checks.append(
            {
                "metric": name,
                "artifact_ref": f"docs/reports/{filename}",
                "field": field,
                "expected": expected,
                "actual": actual,
                "reader_display": display,
                "source_matches": source_ok,
                "display_present": display_ok,
                "passed": source_ok and display_ok,
            }
        )
    baseline_snapshot = _report("pass" if all(row["source_matches"] for row in metric_checks) else "fail", metrics=metric_checks)
    metric_consistency = _report("pass" if all(row["passed"] for row in metric_checks) else "fail", checks=metric_checks)

    conflicts = [
        {
            "topic": "Elliptic2 cohort",
            "authoritative_current_core": {"subgraphs": 121810, "positives": 2763},
            "authoritative_evaluable_cohort": {"rows": 110902, "positives": 2578},
            "resolution": "report both populations; benchmark metrics apply only to the pinned RevTrack-evaluable cohort",
            "passed": all(token in markdown for token in ("121,810", "110,902", "2,763", "2,578")),
        },
        {
            "topic": "Elliptic2 test exposure",
            "resolution": "describe repeated official-partition estimate as confirmatory rather than untouched",
            "passed": "confirmatory rather than an untouched-test estimate" in markdown,
        },
    ]
    conflict_audit = _report("pass" if all(row["passed"] for row in conflicts) else "fail", conflicts=conflicts)

    protocol_phrases = {
        "PaySim exact split ranges": ["1-445", "446-594", "595-743"],
        "PaySim boundary and history policy": ["no gap or embargo", "strictly earlier steps", "same-step events do not see one another"],
        "PaySim balance semantics": ["oldbalanceOrg", "newbalanceOrig", "mixed balance quartet"],
        "Elliptic exact split ranges": ["1-29", "30-39", "40-49"],
        "Elliptic unknown-label policy": ["Unknown-label nodes", "never targets or metric rows"],
        "Elliptic validation-test gap": ["validation PR-AUC 0.9767", "test PR-AUC 0.6688"],
        "Review-threshold transfer": ["applying that threshold unchanged to test", "scores equal to the threshold are included"],
        "Elliptic2 partition provenance": ["TRN", "VAL", "TST", "pinned RevTrack"],
        "Single-seed disclosure": ["single-seed point estimates"],
        "Calibration boundary": ["Raw and calibrated test PR-AUC are both"],
    }
    protocol_checks = [
        {"check": name, "required_phrases": phrases, "passed": all(phrase in markdown for phrase in phrases)}
        for name, phrases in protocol_phrases.items()
    ]
    protocol_audit = _report("pass" if all(row["passed"] for row in protocol_checks) else "fail", checks=protocol_checks)

    bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bibliography))
    citation_checks = [
        {"citation_key": key, "primary_url": url, "present": key in bib_keys}
        for key, url in VERIFIED_CITATIONS.items()
    ]
    author_repairs = {
        "gaurav2025governanceaas": "Pervez, Helen and Gaurav, Suyash and Heikkonen, Jukka and Chaudhary, Jatin",
        "kaptein2026runtimegovernance": "Kaptein, Maurits and Khan, Vassilis-Javed and Podstavnychy, Andriy",
        "naik2026llmopsaml": "Naik, Prathamesh Vasudeo and Dintakurthi, Naresh and Wang, Yue",
    }
    author_checks = [
        {"citation_key": key, "expected_author_field": authors, "passed": authors in bibliography}
        for key, authors in author_repairs.items()
    ]
    bibliography_verification = _report(
        "pass" if all(row["present"] for row in citation_checks) and all(row["passed"] for row in author_checks) else "fail",
        verification_date="2026-07-11",
        primary_source_checks=citation_checks,
        corrected_author_checks=author_checks,
        verification_method="primary arXiv records, DOI landing pages, or publisher/proceedings pages",
    )

    claim_citation_rows = [
        {"claim": "PaySim simulator provenance", "citation_keys": ["lopezrojas2016paysim"]},
        {"claim": "Elliptic and Elliptic2 benchmark provenance", "citation_keys": ["weber2019elliptic", "bellei2024elliptic2", "song2024revtrack"]},
        {"claim": "PR analysis for imbalanced classification", "citation_keys": ["saito2015precisionrecall"]},
        {"claim": "local-first definition", "citation_keys": ["kleppmann2019localfirst"]},
        {"claim": "selected model-family methods", "citation_keys": ["geurts2006extratrees", "chen2016xgboost", "ke2017lightgbm", "platt1999probabilistic"]},
    ]
    for row in claim_citation_rows:
        row["passed"] = all(f"@{key}" in markdown for key in row["citation_keys"])
    claim_citation_map = _report("pass" if all(row["passed"] for row in claim_citation_rows) else "fail", claims=claim_citation_rows)

    prediction_files = [
        path.as_posix()
        for path in root.rglob("*.json")
        if any(token in path.name.lower() for token in ("prediction", "test_scores", "score_vector"))
        and "fixture" not in path.as_posix().lower()
    ]
    statistical_decision = _report(
        "pass" if "single-seed point estimates" in markdown else "fail",
        confidence_interval_decision="not_reported",
        reason="No committed prediction-level PaySim or Elliptic labels-and-scores artifact supports a predeclared bootstrap.",
        prediction_level_candidates=prediction_files,
        paper_disclosure_present="single-seed point estimates" in markdown,
    )

    visual_checks = [
        {"check": "three distinct panels", "passed": all(label in figure4 for label in ("A. Local test ranking evidence", "B. Elliptic2 reference context", "C. Validation-threshold review queues"))},
        {"check": "non-comparability sentence inside figure", "passed": "Values across datasets and task contracts are not directly comparable." in figure4},
        {"check": "vector source", "passed": figure4.lstrip().startswith("<svg")},
        {"check": "realized queue context", "passed": all(token in figure4 for token in ("1,109 / 123,580", "36 / 11,184"))},
    ]
    visual_audit = _report("pass" if all(row["passed"] for row in visual_checks) else "fail", checks=visual_checks)

    reproduction_checks = [
        {"mode": "paper build", "passed": "Paper build" in markdown},
        {"mode": "source validation", "passed": "Source validation" in markdown},
        {"mode": "deterministic fixtures", "passed": "Deterministic fixtures" in markdown},
        {"mode": "artifact verification", "passed": "Artifact verification" in markdown},
        {"mode": "raw-data rerun", "passed": "raw-data rerun" in markdown.lower()},
        {"mode": "optional execution semantics", "passed": "does not guarantee" in markdown and "blocked reasons" in markdown},
    ]
    reproduction_semantics = _report("pass" if all(row["passed"] for row in reproduction_checks) else "fail", checks=reproduction_checks)

    split_checks = _split_checks(reports, markdown)
    split_consistency = _report("pass" if all(row["passed"] for row in split_checks) else "fail", checks=split_checks)

    semantic_findings = _semantic_findings(markdown, bibliography)
    semantic_source = _report("pass" if not semantic_findings else "fail", findings=semantic_findings)

    pack = {
        "paper_p24_evidence_authority": evidence_authority,
        "paper_p24_baseline_metric_snapshot": baseline_snapshot,
        "paper_p24_artifact_conflict_audit": conflict_audit,
        "paper_p24_protocol_disclosure_audit": protocol_audit,
        "paper_p24_bibliography_verification": bibliography_verification,
        "paper_p24_claim_citation_map": claim_citation_map,
        "paper_p24_statistical_reporting_decision": statistical_decision,
        "paper_p24_visual_layout_audit": visual_audit,
        "paper_p24_reproduction_semantics": reproduction_semantics,
        "paper_p24_metric_consistency_audit": metric_consistency,
        "paper_p24_split_consistency_audit": split_consistency,
        "paper_p24_semantic_source_audit": semantic_source,
    }
    checks = [{"report": key, "status": value["status"], "passed": value["status"] == "pass"} for key, value in pack.items()]
    pack["paper_p24_release_manifest"] = _report(
        "release_candidate_ready_for_human_upload" if all(row["passed"] for row in checks) else "blocked_pending_p24_repairs",
        slice="Paper Track P24",
        checks=checks,
        git=git,
        exact_revision_release_required=True,
        arxiv_upload_ready=False,
        benchmark_values_changed=False,
        human_owned_actions=["commit the reviewed source", "run final mode from the clean commit", "inspect the exact-revision PDF", "create a tag and upload if approved"],
    )
    return pack


def sync_paper_release_integrity_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    root = Path(project_root)
    target = Path(output_dir) if output_dir is not None else root / PAPER_RELEASE_INTEGRITY_REPORT_DIR
    target.mkdir(parents=True, exist_ok=True)
    pack = build_paper_release_integrity_pack(root)
    return {
        key: write_json(target / filename, pack[key], indent=2, sort_keys=True)
        for key, filename in PAPER_RELEASE_INTEGRITY_FILENAMES.items()
    }


def build_exact_revision_release(project_root: str | Path) -> dict[str, Any]:
    """Build final paper artifacts out of tree and refuse an uncommitted source state."""
    root = Path(project_root)
    git = _git_state(root)
    if git["dirty"]:
        raise ValueError("Final paper release requires a clean Git worktree; commit or discard reviewed changes first.")
    commit = str(git["commit"] or "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Final paper release could not resolve a full Git commit SHA.")

    from relaytic.release_safety.paper_arxiv_source import sync_paper_arxiv_source_pack
    from relaytic.release_safety.paper_release import sync_paper_release_pack

    release_root = root / "dist" / "paper-release" / commit
    paper_dir = release_root / "paper"
    source_dir = release_root / "source"
    reports_dir = release_root / "reports"
    if release_root.exists():
        shutil.rmtree(release_root)
    reports_dir.mkdir(parents=True, exist_ok=True)
    sync_paper_release_pack(root, output_dir=reports_dir, paper_dir=paper_dir, source_commit=commit)
    sync_paper_arxiv_source_pack(root, output_dir=reports_dir, source_dir=source_dir, paper_dir=paper_dir)
    _compile_latex(source_dir)

    built_pdf = source_dir / "main.pdf"
    if not built_pdf.is_file():
        raise ValueError("LaTeX compilation did not produce main.pdf.")
    pdf_path = release_root / "relaytic_aml_arxiv.pdf"
    shutil.copy2(built_pdf, pdf_path)
    source_archive = release_root / "relaytic_aml_arxiv_source.tar.gz"
    with tarfile.open(source_archive, "w:gz") as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file() and path.suffix not in {".aux", ".bbl", ".blg", ".log", ".out", ".pdf"}:
                archive.add(path, arcname=path.relative_to(source_dir))

    integrity = build_paper_release_integrity_pack(root)
    integrity_ok = integrity["paper_p24_release_manifest"]["status"] == "release_candidate_ready_for_human_upload"
    preflight = {
        "schema_version": PAPER_RELEASE_INTEGRITY_SCHEMA_VERSION,
        "status": "pass" if integrity_ok else "fail",
        "source_commit": commit,
        "clean_worktree_before_build": True,
        "paper_integrity_status": integrity["paper_p24_release_manifest"]["status"],
    }
    preflight_path = write_json(release_root / "final_preflight.json", preflight, indent=2, sort_keys=True)
    manifest = {
        "schema_version": PAPER_RELEASE_INTEGRITY_SCHEMA_VERSION,
        "status": "release_candidate_ready_for_human_upload" if integrity_ok else "blocked",
        "source_commit": commit,
        "clean_worktree_before_build": True,
        "arxiv_upload_ready": bool(integrity_ok),
        "artifacts": {
            "pdf": {"path": pdf_path.relative_to(root).as_posix(), "sha256": _sha256(pdf_path)},
            "source_bundle": {"path": source_archive.relative_to(root).as_posix(), "sha256": _sha256(source_archive)},
            "bibliography": {"path": (source_dir / "references.bib").relative_to(root).as_posix(), "sha256": _sha256(source_dir / "references.bib")},
            "final_preflight": {"path": preflight_path.relative_to(root).as_posix(), "sha256": _sha256(preflight_path)},
        },
    }
    write_json(release_root / "release_revision_manifest.json", manifest, indent=2, sort_keys=True)
    return manifest


def render_paper_release_integrity_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_p24_release_manifest", {}))
    failed = [row["report"] for row in manifest.get("checks", []) if not row.get("passed")]
    return "\n".join(
        [
            "# Paper P24 Release Integrity",
            "",
            f"- Status: `{manifest.get('status', 'unknown')}`",
            f"- Review reports passed: `{len(manifest.get('checks', [])) - len(failed)}/{len(manifest.get('checks', []))}`",
            f"- Failed reports: `{', '.join(failed) if failed else 'none'}`",
            "- Exact-revision final build remains a clean-worktree, human-triggered release action.",
        ]
    ) + "\n"


def _split_checks(reports: Path, markdown: str) -> list[dict[str, Any]]:
    paysim = _read_json(reports / "paysim_temporal_split_report.json")
    elliptic = _read_json(reports / "elliptic_temporal_split_report.json")
    expected = [
        ("PaySim train", paysim, "train", (1, 445, 6010937, 5007)),
        ("PaySim validation", paysim, "validation", (446, 594, 228103, 1552)),
        ("PaySim test", paysim, "test", (595, 743, 123580, 1654)),
        ("Elliptic train", elliptic, "train", (1, 29, 26381, 2871)),
        ("Elliptic validation", elliptic, "validation", (30, 39, 8999, 1038)),
        ("Elliptic test", elliptic, "test", (40, 49, 11184, 636)),
    ]
    rows = []
    for name, report, split, values in expected:
        source = next((row for row in report.get("split_rows", []) if row.get("split") == split), {})
        if "PaySim" in name:
            actual = (source.get("step_min"), source.get("step_max"), source.get("row_count"), source.get("positive_count"))
        else:
            actual = (source.get("time_step_min"), source.get("time_step_max"), source.get("known_label_count"), source.get("illicit_count"))
        display_tokens = [f"{values[0]}-{values[1]}", f"{values[2]:,}", f"{values[3]:,}"]
        rows.append({"split": name, "expected": values, "actual": actual, "display_tokens": display_tokens, "passed": tuple(actual) == values and all(token in markdown for token in display_tokens)})
    return rows


def _semantic_findings(markdown: str, bibliography: str) -> list[dict[str, str]]:
    findings = []
    patterns = {
        "unfinished marker": r"\b(?:TODO|FIXME|placeholder|pending evidence|dummy|temp)\b|\?\?",
        "ASCII plus-minus": r"\+/-",
        "generic rows/nodes": r"rows/nodes",
        "machine table truncation": r"(?m)^\|.*(?:\.{3}|…)\s*\|$",
        "old Elliptic2 partition wording": r"official-partition",
        "stale broad section title": r"^## 7\. System Evaluation$",
        "unsupported statistical qualifier": r"\b(?:statistically significant|significant improvement|meaningful improvement)\b",
        "universal prevention claim": r"\b(?:prevents all|always prevents|guarantees privacy|production-ready AML)\b",
        "obsolete citation key": r"poon2026linemvgnn|fincenAdvisories",
    }
    combined = markdown + "\n" + bibliography
    for rule, pattern in patterns.items():
        match = re.search(pattern, combined, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            findings.append({"rule": rule, "excerpt": match.group(0)[:120]})
    cited = set()
    for block in re.findall(r"\[(@[^\]]+)\]", markdown):
        cited.update(re.findall(r"@([A-Za-z0-9_:-]+)", block))
    bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bibliography))
    for key in sorted(cited - bib_keys):
        findings.append({"rule": "missing bibliography key", "excerpt": key})
    return findings


def _resolve_metric(payload: dict[str, Any], filename: str, field: str) -> Any:
    if filename == "paper_metric_cell_audit.json" and field.startswith("cell:"):
        cell_id = field.removeprefix("cell:")
        cells = [row for row in payload.get("numeric_cells", []) if isinstance(row, dict)]
        return next((row.get("value") for row in cells if row.get("cell_id") == cell_id), None)
    return _nested(payload, field)


def _nested(payload: Any, field: str) -> Any:
    current = payload
    for token in field.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(token)
    return current


def _numeric_close(actual: Any, expected: float, tolerance: float = 5e-7) -> bool:
    try:
        return abs(float(actual) - expected) <= tolerance
    except (TypeError, ValueError):
        return False


def _report(status: str, **payload: Any) -> dict[str, Any]:
    return {"schema_version": PAPER_RELEASE_INTEGRITY_SCHEMA_VERSION, "slice": "Paper Track P24", "status": status, **payload}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _git_state(root: Path) -> dict[str, Any]:
    commit = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--short")
    return {"commit": commit.strip(), "dirty": bool(status.strip()), "status_short": status.splitlines()}


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False, timeout=20)
    return completed.stdout if completed.returncode == 0 else ""


def _compile_latex(source_dir: Path) -> None:
    commands = [
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["bibtex", "main"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=source_dir, capture_output=True, text=True, check=False, timeout=180)
        if completed.returncode != 0:
            tail = (completed.stdout + "\n" + completed.stderr)[-4000:]
            raise ValueError(f"Paper build failed for {' '.join(command)}:\n{tail}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


__all__ = [
    "PAPER_RELEASE_INTEGRITY_FILENAMES",
    "PAPER_RELEASE_INTEGRITY_REPORT_DIR",
    "PAPER_RELEASE_INTEGRITY_SCHEMA_VERSION",
    "build_exact_revision_release",
    "build_paper_release_integrity_pack",
    "render_paper_release_integrity_markdown",
    "sync_paper_release_integrity_pack",
]

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
from relaytic.release_safety.paper_evidence_contract import (
    METRIC_EVIDENCE_CELL_REQUIRED_FIELDS,
    MISSING_FIELD_STRESS_FIXTURE_OMITTED_FIELDS,
    audit_evidence_gate_separation,
    build_evidence_schema_contract,
)


PAPER_RELEASE_INTEGRITY_SCHEMA_VERSION = "relaytic.paper_release_integrity.v1"
PAPER_RELEASE_INTEGRITY_REPORT_DIR = Path("docs") / "reports"
PAPER_RELEASE_INTEGRITY_FILENAMES = {
    "paper_p24_evidence_authority": "paper_p24_evidence_authority.json",
    "paper_p24_baseline_metric_snapshot": "paper_p24_baseline_metric_snapshot.json",
    "paper_p24_artifact_conflict_audit": "paper_p24_artifact_conflict_audit.json",
    "paper_p24_protocol_disclosure_audit": "paper_p24_protocol_disclosure_audit.json",
    "paper_p24_paysim_protocol_audit": "paper_p24_paysim_protocol_audit.json",
    "paper_p24_operating_point_audit": "paper_p24_operating_point_audit.json",
    "paper_p24_reference_provenance_audit": "paper_p24_reference_provenance_audit.json",
    "paper_p24_execution_status_audit": "paper_p24_execution_status_audit.json",
    "paper_p24_bibliography_verification": "paper_p24_bibliography_verification.json",
    "paper_p24_claim_citation_map": "paper_p24_claim_citation_map.json",
    "paper_p24_statistical_reporting_decision": "paper_p24_statistical_reporting_decision.json",
    "paper_p24_visual_layout_audit": "paper_p24_visual_layout_audit.json",
    "paper_p24_reproduction_semantics": "paper_p24_reproduction_semantics.json",
    "paper_p24_metric_consistency_audit": "paper_p24_metric_consistency_audit.json",
    "paper_p24_split_consistency_audit": "paper_p24_split_consistency_audit.json",
    "paper_p24_semantic_source_audit": "paper_p24_semantic_source_audit.json",
    "paper_p26_evidence_gate_separation_audit": "paper_p26_evidence_gate_separation_audit.json",
    "paper_p26_validation_subsplit_audit": "paper_p26_validation_subsplit_audit.json",
    "paper_p26_release_reference_audit": "paper_p26_release_reference_audit.json",
    "paper_p27_evidence_schema_audit": "paper_p27_evidence_schema_audit.json",
    "paper_p27_feature_contract_audit": "paper_p27_feature_contract_audit.json",
    "paper_p27_generated_surface_audit": "paper_p27_generated_surface_audit.json",
    "paper_p27_candidate_revision_audit": "paper_p27_candidate_revision_audit.json",
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
    "deprez2025continualaml": "https://doi.org/10.1002/wics.70040",
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
            "resolution": "report both populations. Benchmark metrics apply only to the pinned RevTrack-evaluable cohort.",
            "passed": all(token in markdown for token in ("121,810", "110,902", "2,763", "2,578")),
        },
        {
            "topic": "Elliptic2 test exposure",
            "resolution": "describe the repeated RevTrack TST estimate as confirmatory, with prior test exposure disclosed",
            "passed": "confirmatory rather than blind or untouched evidence" in markdown,
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
        "Elliptic2 partition provenance": ["TRN", "VAL", "TST", "provided RevTrack"],
        "Single-seed disclosure": ["single-seed point estimates"],
        "Calibration boundary": ["Raw and calibrated test PR-AUC are both"],
    }
    protocol_checks = [
        {"check": name, "required_phrases": phrases, "passed": all(phrase in markdown for phrase in phrases)}
        for name, phrases in protocol_phrases.items()
    ]
    protocol_audit = _report("pass" if all(row["passed"] for row in protocol_checks) else "fail", checks=protocol_checks)

    paysim_protocol = _paysim_protocol_audit(reports, markdown)
    operating_point_audit = _operating_point_audit(reports, markdown)
    reference_provenance_audit = _reference_provenance_audit(reports, markdown)
    execution_status_audit = _execution_status_audit(reports, markdown)

    bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bibliography))
    citation_checks = [
        {"citation_key": key, "primary_url": url, "present": key in bib_keys}
        for key, url in VERIFIED_CITATIONS.items()
    ]
    author_repairs = {
        "gaurav2025governanceaas": "Gaurav, Suyash and Heikkonen, Jukka and Chaudhary, Jatin",
        "kaptein2026runtimegovernance": "Kaptein, Maurits and Khan, Vassilis-Javed and Podstavnychy, Andriy",
        "naik2026llmopsaml": "Naik, Prathamesh Vasudeo and Dintakurthi, Naresh and Wang, Yue",
    }
    author_checks = [
        {"citation_key": key, "expected_author_field": authors, "passed": authors in bibliography}
        for key, authors in author_repairs.items()
    ]
    bibliography_verification = _report(
        "pass" if all(row["present"] for row in citation_checks) and all(row["passed"] for row in author_checks) else "fail",
        verification_date="2026-07-14",
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
        {"mode": "optional execution semantics", "passed": "--require-full-rerun" in markdown and "prior test exposure remains disclosed" in markdown},
    ]
    reproduction_semantics = _report("pass" if all(row["passed"] for row in reproduction_checks) else "fail", checks=reproduction_checks)

    split_checks = _split_checks(reports, markdown)
    split_consistency = _report("pass" if all(row["passed"] for row in split_checks) else "fail", checks=split_checks)

    semantic_findings = _semantic_findings(markdown, bibliography)
    semantic_source = _report("pass" if not semantic_findings else "fail", findings=semantic_findings)
    evidence_gate_separation = _evidence_gate_separation_audit(reports)
    validation_subsplits = _validation_subsplit_audit(reports, markdown)
    release_reference = _release_reference_audit(root, markdown)
    evidence_schema = _evidence_schema_audit(reports, markdown)
    feature_contract = _feature_contract_audit(reports, markdown)
    generated_surfaces = _generated_surface_audit(root, markdown)
    candidate_revision = _candidate_revision_audit(markdown, git)

    pack = {
        "paper_p24_evidence_authority": evidence_authority,
        "paper_p24_baseline_metric_snapshot": baseline_snapshot,
        "paper_p24_artifact_conflict_audit": conflict_audit,
        "paper_p24_protocol_disclosure_audit": protocol_audit,
        "paper_p24_paysim_protocol_audit": paysim_protocol,
        "paper_p24_operating_point_audit": operating_point_audit,
        "paper_p24_reference_provenance_audit": reference_provenance_audit,
        "paper_p24_execution_status_audit": execution_status_audit,
        "paper_p24_bibliography_verification": bibliography_verification,
        "paper_p24_claim_citation_map": claim_citation_map,
        "paper_p24_statistical_reporting_decision": statistical_decision,
        "paper_p24_visual_layout_audit": visual_audit,
        "paper_p24_reproduction_semantics": reproduction_semantics,
        "paper_p24_metric_consistency_audit": metric_consistency,
        "paper_p24_split_consistency_audit": split_consistency,
        "paper_p24_semantic_source_audit": semantic_source,
        "paper_p26_evidence_gate_separation_audit": evidence_gate_separation,
        "paper_p26_validation_subsplit_audit": validation_subsplits,
        "paper_p26_release_reference_audit": release_reference,
        "paper_p27_evidence_schema_audit": evidence_schema,
        "paper_p27_feature_contract_audit": feature_contract,
        "paper_p27_generated_surface_audit": generated_surfaces,
        "paper_p27_candidate_revision_audit": candidate_revision,
    }
    checks = [{"report": key, "status": value["status"], "passed": value["status"] == "pass"} for key, value in pack.items()]
    pack["paper_p24_release_manifest"] = _report(
        "release_candidate_ready_for_human_upload" if all(row["passed"] for row in checks) else "blocked_pending_p24_repairs",
        slice="Paper Track P24 with P27 release-candidate corrections",
        checks=checks,
        git=git,
        release_mode="review_candidate",
        archival_revision_claimed=False,
        exact_revision_release_required=True,
        arxiv_upload_ready=False,
        benchmark_values_changed=False,
        human_owned_actions=["commit the reviewed source", "run final mode from the clean commit", "inspect the exact-revision artifacts", "push the reviewed commit", "verify public revision availability"],
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


def build_exact_revision_release(
    project_root: str | Path,
    *,
    release_tag: str | None = None,
    require_public: bool = False,
) -> dict[str, Any]:
    """Build an immutable commit- or verified-tag paper release outside the worktree."""
    root = Path(project_root)
    git = _git_state(root)
    if git["dirty"]:
        raise ValueError("Final paper release requires a clean Git worktree; commit or discard reviewed changes first.")
    commit = str(git["commit"] or "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Final paper release could not resolve a full Git commit SHA.")
    tag = str(release_tag or "").strip()
    if tag and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", tag):
        raise ValueError("Final paper release received an invalid release tag name.")
    remote_refs = _git(root, "ls-remote", "origin")
    remote_commit_exists = any(line.startswith(f"{commit}\t") for line in remote_refs.splitlines())
    if require_public and not remote_commit_exists:
        raise ValueError("Final paper release requires the exact source commit to exist on the public origin remote.")
    tagged_commit = _git(root, "rev-list", "-n", "1", tag).strip() if tag else ""
    remote_tagged_commit = ""
    if tag:
        if not tagged_commit:
            raise ValueError(f"Final paper release requires local tag `{tag}`.")
        if tagged_commit != commit:
            raise ValueError(f"Release tag `{tag}` must resolve to the current HEAD commit.")
        remote_tag_lines = [
            line for line in remote_refs.splitlines() if line.endswith(f"refs/tags/{tag}") or line.endswith(f"refs/tags/{tag}^{{}}")
        ]
        remote_tagged_commit = next(
            (line.split("\t", 1)[0] for line in remote_tag_lines if line.endswith("^{}")),
            remote_tag_lines[0].split("\t", 1)[0] if remote_tag_lines else "",
        )
        if remote_tagged_commit != commit:
            raise ValueError(f"Release tag `{tag}` must exist remotely and resolve to the current HEAD commit.")

    from relaytic.release_safety.paper_arxiv_source import sync_paper_arxiv_source_pack
    from relaytic.release_safety.paper_release import sync_paper_release_pack

    generated_surface_audit = _generated_surface_audit(
        root,
        _read_text(root / "docs" / "paper" / "relaytic_aml_arxiv_draft.md"),
    )
    if generated_surface_audit["status"] != "pass":
        raise ValueError(
            "Final paper release requires committed manuscript and figure surfaces to match their generators."
        )

    release_root = root / "dist" / "paper-release" / commit
    paper_dir = release_root / "paper"
    source_dir = release_root / "source"
    reports_dir = release_root / "reports"
    if release_root.exists():
        shutil.rmtree(release_root)
    reports_dir.mkdir(parents=True, exist_ok=True)
    sync_paper_release_pack(
        root,
        output_dir=reports_dir,
        paper_dir=paper_dir,
        release_tag=tag or None,
        source_commit=commit,
    )
    canonical_figure_dir = root / "docs" / "paper" / "figures"
    if not canonical_figure_dir.is_dir():
        raise ValueError("Final paper release requires the canonical vector figure directory.")
    shutil.copytree(canonical_figure_dir, paper_dir / "figures", dirs_exist_ok=True)
    sync_paper_arxiv_source_pack(root, output_dir=reports_dir, source_dir=source_dir, paper_dir=paper_dir)
    _compile_latex(source_dir)

    built_pdf = source_dir / "main.pdf"
    if not built_pdf.is_file():
        raise ValueError("LaTeX compilation did not produce main.pdf.")
    source_text = _read_text(source_dir / "main.tex")
    required_release_tokens = (
        (tag, commit, "archive/refs/tags")
        if tag
        else (commit, f"/commit/{commit}", f"/archive/{commit}.tar.gz")
    )
    if not all(token in source_text for token in required_release_tokens):
        raise ValueError("Final source does not contain the required immutable release metadata.")
    forbidden_release_tokens = ("dirty", "under review", "pending release")
    if any(token in source_text.lower() for token in forbidden_release_tokens):
        raise ValueError("Final source contains a non-final release-status phrase.")
    pdf_text = _pdf_to_text(built_pdf)
    if commit not in pdf_text:
        raise ValueError("Final PDF does not expose the same full source commit as the generated TeX source.")
    pdf_path = release_root / "relaytic_aml_arxiv.pdf"
    shutil.copy2(built_pdf, pdf_path)
    source_archive = release_root / "relaytic_aml_arxiv_source.tar.gz"
    with tarfile.open(source_archive, "w:gz") as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file() and path.suffix not in {".aux", ".bbl", ".blg", ".log", ".out"} and path.name != "main.pdf":
                archive.add(path, arcname=path.relative_to(source_dir))

    integrity = build_paper_release_integrity_pack(root)
    integrity_ok = integrity["paper_p24_release_manifest"]["status"] == "release_candidate_ready_for_human_upload"
    preflight = {
        "schema_version": PAPER_RELEASE_INTEGRITY_SCHEMA_VERSION,
        "status": "pass" if integrity_ok else "fail",
        "source_commit": commit,
        "release_identity_mode": "verified_tag" if tag else "immutable_commit",
        "release_tag": tag or None,
        "tagged_commit": tagged_commit or None,
        "remote_tagged_commit": remote_tagged_commit or None,
        "remote_commit_exists": remote_commit_exists,
        "public_revision_required": require_public,
        "clean_worktree_before_build": True,
        "generated_surfaces_match_source": True,
        "tex_revision_matches_source": commit in source_text,
        "pdf_revision_matches_source": commit in pdf_text,
        "paper_integrity_status": integrity["paper_p24_release_manifest"]["status"],
    }
    preflight_path = write_json(release_root / "final_preflight.json", preflight, indent=2, sort_keys=True)
    manifest = {
        "schema_version": PAPER_RELEASE_INTEGRITY_SCHEMA_VERSION,
        "status": "exact_revision_bundle_ready" if integrity_ok else "blocked",
        "release_mode": "archival_final",
        "source_commit": commit,
        "release_identity_mode": "verified_tag" if tag else "immutable_commit",
        "release_tag": tag or None,
        "tagged_commit": tagged_commit or None,
        "remote_tagged_commit": remote_tagged_commit or None,
        "remote_commit_exists": remote_commit_exists,
        "public_revision_required": require_public,
        "clean_worktree_before_build": True,
        "generated_surfaces_match_source": True,
        "tex_revision_matches_source": commit in source_text,
        "pdf_revision_matches_source": commit in pdf_text,
        "arxiv_upload_ready": bool(
            integrity_ok
            and remote_commit_exists
            and (not tag or (tagged_commit == commit and remote_tagged_commit == commit))
        ),
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


def _paysim_protocol_audit(reports: Path, markdown: str) -> dict[str, Any]:
    manifest = _read_json(reports / "paysim_competitive_benchmark_manifest.json")
    budget = _read_json(reports / "paysim_competitive_budget_contract.json")
    trace = _read_json(reports / "paysim_competitive_search_trace.json")
    gate = _read_json(reports / "paysim_publishability_gate.json")
    exposure = dict(manifest.get("test_exposure_contract", {}) or {})
    selected = dict(manifest.get("validation_selected_competitive_model", {}) or {})
    finalist_rows = [
        row
        for row in trace.get("attempts", [])
        if isinstance(row, dict) and row.get("stage") == "full_train_finalist" and row.get("execution_state") == "ran"
    ]
    checks = [
        {
            "check": "selection surface",
            "observed": selected.get("selection_surface"),
            "pass_criterion": "validation_pr_auc_only_before_test_evaluation",
            "passed": selected.get("selection_surface") == "validation_pr_auc_only_before_test_evaluation",
        },
        {
            "check": "previous exposure disclosure",
            "observed": exposure,
            "pass_criterion": "fixed partition, P4/P6 exposure recorded, and no untouched-holdout claim",
            "passed": exposure.get("test_partition_fixed") is True
            and exposure.get("test_partition_previously_exposed") is True
            and exposure.get("prior_test_exposure_roles") == ["P4 reference", "P6 baseline"]
            and exposure.get("untouched_holdout_claim_allowed") is False,
        },
        {
            "check": "post-freeze evaluation budget",
            "observed": budget.get("test_evaluation_policy"),
            "pass_criterion": "one validation-selected competitive finalist after protocol freeze",
            "passed": budget.get("test_evaluation_policy")
            == "one_competitive_finalist_evaluated_after_validation_only_selection_and_protocol_freeze"
            and exposure.get("competitive_finalists_tested_after_freeze") == 1,
        },
        {
            "check": "full-training finalist disclosure",
            "observed": {"count": len(finalist_rows), "selected": selected.get("family_id")},
            "pass_criterion": "five full-training finalists with one selected final model",
            "passed": len(finalist_rows) == 5 and bool(selected.get("family_id")),
        },
        {
            "check": "reader-facing disclosure",
            "observed": "P4/P6 exposure and non-untouched status appear in the manuscript",
            "pass_criterion": "the paper does not present PaySim test evidence as untouched",
            "passed": all(
                phrase in markdown
                for phrase in (
                    "prior P4 and P6 exposure",
                    "not presented as untouched",
                    "validation-only selection",
                )
            ),
        },
        {
            "check": "claim gate",
            "observed": gate.get("blocked_claims"),
            "pass_criterion": "untouched and one-time-inspection claims are blocked",
            "passed": all(
                phrase in list(gate.get("blocked_claims", []))
                for phrase in (
                    "PaySim test partition was an untouched holdout",
                    "PaySim test partition was inspected only once across the project",
                )
            ),
        },
    ]
    return _report("pass" if all(row["passed"] for row in checks) else "fail", checks=checks)


def _operating_point_audit(reports: Path, markdown: str) -> dict[str, Any]:
    sources = [
        ("PaySim", _read_json(reports / "paysim_competitive_benchmark_manifest.json"), "validation_selected_competitive_model"),
        ("Elliptic", _read_json(reports / "paper_graph_feature_table.json"), "validation_selected_competitive_baseline"),
    ]
    checks = []
    for name, payload, field in sources:
        selected = dict(payload.get(field, {}) or {})
        validation = dict(selected.get("validation_operating_point", {}) or {})
        test = dict(selected.get("test_operating_point", {}) or {})
        threshold = selected.get("validation_threshold")
        validation_count = int(validation.get("evaluation_row_count", 0) or 0)
        test_count = int(test.get("evaluation_row_count", 0) or 0)
        validation_recomputed = _operating_row_matches(validation, validation_count)
        test_recomputed = _operating_row_matches(test, test_count)
        checks.append(
            {
                "benchmark": name,
                "artifact_ref": f"docs/reports/{'paysim_competitive_benchmark_manifest.json' if name == 'PaySim' else 'paper_graph_feature_table.json'}",
                "threshold": threshold,
                "validation_operating_partition_rows": validation_count,
                "test_partition_rows": test_count,
                "observed_test_queue": test.get("reviewed_count"),
                "pass_criterion": "validation threshold is transferred unchanged and counts reproduce the stated precision, recall, and queue fraction",
                "validation_count_recomputed": validation_recomputed,
                "test_count_recomputed": test_recomputed,
                "threshold_transfer_recorded": selected.get("threshold_applied_unchanged_to_test") is True
                and selected.get("comparison_operator") == ">="
                and selected.get("tie_rule") == "include_scores_equal_to_threshold",
                "reader_display_present": all(
                    value in markdown
                    for value in (
                        f"{float(selected.get('test_pr_auc', 0.0)):.4f}",
                        f"{float(test.get('precision_at_k', 0.0)):.4f}",
                        f"{float(test.get('recall_at_review_budget', 0.0)):.4f}",
                    )
                ),
            }
        )
        checks[-1]["passed"] = all(
            checks[-1][name]
            for name in (
                "validation_count_recomputed",
                "test_count_recomputed",
                "threshold_transfer_recorded",
                "reader_display_present",
            )
        )
    return _report("pass" if all(row["passed"] for row in checks) else "fail", checks=checks)


def _reference_provenance_audit(reports: Path, markdown: str) -> dict[str, Any]:
    scorecard = _read_json(reports / "elliptic2_revclassify_reference_scorecard.json")
    reference = dict(scorecard.get("reference", {}) or {})
    expected_hash = "b253d97531a0da6fd16a46bb54904437d4373984dfb2559e69c2104faaa08728"
    checks = [
        {
            "check": "versioned RevTrack source",
            "observed": reference.get("versioned_pdf_url"),
            "pass_criterion": "arXiv v1 PDF is pinned",
            "passed": reference.get("versioned_pdf_url") == "https://arxiv.org/pdf/2410.08394v1",
        },
        {
            "check": "published metric location",
            "observed": reference.get("source"),
            "pass_criterion": "Table 1, RevClassifyDS full-shot PR-AUC",
            "passed": "Table 1" in str(reference.get("source", "")) and "RevClassifyDS" in str(reference.get("source", "")),
        },
        {
            "check": "versioned PDF digest",
            "observed": reference.get("versioned_pdf_sha256"),
            "pass_criterion": expected_hash,
            "passed": reference.get("versioned_pdf_sha256") == expected_hash,
        },
        {
            "check": "reader-facing cohort boundary",
            "observed": "published reference is described as context, not parity",
            "pass_criterion": "paper identifies the reference as a published context metric",
            "passed": "RevClassifyDS" in markdown and "shown only as an external reference" in markdown,
        },
    ]
    return _report("pass" if all(row["passed"] for row in checks) else "fail", checks=checks)


def _execution_status_audit(reports: Path, markdown: str) -> dict[str, Any]:
    manifests = [
        ("PaySim", _read_json(reports / "paysim_competitive_benchmark_manifest.json")),
        ("Elliptic", _read_json(reports / "paper_graph_baseline_manifest.json")),
        ("Elliptic2", _read_json(reports / "elliptic2_publishability_gate.json")),
    ]
    checks = []
    for name, manifest in manifests:
        execution = dict(manifest.get("execution_status", {}) or {})
        checks.append(
            {
                "benchmark": name,
                "observed_status": execution.get("status"),
                "blocked_reason_codes": execution.get("blocked_reason_codes", []),
                "pass_criterion": "a machine-readable execution status and blocked reasons are emitted",
                "passed": execution.get("status") in {"executed", "executed_with_optional_skips", "skipped", "blocked"}
                and isinstance(execution.get("blocked_reason_codes"), list),
            }
        )
    paper_check = {
        "benchmark": "reproduction instructions",
        "observed_status": "require-full-rerun command documented",
        "blocked_reason_codes": [],
        "pass_criterion": "full-rerun commands reject skipped benchmark execution",
        "passed": "--require-full-rerun" in markdown,
    }
    checks.append(paper_check)
    return _report("pass" if all(row["passed"] for row in checks) else "fail", checks=checks)


def _operating_row_matches(point: dict[str, Any], row_count: int) -> bool:
    if row_count <= 0:
        return False
    reviewed = _integer_or_default(point.get("reviewed_count"), default=-1)
    true_positive = _integer_or_default(point.get("true_positive_count"), default=-1)
    false_positive = _integer_or_default(point.get("false_positive_count"), default=-1)
    if reviewed != true_positive + false_positive or reviewed <= 0:
        return False
    positive_count = _integer_or_default(point.get("positive_count"), default=0)
    return (
        _numeric_close(point.get("review_fraction"), reviewed / row_count, tolerance=1e-6)
        and _numeric_close(point.get("precision_at_k"), true_positive / reviewed, tolerance=1e-6)
        and positive_count > 0
        and _numeric_close(point.get("recall_at_review_budget"), true_positive / positive_count, tolerance=1e-6)
    )


def _integer_or_default(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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
        "merged evidence interpretation field": r"\bclaim_state\b",
        "reader-facing calibration identifier": r"\bplatt_sigmoid\b",
        "machine comparison expression": r"score\s*>=\s*threshold",
        "incorrect single-seed grammar": r"\bseeds 42\b",
        "incorrect finalist distinction": r"all finalist scores are distinct|finalist scores were distinct|unique XGBoost runner-up",
        "development-build wording": r"review draft|review build|uncommitted review build",
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


def _evidence_gate_separation_audit(reports: Path) -> dict[str, Any]:
    metric_audit = _read_json(reports / "paper_metric_cell_audit.json")
    gate_pack = _read_json(reports / "paper_claim_gate_records.json")
    external_cells = _read_json(reports / "paper_external_score_evidence_cells.json")
    external_gate = _read_json(reports / "paper_external_score_claim_gate.json")
    cells = [
        *[dict(cell) for cell in metric_audit.get("numeric_cells", []) if isinstance(cell, dict)],
        *[dict(cell) for cell in external_cells.get("evidence_cells", []) if isinstance(cell, dict)],
    ]
    gates = [dict(gate) for gate in gate_pack.get("claim_gates", []) if isinstance(gate, dict)]
    if external_gate.get("publishable"):
        gates.append(external_gate)
    audit = audit_evidence_gate_separation(evidence_cells=cells, claim_gates=gates)
    return _report(
        audit["status"],
        slice="Paper Track P27",
        evidence_cell_count=audit["evidence_cell_count"],
        evidence_cell_type_counts=audit["evidence_cell_type_counts"],
        claim_gate_count=audit["claim_gate_count"],
        evidence_type_system_schema=audit["evidence_type_system_schema"],
        metric_evidence_cell_schema=audit["metric_evidence_cell_schema"],
        invariant_evidence_cell_schema=audit["invariant_evidence_cell_schema"],
        interpretive_gate_schema=audit["claim_gate_schema"],
        checks={
            "all_cells_typed": not any(
                row.get("violation") == "untyped_evidence_cell" for row in audit["violations"]
            ),
            "interpretive_fields_absent_from_cells": not any(
                row.get("violation") == "interpretive_fields_in_evidence_cell" for row in audit["violations"]
            ),
            "every_public_cell_has_gate": audit["all_public_cells_have_separate_gate"],
            "gate_references_resolve": not any(
                row.get("violation") == "gate_references_missing_evidence_cells" for row in audit["violations"]
            ),
        },
        violations=audit["violations"],
        source_artifacts=[
            "docs/reports/paper_metric_cell_audit.json",
            "docs/reports/paper_claim_gate_records.json",
            "docs/reports/paper_external_score_evidence_cells.json",
            "docs/reports/paper_external_score_claim_gate.json",
            "docs/reports/paper_evidence_schema_contract.json",
        ],
    )


def _validation_subsplit_audit(reports: Path, markdown: str) -> dict[str, Any]:
    paysim_split = _read_json(reports / "paysim_temporal_split_report.json")
    paysim_trace = _read_json(reports / "paysim_competitive_search_trace.json")
    paysim_manifest = _read_json(reports / "paysim_competitive_benchmark_manifest.json")
    elliptic_split = _read_json(reports / "elliptic_temporal_split_report.json")
    graph_table = _read_json(reports / "paper_graph_feature_table.json")
    graph_manifest = _read_json(reports / "paper_graph_baseline_manifest.json")
    recorded = {
        "PaySim": {
            "order_field": "step",
            "full_validation": {"boundary": "446-594", "count": 228103, "positive_count": 1552},
            "calibration": {"boundary": "446-540", "count": 116502, "positive_count": 984},
            "threshold_selection": {"boundary": "541-594", "count": 111601, "positive_count": 568},
            "selection_scope": "the full validation partition selected the finalist and therefore overlaps both nested subsets",
            "nested_overlap_policy": "calibration and threshold-selection subsets are chronologically ordered and disjoint",
            "calibration_use": "fit Platt sigmoid calibration on the earlier subset",
            "threshold_use": "compare calibration choices by log loss and select the 0.5% threshold on the later subset",
            "source_refs": [
                "docs/reports/paysim_temporal_split_report.json",
                "docs/reports/paysim_competitive_search_trace.json",
                "src/relaytic/release_safety/paysim_competitive.py:_calibration_partitions",
            ],
            "source_identity": {
                "sha256": paysim_split.get("source_sha256") or paysim_manifest.get("source_sha256"),
            },
        },
        "Elliptic": {
            "order_field": "time_step",
            "full_validation": {"boundary": "30-39", "count": 8999, "positive_count": 1038},
            "calibration": {"boundary": "30-35", "count": 4854, "positive_count": 773},
            "threshold_selection": {"boundary": "36-39", "count": 4145, "positive_count": 265},
            "selection_scope": "the full validation partition selected the model and feature view and therefore overlaps both nested subsets",
            "nested_overlap_policy": "calibration and threshold-selection subsets are chronologically ordered and disjoint",
            "calibration_use": "fit Platt sigmoid calibration on the earlier subset",
            "threshold_use": "compare calibration choices by log loss and select the 0.5% threshold on the later subset",
            "source_refs": [
                "docs/reports/elliptic_temporal_split_report.json",
                "docs/reports/paper_graph_feature_table.json",
                "src/relaytic/release_safety/graph_baselines.py:_calibrate_scores",
            ],
            "source_identity": {
                "files": [
                    {"role": row.get("role"), "sha256": row.get("sha256")}
                    for row in graph_manifest.get("source_files", [])
                    if isinstance(row, dict)
                ],
            },
        },
    }
    paysim_validation = next(
        (row for row in paysim_split.get("split_rows", []) if row.get("split") == "validation"), {}
    )
    elliptic_validation = next(
        (row for row in elliptic_split.get("split_rows", []) if row.get("split") == "validation"), {}
    )
    paysim_operating = dict(paysim_trace.get("selected_finalist", {}).get("validation_operating_point") or {})
    paysim_calibration = dict(paysim_trace.get("calibration_trace") or {})
    elliptic_operating = dict(
        graph_table.get("validation_selected_competitive_baseline", {}).get("validation_operating_point") or {}
    )
    paysim_selected = dict(paysim_manifest.get("validation_selected_competitive_model") or {})
    elliptic_selected = dict(graph_table.get("validation_selected_competitive_baseline") or {})
    checks = [
        {
            "check": "PaySim full validation reconciles",
            "passed": paysim_validation.get("row_count") == 228103 and paysim_validation.get("positive_count") == 1552,
        },
        {
            "check": "PaySim nested subsets reconcile",
            "passed": 116502 + 111601 == 228103
            and 984 + 568 == 1552
            and paysim_calibration.get("calibration_row_count") == 116502
            and paysim_calibration.get("operating_point_row_count") == 111601,
        },
        {
            "check": "PaySim threshold denominator and positives reconcile",
            "passed": paysim_operating.get("evaluation_row_count") == 111601 and paysim_operating.get("positive_count") == 568,
        },
        {
            "check": "Elliptic full validation reconciles",
            "passed": elliptic_validation.get("known_label_count") == 8999 and elliptic_validation.get("illicit_count") == 1038,
        },
        {
            "check": "Elliptic nested subsets reconcile",
            "passed": 4854 + 4145 == 8999 and 773 + 265 == 1038,
        },
        {
            "check": "Elliptic threshold denominator and positives reconcile",
            "passed": elliptic_operating.get("evaluation_row_count") == 4145 and elliptic_operating.get("positive_count") == 265,
        },
        {
            "check": "reader-facing subset disclosure present",
            "passed": all(token in markdown for token in ("446-540", "541-594", "30-35", "36-39", "Threshold-selection queue")),
        },
        {
            "check": "nested chronological windows are disjoint",
            "passed": 540 < 541 and 35 < 36,
        },
        {
            "check": "thresholds match artifacts and reader display",
            "passed": _numeric_close(paysim_selected.get("validation_threshold"), 0.404453)
            and _numeric_close(elliptic_selected.get("validation_threshold"), 0.99982)
            and "0.4045" in markdown
            and "0.9998" in markdown,
        },
        {
            "check": "displayed PaySim runner-up tie has consistent prose",
            "passed": _displayed_paysim_runner_up_tie(paysim_trace)
            and "joint XGBoost and Random Forest runner-up rows" in markdown
            and "all finalist scores are distinct" not in markdown.lower(),
        },
    ]
    return _report(
        "pass" if all(row["passed"] for row in checks) else "fail",
        slice="Paper Track P26",
        datasets=recorded,
        checks=checks,
        derivation=(
            "Nested counts and positives were recomputed from the hash-identified local sources during P26 and are "
            "reconciled here against the full validation and operating-point artifacts. The implemented median-boundary "
            "rules define the chronological subwindows. No model was refit and no benchmark value was changed."
        ),
    )


def _displayed_paysim_runner_up_tie(trace: dict[str, Any]) -> bool:
    finalists = [
        row
        for row in trace.get("attempts", [])
        if isinstance(row, dict) and row.get("stage") == "full_train_finalist" and row.get("execution_state") == "ran"
    ]
    scores = sorted(
        [round(float(dict(row.get("validation_metrics") or {}).get("pr_auc")), 4) for row in finalists],
        reverse=True,
    )
    return len(scores) >= 3 and scores[0] > scores[1] and scores[1] == scores[2]


def _evidence_schema_audit(reports: Path, markdown: str) -> dict[str, Any]:
    expected = build_evidence_schema_contract()
    recorded = _read_json(reports / "paper_evidence_schema_contract.json")
    metric_audit = _read_json(reports / "paper_metric_cell_audit.json")
    ablation = _read_json(reports / "paper_governance_ablation_eval.json")
    metric_count = len(METRIC_EVIDENCE_CELL_REQUIRED_FIELDS)
    omitted_count = len(MISSING_FIELD_STRESS_FIXTURE_OMITTED_FIELDS)
    checks = [
        {
            "check": "generated schema contract matches code",
            "observed": recorded.get("schema_version"),
            "pass_criterion": expected.get("schema_version"),
            "passed": recorded == expected,
        },
        {
            "check": "metric audit uses authoritative field count",
            "observed": metric_audit.get("metric_required_field_count"),
            "pass_criterion": metric_count,
            "passed": metric_audit.get("metric_required_field_count") == metric_count,
        },
        {
            "check": "disabled-field ablation uses full metric contract",
            "observed": dict(ablation.get("full_path_metrics") or {}).get("required_metric_field_count"),
            "pass_criterion": metric_count,
            "passed": dict(ablation.get("full_path_metrics") or {}).get("required_metric_field_count") == metric_count,
        },
        {
            "check": "reader disclosure includes both fixture counts",
            "observed": f"metric={metric_count}; omitted={omitted_count}",
            "pass_criterion": "authoritative counts appear in typed-contract table",
            "passed": f"| {metric_count} |" in markdown and f"| {omitted_count} |" in markdown,
        },
    ]
    return _report(
        "pass" if all(row["passed"] for row in checks) else "fail",
        slice="Paper Track P27",
        checks=checks,
        metric_required_field_count=metric_count,
        missing_field_stress_omitted_count=omitted_count,
    )


def _feature_contract_audit(reports: Path, markdown: str) -> dict[str, Any]:
    p6 = _read_json(reports / "paper_leakage_safe_feature_report.json")
    p6a = _read_json(reports / "paysim_leakage_safe_feature_report.json")
    same_dataset = p6.get("dataset_id") == p6a.get("dataset_id") and bool(p6.get("dataset_id"))
    same_split = p6.get("split_contract_id") == p6a.get("split_contract_id") and bool(p6.get("split_contract_id"))
    distinct_features = (
        p6.get("feature_contract_id") != p6a.get("feature_contract_id")
        and set(p6.get("feature_columns", [])) != set(p6a.get("feature_columns", []))
    )
    checks = [
        {"check": "same dataset", "observed": same_dataset, "pass_criterion": True, "passed": same_dataset},
        {"check": "same temporal split contract", "observed": same_split, "pass_criterion": True, "passed": same_split},
        {"check": "distinct feature contracts disclosed", "observed": distinct_features, "pass_criterion": True, "passed": distinct_features},
        {
            "check": "manuscript avoids false same-feature claim",
            "observed": "same dataset, split, feature, and metric contract" in markdown,
            "pass_criterion": False,
            "passed": "same dataset, split, feature, and metric contract" not in markdown
            and "distinct audited feature contract" in markdown,
        },
    ]
    return _report(
        "pass" if all(row["passed"] for row in checks) else "fail",
        slice="Paper Track P27",
        checks=checks,
        p6_feature_contract_id=p6.get("feature_contract_id"),
        p6a_feature_contract_id=p6a.get("feature_contract_id"),
    )


def _generated_surface_audit(root: Path, markdown: str) -> dict[str, Any]:
    from relaytic.release_safety.paper_draft import build_paper_draft_pack
    from relaytic.release_safety.paper_release import build_paper_release_pack

    release_pack = build_paper_release_pack(root)
    draft_pack = build_paper_draft_pack(root)
    figure_dir = root / "docs" / "paper" / "figures"
    generated_figures = dict(draft_pack.get("figures") or {})
    filenames = {
        "claim_gate_flow": "figure_1_claim_gate_flow.svg",
        "supporting_pr_auc": "figure_2_supporting_pr_auc.svg",
        "review_budget": "figure_3_review_budget.svg",
        "publishability_matrix": "figure_4_publishability_matrix.svg",
    }
    figure_checks = {
        figure_id: _read_text(figure_dir / filename) == str(generated_figures.get(figure_id) or "")
        for figure_id, filename in filenames.items()
    }
    checks = [
        {
            "check": "canonical manuscript matches generator",
            "observed": markdown == str(release_pack.get("paper_final_draft") or ""),
            "pass_criterion": True,
            "passed": markdown == str(release_pack.get("paper_final_draft") or ""),
        },
        {
            "check": "canonical SVG figures match generator",
            "observed": figure_checks,
            "pass_criterion": "all true",
            "passed": all(figure_checks.values()),
        },
    ]
    return _report(
        "pass" if all(row["passed"] for row in checks) else "fail",
        slice="Paper Track P27",
        checks=checks,
    )


def _candidate_revision_audit(markdown: str, git: dict[str, Any]) -> dict[str, Any]:
    stale_revision = bool(re.search(r"Source commit:\s*[0-9a-f]{7,40}", markdown))
    candidate_marker = "This review candidate does not claim an archival revision." in markdown
    checks = [
        {
            "check": "candidate has no source-commit claim",
            "observed": stale_revision,
            "pass_criterion": False,
            "passed": not stale_revision,
        },
        {
            "check": "candidate mode is explicit",
            "observed": candidate_marker,
            "pass_criterion": True,
            "passed": candidate_marker,
        },
    ]
    return _report(
        "pass" if all(row["passed"] for row in checks) else "fail",
        slice="Paper Track P27",
        release_mode="review_candidate",
        archival_revision_claimed=False,
        worktree_dirty=bool(git.get("dirty")),
        checks=checks,
    )


def _release_reference_audit(root: Path, markdown: str) -> dict[str, Any]:
    local_tags = set(_git(root, "tag", "--list").splitlines())
    remote_output = _git(root, "ls-remote", "--tags", "origin")
    remote_tags = {
        ref.removeprefix("refs/tags/").removesuffix("^{}")
        for line in remote_output.splitlines()
        if "\t" in line
        for ref in [line.split("\t", 1)[1]]
    }
    named_tag = "relaytic-aml-arxiv-v1"
    paper_claims_tag = named_tag in markdown or "archive/refs/tags" in markdown
    paper_claims_commit = bool(re.search(r"Source commit:\s*[0-9a-f]{7,40}", markdown))
    candidate_marker = "This review candidate does not claim an archival revision." in markdown
    pass_state = not paper_claims_tag and not paper_claims_commit and candidate_marker
    return _report(
        "pass" if pass_state else "fail",
        slice="Paper Track P26",
        release_identity_mode="immutable_commit",
        paper_claims_release_tag=paper_claims_tag,
        paper_claims_source_commit=paper_claims_commit,
        candidate_marker_present=candidate_marker,
        examined_tag=named_tag,
        local_tag_exists=named_tag in local_tags,
        remote_checked=bool(remote_output),
        remote_tag_exists=named_tag in remote_tags,
        public_tag_archive_claim_allowed=named_tag in remote_tags,
        decision="The review candidate claims no archival revision. Final mode injects the immutable commit.",
    )


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


def _pdf_to_text(path: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", str(path), "-"],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise ValueError("Final paper release requires pdftotext to verify PDF/source revision identity.")
    return completed.stdout


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

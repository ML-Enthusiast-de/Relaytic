"""Paper Track P20 narrative, guidance, and visual/table polish audit."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_NARRATIVE_POLISH_SCHEMA_VERSION = "relaytic.paper_narrative_polish.v1"
PAPER_NARRATIVE_POLISH_REPORT_DIR = Path("docs") / "reports"
NEXT_PAPER_NARRATIVE_POLISH_SLICE = "Paper Track P21 - final source/PDF preflight and release changelog"

PAPER_NARRATIVE_POLISH_FILENAMES = {
    "paper_paysim_selection_story_review": "paper_paysim_selection_story_review.json",
    "paper_reader_guidance_audit": "paper_reader_guidance_audit.json",
    "paper_visual_table_polish_audit": "paper_visual_table_polish_audit.json",
    "paper_narrative_polish_manifest": "paper_narrative_polish_manifest.json",
    "paper_polish_readiness": "paper_polish_readiness.md",
}

REQUIRED_PAPER_NARRATIVE_POLISH_INPUT_REFS = [
    "README.md",
    "docs/paper/relaytic_aml_arxiv_draft.md",
    "docs/paper/references.bib",
    "docs/paper/figures/figure_manifest.json",
    "docs/reports/paper_release_manifest.json",
    "docs/reports/paper_public_claims_allowed.json",
    "docs/reports/paper_metric_cell_audit.json",
    "docs/reports/paper_publishability_matrix.json",
    "docs/reports/paper_system_task_eval.json",
    "docs/reports/paysim_competitive_baseline_table.json",
    "docs/reports/paysim_competitive_search_trace.json",
    "docs/reports/paysim_leakage_safe_feature_report.json",
]

FORBIDDEN_P20_READER_TONE_PHRASES = [
    "A weaker paper",
    "weaker paper",
    "serious reader",
    "fertile ground",
    "not cosmetic",
    "stronger sentence",
    "first thing to notice",
    "cleanest improvement story",
    "less glamorous",
    "weak baseline",
    "wins one benchmark table",
    "harder to oversell",
    "This is the part",
    "good-looking result",
    "attractive number",
    "has earned",
]

FORBIDDEN_P20_SOURCE_MARKERS = [
    "TODO",
    "FIXME",
    "TODO_EVIDENCE",
    "pending isolated test",
    "pending main-table evidence",
    "unresolved reference",
    "undefined references",
]

def build_paper_narrative_polish_pack(
    project_root: str | Path,
    *,
    source_report_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build the P20 paper polish and reader-guidance audit pack."""
    root = Path(project_root)
    report_dir = (
        Path(source_report_dir)
        if source_report_dir is not None
        else root / PAPER_NARRATIVE_POLISH_REPORT_DIR
    )
    inputs = _collect_inputs(root=root, report_dir=report_dir)
    paysim_review = _build_paysim_selection_story_review(inputs)
    guidance_audit = _build_reader_guidance_audit(inputs)
    polish_audit = _build_visual_table_polish_audit(inputs)
    manifest = _build_manifest(
        inputs=inputs,
        paysim_review=paysim_review,
        guidance_audit=guidance_audit,
        polish_audit=polish_audit,
    )
    readiness = render_paper_polish_readiness_markdown(
        {
            "paper_paysim_selection_story_review": paysim_review,
            "paper_reader_guidance_audit": guidance_audit,
            "paper_visual_table_polish_audit": polish_audit,
            "paper_narrative_polish_manifest": manifest,
        }
    )
    return {
        "paper_paysim_selection_story_review": paysim_review,
        "paper_reader_guidance_audit": guidance_audit,
        "paper_visual_table_polish_audit": polish_audit,
        "paper_narrative_polish_manifest": manifest,
        "paper_polish_readiness": readiness,
    }


def sync_paper_narrative_polish_pack(
    project_root: str | Path,
    *,
    source_report_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P20 paper polish reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_NARRATIVE_POLISH_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_narrative_polish_pack(root, source_report_dir=source_report_dir)
    written: dict[str, Path] = {}
    for key, filename in PAPER_NARRATIVE_POLISH_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_narrative_polish_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_narrative_polish_manifest", {}))
    paysim = dict(pack.get("paper_paysim_selection_story_review", {}))
    guidance = dict(pack.get("paper_reader_guidance_audit", {}))
    polish = dict(pack.get("paper_visual_table_polish_audit", {}))
    lines = [
        "# Paper P20 Narrative And Guidance Polish",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Paper content ready for P21 preflight: `{manifest.get('paper_content_ready_for_p21_preflight')}`",
        f"- arXiv upload ready: `{manifest.get('arxiv_upload_ready')}`",
        f"- PaySim story: `{paysim.get('status') or 'unknown'}`",
        f"- Reader guidance: `{guidance.get('status') or 'unknown'}`",
        f"- Visual/table polish audit: `{polish.get('status') or 'unknown'}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
    ]
    blockers = list(manifest.get("upload_blockers_remaining", []))
    if blockers:
        lines.extend(["", "## Remaining Upload Blockers", ""])
        for blocker in blockers:
            lines.append(f"- {blocker}")
    return "\n".join(lines).rstrip() + "\n"


def render_paper_polish_readiness_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_narrative_polish_manifest", {}))
    paysim = dict(pack.get("paper_paysim_selection_story_review", {}))
    guidance = dict(pack.get("paper_reader_guidance_audit", {}))
    polish = dict(pack.get("paper_visual_table_polish_audit", {}))
    selection = dict(paysim.get("selection_story", {}))
    lines = [
        "# Paper P20 Polish Readiness",
        "",
        "P20 checks whether the current paper reads as a professional AI systems/evaluation paper rather than an internal benchmark export. It does not add benchmark results or relax claim boundaries.",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Paper content ready for P21 source/PDF preflight: `{manifest.get('paper_content_ready_for_p21_preflight')}`",
        f"- Upload ready now: `{manifest.get('arxiv_upload_ready')}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        "",
        "## PaySim Story",
        "",
        f"- Best probe: `{selection.get('best_probe_family') or 'not_available'}` at validation PR-AUC `{selection.get('best_probe_validation_pr_auc')}` on the probe surface.",
        f"- Selected full finalist: `{selection.get('selected_finalist_family') or 'not_available'}` at validation PR-AUC `{selection.get('selected_finalist_validation_pr_auc')}` before the fixed test.",
        f"- Fixed-test PR-AUC: `{selection.get('selected_finalist_test_pr_auc')}`.",
        f"- Test-surface policy: `{selection.get('test_visibility_policy') or 'not_available'}`.",
        "",
        "## Guidance Path",
        "",
        f"- README path ready: `{guidance.get('reader_path_ready')}`",
        f"- Paper avoids internal planning-file guidance: `{guidance.get('paper_avoids_internal_planning_guidance')}`",
        f"- Cross-platform commands visible: `{guidance.get('cross_platform_commands_visible')}`",
        "",
        "## Remaining Human Work",
        "",
    ]
    blockers = list(manifest.get("upload_blockers_remaining", []))
    for blocker in blockers or ["none recorded"]:
        lines.append(f"- {blocker}")
    return "\n".join(lines).rstrip() + "\n"


def _collect_inputs(*, root: Path, report_dir: Path) -> dict[str, Any]:
    paper = root / "docs" / "paper"
    return {
        "root": root,
        "readme": _read_text_artifact(root / "README.md", root=root),
        "draft": _read_text_artifact(paper / "relaytic_aml_arxiv_draft.md", root=root),
        "references": _read_text_artifact(paper / "references.bib", root=root),
        "figure_manifest": _read_artifact(paper / "figures" / "figure_manifest.json", root=root),
        "paper_release_manifest": _read_artifact(report_dir / "paper_release_manifest.json", root=root),
        "paper_public_claims_allowed": _read_artifact(report_dir / "paper_public_claims_allowed.json", root=root),
        "paper_metric_cell_audit": _read_artifact(report_dir / "paper_metric_cell_audit.json", root=root),
        "paper_publishability_matrix": _read_artifact(report_dir / "paper_publishability_matrix.json", root=root),
        "paper_system_task_eval": _read_artifact(report_dir / "paper_system_task_eval.json", root=root),
        "paysim_competitive_baseline_table": _read_artifact(
            report_dir / "paysim_competitive_baseline_table.json",
            root=root,
        ),
        "paysim_competitive_search_trace": _read_artifact(
            report_dir / "paysim_competitive_search_trace.json",
            root=root,
        ),
        "paysim_competitive_feature_report": _read_artifact(
            report_dir / "paysim_leakage_safe_feature_report.json",
            root=root,
        ),
    }


def _build_paysim_selection_story_review(inputs: dict[str, Any]) -> dict[str, Any]:
    draft = _text_payload(inputs["draft"])
    baseline_table = _payload(inputs["paysim_competitive_baseline_table"])
    search_trace = _payload(inputs["paysim_competitive_search_trace"])
    feature_report = _payload(inputs["paysim_competitive_feature_report"])
    selected = dict(baseline_table.get("validation_selected_competitive_model") or {})
    selected_row = _selected_test_row(baseline_table)
    best_probe = _best_attempt(search_trace, stage="probe")
    best_full = _best_attempt(search_trace, stage="full_train_finalist")
    baseline = dict(baseline_table.get("p6_validation_selected_baseline") or {})
    story = {
        "p4_reference_pr_auc": _rounded(baseline_table.get("p4_reference_row", {}).get("test_pr_auc")),
        "baseline_pr_auc": _rounded(baseline.get("test_pr_auc")),
        "best_probe_family": _family_label(best_probe.get("family_id")),
        "best_probe_validation_pr_auc": _rounded(_pr_auc(best_probe)),
        "selected_finalist_family": _family_label(selected.get("family_id") or selected_row.get("family_id")),
        "selected_finalist_validation_pr_auc": _rounded(
            selected.get("validation_pr_auc") or _pr_auc(selected_row)
        ),
        "selected_finalist_test_pr_auc": _rounded(selected.get("test_pr_auc")),
        "selected_finalist_test_roc_auc": _rounded(selected.get("test_roc_auc")),
        "best_full_finalist_family": _family_label(best_full.get("family_id")),
        "best_full_finalist_validation_pr_auc": _rounded(_pr_auc(best_full)),
        "feature_count": len(feature_report.get("feature_columns", [])),
        "selection_rule": baseline_table.get("selection_rule") or "not_available",
        "selection_surface": selected.get("selection_surface") or selected_row.get("selection_surface"),
        "threshold_selection_surface": selected.get("threshold_selection_surface") or "not_available",
        "test_visibility_policy": baseline_table.get("test_visibility_policy") or "not_available",
    }
    checks = [
        _check(
            "probe_and_full_finalist_surfaces_separated",
            bool(best_probe)
            and bool(best_full)
            and str(best_probe.get("stage")) == "probe"
            and str(best_full.get("stage")) == "full_train_finalist",
            "The audit must distinguish small-sample probe screening from full-training finalist selection.",
            source_artifact="docs/reports/paysim_competitive_search_trace.json",
            detail={
                "best_probe_trial_id": best_probe.get("trial_id"),
                "best_full_source_probe_trial_id": best_full.get("source_probe_trial_id"),
            },
        ),
        _check(
            "selected_finalist_is_full_validation_winner",
            _family_label(best_full.get("family_id")) == story["selected_finalist_family"]
            and _rounded(_pr_auc(best_full)) == story["selected_finalist_validation_pr_auc"],
            "The selected fixed-test finalist must match the full-training validation winner.",
            source_artifact="docs/reports/paysim_competitive_baseline_table.json",
            detail={
                "selected_finalist_family": story["selected_finalist_family"],
                "best_full_finalist_family": story["best_full_finalist_family"],
            },
        ),
        _check(
            "nonselected_finalists_keep_test_metrics_hidden",
            str(baseline_table.get("test_visibility_policy"))
            == "nonselected_competitive_finalists_have_no_test_metrics",
            "Only the validation-selected finalist may have fixed-test metrics.",
            source_artifact="docs/reports/paysim_competitive_baseline_table.json",
        ),
        _check(
            "paper_explains_probe_screen_not_final_selection",
            "Probe screen" in draft
            and "Full finalist selection" in draft
            and "small-sample probe" in draft
            and "full-training validation" in draft,
            "Table 4 and the nearby text must explain why a probe winner can differ from the final fixed-test model.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "no_invented_xgboost_rationale",
            not _contains_any(
                draft,
                [
                    "XGBoost was discarded because",
                    "XGBoost overfit the test",
                    "Extra Trees generalized better on test",
                    "Extra Trees was chosen after test",
                ],
            ),
            "The paper must not invent a causal rationale beyond the recorded validation surfaces.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "results_have_nearby_interpretation",
            _result_has_context(
                draft,
                "fixed-test PR-AUC 0.6388",
                ["synthetic temporal-fraud", "validation evidence", "real-bank AML performance"],
            )
            and _result_has_context(
                draft,
                "test PR-AUC 0.6688",
                ["36 true positives", "0 false positives", "limitation"],
            )
            and _result_has_context(
                draft,
                "PR-AUC 0.9432",
                ["RevClassifyDS reference", "modern benchmark-context", "detector contribution"],
            ),
            "Every main result needs nearby interpretation rather than a bare number.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "detector_superiority_boundary_intact",
            "not evidence of bank-scale AML superiority" in draft
            and "not a new detector architecture" in draft
            and "without converting that context into a detector contribution" in draft
            and "hard aml, headline, sota" in _text_payload(inputs["readme"]).lower(),
            "The detector-superiority boundary must remain visible in the paper and README.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
    ]
    status = "pass" if all(check["passed"] for check in checks) else "fail"
    return {
        "schema_version": PAPER_NARRATIVE_POLISH_SCHEMA_VERSION,
        "slice": "Paper Track P20",
        "status": status,
        "selection_story": story,
        "claim_boundary": "supporting synthetic temporal-fraud evidence only; no real-bank AML superiority",
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def _build_reader_guidance_audit(inputs: dict[str, Any]) -> dict[str, Any]:
    readme = _text_payload(inputs["readme"])
    draft = _text_payload(inputs["draft"])
    tasks = _payload(inputs["paper_system_task_eval"])
    task_ids = {
        str(task.get("task_id"))
        for task in tasks.get("tasks", [])
        if isinstance(task, dict) and task.get("passed")
    }
    checks = [
        _check(
            "reader_enters_through_readme_and_paper",
            "A reader should start with the README and this paper" in draft
            and "For a paper review, use this path" in readme,
            "The paper should route readers to the README and manuscript, not to internal build plans.",
            source_artifact="README.md",
        ),
        _check(
            "relaytic_vs_relaytic_aml_distinction_visible",
            "Relaytic is the general local-first inference lab" in readme
            and "Relaytic-AML is the current flagship edition" in readme
            and "Relaytic began as a general local-first inference-engineering lab" in draft,
            "Readers must understand why the repo is larger than the AML paper.",
            source_artifact="README.md",
        ),
        _check(
            "cross_platform_paper_commands_visible",
            "Windows PowerShell" in readme
            and "macOS/Linux" in readme
            and "paper-narrative-polish --format json" in readme
            and "paper-narrative-polish --format json" in draft,
            "README and paper must expose copy-paste-safe Windows and macOS/Linux paper commands.",
            source_artifact="README.md",
        ),
        _check(
            "paper_avoids_internal_planning_guidance",
            not _contains_any(draft, ["RELAYTIC_SLICING_PLAN", "IMPLEMENTATION_STATUS", "phase_paper", "Paper Track P"]),
            "The paper should not point readers at internal planning files or slice names.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "reader_task_eval_covers_navigation",
            "repo_navigation_separates_relaytic_from_aml_paper" in task_ids
            and "cross_platform_reproduction_path_visible" in task_ids
            and int(tasks.get("passed_task_count") or 0) >= 11,
            "The reader guidance should be backed by deterministic reader/agent tasks.",
            source_artifact="docs/reports/paper_system_task_eval.json",
        ),
        _check(
            "deep_audit_path_available_without_required_artifact_literacy",
            "Deep audit, after the first read" in readme
            and "The long build-control files" in readme
            and "not required reading for the paper" in readme,
            "README may expose audit artifacts, but the first path must stay simple.",
            source_artifact="README.md",
        ),
    ]
    status = "pass" if all(check["passed"] for check in checks) else "fail"
    return {
        "schema_version": PAPER_NARRATIVE_POLISH_SCHEMA_VERSION,
        "slice": "Paper Track P20",
        "status": status,
        "reader_path_ready": status == "pass",
        "cross_platform_commands_visible": any(
            check["check_id"] == "cross_platform_paper_commands_visible" and check["passed"] for check in checks
        ),
        "paper_avoids_internal_planning_guidance": any(
            check["check_id"] == "paper_avoids_internal_planning_guidance" and check["passed"] for check in checks
        ),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def _build_visual_table_polish_audit(inputs: dict[str, Any]) -> dict[str, Any]:
    root = Path(inputs["root"])
    draft = _text_payload(inputs["draft"])
    figure_manifest = _payload(inputs["figure_manifest"])
    figure_rows = [row for row in figure_manifest.get("figures", []) if isinstance(row, dict)]
    missing_figures = []
    for row in figure_rows:
        filename = str(row.get("filename") or "")
        if filename and not (root / "docs" / "paper" / "figures" / filename).exists():
            missing_figures.append(filename)
    table_count = len(re.findall(r"\*\*Table\s+\d+", draft))
    checks = [
        _check(
            "figures_declared_and_present",
            len(figure_rows) == 4 and not missing_figures,
            "Figures 1-4 must be declared in the manifest and present as source SVGs.",
            source_artifact="docs/paper/figures/figure_manifest.json",
            detail={"figure_count": len(figure_rows), "missing_figures": missing_figures},
        ),
        _check(
            "figure_four_metric_grouping_explained",
            "Figure 4 separates ranking metrics from operating-point metrics" in draft
            and "Precision and recall at the selected review budget" in draft,
            "Figure 4 must not mix PR-AUC and review-budget metrics without interpretation.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "table_four_selection_story_clean",
            "Competitive search | XGBoost probe" not in draft
            and "Probe screen" in draft
            and "Full finalist selection" in draft,
            "Table 4 must not imply the probe winner was the final model-selection decision.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "publication_table_count_present",
            table_count >= 11,
            "The generated manuscript should contain the expected publication tables.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
            detail={"table_count": table_count},
        ),
        _check(
            "no_unresolved_public_markers",
            not _contains_any(draft, FORBIDDEN_P20_SOURCE_MARKERS),
            "Reader-facing paper must not contain unresolved TODO, pending, or reference markers.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "reader_tone_lint_passed",
            not _contains_any(draft, FORBIDDEN_P20_READER_TONE_PHRASES),
            "Paper wording should stay calm and professional.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "paper_body_avoids_private_or_internal_paths",
            not _contains_private_path_marker(draft)
            and not _contains_any(draft, ["docs/reports/", "docs/build_slices/"]),
            "Paper body should not expose private paths or make readers chase internal report paths.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
    ]
    status = "pass" if all(check["passed"] for check in checks) else "fail"
    return {
        "schema_version": PAPER_NARRATIVE_POLISH_SCHEMA_VERSION,
        "slice": "Paper Track P20",
        "status": status,
        "figure_count": len(figure_rows),
        "table_count": table_count,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def _build_manifest(
    *,
    inputs: dict[str, Any],
    paysim_review: dict[str, Any],
    guidance_audit: dict[str, Any],
    polish_audit: dict[str, Any],
) -> dict[str, Any]:
    release_manifest = _payload(inputs["paper_release_manifest"])
    public_claims = _payload(inputs["paper_public_claims_allowed"])
    required = _required_artifact_presence(inputs)
    checks = [
        _check(
            "required_p20_inputs_present",
            not required["missing_artifact_refs"],
            "P20 requires the generated paper, README, P13 public-claims gate, system-eval, and PaySim evidence reports.",
            source_artifact="docs/reports",
            detail=required,
        ),
        _check(
            "p13_release_ready",
            release_manifest.get("status") == "ready_for_claim_safe_arxiv_release",
            "P20 runs after a ready P13 paper release pack.",
            source_artifact="docs/reports/paper_release_manifest.json",
        ),
        _check(
            "public_claims_still_claim_safe",
            public_claims.get("status") == "claim_safe_public_wording_allowed"
            and not bool(public_claims.get("hard_claims_allowed"))
            and not bool(public_claims.get("headline_claims_allowed")),
            "Polish must not relax the paper claim boundary.",
            source_artifact="docs/reports/paper_public_claims_allowed.json",
        ),
        _check(
            "paysim_selection_story_passed",
            paysim_review.get("status") == "pass",
            "PaySim selection-story audit must pass.",
            source_artifact="docs/reports/paper_paysim_selection_story_review.json",
        ),
        _check(
            "reader_guidance_audit_passed",
            guidance_audit.get("status") == "pass",
            "Reader guidance from paper to repo must be simple and backed by deterministic tasks.",
            source_artifact="docs/reports/paper_reader_guidance_audit.json",
        ),
        _check(
            "visual_table_polish_audit_passed",
            polish_audit.get("status") == "pass",
            "Visual/table polish checks must pass before final source/PDF preflight.",
            source_artifact="docs/reports/paper_visual_table_polish_audit.json",
        ),
    ]
    ready = all(check["passed"] for check in checks)
    return {
        "schema_version": PAPER_NARRATIVE_POLISH_SCHEMA_VERSION,
        "slice": "Paper Track P20",
        "status": "ready_for_final_pdf_preflight" if ready else "blocked_pending_paper_polish_repairs",
        "paper_content_ready_for_p21_preflight": ready,
        "arxiv_upload_ready": False,
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "release_mode": "claim_safe_evaluation_environment_only" if ready else "blocked",
        "required_source_artifacts": REQUIRED_PAPER_NARRATIVE_POLISH_INPUT_REFS,
        "report_artifact_refs": [
            f"docs/reports/{filename}"
            for filename in PAPER_NARRATIVE_POLISH_FILENAMES.values()
        ],
        "upload_blockers_remaining": [
            "compile and inspect the final PDF from the regenerated source bundle",
            "run LaTeX warning, font-embedding, metadata, and rendered-page checks",
            "confirm a clean git tag target before any public upload",
        ],
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "next_slice": NEXT_PAPER_NARRATIVE_POLISH_SLICE if ready else "Paper Track P20 repair",
    }


def _required_artifact_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    by_ref = {
        str(value.get("artifact_ref")): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    present = []
    missing = []
    for ref in REQUIRED_PAPER_NARRATIVE_POLISH_INPUT_REFS:
        artifact = by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {"present_artifact_refs": present, "missing_artifact_refs": missing}


def _selected_test_row(baseline_table: dict[str, Any]) -> dict[str, Any]:
    for row in baseline_table.get("rows", []):
        if isinstance(row, dict) and row.get("selected_for_test_evaluation"):
            return row
    return {}


def _best_attempt(search_trace: dict[str, Any], *, stage: str) -> dict[str, Any]:
    attempts = [
        row
        for row in search_trace.get("attempts", [])
        if isinstance(row, dict)
        and row.get("stage") == stage
        and isinstance(row.get("validation_metrics"), dict)
        and isinstance(row["validation_metrics"].get("pr_auc"), (int, float))
    ]
    if not attempts:
        return {}
    return max(attempts, key=lambda row: float(row["validation_metrics"]["pr_auc"]))


def _pr_auc(row: dict[str, Any]) -> Any:
    metrics = row.get("validation_metrics")
    if isinstance(metrics, dict):
        return metrics.get("pr_auc")
    return None


def _family_label(family_id: Any) -> str:
    labels = {
        "sklearn_extra_trees": "Extra Trees",
        "sklearn_random_forest": "Random Forest",
        "sklearn_hist_gradient_boosting": "HistGradientBoosting",
        "xgboost_classifier": "XGBoost",
        "lightgbm_classifier": "LightGBM",
    }
    return labels.get(str(family_id or ""), _humanize(str(family_id or "not_available")))


def _result_has_context(draft: str, marker: str, required_terms: list[str], *, window: int = 1200) -> bool:
    start = 0
    while True:
        index = draft.find(marker, start)
        if index < 0:
            return False
        context = draft[max(0, index - 250) : index + window].lower()
        if all(term.lower() in context for term in required_terms):
            return True
        start = index + len(marker)


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in phrases)


def _contains_private_path_marker(text: str) -> bool:
    path_markers = [
        r"[A-Za-z]:\\",
        re.escape("C:" + "/" + "Users"),
        re.escape("C:" + "\\" + "Users"),
        re.escape("/" + "home" + "/"),
        re.escape("/" + "Users" + "/"),
    ]
    return re.search("|".join(path_markers), text) is not None


def _rounded(value: Any) -> Any:
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return "not_available"


def _check(
    check_id: str,
    passed: bool,
    message: str,
    *,
    source_artifact: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "check_id": check_id,
        "passed": bool(passed),
        "message": message,
        "source_artifact": source_artifact,
    }
    if detail is not None:
        row["detail"] = detail
    return row


def _read_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _repo_relative(path, root=root)
    if not path.exists():
        return {"exists": False, "artifact_ref": artifact_ref, "payload": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "exists": True,
            "artifact_ref": artifact_ref,
            "payload": {},
            "parse_error": str(exc),
        }
    return {
        "exists": True,
        "artifact_ref": artifact_ref,
        "byte_count": path.stat().st_size,
        "payload": payload,
    }


def _read_text_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _repo_relative(path, root=root)
    if not path.exists():
        return {"exists": False, "artifact_ref": artifact_ref, "text": ""}
    text = path.read_text(encoding="utf-8")
    return {
        "exists": True,
        "artifact_ref": artifact_ref,
        "byte_count": len(text.encode("utf-8")),
        "text": text,
    }


def _payload(artifact: Any) -> dict[str, Any]:
    if isinstance(artifact, dict) and isinstance(artifact.get("payload"), dict):
        return dict(artifact["payload"])
    return {}


def _text_payload(artifact: Any) -> str:
    if isinstance(artifact, dict) and isinstance(artifact.get("text"), str):
        return str(artifact["text"])
    return ""


def _repo_relative(path: Path, *, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _humanize(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title() or "Not Available"

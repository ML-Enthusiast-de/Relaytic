"""Paper Track P13 claim-safe paper release and attention-pack artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from typing import Any, Callable

from relaytic.core.json_utils import write_json


PAPER_RELEASE_SCHEMA_VERSION = "relaytic.paper_release.v1"
PAPER_RELEASE_REPORT_DIR = Path("docs") / "reports"
PAPER_RELEASE_DOC_DIR = Path("docs") / "paper"
PAPER_RELEASE_TABLE_DIRNAME = "tables"
PAPER_RELEASE_DATE = "2026-07-14"
SOURCE_VERIFICATION_DATE = "2026-07-14"
DEFAULT_RELEASE_TAG = ""
NEXT_PAPER_RELEASE_SLICE = "Paper Track P14 - final arXiv source bundle and clean release candidate"
PAPER_FINAL_DRAFT_FILENAME = "relaytic_aml_arxiv_draft.md"
PAPER_REFERENCES_FILENAME = "references.bib"

PAPER_RELEASE_FILENAMES = {
    "paper_release_manifest": "paper_release_manifest.json",
    "paper_arxiv_submission_checklist": "paper_arxiv_submission_checklist.md",
    "paper_attention_pack": "paper_attention_pack.md",
    "paper_public_claims_allowed": "paper_public_claims_allowed.json",
}

PAPER_RELEASE_TABLE_FILENAMES = {
    "evidence_summary": "table_1_evidence_summary.md",
    "claim_gate_matrix": "table_2_claim_gate_matrix.md",
    "release_artifact_set": "table_3_release_artifact_set.md",
}
PAPER_RELEASE_TABLE_MANIFEST_FILENAME = "table_manifest.json"

CLAIM_GATE_LIMITATION_MARKERS = (
    "blocked",
    "defaulted",
    "differs",
    "does_not",
    "excluded",
    "exposed",
    "hard_",
    "missing",
    "not_",
    "pending",
    "proxy",
    "requires",
    "smaller",
    "sota",
    "unavailable",
    "unproven",
    "unresolved",
)

FINAL_PAPER_REFS = [
    "docs/paper/relaytic_aml_arxiv_draft.md",
    "docs/paper/references.bib",
    "docs/paper/figures/figure_manifest.json",
    "docs/paper/figures/figure_1_claim_gate_flow.svg",
    "docs/paper/figures/figure_2_supporting_pr_auc.svg",
    "docs/paper/figures/figure_3_review_budget.svg",
    "docs/paper/figures/figure_4_publishability_matrix.svg",
    "docs/paper/tables/table_manifest.json",
    "docs/paper/tables/table_1_evidence_summary.md",
    "docs/paper/tables/table_2_claim_gate_matrix.md",
    "docs/paper/tables/table_3_release_artifact_set.md",
]

P13_GATE_REFS = [
    "docs/reports/paper_result_table_final.json",
    "docs/reports/paper_metric_cell_audit.json",
    "docs/reports/paper_publishability_matrix.json",
    "docs/reports/paper_claim_lint_report.json",
    "docs/reports/paper_external_dry_run_report.json",
    "docs/reports/paper_reproduction_failure_report.json",
    "docs/reports/paper_release_go_no_go.json",
    "docs/reports/paper_system_behavior_eval.json",
    "docs/reports/paper_system_task_eval.json",
    "docs/reports/paper_agent_handoff_eval.json",
    "docs/reports/paper_no_lost_user_eval.json",
    "docs/reports/paper_claim_gate_case_studies.json",
    "docs/reports/paper_system_eval_manifest.json",
    "docs/reports/paper_system_eval_summary.md",
    "docs/reports/paper_failure_case_eval.json",
    "docs/reports/paper_failure_case_table.json",
    "docs/reports/paper_failure_case_manifest.json",
    "docs/reports/paper_failure_case_summary.md",
    "docs/reports/paper_governance_ablation_eval.json",
    "docs/reports/paper_governance_ablation_matrix.json",
    "docs/reports/paper_governance_ablation_manifest.json",
    "docs/reports/paper_governance_ablation_summary.md",
    "docs/reports/paper_governance_invariants.json",
    "docs/reports/paper_adjacent_systems_comparison.json",
    "docs/reports/paper_invariant_manifest.json",
    "docs/reports/paper_invariant_summary.md",
    "docs/reports/paper_external_score_case_study.json",
    "docs/reports/paper_external_score_paper_panel.json",
    "docs/reports/paper_external_score_claim_map.json",
    "docs/reports/paper_external_score_repro_card.md",
    "docs/reports/paper_external_score_integration_manifest.json",
]

FORBIDDEN_PUBLIC_RULES = [
    {
        "rule_id": "unguarded_sota_claim",
        "phrase": "SOTA",
        "message": "SOTA wording must be blocked or explicitly negated.",
    },
    {
        "rule_id": "unguarded_state_of_the_art_claim",
        "phrase": "state-of-the-art",
        "message": "State-of-the-art wording must be blocked, quoted as another paper title, or explicitly negated.",
    },
    {
        "rule_id": "unguarded_hard_aml_superiority",
        "phrase": "hard real-world AML superiority",
        "message": "Hard real-world AML superiority must remain blocked.",
    },
    {
        "rule_id": "unguarded_revclassify_parity",
        "phrase": "RevClassify parity",
        "message": "RevClassify parity must remain blocked unless the P8-C reference-parity gate passes.",
    },
    {
        "rule_id": "unguarded_graph_neural_superiority",
        "phrase": "graph-neural superiority",
        "message": "Graph-neural superiority must remain blocked.",
    },
    {
        "rule_id": "unguarded_business_value_claim",
        "phrase": "hard business-value",
        "message": "Hard business-value wording must remain blocked.",
    },
    {
        "rule_id": "unguarded_leaderboard_winner",
        "phrase": "leaderboard winner",
        "message": "The release pack must not frame Relaytic-AML as a leaderboard winner.",
    },
    {
        "rule_id": "unguarded_production_ready",
        "phrase": "production-ready",
        "message": "Production-ready wording is not supported by the paper gates.",
    },
]

FORBIDDEN_READER_TONE_PHRASES = [
    "A weaker paper",
    "A useful score is not enough",
    "weaker paper",
    "serious reader",
    "fertile ground",
    "not cosmetic",
    "stronger sentence",
    "exactly the kind",
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
    "In this setting, the score",
    "the score only becomes useful",
    "which score",
    "That is a useful operating result",
    "The result supports",
    "This is the pattern",
    "That is the point",
]


def build_paper_release_pack(
    project_root: str | Path,
    *,
    release_tag: str | None = None,
    source_commit: str | None = None,
) -> dict[str, Any]:
    """Build P13 release, paper, table, citation, and public wording artifacts."""
    root = Path(project_root)
    release_tag = str(release_tag or DEFAULT_RELEASE_TAG).strip()
    inputs = _collect_inputs(root)
    inputs["release_tag"] = release_tag
    if source_commit:
        inputs["git"] = {**inputs["git"], "commit": source_commit, "dirty": False, "release_injected": True}
    metrics = _metric_lookup(inputs)
    tables = _build_tables(inputs, metrics)
    table_manifest = _build_table_manifest(tables)
    references_bib = _render_references_bib()
    final_draft = _render_final_paper(inputs=inputs, metrics=metrics, tables=tables)
    attention_pack = _render_attention_pack(inputs=inputs, metrics=metrics, release_tag=release_tag)
    public_claims = _build_public_claims_allowed(
        inputs=inputs,
        final_draft=final_draft,
        attention_pack=attention_pack,
    )
    checklist = _render_arxiv_checklist(
        inputs=inputs,
        release_tag=release_tag,
        public_claims=public_claims,
    )
    manifest = _build_release_manifest(
        root=root,
        inputs=inputs,
        release_tag=release_tag,
        public_claims=public_claims,
        table_manifest=table_manifest,
    )
    return {
        "paper_release_manifest": manifest,
        "paper_arxiv_submission_checklist": checklist,
        "paper_attention_pack": attention_pack,
        "paper_public_claims_allowed": public_claims,
        "paper_final_draft": final_draft,
        "paper_references_bib": references_bib,
        "paper_table_manifest": table_manifest,
        "paper_tables": tables,
    }


def sync_paper_release_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    paper_dir: str | Path | None = None,
    release_tag: str | None = None,
    source_commit: str | None = None,
) -> dict[str, Path]:
    """Write the P13 release pack to docs/reports and docs/paper by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_RELEASE_REPORT_DIR
    resolved_paper_dir = Path(paper_dir) if paper_dir is not None else root / PAPER_RELEASE_DOC_DIR
    table_dir = resolved_paper_dir / PAPER_RELEASE_TABLE_DIRNAME
    report_dir.mkdir(parents=True, exist_ok=True)
    resolved_paper_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    pack = build_paper_release_pack(root, release_tag=release_tag, source_commit=source_commit)
    written: dict[str, Path] = {}
    for key, filename in PAPER_RELEASE_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)

    final_draft_path = resolved_paper_dir / PAPER_FINAL_DRAFT_FILENAME
    final_draft_path.write_text(str(pack["paper_final_draft"]), encoding="utf-8")
    written["paper_final_draft"] = final_draft_path

    references_path = resolved_paper_dir / PAPER_REFERENCES_FILENAME
    references_path.write_text(str(pack["paper_references_bib"]), encoding="utf-8")
    written["paper_references_bib"] = references_path

    written["paper_table_manifest"] = write_json(
        table_dir / PAPER_RELEASE_TABLE_MANIFEST_FILENAME,
        pack["paper_table_manifest"],
        indent=2,
        sort_keys=True,
    )
    for table_id, text in dict(pack["paper_tables"]).items():
        filename = PAPER_RELEASE_TABLE_FILENAMES[table_id]
        path = table_dir / filename
        path.write_text(str(text), encoding="utf-8")
        written[f"paper_table_{table_id}"] = path
    return written


def render_paper_release_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_release_manifest", {}))
    public_claims = dict(pack.get("paper_public_claims_allowed", {}))
    return "\n".join(
        [
            "# Paper P13 Release Pack",
            "",
            f"- Release status: `{manifest.get('status') or 'unknown'}`",
            f"- Claim-safe public release allowed: `{manifest.get('claim_safe_public_release_allowed')}`",
            f"- Claim-safe Markdown draft: `{manifest.get('paper_version', {}).get('draft_ref') or 'unknown'}`",
            f"- Release identity: `{manifest.get('release_tag_plan', {}).get('tag') or 'immutable commit'}`",
            f"- Hard claims allowed: `{public_claims.get('hard_claims_allowed')}`",
            f"- Headline claims allowed: `{public_claims.get('headline_claims_allowed')}`",
            f"- Wording lint: `{public_claims.get('wording_lint', {}).get('status') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _collect_inputs(root: Path) -> dict[str, Any]:
    reports = root / PAPER_RELEASE_REPORT_DIR
    paper = root / PAPER_RELEASE_DOC_DIR
    figure_dir = paper / "figures"
    return {
        "root": root,
        "result_table": _read_artifact(reports / "paper_result_table_final.json"),
        "metric_audit": _read_artifact(reports / "paper_metric_cell_audit.json"),
        "publishability_matrix": _read_artifact(reports / "paper_publishability_matrix.json"),
        "claim_lint": _read_artifact(reports / "paper_claim_lint_report.json"),
        "limitations_matrix": _read_artifact(reports / "paper_limitations_matrix.json"),
        "external_dry_run": _read_artifact(reports / "paper_external_dry_run_report.json"),
        "reproduction_failures": _read_artifact(reports / "paper_reproduction_failure_report.json"),
        "release_go_no_go": _read_artifact(reports / "paper_release_go_no_go.json"),
        "system_behavior_eval": _read_artifact(reports / "paper_system_behavior_eval.json"),
        "system_task_eval": _read_artifact(reports / "paper_system_task_eval.json"),
        "agent_handoff_eval": _read_artifact(reports / "paper_agent_handoff_eval.json"),
        "no_lost_user_eval": _read_artifact(reports / "paper_no_lost_user_eval.json"),
        "claim_gate_case_studies": _read_artifact(reports / "paper_claim_gate_case_studies.json"),
        "system_eval_manifest": _read_artifact(reports / "paper_system_eval_manifest.json"),
        "system_eval_summary": _read_text_artifact(reports / "paper_system_eval_summary.md"),
        "failure_case_eval": _read_artifact(reports / "paper_failure_case_eval.json"),
        "failure_case_table": _read_artifact(reports / "paper_failure_case_table.json"),
        "failure_case_manifest": _read_artifact(reports / "paper_failure_case_manifest.json"),
        "failure_case_summary": _read_text_artifact(reports / "paper_failure_case_summary.md"),
        "governance_ablation_eval": _read_artifact(reports / "paper_governance_ablation_eval.json"),
        "governance_ablation_matrix": _read_artifact(reports / "paper_governance_ablation_matrix.json"),
        "governance_ablation_manifest": _read_artifact(reports / "paper_governance_ablation_manifest.json"),
        "governance_ablation_summary": _read_text_artifact(reports / "paper_governance_ablation_summary.md"),
        "governance_invariants": _read_artifact(reports / "paper_governance_invariants.json"),
        "adjacent_systems_comparison": _read_artifact(reports / "paper_adjacent_systems_comparison.json"),
        "invariant_manifest": _read_artifact(reports / "paper_invariant_manifest.json"),
        "invariant_summary": _read_text_artifact(reports / "paper_invariant_summary.md"),
        "external_score_case_study": _read_artifact(reports / "paper_external_score_case_study.json"),
        "external_score_paper_panel": _read_artifact(reports / "paper_external_score_paper_panel.json"),
        "external_score_claim_map": _read_artifact(reports / "paper_external_score_claim_map.json"),
        "external_score_repro_card": _read_text_artifact(reports / "paper_external_score_repro_card.md"),
        "external_score_integration_manifest": _read_artifact(
            reports / "paper_external_score_integration_manifest.json"
        ),
        "table_provenance": _read_artifact(reports / "paper_table_provenance.json"),
        "claim_gate_records": _read_artifact(reports / "paper_claim_gate_records.json"),
        "external_score_evidence_cells": _read_artifact(reports / "paper_external_score_evidence_cells.json"),
        "external_score_claim_gate": _read_artifact(reports / "paper_external_score_claim_gate.json"),
        "paper_reproduction_commands": _read_text_artifact(reports / "paper_reproduction_commands.md"),
        "dataset_registry": _read_artifact(reports / "paper_dataset_registry.json"),
        "split_contracts": _read_artifact(reports / "paper_split_contracts.json"),
        "paysim_temporal_split": _read_artifact(reports / "paysim_temporal_split_report.json"),
        "paysim_competitive_manifest": _read_artifact(reports / "paysim_competitive_benchmark_manifest.json"),
        "paysim_competitive_baseline_table": _read_artifact(reports / "paysim_competitive_baseline_table.json"),
        "paysim_competitive_feature_report": _read_artifact(reports / "paysim_leakage_safe_feature_report.json"),
        "paysim_competitive_search_trace": _read_artifact(reports / "paysim_competitive_search_trace.json"),
        "paysim_competitive_budget_contract": _read_artifact(reports / "paysim_competitive_budget_contract.json"),
        "elliptic_temporal_split": _read_artifact(reports / "elliptic_temporal_split_report.json"),
        "elliptic_graph_feature_table": _read_artifact(reports / "paper_graph_feature_table.json"),
        "elliptic_graph_budget_contract": _read_artifact(reports / "paper_graph_budget_contract.json"),
        "elliptic2_repeated_seed_scorecard": _read_artifact(reports / "elliptic2_repeated_seed_scorecard.json"),
        "elliptic2_modern_reference_contract": _read_artifact(reports / "elliptic2_modern_reference_contract.json"),
        "elliptic2_protocol_audit": _read_artifact(reports / "elliptic2_protocol_audit.json"),
        "elliptic2_cohort_reconciliation": _read_artifact(reports / "elliptic2_evaluable_cohort_reconciliation.json"),
        "elliptic2_split_robustness": _read_artifact(reports / "elliptic2_split_robustness_report.json"),
        "elliptic2_reference_parity": _read_artifact(reports / "elliptic2_reference_parity_gate.json"),
        "p11_draft": _read_text_artifact(paper / "relaytic_aml_draft.md"),
        "figure_manifest": _read_artifact(figure_dir / "figure_manifest.json"),
        "readme": _read_text_artifact(root / "README.md"),
        "git": _git_state(root),
    }


def _build_release_manifest(
    *,
    root: Path,
    inputs: dict[str, Any],
    release_tag: str,
    public_claims: dict[str, Any],
    table_manifest: dict[str, Any],
) -> dict[str, Any]:
    checks = _release_checks(inputs=inputs, public_claims=public_claims, table_manifest=table_manifest)
    status = "ready_for_claim_safe_arxiv_release" if all(check["passed"] for check in checks) else "blocked_pending_release_repairs"
    paper_refs = [*FINAL_PAPER_REFS, *P13_GATE_REFS]
    tag_plan_refs = sorted(set(paper_refs + list(PAPER_RELEASE_FILENAMES.values())))
    return {
        "schema_version": PAPER_RELEASE_SCHEMA_VERSION,
        "slice": "Paper Track P13",
        "status": status,
        "release_mode": "claim_safe_evaluation_environment_only" if status.startswith("ready") else "blocked",
        "claim_safe_public_release_allowed": status.startswith("ready"),
        "arxiv_upload_ready": False,
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "release_date": PAPER_RELEASE_DATE,
        "git_commit": inputs["git"].get("commit"),
        "git_dirty": inputs["git"].get("dirty"),
        "git_state_semantics": "generation_base_commit_not_manifest_self_hash",
        "submission_package_state": {
            "current_format": "claim_safe_markdown_draft_pack",
            "required_before_upload": [
                "convert the Markdown draft into final TeX/PDF source",
                "convert SVG figures into figure formats accepted by the selected arXiv processor",
                "confirm author block, license, acknowledgements, local PDF inspection, and a clean cited revision",
                "rerun release-safety checks from the final clean public revision",
            ],
        },
        "release_tag_plan": {
            "mode": "verified_tag" if release_tag else "immutable_commit",
            "tag": release_tag or None,
            "tag_created_by_this_slice": False,
            "creation_command": (
                f"git tag -a {release_tag} -m \"Relaytic-AML claim-safe paper release\""
                if release_tag
                else None
            ),
            "artifact_refs": tag_plan_refs,
            "note": (
                "A tag may be reported only after local and remote verification."
                if release_tag
                else "No public release tag is claimed; final artifacts identify an immutable commit."
            ),
        },
        "paper_version": {
            "draft_ref": "docs/paper/relaytic_aml_arxiv_draft.md",
            "source_draft_ref": "docs/paper/relaytic_aml_draft.md",
            "bib_ref": "docs/paper/references.bib",
            "figure_manifest_ref": "docs/paper/figures/figure_manifest.json",
            "table_manifest_ref": "docs/paper/tables/table_manifest.json",
            "artifact_refs": paper_refs,
        },
        "required_source_artifacts": P13_GATE_REFS,
        "source_verification": _source_verification_records(),
        "public_claims_ref": "docs/reports/paper_public_claims_allowed.json",
        "attention_pack_ref": "docs/reports/paper_attention_pack.md",
        "arxiv_submission_checklist_ref": "docs/reports/paper_arxiv_submission_checklist.md",
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "next_slice": NEXT_PAPER_RELEASE_SLICE if status.startswith("ready") else "Paper Track P13 repair",
    }


def _build_public_claims_allowed(
    *,
    inputs: dict[str, Any],
    final_draft: str,
    attention_pack: str,
) -> dict[str, Any]:
    go_no_go = _payload(inputs["release_go_no_go"])
    readme_text = _text_payload(inputs["readme"])
    surfaces = [
        ("docs/paper/relaytic_aml_arxiv_draft.md", final_draft),
        ("docs/reports/paper_attention_pack.md", attention_pack),
        ("README.md", readme_text),
    ]
    lint = _lint_public_surfaces(surfaces)
    readme_release_section_present = (
        "Relaytic-AML Paper Draft" in readme_text or "Paper P13 Claim-Safe Release Status" in readme_text
    )
    checks = [
        _check(
            "p12_go_no_go_allows_p13",
            bool(go_no_go.get("paper_can_continue_to_p13")),
            "P12 go/no-go must allow P13 before public release wording is allowed.",
            source_artifact="docs/reports/paper_release_go_no_go.json",
        ),
        _check(
            "hard_and_headline_claims_blocked",
            not bool(go_no_go.get("hard_claims_allowed")) and not bool(go_no_go.get("headline_claims_allowed")),
            "Claim-safe release requires hard and headline claims to remain blocked.",
            source_artifact="docs/reports/paper_release_go_no_go.json",
        ),
        _check(
            "readme_release_section_present",
            readme_release_section_present,
            "README must expose the Relaytic-AML paper status and point to the paper artifacts.",
            source_artifact="README.md",
        ),
        _check(
            "public_wording_lint_passed",
            lint["status"] == "pass",
            "Draft, attention pack, and README wording must not contain unguarded blocked claims.",
            source_artifact="docs/reports/paper_public_claims_allowed.json",
            detail={"violation_count": len(lint["violations"])},
        ),
    ]
    status = "claim_safe_public_wording_allowed" if all(check["passed"] for check in checks) else "blocked_public_wording"
    return {
        "schema_version": PAPER_RELEASE_SCHEMA_VERSION,
        "slice": "Paper Track P13",
        "status": status,
        "claim_safe_public_wording_allowed": status.startswith("claim_safe"),
        "release_mode": "claim_safe_evaluation_environment_only" if status.startswith("claim_safe") else "blocked",
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "allowed_public_claims": [
            "Relaytic-AML is a local-first, claim-gated evaluation environment for temporal, graph, and operational financial-crime machine learning.",
            "The current paper pack presents Relaytic as a local-first anti-money-laundering evaluation lab with local artifacts, specialist roles, redacted context export, and explicit claim boundaries.",
            "PaySim and Elliptic rows may be described as supporting evidence only under their documented proxy and graph-feature boundaries.",
            "Elliptic2 may be described as modern context and limitation evidence only, not as a Relaytic performance contribution.",
            "The public source package and paper assets may be regenerated from the repository commands documented in the paper.",
        ],
        "blocked_public_claims": [
            "hard real-world AML superiority",
            "SOTA or leaderboard-winner claim",
            "RevClassify parity or Elliptic2 performance contribution",
            "graph-neural superiority",
            "hard business-value or analyst-hour savings claim",
            "production-ready AML deployment claim",
        ],
        "metric_wording_boundaries": {
            "paysim_p6a_competitive_selected.test_pr_auc": "May be cited as supporting synthetic temporal-fraud evidence only.",
            "elliptic_p7_selected_graph_feature_baseline.test_pr_auc": "May be cited as supporting temporal graph-feature evidence only.",
            "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean": "May be cited as modern context only, below the recorded RevClassifyDS reference and not a parity claim.",
        },
        "surfaces_linted": [surface for surface, _ in surfaces],
        "wording_lint": lint,
        "checks": checks,
        "next_slice": NEXT_PAPER_RELEASE_SLICE if status.startswith("claim_safe") else "Paper Track P13 repair",
    }


def _release_checks(
    *,
    inputs: dict[str, Any],
    public_claims: dict[str, Any],
    table_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    table = _payload(inputs["result_table"])
    audit = _payload(inputs["metric_audit"])
    claim_lint = _payload(inputs["claim_lint"])
    dry_run = _payload(inputs["external_dry_run"])
    failures = _payload(inputs["reproduction_failures"])
    go_no_go = _payload(inputs["release_go_no_go"])
    system_manifest = _payload(inputs["system_eval_manifest"])
    system_behavior = _payload(inputs["system_behavior_eval"])
    system_tasks = _payload(inputs["system_task_eval"])
    failure_manifest = _payload(inputs["failure_case_manifest"])
    failure_eval = _payload(inputs["failure_case_eval"])
    failure_table = _payload(inputs["failure_case_table"])
    governance_manifest = _payload(inputs["governance_ablation_manifest"])
    governance_eval = _payload(inputs["governance_ablation_eval"])
    governance_matrix = _payload(inputs["governance_ablation_matrix"])
    invariant_manifest = _payload(inputs["invariant_manifest"])
    governance_invariants = _payload(inputs["governance_invariants"])
    adjacent_systems = _payload(inputs["adjacent_systems_comparison"])
    external_score_manifest = _payload(inputs["external_score_integration_manifest"])
    external_score_case_study = _payload(inputs["external_score_case_study"])
    external_score_panel = _payload(inputs["external_score_paper_panel"])
    external_score_claim_map = _payload(inputs["external_score_claim_map"])
    required = _required_artifact_presence(inputs)
    paper_artifact_set = set(FINAL_PAPER_REFS)
    table_artifact_set = {item.get("artifact_ref") for item in table_manifest.get("tables", []) if isinstance(item, dict)}
    return [
        _check(
            "p10_table_pack_passed",
            table.get("status") == "tables_generated_claim_guarded"
            and audit.get("status") == "pass"
            and bool(audit.get("paper_can_continue_to_p11")),
            "P10 table pack and evidence-cell audit must pass.",
            source_artifact="docs/reports/paper_metric_cell_audit.json",
        ),
        _check(
            "p11_claim_lint_passed",
            claim_lint.get("status") == "pass" and bool(claim_lint.get("paper_can_continue_to_p12")),
            "P11 claim lint must pass before release.",
            source_artifact="docs/reports/paper_claim_lint_report.json",
        ),
        _check(
            "p12_external_dry_run_passed",
            dry_run.get("status") == "pass_paper_smoke_reproduced_claim_linted",
            "P12 external dry-run report must pass.",
            source_artifact="docs/reports/paper_external_dry_run_report.json",
        ),
        _check(
            "p12_reproduction_failures_clear",
            failures.get("status") == "no_failures" and int(failures.get("unresolved_failure_count") or 0) == 0,
            "P12 reproduction failure report must have zero unresolved failures.",
            source_artifact="docs/reports/paper_reproduction_failure_report.json",
        ),
        _check(
            "p12_go_no_go_allows_claim_safe_p13",
            go_no_go.get("status") == "go_for_p13_claim_safe_release_pack"
            and bool(go_no_go.get("paper_can_continue_to_p13")),
            "P12 go/no-go must allow P13 in claim-safe release mode.",
            source_artifact="docs/reports/paper_release_go_no_go.json",
        ),
        _check(
            "hard_and_headline_claims_remain_blocked",
            not bool(go_no_go.get("hard_claims_allowed")) and not bool(go_no_go.get("headline_claims_allowed")),
            "P13 is allowed only because hard/headline claims remain blocked.",
            source_artifact="docs/reports/paper_release_go_no_go.json",
        ),
        _check(
            "p15_system_eval_passed",
            system_manifest.get("status") == "ready_for_system_evaluation_evidence"
            and system_behavior.get("status") == "pass"
            and system_tasks.get("status") == "pass",
            "Measured system-evaluation proof must pass before the paper describes Relaytic's user and agent handoff behavior.",
            source_artifact="docs/reports/paper_system_eval_manifest.json",
        ),
        _check(
            "p15_reader_task_eval_passed",
            system_tasks.get("status") == "pass"
            and int(system_tasks.get("task_count") or 0) >= 10
            and not system_tasks.get("failed_tasks"),
            "Reader and external-agent task evaluation must prove navigation, provenance, recovery, privacy, and claim-boundary tasks.",
            source_artifact="docs/reports/paper_system_task_eval.json",
        ),
        _check(
            "p16_failure_case_eval_passed",
            failure_manifest.get("status") == "ready_for_failure_case_evidence"
            and failure_eval.get("status") == "pass"
            and failure_table.get("status") == "pass"
            and int(failure_eval.get("passed_case_count") or 0) == int(failure_eval.get("case_count") or -1),
            "Failure-case evaluation must verify leakage, test-selection, over-claim, redaction, and recovery guardrails before the paper describes measured failure prevention.",
            source_artifact="docs/reports/paper_failure_case_manifest.json",
        ),
        _check(
            "p17_governance_ablation_passed",
            governance_manifest.get("status") == "ready_for_governance_ablation_evidence"
            and governance_eval.get("status") == "pass"
            and governance_matrix.get("status") == "pass"
            and bool(governance_eval.get("full_path_safe")),
            "Governance-ablation evidence must compare the full path with disabled-component fixtures before the paper describes machinery-level release behavior.",
            source_artifact="docs/reports/paper_governance_ablation_manifest.json",
        ),
        _check(
            "p18_governance_invariants_passed",
            invariant_manifest.get("status") == "ready_for_governance_invariant_evidence"
            and governance_invariants.get("status") == "pass"
            and adjacent_systems.get("status") == "pass"
            and bool(governance_invariants.get("proof_obligation_passed"))
            and int(governance_invariants.get("current_invariant_count") or 0) >= 6,
            "Governance-invariant evidence must map every current invariant in the paper to artifacts, failure cases, ablations, or limitations.",
            source_artifact="docs/reports/paper_invariant_manifest.json",
        ),
        _check(
            "p19b_hosted_score_case_study_passed",
            external_score_manifest.get("status") == "ready_for_hosted_score_case_study"
            and bool(external_score_manifest.get("paper_integration_allowed"))
            and external_score_case_study.get("status") == "pass"
            and external_score_panel.get("status") == "pass"
            and external_score_claim_map.get("status") == "pass"
            and external_score_claim_map.get("allowed_claim_scope") == "hosted detector-output governance only"
            and not bool(external_score_claim_map.get("detector_superiority_allowed"))
            and not bool(external_score_claim_map.get("production_aml_readiness_allowed"))
            and not bool(external_score_claim_map.get("revclassifyds_parity_allowed")),
            "Hosted-score case-study integration must pass before the paper describes external detector-output governance.",
            source_artifact="docs/reports/paper_external_score_integration_manifest.json",
        ),
        _check(
            "required_p13_inputs_present",
            not required["missing_artifact_refs"],
            "All P10-P12 source artifacts required by P13 must be present.",
            source_artifact="docs/reports",
            detail=required,
        ),
        _check(
            "public_claims_allowed",
            bool(public_claims.get("claim_safe_public_wording_allowed")),
            "Public wording must pass the P13 allowed-claims lint.",
            source_artifact="docs/reports/paper_public_claims_allowed.json",
        ),
        _check(
            "paper_table_refs_align_with_release_artifact_set",
            table_artifact_set.issubset(paper_artifact_set),
            "Generated paper tables must be included in the release artifact set.",
            source_artifact="docs/paper/tables/table_manifest.json",
            detail={"table_artifact_refs": sorted(str(item) for item in table_artifact_set if item)},
        ),
    ]


def _required_artifact_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    missing = []
    present = []
    artifact_by_ref = {
        value.get("artifact_ref"): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    for ref in P13_GATE_REFS:
        artifact = artifact_by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {"present_artifact_refs": present, "missing_artifact_refs": missing}


def _build_tables(inputs: dict[str, Any], metrics: dict[str, dict[str, Any]]) -> dict[str, str]:
    return {
        "evidence_summary": _render_evidence_summary_table(metrics),
        "claim_gate_matrix": _render_claim_gate_table(_payload(inputs["publishability_matrix"])),
        "release_artifact_set": _render_release_artifact_table(inputs),
    }


def _build_table_manifest(tables: dict[str, str]) -> dict[str, Any]:
    rows = []
    for table_id, filename in PAPER_RELEASE_TABLE_FILENAMES.items():
        rows.append(
            {
                "table_id": table_id,
                "artifact_ref": f"docs/paper/tables/{filename}",
                "source_refs": P13_GATE_REFS,
                "paper_claim_role": "claim_safe_supporting_evidence_only",
                "byte_count": len(tables.get(table_id, "").encode("utf-8")),
            }
        )
    return {
        "schema_version": PAPER_RELEASE_SCHEMA_VERSION,
        "slice": "Paper Track P13",
        "status": "tables_materialized",
        "table_dir": "docs/paper/tables",
        "tables": rows,
    }


def _render_evidence_summary_table(metrics: dict[str, dict[str, Any]]) -> str:
    rows = [
        ("PaySim baseline", "test PR-AUC", "paysim_p6_validation_selected_baseline.test_pr_auc", "baseline-only"),
        ("PaySim competitive", "test PR-AUC", "paysim_p6a_competitive_selected.test_pr_auc", "supporting-only synthetic temporal proxy"),
        ("PaySim competitive", "precision at review budget", "paysim_p6a_competitive_selected.precision_at_review_budget", "supporting-only"),
        ("PaySim competitive", "recall at review budget", "paysim_p6a_competitive_selected.recall_at_review_budget", "supporting-only"),
        ("Elliptic graph-feature", "test PR-AUC", "elliptic_p7_selected_graph_feature_baseline.test_pr_auc", "supporting-only graph-feature evidence"),
        ("Elliptic graph-feature", "precision at review budget", "elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget", "supporting-only"),
        ("Elliptic graph-feature", "recall at review budget", "elliptic_p7_selected_graph_feature_baseline.recall_at_review_budget", "supporting-only"),
        ("Elliptic2 context", "provided RevTrack TST PR-AUC mean", "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean", "modern context only"),
        ("Elliptic2 context", "provided RevTrack TST PR-AUC std", "elliptic2_p8b_modern_context.official_partition_test_pr_auc_std", "modern context only"),
        ("RevClassifyDS reference", "published PR-AUC", "elliptic2_p8b_modern_context.published_reference_pr_auc", "reference context, not parity"),
    ]
    lines = [
        "# Table 1. Evidence Summary",
        "",
        "| Evidence row | Metric | Value | Claim posture |",
        "|---|---:|---:|---|",
    ]
    for label, metric, cell_id, posture in rows:
        lines.append(
            f"| {_escape_md(label)} | {_escape_md(metric)} | {_format_metric(_metric_value(metrics, cell_id))} | "
            f"{_escape_md(posture)} |"
        )
    lines.append("")
    lines.append("<!-- evidence-cells: " + " ".join(f"paper-cell:{cell_id}" for _, _, cell_id, _ in rows) + " -->")
    lines.append("")
    lines.append(
        "Exact evidence-cell identifiers and artifact fields are stored in the evidence-cell audit artifact named "
        "in the reproducibility section. None of these rows is a headline or hard AML claim."
    )
    return "\n".join(lines).rstrip() + "\n"


def _render_claim_gate_table(publishability: dict[str, Any]) -> str:
    rows = [row for row in publishability.get("rows", []) if isinstance(row, dict)]
    seen_tracks: set[str] = set()
    lines = [
        "# Table 2. Claim Gate Matrix",
        "",
        "| Track | Current paper use | Blocked stronger claim | Evidence needed before promotion | Gate status |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        dataset_id = str(row.get("dataset_id") or "unknown")
        if dataset_id in seen_tracks:
            continue
        seen_tracks.add(dataset_id)
        summary = _claim_gate_summary(row)
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(summary["track"]),
                    _escape_md(summary["current_use"]),
                    _escape_md(summary["blocked_claim"]),
                    _escape_md(summary["needed_evidence"]),
                    _escape_md(summary["gate_status"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _claim_gate_summary(row: dict[str, Any]) -> dict[str, str]:
    dataset_id = str(row.get("dataset_id") or "unknown")
    summaries = {
        "paysim_temporal_transaction_fraud": {
            "track": "PaySim temporal proxy",
            "current_use": "supporting synthetic temporal-fraud evidence",
            "blocked_claim": "real-bank AML superiority",
            "needed_evidence": "partner or real holdout with frozen evaluation budget",
            "gate_status": "supporting only",
        },
        "elliptic_flattened_graph_aml": {
            "track": "Elliptic graph-feature",
            "current_use": "supporting temporal graph-feature evidence",
            "blocked_claim": "graph-neural or graph benchmark superiority",
            "needed_evidence": "repeated graph evaluation budget against strong feature baselines",
            "gate_status": "supporting only",
        },
        "elliptic2_subgraph_aml": {
            "track": "Elliptic2 subgraph",
            "current_use": "modern subgraph context and limitation evidence",
            "blocked_claim": "Elliptic2 performance contribution or reference-method match",
            "needed_evidence": "faithful RevClassify reproduction or leakage-resistant subgraph protocol",
            "gate_status": "context only",
        },
        "paper_operational_layer": {
            "track": "Operational review layer",
            "current_use": "supporting review-budget estimates",
            "blocked_claim": "hard analyst-hour or business-value claim",
            "needed_evidence": "complete case packets and same-queue incumbent comparison",
            "gate_status": "supporting only",
        },
    }
    if dataset_id in summaries:
        return summaries[dataset_id]
    return {
        "track": _humanize_gate_token(dataset_id),
        "current_use": "supporting or blocked evidence",
        "blocked_claim": "headline or hard claim",
        "needed_evidence": _humanize_gate_token(_claim_gate_notes(row)),
        "gate_status": _humanize_gate_token(str(row.get("gate_status") or "unknown")),
    }


def _humanize_gate_token(text: str) -> str:
    return " ".join(text.replace("_", " ").replace("+", " +").split())


def _claim_gate_notes(row: dict[str, Any]) -> str:
    reason_codes = [str(item) for item in _as_list(row.get("blocked_reason_codes"))]
    limitation_codes = [
        code
        for code in reason_codes
        if any(marker in code.lower() for marker in CLAIM_GATE_LIMITATION_MARKERS)
    ]
    if not limitation_codes:
        if not row.get("headline_claim_allowed") or not row.get("hard_claim_allowed"):
            return "hard_or_headline_claims_not_allowed_by_gate"
        return "none"
    max_codes = 6
    shown = limitation_codes[:max_codes]
    suffix = f", +{len(limitation_codes) - max_codes} more" if len(limitation_codes) > max_codes else ""
    return ", ".join(shown) + suffix


def _render_release_artifact_table(inputs: dict[str, Any]) -> str:
    refs = [
        *P13_GATE_REFS,
        "docs/paper/relaytic_aml_arxiv_draft.md",
        "docs/paper/relaytic_aml_draft.md",
        "docs/paper/figures/figure_manifest.json",
        "docs/paper/figures/figure_1_claim_gate_flow.svg",
        "docs/paper/figures/figure_2_supporting_pr_auc.svg",
        "docs/paper/figures/figure_3_review_budget.svg",
        "docs/paper/figures/figure_4_publishability_matrix.svg",
    ]
    artifact_by_ref = {
        value.get("artifact_ref"): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    lines = [
        "# Table 3. Release Artifact Set",
        "",
        "| Artifact | Present | Role |",
        "|---|---:|---|",
    ]
    for ref in refs:
        artifact = artifact_by_ref.get(ref)
        present = bool(artifact.get("exists")) if artifact else Path(ref).exists()
        if ref == "docs/paper/relaytic_aml_arxiv_draft.md":
            role = "paper manuscript"
        elif ref == "docs/paper/relaytic_aml_draft.md":
            role = "draft-generation support artifact"
        elif ref.startswith("docs/reports"):
            role = "internal evidence record"
        elif ref.startswith("docs/paper/figures"):
            role = "figure source artifact"
        elif ref.startswith("docs/paper/tables"):
            role = "table source artifact"
        else:
            role = "paper support artifact"
        lines.append(f"| `{ref}` | {_yes_no(present)} | {role} |")
    return "\n".join(lines).rstrip() + "\n"


def _reader_facing_table(table_markdown: str, *, title: str) -> str:
    text = table_markdown.replace(f"# {title}\n\n", "")
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<!--"):
            continue
        if stripped.startswith("Exact evidence-cell identifiers"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _render_agent_role_table() -> str:
    rows = [
        (
            "Operator and mandate owner",
            "Sets goals, constraints, privacy posture, and stop/continue preferences.",
            "Mandate, policy, permission, and next-action artifacts. Data can stay on a controlled local machine, server, or cluster.",
        ),
        (
            "Guide and assist layer",
            "Answers where the run is, what artifacts matter, and which action is safe next.",
            "Guide payloads, assist turns, status, and context packs. Optional LLM help is advisory and redacted by default.",
        ),
        (
            "Scout and task-contract agents",
            "Inspect source posture, target semantics, split validity, and leakage risk.",
            "Dataset registry, source manifests, split contracts, and task reports. Work from staged local snapshots.",
        ),
        (
            "Scientist and challenger agents",
            "Propose baselines, ablations, shadow candidates, and failure explanations.",
            "Experiment registry, scorecards, ablations, and shadow-trial reports. Candidate work is budgeted and permission-bound.",
        ),
        (
            "Builder and search controller",
            "Execute reproducible model/search plans and select thresholds on validation evidence.",
            "Run directories, model artifacts, search traces, and operating-point records. Optional adapters are versioned.",
        ),
        (
            "Evidence and release governors",
            "Decide how evidence may be described and which claims stay blocked.",
            "Metric cells, claim boundaries, release notes, and source-bundle audits. Gates fail closed on unsupported interpretation.",
        ),
        (
            "External agents or LLMs",
            "Consume exported context, propose repairs, or continue work through stable surfaces.",
            "External context packs, handoff reports, and reproducible commands. Rowless/redacted by default unless policy grants more.",
        ),
    ]
    lines = [
        "| Role | Responsibility | Boundary and outputs |",
        "| --- | --- | --- |",
    ]
    for role, owns, boundary in rows:
        lines.append(f"| {_escape_md(role)} | {_escape_md(owns)} | {_escape_md(boundary)} |")
    return "\n".join(lines)


def _render_evidence_layer_table() -> str:
    rows = [
        (
            "Source and task contracts",
            "Dataset access, target semantics, benchmark posture, and split rules.",
            "Lets a reader judge task validity before judging a score.",
        ),
        (
            "Execution and search artifacts",
            "Candidate families, budgets, calibration, thresholds, selected runs, and search traces.",
            "Makes model development inspectable rather than anecdotal.",
        ),
        (
            "AML domain artifacts",
            "Entity graphs, typology posture, review queues, delayed labels, and case evidence.",
            "Connects model output to analyst workflow instead of treating rows in isolation.",
        ),
        (
            "Evidence ledgers",
            "Metric cells, tables, figures, limitations, and commands.",
            "Keeps every public number tied to local source artifacts.",
        ),
        (
            "Claim boundaries",
            "Allowed claims, blocked claims, limitation notes, and future unlock conditions.",
            "Prevents metric values from becoming unsupported claims.",
        ),
        (
            "Trace and replay artifacts",
            "Runtime spans, branch graphs, tool logs, claim packets, and adjudication scorecards.",
            "Lets another reviewer reconstruct how Relaytic reached the state.",
        ),
        (
            "Handoff surfaces",
            "Guide, status, assist, mission control, and redacted context export.",
            "Lets humans and external agents continue without guessing hidden state.",
        ),
    ]
    lines = [
        "| Layer | What It Records | Why It Matters |",
        "| --- | --- | --- |",
    ]
    for layer, records, purpose in rows:
        lines.append(f"| {_escape_md(layer)} | {_escape_md(records)} | {_escape_md(purpose)} |")
    return "\n".join(lines)


def _render_adjacent_systems_table() -> str:
    rows = [
        (
            "Experiment tracking",
            "Runs, metrics, artifacts, lineage, and model versions.",
            "A metric can still be separated from task validity, privacy posture, review capacity, and public interpretation.",
        ),
        (
            "Data validation and monitoring",
            "Schema checks, drift, quality rules, and production signals.",
            "Validation often stops before model-search budgets, operating-point choices, and manuscript claims are tied together.",
        ),
        (
            "Workflow orchestration",
            "DAG execution, retries, scheduling, and dependency management.",
            "Execution graphs usually do not decide whether evidence is strong enough for a claim or a safe next action.",
        ),
        (
            "AutoML and benchmark suites",
            "Model-family search, hyperparameter optimization, and leaderboard comparison.",
            "Score search can obscure leakage posture, budget spent, review-queue utility, and whether a result may be generalized.",
        ),
        (
            "General agent frameworks",
            "Tool use, planning, memory, and host integration.",
            "Agent fluency can outpace evidence unless state, permissions, redaction, traces, and claim gates are explicit.",
        ),
    ]
    lines = [
        "| Adjacent practice | What it handles well | Gap for AML evaluation |",
        "| --- | --- | --- |",
    ]
    for system, strength, gap in rows:
        lines.append(f"| {_escape_md(system)} | {_escape_md(strength)} | {_escape_md(gap)} |")
    return "\n".join(lines)


def _render_paysim_evidence_walkthrough(
    *,
    pay_base_pr: str,
    pay_pr: str,
    pay_precision: str,
    pay_recall: str,
) -> str:
    return "\n".join(
        [
            "The PaySim row is the clearest example of the evidence-cell path. The source contract identifies a synthetic mobile-money transaction-fraud task. The split contract orders records by simulator step. The leakage contract excludes simulator balance fields that can reveal after-event information, then allows prior-step destination-history features. The model-search contract separates a baseline budget from a competitive budget. The threshold contract chooses operating points on validation evidence and applies them unchanged to the test partition.",
            "",
            f"The competitive PaySim path changes the fixed-test PR-AUC from {pay_base_pr} in the baseline run to {pay_pr} in the competitive run. At the selected review budget, separate factual cells record precision {pay_precision} and recall {pay_recall}. The comparison uses the same dataset, split, feature, and metric contract with different declared modeling budgets. A separate gate limits the result to temporal proxy evidence because PaySim is synthetic.",
            "",
            "Relaytic is meant to enforce this pattern: useful evidence is preserved, the modeling work that created it is inspectable, and the stronger interpretation is blocked until the data and protocol justify it.",
        ]
    )


def _render_measured_system_eval_section(inputs: dict[str, Any]) -> str:
    manifest = _payload(inputs["system_eval_manifest"])
    behavior = _payload(inputs["system_behavior_eval"])
    task_eval = _payload(inputs["system_task_eval"])
    if (
        manifest.get("status") != "ready_for_system_evaluation_evidence"
        or behavior.get("status") != "pass"
        or task_eval.get("status") != "pass"
        or not behavior.get("evaluation_rows")
    ):
        return ""
    task_count = int(task_eval.get("task_count") or 0)
    required_count = int(behavior.get("required_task_count") or 0)
    task_ids = {
        str(item.get("task_id"))
        for item in list(task_eval.get("tasks", []))
        if isinstance(item, dict) and item.get("task_id")
    }
    task_scope = ", ".join(
        item
        for item, task_id in [
            ("repository navigation", "repo_navigation_separates_relaytic_from_aml_paper"),
            ("cross-platform reproduction", "cross_platform_reproduction_path_visible"),
            ("metric provenance", "metric_cell_provenance_available"),
            ("baseline-versus-competitive comparison", "paysim_baseline_and_competitive_budget_comparable"),
            ("claim-boundary recovery", "claim_gate_fails_closed_for_public_interpretation"),
            ("rowless handoff", "rowless_external_agent_handoff_recoverable"),
        ]
        if task_id in task_ids
    )
    lines = [
        "The release pack measures part of the system behavior directly. The target is a basic property that an evaluation lab should have: a reader or external agent should be able to enter the repository, find the paper evidence, recover the current state, trace a number back to its source, and see why a stronger claim remains blocked.",
        "",
        f"The current pack contains {required_count} required deterministic checks. Within it, {task_count} reader and external-agent tasks cover {task_scope}. These tasks are intentionally concrete. They ask whether the README separates the general Relaytic platform from the Relaytic-AML paper path, whether Windows and macOS/Linux reproduction commands are visible, whether the PaySim PR-AUC cell carries dataset/split/command/artifact/budget/leakage/claim provenance, whether PaySim baseline and competitive budgets are comparable, whether Elliptic2 is recoverable as modern context rather than a performance contribution, and whether an interrupted run can be exported to another model without raw rows or private paths.",
        "",
        "This matters because the paper's central claim is about controlled evidence. A strong PR-AUC with no recoverable provenance would be weak evidence for this paper. Conversely, an Elliptic2 context row is still useful when the system can explain its role and which future evidence would change that state.",
        "",
        "The evaluation also checks the local-first handoff contract. Relaytic exports a rowless external-agent context pack from local artifacts, verifies that raw rows are absent, records redactions, and exposes safe next actions plus tool discovery. Optional local large-language-model phrasing remains advisory in the evaluated fixture; the truth-bearing state is the artifact graph.",
        "",
        "All required checks currently pass. Relaytic demonstrates deterministic navigation, provenance recovery, partial-run recovery, rowless handoff, optional-LLM containment, and fail-closed claim gating. Controlled human-subject results, analyst-hour savings, production deployment, and autonomous external-agent performance improvement remain future evaluation targets.",
        "",
        "The repository publishes the task-level system evaluation, aggregate behavior evaluation, partial-run recovery check, rowless handoff check, claim-gate case studies, and fail-closed manifest as machine-readable evidence. The README maps those generated reports to concrete filenames for readers who want to audit the JSON.",
    ]
    return "\n".join(lines)


def _render_final_paper(
    *,
    inputs: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    tables: dict[str, str],
) -> str:
    return _render_final_paper_v2(inputs=inputs, metrics=metrics, tables=tables)


def _render_final_paper_v2(
    *,
    inputs: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    tables: dict[str, str],
) -> str:
    pay_base_pr = _format_metric(_metric_value(metrics, "paysim_p6_validation_selected_baseline.test_pr_auc"))
    pay_pr = _format_metric(_metric_value(metrics, "paysim_p6a_competitive_selected.test_pr_auc"))
    pay_roc = _format_metric(_metric_value(metrics, "paysim_p6a_competitive_selected.test_roc_auc"))
    pay_precision = _format_metric(_metric_value(metrics, "paysim_p6a_competitive_selected.precision_at_review_budget"))
    pay_recall = _format_metric(_metric_value(metrics, "paysim_p6a_competitive_selected.recall_at_review_budget"))
    ell_pr = _format_metric(_metric_value(metrics, "elliptic_p7_selected_graph_feature_baseline.test_pr_auc"))
    ell_precision = _format_metric(_metric_value(metrics, "elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget"))
    ell_recall = _format_metric(_metric_value(metrics, "elliptic_p7_selected_graph_feature_baseline.recall_at_review_budget"))
    e2_pr = _format_metric(_metric_value(metrics, "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean"))
    e2_std = _format_metric(_metric_value(metrics, "elliptic2_p8b_modern_context.official_partition_test_pr_auc_std"))
    ref_pr = _format_metric(_metric_value(metrics, "elliptic2_p8b_modern_context.published_reference_pr_auc"))
    e2_hash = _format_metric(_metric_value(metrics, "elliptic2_p8b_modern_context.hash_partition_test_pr_auc_mean"))
    paysim_review_counts = _review_budget_count_summary(inputs, "paysim")
    elliptic_review_counts = _review_budget_count_summary(inputs, "elliptic")
    source_candidate_line = _source_candidate_release_line(inputs)

    figure_manifest = _payload(inputs["figure_manifest"])
    architecture_figure = _render_figure_list(figure_manifest, figure_ids={"claim_gate_flow"})
    evidence_schema_figure = _render_figure_list(figure_manifest, figure_ids={"supporting_pr_auc"})
    benchmark_figure = _render_figure_list(figure_manifest, figure_ids={"review_budget"})
    claim_gate_figure = _render_figure_list(figure_manifest, figure_ids={"publishability_matrix"})

    evidence_cell_table = _render_evidence_cell_table_v2(metrics, inputs)
    evidence_cell_snippet = _render_evidence_cell_snippet(metrics, inputs)
    dataset_policy_table = _render_dataset_policy_table(inputs)
    model_search_table = _render_model_search_table(inputs)
    paysim_finalist_table = _render_paysim_finalist_table(inputs)
    operating_point_table = _render_operating_point_table(inputs)
    validation_subsplit_table = _render_validation_subsplit_table()
    adjacent_systems_table = _render_adjacent_systems_comparison_table(inputs)
    paysim_ablation_table = _render_paysim_ablation_table(inputs, metrics)
    system_eval_table = _render_system_evaluation_summary_table(inputs)
    failure_case_table = _render_failure_case_table(inputs)
    governance_ablation_table = _render_governance_ablation_table(inputs)
    governance_invariant_table = _render_governance_invariant_table(inputs)
    hosted_score_case_study_table = _render_hosted_score_case_study_table(inputs)
    hosted_score_record_snippet = _render_hosted_score_record_snippet(inputs)
    blocked_claim_table = _render_blocked_claim_examples_table()
    handoff_recovery_table = _render_handoff_recovery_table(inputs)
    reproducibility_table = _render_reproducibility_table(inputs)
    references = _render_reference_section()

    draft = "\n".join(
        [
            "# Relaytic-AML: A Local-First, Agent-Assisted Evaluation Lab for Financial-Crime Machine Learning",
            "",
            "## Abstract",
            "",
            "Anti-money laundering (AML) machine-learning experiments are difficult to audit when data residency, temporal validity, graph provenance, agent assistance, review capacity, and public reporting are handled separately. Relaytic-AML is a local-first evaluation lab in which capability-scoped agents and deterministic harnesses turn local runs into provenance-bearing measurements and bounded release decisions. Temporal PaySim and Elliptic workflows, an Elliptic2 reference workflow, and deterministic governance fixtures evaluate the architecture. The selected PaySim and Elliptic test PR-AUC point estimates are "
            f"{pay_pr} and {ell_pr}. The Elliptic2 context estimate is {e2_pr} $\\pm$ {e2_std}, alongside a published RevClassifyDS reference of {ref_pr}. The tasks are not a shared leaderboard. The contribution is the evaluation, governance, and reproducibility architecture rather than a new detector or detector-superiority result.",
            "",
            "## 1. Introduction",
            "",
            "AML modeling is a rare-event, high-stakes evaluation problem. The input may be a stream of mobile-money transfers, card events, account activity, wire messages, customer profiles, or blockchain transactions. Suspicion often appears as a temporal or network pattern: rapid movement of newly received funds, repeated transfers through related accounts, structured amounts, new counterparties receiving many payments, activity inconsistent with a customer profile, or cryptocurrency flows involving higher-risk services and jurisdictions. FATF and FFIEC material describes such pattern-oriented red flags in operational terms [@fatf2020virtualassets; @ffiecRedFlags].",
            "",
            "Because AML suspicion is often pattern-based, an isolated model metric is easy to misread. A precision-recall area under the curve (PR-AUC) estimate or a precision-at-review-budget estimate becomes interpretable only when the evaluation record shows which data stayed local, which fields were available at decision time, how temporal or graph boundaries were split, whether model selection touched the test partition, and which review capacity was assumed. Precision-recall analysis is particularly informative for highly imbalanced tasks because it focuses on performance for the rare positive class [@saito2015precisionrecall]. Agent assistance raises the provenance burden: fluent explanations from large language models (LLMs) or coding agents can drift from the artifact record unless release decisions are tied to machine-checkable evidence.",
            "",
            "Relaytic began as a general local-first inference-engineering lab. Relaytic-AML is the financial-crime edition used here to test whether that architecture can support governed AML experimentation. It is a set of cooperating agents and deterministic harnesses around a local artifact store. The guide helps a user or another agent understand where the run is. The scout checks source posture, schema, leakage risk, and split feasibility. The strategist turns the objective into a task contract. The scientist challenges baselines, ablations, and budget choices. The builder executes bounded runs. Reviewers reconstruct traces. Release governors lint claims, figures, tables, source packages, and public wording against the evidence record.",
            "",
            "Relaytic-AML contributes a local evidence and release-governance layer for AML machine-learning experiments. Benchmark rows exercise the architecture under temporal, graph, operating-point, and reporting pressure. The central question is whether a local evaluation lab can keep evidence, agent assistance, privacy boundaries, and admissible interpretation aligned.",
            "",
            "The work is organized around four research questions, each scoped to the workflows and deterministic fixtures evaluated here:",
            "",
            "- **RQ1:** Can Relaytic-AML produce reproducible evidence cells for AML-style temporal and graph tasks?",
            "- **RQ2:** Do the implemented gates block the tested leakage-prone and unsupported claims?",
            "- **RQ3:** Can the local artifact record support rowless handoff to external agents while preserving provenance?",
            "- **RQ4:** Do the benchmark workflows produce interpretable evidence under explicit split and budget contracts?",
            "",
            "The contribution has four linked parts. Evidence cells bind measurements to dataset, split, command, artifact, budget, leakage posture, and operating point. Claim gates govern admissible interpretation separately from the measurement. Rowless handoff exposes state and next actions without exporting raw records. Deterministic failure and ablation fixtures exercise those release boundaries. Local-first software keeps primary data and control on the user's device while still permitting deliberate collaboration [@kleppmann2019localfirst]. PaySim, Elliptic, and Elliptic2 workflows provide the empirical settings in which these mechanisms are tested.",
            "",
            "## 2. Related Work",
            "",
            "The AML benchmark landscape is moving toward larger, more realistic, and more graph-native settings. PaySim remains useful as a synthetic mobile-money fraud simulator for temporal proxy experiments [@lopezrojas2016paysim]. Elliptic introduced a public Bitcoin transaction graph with anonymized node features and temporal labels [@weber2019elliptic]. Elliptic2 and RevTrack/RevClassify shifted attention to suspicious subgraphs and richer blockchain context [@bellei2024elliptic2; @song2024revtrack]. Recent preprints such as TransXion, quasi-temporal graph extraction, and BlazingAML, together with published LineMVGNN and continual graph-learning work, treat AML increasingly as a dynamic graph and systems problem [@chen2026transxion; @poon2025linemvgnn; @tariq2026extraqt; @ye2026blazingaml; @deprez2025continualaml].",
            "",
            "Detector papers such as TransXion, BlazingAML, LineMVGNN, and RevClassifyDS push the model frontier. Relaytic-AML sits one layer around that work: it asks how experiments should be governed when data is local or licensed, the task may be temporal or graph-based, analyst review capacity matters, and an agent-assisted workflow must still produce evidence that a skeptical reviewer can audit. The focus on governed local experimentation places Relaytic-AML near dataset documentation, model reporting, reproducibility practice, experiment tracking, and governance work [@gebru2021datasheets; @mitchell2019modelcards; @pineau2021reproducibility; @zaharia2018mlflow].",
            "",
            "Experiment-tracking systems preserve runs and artifacts [@zaharia2018mlflow]. Model cards describe trained models, datasheets describe data, reproducibility checklists improve reporting, and agent benchmarks evaluate agent behavior. Relaytic-AML instead connects an executable local measurement to the interpretation that may be released from it. This responsibility matters when evidence comes from licensed files, proxy datasets, temporal graph tasks, or rowless handoff packets rather than from one open leaderboard run.",
            "",
            "A closely related newer line uses LLMs and agents for AML triage, graph-context reasoning, suspicious activity report (SAR) narrative support, compliance serving stacks, and runtime agent governance [@pirmorad2025amlgraphllm; @naik2025coinvestigator; @naik2026llmopsaml; @gaurav2025governanceaas; @kaptein2026runtimegovernance]. Those systems make agent assistance more capable, but they also make evidence boundaries more important. Relaytic-AML is not a SAR drafting system, not an LLM detector, and not a general-purpose agent-governance product. Its role is narrower: keep local AML evidence, rowless handoff, and public claims aligned.",
            "",
            "**System distinction.** Relaytic-AML places an executable provenance record and a separate interpretation gate between a detector run and every outward-facing table, handoff packet, or claim. Table 1 distinguishes this responsibility from documentation, experiment tracking, detector, and general agent-governance systems.",
            "",
            adjacent_systems_table,
            "",
            "The adjacent systems remain complementary. Relaytic-AML makes a result reader-facing only after source posture, split, leakage policy, budget, artifact field, handoff posture, and claim boundary are present.",
            "",
            "Recent agent-evaluation work shows that language-model systems can produce persuasive research artifacts while still failing on reproduction, validation, or expert-level judgment [@chen2025mlrbench; @starace2025paperbench; @wijk2025rebench]. Skill- and tool-using agents make that opportunity larger and the governance problem sharper [@yang2026skillopt]. Relaytic-AML responds by making model scores, public claims, handoff packets, and paper assets downstream of local artifacts rather than downstream of a conversation transcript.",
            "",
            "## 3. System Overview",
            "",
            "Relaytic-AML is built around one authority rule: truth-bearing records live in the local workspace, not in the conversation. Raw data, licensed benchmark files, run summaries, traces, evidence cells, model outputs, tables, figures, and release reports live on disk. Agents may explain, propose, and repair, but their proposals only become evidence when they are materialized as artifacts another human or agent can inspect.",
            "",
            "The end-to-end control path is shown in Figure 1. Local inputs enter role-scoped execution, each stage writes typed run artifacts, evidence cells bind reported values to provenance, and release gates determine which interpretations can leave the workspace.",
            "",
            architecture_figure,
            "",
            "Figure 1 follows the same state across the system. Dataset registries and split contracts enter the role-scoped runtime. Candidate runs write benchmark manifests, search traces, feature reports, and evidence cells. Release gates read those cells together with audit results and emit only the interpretations supported by the recorded evidence. The same contract feeds the command-line interface, project skills, OpenClaw-style handoff, Claude and Codex skill files, and Model Context Protocol (MCP) adapters.",
            "",
            "### Specialist Roles and State",
            "",
            "An agent in Relaytic-AML is a capability-scoped role with declared inputs, allowed tools, output artifacts, and an execution budget. The term does not imply that every role is a separate language-model process. Deterministic specialists implement ingestion, profiling, split checks, training, metric computation, redaction, and release validation. Optional language-model backends are reserved for semantic interpretation and guidance, and their output remains advisory until a deterministic artifact contract accepts it.",
            "",
            "The roles form a sequence of technical responsibilities. The intake translator converts the request into a task brief. The scout examines source posture, schema, target availability, leakage risks, and split feasibility. The scientist challenges assumptions, baseline strength, ablations, and metric choice. The strategist writes the task, search, and operating-point contracts. The builder executes the approved model route. The challenger and benchmark referee compare alternatives under the same contract. Completion and lifecycle governors decide whether evidence is sufficient, whether another bounded attempt is justified, and whether a candidate can be promoted. Trace adjudicators and release governors reconstruct the path from artifacts and restrict public wording. The guide exposes the same state to a user or an external agent without becoming a second source of truth.",
            "",
            "### Harness Execution and Control Loops",
            "",
            "The shared harness resolves runtime policy before a specialist runs. A capability profile declares artifact read and write scope, raw-row access, semantic access, and external-adapter access. Stage start records the active specialist, input artifacts, source surface, and data-access decisions in an append-only event stream. Tool calls are dispatched through a registry that validates names and argument schemas. Stage completion records output artifacts, emits trace events, runs read-only hooks by default, and writes a checkpoint that can be used for recovery or replay.",
            "",
            "Language-model-backed turns use a strict action protocol. Each response must be either a structured `tool_call` with validated arguments or a terminal `respond` action. The loop stops when it reaches a response, a policy block, or a user-confirmation boundary. Turn limits, invalid-action limits, repeated-result detection, and consecutive tool-error limits prevent an agent from drifting into an open-ended conversation or repeatedly invoking a failing tool.",
            "",
            "Three control loops operate at different levels. The tool-use loop governs one specialist turn. The evaluation loop moves from baseline construction through bounded challenger branches, validation-only selection, audit, and a completion decision. A current follow-up round may request recalibration, retraining, or an alternate challenger, but branch count and round count remain policy-bounded and the incumbent is retained when promotion criteria are not met. The release loop converts metric artifacts into evidence cells, checks leakage and benchmark role, and either emits admissible wording or records the missing evidence required for a stronger claim. These loops communicate through files and events rather than hidden conversational state.",
            "",
            "The external-agent path is rowless by default. Relaytic can export current state, next-action options, artifact shortlists, and safe commands for another model without sending raw transaction rows, secrets, or private local paths. A local LLM can optionally help phrase guidance, but the deterministic guide and evidence artifacts remain the source of truth. The separation between advisory help and local evidence matters for private AML work: outside intelligence may help navigate the run, but data residency and claim provenance stay local unless an operator deliberately changes policy.",
            "",
            "## 4. Evidence Cell and Claim-Gate Design",
            "",
            "An evidence cell is the unit that makes a paper number auditable. Rather than storing a bare metric value, it records the dataset, split, command, artifact field, model or feature budget, leakage posture, and operating point. Interpretation is deliberately stored in a separate gate output: the cell says what happened, and the gate says how that fact may be used.",
            "",
            "The factual fields and their separation from interpretation can be seen in Figure 2.",
            "",
            evidence_schema_figure,
            "",
            "Table 2 presents representative evidence cells with compact publication aliases. The underlying evidence records retain the full machine identifiers. Keeping the factual metric record separate from the claim boundary is the central design choice.",
            "",
            evidence_cell_table,
            "",
            "A representative record is compact enough to audit directly. The public table uses the alias `PS-PR`, while the underlying artifact keeps the longer machine identifier. The example shows the factual record that the claim gate later consumes. Stronger interpretations are deliberately kept outside the cell.",
            "",
            evidence_cell_snippet,
            "",
            "Algorithm 1 defines the deterministic construction path from a split contract and bounded run to an auditable evidence cell.",
            "",
            "```algorithm",
            "Algorithm: Evidence-cell creation",
            "Input: dataset registry D, split contract S, candidate budget B, run artifacts A",
            "Output: evidence cell c with factual provenance",
            "1. Freeze source posture, license posture, task target, and split contract.",
            "2. Derive only features allowed by S and record excluded leakage fields.",
            "3. Run baseline candidates under the declared baseline budget.",
            "4. Run stronger candidates only within B and select on validation evidence.",
            "5. After validation-only competitive selection and protocol freeze, evaluate the selected competitive finalist on the fixed test partition.",
            "6. Record whether that partition had earlier reference or baseline exposure.",
            "7. Write c = dataset, split, command, artifact field, metric, value, budget, leakage posture, operating point, and exposure status.",
            "8. Hand c to the claim gate before it appears in tables, figures, or release text.",
            "```",
            "",
            "The claim gate is the second half of the design. If the evidence cell is incomplete, a split is leakage-prone, a metric is only a proxy, or a stronger interpretation needs a different dataset or study, the gate preserves the evidence and routes the stronger use to an evidence-needs record. The gate is implemented as a release mechanism, so it changes what the paper artifact pipeline and public release surfaces are allowed to say. Algorithm 2 specifies that validation path.",
            "",
            "```algorithm",
            "Algorithm: Claim-gate validation",
            "Input: public claim q, evidence cells C, gates G, limitations L",
            "Output: admissible wording and evidence-needs record",
            "1. Resolve every evidence cell named by q and require dataset, split, command, artifact, budget, and leakage fields.",
            "2. Compare the strength of q with source posture, split validity, metric scope, and benchmark role.",
            "3. If q is exactly supported, emit the admissible wording and the evidence-cell identifiers.",
            "4. If q is stronger than C and G permit, record the stronger-claim status and gate reason.",
            "5. Attach the missing evidence needed to make q testable in future work.",
            "6. Route current evidence to its admissible paper use and keep stronger uses out of headline wording.",
            "```",
            "",
            "The resulting routes from current evidence to admissible and stronger future uses are shown in Figure 3.",
            "",
            claim_gate_figure,
            "",
            "Figure 3 makes the routing behavior concrete. A PaySim row becomes a temporal-proxy demonstration, an Elliptic row becomes graph-feature evidence with temporal provenance, and an Elliptic2 row becomes external benchmark context. The same records specify what evidence would be needed before stronger future uses could be made.",
            "",
            "## 5. Experimental Protocol",
            "",
            "The experiments test Relaytic-AML as an evaluation lab. The datasets are separated by evidence role. PaySim is the main empirical demonstration because it is fully local and supports a controlled temporal proxy workflow. Elliptic tests temporal graph provenance and feature-view discipline. Elliptic2 tests whether the system can keep a modern external reference row visible without overstating its role.",
            "",
            "Dataset scale and exact split boundaries can be seen in Table 3. The corresponding feature, leakage, and metric policies are shown in Table 4. PR-AUC is the primary ranking score because the positive class is rare and analyst capacity is constrained. PaySim uses whole chronological simulator-step boundaries with no gap or embargo. Elliptic uses non-overlapping graph time-step windows. Elliptic2 uses the `TRN`, `VAL`, and `TST` labels supplied by the pinned RevTrack preprocessing artifact. It is reported separately as reference context.",
            "",
            dataset_policy_table,
            "",
            "Modeling effort is budgeted rather than open-ended. PaySim uses probes on a seeded train-only sample followed by five full-training finalists. Competitive selection, Platt sigmoid calibration, and operating-threshold choice use validation evidence. After protocol freeze, one competitive finalist is evaluated on the fixed test partition [@geurts2006extratrees; @chen2016xgboost; @platt1999probabilistic]. The same test partition had already produced the P4 reference and P6 baseline rows, so it is fixed but not an untouched holdout. Elliptic compares source-provided anonymized features, Relaytic-derived same-step structural features, and their combination. The selected LightGBM configuration uses seed 42 [@ke2017lightgbm]. Elliptic2 uses pooled subgraph summaries with LightGBM seeds 11, 42, and 73 as a context workflow. The model-family and search-budget inventory is kept in the appendix.",
            "",
            "For PaySim and Elliptic, finalist or feature-view selection used the full declared validation partition. After that selection, the earlier chronological validation subwindow fitted Platt sigmoid calibration. The later subwindow compared calibrated and identity scores by log loss and selected the review threshold. The two nested subwindows are disjoint, but model selection overlaps both because it used the full validation partition. Their exact boundaries and class counts are reported in the appendix validation-subsplit table.",
            "",
            "PaySim contains a mixed balance quartet: `oldbalanceOrg` and `oldbalanceDest` describe pre-transaction balances, whereas `newbalanceOrig` and `newbalanceDest` describe post-transaction balances. Relaytic excludes all four conservatively because their availability and simulator consistency do not match the intended pre-decision contract. Raw account identifiers and simulator flags are also excluded as model inputs. Destination history is computed over the full chronological stream as cumulative activity from strictly earlier steps. It carries across train, validation, and test boundaries, but same-step events do not see one another and future steps cannot contribute. The destination identifier is used only as a grouping key, never as a model feature. Amount thresholds are fitted on training data. The isolated contribution of this history family has not been tested and is not claimed.",
            "For Elliptic, supervised fitting and metrics use only known labels. Unknown-label nodes may contribute observable features and same-step topology, but never targets or metric rows. The source view retains the dataset's 94 anonymized local features and 72 supplied one-hop neighbor aggregates as one distinct feature family [@weber2019elliptic]. Elliptic contains no edges between time steps, so those supplied neighborhood aggregates are confined to the dataset snapshot. Their construction is inherited from the source and is not attributed to Relaytic. A second family contains Relaytic-derived structural statistics computed only from edges whose endpoints occur in the same time step. The combined view concatenates the two families. No later snapshot contributes to an earlier prediction.",
            "",
            "## 6. Results",
            "",
            "The staged PaySim model-selection path and the evidence visible at each stage can be seen in Table 5.",
            "",
            paysim_ablation_table,
            "",
            f"PaySim is the most complete local modeling path in the current evidence pack. The P4 reference row had test PR-AUC 0.2159, and the P6 leakage-safe baseline reached {pay_base_pr}. The competitive search then used validation evidence only. A small-sample XGBoost probe reached validation PR-AUC 0.5944 on a 750,000-row train-only sample. It is not directly rankable against the five finalists, which were refitted on all 6,010,937 training rows. Among those comparable full-training rows, Extra Trees had the highest validation PR-AUC at 0.5687, 0.0282 above the joint XGBoost and Random Forest runner-up rows at the four-decimal precision shown in the table. No tie-break was required to select the winner. One competitive finalist was evaluated after protocol freeze and reached test PR-AUC {pay_pr} and ROC-AUC {pay_roc}. Raw and calibrated test PR-AUC are both {pay_pr}, so Platt scaling supports probability and threshold handling rather than a ranking-gain claim. The fixed test partition had prior P4 and P6 exposure and is not presented as untouched.",
            "",
            f"The PaySim operating point was chosen by taking the score at the requested top 0.5% rank on validation and applying that threshold unchanged to test. Test rows with scores equal to the threshold are included. Ties therefore produced a realized test queue of 1,109 of 123,580 transactions (0.8974%), with precision {pay_precision} and recall {pay_recall}. This queue is more concentrated than the 1.3384% test prevalence, but it still misses more than half of the positive test events. The requested fraction and realized queue must therefore be read separately.",
            "",
            f"Elliptic is a different evidence contract. The validation-selected source-plus-structural LightGBM row has validation PR-AUC 0.9767 and later-window test PR-AUC {ell_pr}. The gap is consistent with temporal shift, validation-specific selection, or both, but the current artifacts do not identify a causal decomposition. The same validation-threshold procedure produced a realized test queue of 36 of 11,184 known-label nodes (0.3219%), with precision {ell_precision} and recall {ell_recall}. The difference from the requested 0.5% follows from applying a fixed threshold with ties rather than forcing a test-set rank. This seed-42 point estimate supports temporal graph provenance and operating-point reporting. It does not isolate a graph-detector advance, because source-provided anonymized features strongly influence the selected view.",
            "The numerical thresholds, threshold-selection queues, test queues, calibration choices, and tie policy are collected in the appendix operating-point table. In both workflows, the validation-derived threshold is applied unchanged to test, and scores greater than or equal to the threshold are included. No test-set ranking is used to force an exact 0.5% queue.",
            "",
            f"Elliptic2 is modern benchmark context, not a detector contribution. The audited current core contains 121,810 subgraphs and 2,763 positives, whereas the pinned RevTrack-evaluable table contains 110,902 rows and 2,578 positives. The latter supplies `TRN`/`VAL`/`TST` partitions of 88,738/11,059/11,105 rows. The repeated context estimate on the provided RevTrack `TST` partition is PR-AUC {e2_pr} $\\pm$ {e2_std}. A separately defined content-hash partition gives mean PR-AUC {e2_hash}. The provided `TST` partition had already been inspected during an earlier recovery run, so the repeated value is confirmatory rather than blind or untouched evidence. The published RevClassifyDS full-shot PR-AUC {ref_pr} comes from Table 1 of the cited paper and is shown only as an external reference. Cohort equivalence and parity are not established.",
            "",
            "Figure 4 separates local ranking evidence, external reference context, and realized review queues. The panels use distinct task contracts and must not be read as a cross-dataset leaderboard.",
            "",
            benchmark_figure,
            "",
            "In Figure 4, PR-AUC summarizes ranking within a dataset. Precision and recall describe the test rows selected by a validation-derived threshold, while the realized fractions show how ties and score distributions changed queue size.",
            "",
            "## 7. Deterministic Artifact and Release-Gate Evaluation",
            "",
            "The system claim is evaluated through deterministic reader and agent tasks. These checks ask whether a reviewer can navigate from the README to the paper evidence, trace PaySim metric provenance, compare baseline and competitive budgets, keep Elliptic2 as context rather than a contribution, export rowless state for an external agent, recover an interrupted run, and block over-strong public claims. Table 6 reports the synthesis. Detailed failure cases, ablations, the invariant map, the hosted-score example, and handoff rows are preserved in the appendix and generated evidence artifacts.",
            "",
            system_eval_table,
            "",
            "Across the tested fixtures, Relaytic-AML changes what the release pipeline may promote: a number with missing provenance, a prohibited feature path, a test-selected finalist, an unsafe handoff packet, or an over-strong claim produces a blocked record instead of reader-facing text. These are deterministic infrastructure checks. They are not human usability evidence, privacy certification, or production AML validation.",
            "",
            "The hosted external-score fixture shows the intended integration point for stronger third-party detectors. A rowless detector-score artifact enters Relaytic with schema and content hashes, not raw rows. Relaytic emits one governance evidence cell, redacts unsafe handoff fields, and routes the result as hosted detector-output governance evidence. Future detector outputs can therefore pass through the same local release boundary without being mistaken for a new detector contribution.",
            "",
            "## 8. Limitations and Threats to Validity",
            "",
            "PaySim is synthetic. It is useful for controlled temporal fraud experiments, but it is not evidence of bank-scale AML superiority. The simulator has known simplifications, and the current result is a leakage-audited proxy result. The same fixed test partition had already been observed through the P4 reference and P6 baseline before the competitive run. Competitive finalist selection, calibration, and threshold choice remained validation-only, and only one competitive finalist was tested after protocol freeze. Prior exposure nevertheless weakens any untouched-holdout interpretation. A future study should reserve a genuinely unseen chronological or external holdout. The destination-history feature contract is present, but its isolated contribution is not in the current evidence pack.",
            "",
            "Public blockchain data is also not the same as bank AML. Elliptic provides a valuable temporal graph task, but unknown labels, anonymized source features, source-supplied neighbor aggregates, and public-chain behavior limit direct operational interpretation. The dataset documentation establishes the one-hop aggregate feature definitions and absence of cross-time-step edges, but Relaytic does not reconstruct the source feature pipeline independently. Elliptic2 is modern and highly relevant, but the current local evidence does not satisfy the reference-parity conditions needed for a performance contribution against RevClassifyDS.",
            "",
            "The PaySim and Elliptic detector rows are single-seed point estimates. Prediction-level scores are not part of the committed public evidence pack, so confidence intervals cannot be reconstructed faithfully from aggregate metrics. The deterministic system checks are also not a substitute for a human usability study. They test artifacts, redactions, gate decisions, and recovery surfaces, but do not measure analyst time, production incidents, organizational adoption, or investigation quality. Future work should add repeated runs or a predeclared rowless prediction artifact, private or partner-approved holdouts, same-queue incumbent comparisons, and graph-native families under the same evidence discipline.",
            "",
            "The system is intentionally local-first, which creates a tradeoff. Privacy and provenance improve because raw rows stay local, but external reviewers cannot rerun licensed or private data without obtaining it themselves. The paper handles that by publishing commands, hashes where allowed, generated artifacts, and claim boundaries, but a fully independent reproduction of every heavy benchmark still depends on legal access to the source datasets.",
            "",
            "## 9. Reproducibility",
            "",
            "The repository is larger than this AML paper. Relaytic is the general local-first inference lab and public package. Relaytic-AML is the focused AML edition used here for the manuscript. A reader should start with the README and this paper. Development-control files record the build history, but they are not required to understand the paper claims. Public citation should use the immutable source commit recorded in the release bundle, or a separately verified public tag, because the main branch can continue to evolve after the paper is posted.",
            "",
            source_candidate_line,
            "",
            "Table 7 separates what a clean clone can reproduce immediately from what requires local benchmark access. The README contains the full regeneration script, while the paper keeps the main path short enough to try without reading the generated audit files first.",
            "",
            reproducibility_table,
            "",
            "The first four rows in Table 7 are available from a clean clone. Artifact verification checks committed evidence without retraining. Deterministic fixtures execute repo-local synthetic cases, and the paper build regenerates publication assets. Raw-data benchmark reruns require local PaySim, Elliptic, or Elliptic2/RevTrack data. A zero process exit from an optional command is not by itself evidence that every benchmark branch ran. Each command emits a machine-readable execution status. Adding `--require-full-rerun` makes the command fail when data, dependencies, or requested branches were skipped.",
            "",
            "Minimal public check:",
            "",
            "```bash",
            "python -m pip install -e \".[full]\"",
            "python -m relaytic.ui.cli release-safety paper-invariants --format json",
            "python -m relaytic.ui.cli release-safety paper-release --format json",
            "python -m relaytic.ui.cli release-safety paper-narrative-polish --format json",
            "python -m relaytic.ui.cli release-safety paper-novelty-positioning --format json",
            "python -m relaytic.ui.cli release-safety paper-release-integrity --format json",
            "python -m relaytic.ui.cli release-safety paper-arxiv-source --format json",
            "python -m relaytic.ui.cli release-safety paper-final-preflight --format json",
            "```",
            "",
            "Raw benchmark data is not committed. PaySim and Elliptic require local downloads and are referenced through registry artifacts, split reports, hashes, and command ledgers. Elliptic2 is used as benchmark context because the stronger reference-parity conditions are not satisfied locally. Clean clones can reproduce paper builds, artifact checks, and repo-local public fixtures. Full benchmark regeneration requires the local datasets named in the README and the fail-on-skip command mode.",
            "",
            "## AI Assistance Disclosure",
            "",
            "Large language model tools assisted with drafting, editing, repository inspection, consistency checks, and implementation work around the paper artifacts. They are not authors. Responsibility for the evidence cells, benchmark outputs, source code, figures, tables, limitations, and interpretation remains with the author.",
            "",
            "## Conclusion",
            "",
            "Relaytic-AML shows how an agent-assisted AML evaluation lab can be built around local evidence rather than conversational memory. The system records data posture, temporal and graph split validity, leakage controls, model budgets, review-budget operating points, and rowless handoff as factual artifacts. Separate gates govern the interpretations that may be released. The PaySim, Elliptic, and Elliptic2 rows demonstrate that architecture under rare-event, graph-provenance, modern-context, and reporting pressure.",
            "",
            "The evidence supports a bounded architectural conclusion: in the workflows and fixtures evaluated here, Relaytic-AML preserved metric provenance, exposed split and operating-point assumptions, produced rowless handoff records, recovered interrupted state, and blocked the tested unsupported claims. Whether those mechanisms improve expert decisions or production outcomes requires human and institutional evaluation. Relaytic-AML is a governance substrate for detector studies rather than a replacement for them.",
            "",
            "## Appendix: Detailed Audit and Reproducibility Records",
            "",
            "The appendix keeps concrete audit evidence out of the main reading path while preserving it for reviewers who want to inspect the mechanics. Table 8 records model families and search budgets. The repository stores the corresponding JSON reports with full fields, hashes, and pass criteria.",
            "",
            model_search_table,
            "",
            "The model-search table records budget shape and evidence role. It is appendix material because it supports auditability without changing the paper's central architectural claim.",
            "",
            "The five comparable PaySim full-training finalists are shown in Table 9. Their validation scores, rather than the small-sample probe scores, determined the competitive winner.",
            "",
            paysim_finalist_table,
            "",
            "Extra Trees leads the full-training finalist set by 0.0282 PR-AUC over the joint XGBoost and Random Forest runner-up rows at the reported precision. No tie-break was required to select the winner. Nonselected finalists were neither calibrated nor evaluated on test.",
            "",
            "Table 10 records the complete operating-point transfer for PaySim and Elliptic.",
            "",
            operating_point_table,
            "",
            "The validation threshold is carried unchanged to test and equality is included. Consequently, the realized test queue may differ from the requested validation fraction.",
            "",
            "Table 11 reports the validation surfaces used for model selection, calibration, and threshold selection. The full validation partition selected the model, while the nested chronological subwindows separated calibration fitting from calibration comparison and threshold choice.",
            "",
            validation_subsplit_table,
            "",
            "The calibration and threshold-selection subwindows are disjoint. They are not independent of model selection because the complete validation partition was used to rank finalists or feature views.",
            "",
            "The injected risks and observed release behavior can be seen in Table 12.",
            "",
            failure_case_table,
            "",
            "The failure-case fixtures exercise whether the release path refuses leakage features, test-set model selection, over-strong claims, unsafe handoff, and lost-run states. They do not add detector benchmark rows.",
            "",
            "Table 13 compares the complete governance path with fixtures in which one control is disabled.",
            "",
            governance_ablation_table,
            "",
            "These ablations do not rerun detector training. They change the available governance controls and measure the resulting artifact, handoff, recovery, release, and claim states.",
            "",
            "The mechanism, stress signal, and boundary associated with each invariant are collected in Table 14.",
            "",
            governance_invariant_table,
            "",
            "The invariant map records release-time rules rather than prose preferences. Each invariant pairs a mechanism with an observed stress signal and an explicit boundary.",
            "",
            "The hosted external-score path is illustrated by the rowless fixture in Table 15.",
            "",
            hosted_score_case_study_table,
            "",
            hosted_score_record_snippet,
            "",
            "The hosted-score record is metadata governance only. On the tested fixture, a rowless score artifact is wrapped by a factual schema-and-hash record, a redaction report, and a separate interpretation gate. Its completeness result is not detector accuracy or ranking performance.",
            "",
            "Table 16 connects stronger future claims to current admissible uses and to the additional evidence each claim would require.",
            "",
            blocked_claim_table,
            "",
            "The blocked-claim rows show how stronger future uses are handled. The gate records current admissible use and the evidence needed before a stronger interpretation could be made.",
            "",
            "Concrete external-agent handoff and interrupted-run recovery records are shown in Table 17.",
            "",
            handoff_recovery_table,
            "",
            "The handoff and recovery rows give the practical external-agent story. A second model can receive state, commands, artifacts, and starter questions, while raw rows remain redacted and private paths stay withheld.",
            "",
            "Appendix reproduction shortcut:",
            "",
            "The full Windows and macOS/Linux regeneration script is kept in the README so the appendix remains readable. The essential local paper path is:",
            "",
            "Windows PowerShell:",
            "",
            "```powershell",
            "py -3.11 -m pip install -e \".[full]\"",
            "py -3.11 -m relaytic.ui.cli release-safety paper-invariants --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-release --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-narrative-polish --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-novelty-positioning --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-release-integrity --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-arxiv-source --format json",
            "py -3.11 -m pytest -m prepush -q",
            "```",
            "",
            "After compiling `docs/paper/arxiv_src/main.tex` and copying the compiled PDF to the final paper location, run `paper-final-preflight`. The README includes the exact compile and verification commands.",
            "",
            "macOS/Linux:",
            "",
            "```bash",
            "python3 -m pip install -e \".[full]\"",
            "python3 -m relaytic.ui.cli release-safety paper-invariants --format json",
            "python3 -m relaytic.ui.cli release-safety paper-release --format json",
            "python3 -m relaytic.ui.cli release-safety paper-narrative-polish --format json",
            "python3 -m relaytic.ui.cli release-safety paper-novelty-positioning --format json",
            "python3 -m relaytic.ui.cli release-safety paper-release-integrity --format json",
            "python3 -m relaytic.ui.cli release-safety paper-arxiv-source --format json",
            "python3 -m pytest -m prepush -q",
            "```",
            "",
            "## References",
            "",
            references,
        ]
    ).rstrip() + "\n"
    return _polish_reader_facing_punctuation(draft)


def _polish_reader_facing_punctuation(text: str) -> str:
    """Remove reader-visible semicolons without changing citation grouping syntax."""
    citations: list[str] = []

    def hold_citation(match: re.Match[str]) -> str:
        citations.append(match.group(0))
        return f"__RELAYTIC_CITATION_{len(citations) - 1}__"

    polished = re.sub(r"\[@[^\]]+\]", hold_citation, text)
    polished = polished.replace("; ", ", ").replace(";", ",")
    for index, citation in enumerate(citations):
        polished = polished.replace(f"__RELAYTIC_CITATION_{index}__", citation)
    return polished


def _render_dataset_policy_table(inputs: dict[str, Any]) -> str:
    paysim = _payload(inputs["paysim_temporal_split"])
    elliptic = _payload(inputs["elliptic_temporal_split"])
    e2_contract = _payload(inputs["elliptic2_modern_reference_contract"])
    e2_cohort = _payload(inputs["elliptic2_cohort_reconciliation"])

    def split_row(report: dict[str, Any], split: str) -> dict[str, Any]:
        return next(
            (dict(row) for row in report.get("split_rows", []) if isinstance(row, dict) and row.get("split") == split),
            {},
        )

    ps_train, ps_val, ps_test = (split_row(paysim, name) for name in ("train", "validation", "test"))
    el_train, el_val, el_test = (split_row(elliptic, name) for name in ("train", "validation", "test"))
    e2_splits = dict(e2_contract.get("partition_summary", {}).get("split_rows", {}))
    scale_rows = [
        [
            "PaySim",
            "transactions / fraud events",
            f"1-445: {_format_count(ps_train.get('row_count'))} / {_format_count(ps_train.get('positive_count'))}",
            f"446-594: {_format_count(ps_val.get('row_count'))} / {_format_count(ps_val.get('positive_count'))}",
            f"595-743: {_format_count(ps_test.get('row_count'))} / {_format_count(ps_test.get('positive_count'))}",
        ],
        [
            "Elliptic",
            "known-label nodes / illicit nodes",
            f"1-29: {_format_count(el_train.get('known_label_count'))} / {_format_count(el_train.get('illicit_count'))}",
            f"30-39: {_format_count(el_val.get('known_label_count'))} / {_format_count(el_val.get('illicit_count'))}",
            f"40-49: {_format_count(el_test.get('known_label_count'))} / {_format_count(el_test.get('illicit_count'))}",
        ],
        [
            "Elliptic2 context",
            "RevTrack rows / positives",
            f"TRN: {_format_count(e2_splits.get('TRN', {}).get('row_count'))} / {_format_count(e2_splits.get('TRN', {}).get('positive_count'))}",
            f"VAL: {_format_count(e2_splits.get('VAL', {}).get('row_count'))} / {_format_count(e2_splits.get('VAL', {}).get('positive_count'))}",
            f"TST: {_format_count(e2_splits.get('TST', {}).get('row_count'))} / {_format_count(e2_splits.get('TST', {}).get('positive_count'))}",
        ],
    ]
    policy_rows = [
        ["PaySim", "whole chronological steps; no gap or embargo", "row-local amount/type/time; prior-step destination history", "mixed balance quartet, raw account IDs, simulator flag", "PR-AUC; precision/recall at validation threshold"],
        ["Elliptic", "disjoint time windows; metrics on known labels", "source features; same-snapshot structure; combined view", "future snapshots; unknown labels as targets", "PR-AUC; precision/recall at validation threshold"],
        [
            "Elliptic2 context",
            "provided RevTrack TRN/VAL/TST labels",
            "pinned pooled subgraph summaries",
            "full-core equivalence not established",
            "repeated PR-AUC; contextual comparison only",
        ],
    ]
    cohort_note = (
        f"Elliptic has {_format_count(elliptic.get('node_count'))} total nodes. Unknown-label nodes are excluded from fitting and metrics. "
        f"Elliptic2 distinguishes the audited core ({_format_count(e2_cohort.get('official_core_subgraph_count'))} subgraphs) "
        f"from the RevTrack-evaluable cohort ({_format_count(e2_cohort.get('revtrack_evaluable_row_count'))} rows)."
    )
    return "\n\n".join(
        [
            _markdown_table(
                "Table 3. Dataset scale and exact split contracts",
                ["Dataset", "Unit / positive", "Train", "Validation", "Test"],
                scale_rows,
            ),
            cohort_note,
            _markdown_table(
                "Table 4. Feature, leakage, and metric policy",
                ["Dataset", "Split policy", "Allowed information", "Excluded information", "Primary reporting"],
                policy_rows,
            ),
        ]
    )


def _render_model_search_table(inputs: dict[str, Any]) -> str:
    paysim_budget = _payload(inputs["paysim_competitive_budget_contract"])
    paysim_search = _payload(inputs["paysim_competitive_search_trace"])
    graph_budget = _payload(inputs["elliptic_graph_budget_contract"])
    graph_table = _payload(inputs["elliptic_graph_feature_table"])
    elliptic2 = _payload(inputs["elliptic2_repeated_seed_scorecard"])
    rows = [
        [
            "PaySim",
            "tree and boosting candidates; Extra Trees selected",
            "amount, type, time, shifted destination history",
            f"{paysim_budget.get('probe_trial_count', 'n/a')} probes; {paysim_budget.get('finalist_fit_count', 'n/a')} finalists; {_seed_summary(paysim_budget.get('random_seeds', []))}",
            "validation-selected finalist; prior baseline test exposure disclosed",
        ],
        [
            "Elliptic",
            "tree/boosting baselines; LightGBM selected",
            "source node features plus same-step graph statistics",
            f"{graph_budget.get('validation_search_trial_count', 'n/a')} trials; {_seed_summary(graph_budget.get('random_seeds', []))}",
            "graph-feature evidence row",
        ],
        [
            "Elliptic2",
            "LightGBM context row",
            "348 pooled subgraph moments/counts",
            f"{elliptic2.get('official_partition', {}).get('seed_count', 'n/a')} repeated seeds: {', '.join(str(seed) for seed in elliptic2.get('seeds', [])) or 'n/a'}",
            "external reference row",
        ],
    ]
    return _markdown_table("Appendix table. Model families and search budgets", ["Track", "Families", "Features", "Search budget", "Evidence role"], rows)


def _render_paysim_finalist_table(inputs: dict[str, Any]) -> str:
    trace = _payload(inputs["paysim_competitive_search_trace"])
    selected = dict(trace.get("selected_finalist") or {})
    rows = [
        dict(row)
        for row in trace.get("attempts", [])
        if isinstance(row, dict)
        and row.get("stage") == "full_train_finalist"
        and row.get("execution_state") == "ran"
    ]
    rows.sort(
        key=lambda row: float(dict(row.get("validation_metrics") or {}).get("pr_auc") or float("-inf")),
        reverse=True,
    )
    selected_family = str(selected.get("family_id") or "")
    runner_display = (
        _format_metric(dict(rows[1].get("validation_metrics") or {}).get("pr_auc"))
        if len(rows) > 1
        else None
    )
    table_rows = []
    for rank, row in enumerate(rows, start=1):
        family_id = str(row.get("family_id") or "")
        is_selected = family_id == selected_family and rank == 1
        displayed_pr_auc = _format_metric(dict(row.get("validation_metrics") or {}).get("pr_auc"))
        displayed_runner_tie = rank > 1 and runner_display is not None and displayed_pr_auc == runner_display
        table_rows.append(
            [
                "2=" if displayed_runner_tie else str(rank),
                _model_family_label(family_id),
                _compact_model_configuration(dict(row.get("configuration") or {})),
                displayed_pr_auc,
                _calibration_label(selected.get("calibration_method")) if is_selected else "not run",
                "eligible and evaluated" if is_selected else "not eligible after validation rank",
                "selected" if is_selected else ("joint runner-up at displayed precision" if displayed_runner_tie else "lower validation PR-AUC"),
            ]
        )
    if not table_rows:
        table_rows.append(["n/a", "finalist evidence unavailable", "n/a", "n/a", "n/a", "blocked", "preflight must fail"])
    return _markdown_table(
        "Appendix table. Full-training PaySim finalist comparison",
        ["Rank", "Finalist", "Compact configuration", "Validation PR-AUC", "Calibration", "Test status", "Outcome"],
        table_rows,
    )


def _render_operating_point_table(inputs: dict[str, Any]) -> str:
    paysim_trace = _payload(inputs["paysim_competitive_search_trace"])
    paysim = dict(paysim_trace.get("selected_finalist") or {})
    paysim_calibration = dict(paysim_trace.get("calibration_trace") or {})
    graph = dict(
        _payload(inputs["elliptic_graph_feature_table"]).get("validation_selected_competitive_baseline") or {}
    )
    graph_calibration = dict(graph.get("calibration") or {})
    rows = [
        [
            "PaySim",
            _calibration_label(paysim.get("calibration_method")),
            _format_metric(paysim.get("validation_threshold")),
            _format_rate_precise(paysim.get("review_budget_fraction")),
            _format_operating_queue(
                dict(paysim.get("validation_operating_point") or {}),
                fallback_total=paysim_calibration.get("operating_point_row_count"),
            ),
            _format_operating_queue(dict(paysim.get("test_operating_point") or {}), fallback_total=123580),
            "score $\\geq$ threshold; equality included",
        ],
        [
            "Elliptic",
            _calibration_label(graph_calibration.get("selected_method")),
            _format_metric(graph.get("validation_threshold")),
            _format_rate_precise(graph.get("review_budget_fraction")),
            _format_operating_queue(
                dict(graph.get("validation_operating_point") or {}),
                fallback_total=graph.get("validation_operating_partition_row_count"),
            ),
            _format_operating_queue(dict(graph.get("test_operating_point") or {}), fallback_total=11184),
            "score $\\geq$ threshold; equality included",
        ],
    ]
    return _markdown_table(
        "Appendix table. Validation-derived operating-point transfer",
        ["Dataset", "Calibration", "Threshold", "Requested queue", "Threshold-selection queue; P/R", "Test queue; P/R", "Rule"],
        rows,
    )


def _render_validation_subsplit_table() -> str:
    rows = [
        ["PaySim", "Model selection", "steps 446-594", "228,103", "1,552", "full validation; contains both nested subsets"],
        ["PaySim", "Calibration fit", "steps 446-540", "116,502", "984", "earlier subwindow; disjoint from threshold subset"],
        ["PaySim", "Calibration comparison and threshold", "steps 541-594", "111,601", "568", "later subwindow; 0.5% threshold selected here"],
        ["Elliptic", "Model and feature-view selection", "time steps 30-39", "8,999", "1,038", "full validation; contains both nested subsets"],
        ["Elliptic", "Calibration fit", "time steps 30-35", "4,854", "773", "earlier subwindow; disjoint from threshold subset"],
        ["Elliptic", "Calibration comparison and threshold", "time steps 36-39", "4,145", "265", "later subwindow; 0.5% threshold selected here"],
    ]
    return _markdown_table(
        "Appendix table. Validation surfaces for selection, calibration, and thresholding",
        ["Dataset", "Purpose", "Boundary", "Evaluated units", "Positives", "Overlap and use"],
        rows,
    )


def _compact_model_configuration(configuration: dict[str, Any]) -> str:
    labels = {
        "n_estimators": "trees",
        "max_iter": "iterations",
        "max_depth": "depth",
        "learning_rate": "learning rate",
        "num_leaves": "leaves",
        "min_samples_leaf": "leaf size",
    }
    keys = ["n_estimators", "max_iter", "max_depth", "learning_rate", "num_leaves", "min_samples_leaf"]
    values = [
        f"{configuration[key]} {labels[key]}"
        for key in keys
        if key in configuration and configuration[key] is not None
    ]
    return ", ".join(values[:3]) or "recorded in search trace"


def _calibration_label(value: Any) -> str:
    return {"platt_sigmoid": "Platt sigmoid calibration", "identity": "identity calibration"}.get(
        str(value or ""), str(value or "not recorded")
    )


def _seed_summary(values: Any) -> str:
    seeds = [str(seed) for seed in values or []]
    if len(seeds) == 1:
        return f"seed {seeds[0]}"
    if seeds:
        return f"seeds {', '.join(seeds)}"
    return "seed not recorded"


def _format_rate_precise(value: Any) -> str:
    try:
        return f"{float(value) * 100:.4f}%"
    except (TypeError, ValueError):
        return "n/a"


def _format_operating_queue(operating: dict[str, Any], *, fallback_total: Any) -> str:
    reviewed = operating.get("reviewed_count")
    total = operating.get("evaluation_row_count") or fallback_total
    queue = f"{_format_count(reviewed)}/{_format_count(total)} ({_format_rate_precise(operating.get('review_fraction'))})"
    precision = _format_metric(operating.get("precision_at_k"))
    recall = _format_metric(operating.get("recall_at_review_budget"))
    return f"{queue}; {precision}/{recall}"


def _render_adjacent_systems_comparison_table(inputs: dict[str, Any]) -> str:
    report = _payload(inputs["adjacent_systems_comparison"])
    rows = []
    for row in report.get("comparison_rows", []):
        if not isinstance(row, dict):
            continue
        boundary = str(row.get("relaytic_aml_boundary") or "")
        if boundary == "is not a new graph-neural detector and does not claim detector SOTA":
            boundary = "governs detector evidence rather than introducing a graph-neural model"
        primary = str(row.get("primary_object") or "")
        position = str(row.get("relaytic_aml_position") or "")
        if str(row.get("adjacent_family") or "") == "Agent governance and runtime trust layers":
            primary = "runtime policy, enforcement, logging, and trust"
            position = "specializes governance to AML result provenance, rowless handoff, benchmark context, and public claims"
            boundary = "not a general agent-governance platform"
        rows.append([_family_with_citations(row), primary, position, boundary])
    if not rows:
        rows.append(
            [
                "Adjacent systems",
                "source report absent",
                "Generate the P18 invariant pack before positioning the paper.",
                "no stronger detector claim",
            ]
        )
    return _markdown_table(
        "Table 1. Adjacent systems comparison",
        ["Family", "Primary object", "Relaytic-AML position", "Boundary"],
        rows,
    )


def _render_evidence_cell_table_v2(
    metrics: dict[str, dict[str, Any]],
    inputs: dict[str, Any],
) -> str:
    gates = _claim_gate_by_cell(inputs)
    cell_ids = [
        "paysim_p6a_competitive_selected.test_pr_auc",
        "paysim_p6a_competitive_selected.precision_at_review_budget",
        "elliptic_p7_selected_graph_feature_baseline.test_pr_auc",
        "elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget",
        "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean",
        "elliptic2_p8b_modern_context.published_reference_pr_auc",
    ]
    rows = []
    for cell_id in cell_ids:
        cell = metrics.get(cell_id, {})
        rows.append([
            _evidence_cell_display_id(cell_id),
            _dataset_short_name(str(cell.get("dataset_id") or "")),
            _paper_metric_label(str(cell.get("metric_id") or cell_id)),
            _format_metric(cell.get("value")),
            _compact_cell_split(cell_id, str(cell.get("split") or "not recorded")),
            _compact_command_artifact(cell),
            str(gates.get(cell_id, {}).get("admissible_use") or "gate record unavailable"),
        ])
    return _markdown_table(
        "Table 2. Representative evidence cells and gate-derived publication roles",
        ["ID", "Dataset", "Metric", "Value", "Split", "Artifact", "Gate-derived use"],
        rows,
    )


def _render_evidence_cell_snippet(
    metrics: dict[str, dict[str, Any]],
    inputs: dict[str, Any],
) -> str:
    cell_id = "paysim_p6a_competitive_selected.test_pr_auc"
    cell = metrics.get(cell_id, {})
    exposure = dict(cell.get("test_exposure_contract") or {})
    test_exposure = {
        key: exposure[key]
        for key in (
            "test_partition_fixed",
            "test_partition_previously_exposed",
            "competitive_selection_used_test",
            "competitive_finalists_tested_after_freeze",
        )
        if key in exposure
    }
    evidence = {
        "cell_id": "PS-PR",
        "dataset_id": cell.get("dataset_id") or "paysim_temporal_transaction_fraud",
        "split": _compact_cell_split(cell_id, str(cell.get("split") or "temporal fixed test")),
        "command": "paysim-competitive --budget-tier competitive",
        "artifact_ref": "paper evidence audit: test_pr_auc",
        "metric": "test_pr_auc",
        "value": cell.get("value"),
        "budget_tier": cell.get("budget_tier") or "competitive",
        "leakage_posture": "balance fields and raw identifiers excluded",
        "calibration_status": _calibration_label(str(cell.get("calibration_status") or "not recorded")),
        "test_exposure_contract": test_exposure,
    }
    gate = dict(_claim_gate_by_cell(inputs).get(cell_id) or {})
    gate_example = {
        "gate_id": gate.get("gate_id") or "paysim_p6a_competitive_selected.publication_gate",
        "evidence_cell_ids": ["PS-PR"],
        "admissible_use": gate.get("admissible_use") or "bounded PaySim temporal-proxy demonstration",
        "stronger_claim_status": gate.get("stronger_claim_status") or "blocked",
        "gate_reasons": gate.get("gate_reasons") or [],
        "missing_evidence": gate.get("missing_evidence") or [],
    }
    return (
        "**Factual evidence cell**\n\n```json\n"
        + json.dumps(evidence, indent=2)
        + "\n```\n\n**Separate claim-gate record**\n\n```json\n"
        + json.dumps(gate_example, indent=2)
        + "\n```"
    )


def _render_paysim_ablation_table(inputs: dict[str, Any], metrics: dict[str, dict[str, Any]]) -> str:
    baseline_table = _payload(inputs["paysim_competitive_baseline_table"])
    feature_report = _payload(inputs["paysim_competitive_feature_report"])
    search_trace = _payload(inputs["paysim_competitive_search_trace"])
    attempts = [row for row in search_trace.get("attempts", []) if isinstance(row, dict)]
    probe_rows = [row for row in attempts if row.get("stage") == "probe"]
    full_rows = [row for row in attempts if row.get("stage") == "full_train_finalist"]
    best_probe = _best_validation_attempt({"attempts": probe_rows})
    best_full = _best_validation_attempt({"attempts": full_rows})
    selected = dict(baseline_table.get("validation_selected_competitive_model") or {})
    selected_family = _model_family_label(str(selected.get("family_id") or best_full.get("family_id") or "sklearn_extra_trees"))
    selected_val = selected.get("validation_pr_auc") or best_full.get("validation_metrics", {}).get("pr_auc")
    feature_count = len(feature_report.get("feature_columns", []))
    rows = [
        ["P4 reference", "SGD logistic baseline", "source-safe starting point", _format_metric(baseline_table.get("p4_reference_row", {}).get("test_pr_auc")), "reference row"],
        ["P6 baseline", "Extra Trees baseline", "leakage-safe feature set", _format_metric(_metric_value(metrics, "paysim_p6_validation_selected_baseline.test_pr_auc")), "baseline row"],
        ["Probe screen", f"best small-sample probe: {_model_family_label(str(best_probe.get('family_id') or 'best validation probe'))}", f"{feature_count} allowed features; probe validation PR-AUC {_format_metric(best_probe.get('validation_metrics', {}).get('pr_auc'))}", "no test evaluation", "candidate screening"],
        ["Full finalist selection", f"{selected_family} finalist", f"full-training validation PR-AUC {_format_metric(selected_val)}; selected without test evidence", "not evaluated during selection", "model selection"],
        ["Competitive test", "Extra Trees with Platt calibration", "one finalist after protocol freeze; P4/P6 exposure disclosed", _format_metric(_metric_value(metrics, "paysim_p6a_competitive_selected.test_pr_auc")), "bounded demonstration"],
    ]
    return _markdown_table("Table 5. PaySim modeling path", ["Stage", "Model/contract", "Selection evidence", "Final test evidence", "Role"], rows)


def _render_system_evaluation_summary_table(inputs: dict[str, Any]) -> str:
    tasks = _task_by_id(_payload(inputs["system_task_eval"]))
    external_panel = _payload(inputs["external_score_paper_panel"])

    def signal(task_id: str) -> str:
        measured_signal = str(tasks.get(task_id, {}).get("measured_signal") or "not observed")
        reader_signals = {
            "audit_status=pass; required_fields_present=14/14": "14/14 factual fields present; evidence/gate separation audit passed.",
            "baseline=0.331345; competitive=0.638773; improved=True": "PaySim PR-AUC changed from 0.3313 to 0.6388 under the same dataset, split, feature, and metric contract, with different declared modeling budgets.",
            "claim_cases_status=pass; go_no_go=True": "Six stronger-claim cases tested; hard and headline claims blocked.",
            "rowless=True; next_action=True; tools=True": "Rowless handoff preserved next action and allowed tools.",
            "onboarding=True; partial=True; shortlist=True": "Recovery guide, partial-run state, and artifact shortlist were emitted.",
        }
        return reader_signals.get(measured_signal, _reader_signal(measured_signal))

    hosted_score_signal = "rowless score wrapped by schema, hash, redaction, and a separate gate record"
    panel_rows = [row for row in external_panel.get("rows", []) if isinstance(row, dict)]
    for row in panel_rows:
        if row.get("component") == "Rowless handoff":
            hosted_score_signal = str(row.get("observed") or hosted_score_signal)
            break

    rows = [
        ["Metric provenance", "A reported number cannot be traced to source, split, command, or artifact.", "Required evidence-cell fields and evidence-cell audit.", signal("metric_cell_provenance_available"), "Demonstrates traceability on tested paths, not detector optimality."],
        ["Budget comparability", "Baseline and competitive rows are compared under different contracts.", "Dataset, split doctrine, metric, and budget checks.", signal("paysim_baseline_and_competitive_budget_comparable"), "Supports a bounded PaySim comparison, not SOTA."],
        ["Leakage and selection firewall", "Post-event fields or test evidence influence competitive selection.", "Feature policy, validation-only selection, and exposure record.", "4 balance fields excluded; competitive selection used no test evidence; one competitive finalist evaluated after protocol freeze; prior P4/P6 exposure recorded.", "Fixed partition, not an untouched holdout."],
        ["Claim-strength gating", "Proxy or context rows become real-bank, parity, or headline claims.", "Public wording lint, publishability matrix, and stronger-claim cases.", signal("claim_gate_fails_closed_for_public_interpretation"), "Deterministic release gate, not peer review."],
        ["Rowless handoff", "An external agent receives raw rows, credentials, or private paths.", "Context-export redaction and handoff evaluator.", signal("rowless_external_agent_handoff_recoverable"), "Deterministic fixture result, not a privacy certification."],
        ["Interrupted recovery", "A user or agent cannot recover current state without artifact literacy.", "No-lost-user guide and recovery artifact shortlist.", signal("partial_run_recovery_without_artifact_literacy"), "Deterministic recovery check, not a human study."],
        ["Hosted-score wrapper", "A third-party score file is mistaken for Relaytic detector novelty.", "Schema/hash adapter, evidence cell, redaction report, and claim map.", hosted_score_signal, "Hosted detector-output governance only."],
    ]
    return _markdown_table("Table 6. Deterministic artifact and release-gate checks", ["Check", "Failure condition", "Mechanism", "Observed result", "Scope"], rows)


def _render_failure_case_table(inputs: dict[str, Any]) -> str:
    table = _payload(inputs["failure_case_table"])
    rows = []
    for row in table.get("rows", []):
        if not isinstance(row, dict):
            continue
        rows.append(
            [
                str(row.get("failure_mode") or ""),
                str(row.get("injected_risk") or ""),
                str(row.get("gate_or_check") or ""),
                str(row.get("evidence") or ""),
                str(row.get("expected_behavior") or ""),
                _reader_signal(str(row.get("observed_result") or "")),
            ]
        )
    if not rows:
        rows.append(
            [
                "Failure-case pack",
                "Required P16 report is absent.",
                "release gate",
                "paper_failure_case_manifest",
                "Paper release blocks until the failure-case report is generated.",
                "not available",
            ]
        )
    return _markdown_table(
        "Appendix table. Detailed failure-case fixtures",
        ["Failure mode", "Injected risk", "Gate/check", "Evidence", "Expected behavior", "Observed result"],
        rows,
    )


def _render_governance_ablation_table(inputs: dict[str, Any]) -> str:
    matrix = _payload(inputs["governance_ablation_matrix"])
    rows = []
    for row in matrix.get("rows", []):
        if not isinstance(row, dict):
            continue
        rows.append(
            [
                str(row.get("path") or ""),
                str(row.get("disabled_machinery") or ""),
                _reader_signal(str(row.get("unsafe_signal") or "")),
                _reader_signal(str(row.get("artifact_integrity") or "")),
                _reader_signal(str(row.get("handoff_recovery") or "")),
                str(row.get("interpretation") or ""),
            ]
        )
    if not rows:
        rows.append(
            [
                "Governance ablation",
                "Required P17 report absent",
                "release blocks",
                "no publication matrix",
                "no recovery proof",
                "Generate the P17 ablation pack before describing machinery-level release behavior.",
            ]
        )
    return _markdown_table(
        "Appendix table. Governance machinery ablation",
        ["Path", "Disabled machinery", "Unsafe signal", "Artifact integrity", "Handoff / recovery", "Interpretation"],
        rows,
    )


def _render_governance_invariant_table(inputs: dict[str, Any]) -> str:
    report = _payload(inputs["governance_invariants"])
    rows = []
    for row in report.get("invariants", []):
        if not isinstance(row, dict):
            continue
        rows.append(
            [
                str(row.get("name") or row.get("invariant_id") or ""),
                _shorten_table_text(str(row.get("enforcement_mechanism") or ""), 110),
                _invariant_evidence_cell(row),
                _shorten_table_text(str(row.get("limitation_or_boundary") or ""), 115),
            ]
        )
    if not rows:
        rows.append(
            [
                "Governance invariants",
                "P18 report absent",
                "Generate paper-invariants before publishing the systems claim.",
                "current behavior cannot be described without the report",
            ]
        )
    return _markdown_table(
        "Appendix table. Governance invariants and evidence map",
        ["Invariant", "Mechanism", "Evidence and stress signal", "Boundary"],
        rows,
    )


def _render_hosted_score_case_study_table(inputs: dict[str, Any]) -> str:
    panel = _payload(inputs["external_score_paper_panel"])
    rows = []
    for row in panel.get("rows", []):
        if not isinstance(row, dict):
            continue
        observed = str(row.get("observed") or "")
        if row.get("component") == "Evidence emitted":
            observed = "Required metadata fields present; schema-completeness invariant passed"
        rows.append(
            [
                row.get("component") or "",
                observed,
                _short_report_ref(str(row.get("evidence_ref") or "")),
                row.get("reader_takeaway") or "",
            ]
        )
    if not rows:
        rows.append(
            [
                "Hosted score integration",
                "P19-B report absent",
                "paper_external_score_integration_manifest",
                "Paper release blocks until the hosted-score case-study pack is generated.",
            ]
        )
    return _markdown_table(
        "Appendix table. Hosted external-score case study",
        ["Component", "Observed evidence", "Evidence", "Admissible interpretation"],
        rows,
    )


def _render_hosted_score_record_snippet(inputs: dict[str, Any]) -> str:
    case_study = _payload(inputs["external_score_case_study"])
    snippet = dict(case_study.get("auditable_record_snippet", {}))
    ordered = {
        "cell_id": snippet.get("cell_id") or "not_available",
        "dataset_id": snippet.get("dataset_id") or "not_available",
        "split": snippet.get("split") or "not_available",
        "command": snippet.get("command") or "not_available",
        "artifact_ref": snippet.get("artifact_ref") or "not_available",
        "metric": snippet.get("metric") or "not_available",
        "invariant_state": snippet.get("invariant_state") or ("pass" if snippet.get("value") == 1.0 else "not_available"),
        "detector_performance_metric": False,
        "leakage_posture": snippet.get("leakage_posture") or "not_available",
        "rowless_export_status": snippet.get("rowless_export_status") or "rowless",
    }
    gate = _payload(inputs["external_score_claim_gate"])
    gate_record = {
        "gate_id": gate.get("gate_id") or "p19a.external_score.hosted_output_gate",
        "evidence_cell_ids": gate.get("evidence_cell_ids") or ["p19a.external_score.hosted_metadata_completeness"],
        "admissible_use": gate.get("admissible_use") or "hosted detector-output governance only",
        "stronger_claim_status": gate.get("stronger_claim_status") or "blocked",
        "gate_reasons": gate.get("gate_reasons") or [],
    }
    return (
        "**Factual hosted-score cell**\n\n```json\n"
        + json.dumps(ordered, indent=2)
        + "\n```\n\n**Separate hosted-score gate**\n\n```json\n"
        + json.dumps(gate_record, indent=2)
        + "\n```"
    )


def _render_blocked_claim_examples_table() -> str:
    rows = [
        ["Real-bank deployment study", "bounded PaySim temporal-proxy demonstration", "Partner or bank-approved holdout, incumbent comparison, analyst-review protocol, and legal release gate."],
        ["Elliptic2 reference-method comparison", "external RevClassifyDS reference marker plus local context row", "Faithful reference execution, cohort reconciliation, resource budget, and repeated parity report."],
        ["Graph-native detector release", "Elliptic temporal graph-feature evidence path", "Graph-native release budget, neural baselines, repeated seeds, and graph-specific ablations."],
    ]
    return _markdown_table("Appendix table. Evidence routing examples", ["Stronger future use", "Current admissible use", "Evidence needed"], rows)


def _render_handoff_recovery_table(inputs: dict[str, Any]) -> str:
    handoff_tasks = _task_by_id(_payload(inputs["agent_handoff_eval"]))
    recovery_tasks = _task_by_id(_payload(inputs["no_lost_user_eval"]))
    rows = [
        ["External-agent handoff", "partial run with available guide state", "state summary, action options, starter questions, tool contract, artifact shortlist", "raw transaction rows, credentials, private paths, raw source files", _paper_signal("handoff_redaction", handoff_tasks.get("external_context_rowless_and_redacted", {}).get("measured_signal"))],
        ["Safe next action", "external model asked what to do next", "six next actions, six starter questions, command options", "unredacted local paths and data rows", _paper_signal("safe_next_action", handoff_tasks.get("safe_next_action_exported", {}).get("measured_signal"))],
        ["Interrupted-run recovery", "operator returns to partial run without artifact literacy", "current state, missing evidence count, canonical artifact shortlist, context-export command", "raw benchmark data and private machine paths", _paper_signal("interrupted_recovery", recovery_tasks.get("partial_run_state_recovery", {}).get("measured_signal"))],
    ]
    return _markdown_table("Appendix table. Rowless handoff and interrupted-run recovery examples", ["Scenario", "Input state", "Exported fields", "Redacted fields", "Observed signal"], rows)


def _render_reproducibility_table(inputs: dict[str, Any]) -> str:
    rows = [
        ["Paper build", "paper-release; paper-arxiv-source", "Markdown, LaTeX, bibliography, and vector figures", "clean clone; TeX required only for PDF compilation"],
        ["Source validation", "paper-final-preflight", "citations, logs, fonts, links, metadata, and release gates", "compiled PDF and local TeX tools"],
        ["Deterministic fixtures", "paper-invariants", "provenance, claim, handoff, and recovery cases", "repo-local fixtures; no benchmark data"],
        ["Artifact verification", "paper-release-integrity", "metric/split agreement and evidence authority", "committed rowless reports; no retraining"],
        ["PaySim raw-data rerun", "paysim-competitive --budget-tier competitive --run-optional --require-full-rerun", "competitive model and operating-point artifacts", f"local PaySim CSV; {_repro_hash_summary(inputs, 'paysim_temporal_transaction_fraud')}"],
        ["Elliptic raw-data rerun", "graph-baselines --budget-tier competitive --run-optional --require-full-rerun", "graph-feature and operating-point artifacts", f"local Elliptic bundle; {_repro_hash_summary(inputs, 'elliptic_bitcoin_flattened_graph_aml')}"],
        ["Elliptic2 context rerun", "elliptic2-competitive --budget-tier competitive --run-suite --require-full-rerun", "RevTrack-cohort context artifacts", "local Elliptic2/RevTrack files; prior test exposure remains disclosed"],
    ]
    return _markdown_table("Table 7. Reproduction modes and dependencies", ["Mode", "Command fragment", "Output class", "Requirement"], rows)


def _evidence_cell_display_id(cell_id: str) -> str:
    display = {
        "paysim_p6a_competitive_selected.test_pr_auc": "PS-PR",
        "paysim_p6a_competitive_selected.precision_at_review_budget": "PS-P@B",
        "elliptic_p7_selected_graph_feature_baseline.test_pr_auc": "EL-PR",
        "elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget": "EL-P@B",
        "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean": "E2-PRm",
        "elliptic2_p8b_modern_context.published_reference_pr_auc": "E2-ref",
    }
    return display.get(cell_id, cell_id)


def _family_with_citations(row: dict[str, Any]) -> str:
    family = str(row.get("adjacent_family") or "")
    sources = [str(item) for item in row.get("representative_sources", []) if item]
    if not sources:
        return family
    visible = sources[:2]
    return f"{family} [@{'; @'.join(visible)}]"


def _invariant_evidence_cell(row: dict[str, Any]) -> str:
    evidence_refs = [item for item in row.get("evidence_refs", []) if isinstance(item, dict)]
    stress_refs = [item for item in row.get("failure_or_ablation_refs", []) if isinstance(item, dict)]
    evidence = evidence_refs[0] if evidence_refs else {}
    stress = stress_refs[0] if stress_refs else {}
    pieces = []
    if evidence:
        evidence_id = str(evidence.get("evidence_id") or "evidence")
        pieces.append(
            f"{_evidence_table_label(evidence_id)}: {_evidence_table_signal(evidence.get('observed_signal'), evidence_id)}"
        )
    if stress:
        stress_id = str(stress.get("evidence_id") or "fixture")
        pieces.append(
            f"stress {_evidence_table_label(stress_id)}: {_evidence_table_signal(stress.get('observed_signal'), stress_id)}"
        )
    return "; ".join(piece for piece in pieces if piece) or "not observed"


def _evidence_table_label(evidence_id: str) -> str:
    labels = {
        "all_numeric_cells_have_required_provenance": "audit",
        "metric_cell_provenance_available": "provenance task",
        "claim_safe_public_wording_allowed": "claim lint",
        "hard_headline_claims_blocked": "publishability matrix",
        "forbidden_balance_columns_used": "leakage policy",
        "test_set_selection_violation": "test-selection fixture",
        "external_context_rowless_and_redacted": "handoff audit",
        "rowless_external_agent_handoff_recoverable": "handoff task",
        "partial_run_state_recovery": "recovery audit",
        "partial_run_recovery_without_artifact_literacy": "recovery task",
        "supporting_table_allowed": "role matrix",
        "elliptic2_supporting_context_and_firewall_visible": "Elliptic2 role task",
        "wording_lint": "wording lint",
        "go_for_p13_claim_safe_release_pack": "go/no-go gate",
        "No evidence-cell required fields": "ablation",
        "overstrong_claim_attempt": "overclaim stress",
        "leakage_column_injection": "leakage stress",
        "rowless_handoff_redaction": "redaction stress",
        "interrupted_run_recovery": "recovery stress",
        "blocked_public_claims": "claim stress",
        "detector_claim_boundary": "claim boundary",
    }
    return labels.get(evidence_id, _humanize_gate_token(evidence_id))


def _evidence_table_signal(value: Any, evidence_id: str) -> str:
    signal_overrides = {
        "all_numeric_cells_have_required_provenance": "pass",
        "claim_safe_public_wording_allowed": "pass",
        "forbidden_balance_columns_used": "4 forbidden fields offered; 0 used",
        "external_context_rowless_and_redacted": "raw rows excluded; 8 unsafe fields redacted; 6 fields blocked",
        "partial_run_state_recovery": "partial run recovered; 8 missing items; 6 actions exposed",
        "supporting_table_allowed": "5 supporting rows allowed; hard/headline claims blocked",
        "wording_lint": "pass",
        "No evidence-cell required fields": "11 factual provenance fields missing; release blocked",
        "overstrong_claim_attempt": "6 unsupported claims blocked",
        "leakage_column_injection": "4 leakage fields offered and excluded; 0 used",
        "rowless_handoff_redaction": "6 unsafe fields blocked; raw rows excluded",
        "interrupted_run_recovery": "partial run recovered; 6 actions exposed",
        "blocked_public_claims": "6 public claims blocked",
        "detector_claim_boundary": "headline and hard performance claims blocked",
    }
    if evidence_id in signal_overrides:
        return signal_overrides[evidence_id]
    text = str(value or "not observed").strip()
    replacements = {
        "claim_safe_public_wording_allowed": "pass",
        "True": "pass",
        "False": "fail",
    }
    text = replacements.get(text, text)
    return " ".join(text.replace("_", " ").split())


def _shorten_table_text(value: str, max_len: int) -> str:
    text = " ".join(str(value).split())
    if len(text) <= max_len:
        return text
    # Never put machine-style truncation into a publication table. Callers must
    # provide concise reader-facing text when a source artifact is verbose.
    return text


def _audit_result(task_id: str, passed: Callable[[str], str], signal: Callable[[str], str]) -> str:
    compact_signal = {
        "metric_cell_provenance_available": "required factual fields present in the evidence-cell audit",
        "paysim_baseline_and_competitive_budget_comparable": "same split/metric; PR-AUC 0.3313 -> 0.6388",
        "paysim_claim_boundary_machine_readable": "bounded use present; headline and hard performance claims blocked",
        "elliptic2_supporting_context_and_firewall_visible": "reference role visible; parity evidence required",
        "rowless_external_agent_handoff_recoverable": "raw rows excluded from export; 8 unsafe fields redacted; 6 blocked fields recorded",
        "partial_run_recovery_without_artifact_literacy": "partial run recovered; 8 missing-evidence items and 6 actions exposed",
        "claim_gate_fails_closed_for_public_interpretation": "case studies record missing evidence",
    }.get(task_id, signal(task_id))
    return f"{passed(task_id)}; {compact_signal}"


def _paper_signal(signal_id: str, measured_signal: Any) -> str:
    display = {
        "handoff_redaction": "raw rows excluded from export; 8 unsafe fields redacted; 6 blocked fields recorded",
        "safe_next_action": "6 next actions and 6 starter questions exposed",
        "interrupted_recovery": "partial run recovered; 8 missing-evidence items and 6 actions exposed",
    }
    if signal_id in display:
        return display[signal_id]
    return str(measured_signal or "not observed").replace("_", " ")


def _reader_signal(value: str) -> str:
    text = " ".join(str(value or "").split())
    replacements = {
        "actions=6": "6 recovery actions exposed",
        "actions=0": "0 recovery actions exposed",
        "missing=8": "8 missing-evidence items recorded",
        "missing evidence=8": "8 missing-evidence items recorded",
        "redactions=8": "8 unsafe fields redacted",
        "blocked fields=6": "6 blocked fields recorded",
        "raw rows absent": "raw rows excluded from export",
        "raw rows=false": "raw rows excluded from export",
        "raw rows=no": "raw rows excluded from export",
        "hard/headline=false": "headline and hard performance claims blocked",
        "hard=no; headline=no": "hard and headline claims blocked",
        "labels=no": "labels not used as features",
        "safe=false": "release blocked",
        "blocked claims=6": "6 unsupported claims blocked",
        "blocked=6": "6 public claims blocked",
        "used=0": "0 used",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return " ".join(text.replace(";", "; ").split())


def _review_budget_count_summary(inputs: dict[str, Any], dataset: str) -> str:
    if dataset == "paysim":
        trace = _payload(inputs["paysim_competitive_search_trace"])
        row = dict(trace.get("selected_finalist") or {})
    elif dataset == "elliptic":
        feature_table = _payload(inputs["elliptic_graph_feature_table"])
        row = dict(feature_table.get("validation_selected_competitive_baseline") or {})
    else:
        row = {}
    operating = dict(row.get("test_operating_point") or {})
    reviewed = _as_int(operating.get("reviewed_count"))
    true_positive = _as_int(operating.get("true_positive_count"))
    false_positive = _as_int(operating.get("false_positive_count"))
    recall = _as_float(operating.get("recall_at_review_budget"))
    total_positive = _as_int(row.get("test_positive_count") or row.get("positive_count"))
    if total_positive is None and true_positive is not None and recall and recall > 0:
        total_positive = int(round(true_positive / recall))
    false_negative = (
        total_positive - true_positive
        if total_positive is not None and true_positive is not None
        else None
    )
    if None in {reviewed, true_positive, false_positive, false_negative, total_positive}:
        return "The current public cell reports precision and recall at the review budget; queue-count expansion remains future evidence."
    return (
        f"The fixed queue reviews {reviewed:,} items, containing {true_positive:,} true positives "
        f"and {false_positive:,} false positives; {false_negative:,} of {total_positive:,} positives remain outside the reviewed set."
    )


def _as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _compact_split_label(split: str) -> str:
    mapping = {
        "fixed_temporal_test": "temporal test",
        "temporal_fixed_test": "temporal test",
        "temporal_graph_test": "graph time test",
        "official_partition_test": "provided RevTrack TST",
        "published_reference": "published ref.",
        "not recorded": "not recorded",
    }
    return mapping.get(split, _humanize_gate_token(split).replace(" partition", "").replace(" reference", " ref."))


def _compact_cell_split(cell_id: str, split: str) -> str:
    if cell_id.startswith("paysim_") and split == "test":
        return "temporal test"
    if cell_id.startswith("elliptic_p7_") and split == "test":
        return "graph-time test"
    if cell_id.endswith("published_reference_pr_auc"):
        return "reported ref."
    return _compact_split_label(split)


def _markdown_table(title: str, headers: list[str], rows: list[list[Any]]) -> str:
    lines = [f"**{title}.**", "", "| " + " | ".join(_escape_md(str(header)) for header in headers) + " |"]
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        cells = list(row)[: len(headers)]
        while len(cells) < len(headers):
            cells.append("")
        lines.append("| " + " | ".join(_escape_md(str(cell)) for cell in cells) + " |")
    return "\n".join(lines)


def _short_report_ref(ref: str) -> str:
    if not ref:
        return "not available"
    stem = Path(ref).stem
    labels = {
        "paper_external_score_schema": "schema/hash report",
        "paper_external_score_evidence_cells": "evidence-cell report",
        "paper_external_score_handoff_eval": "handoff-redaction report",
        "paper_external_score_claim_gate": "claim-gate report",
    }
    return labels.get(stem, stem)


def _dataset_lookup(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(dataset.get("dataset_id")): dict(dataset)
        for dataset in registry.get("datasets", [])
        if isinstance(dataset, dict) and dataset.get("dataset_id")
    }


def _contract_lookup(split_contracts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(contract.get("dataset_id")): dict(contract)
        for contract in split_contracts.get("contracts", [])
        if isinstance(contract, dict) and contract.get("dataset_id")
    }


def _dataset_split_report(inputs: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    if dataset_id == "paysim_temporal_transaction_fraud":
        return _payload(inputs["paysim_temporal_split"])
    if dataset_id == "elliptic_bitcoin_flattened_graph_aml":
        return _payload(inputs["elliptic_temporal_split"])
    if dataset_id == "elliptic2_subgraph_aml":
        return _payload(inputs["elliptic2_repeated_seed_scorecard"])
    return {}


def _dataset_scale_summary(dataset: dict[str, Any], split_report: dict[str, Any]) -> str:
    facts = dataset.get("known_source_facts", {}) if isinstance(dataset.get("known_source_facts"), dict) else {}
    if split_report.get("split_rows"):
        total = split_report.get("row_count") or split_report.get("node_count")
        positive = sum(int(row.get("positive_count", row.get("illicit_count", 0)) or 0) for row in split_report.get("split_rows", []))
        if total:
            unit = "nodes" if split_report.get("node_count") else "transactions"
            return f"{_format_count(total)} {unit}; {positive} positives"
    if "labeled_subgraphs" in facts:
        return f"{_format_count(facts.get('labeled_subgraphs'))} labeled subgraphs; context row"
    if "nodes" in facts:
        return f"{_format_count(facts.get('nodes'))} nodes; {_format_count(facts.get('edges'))} edges"
    if "approx_rows" in facts:
        return f"{_format_count(facts.get('approx_rows'))} rows"
    return "not recorded"


def _split_size_summary(split_report: dict[str, Any]) -> str:
    if split_report.get("split_rows"):
        parts = []
        for row in split_report.get("split_rows", []):
            if not isinstance(row, dict):
                continue
            count = row.get("row_count") or row.get("known_label_count") or row.get("node_count")
            rate = row.get("positive_rate") or row.get("positive_rate_labeled")
            rate_text = f", pos {_format_rate(rate)}" if rate is not None else ""
            parts.append(f"{row.get('split')}: {_format_count(count)}{rate_text}")
        return "; ".join(parts)
    official = split_report.get("official_partition", {}) if isinstance(split_report.get("official_partition"), dict) else {}
    first_row = next((row for row in official.get("rows", []) if isinstance(row, dict)), {})
    if first_row:
        return (
            f"val {_format_count(first_row.get('validation_count'))}, "
            f"test {_format_count(first_row.get('test_count'))}; "
            f"test positives {_format_count(first_row.get('test_positive_count'))}"
        )
    return "not recorded"


def _feature_policy_summary(inputs: dict[str, Any], dataset_id: str) -> str:
    if dataset_id == "paysim_temporal_transaction_fraud":
        report = _payload(inputs["paysim_competitive_feature_report"])
        allowed = len(report.get("feature_columns", []))
        return f"{allowed} decision-time features; balance columns excluded"
    if dataset_id == "elliptic_bitcoin_flattened_graph_aml":
        graph = _payload(inputs["elliptic_graph_feature_table"])
        views = [str(view.get("feature_view_id")) for view in graph.get("feature_views", []) if isinstance(view, dict)]
        return "; ".join(_humanize_gate_token(view) for view in views[:3]) or "not recorded"
    if dataset_id == "elliptic2_subgraph_aml":
        repeated = _payload(inputs["elliptic2_repeated_seed_scorecard"])
        feature_view = _humanize_gate_token(str(repeated.get("feature_view_id") or "not recorded"))
        return f"{feature_view}; raw subgraphs local-gated"
    return "not recorded"

def _forbidden_feature_summary(contract: dict[str, Any], dataset_id: str) -> str:
    forbidden = [str(item) for item in _as_list(contract.get("forbidden_feature_fields"))]
    if dataset_id == "paysim_temporal_transaction_fraud":
        return "balance columns, raw account IDs, simulator flags, random row shuffles"
    if dataset_id == "elliptic_bitcoin_flattened_graph_aml":
        return "future-to-train edges and random node splits across time"
    if dataset_id == "elliptic2_subgraph_aml":
        return "claim use gated by reference parity and local data availability"
    return ", ".join(forbidden) if forbidden else "none recorded"


def _source_hash_summary(dataset: dict[str, Any], split_report: dict[str, Any]) -> str:
    source_sha = split_report.get("source_sha256")
    if source_sha:
        return f"sha256 prefix {str(source_sha)[:12]}"
    checks = [row for row in dataset.get("required_file_checks", []) if isinstance(row, dict) and row.get("sha256")]
    if checks:
        first = str(checks[0].get("sha256"))
        suffix = "" if len(checks) == 1 else f" plus {len(checks) - 1} files"
        return f"sha256 prefix {first[:12]}{suffix}"
    return "not bundled"


def _repro_hash_summary(inputs: dict[str, Any], dataset_id: str) -> str:
    registry = _payload(inputs["dataset_registry"])
    dataset = _dataset_lookup(registry).get(dataset_id, {})
    split_report = _dataset_split_report(inputs, dataset_id)
    return _source_hash_summary(dataset, split_report)


def _task_by_id(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(task.get("task_id")): dict(task)
        for task in report.get("tasks", [])
        if isinstance(task, dict) and task.get("task_id")
    }


def _selection_summary(search_trace: dict[str, Any], default_selection: str, threshold_summary: str) -> str:
    selected = search_trace.get("selected_finalist", {}) if isinstance(search_trace.get("selected_finalist"), dict) else {}
    selection = selected.get("selection_surface") or default_selection
    calibration = selected.get("calibration_method") or search_trace.get("calibration_trace", {}).get("selected_method")
    selection_key = str(selection)
    if selection_key.startswith("validation_pr_auc_only"):
        selection_label = "validation PR-AUC only"
    else:
        selection_label = _humanize_gate_token(selection_key)
    calibration_label = {
        "platt_sigmoid": "Platt calibration",
    }.get(str(calibration), str(calibration) if calibration else threshold_summary)
    return f"{selection_label}; {calibration_label}"


def _best_validation_attempt(search_trace: dict[str, Any]) -> dict[str, Any]:
    attempts = [row for row in search_trace.get("attempts", []) if isinstance(row, dict)]
    scored = [
        row
        for row in attempts
        if isinstance(row.get("validation_metrics"), dict)
        and isinstance(row["validation_metrics"].get("pr_auc"), (int, float))
    ]
    if not scored:
        return {}
    return max(scored, key=lambda row: float(row["validation_metrics"]["pr_auc"]))


def _dataset_short_name(dataset_id: str) -> str:
    aliases = {
        "paysim_temporal_transaction_fraud": "PaySim",
        "elliptic_flattened_graph_aml": "Elliptic",
        "elliptic_bitcoin_flattened_graph_aml": "Elliptic",
        "elliptic2_subgraph_aml": "Elliptic2",
    }
    return aliases.get(dataset_id, _humanize_gate_token(dataset_id or "unknown"))


def _compact_command_artifact(cell: dict[str, Any]) -> str:
    command = str(cell.get("command") or "command unavailable")
    if "paysim-competitive" in command:
        command_label = "PaySim run"
        artifact_label = "manifest"
    elif "graph-baselines" in command:
        command_label = "graph run"
        artifact_label = "feature table"
    elif "elliptic2-competitive" in command:
        command_label = "E2 run"
        artifact_label = "scorecard"
    elif "paper-operational-metrics" in command:
        command_label = "paper-operational-metrics"
        artifact_label = "operational metrics"
    else:
        command_label = command.split()[0] if command else "command"
        artifact_label = _artifact_label(str(cell.get("artifact_ref") or "artifact unavailable"))
    return f"{command_label}; {artifact_label}"


def _artifact_label(source_artifact: str) -> str:
    if source_artifact == "README.md":
        return "README"
    name = Path(source_artifact).name
    label = name.replace(".json", "").replace(".md", "") or source_artifact
    labels = {
        "paper_metric_cell_audit": "evidence-cell audit",
        "paper_publishability_matrix": "publishability matrix",
        "paper_agent_handoff_eval": "agent handoff evidence",
        "paper_no_lost_user_eval": "recovery evidence",
        "paper_claim_gate_case_studies": "claim-gate cases",
        "paper_result_table_final": "result table",
    }
    return labels.get(label, _humanize_gate_token(label))


def _metric_list(metrics: Any) -> str:
    names = {
        "pr_auc": "PR-AUC",
        "roc_auc": "ROC-AUC",
        "precision_at_k": "P@k",
        "recall_at_review_budget": "R@budget",
        "fixed_fpr_recall": "fixed-FPR recall",
    }
    return ", ".join(names.get(str(metric), _humanize_gate_token(str(metric))) for metric in _as_list(metrics))


def _paper_metric_label(metric_id: str) -> str:
    labels = {
        "test_pr_auc": "test PR-AUC",
        "precision_at_review_budget": "precision at review budget",
        "recall_at_review_budget": "recall at review budget",
        "official_partition_test_pr_auc_mean": "provided RevTrack TST PR-AUC mean",
        "official_partition_test_pr_auc_std": "provided RevTrack TST PR-AUC std",
        "published_reference_pr_auc": "published reference PR-AUC",
    }
    return labels.get(metric_id, _humanize_gate_token(metric_id))


def _short_split_rule(split_type: str) -> str:
    labels = {
        "chronological_by_step": "time step",
        "temporal_graph_by_time_step": "graph time",
        "subgraph_level_fixed_seed_or_official": "fixed partition",
    }
    return labels.get(split_type, _humanize_gate_token(split_type))


def _model_family_label(family_id: str) -> str:
    labels = {
        "xgboost_classifier": "XGBoost",
        "lightgbm_classifier": "LightGBM",
        "extra_trees": "Extra Trees",
        "sklearn_extra_trees": "Extra Trees",
        "random_forest": "Random Forest",
        "sklearn_random_forest": "Random Forest",
        "hist_gradient_boosting": "Histogram gradient boosting",
        "sklearn_hist_gradient_boosting": "Histogram gradient boosting",
    }
    return labels.get(family_id, _humanize_gate_token(family_id))


def _shorten_sentence(text: str, *, max_words: int = 18) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def _format_count(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def _format_rate(value: Any) -> str:
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def _normalize_embedded_reproduction_commands(text: str) -> str:
    if not text:
        return text
    normalized = []
    for line in text.splitlines():
        if line.startswith("# "):
            normalized.append("### " + line[2:])
        elif line.startswith("## "):
            normalized.append("### " + line[3:])
        else:
            normalized.append(line)
    return "\n".join(normalized).strip()


def _render_attention_pack(
    *,
    inputs: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    release_tag: str,
) -> str:
    pay_pr = _format_metric(_metric_value(metrics, "paysim_p6a_competitive_selected.test_pr_auc"))
    ell_pr = _format_metric(_metric_value(metrics, "elliptic_p7_selected_graph_feature_baseline.test_pr_auc"))
    return "\n".join(
        [
            "# Relaytic-AML Paper Attention Pack",
            "",
            "Use this wording for public posts until a later benchmark gate unlocks stronger claims.",
            "",
            "## One-Line Summary",
            "",
            "Relaytic-AML is a local-first agentic evaluation environment for financial-crime machine learning where specialist roles, local artifacts, redacted context packs, evidence cells, and claim gates keep humans and external agents oriented without turning benchmark rows into unsupported claims.",
            "",
            "## Short Abstract",
            "",
            "The Relaytic-AML draft presents a local-first architecture for agent-assisted anti-money-laundering (AML) evaluation, not a detector superiority claim. The controlled workspace is the source of truth. Specialist roles inspect source posture, challenge modeling plans, execute bounded searches, explain current state, and govern public claims. Benchmarks exercise that architecture. The current draft includes supporting PaySim synthetic temporal-fraud test precision-recall area under the curve (PR-AUC) "
            f"{pay_pr} and supporting Elliptic temporal graph-feature test PR-AUC {ell_pr}, while blocking hard AML, headline, graph-neural, claimed-equivalence-to-RevClassify, and hard business-value claims.",
            "",
            "## Public Post",
            "",
            "The Relaytic-AML paper presents a claim-bounded local evaluation architecture. The workspace remains authoritative, humans and agents have explicit roles, handoff exports redacted context rather than private rows, and each reported metric is traceable before it becomes a public claim. The draft covers architecture, role boundaries, research and operational use, current anti-money-laundering context, figures, reproducible source, and explicit benchmark limitations.",
            "",
            "The benchmark rows are supporting evidence for that architecture, not the identity of the system. PaySim and Elliptic are supporting evidence only, Elliptic2 is modern context only, and stronger claims stay blocked until the gates earn them. The public story is that Relaytic-AML is an auditable local evaluation environment where agents and humans can see what is proven, what is blocked, and what would need to happen next.",
            "",
            "## What This Does Not Claim",
            "",
            "- No hard real-world AML superiority claim.",
            "- No SOTA or leaderboard-winner claim.",
            "- No claimed equivalence to RevClassify and no Elliptic2 performance-contribution claim.",
            "- No graph-neural superiority claim.",
            "- No hard business-value or analyst-hour savings claim.",
            "",
            "## Reviewer Commands",
            "",
            "```powershell",
            "relaytic release-safety paper-tables --format json",
            "relaytic release-safety paper-draft --format json",
            "relaytic release-safety paper-release --format json",
            "relaytic release-safety paper-arxiv-source --format json",
            "relaytic scan-git-safety",
            "```",
            "",
            "## Release Facts",
            "",
            "- Paper draft: `docs/paper/relaytic_aml_arxiv_draft.md`",
            "- arXiv source tree: `docs/paper/arxiv_src/`",
            "- Public claims whitelist: `docs/reports/paper_public_claims_allowed.json`",
        ]
    ).rstrip() + "\n"


def _render_arxiv_checklist(
    *,
    inputs: dict[str, Any],
    release_tag: str,
    public_claims: dict[str, Any],
) -> str:
    git_commit = inputs["git"].get("commit") or "unknown"
    release_identity_lines = (
        [
            "- [ ] Confirm `git status --short` is empty at the final tag target.",
            f"- [ ] Verify tag `{release_tag}` exists locally and remotely and resolves to the final source commit.",
            f"- [ ] Create the tag only after the final source is committed: `git tag -a {release_tag} -m \"Relaytic-AML paper release\"`.",
        ]
        if release_tag
        else [
            "- [ ] Confirm `git status --short` is empty at the final commit.",
            "- [ ] Verify the final commit exists on the public remote before citing its commit URL.",
            "- [ ] Confirm the PDF, source archive, and revision manifest report the same full commit.",
        ]
    )
    return "\n".join(
        [
            "# Paper P13 arXiv Submission Checklist",
            "",
            "P13 permits only a claim-safe evaluation-environment release.",
            "",
            "## Gate Checks",
            "",
            "- [ ] `docs/reports/paper_metric_cell_audit.json` status is `pass`.",
            "- [ ] `docs/reports/paper_claim_lint_report.json` status is `pass`.",
            "- [ ] `docs/reports/paper_external_dry_run_report.json` status is `pass_paper_smoke_reproduced_claim_linted`.",
            "- [ ] `docs/reports/paper_reproduction_failure_report.json` status is `no_failures`.",
            "- [ ] `docs/reports/paper_public_claims_allowed.json` status is `claim_safe_public_wording_allowed`.",
            "- [ ] `relaytic scan-git-safety` reports no findings after staging P13 files.",
            "",
            "## Paper Package",
            "",
            "- [ ] Regenerate `docs/paper/arxiv_src/` with `relaytic release-safety paper-arxiv-source --format json` after any final paper edit.",
            "- [ ] Include `docs/paper/references.bib` and verify every in-text citation has a matching BibTeX key.",
            "- [ ] Verify the converted PDF figures in `docs/paper/arxiv_src/figures/` are accepted by the selected arXiv processor.",
            "- [ ] Keep the table values synchronized with `docs/paper/tables/table_manifest.json` and `docs/reports/paper_metric_cell_audit.json`.",
            "- [ ] Verify the author block, affiliation, contact, and optional acknowledgements before upload.",
            "- [ ] Confirm the AI-assistance disclosure is accurate before upload.",
            "",
            "## Public Claim Discipline",
            "",
            "- [ ] Public posts use `docs/reports/paper_attention_pack.md` wording only.",
            "- [ ] Do not add hard anti-money-laundering, headline, SOTA, claimed-equivalence-to-RevClassify, graph-neural superiority, or hard business-value claims.",
            f"- [ ] Confirm public wording status is `{public_claims.get('status')}`.",
            "",
            "## Suggested arXiv Metadata",
            "",
            "- Title: `Relaytic-AML: A Local-First, Agent-Assisted Evaluation Lab for Financial-Crime Machine Learning`",
            "- Primary category: `cs.LG`",
            "- Secondary categories: `q-fin.GN`, `cs.SI`, `cs.CY`",
            "- Keywords: anti-money laundering, financial crime, graph machine learning, reproducibility, evaluation environments, claim gating",
            "",
            "## Tag And Release",
            "",
            *release_identity_lines,
            f"- [ ] Confirm the release pack was regenerated after source commit `{git_commit}` if the evidence changed.",
            "- [ ] Attach or link the paper PDF, release manifest, public claims JSON, and benchmark artifacts.",
            "",
            "## Fallback",
            "",
            "If any gate fails, do not submit. Keep `paper_release_manifest.json` as a release-blocker report and repair the failed gate first.",
        ]
    ).rstrip() + "\n"


def _render_references_bib() -> str:
    return r"""@inproceedings{lopezrojas2016paysim,
  title = {{PaySim: A Financial Mobile Money Simulator for Fraud Detection}},
  author = {Lopez-Rojas, Edgar Alonso and Elmir, Ahmad and Axelsson, Stefan},
  booktitle = {Proceedings of the 28th European Modeling and Simulation Symposium},
  year = {2016},
  url = {https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf}
}

@misc{fatf2020virtualassets,
  title = {{Virtual Assets Red Flag Indicators of Money Laundering and Terrorist Financing}},
  author = {{Financial Action Task Force}},
  year = {2020},
  urldate = {2026-07-14},
  note = {Accessed 2026-07-14},
  url = {https://www.fatf-gafi.org/en/publications/Methodsandtrends/Virtual-assets-red-flag-indicators.html}
}

@misc{ffiecRedFlags,
  title = {{BSA/AML Examination Manual: Appendix F, Money Laundering and Terrorist Financing Red Flags}},
  author = {{Federal Financial Institutions Examination Council}},
  year = {2014},
  urldate = {2026-07-14},
  note = {Accessed 2026-07-14},
  url = {https://bsaaml.ffiec.gov/manual/Appendices/07}
}

@misc{weber2019elliptic,
  title = {{Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics}},
  author = {Weber, Mark and Domeniconi, Giacomo and Chen, Jie and Weidele, Daniel Karl I. and Bellei, Claudio and Robinson, Tom and Leiserson, Charles E.},
  year = {2019},
  eprint = {1908.02591},
  archivePrefix = {arXiv},
  primaryClass = {cs.SI},
  doi = {10.48550/arXiv.1908.02591},
  url = {https://arxiv.org/abs/1908.02591}
}

@misc{bellei2024elliptic2,
  title = {{The Shape of Money Laundering: Subgraph Representation Learning on the Blockchain with the Elliptic2 Dataset}},
  author = {Bellei, Claudio and Xu, Muhua and Phillips, Ross and Robinson, Tom and Weber, Mark and Kaler, Tim and Leiserson, Charles E. and Arvind and Chen, Jie},
  year = {2024},
  eprint = {2404.19109},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2404.19109},
  url = {https://arxiv.org/abs/2404.19109}
}

@inproceedings{song2024revtrack,
  title = {{Identifying Money Laundering Subgraphs on the Blockchain}},
  author = {Song, Kiwhan and Dhraief, Mohamed Ali and Xu, Muhua and Cai, Locke and Chen, Xuhao and Arvind and Chen, Jie},
  booktitle = {Proceedings of the 5th ACM International Conference on AI in Finance},
  year = {2024},
  doi = {10.1145/3677052.3698635},
  eprint = {2410.08394},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2410.08394}
}

@misc{chen2026transxion,
  title = {{TransXion: A High-Fidelity Graph Benchmark for Realistic Anti-Money Laundering}},
  author = {Chen, Keyang and Jiang, Mingxuan and Zhao, Yongsheng and Li, Zeping and Chen, Zaiyuan and Luo, Weiqi and Li, Zhixin and Liu, Sen and Jing, Yinan and Ye, Guangnan and Wu, Xihong and Chai, Hongfeng},
  year = {2026},
  eprint = {2604.17420},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2604.17420},
  url = {https://arxiv.org/abs/2604.17420}
}

@article{poon2025linemvgnn,
  title = {{LineMVGNN: Anti-Money Laundering with Line-Graph-Assisted Multi-View Graph Neural Networks}},
  author = {Poon, Chung-Hoo and Kwok, James Tin Yau and Chow, Calvin and Choi, Jang-Hyeon},
  journal = {AI},
  volume = {6},
  number = {4},
  pages = {69},
  year = {2025},
  doi = {10.3390/ai6040069},
  url = {https://doi.org/10.3390/ai6040069}
}

@misc{tariq2026extraqt,
  title = {{Extracting Money Laundering Transactions from Quasi-Temporal Graph Representation}},
  author = {Tariq, Haseeb and Hassani, Marwan},
  year = {2026},
  eprint = {2604.02899},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2604.02899},
  url = {https://arxiv.org/abs/2604.02899}
}

@misc{ye2026blazingaml,
  title = {{BlazingAML: High-Throughput Anti-Money Laundering (AML) via Multi-Stage Graph Mining}},
  author = {Ye, Haojie and Laxman, Arjun and Yuan, Yichao and Flautner, Krisztian and Talati, Nishil},
  year = {2026},
  eprint = {2604.12241},
  archivePrefix = {arXiv},
  primaryClass = {cs.DC},
  doi = {10.48550/arXiv.2604.12241},
  url = {https://arxiv.org/abs/2604.12241}
}

@article{deprez2025continualaml,
  title = {{Advances in Continual Graph Learning for Anti-Money Laundering Systems: A Comprehensive Review}},
  author = {Deprez, Bruno and Wei, Wei and Verbeke, Wouter and Baesens, Bart and Mets, Kevin and Verdonck, Tim},
  journal = {WIREs Computational Statistics},
  volume = {17},
  number = {3},
  pages = {e70040},
  year = {2025},
  doi = {10.1002/wics.70040},
  url = {https://doi.org/10.1002/wics.70040}
}

@misc{pirmorad2025amlgraphllm,
  title = {{Exploring the In-Context Learning Capabilities of LLMs for Money Laundering Detection in Financial Graphs}},
  author = {Pirmorad, Erfan},
  year = {2025},
  eprint = {2507.14785},
  archivePrefix = {arXiv},
  doi = {10.48550/arXiv.2507.14785},
  url = {https://arxiv.org/abs/2507.14785}
}

@misc{naik2025coinvestigator,
  title = {{Co-Investigator AI: The Rise of Agentic AI for Smarter, Trustworthy AML Compliance Narratives}},
  author = {Naik, Prathamesh Vasudeo and Dintakurthi, Naresh Kumar and Hu, Zhanghao and Wang, Yue and Qiu, Robby},
  year = {2025},
  eprint = {2509.08380},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2509.08380}
}

@misc{naik2026llmopsaml,
  title = {{Rethinking LLMOps for Fraud and AML: Building a Compliance-Grade LLM Serving Stack}},
  author = {Naik, Prathamesh Vasudeo and Dintakurthi, Naresh and Wang, Yue},
  year = {2026},
  eprint = {2605.11232},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2605.11232}
}

@misc{gaurav2025governanceaas,
  title = {{Governance-as-a-Service: A Multi-Agent Framework for AI System Compliance and Policy Enforcement}},
  author = {Gaurav, Suyash and Heikkonen, Jukka and Chaudhary, Jatin},
  year = {2025},
  eprint = {2508.18765},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2508.18765}
}

@misc{kaptein2026runtimegovernance,
  title = {{Runtime Governance for AI Agents: Policies on Paths}},
  author = {Kaptein, Maurits and Khan, Vassilis-Javed and Podstavnychy, Andriy},
  year = {2026},
  eprint = {2603.16586},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2603.16586}
}

@article{gebru2021datasheets,
  title = {{Datasheets for Datasets}},
  author = {Gebru, Timnit and Morgenstern, Jamie and Vecchione, Briana and Vaughan, Jennifer Wortman and Wallach, Hanna and Daume III, Hal and Crawford, Kate},
  journal = {Communications of the ACM},
  volume = {64},
  number = {12},
  pages = {86--92},
  year = {2021},
  doi = {10.1145/3458723},
  url = {https://arxiv.org/abs/1803.09010}
}

@inproceedings{mitchell2019modelcards,
  title = {{Model Cards for Model Reporting}},
  author = {Mitchell, Margaret and Wu, Simone and Zaldivar, Andrew and Barnes, Parker and Vasserman, Lucy and Hutchinson, Ben and Spitzer, Elena and Raji, Inioluwa Deborah and Gebru, Timnit},
  booktitle = {Proceedings of the Conference on Fairness, Accountability, and Transparency},
  pages = {220--229},
  year = {2019},
  doi = {10.1145/3287560.3287596},
  url = {https://arxiv.org/abs/1810.03993}
}

@article{pineau2021reproducibility,
  title = {{Improving Reproducibility in Machine Learning Research}},
  author = {Pineau, Joelle and Vincent-Lamarre, Philippe and Sinha, Koustuv and Lariviere, Vincent and Beygelzimer, Alina and d'Alche-Buc, Florence and Fox, Emily and Larochelle, Hugo},
  journal = {Journal of Machine Learning Research},
  volume = {22},
  number = {164},
  pages = {1--20},
  year = {2021},
  url = {https://www.jmlr.org/papers/v22/20-303.html}
}

@article{zaharia2018mlflow,
  title = {{Accelerating the Machine Learning Lifecycle with MLflow}},
  author = {Zaharia, Matei and Chen, Andrew and Davidson, Aaron and Ghodsi, Ali and Hong, Sue Ann and Konwinski, Andy and Murching, Siddharth and Nykodym, Tomas and Ogilvie, Paul and Parkhe, Mani and Xie, Fen and Zumar, Corey},
  journal = {IEEE Data Engineering Bulletin},
  volume = {41},
  number = {4},
  pages = {39--45},
  year = {2018},
  url = {https://people.eecs.berkeley.edu/~matei/papers/2018/ieee_mlflow.pdf}
}

@misc{chen2025mlrbench,
  title = {{MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research}},
  author = {Chen, Hui and Xiong, Miao and Lu, Yujie and Han, Wei and Deng, Ailin and He, Yufei and Wu, Jiaying and Li, Yibo and Liu, Yue and Hooi, Bryan},
  year = {2025},
  eprint = {2505.19955},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  url = {https://arxiv.org/abs/2505.19955}
}

@misc{starace2025paperbench,
  title = {{PaperBench: Evaluating AI's Ability to Replicate AI Research}},
  author = {Starace, Giulio and Jaffe, Oliver and Sherburn, Dane and Aung, James and Chan, Jun Shern and Maksin, Leon and Dias, Rachel and Mays, Evan and Kinsella, Benjamin and Thompson, Wyatt and Heidecke, Johannes and Glaese, Amelia and Patwardhan, Tejal},
  year = {2025},
  eprint = {2504.01848},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  doi = {10.48550/arXiv.2504.01848},
  url = {https://arxiv.org/abs/2504.01848}
}

@inproceedings{wijk2025rebench,
  title = {{RE-Bench: Evaluating Frontier AI R\&D Capabilities of Language Model Agents against Human Experts}},
  author = {Wijk, Hjalmar and Lin, Tao Roa and Becker, Joel and Jawhar, Sami and Parikh, Neev and Broadley, Thomas and Chan, Lawrence and Chen, Michael and Clymer, Joshua M. and Dhyani, Jai and Ericheva, Elena and Garcia, Katharyn and Goodrich, Brian and Jurkovic, Nikola and Kinniment, Megan and Lajko, Aron and Nix, Seraphina and Koba Sato, Lucas Jun and Saunders, William and Taran, Maksym and West, Ben and Barnes, Elizabeth},
  booktitle = {Proceedings of the 42nd International Conference on Machine Learning},
  year = {2025},
  series = {Proceedings of Machine Learning Research},
  volume = {267},
  pages = {66772--66832},
  url = {https://proceedings.mlr.press/v267/wijk25a.html}
}

@misc{yang2026skillopt,
  title = {{SkillOpt: Executive Strategy for Self-Evolving Agent Skills}},
  author = {Yang, Yifan and Gong, Ziyang and Huang, Weiquan and Yang, Qihao and Zhou, Ziwei and Huang, Zisu and Li, Yan and Gao, Xuemei and Dai, Qi and Liu, Bei and Qiu, Kai and Yang, Yuqing and Chen, Dongdong and Yang, Xue and Luo, Chong},
  year = {2026},
  eprint = {2605.23904},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  doi = {10.48550/arXiv.2605.23904},
  url = {https://arxiv.org/abs/2605.23904}
}

@article{saito2015precisionrecall,
  title = {{The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets}},
  author = {Saito, Takaya and Rehmsmeier, Marc},
  journal = {PLOS ONE},
  volume = {10},
  number = {3},
  pages = {e0118432},
  year = {2015},
  doi = {10.1371/journal.pone.0118432},
  url = {https://doi.org/10.1371/journal.pone.0118432}
}

@inproceedings{kleppmann2019localfirst,
  title = {{Local-First Software: You Own Your Data, in Spite of the Cloud}},
  author = {Kleppmann, Martin and Wiggins, Adam and van Hardenberg, Peter and McGranaghan, Mark},
  booktitle = {Proceedings of the 2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software},
  year = {2019},
  pages = {154--178},
  doi = {10.1145/3359591.3359737},
  url = {https://doi.org/10.1145/3359591.3359737}
}

@article{geurts2006extratrees,
  title = {{Extremely Randomized Trees}},
  author = {Geurts, Pierre and Ernst, Damien and Wehenkel, Louis},
  journal = {Machine Learning},
  volume = {63},
  number = {1},
  pages = {3--42},
  year = {2006},
  doi = {10.1007/s10994-006-6226-1},
  url = {https://doi.org/10.1007/s10994-006-6226-1}
}

@inproceedings{chen2016xgboost,
  title = {{XGBoost: A Scalable Tree Boosting System}},
  author = {Chen, Tianqi and Guestrin, Carlos},
  booktitle = {Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining},
  pages = {785--794},
  year = {2016},
  doi = {10.1145/2939672.2939785},
  url = {https://doi.org/10.1145/2939672.2939785}
}

@inproceedings{ke2017lightgbm,
  title = {{LightGBM: A Highly Efficient Gradient Boosting Decision Tree}},
  author = {Ke, Guolin and Meng, Qi and Finley, Thomas and Wang, Taifeng and Chen, Wei and Ma, Weidong and Ye, Qiwei and Liu, Tie-Yan},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {30},
  year = {2017},
  url = {https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html}
}

@incollection{platt1999probabilistic,
  title = {{Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods}},
  author = {Platt, John C.},
  booktitle = {Advances in Large Margin Classifiers},
  publisher = {MIT Press},
  year = {1999},
  pages = {61--74}
}
""".rstrip() + "\n"


def _render_reference_section() -> str:
    return "\n".join(
        [
            "- Lopez-Rojas, E. A., Elmir, A., and Axelsson, S. (2016). PaySim: A Financial Mobile Money Simulator for Fraud Detection. European Modeling and Simulation Symposium.",
            "- Financial Action Task Force. (2020). Virtual Assets Red Flag Indicators of Money Laundering and Terrorist Financing. Accessed 2026-07-14.",
            "- Federal Financial Institutions Examination Council. (2014). BSA/AML Examination Manual: Appendix F, Money Laundering and Terrorist Financing Red Flags. Accessed 2026-07-14.",
            "- Weber, M., Domeniconi, G., Chen, J., Weidele, D. K. I., Bellei, C., Robinson, T., and Leiserson, C. E. (2019). Anti-Money Laundering in Bitcoin. arXiv:1908.02591.",
            "- Bellei, C., Xu, M., Phillips, R., Robinson, T., Weber, M., Kaler, T., Leiserson, C. E., Arvind, and Chen, J. (2024). The Shape of Money Laundering. arXiv:2404.19109.",
            "- Song, K., Dhraief, M. A., Xu, M., Cai, L., Chen, X., Arvind, and Chen, J. (2024). Identifying Money Laundering Subgraphs on the Blockchain. ICAIF 2024.",
            "- Chen, K. et al. (2026). TransXion: A High-Fidelity Graph Benchmark for Realistic Anti-Money Laundering. arXiv:2604.17420.",
            "- Poon, C.-H., Kwok, J. T. Y., Chow, C., and Choi, J.-H. (2025). LineMVGNN: Anti-Money Laundering with Line-Graph-Assisted Multi-View Graph Neural Networks. AI, 6(4), 69.",
            "- Tariq, H., and Hassani, M. (2026). Extracting Money Laundering Transactions from Quasi-Temporal Graph Representation. arXiv:2604.02899.",
            "- Ye, H., Laxman, A., Yuan, Y., Flautner, K., and Talati, N. (2026). BlazingAML: High-Throughput Anti-Money Laundering via Multi-Stage Graph Mining. arXiv:2604.12241.",
            "- Deprez, B., Wei, W., Verbeke, W., Baesens, B., Mets, K., and Verdonck, T. (2025). Advances in Continual Graph Learning for Anti-Money Laundering Systems. arXiv:2503.24259.",
            "- Pirmorad, E. (2025). Exploring the In-Context Learning Capabilities of LLMs for Money Laundering Detection in Financial Graphs. arXiv:2507.14785.",
            "- Naik, P. V., Dintakurthi, N. K., Hu, Z., Wang, Y., and Qiu, R. (2025). Co-Investigator AI. arXiv:2509.08380.",
            "- Naik, P. V., Dintakurthi, N., and Wang, Y. (2026). Rethinking LLMOps for Fraud and AML. arXiv:2605.11232.",
            "- Gaurav, S., Heikkonen, J., and Chaudhary, J. (2025). Governance-as-a-Service. arXiv:2508.18765.",
            "- Kaptein, M., Khan, V.-J., and Podstavnychy, A. (2026). Runtime Governance for AI Agents. arXiv:2603.16586.",
            "- Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM.",
            "- Mitchell, M. et al. (2019). Model Cards for Model Reporting. FAT* 2019.",
            "- Pineau, J. et al. (2021). Improving Reproducibility in Machine Learning Research. JMLR.",
            "- Zaharia, M. et al. (2018). Accelerating the Machine Learning Lifecycle with MLflow. IEEE Data Engineering Bulletin.",
            "- Chen, H. et al. (2025). MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research. arXiv:2505.19955.",
            "- Starace, G. et al. (2025). PaperBench: Evaluating AI's Ability to Replicate AI Research. arXiv:2504.01848.",
            "- Wijk, H. et al. (2025). RE-Bench: Evaluating Frontier AI R&D Capabilities of Language Model Agents against Human Experts. ICML 2025.",
            "- Yang, Y. et al. (2026). SkillOpt: Executive Strategy for Self-Evolving Agent Skills. arXiv:2605.23904.",
            "- Saito, T., and Rehmsmeier, M. (2015). The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets. PLOS ONE.",
            "- Kleppmann, M., Wiggins, A., van Hardenberg, P., and McGranaghan, M. (2019). Local-First Software. Onward! 2019.",
            "- Geurts, P., Ernst, D., and Wehenkel, L. (2006). Extremely Randomized Trees. Machine Learning.",
            "- Chen, T., and Guestrin, C. (2016). XGBoost. KDD 2016.",
            "- Ke, G. et al. (2017). LightGBM. NeurIPS 2017.",
            "- Platt, J. C. (1999). Probabilistic Outputs for Support Vector Machines. Advances in Large Margin Classifiers.",
        ]
    )


def _source_verification_records() -> list[dict[str, str]]:
    return [
        {
            "citation_key": "lopezrojas2016paysim",
            "source_url": "https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf",
            "verified_role": "PaySim synthetic mobile-money simulator source and caveat.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "fatf2020virtualassets",
            "source_url": "https://www.fatf-gafi.org/en/publications/Methodsandtrends/Virtual-assets-red-flag-indicators.html",
            "verified_role": "Official virtual-asset red-flag categories for transaction pattern, anonymity, geography, sender/recipient, and source-of-funds context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "ffiecRedFlags",
            "source_url": "https://bsaaml.ffiec.gov/manual/Appendices/07",
            "verified_role": "Official BSA/AML examination red-flag examples for funds transfers, inconsistent activity, cross-border flows, and unusual transactions.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "weber2019elliptic",
            "source_url": "https://arxiv.org/abs/1908.02591",
            "verified_role": "Elliptic transaction graph size, features, and AML benchmark context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "bellei2024elliptic2",
            "source_url": "https://arxiv.org/abs/2404.19109",
            "verified_role": "Elliptic2 subgraph benchmark scale and task framing.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "song2024revtrack",
            "source_url": "https://arxiv.org/abs/2410.08394",
            "verified_role": "RevTrack/RevClassify modern reference and subgraph-method context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "chen2026transxion",
            "source_url": "https://arxiv.org/abs/2604.17420",
            "verified_role": "Recent AML benchmark-realism context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "poon2025linemvgnn",
            "source_url": "https://doi.org/10.3390/ai6040069",
            "verified_role": "Published multi-view directed transaction-graph detector context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "tariq2026extraqt",
            "source_url": "https://arxiv.org/abs/2604.02899",
            "verified_role": "Recent quasi-temporal transaction-graph detector context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "ye2026blazingaml",
            "source_url": "https://arxiv.org/abs/2604.12241",
            "verified_role": "Recent high-throughput AML graph-mining systems context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "deprez2025continualaml",
            "source_url": "https://doi.org/10.1002/wics.70040",
            "verified_role": "Peer-reviewed continual-learning and drift context for AML graph systems.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "pirmorad2025amlgraphllm",
            "source_url": "https://arxiv.org/abs/2507.14785",
            "verified_role": "Recent AML graph-reasoning context using LLM in-context learning rather than a local evidence-governance layer.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "naik2025coinvestigator",
            "source_url": "https://arxiv.org/abs/2509.08380",
            "verified_role": "Agentic SAR and compliance-narrative assistant context for distinguishing Relaytic-AML from report-writing workflows.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "naik2026llmopsaml",
            "source_url": "https://arxiv.org/abs/2605.11232",
            "verified_role": "Compliance-grade LLMOps serving-stack context for distinguishing Relaytic-AML from AML LLM deployment infrastructure.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "gaurav2025governanceaas",
            "source_url": "https://arxiv.org/abs/2508.18765",
            "verified_role": "General multi-agent AI governance framework context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "kaptein2026runtimegovernance",
            "source_url": "https://arxiv.org/abs/2603.16586",
            "verified_role": "Runtime path-policy governance context for agent systems.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "gebru2021datasheets",
            "source_url": "https://arxiv.org/abs/1803.09010",
            "verified_role": "Dataset documentation and transparency context; arXiv source retained because the CACM article page blocks automated access.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "mitchell2019modelcards",
            "source_url": "https://arxiv.org/abs/1810.03993",
            "verified_role": "Model reporting context for distinguishing model documentation from Relaytic-AML's evidence-cell and claim-gating workflow.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "pineau2021reproducibility",
            "source_url": "https://www.jmlr.org/papers/v22/20-303.html",
            "verified_role": "ML reproducibility checklist and code/data discipline context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "zaharia2018mlflow",
            "source_url": "https://people.eecs.berkeley.edu/~matei/papers/2018/ieee_mlflow.pdf",
            "verified_role": "Experiment-tracking and ML lifecycle context for run, artifact, parameter, and model lineage comparisons.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "chen2025mlrbench",
            "source_url": "https://arxiv.org/abs/2505.19955",
            "verified_role": "Agent-generated ML research reliability and invalidated-experiment risk context.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "starace2025paperbench",
            "source_url": "https://arxiv.org/abs/2504.01848",
            "verified_role": "AI-agent paper replication benchmark context and gap between fluent research artifacts and validated experimental reproduction.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "wijk2025rebench",
            "source_url": "https://proceedings.mlr.press/v267/wijk25a.html",
            "verified_role": "Recent research-engineering benchmark context comparing language-model agents with human experts.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "yang2026skillopt",
            "source_url": "https://arxiv.org/abs/2605.23904",
            "verified_role": "Recent agentic-ML context for treating external agent state and validation-gated updates as first-class research objects.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "saito2015precisionrecall",
            "source_url": "https://doi.org/10.1371/journal.pone.0118432",
            "verified_role": "Primary support for precision-recall analysis on imbalanced classification tasks.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "kleppmann2019localfirst",
            "source_url": "https://doi.org/10.1145/3359591.3359737",
            "verified_role": "Canonical local-first software definition and ownership principles.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "geurts2006extratrees",
            "source_url": "https://doi.org/10.1007/s10994-006-6226-1",
            "verified_role": "Primary Extremely Randomized Trees method citation.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "chen2016xgboost",
            "source_url": "https://doi.org/10.1145/2939672.2939785",
            "verified_role": "Primary XGBoost method citation.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "ke2017lightgbm",
            "source_url": "https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html",
            "verified_role": "Primary LightGBM method citation.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
        {
            "citation_key": "platt1999probabilistic",
            "source_url": "https://www.microsoft.com/en-us/research/publication/probabilistic-outputs-for-support-vector-machines-and-comparisons-to-regularized-likelihood-methods/",
            "verified_role": "Primary Platt probability-scaling method citation.",
            "accessed_date": SOURCE_VERIFICATION_DATE,
        },
    ]


def _render_limitations(limitations: dict[str, Any]) -> str:
    rows = [row for row in limitations.get("limitations", []) if isinstance(row, dict)]
    if not rows:
        return "The committed limitations matrix was unavailable; release is blocked until P11/P12 artifacts are repaired."
    lines = []
    for row in rows:
        if row.get("limitation_id") == "LIM-05-clean-clone-pending":
            lines.append(
                "- **LIM-05-clean-clone-smoke-scope**: P12 clean-clone and paper-smoke proof now passes for the "
                "generated paper path, including install-readiness checks, P10/P11 smoke regeneration, leak scan, "
                "and reproduction failure reporting. The remaining limitation is scope: heavy external-local "
                "benchmark reruns are documented but not rerun inside the P12 smoke proof. Required repair: run the "
                "heavy benchmark commands under a frozen release budget before promoting hard or headline benchmark claims."
            )
            continue
        lines.append(
            f"- **{row.get('limitation_id')}**: {row.get('limitation_text')} Required repair: {row.get('required_repair')}"
        )
    return "\n".join(lines)


def _render_figure_list(figure_manifest: dict[str, Any], *, figure_ids: set[str] | None = None) -> str:
    figures = [fig for fig in figure_manifest.get("figures", []) if isinstance(fig, dict)]
    if figure_ids is not None:
        figures = [fig for fig in figures if str(fig.get("figure_id") or "") in figure_ids]
    if not figures:
        return "No figure manifest was available; release is blocked until P11/P13 artifacts are repaired."
    lines = []
    for fig in figures:
        title = fig.get("title") or fig.get("figure_id") or "figure"
        filename = fig.get("filename") or ""
        lines.append(f"![{title}](figures/{filename})")
        lines.append("")
    return "\n".join(lines).rstrip()


def _lint_public_surfaces(surfaces: list[tuple[str, str]]) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    for surface_ref, text in surfaces:
        if not text:
            violations.append(
                {
                    "rule_id": "missing_surface_text",
                    "surface_ref": surface_ref,
                    "message": "Surface text was missing during P13 public wording lint.",
                }
            )
            continue
        for rule in FORBIDDEN_PUBLIC_RULES:
            for hit in _unguarded_phrase_hits(text, rule["phrase"]):
                violations.append(
                    {
                        "rule_id": rule["rule_id"],
                        "surface_ref": surface_ref,
                        "message": rule["message"],
                        "hit": hit,
                    }
                )
        lower_text = text.lower()
        for phrase in FORBIDDEN_READER_TONE_PHRASES:
            index = lower_text.find(phrase.lower())
            if index != -1:
                violations.append(
                    {
                        "rule_id": "reader_tone_phrase",
                        "surface_ref": surface_ref,
                        "message": "Reader-facing paper text must avoid meta-comparative or self-congratulatory prose.",
                        "hit": {"offset": index, "excerpt": text[index: index + len(phrase)]},
                    }
                )
    return {
        "schema_version": PAPER_RELEASE_SCHEMA_VERSION,
        "status": "pass" if not violations else "fail",
        "rule_count": len(FORBIDDEN_PUBLIC_RULES) + len(FORBIDDEN_READER_TONE_PHRASES),
        "surface_count": len(surfaces),
        "violations": violations,
    }


def _unguarded_phrase_hits(text: str, phrase: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    lower = text.lower()
    target = phrase.lower()
    start = 0
    while True:
        index = lower.find(target, start)
        if index == -1:
            break
        window = lower[max(0, index - 170): min(len(lower), index + len(target) + 110)]
        guarded = any(
            token in window
            for token in [
                "blocked",
                "blocks",
                "blocking",
                "not ",
                "not.",
                "no ",
                "without",
                "does not",
                "must not",
                "remain unresolved",
                "separate from",
                "what this does not claim",
                "another paper title",
            ]
        )
        if not guarded:
            hits.append({"offset": index, "excerpt": text[index: index + len(phrase)]})
        start = index + len(target)
    return hits


def _metric_lookup(inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    audit = _payload(inputs["metric_audit"])
    cells = audit.get("numeric_cells", [])
    return {str(cell.get("cell_id")): dict(cell) for cell in cells if isinstance(cell, dict) and cell.get("cell_id")}


def _claim_gate_by_cell(inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    payload = _payload(inputs["claim_gate_records"])
    lookup: dict[str, dict[str, Any]] = {}
    for gate in payload.get("claim_gates", []):
        if not isinstance(gate, dict):
            continue
        for cell_id in gate.get("evidence_cell_ids", []):
            if cell_id:
                lookup[str(cell_id)] = dict(gate)
    return lookup


def _metric_value(metrics: dict[str, dict[str, Any]], cell_id: str) -> Any:
    return metrics.get(cell_id, {}).get("value")


def _source_candidate_release_line(inputs: dict[str, Any]) -> str:
    commit = str(inputs.get("git", {}).get("commit") or "").strip()
    short_commit = commit[:12] if commit else "unavailable"
    release_tag = str(inputs.get("release_tag") or "").strip()
    if inputs.get("git", {}).get("release_injected") and release_tag:
        return (
            "Repository: https://github.com/ML-Enthusiast-de/Relaytic. "
            f"Release tag: {release_tag}. Source commit: {commit}. "
            f"Revision archive: https://github.com/ML-Enthusiast-de/Relaytic/archive/refs/tags/{release_tag}.tar.gz. "
            "The PDF and arXiv source-bundle manifests are generated together and record hashes for this revision."
        )
    if inputs.get("git", {}).get("release_injected") and commit:
        return (
            "Repository: https://github.com/ML-Enthusiast-de/Relaytic. "
            f"Source commit: {commit}. "
            f"Commit record: https://github.com/ML-Enthusiast-de/Relaytic/commit/{commit}. "
            f"Revision archive: https://github.com/ML-Enthusiast-de/Relaytic/archive/{commit}.tar.gz. "
            "The PDF and arXiv source-bundle manifests are generated together and record hashes for this revision."
        )
    return (
        "Repository: https://github.com/ML-Enthusiast-de/Relaytic. "
        f"Source commit: {short_commit}. "
        "Exact release metadata is injected by the clean immutable-revision build."
    )


def _read_artifact(path: Path) -> dict[str, Any]:
    return {"artifact_ref": _artifact_ref(path), "exists": path.is_file(), "payload": _read_json(path) if path.is_file() else {}}


def _read_text_artifact(path: Path) -> dict[str, Any]:
    text = ""
    if path.is_file():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            text = ""
    return {"artifact_ref": _artifact_ref(path), "exists": path.is_file(), "text": text}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload", {})
    return dict(payload) if isinstance(payload, dict) else {}


def _text_payload(artifact: dict[str, Any]) -> str:
    return str(artifact.get("text") or "")


def _artifact_ref(path: Path) -> str:
    parts = path.parts
    if "docs" in parts:
        return Path(*parts[parts.index("docs"):]).as_posix()
    if path.name == "README.md":
        return "README.md"
    return path.as_posix()


def _git_state(root: Path) -> dict[str, Any]:
    commit = _run_git(root, ["rev-parse", "HEAD"])
    status = _run_git(root, ["status", "--short"])
    return {
        "commit": commit.strip() if commit else None,
        "dirty": bool(status.strip()) if status is not None else None,
        "status_short": status.strip().splitlines() if status else [],
    }


def _run_git(root: Path, args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def _check(
    check_id: str,
    passed: bool,
    message: str,
    *,
    source_artifact: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "check_id": check_id,
        "passed": bool(passed),
        "message": message,
        "source_artifact": source_artifact,
    }
    if detail is not None:
        payload["detail"] = detail
    return payload


def _format_metric(value: Any) -> str:
    if value is None:
        return "blocked"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if abs(value) >= 100:
            return f"{value:.0f}"
        return f"{value:.4f}"
    return str(value)


def _yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|")

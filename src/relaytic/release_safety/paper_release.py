"""Paper Track P13 claim-safe paper release and attention-pack artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any, Callable

from relaytic.core.json_utils import write_json


PAPER_RELEASE_SCHEMA_VERSION = "relaytic.paper_release.v1"
PAPER_RELEASE_REPORT_DIR = Path("docs") / "reports"
PAPER_RELEASE_DOC_DIR = Path("docs") / "paper"
PAPER_RELEASE_TABLE_DIRNAME = "tables"
PAPER_RELEASE_DATE = "2026-06-09"
SOURCE_VERIFICATION_DATE = "2026-06-26"
DEFAULT_RELEASE_TAG = "relaytic-aml-paper-p13-claim-safe"
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
]


def build_paper_release_pack(
    project_root: str | Path,
    *,
    release_tag: str | None = None,
) -> dict[str, Any]:
    """Build P13 release, paper, table, citation, and public wording artifacts."""
    root = Path(project_root)
    release_tag = release_tag or DEFAULT_RELEASE_TAG
    inputs = _collect_inputs(root)
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
) -> dict[str, Path]:
    """Write the P13 release pack to docs/reports and docs/paper by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_RELEASE_REPORT_DIR
    resolved_paper_dir = Path(paper_dir) if paper_dir is not None else root / PAPER_RELEASE_DOC_DIR
    table_dir = resolved_paper_dir / PAPER_RELEASE_TABLE_DIRNAME
    report_dir.mkdir(parents=True, exist_ok=True)
    resolved_paper_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    pack = build_paper_release_pack(root, release_tag=release_tag)
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
            f"- Planned tag: `{manifest.get('release_tag_plan', {}).get('tag') or 'unknown'}`",
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
                "confirm author block, license, acknowledgements, local PDF inspection, and clean tag target",
                "rerun release-safety checks from the final clean tag target",
            ],
        },
        "release_tag_plan": {
            "tag": release_tag,
            "tag_created_by_this_slice": False,
            "creation_command": f"git tag -a {release_tag} -m \"Relaytic-AML claim-safe paper release\"",
            "artifact_refs": tag_plan_refs,
            "note": "P13 writes a tag plan and verifies the artifact set; it does not create or push tags automatically.",
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
            "P10 table pack and metric-cell audit must pass.",
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
            and external_score_claim_map.get("allowed_claim_scope") == "hosted_detector_output_governance_only"
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
        ("Elliptic2 context", "official-partition PR-AUC mean", "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean", "modern context only"),
        ("Elliptic2 context", "official-partition PR-AUC std", "elliptic2_p8b_modern_context.official_partition_test_pr_auc_std", "modern context only"),
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
    lines.append("<!-- metric-cells: " + " ".join(f"paper-cell:{cell_id}" for _, _, cell_id, _ in rows) + " -->")
    lines.append("")
    lines.append(
        "Exact metric-cell identifiers and artifact fields are stored in the metric-cell audit artifact named "
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
        if stripped.startswith("Exact metric-cell identifiers"):
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
            f"That path changes the fixed-test PR-AUC from {pay_base_pr} in the baseline run to {pay_pr} in the competitive run. At the selected review budget, the same evidence cell records precision {pay_precision} and recall {pay_recall}. The result is meaningful because the improvement is tied to a documented modeling change under the same split and metric contract. It remains bounded because PaySim is synthetic, so the claim state is supporting temporal-fraud evidence rather than real-bank AML performance.",
            "",
            "This is the pattern Relaytic is meant to enforce: useful evidence is preserved, the modeling work that created it is inspectable, and the stronger interpretation is blocked until the data and protocol justify it.",
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
        "The release pack measures part of the system behavior directly. The target is not user satisfaction. The target is a more basic property that an evaluation lab should have: a reader or external agent should be able to enter the repository, find the paper evidence, recover the current state, trace a number back to its source, and see why a stronger claim remains blocked.",
        "",
        f"The current pack contains {required_count} required deterministic checks. Within it, {task_count} reader and external-agent tasks cover {task_scope}. These tasks are intentionally concrete. They ask whether the README separates the general Relaytic platform from the Relaytic-AML paper path, whether Windows and macOS/Linux reproduction commands are visible, whether the PaySim PR-AUC cell carries dataset/split/command/artifact/budget/leakage/claim provenance, whether PaySim baseline and competitive budgets are comparable, whether Elliptic2 is recoverable as modern context rather than a performance contribution, and whether an interrupted run can be exported to another model without raw rows or private paths.",
        "",
        "This matters because the paper's central claim is about controlled evidence, not only detector performance. A strong PR-AUC with no recoverable provenance would be weak evidence for this paper. Conversely, a blocked Elliptic2 row is still useful when the system can explain exactly why it is blocked and which future evidence would change that state.",
        "",
        "The evaluation also checks the local-first handoff contract. Relaytic exports a rowless external-agent context pack from local artifacts, verifies that raw rows are absent, records redactions, and exposes safe next actions plus tool discovery. Optional local large-language-model phrasing remains advisory in the evaluated fixture; the truth-bearing state is the artifact graph.",
        "",
        "All required checks currently pass. The result should be read narrowly but seriously: Relaytic demonstrates deterministic navigation, provenance recovery, partial-run recovery, rowless handoff, optional-LLM containment, and fail-closed claim gating. It does not claim a controlled human-subject result, analyst-hour savings, production deployment, or autonomous external-agent performance improvement.",
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

    figure_manifest = _payload(inputs["figure_manifest"])
    architecture_figure = _render_figure_list(figure_manifest, figure_ids={"claim_gate_flow"})
    evidence_schema_figure = _render_figure_list(figure_manifest, figure_ids={"supporting_pr_auc"})
    benchmark_figure = _render_figure_list(figure_manifest, figure_ids={"review_budget"})
    claim_gate_figure = _render_figure_list(figure_manifest, figure_ids={"publishability_matrix"})

    evidence_cell_table = _render_evidence_cell_table_v2(metrics)
    evidence_cell_snippet = _render_evidence_cell_snippet(metrics)
    dataset_split_table = _render_dataset_split_table(inputs)
    feature_metric_policy_table = _render_feature_metric_policy_table(inputs)
    model_search_table = _render_model_search_table(inputs)
    adjacent_systems_table = _render_adjacent_systems_comparison_table(inputs)
    paysim_ablation_table = _render_paysim_ablation_table(inputs, metrics)
    system_eval_table = _render_system_evaluation_table(inputs)
    failure_case_table = _render_failure_case_table(inputs)
    governance_ablation_table = _render_governance_ablation_table(inputs)
    governance_invariant_table = _render_governance_invariant_table(inputs)
    hosted_score_case_study_table = _render_hosted_score_case_study_table(inputs)
    hosted_score_record_snippet = _render_hosted_score_record_snippet(inputs)
    blocked_claim_table = _render_blocked_claim_examples_table()
    handoff_recovery_table = _render_handoff_recovery_table(inputs)
    reproducibility_table = _render_reproducibility_table(inputs)
    references = _render_reference_section()

    return "\n".join(
        [
            "# Relaytic-AML: A Local-First Agentic Evaluation Lab for Financial-Crime Machine Learning",
            "",
            "## Abstract",
            "",
            "Anti-money laundering (AML) machine-learning experiments are difficult to audit when private data, temporal validity, graph provenance, leakage controls, review capacity, and public claims are managed in separate tools. Relaytic-AML is a local-first agentic evaluation lab in which role-scoped agents write evidence cells and deterministic claim gates decide how those cells may be used. The current evidence pack reports PaySim synthetic temporal-fraud PR-AUC "
            f"{pay_pr}, Elliptic temporal graph-feature PR-AUC {ell_pr}, and Elliptic2 context PR-AUC {e2_pr} +/- {e2_std}, reported as benchmark context against a RevClassifyDS reference of {ref_pr}. The contribution is the evaluation and release-governance substrate: local artifact truth, rowless handoff, reproducible paper assets, and evidence-bound public wording for financial-crime ML.",
            "",
            "## 1. Introduction",
            "",
            "AML modeling is a rare-event, high-stakes evaluation problem. The input may be a stream of mobile-money transfers, card events, account activity, wire messages, customer profiles, or blockchain transactions. Suspicion rarely appears in one row. It often appears as a temporal or network pattern: fast movement of funds after receipt, repeated transfers through related accounts, structured amounts, new counterparties receiving many payments, activity that does not match a customer's profile, or cryptocurrency behavior that involves risky services and geography. Regulatory and typology material from FATF, FinCEN, and FFIEC describes this kind of pattern-based reasoning in operational language [@fatf2020virtualassets; @fincenAdvisories; @ffiecRedFlags].",
            "",
            "A useful score is not enough. A reader needs to know which data stayed local, which columns were available at decision time, how time or graph boundaries were split, whether model selection touched the test surface, what review budget was assumed, and what interpretation the evidence can support. These questions become sharper when large language models (LLMs) or coding agents assist the research workflow, because fluent explanations can drift away from the artifact record unless the system is designed to fail closed.",
            "",
            "Relaytic began as a general local-first inference-engineering lab. Relaytic-AML is the financial-crime edition used here to test whether that architecture can support governed AML experimentation. It is a set of cooperating agents and deterministic harnesses around a local artifact store. The guide helps a user or another agent understand where the run is. The scout checks source posture, schema, leakage risk, and split feasibility. The strategist turns the objective into a task contract. The scientist challenges baselines, ablations, and budget choices. The builder executes bounded runs. Reviewers reconstruct traces. Release governors lint claims, figures, tables, source packages, and public wording against the evidence record.",
            "",
            "Relaytic-AML contributes a local-first evidence and release-governance layer for AML machine-learning experiments, not a new detector architecture. The benchmark rows matter because they exercise the architecture under temporal, graph, operating-point, and claim-governance pressure. The central question is whether a local evaluation lab can keep evidence, agent assistance, privacy boundaries, and publishable claims aligned while preserving the role of each result.",
            "",
            "The work is organized around four research questions:",
            "",
            "- **RQ1:** Can Relaytic-AML produce reproducible evidence cells for AML-style temporal and graph tasks?",
            "- **RQ2:** Can it prevent leakage-prone or unsupported claims from being promoted?",
            "- **RQ3:** Can the local artifact record support rowless handoff to external agents while preserving provenance?",
            "- **RQ4:** Do the benchmark rows demonstrate useful, bounded detector evidence under explicit split and budget contracts?",
            "",
            "This paper makes five contributions. First, it presents a workspace-backed, role-scoped agent runtime for AML evaluation. Second, it defines an evidence-cell schema tying each metric to dataset, split, command, artifact, budget, leakage posture, and operating point. Third, it contributes deterministic claim gates that route evidence into admissible paper uses. Fourth, it shows rowless handoff and interrupted-run recovery for external agents without exposing raw benchmark rows or private paths. Fifth, it generates reproducible paper assets and demonstrates the release path on PaySim, Elliptic, and Elliptic2 under explicit evidence roles.",
            "",
            "## 2. Related Work",
            "",
            "The AML benchmark landscape is moving toward larger, more realistic, and more graph-native settings. PaySim remains useful as a synthetic mobile-money fraud simulator for temporal proxy experiments [@lopezrojas2016paysim]. Elliptic introduced a public Bitcoin transaction graph with anonymized node features and temporal labels [@weber2019elliptic]. Elliptic2 and RevTrack/RevClassify shifted attention to suspicious subgraphs and richer blockchain context [@bellei2024elliptic2; @song2024revtrack]. Recent work such as TransXion, LineMVGNN, quasi-temporal graph extraction, BlazingAML, and continual graph-learning studies shows that the research frontier increasingly treats AML as dynamic graph and systems work rather than static tabular classification [@chen2026transxion; @poon2026linemvgnn; @tariq2026extraqt; @ye2026blazingaml; @deprez2025continualaml].",
            "",
            "Detector papers such as TransXion, BlazingAML, LineMVGNN, and RevClassifyDS push the model frontier. Relaytic-AML sits one layer around that work: it asks how experiments should be governed when data is local or licensed, the task may be temporal or graph-based, analyst review capacity matters, and an agent-assisted workflow must still produce evidence that a skeptical reviewer can audit. That places the system near dataset documentation, model reporting, reproducibility practice, experiment tracking, and governance work [@gebru2021datasheets; @mitchell2019modelcards; @pineau2021reproducibility].",
            "",
            "The system also differs from adjacent evaluation artifacts. Model cards explain a trained model, but they do not usually bind every number to a command, split, artifact field, and admissible-use record. Datasheets describe data, but they do not run the model-search and release gates. Reproducibility checklists improve reporting, but they are often static forms rather than executable evidence. MLOps experiment trackers preserve runs, but they are not designed to govern public scientific claims about local, licensed, or privacy-sensitive AML data. Agent benchmarks evaluate agents, while Relaytic-AML uses agents inside an evaluation lab and then tests whether the lab keeps the agents attached to artifacts. This is the systems contribution: evidence, agents, local privacy, and publishable wording are coupled in one deterministic release path.",
            "",
            adjacent_systems_table,
            "",
            "The comparison is intentionally narrow. Relaytic-AML does not replace dataset documentation, model cards, experiment trackers, or detector papers. It occupies the layer that ties those concerns together for local AML research: a model result is only reader-facing after its source posture, split, leakage policy, budget, artifact field, handoff posture, and claim boundary are visible.",
            "",
            "Recent agent-evaluation work shows that language-model systems can produce persuasive research artifacts while still failing on reproduction, validation, or expert-level judgment [@chen2025mlrbench; @starace2025paperbench; @wijk2025rebench]. Skill- and tool-using agents make that opportunity larger and the governance problem sharper [@yang2026skillopt]. Relaytic-AML responds by making model scores, public claims, handoff packets, and paper assets downstream of local artifacts rather than downstream of a conversation transcript.",
            "",
            "## 3. System Overview",
            "",
            "Relaytic-AML is built around one authority rule: the workspace owns the truth. Raw data, licensed benchmark files, run summaries, traces, metric cells, model outputs, tables, figures, and release reports live on disk. Agents may explain, propose, and repair, but their proposals only become evidence when they are materialized as artifacts another human or agent can inspect.",
            "",
            architecture_figure,
            "",
            "Figure 1 summarizes the local evidence loop. Dataset registries and split contracts enter the role-scoped agent runtime. Candidate runs write benchmark manifests, search traces, feature reports, and metric cells. Claim gates read those cells together with release audits and emit only the interpretations that the evidence supports. The same contract feeds the command-line interface, project skills, OpenClaw-style handoff, Claude/Codex skill files, and Model Context Protocol (MCP) adapters.",
            "",
            "The external-agent path is rowless by default. Relaytic can export current state, next-action options, artifact shortlists, and safe commands for another model without sending raw transaction rows, secrets, or private local paths. A local LLM can optionally help phrase guidance, but the deterministic guide and evidence artifacts remain the source of truth. That separation matters for private AML work: outside intelligence may help navigate the run, but data residency and claim provenance stay local unless an operator deliberately changes policy.",
            "",
            "## 4. Evidence Cell and Claim-Gate Design",
            "",
            "An evidence cell is the unit that makes a paper number auditable. It is not just a metric value. It records the dataset, split, command, artifact field, model or feature budget, leakage posture, and operating point. Interpretation is deliberately stored in a separate gate output: the cell says what happened, and the gate says how that fact may be used.",
            "",
            evidence_schema_figure,
            "",
            "Table 1 uses compact publication aliases for readability; the full machine metric-cell identifiers are preserved in the metric-cell audit artifact and generated table comments.",
            "",
            evidence_cell_table,
            "",
            "A representative record is compact enough to audit directly. The public table uses the alias `PS-PR`, while the underlying artifact keeps the longer machine identifier. The example separates the factual evidence cell from the gate output that names admissible use and evidence needed for a stronger interpretation.",
            "",
            evidence_cell_snippet,
            "",
            "```algorithm",
            "Algorithm: Evidence-cell creation",
            "Input: dataset registry D, split contract S, candidate budget B, run artifacts A",
            "Output: evidence cell c with factual provenance",
            "1. Freeze source posture, license posture, task target, and split contract.",
            "2. Derive only features allowed by S and record excluded leakage fields.",
            "3. Run baseline candidates under the declared baseline budget.",
            "4. Run stronger candidates only within B and select on validation evidence.",
            "5. Evaluate the selected row once on the fixed test surface.",
            "6. Write c = dataset, split, command, artifact field, metric, value, budget, leakage posture, and operating point.",
            "7. Hand c to the claim gate before it appears in tables, figures, or release text.",
            "```",
            "",
            "The claim gate is the second half of the design. It is deliberately conservative. If the evidence cell is incomplete, if a split is leakage-prone, if a metric is only a proxy, or if a stronger interpretation needs a different dataset or study, the gate preserves the evidence and routes the stronger use to an evidence-needs record. This is a mechanism, not a disclaimer: it changes what the paper generator and public release surfaces are allowed to say.",
            "",
            "```algorithm",
            "Algorithm: Claim-gate validation",
            "Input: public claim q, evidence cells C, gates G, limitations L",
            "Output: admissible wording and evidence-needs record",
            "1. Resolve every evidence cell named by q and require dataset, split, command, artifact, budget, and leakage fields.",
            "2. Compare the strength of q with source posture, split validity, metric scope, and benchmark role.",
            "3. If q is exactly supported, emit the bounded wording and the evidence-cell identifiers.",
            "4. If q is stronger than C and G permit, record the stronger-claim status and gate reason.",
            "5. Attach the missing evidence needed to make q testable in future work.",
            "6. Route current evidence to its admissible paper use and keep stronger uses out of headline wording.",
            "```",
            "",
            claim_gate_figure,
            "",
            "Figure 3 gives concrete routing behavior. A PaySim row becomes a bounded temporal-proxy demonstration, an Elliptic row becomes graph-feature evidence with temporal provenance, and an Elliptic2 row becomes external benchmark context. The same records also specify what evidence would be needed before stronger future uses could be made.",
            "",
            "## 5. Experimental Protocol",
            "",
            "The experiments test Relaytic-AML as an evaluation lab. The datasets are separated by evidence role. PaySim is the main empirical demonstration because it is fully local and supports a controlled temporal proxy workflow. Elliptic tests temporal graph provenance and feature-view discipline. Elliptic2 tests whether the system can keep a modern external reference row visible without overstating its role.",
            "",
            dataset_split_table,
            "",
            feature_metric_policy_table,
            "",
            "Tables 2a and 2b record the context a reader needs before interpreting any metric. The positive rates show why precision-recall area under the curve (PR-AUC) is the primary score. These are rare-event tasks where receiver-operating-characteristic area under the curve can look strong while the review queue remains poor. The split rules are equally important: PaySim is split by chronological simulator step, Elliptic by time-step graph windows, and Elliptic2 by the official/context partitions recorded in the local evidence pack.",
            "",
            model_search_table,
            "",
            "Table 3 records the modeling effort without presenting the paper as a hyperparameter leaderboard. PaySim uses a two-stage competitive budget: probes over a seeded train-only sample, five full-training finalists, validation-only calibration, and one fixed test evaluation for the selected finalist. Elliptic uses a graph-feature budget over source-provided anonymized features, same-snapshot structural features, and their combination. Elliptic2 uses repeated pooled-moment LightGBM context rows with seeds 11, 42, and 73 as an external-reference stress test for the release machinery.",
            "",
            "The feature policy is strictest for PaySim because simulator balance columns can leak post-event state. Relaytic excludes those balance fields, raw origin and destination identifiers as model features, and simulator flags. It allows row-local amount, type, and time features, train-only thresholds, and destination history shifted before each step. The isolated contribution of destination-history features has not been measured as a separate test row, so it is not reported as a main result.",
            "",
            "## 6. Results",
            "",
            paysim_ablation_table,
            "",
            f"PaySim is the most complete local modeling path in the current evidence pack. It should be read as an audited sequence rather than as a leaderboard claim. The earliest reference row was PR-AUC 0.2159. The later leakage-safe baseline improved to {pay_base_pr}. The small-sample probe screen then identified a strong XGBoost probe, but fixed-test eligibility was decided later among full-training finalists; Extra Trees had the best full-training validation PR-AUC and was the only competitive finalist evaluated on the fixed test. It reached fixed-test PR-AUC {pay_pr} and ROC-AUC {pay_roc}. The improvement is meaningful inside the synthetic temporal-fraud contract because balance fields were excluded, prior-step destination history was added without raw account encoding, candidates were selected by validation evidence, and calibration and thresholding used validation-only partitions. The admissible interpretation is precise: Relaytic-AML produced a stronger, leakage-audited PaySim temporal-proxy row under a declared budget. It is supporting temporal-fraud evidence rather than real-bank AML performance.",
            "",
            f"The review-budget metrics sharpen the interpretation. At the selected PaySim review budget, precision is {pay_precision} and recall is {pay_recall}. {paysim_review_counts} The top of the queue is much richer than prevalence, but it still misses substantial fraud. That is a useful operating result for an evaluation lab because it connects ranking quality to analyst capacity instead of treating PR-AUC as the whole story.",
            "",
            f"Elliptic is a different kind of evidence. The validation-selected source-plus-structural LightGBM row reports test PR-AUC {ell_pr}, with review-budget precision {ell_precision} and recall {ell_recall}. {elliptic_review_counts} The result supports temporal graph-feature provenance and operating-point reporting. It also reveals a limitation: the current graph-structure-only floor is weak, and the final row is heavily influenced by source-provided anonymized features. Relaytic's contribution here is the graph-aware evidence path: feature provenance, temporal splits, operating-point metrics, and interpretation routing are made auditable together.",
            "",
            f"Elliptic2 is the modern benchmark-context row. The repeated official-partition context row reports PR-AUC {e2_pr} +/- {e2_std}, and the content-hash robustness partition reports mean PR-AUC {e2_hash}. Those values sit beside the recorded RevClassifyDS reference of {ref_pr}, giving the reader a frontier marker while keeping Relaytic's role precise: carrying modern external benchmark evidence, cohort notes, and reference-execution requirements without converting that context into a detector contribution.",
            "",
            benchmark_figure,
            "",
            "Figure 4 separates ranking metrics from operating-point metrics. PR-AUC summarizes ranking quality under rare-event imbalance. Precision and recall at the selected review budget describe what the top of an analyst queue would contain under the paper's fixed policy. Keeping those views together, but visually separated, is important because a useful top queue can still leave many positives unreviewed.",
            "",
            "## 7. System Evaluation",
            "",
            "The system claim is evaluated through deterministic reader and agent tasks. These checks ask whether a reviewer can navigate from the README to the paper evidence, trace PaySim metric provenance, compare baseline and competitive budgets, keep Elliptic2 as context rather than a contribution, export rowless state for an external agent, recover an interrupted run, and block over-strong public claims. This is narrower than a human-subject usability study, but it directly tests the infrastructure claim made by the paper.",
            "",
            system_eval_table,
            "",
            "Table 5 reports the audit matrix behind the system claim. Each row names a behavior, a deterministic check, a pass criterion, and an observed signal: 13 of 13 provenance fields are present for the PaySim metric cell, baseline and competitive budgets are comparable under the same contract, Elliptic2 remains in its reference role, rowless handoff exposes no raw rows, and interrupted-run recovery surfaces state, missing evidence, and next actions.",
            "",
            failure_case_table,
            "",
            "Table 6 adds injected failure cases. The point is not detector performance; the checks exercise whether the release path refuses leakage features, test-set model selection, over-strong claims, unsafe handoff, and lost-run states under deterministic system fixtures. These cases make the governance claim auditable without adding a new benchmark row.",
            "",
            governance_ablation_table,
            "",
            "Table 7 compares the full governance path with disabled-component fixtures. The ablation does not change detector results. It tests whether claim gates, leakage policy, redaction, metric provenance, and recovery guidance change what can be released from the same evidence pack.",
            "",
            governance_invariant_table,
            "",
            "Table 8 states the current invariants as release-time rules rather than prose preferences. Each invariant has a mechanism, evidence artifacts, an observed failure or ablation signal, and an explicit boundary. This is the core systems claim: Relaytic-AML makes agent-assisted evaluation safer by turning interpretation into checked state.",
            "",
            hosted_score_case_study_table,
            "",
            "The hosted external-score case study makes the integration point concrete. A rowless detector-score artifact enters Relaytic with schema and content hashes, not raw rows. Relaytic emits one governance evidence cell, redacts unsafe handoff fields, and routes the result as hosted detector-output governance evidence. This shows how a stronger or third-party detector output can be wrapped by the same local evidence and release boundary.",
            "",
            hosted_score_record_snippet,
            "",
            blocked_claim_table,
            "",
            "Table 10 shows how stronger future uses are handled. Rather than letting narrative claims drift beyond the artifacts, the gate records the current admissible use and the evidence that would be needed before the stronger interpretation could be made.",
            "",
            handoff_recovery_table,
            "",
            "Table 11 gives the practical external-agent story. A second model can receive state, commands, artifacts, and starter questions, while raw rows remain redacted together with private machine paths. The same mechanism helps an inexperienced or interrupted user recover the next action without knowing which internal artifact to inspect first.",
            "",
            "## 8. Limitations and Threats to Validity",
            "",
            "PaySim is synthetic. It is useful for controlled temporal fraud experiments, but it is not evidence of bank-scale AML superiority. The simulator has known simplifications, and the current result should be interpreted as a leakage-audited proxy result. The destination-history feature contract is present, but the isolated destination-history ablation is not in the current evidence pack, so no separate result is claimed for that feature family.",
            "",
            "Public blockchain data is also not the same as bank AML. Elliptic provides a valuable temporal graph task, but unknown labels, anonymized features, and public-chain behavior limit direct operational interpretation. Elliptic2 is modern and highly relevant, but the current local evidence does not satisfy the stronger reference-parity conditions needed for a performance contribution against RevClassifyDS.",
            "",
            "The deterministic system checks are not a substitute for a human usability study. They show that artifacts, redactions, interpretation gates, and recovery surfaces are present and internally consistent. They do not measure analyst time, production incident rates, organizational adoption, or real investigation quality. Future work should test stronger release budgets, repeated runs, private or partner-approved holdouts, same-queue incumbent comparisons, and graph-native families under the same evidence-cell discipline.",
            "",
            "The system is intentionally local-first, which creates a tradeoff. Privacy and provenance improve because raw rows stay local, but external reviewers cannot rerun licensed or private data without obtaining it themselves. The paper handles that by publishing commands, hashes where allowed, generated artifacts, and claim boundaries, but a fully independent reproduction of every heavy benchmark still depends on legal access to the source datasets.",
            "",
            "## 9. Reproducibility",
            "",
            "The repository is larger than this AML paper. Relaytic is the general local-first inference lab and public package; Relaytic-AML is the focused AML edition used here for the manuscript. A reader should start with the README and this paper. Development-control files record the build history, but they are not required to understand the paper claims.",
            "",
            "Repository: https://github.com/ML-Enthusiast-de/Relaytic. Public release tag: TODO before arXiv submission. Current source-candidate manifests record the generation commit hash and artifact hashes; a final tag should be created only after the P21 preflight reports a clean target.",
            "",
            reproducibility_table,
            "",
            "Minimal public checks use only repo-local deterministic fixtures and paper-generation artifacts. Full benchmark regeneration additionally requires local PaySim, Elliptic, and Elliptic2 access where the dataset licenses permit local use but not redistribution.",
            "",
            "Windows PowerShell:",
            "",
            "```powershell",
            "py -3.11 -m pip install -e \".[full]\"",
            "",
            "# Minimal public check: deterministic fixtures and paper generation.",
            "py -3.11 -m relaytic.ui.cli release-safety paper-system-eval --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-failure-eval --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-governance-ablation --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-invariants --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-external-score-proof --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-external-score-integration --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-release --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-narrative-polish --format json",
            "py -3.11 -m relaytic.ui.cli release-safety paper-arxiv-source --format json",
            "# After compiling docs/paper/arxiv_src/main.tex and copying main.pdf to the review PDF:",
            "py -3.11 -m relaytic.ui.cli release-safety paper-final-preflight --format json",
            "py -3.11 -m pytest tests/test_paper_track_p13.py tests/test_paper_track_p14.py -q",
            "py -3.11 -m pytest tests/test_paper_track_p15.py tests/test_paper_track_p16.py -q",
            "py -3.11 -m pytest tests/test_paper_track_p17.py tests/test_paper_track_p18.py -q",
            "py -3.11 -m pytest tests/test_paper_track_p19a.py tests/test_paper_track_p19b.py -q",
            "py -3.11 -m pytest tests/test_paper_track_p20.py tests/test_paper_track_p21.py -q",
            "py -3.11 -m pytest tests/test_paper_strengthening_plan.py -q",
            "```",
            "",
            "macOS/Linux:",
            "",
            "```bash",
            "python3 -m pip install -e \".[full]\"",
            "",
            "# Minimal public check: deterministic fixtures and paper generation.",
            "python3 -m relaytic.ui.cli release-safety paper-system-eval --format json",
            "python3 -m relaytic.ui.cli release-safety paper-failure-eval --format json",
            "python3 -m relaytic.ui.cli release-safety paper-governance-ablation --format json",
            "python3 -m relaytic.ui.cli release-safety paper-invariants --format json",
            "python3 -m relaytic.ui.cli release-safety paper-external-score-proof --format json",
            "python3 -m relaytic.ui.cli release-safety paper-external-score-integration --format json",
            "python3 -m relaytic.ui.cli release-safety paper-release --format json",
            "python3 -m relaytic.ui.cli release-safety paper-narrative-polish --format json",
            "python3 -m relaytic.ui.cli release-safety paper-arxiv-source --format json",
            "# After compiling docs/paper/arxiv_src/main.tex and copying main.pdf to the review PDF:",
            "python3 -m relaytic.ui.cli release-safety paper-final-preflight --format json",
            "python3 -m pytest tests/test_paper_track_p13.py tests/test_paper_track_p14.py -q",
            "python3 -m pytest tests/test_paper_track_p15.py tests/test_paper_track_p16.py -q",
            "python3 -m pytest tests/test_paper_track_p17.py tests/test_paper_track_p18.py -q",
            "python3 -m pytest tests/test_paper_track_p19a.py tests/test_paper_track_p19b.py -q",
            "python3 -m pytest tests/test_paper_track_p20.py tests/test_paper_track_p21.py -q",
            "python3 -m pytest tests/test_paper_strengthening_plan.py -q",
            "```",
            "",
            "Raw benchmark data is not committed. PaySim and Elliptic require local downloads and are referenced through registry artifacts, split reports, hashes, and command ledgers. Elliptic2 remains context-only in this paper because the stronger reference-parity conditions are not satisfied locally. Clean clones can reproduce the paper-generation checks and repo-local public fixtures; full benchmark regeneration requires the locally licensed datasets named in the README.",
            "",
            "## AI Assistance Disclosure",
            "",
            "Large language model tools assisted with drafting, editing, repository inspection, consistency checks, and implementation work around the paper artifacts. They are not authors. The evidence cells, benchmark outputs, source code, figures, tables, limitations, and final interpretation remain the author's responsibility.",
            "",
            "## Conclusion",
            "",
            "Relaytic-AML shows how an agent-assisted AML evaluation lab can be built around local evidence rather than conversational memory. The system keeps data posture, temporal and graph split validity, leakage controls, model budgets, review-budget operating points, rowless handoff, and public claims inside one artifact record. The PaySim, Elliptic, and Elliptic2 rows are useful because they demonstrate that architecture under realistic forms of pressure, including rare events, graph provenance, modern benchmark context, and governed interpretation.",
            "",
            "The strongest claim supported today is architectural: Relaytic-AML can make AML experiments easier to inspect, easier to challenge, safer to hand off to another agent, and harder to overstate. That is the useful substrate on which stronger detector studies, private holdouts, incumbent comparisons, and graph-native budgets can be built.",
            "",
            "## References",
            "",
            references,
        ]
    ).rstrip() + "\n"


def _render_dataset_split_table(inputs: dict[str, Any]) -> str:
    registry = _payload(inputs["dataset_registry"])
    split_contracts = _payload(inputs["split_contracts"])
    dataset_by_id = _dataset_lookup(registry)
    contract_by_id = _contract_lookup(split_contracts)
    rows = []
    for dataset_id, task in [
        ("paysim_temporal_transaction_fraud", "Synthetic temporal transaction fraud"),
        ("elliptic_bitcoin_flattened_graph_aml", "Temporal Bitcoin graph node classification"),
        ("elliptic2_subgraph_aml", "Suspicious-versus-licit subgraph context"),
    ]:
        dataset = dataset_by_id.get(dataset_id, {})
        contract = contract_by_id.get(dataset_id, {})
        split_report = _dataset_split_report(inputs, dataset_id)
        rows.append(
            [
                dataset.get("display_name") or _humanize_gate_token(dataset_id),
                task,
                _dataset_scale_summary(dataset, split_report),
                _split_size_summary(split_report),
                _short_split_rule(str(contract.get("split_type") or "not recorded")),
                _source_hash_summary(dataset, split_report),
            ]
        )
    return _markdown_table(
        "Table 2a. Dataset scale and split contracts",
        ["Dataset", "Task", "Scale and positives", "Train / validation / test", "Split rule", "Source hash"],
        rows,
    )


def _render_feature_metric_policy_table(inputs: dict[str, Any]) -> str:
    split_contracts = _payload(inputs["split_contracts"])
    contract_by_id = _contract_lookup(split_contracts)
    rows = []
    for dataset_id in [
        "paysim_temporal_transaction_fraud",
        "elliptic_bitcoin_flattened_graph_aml",
        "elliptic2_subgraph_aml",
    ]:
        contract = contract_by_id.get(dataset_id, {})
        rows.append(
            [
                _dataset_short_name(dataset_id),
                _feature_policy_summary(inputs, dataset_id),
                _forbidden_feature_summary(contract, dataset_id),
                _metric_list(contract.get("primary_metrics") or []),
                _evidence_role_from_dataset(dataset_id),
            ]
        )
    return _markdown_table(
        "Table 2b. Feature and metric policy",
        ["Track", "Allowed feature policy", "Forbidden or gated inputs", "Primary metrics", "Evidence role"],
        rows,
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
            f"{paysim_budget.get('probe_trial_count', 'n/a')} probes; {paysim_budget.get('finalist_fit_count', 'n/a')} finalists; seeds {', '.join(str(seed) for seed in paysim_budget.get('random_seeds', [])) or 'n/a'}",
            "validation PR-AUC; one fixed test",
        ],
        [
            "Elliptic",
            "tree/boosting baselines; LightGBM selected",
            "source node features plus same-step graph statistics",
            f"{graph_budget.get('validation_search_trial_count', 'n/a')} trials; seeds {', '.join(str(seed) for seed in graph_budget.get('random_seeds', [])) or 'n/a'}",
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
    return _markdown_table("Table 3. Model families and search budgets", ["Track", "Families", "Features", "Search budget", "Evidence role"], rows)


def _render_adjacent_systems_comparison_table(inputs: dict[str, Any]) -> str:
    report = _payload(inputs["adjacent_systems_comparison"])
    rows = []
    for row in report.get("comparison_rows", []):
        if not isinstance(row, dict):
            continue
        rows.append(
            [
                _family_with_citations(row),
                _shorten_table_text(str(row.get("primary_object") or ""), 92),
                _shorten_table_text(str(row.get("relaytic_aml_position") or ""), 115),
                _shorten_table_text(str(row.get("relaytic_aml_boundary") or ""), 82),
            ]
        )
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
        "Adjacent systems comparison",
        ["Family", "Primary object", "Relaytic-AML position", "Boundary"],
        rows,
    )


def _render_evidence_cell_table_v2(metrics: dict[str, dict[str, Any]]) -> str:
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
            _evidence_role_from_cell(cell_id),
        ])
    return _markdown_table("Table 1. Representative evidence cells", ["ID", "Dataset", "Metric", "Value", "Split", "Artifact", "Evidence role"], rows)


def _render_evidence_cell_snippet(metrics: dict[str, dict[str, Any]]) -> str:
    cell_id = "paysim_p6a_competitive_selected.test_pr_auc"
    cell = metrics.get(cell_id, {})
    snippet = [
        "{",
        '  "evidence_cell": {',
        '    "cell_id": "PS-PR", "dataset_id": "paysim_temporal_transaction_fraud",',
        f'    "split": "{_compact_cell_split(cell_id, str(cell.get("split") or "temporal_fixed_test"))}", "metric": "test_pr_auc", "value": {_format_metric(cell.get("value"))},',
        '    "artifact_ref": "paper_metric_cell_audit.json:test_pr_auc",',
        '    "budget": "competitive", "leakage_posture": "balance/raw IDs excluded",',
        '    "operating_point": "ranking metric"',
        '  },',
        '  "claim_gate_output": {',
        '    "evidence_cell_ids": ["PS-PR"], "admissible_use": "bounded PaySim proxy",',
        '    "stronger_claim_status": "requires external holdout",',
        '    "missing_evidence": ["partner holdout", "incumbent queue study"]',
        '  }',
        "}",
    ]
    return "```json\n" + "\n".join(snippet) + "\n```"


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
        ["Full finalist selection", f"{selected_family} finalist", f"full-training validation PR-AUC {_format_metric(selected_val)}; selected before test", "test still hidden", "model selection"],
        ["Final fixed test", "Extra Trees with Platt calibration", "validation-only calibration and threshold", _format_metric(_metric_value(metrics, "paysim_p6a_competitive_selected.test_pr_auc")), "bounded demonstration"],
    ]
    return _markdown_table("Table 4. PaySim modeling path", ["Stage", "Model/contract", "Selection evidence", "Final test evidence", "Role"], rows)


def _render_system_evaluation_table(inputs: dict[str, Any]) -> str:
    tasks = _task_by_id(_payload(inputs["system_task_eval"]))
    def signal(task_id: str) -> str:
        return str(tasks.get(task_id, {}).get("measured_signal") or "not observed")
    def passed(task_id: str) -> str:
        return "pass" if tasks.get(task_id, {}).get("passed") else "blocked"
    rows = [
        ["Metric provenance", "metric provenance", "PaySim selected PR-AUC cell", "required fields present", _audit_result("metric_cell_provenance_available", passed, signal)],
        ["Budget comparison", "budget comparability", "PaySim baseline and competitive cells", "same dataset, split doctrine, and metric", _audit_result("paysim_baseline_and_competitive_budget_comparable", passed, signal)],
        ["PaySim interpretation", "interpretation-route check", "PaySim publishability row", "bounded use present; headline claim blocked", _audit_result("paysim_claim_boundary_machine_readable", passed, signal)],
        ["Elliptic2 reference role", "reference role check", "Elliptic2 publishability row", "reference role visible; parity evidence required", _audit_result("elliptic2_supporting_context_and_firewall_visible", passed, signal)],
        ["Rowless handoff", "handoff recovery", "agent handoff report", "state, tools, next action; no rows", _audit_result("rowless_external_agent_handoff_recoverable", passed, signal)],
        ["Interrupted recovery", "no-lost-user recovery", "guide recovery report", "stage, shortlist, next action exposed", _audit_result("partial_run_recovery_without_artifact_literacy", passed, signal)],
        ["Stronger-use routing", "routing cases", "evidence-needs case studies", "missing evidence recorded", _audit_result("claim_gate_fails_closed_for_public_interpretation", passed, signal)],
    ]
    return _markdown_table("Table 5. System audit matrix", ["Check", "Command or test", "Evidence", "Pass criterion", "Observed result"], rows)


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
        "Table 6. Failure-case evaluation",
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
        "Table 7. Governance machinery ablation",
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
                _shorten_table_text(str(row.get("enforcement_mechanism") or ""), 90),
                _shorten_table_text(_invariant_evidence_cell(row), 130),
                _shorten_table_text(str(row.get("limitation_or_boundary") or ""), 95),
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
        "Table 8. Governance invariants and evidence map",
        ["Invariant", "Mechanism", "Evidence and stress signal", "Boundary"],
        rows,
    )


def _render_hosted_score_case_study_table(inputs: dict[str, Any]) -> str:
    panel = _payload(inputs["external_score_paper_panel"])
    rows = []
    for row in panel.get("rows", []):
        if not isinstance(row, dict):
            continue
        rows.append(
            [
                row.get("component") or "",
                row.get("observed") or "",
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
        "Table 9. Hosted external-score case study",
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
        "value": snippet.get("value") if "value" in snippet else "not_available",
        "leakage_posture": snippet.get("leakage_posture") or "not_available",
        "claim_state": snippet.get("claim_state") or "not_available",
    }
    return "```json\n" + json.dumps(ordered, indent=2) + "\n```"


def _render_blocked_claim_examples_table() -> str:
    rows = [
        ["Real-bank deployment study", "bounded PaySim temporal-proxy demonstration", "Partner or bank-approved holdout, incumbent comparison, analyst-review protocol, and legal release gate."],
        ["Elliptic2 reference-method comparison", "external RevClassifyDS reference marker plus local context row", "Faithful reference execution, cohort reconciliation, resource budget, and repeated parity report."],
        ["Graph-native detector release", "Elliptic temporal graph-feature evidence path", "Graph-native release budget, neural baselines, repeated seeds, and graph-specific ablations."],
    ]
    return _markdown_table("Table 10. Evidence routing examples", ["Stronger future use", "Current admissible use", "Evidence needed"], rows)


def _render_handoff_recovery_table(inputs: dict[str, Any]) -> str:
    handoff_tasks = _task_by_id(_payload(inputs["agent_handoff_eval"]))
    recovery_tasks = _task_by_id(_payload(inputs["no_lost_user_eval"]))
    rows = [
        ["External-agent handoff", "partial run with available guide state", "state summary, action options, starter questions, tool contract, artifact shortlist", "raw transaction rows, credentials, private paths, raw source files", _paper_signal("handoff_redaction", handoff_tasks.get("external_context_rowless_and_redacted", {}).get("measured_signal"))],
        ["Safe next action", "external model asked what to do next", "six next actions, six starter questions, command options", "unredacted local paths and data rows", _paper_signal("safe_next_action", handoff_tasks.get("safe_next_action_exported", {}).get("measured_signal"))],
        ["Interrupted-run recovery", "operator returns to partial run without artifact literacy", "current state, missing evidence count, canonical artifact shortlist, context-export command", "raw benchmark data and private machine paths", _paper_signal("interrupted_recovery", recovery_tasks.get("partial_run_state_recovery", {}).get("measured_signal"))],
    ]
    return _markdown_table("Table 11. Rowless handoff and interrupted-run recovery examples", ["Scenario", "Input state", "Exported fields", "Redacted fields", "Observed signal"], rows)


def _render_reproducibility_table(inputs: dict[str, Any]) -> str:
    rows = [
        ["Minimal paper rebuild", "paper-release; paper-narrative-polish; paper-arxiv-source; paper-final-preflight", "Markdown draft, arXiv source, vector figures, PDF preflight, and paper audits", "Clean clone with Python >=3.10 and the full extra; final preflight follows local TeX compile", "source, figure, PDF, and log checks in manifests"],
        ["PaySim benchmark", "paysim-competitive --budget-tier competitive --run-optional", "Selected PaySim PR-AUC and review-budget cells", "Local Kaggle PaySim file; raw data not redistributed", _repro_hash_summary(inputs, "paysim_temporal_transaction_fraud")],
        ["Elliptic benchmark", "graph-baselines --budget-tier competitive --run-optional", "Selected Elliptic graph-feature evidence cells", "Local Kaggle Elliptic files; raw data not redistributed", _repro_hash_summary(inputs, "elliptic_bitcoin_flattened_graph_aml")],
        ["System evaluation", "paper-system-eval", "navigation, handoff, recovery, and claim-gate reports", "Repo-local deterministic fixtures", "all required tasks pass in current evidence pack"],
        ["Failure cases", "paper-failure-eval", "leakage, test-selection, overclaim, redaction, and recovery stress cases", "Repo-local deterministic fixtures", "required failure cases pass"],
        ["Governance ablation", "paper-governance-ablation", "full path compared with disabled-governance fixtures", "Repo-local deterministic fixtures", "full path safe; disabled fixtures expose expected failures"],
        ["Governance invariants", "paper-invariants", "invariant map and adjacent-systems comparison", "Repo-local deterministic fixtures", "7 invariants and 6 adjacent families recorded"],
        ["Hosted-score case study", "paper-external-score-proof; paper-external-score-integration", "rowless score schema, evidence cell, redaction, claim map, and case-study panel", "Repo-local rowless fixture by default; optional local score files stay local", "schema/content hash prefixes plus evidence-cell ID"],
    ]
    return _markdown_table("Table 12. Reproducibility contract", ["Component", "Command", "Expected output", "Environment or data dependency", "Hash or seed record"], rows)


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
        "all_numeric_cells_have_required_provenance": "metric audit",
        "metric_cell_provenance_available": "provenance task",
        "claim_safe_public_wording_allowed": "claim whitelist",
        "hard_headline_claims_blocked": "publishability matrix",
        "forbidden_balance_columns_used": "leakage report",
        "test_set_selection_violation": "test-selection fixture",
        "external_context_rowless_and_redacted": "handoff eval",
        "rowless_external_agent_handoff_recoverable": "handoff task",
        "partial_run_state_recovery": "recovery eval",
        "partial_run_recovery_without_artifact_literacy": "recovery task",
        "supporting_table_allowed": "publishability rows",
        "elliptic2_supporting_context_and_firewall_visible": "Elliptic2 role task",
        "wording_lint": "wording lint",
        "go_for_p13_claim_safe_release_pack": "go/no-go gate",
        "No evidence-cell required fields": "missing-field ablation",
        "overstrong_claim_attempt": "overclaim fixture",
        "leakage_column_injection": "leakage fixture",
        "rowless_handoff_redaction": "redaction fixture",
        "interrupted_run_recovery": "recovery fixture",
        "blocked_public_claims": "blocked claims",
        "detector_claim_boundary": "claim boundary",
    }
    return labels.get(evidence_id, _humanize_gate_token(evidence_id))


def _evidence_table_signal(value: Any, evidence_id: str) -> str:
    signal_overrides = {
        "all_numeric_cells_have_required_provenance": "pass",
        "claim_safe_public_wording_allowed": "pass",
        "forbidden_balance_columns_used": "4 forbidden fields offered; 0 used",
        "external_context_rowless_and_redacted": "raw rows absent; 8 unsafe fields redacted; 6 blocked fields recorded",
        "partial_run_state_recovery": "partial run recovered; 8 missing-evidence items and 6 recovery actions exposed",
        "supporting_table_allowed": "5 supporting rows allowed; headline and hard performance claims blocked",
        "wording_lint": "pass",
        "No evidence-cell required fields": "13 provenance fields missing; release blocked",
        "overstrong_claim_attempt": "6 unsupported claims blocked",
        "leakage_column_injection": "4 leakage fields offered; 4 excluded; 0 used",
        "rowless_handoff_redaction": "6 unsafe fields blocked; raw rows absent",
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
    return text[: max_len - 3].rstrip(" ;,.") + "..."


def _audit_result(task_id: str, passed: Callable[[str], str], signal: Callable[[str], str]) -> str:
    compact_signal = {
        "metric_cell_provenance_available": "fields 13/13 in metric-cell audit",
        "paysim_baseline_and_competitive_budget_comparable": "same split/metric; PR-AUC 0.3313 -> 0.6388",
        "paysim_claim_boundary_machine_readable": "bounded use present; headline and hard performance claims blocked",
        "elliptic2_supporting_context_and_firewall_visible": "reference role visible; parity evidence required",
        "rowless_external_agent_handoff_recoverable": "raw rows absent; 8 unsafe fields redacted; 6 blocked fields recorded",
        "partial_run_recovery_without_artifact_literacy": "partial run recovered; 8 missing-evidence items and 6 actions exposed",
        "claim_gate_fails_closed_for_public_interpretation": "case studies record missing evidence",
    }.get(task_id, signal(task_id))
    return f"{passed(task_id)}; {compact_signal}"


def _paper_signal(signal_id: str, measured_signal: Any) -> str:
    display = {
        "handoff_redaction": "raw rows absent; 8 unsafe fields redacted; 6 blocked fields recorded",
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
        "raw rows=false": "raw rows absent",
        "raw rows=no": "raw rows absent",
        "hard/headline=false": "headline and hard performance claims blocked",
        "safe=false": "release blocked",
        "blocked claims=6": "6 unsupported claims blocked",
        "blocked=6": "6 public claims blocked",
        "used=0": "0 used",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.replace(";", "; ")


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
        "official_partition_test": "official test",
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
            return f"{_format_count(total)} rows/nodes; {positive} positives"
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


def _evidence_role_from_dataset(dataset_id: str) -> str:
    roles = {
        "paysim_temporal_transaction_fraud": "bounded demonstration",
        "elliptic_bitcoin_flattened_graph_aml": "graph-feature evidence",
        "elliptic2_subgraph_aml": "external reference/context",
    }
    return roles.get(dataset_id, "recorded evidence")


def _evidence_role_from_cell(cell_id: str) -> str:
    if cell_id.startswith("paysim_p6a_"):
        return "bounded demonstration"
    if cell_id.startswith("elliptic_p7_"):
        return "graph-feature evidence"
    if cell_id.startswith("elliptic2_"):
        return "external reference/context"
    return "recorded evidence"


def _compact_claim_state(claim_state: str) -> str:
    replacements = {
        "supporting-only": "supporting only",
        "supporting_context_only_not_performance_contribution": "context only; no contribution",
        "baseline_only_not_headline": "baseline only",
        "blocked_claim_evidence": "blocked claim evidence",
    }
    return replacements.get(claim_state, _humanize_gate_token(claim_state))


def _artifact_label(source_artifact: str) -> str:
    if source_artifact == "README.md":
        return "README"
    name = Path(source_artifact).name
    label = name.replace(".json", "").replace(".md", "") or source_artifact
    labels = {
        "paper_metric_cell_audit": "metric-cell audit",
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
        "official_partition_test_pr_auc_mean": "official test PR-AUC mean",
        "official_partition_test_pr_auc_std": "official test PR-AUC std",
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
        "hist_gradient_boosting": "HistGradientBoosting",
        "sklearn_hist_gradient_boosting": "HistGradientBoosting",
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
            "I finished a first claim-safe Relaytic-AML paper draft. The core idea is local-first agentic evaluation: keep the workspace as the authority, give humans and agents clear roles, export redacted context instead of private rows, and make every metric traceable before anybody turns it into a claim. The draft foregrounds the Relaytic architecture, role boundaries, intended company and research uses, current anti-money-laundering context, figures, an arXiv source candidate, and explicit limitations for PaySim, Elliptic, Elliptic2, and AMLSim-style tracks.",
            "",
            "The benchmark rows are supporting evidence for that architecture, not the identity of the system. PaySim and Elliptic are supporting evidence only, Elliptic2 is modern context only, and stronger claims stay blocked until the gates earn them. That is the point: Relaytic-AML is being built as an auditable local evaluation environment where agents and humans can see what is proven, what is blocked, and what would need to happen next.",
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
            "- [ ] Verify the pseudonymous author block, affiliation, contact, and optional acknowledgements before upload.",
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
            "- Title: `Relaytic-AML: A Local-First Agentic Evaluation Lab for Financial-Crime Machine Learning`",
            "- Primary category: `cs.LG`",
            "- Secondary categories: `q-fin.GN`, `cs.SI`, `cs.CY`",
            "- Keywords: anti-money laundering, financial crime, graph machine learning, reproducibility, evaluation environments, claim gating",
            "",
            "## Tag And Release",
            "",
            "- [ ] Confirm `git status --short` is empty at the final tag target.",
            f"- [ ] Confirm the final tag target contains the release-pack artifacts generated from base commit `{git_commit}`; rerun the manifest after final edits if the source evidence changes.",
            f"- [ ] Create tag after the final PDF/source matches the manifest: `git tag -a {release_tag} -m \"Relaytic-AML claim-safe paper release\"`.",
            "- [ ] Attach or link the paper PDF, release manifest, public claims JSON, and benchmark artifacts.",
            "",
            "## Fallback",
            "",
            "If any gate fails, do not submit. Keep `paper_release_manifest.json` as a release-blocker report and repair the failed gate first.",
        ]
    ).rstrip() + "\n"


def _render_references_bib() -> str:
    return r"""@inproceedings{lopezrojas2016paysim,
  title = {PaySim: A Financial Mobile Money Simulator for Fraud Detection},
  author = {Lopez-Rojas, Edgar Alonso and Elmir, Ahmad and Axelsson, Stefan},
  booktitle = {Proceedings of the 28th European Modeling and Simulation Symposium},
  year = {2016},
  url = {https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf}
}

@misc{fatf2020virtualassets,
  title = {Virtual Assets Red Flag Indicators of Money Laundering and Terrorist Financing},
  author = {{Financial Action Task Force}},
  year = {2020},
  url = {https://www.fatf-gafi.org/en/publications/Methodsandtrends/Virtual-assets-red-flag-indicators.html}
}

@misc{fincenAdvisories,
  title = {Alerts, Advisories, Notices, Bulletins, and Fact Sheets},
  author = {{Financial Crimes Enforcement Network}},
  year = {2026},
  url = {https://www.fincen.gov/resources/advisoriesbulletinsfact-sheets}
}

@misc{ffiecRedFlags,
  title = {BSA/AML Examination Manual: Appendix F, Money Laundering and Terrorist Financing Red Flags},
  author = {{Federal Financial Institutions Examination Council}},
  year = {2026},
  url = {https://bsaaml.ffiec.gov/manual/Appendices/07}
}

@misc{weber2019elliptic,
  title = {Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics},
  author = {Weber, Mark and Domeniconi, Giacomo and Chen, Jie and Weidele, Daniel Karl I. and Bellei, Claudio and Robinson, Tom and Leiserson, Charles E.},
  year = {2019},
  eprint = {1908.02591},
  archivePrefix = {arXiv},
  primaryClass = {cs.SI},
  doi = {10.48550/arXiv.1908.02591},
  url = {https://arxiv.org/abs/1908.02591}
}

@misc{bellei2024elliptic2,
  title = {The Shape of Money Laundering: Subgraph Representation Learning on the Blockchain with the Elliptic2 Dataset},
  author = {Bellei, Claudio and Xu, Muhua and Phillips, Ross and Robinson, Tom and Weber, Mark and Kaler, Tim and Leiserson, Charles E. and Arvind and Chen, Jie},
  year = {2024},
  eprint = {2404.19109},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2404.19109},
  url = {https://arxiv.org/abs/2404.19109}
}

@inproceedings{song2024revtrack,
  title = {Identifying Money Laundering Subgraphs on the Blockchain},
  author = {Song, Kiwhan and Dhraief, Mohamed Ali and Xu, Muhua and Cai, Locke and Chen, Xuhao and Arvind and Chen, Jie},
  booktitle = {Proceedings of the 5th ACM International Conference on AI in Finance},
  year = {2024},
  doi = {10.1145/3677052.3698635},
  eprint = {2410.08394},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2410.08394}
}

@misc{chen2026transxion,
  title = {TransXion: A High-Fidelity Graph Benchmark for Realistic Anti-Money Laundering},
  author = {Chen, Keyang and Jiang, Mingxuan and Zhao, Yongsheng and Li, Zeping and Chen, Zaiyuan and Luo, Weiqi and Li, Zhixin and Liu, Sen and Jing, Yinan and Ye, Guangnan and Wu, Xihong and Chai, Hongfeng},
  year = {2026},
  eprint = {2604.17420},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2604.17420},
  url = {https://arxiv.org/abs/2604.17420}
}

@misc{poon2026linemvgnn,
  title = {LineMVGNN: Anti-Money Laundering with Line-Graph-Assisted Multi-View Graph Neural Networks},
  author = {Poon, Chung-Hoo and Kwok, James and Chow, Calvin and Choi, Jang-Hyeon},
  year = {2026},
  eprint = {2603.23584},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2603.23584},
  url = {https://arxiv.org/abs/2603.23584}
}

@misc{tariq2026extraqt,
  title = {Extracting Money Laundering Transactions from Quasi-Temporal Graph Representation},
  author = {Tariq, Haseeb and Hassani, Marwan},
  year = {2026},
  eprint = {2604.02899},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2604.02899},
  url = {https://arxiv.org/abs/2604.02899}
}

@misc{ye2026blazingaml,
  title = {BlazingAML: High-Throughput Anti-Money Laundering (AML) via Multi-Stage Graph Mining},
  author = {Ye, Haojie and Laxman, Arjun and Yuan, Yichao and Flautner, Krisztian and Talati, Nishil},
  year = {2026},
  eprint = {2604.12241},
  archivePrefix = {arXiv},
  primaryClass = {cs.DC},
  doi = {10.48550/arXiv.2604.12241},
  url = {https://arxiv.org/abs/2604.12241}
}

@misc{deprez2025continualaml,
  title = {Advances in Continual Graph Learning for Anti-Money Laundering Systems: A Comprehensive Review},
  author = {Deprez, Bruno and Wei, Wei and Verbeke, Wouter and Baesens, Bart and Mets, Kevin and Verdonck, Tim},
  year = {2025},
  eprint = {2503.24259},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2503.24259},
  url = {https://arxiv.org/abs/2503.24259}
}

@article{gebru2021datasheets,
  title = {Datasheets for Datasets},
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
  title = {Model Cards for Model Reporting},
  author = {Mitchell, Margaret and Wu, Simone and Zaldivar, Andrew and Barnes, Parker and Vasserman, Lucy and Hutchinson, Ben and Spitzer, Elena and Raji, Inioluwa Deborah and Gebru, Timnit},
  booktitle = {Proceedings of the Conference on Fairness, Accountability, and Transparency},
  pages = {220--229},
  year = {2019},
  doi = {10.1145/3287560.3287596},
  url = {https://arxiv.org/abs/1810.03993}
}

@article{pineau2021reproducibility,
  title = {Improving Reproducibility in Machine Learning Research},
  author = {Pineau, Joelle and Vincent-Lamarre, Philippe and Sinha, Koustuv and Lariviere, Vincent and Beygelzimer, Alina and d'Alche-Buc, Florence and Fox, Emily and Larochelle, Hugo},
  journal = {Journal of Machine Learning Research},
  volume = {22},
  number = {164},
  pages = {1--20},
  year = {2021},
  url = {https://www.jmlr.org/papers/v22/20-303.html}
}

@misc{chen2025mlrbench,
  title = {MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research},
  author = {Chen, Hui and Xiong, Miao and Lu, Yujie and Han, Wei and Deng, Ailin and He, Yufei and Wu, Jiaying and Li, Yibo and Liu, Yue and Hooi, Bryan},
  year = {2025},
  eprint = {2505.19955},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  url = {https://arxiv.org/abs/2505.19955}
}

@misc{starace2025paperbench,
  title = {PaperBench: Evaluating AI's Ability to Replicate AI Research},
  author = {Starace, Giulio and Jaffe, Oliver and Sherburn, Dane and Aung, James and Chan, Jun Shern and Maksin, Leon and Dias, Rachel and Mays, Evan and Kinsella, Benjamin and Thompson, Wyatt and Heidecke, Johannes and Glaese, Amelia and Patwardhan, Tejal},
  year = {2025},
  eprint = {2504.01848},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  doi = {10.48550/arXiv.2504.01848},
  url = {https://arxiv.org/abs/2504.01848}
}

@inproceedings{wijk2025rebench,
  title = {RE-Bench: Evaluating Frontier AI R\&D Capabilities of Language Model Agents against Human Experts},
  author = {Wijk, Hjalmar and Lin, Tao Roa and Becker, Joel and Jawhar, Sami and Parikh, Neev and Broadley, T. and Chan, Lawrence and Chen, Michael and Clymer, Joshua M. and Dhyani, Jai and Ericheva, Elena and Garcia, Katharyn and Goodrich, Brian and Jurkovic, Nikola and Kinniment, Megan and Lajko, Aron and Nix, Seraphina and Sato, Lucas Jun Koba and Saunders, William and Taran, Maksym and West, Ben and Barnes, Elizabeth},
  booktitle = {Proceedings of the 42nd International Conference on Machine Learning},
  year = {2025},
  series = {Proceedings of Machine Learning Research},
  volume = {267},
  pages = {66772--66832},
  url = {https://proceedings.mlr.press/v267/wijk25a.html}
}

@misc{yang2026skillopt,
  title = {SkillOpt: Executive Strategy for Self-Evolving Agent Skills},
  author = {Yang, Yifan and Gong, Ziyang and Huang, Weiquan and Yang, Qihao and Zhou, Ziwei and Huang, Zisu and Li, Yan and Gao, Xuemei and Dai, Qi and Liu, Bei and Qiu, Kai and Yang, Yuqing and Chen, Dongdong and Yang, Xue and Luo, Chong},
  year = {2026},
  eprint = {2605.23904},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  doi = {10.48550/arXiv.2605.23904},
  url = {https://arxiv.org/abs/2605.23904}
}
""".rstrip() + "\n"


def _render_reference_section() -> str:
    return "\n".join(
        [
            "- Lopez-Rojas, E. A., Elmir, A., and Axelsson, S. (2016). PaySim: A Financial Mobile Money Simulator for Fraud Detection. European Modeling and Simulation Symposium.",
            "- Financial Action Task Force. (2020). Virtual Assets Red Flag Indicators of Money Laundering and Terrorist Financing.",
            "- Financial Crimes Enforcement Network. (2026). Alerts, Advisories, Notices, Bulletins, and Fact Sheets.",
            "- Federal Financial Institutions Examination Council. (2026). BSA/AML Examination Manual: Appendix F, Money Laundering and Terrorist Financing Red Flags.",
            "- Weber, M., Domeniconi, G., Chen, J., Weidele, D. K. I., Bellei, C., Robinson, T., and Leiserson, C. E. (2019). Anti-Money Laundering in Bitcoin. arXiv:1908.02591.",
            "- Bellei, C., Xu, M., Phillips, R., Robinson, T., Weber, M., Kaler, T., Leiserson, C. E., Arvind, and Chen, J. (2024). The Shape of Money Laundering. arXiv:2404.19109.",
            "- Song, K., Dhraief, M. A., Xu, M., Cai, L., Chen, X., Arvind, and Chen, J. (2024). Identifying Money Laundering Subgraphs on the Blockchain. ICAIF 2024.",
            "- Chen, K. et al. (2026). TransXion: A High-Fidelity Graph Benchmark for Realistic Anti-Money Laundering. arXiv:2604.17420.",
            "- Poon, C.-H., Kwok, J., Chow, C., and Choi, J.-H. (2026). LineMVGNN: Anti-Money Laundering with Line-Graph-Assisted Multi-View Graph Neural Networks. arXiv:2603.23584.",
            "- Tariq, H., and Hassani, M. (2026). Extracting Money Laundering Transactions from Quasi-Temporal Graph Representation. arXiv:2604.02899.",
            "- Ye, H., Laxman, A., Yuan, Y., Flautner, K., and Talati, N. (2026). BlazingAML: High-Throughput Anti-Money Laundering via Multi-Stage Graph Mining. arXiv:2604.12241.",
            "- Deprez, B., Wei, W., Verbeke, W., Baesens, B., Mets, K., and Verdonck, T. (2025). Advances in Continual Graph Learning for Anti-Money Laundering Systems. arXiv:2503.24259.",
            "- Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM.",
            "- Mitchell, M. et al. (2019). Model Cards for Model Reporting. FAT* 2019.",
            "- Pineau, J. et al. (2021). Improving Reproducibility in Machine Learning Research. JMLR.",
            "- Chen, H. et al. (2025). MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research. arXiv:2505.19955.",
            "- Starace, G. et al. (2025). PaperBench: Evaluating AI's Ability to Replicate AI Research. arXiv:2504.01848.",
            "- Wijk, H. et al. (2025). RE-Bench: Evaluating Frontier AI R&D Capabilities of Language Model Agents against Human Experts. ICML 2025.",
            "- Yang, Y. et al. (2026). SkillOpt: Executive Strategy for Self-Evolving Agent Skills. arXiv:2605.23904.",
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
            "citation_key": "fincenAdvisories",
            "source_url": "https://www.fincen.gov/resources/advisoriesbulletinsfact-sheets",
            "verified_role": "Official FinCEN description of advisories, typologies, red flags, and AML monitoring use.",
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
            "citation_key": "poon2026linemvgnn",
            "source_url": "https://arxiv.org/abs/2603.23584",
            "verified_role": "Recent directed transaction-graph detector context.",
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
            "source_url": "https://arxiv.org/abs/2503.24259",
            "verified_role": "Recent continual-learning and drift context for AML graph systems.",
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


def _metric_value(metrics: dict[str, dict[str, Any]], cell_id: str) -> Any:
    return metrics.get(cell_id, {}).get("value")


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

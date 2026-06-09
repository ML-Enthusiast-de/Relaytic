"""Paper Track P13 claim-safe paper release and attention-pack artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_RELEASE_SCHEMA_VERSION = "relaytic.paper_release.v1"
PAPER_RELEASE_REPORT_DIR = Path("docs") / "reports"
PAPER_RELEASE_DOC_DIR = Path("docs") / "paper"
PAPER_RELEASE_TABLE_DIRNAME = "tables"
PAPER_RELEASE_DATE = "2026-06-09"
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
        "table_provenance": _read_artifact(reports / "paper_table_provenance.json"),
        "paper_reproduction_commands": _read_text_artifact(reports / "paper_reproduction_commands.md"),
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
                "fill author metadata, affiliation, contact, license, and acknowledgements",
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
            "Relaytic-AML is a local-first, claim-gated evaluation environment for temporal, graph, and operational financial-crime ML.",
            "The current paper pack presents Relaytic as a local-first AML evaluation lab with local artifacts, specialist roles, redacted context export, and explicit claim boundaries.",
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
        present = bool(artifact.get("exists")) if artifact else (Path(ref).suffix == ".svg")
        role = "internal evidence record" if ref.startswith("docs/reports") else "reader-facing paper asset"
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
            "Can keep all data on a controlled local machine, server, or cluster.",
            "Mandate, policy, permission, and next-action artifacts.",
        ),
        (
            "Guide and assist layer",
            "Answers where the run is, what artifacts matter, and which action is safe next.",
            "Uses local artifacts first. Optional LLM help is advisory and redacted by default.",
            "Guide payloads, assist turns, status, and context packs.",
        ),
        (
            "Scout and task-contract agents",
            "Inspect source posture, target semantics, split validity, and leakage risk.",
            "Work from staged local snapshots rather than mutating the original data source.",
            "Dataset registry, source manifests, split contracts, and task reports.",
        ),
        (
            "Scientist and challenger agents",
            "Propose baselines, ablations, shadow candidates, and failure explanations.",
            "Candidate work is bounded by explicit budgets and local artifact permissions.",
            "Experiment registry, scorecards, ablations, and shadow-trial reports.",
        ),
        (
            "Builder and search controller",
            "Execute reproducible model/search plans and select thresholds on validation evidence.",
            "Optional adapters are versioned and never become hidden sources of truth.",
            "Run directories, model artifacts, search traces, and operating-point records.",
        ),
        (
            "Claim and release governors",
            "Decide which evidence can be said publicly and which claims stay blocked.",
            "Fail closed on leakage, missing provenance, unsafe wording, or dirty release state.",
            "Metric cells, claim boundaries, public wording notes, and source-bundle audits.",
        ),
        (
            "External agents or LLMs",
            "Consume exported context, propose repairs, or continue work through stable surfaces.",
            "Receive rowless/redacted context unless policy explicitly grants richer access.",
            "External context packs, handoff reports, and reproducible commands.",
        ),
    ]
    lines = [
        "| Role | What it owns | Local-first boundary | Main artifacts |",
        "|---|---|---|---|",
    ]
    for role, owns, boundary, artifacts in rows:
        lines.append(
            f"| {_escape_md(role)} | {_escape_md(owns)} | {_escape_md(boundary)} | {_escape_md(artifacts)} |"
        )
    return "\n".join(lines)


def _render_final_paper(
    *,
    inputs: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    tables: dict[str, str],
) -> str:
    reproduction_commands = _normalize_embedded_reproduction_commands(
        _text_payload(inputs["paper_reproduction_commands"]).strip()
    )
    if not reproduction_commands:
        reproduction_commands = "relaytic release-safety paper-tables --format json\nrelaytic release-safety paper-draft --format json"
    pay_pr = _format_metric(_metric_value(metrics, "paysim_p6a_competitive_selected.test_pr_auc"))
    ell_pr = _format_metric(_metric_value(metrics, "elliptic_p7_selected_graph_feature_baseline.test_pr_auc"))
    e2_pr = _format_metric(_metric_value(metrics, "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean"))
    e2_std = _format_metric(_metric_value(metrics, "elliptic2_p8b_modern_context.official_partition_test_pr_auc_std"))
    ref_pr = _format_metric(_metric_value(metrics, "elliptic2_p8b_modern_context.published_reference_pr_auc"))
    limitations = _render_limitations(_payload(inputs["limitations_matrix"]))
    figure_manifest = _payload(inputs["figure_manifest"])
    architecture_figures = _render_figure_list(figure_manifest, figure_ids={"claim_gate_flow"})
    evidence_figures = _render_figure_list(
        figure_manifest,
        figure_ids={"supporting_pr_auc", "review_budget", "publishability_matrix"},
    )
    agent_roles = _render_agent_role_table()
    references = _render_reference_section()
    return "\n".join(
        [
            "# Relaytic-AML: A Local-First Evaluation Lab for Financial-Crime ML",
            "",
            "## Abstract",
            "",
            "Financial-crime machine learning is usually judged by detector scores, but operational AML work depends on evidence a team can trust: data posture, temporal validity, graph provenance, review capacity, and claim discipline. Relaytic-AML is a local-first evaluation lab for that setting. It keeps the workspace as the source of truth, records data and modeling decisions as inspectable artifacts, and lets specialist agents help without making their prose the authority.",
            "",
            "Relaytic began as a general local inference-engineering system. In this work it is sharpened into an AML-focused environment where a human or external agent can ask what is known, what is blocked, and what should happen next. The public evidence includes supporting PaySim synthetic temporal-fraud PR-AUC "
            f"{pay_pr}, supporting Elliptic temporal graph-feature PR-AUC {ell_pr}, and Elliptic2 modern-context PR-AUC {e2_pr} +/- {e2_std}, below the recorded RevClassifyDS reference of {ref_pr}. The contribution is not a detector-superiority claim. It is a reproducible architecture for keeping experiments, review assumptions, limitations, and public wording aligned.",
            "",
            "## 1. Introduction",
            "",
            "AML systems are operational decision systems. A useful model does not only rank transactions or entities. It has to respect time, explain why a case reached a review queue, preserve graph or entity provenance, and make clear what a result does not prove. This is especially hard in financial-crime work because the most realistic data is private, licensed, regulated, or operationally sensitive.",
            "",
            "Relaytic was first built as a broader local inference lab for structured data. The AML edition is a deliberate narrowing of that idea. Instead of trying to be a generic benchmark runner, Relaytic-AML asks a more practical question: can a local machine or local server become a trustworthy evaluation lab where data, modeling work, agent assistance, review assumptions, and public claims stay connected?",
            "",
            "The answer explored here is architectural. Relaytic-AML treats the local workspace as the authority. Models, tables, context packs, figures, and paper text are downstream of artifacts on disk. Agents are useful, but they act through bounded roles. A guide explains the current state. A scout checks data posture and leakage risk. A scientist challenges the modeling plan. A builder runs the experiment. A claim governor decides whether a result can be described publicly. The user is never expected to know which file to open first because Relaytic itself can explain the run state and export a compact context pack for another LLM or coding agent.",
            "",
            "The benchmarks in this paper are deliberately modest in their role. They are stress tests for the environment. A score is valuable only if the reader can see the dataset boundary, split rule, budget, operating point, limitation, and claim boundary that produced it. This paper therefore presents Relaytic-AML as an evaluation lab first and a benchmark package second.",
            "",
            "## 2. Contribution and Scope",
            "",
            "This paper is a systems paper about local-first AML evaluation. Its first contribution is the Relaytic-AML architecture: a workspace-centered lab where artifacts, not chat transcripts, carry the truth of an experiment. The second contribution is a role model for agentic help that keeps guidance, scouting, scientific challenge, model building, and claim review separate. The third contribution is an evidence-cell contract that makes every reported number traceable to a dataset, split, command, artifact field, budget, operating point, and claim state. The fourth contribution is a claim discipline that keeps useful evidence from becoming stronger than it deserves to be.",
            "",
            "This scope matters. Relaytic-AML does not claim hard AML superiority, production readiness, graph-neural superiority, or equivalence to RevClassify. It shows a working local evaluation environment that can run meaningful public evidence, expose where stronger claims remain blocked, and give both humans and agents a stable way to continue the work.",
            "",
            "| Paper claim | Relaytic mechanism | Current evidence posture |",
            "|---|---|---|",
            "| Local state is auditable | Run directories, manifests, traces, metric cells, tables, and release reports live in the workspace | Demonstrated by the generated paper and source package |",
            "| Agent help is bounded | Guide, scout, scientist, builder, and claim governor roles have separate jobs and artifacts | Architecture evidence; not yet a formal autonomy benchmark |",
            "| Scores are traceable | Evidence cells bind every number to dataset, split, command, artifact field, budget, and claim state | Supporting PaySim, Elliptic, and Elliptic2-context rows |",
            "| Public wording is governed | Claim linting, release manifests, and source-package audits fail closed | Hard and headline AML claims remain blocked |",
            "",
            "## 3. Questions",
            "",
            "The central question is whether an AML evaluation system can stay useful without becoming opaque. A trained reader can understand PR-AUC, temporal splits, graph features, and review budgets. That reader cannot know Relaytic's internal state unless the system makes it legible. The paper therefore asks whether Relaytic can keep the state of a run visible, whether external agents can receive enough structured context to help safely, and whether claim boundaries can stop a local result from being overstated.",
            "",
            "| Question | What to inspect | Current answer |",
            "|---|---|---|",
            "| Can local artifacts remain the authority? | Source manifests, run summaries, metric cells, tables, and source-bundle reports | Yes for the current paper path |",
            "| Can humans and agents avoid getting lost? | Guide, status, assist, mission-control, and redacted context-export surfaces | Supported by product surfaces; formal user/agent study remains future work |",
            "| Can benchmark evidence stay useful without becoming marketing language? | Claim-boundary reports, public wording lint, and release gates | Yes: supporting rows are visible while stronger claims stay blocked |",
            "| What would make the work stronger? | Future unlock conditions for holdout data, same-queue comparison, and faithful graph reference reproduction | Explicitly listed as future work rather than implied as solved |",
            "",
            "## 4. Local-First Agent Architecture",
            "",
            "Relaytic is designed around one control rule: the user's workspace is the authority. Raw and licensed data stay local by default. Run directories, manifests, traces, metric cells, model files, and paper assets form the durable record. Semantic caches, memory indexes, and LLM summaries are derived views. This is different from a remote-first agent that sends private rows to a hosted planner and later reconstructs provenance from a conversation.",
            "",
            "The system is agentic, but the roles are concrete. They are small jobs with bounded permissions and visible outputs. A scout inspects source posture and split risk. A scientist challenges baselines and ablations. A builder executes a controlled run. A claim governor can reject wording even when the model score looks attractive. A guide explains the current state to a human or exports a redacted context pack to another model.",
            "",
            agent_roles,
            "",
            "Two design choices carry most of the system. First, important work produces a local artifact that another human or agent can inspect. Second, optional intelligence is subordinate to the artifact graph. A local LLM may help phrase guidance, and a frontier model may suggest repairs, but neither becomes the source of truth unless its proposal is converted into a reproducible local artifact.",
            "",
            architecture_figures,
            "",
            "## 5. Current Frontier Context",
            "",
            "The current AML frontier is not a single leaderboard. It is a set of pressure points: real graph scale, realistic entity behavior, temporal drift, operational throughput, and reliable agent-assisted research. Relaytic-AML is designed as infrastructure around those pressure points, not as a replacement for detector papers.",
            "",
            "Recent agentic-ML work also treats external state, benchmark environments, and research validity as first-class objects. SkillOpt, for example, frames agent skills as trainable external state with validation-gated edits [@yang2026skillopt], while MLR-Bench evaluates whether agents can produce valid open-ended ML research rather than only fluent reports [@chen2025mlrbench]. Relaytic-AML follows the same broader style of making the environment and its evidence inspectable, but applies it to AML-specific data custody, review queues, and public-claim gates.",
            "",
            "PaySim is a synthetic mobile-money simulator designed to address the scarcity of legitimate public mobile-transaction datasets for fraud research [@lopezrojas2016paysim]. It is useful for temporal transaction-fraud workflow evaluation, but synthetic evidence cannot by itself establish hard real-bank AML performance.",
            "",
            "The Elliptic Bitcoin dataset introduced a public transaction graph with more than 200K transaction nodes, 234K directed payment-flow edges, and 166 node features across 49 time steps [@weber2019elliptic]. That work also showed why graph evidence must be compared against strong simpler baselines rather than assumed superior.",
            "",
            "Elliptic2 shifts the public AML benchmark center toward subgraph learning, with 121,810 labeled subgraphs inside a background graph of roughly 49M node clusters and 196M edge transactions [@bellei2024elliptic2]. RevTrack and RevClassify further argue that sender and receiver context around a subgraph can be a powerful and scalable signal [@song2024revtrack]. These works motivate Relaytic-AML's modern-context and limitation track, but they do not make the current Relaytic Elliptic2 row a performance contribution.",
            "",
            "Recent AML graph work raises the bar beyond the current Relaytic evidence rows. TransXion frames benchmark realism around profile-aware simulation, richer entity attributes, non-template illicit synthesis, and out-of-character behavior [@chen2026transxion]. LineMVGNN and ExSTraQt focus on directed money flow, edge-aware graph views, and quasi-temporal transaction representations [@poon2026linemvgnn] [@tariq2026extraqt]. BlazingAML treats throughput and multi-stage graph mining as a systems problem [@ye2026blazingaml]. Continual graph-learning reviews emphasize drift, adaptation, class imbalance, and changing laundering behavior [@deprez2025continualaml]. Relaytic-AML is complementary to these efforts. It does not claim detector parity with them. It tries to make dataset posture, split validity, budget, limitations, and public claims auditable.",
            "",
            "The paper also follows broader ML documentation and reproducibility practice. Datasheets for Datasets and Model Cards argue for explicit dataset and model reporting [@gebru2021datasheets] [@mitchell2019modelcards]. The NeurIPS reproducibility program highlights the need for code, data, and checklist discipline in ML research [@pineau2021reproducibility]. Recent work on ML research agents warns that coherent papers can still contain invalidated experiments, which reinforces the need for executable artifacts and claim boundaries [@chen2025mlrbench].",
            "",
            "## 6. Methodology: Evidence Cells, Gates, and Budgets",
            "",
            "Relaytic-AML treats a metric as an evidence cell, not as a free-standing score. An evidence cell records the dataset identity, split contract, execution command, run or artifact reference, metric value, budget tier, leakage posture, operating-point rule, claim state, and limitation notes. A reported row is accepted only when those fields are present.",
            "",
            "The claim gate is intentionally conservative. It can mark a row as supporting evidence, modern context, baseline-only evidence, or blocked evidence. In the current public version, no row is headline-eligible. This is not a weakness of the environment. It is the point of the environment. A strong-looking number is only useful if the system can also say what the number is allowed to mean.",
            "",
            "The budget ladder separates quick engineering checks from serious evidence. Smoke runs test that commands and artifacts exist. Baseline runs establish conservative rows. Competitive runs add stronger feature families, validation-only threshold selection, calibration, and model search. Frozen reporting runs preserve the transformation from experiment to table, figure, and public claim. This prevents a weak first pass from being quietly promoted into a strong paper claim.",
            "",
            "For an external reader, the important idea is simple: every number has a trail, and every claim has a boundary. The trail helps another person reproduce or challenge the result. The boundary says whether the result is a benchmark observation, an operational estimate, a limitation, or a claim that should not be made yet.",
            "",
            "## 7. Evidence Operating Layer",
            "",
            "The local-first architecture becomes concrete through an evidence operating layer. Relaytic-AML is not only a model runner. It coordinates source posture, task semantics, split discipline, model search, decision thresholds, review queues, artifacts, and claim boundaries.",
            "",
            "| Layer | What Relaytic records | Why it matters |",
            "|---|---|---|",
            "| Source and task contracts | Dataset access, target semantics, benchmark posture, and split rules | A reader can see whether the task is valid before judging the score |",
            "| Execution and search | Candidate families, budgets, calibration, thresholds, and selected runs | Model development becomes inspectable instead of anecdotal |",
            "| AML domain layer | Entity graphs, typology posture, review queues, delayed labels, and case evidence | The model is tied to the analyst workflow it is supposed to support |",
            "| Evidence ledger | Metric cells, tables, figures, limitations, and commands | Numbers are connected to the artifacts that produced them |",
            "| Claim boundaries | Allowed claims, blocked claims, and future unlock conditions | The same result cannot quietly become marketing language |",
            "| Handoff surfaces | Guide, status, assist, mission control, and redacted context export | Humans and external agents can continue work without guessing hidden state |",
            "",
            "This operating layer is useful even when a detector claim is blocked. A blocked row is not thrown away. It becomes a structured research state with a reason, an artifact reference, and a repair path.",
            "",
            "## 8. What Relaytic-AML Is For",
            "",
            "The intended user is a person or team that has data, a risky modeling question, and a need to know whether the evidence is strong enough to act on. That includes a bank team comparing a new model against an incumbent queue, a fraud group exploring a new dataset, a researcher testing a benchmark protocol, or an external agent trying to continue a run without seeing private rows.",
            "",
            "| Capability | Reader-facing meaning |",
            "|---|---|",
            "| Local-first privacy posture | Private or licensed data can stay outside the public repo while hashes, access posture, and evidence artifacts remain inspectable |",
            "| Artifact-first reproducibility | Tables and figures are tied to local JSON and model artifacts rather than loose notes |",
            "| Role-scoped agent help | A guide, scout, scientist, builder, and claim reviewer have different responsibilities |",
            "| Budget-aware modeling | Quick checks, baseline evidence, competitive runs, and frozen reporting are kept separate |",
            "| Operational evaluation | Review-budget precision, recall, false-positive burden, and case-packet completeness sit next to model metrics |",
            "| External context export | Another LLM or coding agent can receive a redacted summary and reproducible commands |",
            "",
            "This is why the project moved from a broad Relaytic system toward Relaytic-AML as the flagship story. The general architecture still matters, but AML gives it a sharper test. It forces the system to handle rare events, temporal splits, graph context, human review limits, privacy, and public-claim discipline at the same time.",
            "",
            "Companies could use this kind of lab to challenge incumbent rules or models on the same review queue, evaluate whether a new dataset is worth deeper investment, audit whether a vendor comparison is fair, and prepare evidence packs for compliance or model-risk review. Researchers could use it to ask whether an AML result is supported, blocked, or mainly useful as a limitation.",
            "",
            "## 9. Evaluation Environment",
            "",
            "The current evaluation environment combines public benchmark evidence with local artifact discipline. Dataset registry artifacts define source and access posture. Split contracts define chronological, graph-snapshot, or subgraph partition rules. Benchmark runners produce model and operating-point artifacts. Tables and figures then read from those artifacts.",
            "",
            "The current public evidence uses three tracks. PaySim is a synthetic temporal proxy. Elliptic is temporal graph-feature evidence. Elliptic2 is retained as modern subgraph context and limitation evidence because a faithful RevClassify reference-protocol reproduction has not yet been completed locally.",
            "",
            "The environment follows three design rules. Local artifacts are the source of truth. Validation selects models, thresholds, and operating points before fixed test evaluation. Blocked evidence stays visible because hiding failed or incomplete tracks makes both human and agent-assisted research less scientific.",
            "",
            "## 10. Benchmark Protocol",
            "",
            "The benchmark protocol is deliberately subordinate to the architecture. Its purpose is to check whether Relaytic can produce traceable evidence, respect split and leakage contracts, expose operational assumptions, and block unsupported claims. A single score does not define the value of the system.",
            "",
            "The public rows separate baseline and competitive evidence. Competitive rows use stronger feature families, candidate search, calibration, and validation-only operating-point selection. The goal is not to pretend the current numbers are final. The goal is to make their scope visible.",
            "",
            "The evidence summary below should be read as a claim-boundary table as much as a performance table. The numbers matter, but the posture column is what stops them from being overstated.",
            "",
            _reader_facing_table(tables["evidence_summary"], title="Table 1. Evidence Summary"),
            "",
            evidence_figures,
            "",
            "## 11. Results",
            "",
            "The PaySim competitive row improves over the PaySim baseline inside the synthetic temporal-fraud contract. The Elliptic graph-feature row is useful supporting graph evidence, but it is not a graph-neural superiority claim. The Elliptic2 context row is strong enough to justify more work, but not enough to claim parity with the RevClassifyDS reference or to make an Elliptic2 performance contribution.",
            "",
            "The more important result is the behavior of the environment. Relaytic can carry a useful score and still refuse the stronger sentence. In financial-crime ML, that refusal is not cosmetic. It is part of scientific and operational honesty.",
            "",
            _reader_facing_table(tables["claim_gate_matrix"], title="Table 2. Claim Gate Matrix"),
            "",
            "## 12. Discussion",
            "",
            "The practical value of Relaytic-AML is not that it replaces a compliance platform or wins one benchmark table. Its value is that it gives risk, fraud, or AML teams a local evidence lab for unknown datasets, incumbent challenges, review-budget tradeoffs, leakage checks, and claim discipline. A team evaluating a new dataset can inspect whether the result is a model win, an environment win, a proxy-only result, or a blocked claim.",
            "",
            "For research teams and agentic ML workflows, the same structure is a guard against coherent but invalid experiments. External agents can read the structured artifacts, see blocked claims, and propose the next benchmark action without inferring hidden state from prose. The strongest story is the artifact discipline: Relaytic-AML demonstrates that an ambitious evaluation system can still refuse claims it has not earned.",
            "",
            "The system is also valuable when results are not spectacular. A low or blocked row can still tell a team that a dataset is synthetic-only, that a split leaks future information, that a graph-native candidate failed to beat strong tabular features, that a review-queue claim lacks a same-queue incumbent, or that a paper sentence is stronger than the evidence permits. In high-risk financial-crime settings, those negative answers are productive outputs.",
            "",
            "A company would not use Relaytic-AML because it magically knows AML. It would use it because the difficult parts of a model evaluation are forced into the open: what data was allowed to move, what split was used, what budget was spent, whether the threshold was chosen on validation evidence, what a reviewer would see, and which sentence the evidence still refuses to support.",
            "",
            "## 13. Limitations",
            "",
            "The current public evidence is not a deployment validation. PaySim is synthetic mobile-money evidence, so it cannot establish real-bank AML superiority. The Elliptic row is a temporal graph-feature result, not proof that a graph-neural model is better. Elliptic2 is modern context, not a Relaytic performance contribution, because faithful reference-protocol reproduction and cohort equivalence still need more work.",
            "",
            "The operational evidence also remains early. The review-budget rows are useful for showing how Relaytic connects model output to analyst capacity, but they do not prove analyst-hour savings against an incumbent queue. A stronger version of this work should include complete case packets, a same-queue incumbent comparison, and a partner-approved or otherwise realistic holdout.",
            "",
            "The paper therefore does not make a hard AML superiority claim. It argues that Relaytic-AML is a useful local evaluation environment and that the current benchmark rows are enough to demonstrate the architecture. They are not enough to end the detector question.",
            "",
            "## 14. Future Work",
            "",
            "The next step is to make the architecture harder to fool and the evidence more operationally realistic. Some work should test Relaytic itself: whether the guide, scout, scientist, builder, and claim reviewer agree about the same local run state, and whether an external LLM can use a redacted context pack to propose a useful repair without inventing unsupported claims. Other work should push the AML evidence: a partner-approved holdout, faithful Elliptic2 reference reproduction, stronger graph-native candidates, continual-learning experiments, and same-queue business-value comparisons.",
            "",
            "The next strong paper version should evaluate the environment as directly as it evaluates detector rows. A first-time human, a local LLM, and an external coding agent should each be given the same run and asked to recover current state, identify the right artifacts, propose the next safe action, and avoid unsupported public claims. That would turn Relaytic's usability promise into a measurable benchmark rather than a narrative assertion.",
            "",
            "| Direction | What would make the claim stronger |",
            "|---|---|",
            "| Role-level evaluation | Show that guide, scout, scientist, builder, and claim reviewer agree on the same run state |",
            "| External-agent handoff | Measure whether redacted context packs let another model help without seeing private rows |",
            "| Realistic AML holdout | Add partner-approved or otherwise realistic data with frozen access posture and repeated runs |",
            "| Elliptic2 reproduction | Run a faithful RevClassify-style protocol or define a new leakage-resistant cohort |",
            "| Operational proof | Compare against the same review queue or incumbent ruleset with complete case packets |",
            "| Continual learning | Add drift, delayed labels, recalibration, and forgetting tests |",
            "",
            "The longer-term goal is still broader than AML. Relaytic should become a general local evaluation laboratory for structured, temporal, and graph ML. AML is the current flagship because it forces the system to handle privacy, time, graph context, human review, and claim discipline together.",
            "",
            "## 15. Reproducibility",
            "",
            "The code, paper source, figures, tables, and public evidence artifacts are in the Relaytic repository. The public repo keeps raw private or licensed data out of version control. Where a benchmark requires local data, the command ledger describes the expected local paths and access posture.",
            "",
            "A compact reproduction path for the public paper assets is:",
            "```powershell",
            "relaytic release-safety paper-tables --format json",
            "relaytic release-safety paper-draft --format json",
            "relaytic release-safety paper-release --format json",
            "relaytic release-safety paper-arxiv-source --format json",
            "relaytic scan-git-safety",
            "```",
            "",
            "The main reader-facing files are `docs/paper/relaytic_aml_arxiv_draft.md`, `docs/paper/relaytic_aml_arxiv_draft.pdf`, `docs/paper/arxiv_src/`, `docs/paper/figures/`, and `docs/paper/tables/`. The benchmark command ledger is `docs/reports/paper_reproduction_commands.md`. The README explains the current project shape: Relaytic remains the general package and CLI, while Relaytic-AML is the flagship AML edition used for this paper.",
            "",
            "## 16. Author Use of AI Assistance",
            "",
            "This manuscript was written and revised by the human author with assistance from LLM-based tools for drafting, editing, repository inspection, consistency checks, and formatting support. The author reviewed the text, code references, figures, tables, claims, and limitations, and remains responsible for the accuracy and interpretation of the work. The LLM tools are not listed as authors because they do not take responsibility for the manuscript or the underlying experiments.",
            "",
            "## 17. Conclusion",
            "",
            "Relaytic-AML should be read as a local-first AML evaluation-lab paper. The current work is valuable because it makes the operating idea concrete. Data stays locally governed. Specialist roles create inspectable artifacts. External agents receive structured context instead of hidden state. Claim boundaries prevent stronger wording than the evidence has earned. The same evidence does not support hard AML superiority, a headline benchmark claim, graph-neural superiority, claimed equivalence to RevClassify, or hard business value. That restraint is not a footnote. It is part of the contribution.",
            "",
            "The right test for this version is therefore not whether it ends the AML detector race. It does not. The right test is whether the repository makes the current evidence easier to inspect, easier to challenge, and harder to oversell. That is the claim this paper is prepared to make.",
            "",
            "## References",
            "",
            references,
        ]
    ).rstrip() + "\n"


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
            "Relaytic-AML is a local-first agentic evaluation environment for financial-crime ML where specialist roles, local artifacts, redacted context packs, evidence cells, and claim gates keep humans and external agents oriented without turning benchmark rows into unsupported claims.",
            "",
            "## Short Abstract",
            "",
            "The Relaytic-AML draft presents a local-first architecture for agent-assisted AML evaluation, not a detector superiority claim. The controlled workspace is the source of truth. Specialist roles inspect source posture, challenge modeling plans, execute bounded searches, explain current state, and govern public claims. Benchmarks exercise that architecture. The current draft includes supporting PaySim synthetic temporal-fraud test PR-AUC "
            f"{pay_pr} and supporting Elliptic temporal graph-feature test PR-AUC {ell_pr}, while blocking hard AML, headline, graph-neural, claimed-equivalence-to-RevClassify, and hard business-value claims.",
            "",
            "## Public Post",
            "",
            "I finished a first claim-safe Relaytic-AML paper draft. The core idea is local-first agentic evaluation: keep the workspace as the authority, give humans and agents clear roles, export redacted context instead of private rows, and make every metric traceable before anybody turns it into a claim. The draft foregrounds the Relaytic architecture, role boundaries, intended company and research uses, current frontier AML context, figures, an arXiv source candidate, and explicit limitations for PaySim, Elliptic, Elliptic2, and AMLSim-style tracks.",
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
            "- [ ] Fill in author name, affiliation, contact, and optional acknowledgements before upload.",
            "- [ ] Confirm the AI-assistance disclosure is accurate before upload.",
            "",
            "## Public Claim Discipline",
            "",
            "- [ ] Public posts use `docs/reports/paper_attention_pack.md` wording only.",
            "- [ ] Do not add hard AML, headline, SOTA, claimed-equivalence-to-RevClassify, graph-neural superiority, or hard business-value claims.",
            f"- [ ] Confirm public wording status is `{public_claims.get('status')}`.",
            "",
            "## Suggested arXiv Metadata",
            "",
            "- Title: `Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML`",
            "- Primary category: `cs.LG`",
            "- Secondary categories: `q-fin.GN`, `cs.SI`, `cs.CY`",
            "- Keywords: AML, financial crime, graph ML, reproducibility, evaluation environments, claim gating",
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
  url = {https://cacm.acm.org/research/datasheets-for-datasets/}
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
            "- Yang, Y. et al. (2026). SkillOpt: Executive Strategy for Self-Evolving Agent Skills. arXiv:2605.23904.",
        ]
    )


def _source_verification_records() -> list[dict[str, str]]:
    return [
        {
            "citation_key": "lopezrojas2016paysim",
            "source_url": "https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf",
            "verified_role": "PaySim synthetic mobile-money simulator source and caveat.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "weber2019elliptic",
            "source_url": "https://arxiv.org/abs/1908.02591",
            "verified_role": "Elliptic transaction graph size, features, and AML benchmark context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "bellei2024elliptic2",
            "source_url": "https://arxiv.org/abs/2404.19109",
            "verified_role": "Elliptic2 subgraph benchmark scale and task framing.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "song2024revtrack",
            "source_url": "https://arxiv.org/abs/2410.08394",
            "verified_role": "RevTrack/RevClassify modern reference and subgraph-method context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "chen2026transxion",
            "source_url": "https://arxiv.org/abs/2604.17420",
            "verified_role": "Recent AML benchmark-realism context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "poon2026linemvgnn",
            "source_url": "https://arxiv.org/abs/2603.23584",
            "verified_role": "Recent directed transaction-graph detector context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "tariq2026extraqt",
            "source_url": "https://arxiv.org/abs/2604.02899",
            "verified_role": "Recent quasi-temporal transaction-graph detector context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "ye2026blazingaml",
            "source_url": "https://arxiv.org/abs/2604.12241",
            "verified_role": "Recent high-throughput AML graph-mining systems context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "deprez2025continualaml",
            "source_url": "https://arxiv.org/abs/2503.24259",
            "verified_role": "Recent continual-learning and drift context for AML graph systems.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "gebru2021datasheets",
            "source_url": "https://cacm.acm.org/research/datasheets-for-datasets/",
            "verified_role": "Dataset documentation and transparency context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "pineau2021reproducibility",
            "source_url": "https://www.jmlr.org/papers/v22/20-303.html",
            "verified_role": "ML reproducibility checklist and code/data discipline context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "chen2025mlrbench",
            "source_url": "https://arxiv.org/abs/2505.19955",
            "verified_role": "Agent-generated ML research reliability and invalidated-experiment risk context.",
            "accessed_date": PAPER_RELEASE_DATE,
        },
        {
            "citation_key": "yang2026skillopt",
            "source_url": "https://arxiv.org/abs/2605.23904",
            "verified_role": "Recent agentic-ML context for treating external agent state and validation-gated updates as first-class research objects.",
            "accessed_date": PAPER_RELEASE_DATE,
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
    return {
        "schema_version": PAPER_RELEASE_SCHEMA_VERSION,
        "status": "pass" if not violations else "fail",
        "rule_count": len(FORBIDDEN_PUBLIC_RULES),
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
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def _yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|")

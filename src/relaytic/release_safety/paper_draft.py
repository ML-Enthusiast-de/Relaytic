"""Paper Track P11 claim-linted paper draft and figure pack."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_DRAFT_SCHEMA_VERSION = "relaytic.paper_draft.v1"
PAPER_DRAFT_DOC_DIR = Path("docs") / "paper"
PAPER_DRAFT_REPORT_DIR = Path("docs") / "reports"
PAPER_DRAFT_FIGURE_DIRNAME = "figures"
PAPER_DRAFT_DOC_FILENAME = "relaytic_aml_draft.md"
PAPER_DRAFT_FILENAMES = {
    "paper_claim_lint_report": "paper_claim_lint_report.json",
    "paper_limitations_matrix": "paper_limitations_matrix.json",
}
PAPER_FIGURE_FILENAMES = {
    "claim_gate_flow": "figure_1_claim_gate_flow.svg",
    "supporting_pr_auc": "figure_2_supporting_pr_auc.svg",
    "review_budget": "figure_3_review_budget.svg",
    "publishability_matrix": "figure_4_publishability_matrix.svg",
}
PAPER_FIGURE_MANIFEST_FILENAME = "figure_manifest.json"


def build_paper_draft_pack(project_root: str | Path) -> dict[str, Any]:
    """Build P11 draft, figures, limitations, and claim lint from P10 artifacts."""
    root = Path(project_root)
    inputs = _collect_inputs(root / PAPER_DRAFT_REPORT_DIR)
    limitations = _build_limitations_matrix(inputs)
    figures = _build_figure_pack(inputs)
    draft = _render_paper_draft(inputs=inputs, limitations=limitations, figure_manifest=figures["manifest"])
    lint = _build_claim_lint_report(inputs=inputs, draft=draft, limitations=limitations, figure_manifest=figures["manifest"])
    return {
        "paper_draft": draft,
        "paper_claim_lint_report": lint,
        "paper_limitations_matrix": limitations,
        "paper_figure_manifest": figures["manifest"],
        "figures": figures["svg"],
    }


def sync_paper_draft_pack(
    project_root: str | Path,
    *,
    paper_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write the P11 paper draft pack to docs/paper and docs/reports by default."""
    root = Path(project_root)
    resolved_paper_dir = Path(paper_dir) if paper_dir is not None else root / PAPER_DRAFT_DOC_DIR
    resolved_report_dir = Path(output_dir) if output_dir is not None else root / PAPER_DRAFT_REPORT_DIR
    figure_dir = resolved_paper_dir / PAPER_DRAFT_FIGURE_DIRNAME
    resolved_paper_dir.mkdir(parents=True, exist_ok=True)
    resolved_report_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    pack = build_paper_draft_pack(root)
    written: dict[str, Path] = {}

    draft_path = resolved_paper_dir / PAPER_DRAFT_DOC_FILENAME
    draft_path.write_text(str(pack["paper_draft"]), encoding="utf-8")
    written["paper_draft"] = draft_path

    for key, filename in PAPER_DRAFT_FILENAMES.items():
        written[key] = write_json(resolved_report_dir / filename, pack[key], indent=2, sort_keys=True)

    written["paper_figure_manifest"] = write_json(
        figure_dir / PAPER_FIGURE_MANIFEST_FILENAME,
        pack["paper_figure_manifest"],
        indent=2,
        sort_keys=True,
    )
    for figure_id, svg in dict(pack["figures"]).items():
        filename = PAPER_FIGURE_FILENAMES[figure_id]
        path = figure_dir / filename
        path.write_text(str(svg), encoding="utf-8")
        written[figure_id] = path
    return written


def render_paper_draft_markdown(pack: dict[str, Any]) -> str:
    lint = dict(pack.get("paper_claim_lint_report", {}))
    limitations = dict(pack.get("paper_limitations_matrix", {}))
    manifest = dict(pack.get("paper_figure_manifest", {}))
    return "\n".join(
        [
            "# Paper P11 Draft Pack",
            "",
            f"- Claim lint: `{lint.get('status') or 'unknown'}`",
            f"- Paper may continue to P12: `{lint.get('paper_can_continue_to_p12')}`",
            f"- Limitations tracked: `{len(limitations.get('limitations') or [])}`",
            f"- Figures generated: `{len(manifest.get('figures') or [])}`",
            f"- Hard claims allowed: `{lint.get('hard_claims_allowed')}`",
            f"- Headline claims allowed: `{lint.get('headline_claims_allowed')}`",
        ]
    ).rstrip() + "\n"


def _collect_inputs(reports: Path) -> dict[str, Any]:
    return {
        "thesis_contract": _read_artifact(reports / "paper_thesis_contract.json"),
        "claim_taxonomy": _read_artifact(reports / "paper_claim_taxonomy.json"),
        "related_work_seed": _read_artifact(reports / "paper_related_work_seed.json"),
        "dataset_registry": _read_artifact(reports / "paper_dataset_registry.json"),
        "split_contracts": _read_artifact(reports / "paper_split_contracts.json"),
        "p8d_decision": _read_artifact(reports / "paper_p8d_thesis_decision.json"),
        "p8d_evidence_roles": _read_artifact(reports / "paper_p8d_evidence_role_matrix.json"),
        "p10_result_table": _read_artifact(reports / "paper_result_table_final.json"),
        "p10_table_provenance": _read_artifact(reports / "paper_table_provenance.json"),
        "p10_metric_audit": _read_artifact(reports / "paper_metric_cell_audit.json"),
        "p10_publishability": _read_artifact(reports / "paper_publishability_matrix.json"),
        "p10_reproduction_commands": _read_text_artifact(reports / "paper_reproduction_commands.md"),
        "p9_operational_guard": _read_artifact(reports / "paper_operational_claim_guard.json"),
        "elliptic2_repeated": _read_artifact(reports / "elliptic2_repeated_seed_scorecard.json"),
        "elliptic2_reference_parity": _read_artifact(reports / "elliptic2_reference_parity_gate.json"),
    }


def _build_limitations_matrix(inputs: dict[str, Any]) -> dict[str, Any]:
    publishability = _payload(inputs["p10_publishability"])
    p8d = _payload(inputs["p8d_decision"])
    p9_guard = _payload(inputs["p9_operational_guard"])
    rows = publishability.get("rows", []) if isinstance(publishability.get("rows"), list) else []
    row_by_dataset = {str(row.get("dataset_id")): dict(row) for row in rows if isinstance(row, dict)}

    limitations = [
        _limitation(
            "LIM-01-paysim-proxy",
            "PaySim is synthetic mobile-money fraud evidence. It is useful for a temporal proxy workflow, but it is not real-bank AML superiority evidence.",
            dataset_id="paysim_temporal_transaction_fraud",
            affected_claims=["claim_paysim_temporal_transaction_fraud", "claim_sota_or_hard_aml_superiority"],
            evidence_refs=["docs/reports/paysim_publishability_gate.json", "docs/reports/paper_dataset_registry.json"],
            blocked_reason_codes=row_by_dataset.get("paysim_temporal_transaction_fraud", {}).get("blocked_reason_codes", []),
            required_repair="Add a real financial-crime holdout or partner-approved private evaluation before making hard AML claims.",
        ),
        _limitation(
            "LIM-02-elliptic-supporting-graph",
            "The Elliptic row is a supporting temporal graph-feature result. It does not prove graph-neural or graph benchmark superiority.",
            dataset_id="elliptic_flattened_graph_aml",
            affected_claims=["claim_elliptic_flattened_graph_aml", "claim_sota_or_hard_aml_superiority"],
            evidence_refs=["docs/reports/paper_graph_publishability_gate.json", "docs/reports/paper_graph_model_shadow_scorecard.json"],
            blocked_reason_codes=row_by_dataset.get("elliptic_flattened_graph_aml", {}).get("blocked_reason_codes", []),
            required_repair="Run repeated-seed graph baselines and promote a graph-native candidate only if it beats strong feature baselines under the same split.",
        ),
        _limitation(
            "LIM-03-elliptic2-context-only",
            "Elliptic2 is retained as modern context and limitation evidence only; it is not a Relaytic performance contribution in this paper.",
            dataset_id="elliptic2_subgraph_aml",
            affected_claims=["claim_subgraph_or_synthetic_bank_graph", "claim_sota_or_hard_aml_superiority"],
            evidence_refs=[
                "docs/reports/elliptic2_publishability_gate.json",
                "docs/reports/elliptic2_reference_parity_gate.json",
                "docs/reports/paper_p8d_thesis_decision.json",
            ],
            blocked_reason_codes=_merge_reason_codes(
                row_by_dataset.get("elliptic2_subgraph_aml", {}),
                _payload(inputs["elliptic2_reference_parity"]),
            ),
            required_repair="Reproduce the RevClassify reference setup faithfully or define a new leakage-resistant subgraph protocol with viable cohort proof.",
        ),
        _limitation(
            "LIM-04-operational-assumptions",
            "Operational review-budget rows are supporting estimates because aggregate case packets, same-queue incumbent comparisons, and analyst-hour assumptions are not fully frozen.",
            dataset_id="paper_operational_layer",
            affected_claims=["claim_release_freeze_pack_exists"],
            evidence_refs=["docs/reports/paper_operational_claim_guard.json", "docs/reports/paper_case_packet_completeness_report.json"],
            blocked_reason_codes=p9_guard.get("blocked_reason_codes", []),
            required_repair="Freeze case-packet completeness and compare against the same review queue or an approved incumbent baseline.",
        ),
        _limitation(
            "LIM-05-clean-clone-pending",
            "The first draft is generated from committed evidence, but P12 must still prove clean-clone install, paper-smoke reproduction, leak scan, and claim lint.",
            dataset_id="paper_reproducibility_path",
            affected_claims=["claim_release_freeze_pack_exists"],
            evidence_refs=["docs/reports/paper_metric_cell_audit.json", "docs/reports/paper_table_provenance.json"],
            blocked_reason_codes=["external_dry_run_not_yet_executed_p12_required"],
            required_repair="Run Paper Track P12 from a clean clone and record the external dry-run report before arXiv release.",
        ),
    ]
    hard_allowed = bool(publishability.get("hard_claims_allowed")) or bool(p8d.get("hard_aml_claim_allowed"))
    headline_allowed = bool(publishability.get("headline_claims_allowed")) or bool(p8d.get("headline_or_sota_claim_allowed"))
    return {
        "schema_version": PAPER_DRAFT_SCHEMA_VERSION,
        "slice": "Paper Track P11",
        "status": "limitations_materialized_claims_guarded",
        "hard_claims_allowed": hard_allowed,
        "headline_claims_allowed": headline_allowed,
        "limitation_count": len(limitations),
        "limitations": limitations,
        "paper_must_state": [
            "No hard real-world AML superiority claim is allowed in the first draft.",
            "No SOTA, claimed equivalence to RevClassify, graph-neural superiority, or business-value headline claim is allowed.",
            "PaySim and Elliptic numbers may be used as supporting evidence only.",
            "Elliptic2 numbers may be used only as modern context and limitation evidence.",
            "P12 clean-clone proof remains required before public release.",
        ],
        "next_slice": "Paper Track P12 - external dry run and clean-clone proof",
    }


def _build_figure_pack(inputs: dict[str, Any]) -> dict[str, Any]:
    cells = _audit_cells(inputs)
    manifest_figures = [
        {
            "figure_id": "claim_gate_flow",
            "filename": PAPER_FIGURE_FILENAMES["claim_gate_flow"],
            "title": (
                "Relaytic-AML local evidence loop. Specialist roles write local artifacts; "
                "external handoff is rowless by default and claim gates fail closed."
            ),
            "source_type": "schematic_explicit",
            "source_refs": [
                "docs/reports/paper_thesis_contract.json",
                "docs/reports/paper_table_provenance.json",
                "docs/reports/paper_publishability_matrix.json",
            ],
            "paper_claim_role": "method_schematic_not_performance_evidence",
        },
        {
            "figure_id": "supporting_pr_auc",
            "filename": PAPER_FIGURE_FILENAMES["supporting_pr_auc"],
            "title": (
                "PR-AUC evidence rows. PaySim improves under the synthetic temporal proxy, "
                "while Elliptic2 remains below the RevClassifyDS reference and is not a parity claim."
            ),
            "source_type": "artifact_generated",
            "source_refs": ["docs/reports/paper_metric_cell_audit.json", "docs/reports/paper_result_table_final.json"],
            "paper_claim_role": "supporting_numeric_evidence_only",
        },
        {
            "figure_id": "review_budget",
            "filename": PAPER_FIGURE_FILENAMES["review_budget"],
            "title": (
                "Review-budget operating points. High top-queue precision with lower recall shows useful "
                "but incomplete analyst coverage under a bounded review budget."
            ),
            "source_type": "artifact_generated",
            "source_refs": ["docs/reports/paper_operational_metric_table.json", "docs/reports/paper_metric_cell_audit.json"],
            "paper_claim_role": "supporting_operational_evidence_only",
        },
        {
            "figure_id": "publishability_matrix",
            "filename": PAPER_FIGURE_FILENAMES["publishability_matrix"],
            "title": (
                "Claim boundary ladder. Current evidence is preserved while stronger AML, graph-neural, "
                "RevClassify-parity, and business-value claims remain blocked."
            ),
            "source_type": "artifact_generated",
            "source_refs": ["docs/reports/paper_publishability_matrix.json"],
            "paper_claim_role": "claim_gate_evidence",
        },
    ]
    manifest = {
        "schema_version": PAPER_DRAFT_SCHEMA_VERSION,
        "slice": "Paper Track P11",
        "status": "figures_generated",
        "figure_dir": "docs/paper/figures",
        "figures": manifest_figures,
    }
    return {
        "manifest": manifest,
        "svg": {
            "claim_gate_flow": _claim_gate_flow_svg(),
            "supporting_pr_auc": _supporting_pr_auc_svg(cells),
            "review_budget": _review_budget_svg(cells),
            "publishability_matrix": _publishability_matrix_svg(_payload(inputs["p10_publishability"])),
        },
    }


def _render_paper_draft(
    *,
    inputs: dict[str, Any],
    limitations: dict[str, Any],
    figure_manifest: dict[str, Any],
) -> str:
    thesis = _payload(inputs["thesis_contract"])
    claim_taxonomy = _payload(inputs["claim_taxonomy"])
    table = _payload(inputs["p10_result_table"])
    publishability = _payload(inputs["p10_publishability"])
    cells = _audit_cells(inputs)
    related = _payload(inputs["related_work_seed"])

    title = thesis.get("paper_title") or "Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML"
    key = _key_metric_lookup(cells)
    related_sources = _render_related_work_sources(related)
    benchmark_rows = _render_benchmark_rows(table)
    results_table = _render_results_table(key)
    limitations_text = _render_limitations_section(limitations)
    reproduction_commands = _payload_text(inputs["p10_reproduction_commands"])
    if not reproduction_commands:
        reproduction_commands = "relaytic release-safety paper-tables --format json\nrelaytic release-safety paper-draft --format json\n"

    figure_lines = [
        f"![{fig['title']}](figures/{fig['filename']})"
        for fig in figure_manifest.get("figures", [])
        if isinstance(fig, dict)
    ]
    allowed_claims = [
        str(claim.get("claim_id"))
        for claim in claim_taxonomy.get("claims", [])
        if isinstance(claim, dict) and claim.get("boundary") != "blocked"
    ]

    return "\n".join(
        [
            f"# {title}",
            "",
            "Source-draft status: generated evidence draft used by the release pipeline. For reader-facing review, use `docs/paper/relaytic_aml_arxiv_draft.md`.",
            "",
            "## Abstract",
            "",
            "Financial-crime machine learning is often evaluated through isolated model scores, while the operational question involves temporal validity, graph provenance, review capacity, case evidence, and public claim discipline. Relaytic-AML is a local-first evaluation environment that binds each benchmark row to a dataset registry, split contract, command, artifact path, leakage posture, budget tier, and publishability gate. In the current evidence pack, PaySim synthetic temporal-fraud and Elliptic temporal graph results are supporting rows, not headline superiority claims. The PaySim competitive row reports test PR-AUC "
            f"{_metric_value(key, 'paysim_p6a_competitive_selected.test_pr_auc')} and the Elliptic graph-feature row reports test PR-AUC "
            f"{_metric_value(key, 'elliptic_p7_selected_graph_feature_baseline.test_pr_auc')}; both are explicitly claim-guarded. Elliptic2 subgraph evidence is retained as modern context and limitation evidence only because reference-parity and cohort gates remain unresolved. The contribution is an auditable environment for claim-safe AML evaluation, not a detector-superiority claim.",
            "",
            "## Introduction",
            "",
            "AML and fraud detection systems are rare-event decision systems, not only classifiers. A model can look strong under a single metric while still being unusable if the split leaks future information, if graph evidence is flattened into an overbroad claim, if review capacity is ignored, or if paper text drifts beyond what the benchmark actually proves. Relaytic-AML treats those failure modes as first-class evaluation objects.",
            "",
            "This source draft argues for a claim-gated evaluation environment. Each numeric cell in the result table is tied to a command, dataset, split, run-directory reference, artifact field, budget tier, leakage posture, and claim state. Public claims are allowed only when the evidence pack and publishability gates agree. The current package allows supporting evidence claims and blocks hard AML, headline performance, and hard business-value claims.",
            "",
            "The paper therefore asks whether a local artifact system can make AML evaluation more credible by keeping model score, temporal correctness, graph provenance, operational review utility, and public claim boundaries inspectable together.",
            "",
            "## Related Work",
            "",
            "Relaytic-AML sits between AML benchmark papers, synthetic financial-crime data, modern tabular and graph baselines, and research reproducibility work. The related-work seed is intentionally artifact-backed so the paper can be refreshed without turning literature context into unsupported authority.",
            "",
            related_sources,
            "",
            "## Method",
            "",
            "Relaytic-AML is organized as a local evidence pipeline rather than a single model family. The pipeline records a dataset registry and split contracts, runs benchmark-specific evidence builders, materializes operational review-budget rows, generates paper tables from artifacts, and then lints draft claims against the claim taxonomy and publishability matrix.",
            "",
            "The method has four claim-control rules:",
            "",
            "1. Proxy, graph, subgraph, and synthetic-bank tracks keep separate claim boundaries.",
            "2. Validation selects models, thresholds, and operating points before fixed test evaluation.",
            "3. Numeric paper cells must cite machine-readable provenance rather than handwritten notes.",
            "4. Blocked tracks stay visible as limitations instead of being replaced by easier evidence.",
            "",
            "\n\n".join(figure_lines),
            "",
            "## Benchmarks",
            "",
            benchmark_rows,
            "",
            "## Results",
            "",
            "The current result table is intentionally supporting-only. It is useful because it shows where Relaytic-AML can produce leakage-aware, operationally annotated evidence, and where it refuses to overclaim.",
            "",
            results_table,
            "",
            "The PaySim competitive result improved over the PaySim baseline under the recorded temporal proxy contract, but PaySim remains synthetic. The Elliptic graph-feature result is credible supporting graph evidence, but it does not promote a graph-neural claim. The Elliptic2 context row shows a strong reproduced local candidate relative to many ordinary baselines, yet it remains below the recorded RevClassifyDS reference and cannot support a parity or headline detector claim in this source draft.",
            "",
            "## Limitations",
            "",
            limitations_text,
            "",
            "## Reproducibility Appendix",
            "",
            "The draft, figures, tables, limitations matrix, and claim-lint report are generated from local artifacts. The core P10 command sequence is:",
            "",
            reproduction_commands.rstrip(),
            "",
            "The P11 generation command is:",
            "",
            "```powershell",
            "relaytic release-safety paper-draft --format json",
            "```",
            "",
            "Important artifact references:",
            "",
            "- `docs/reports/paper_result_table_final.json`",
            "- `docs/reports/paper_table_provenance.json`",
            "- `docs/reports/paper_metric_cell_audit.json`",
            "- `docs/reports/paper_publishability_matrix.json`",
            "- `docs/reports/paper_claim_lint_report.json`",
            "- `docs/reports/paper_limitations_matrix.json`",
            "",
            f"Allowed non-blocked claim IDs in this draft: {', '.join(allowed_claims) if allowed_claims else 'none recorded'}.",
            f"Hard claims allowed by the P10/P11 gates: {bool(publishability.get('hard_claims_allowed'))}.",
            f"Headline claims allowed by the P10/P11 gates: {bool(publishability.get('headline_claims_allowed'))}.",
            "",
        ]
    ).rstrip() + "\n"


def _build_claim_lint_report(
    *,
    inputs: dict[str, Any],
    draft: str,
    limitations: dict[str, Any],
    figure_manifest: dict[str, Any],
) -> dict[str, Any]:
    publishability = _payload(inputs["p10_publishability"])
    audit = _payload(inputs["p10_metric_audit"])
    known_cell_ids = {str(cell.get("cell_id")) for cell in _audit_cells(inputs)}
    referenced_cell_ids = set(re.findall(r"paper-cell:([A-Za-z0-9_.-]+)", draft))
    limitation_ids = [str(item.get("limitation_id")) for item in limitations.get("limitations", []) if isinstance(item, dict)]

    checks = []
    violations: list[dict[str, Any]] = []
    checks.append(_check("p10_metric_audit_passes", audit.get("status") == "pass", "P10 metric cell audit must pass."))
    checks.append(_check("p10_allows_p11", bool(audit.get("paper_can_continue_to_p11")), "P10 must allow P11 drafting."))

    required_sections = ["Abstract", "Introduction", "Related Work", "Method", "Benchmarks", "Results", "Limitations", "Reproducibility Appendix"]
    for section in required_sections:
        passed = f"## {section}" in draft
        checks.append(_check(f"section_{_slug(section)}", passed, f"Draft must contain section `{section}`."))

    for cell_id in referenced_cell_ids:
        if cell_id not in known_cell_ids:
            violations.append(
                {
                    "rule_id": "unknown_metric_cell_ref",
                    "severity": "error",
                    "message": f"Draft references unknown metric cell `{cell_id}`.",
                }
            )
    checks.append(
        _check(
            "metric_cell_refs_known",
            bool(referenced_cell_ids) and all(cell_id in known_cell_ids for cell_id in referenced_cell_ids),
            "Every paper-cell reference must exist in P10 metric-cell audit.",
        )
    )

    missing_limitations = [limitation_id for limitation_id in limitation_ids if limitation_id not in draft]
    checks.append(
        _check(
            "limitations_covered",
            not missing_limitations,
            "Every limitations-matrix row must be named in the draft limitations section.",
            detail={"missing_limitations": missing_limitations},
        )
    )

    forbidden_violations = []
    for rule in _forbidden_claim_rules():
        unguarded = _unguarded_phrase_hits(draft, rule["phrase"])
        if unguarded:
            forbidden_violations.append(
                {
                    "rule_id": rule["rule_id"],
                    "severity": "error",
                    "phrase": rule["phrase"],
                    "matches": unguarded,
                    "message": rule["message"],
                }
            )
    violations.extend(forbidden_violations)
    checks.append(
        _check(
            "blocked_claim_language_guarded",
            not forbidden_violations,
            "No unguarded blocked claim language may appear.",
        )
    )

    figure_errors = []
    for fig in figure_manifest.get("figures", []):
        if not isinstance(fig, dict):
            figure_errors.append({"figure": fig, "reason": "figure_manifest_entry_not_object"})
            continue
        if fig.get("source_type") not in {"artifact_generated", "schematic_explicit"}:
            figure_errors.append({"figure_id": fig.get("figure_id"), "reason": "invalid_source_type"})
        if not fig.get("source_refs"):
            figure_errors.append({"figure_id": fig.get("figure_id"), "reason": "missing_source_refs"})
    checks.append(
        _check(
            "figures_generated_or_schematic",
            not figure_errors,
            "Figures must be artifact-generated or explicitly schematic, with source references.",
            detail={"figure_errors": figure_errors},
        )
    )

    missing_input_refs = [
        item["artifact_ref"]
        for item in inputs.values()
        if isinstance(item, dict) and not item.get("exists") and item.get("artifact_ref") in {
            "docs/reports/paper_result_table_final.json",
            "docs/reports/paper_metric_cell_audit.json",
            "docs/reports/paper_publishability_matrix.json",
            "docs/reports/paper_table_provenance.json",
        }
    ]
    checks.append(
        _check(
            "required_p10_inputs_present",
            not missing_input_refs,
            "Required P10 draft inputs must exist.",
            detail={"missing_input_refs": missing_input_refs},
        )
    )

    for check in checks:
        if not check["passed"]:
            violations.append(
                {
                    "rule_id": check["check_id"],
                    "severity": "error",
                    "message": check["message"],
                    "detail": check.get("detail", {}),
                }
            )

    hard_allowed = bool(publishability.get("hard_claims_allowed"))
    headline_allowed = bool(publishability.get("headline_claims_allowed"))
    status = "pass" if not violations else "fail"
    return {
        "schema_version": PAPER_DRAFT_SCHEMA_VERSION,
        "slice": "Paper Track P11",
        "status": status,
        "paper_can_continue_to_p12": status == "pass",
        "hard_claims_allowed": hard_allowed,
        "headline_claims_allowed": headline_allowed,
        "draft_ref": "docs/paper/relaytic_aml_draft.md",
        "figure_manifest_ref": "docs/paper/figures/figure_manifest.json",
        "claim_contract_refs": [
            "docs/reports/paper_thesis_contract.json",
            "docs/reports/paper_claim_taxonomy.json",
            "docs/reports/paper_publishability_matrix.json",
        ],
        "metric_cell_ref_count": len(referenced_cell_ids),
        "known_metric_cell_count": len(known_cell_ids),
        "limitation_count": len(limitation_ids),
        "checks": checks,
        "violations": violations,
        "next_slice": "Paper Track P12 - external dry run and clean-clone proof" if status == "pass" else "Paper Track P11 follow-up",
    }


def _render_related_work_sources(related: dict[str, Any]) -> str:
    sources = [item for item in related.get("sources", []) if isinstance(item, dict)]
    if not sources:
        return "No related-work seed artifacts were available."
    lines = ["| Source | Role in this paper |", "|---|---|"]
    for source in sources:
        title = _escape_md(str(source.get("title") or source.get("source_id") or "source"))
        role = _escape_md(str(source.get("paper_relevance") or source.get("topic") or "context"))
        url = str(source.get("url") or "")
        label = f"[{title}]({url})" if url else title
        lines.append(f"| {label} | {role} |")
    return "\n".join(lines)


def _render_benchmark_rows(table: dict[str, Any]) -> str:
    rows = _all_table_rows(table)
    if not rows:
        return "No P10 benchmark rows were available; this draft is blocked until table generation succeeds."
    lines = ["| Track | Role | Budget | Claim state | Gate |", "|---|---|---|---|---|"]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(row.get("dataset_display_name") or row.get("dataset_id") or "unknown")),
                    _escape_md(str(row.get("evidence_role") or "supporting")),
                    _escape_md(str(row.get("budget_tier") or "unknown")),
                    _escape_md(str(row.get("claim_state") or "unknown")),
                    _escape_md(str(row.get("publishability_gate_status") or "unknown")),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def _render_results_table(key: dict[str, dict[str, Any]]) -> str:
    rows = [
        ("PaySim baseline", "paysim_p6_validation_selected_baseline.test_pr_auc", "test PR-AUC", "baseline-only"),
        ("PaySim competitive", "paysim_p6a_competitive_selected.test_pr_auc", "test PR-AUC", "supporting-only"),
        ("PaySim competitive", "paysim_p6a_competitive_selected.precision_at_review_budget", "precision at review budget", "supporting-only"),
        ("PaySim competitive", "paysim_p6a_competitive_selected.recall_at_review_budget", "recall at review budget", "supporting-only"),
        ("Elliptic graph-feature", "elliptic_p7_selected_graph_feature_baseline.test_pr_auc", "test PR-AUC", "supporting-only"),
        ("Elliptic graph-feature", "elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget", "precision at review budget", "supporting-only"),
        ("Elliptic2 context", "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean", "official-partition PR-AUC mean", "modern context only"),
        ("Elliptic2 context", "elliptic2_p8b_modern_context.published_reference_pr_auc", "published RevClassifyDS PR-AUC", "reference context"),
    ]
    lines = ["| Evidence row | Metric | Value | Claim posture | Provenance |", "|---|---:|---:|---|---|"]
    for label, cell_id, metric, claim in rows:
        value = _metric_value(key, cell_id)
        lines.append(
            f"| {_escape_md(label)} | {_escape_md(metric)} | {value} | {_escape_md(claim)} | `paper-cell:{cell_id}` |"
        )
    return "\n".join(lines)


def _render_limitations_section(limitations: dict[str, Any]) -> str:
    rows = limitations.get("limitations", []) if isinstance(limitations.get("limitations"), list) else []
    lines = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"- **{row.get('limitation_id')}**: {row.get('limitation_text')} Required repair: {row.get('required_repair')}"
        )
    return "\n".join(lines) if lines else "No limitations matrix was available."


def _claim_gate_flow_svg() -> str:
    agent_boxes = [
        ("Operator", 55, "#edf6f9"),
        ("Guide", 205, "#edf6f9"),
        ("Scout", 355, "#f7f4ea"),
        ("Science", 505, "#f7f4ea"),
        ("Builder", 655, "#eef4ff"),
        ("Review", 805, "#fdeeee"),
    ]
    artifact_boxes = [
        ("Mandate", 55, "#ffffff"),
        ("Status", 205, "#ffffff"),
        ("Split", 355, "#ffffff"),
        ("Ablations", 505, "#ffffff"),
        ("Model", 655, "#ffffff"),
        ("Claims", 805, "#ffffff"),
    ]
    parts = [
        _svg_header(980, 480),
        '<rect x="30" y="28" width="920" height="394" rx="8" fill="#fbfcfe" stroke="#8d99ae" stroke-width="1.7"/>',
        '<text x="55" y="66" font-size="21" font-weight="700" fill="#293241">Workspace authority and evidence flow</text>',
        '<text x="55" y="96" font-size="18" fill="#5b6472">Specialist roles create local artifacts. Optional LLM help is redacted advice, not truth.</text>',
        '<line x1="55" y1="119" x2="925" y2="119" stroke="#d7dde8" stroke-width="1.4"/>',
    ]
    for label, x, fill in agent_boxes:
        parts.append(f'<rect x="{x}" y="145" width="132" height="76" rx="7" fill="{fill}" stroke="#293241" stroke-width="1.5"/>')
        parts.extend(_svg_text_lines(label, x + 66, 191, font_size=20, anchor="middle", line_height=22))
    for label, x, fill in artifact_boxes:
        parts.append(f'<rect x="{x}" y="260" width="132" height="66" rx="7" fill="{fill}" stroke="#8d99ae" stroke-width="1.25"/>')
        parts.extend(_svg_text_lines(label, x + 66, 300, font_size=18, anchor="middle", line_height=20))
    for x in [121, 271, 421, 571, 721, 871]:
        parts.append(f'<line x1="{x}" y1="221" x2="{x}" y2="260" stroke="#293241" stroke-width="1.5"/>')
        parts.append(f'<polygon points="{x},260 {x - 7},249 {x + 7},249" fill="#293241"/>')
    for x1, x2 in [(187, 205), (337, 355), (487, 505), (637, 655), (787, 805)]:
        parts.append(f'<line x1="{x1}" y1="183" x2="{x2}" y2="183" stroke="#293241" stroke-width="1.5"/>')
        parts.append(f'<polygon points="{x2},183 {x2 - 10},176 {x2 - 10},190" fill="#293241"/>')
    parts.append('<rect x="55" y="354" width="280" height="36" rx="6" fill="#eef4ff" stroke="#8d99ae" stroke-width="1.0"/>')
    parts.append('<text x="195" y="378" text-anchor="middle" font-size="17" fill="#293241">Canonical artifact graph</text>')
    parts.append('<rect x="350" y="354" width="280" height="36" rx="6" fill="#edf6f9" stroke="#8d99ae" stroke-width="1.0"/>')
    parts.append('<text x="490" y="378" text-anchor="middle" font-size="17" fill="#293241">Rowless external handoff</text>')
    parts.append('<rect x="645" y="354" width="280" height="36" rx="6" fill="#fdeeee" stroke="#8d99ae" stroke-width="1.0"/>')
    parts.append('<text x="785" y="378" text-anchor="middle" font-size="17" fill="#293241">Claim gates fail closed</text>')
    parts.append('<text x="30" y="454" font-size="17" fill="#5b6472">Benchmarks exercise this architecture; they do not replace the local-first artifact and claim-control thesis.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _supporting_pr_auc_svg(cells: list[dict[str, Any]]) -> str:
    values = [
        ("PaySim baseline", _cell_value(cells, "paysim_p6_validation_selected_baseline.test_pr_auc"), "#8d99ae"),
        ("PaySim competitive", _cell_value(cells, "paysim_p6a_competitive_selected.test_pr_auc"), "#2a9d8f"),
        ("Elliptic graph", _cell_value(cells, "elliptic_p7_selected_graph_feature_baseline.test_pr_auc"), "#457b9d"),
        ("Elliptic2 context", _cell_value(cells, "elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean"), "#e9c46a"),
        ("RevClassifyDS ref", _cell_value(cells, "elliptic2_p8b_modern_context.published_reference_pr_auc"), "#e76f51"),
    ]
    return _bar_chart_svg(
        title="PR-AUC evidence rows",
        ylabel="PR-AUC",
        values=values,
        width=940,
        height=430,
    )


def _review_budget_svg(cells: list[dict[str, Any]]) -> str:
    values = [
        ("PaySim precision", _cell_value(cells, "paysim_p6a_competitive_selected.precision_at_review_budget"), "#2a9d8f"),
        ("PaySim recall", _cell_value(cells, "paysim_p6a_competitive_selected.recall_at_review_budget"), "#80b918"),
        ("Elliptic precision", _cell_value(cells, "elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget"), "#457b9d"),
        ("Elliptic recall", _cell_value(cells, "elliptic_p7_selected_graph_feature_baseline.recall_at_review_budget"), "#f4a261"),
    ]
    return _bar_chart_svg(
        title="Review-budget operating points",
        ylabel="score",
        values=values,
        width=880,
        height=410,
    )


def _publishability_matrix_svg(publishability: dict[str, Any]) -> str:
    _ = publishability
    rows = [
        ("PaySim", "current: synthetic temporal proxy", "blocked: real-bank superiority", "unlock: partner/real holdout"),
        ("Elliptic", "current: temporal graph features", "blocked: graph-neural superiority", "unlock: repeated graph release budget"),
        ("Elliptic2", "current: modern subgraph context", "blocked: RevClassify parity", "unlock: faithful parity + cohort proof"),
        ("Operational", "current: review-budget support", "blocked: hard business value", "unlock: same-queue incumbent"),
    ]
    width = 1040
    height = 440
    parts = [
        _svg_header(width, height),
        '<text x="30" y="38" font-size="17" fill="#5b6472">Rows can be useful evidence while still failing stronger claim gates.</text>',
        '<line x1="185" y1="92" x2="905" y2="92" stroke="#d7dde8" stroke-width="2"/>',
        '<text x="185" y="72" text-anchor="middle" font-size="15" font-weight="700" fill="#293241">current evidence</text>',
        '<text x="545" y="72" text-anchor="middle" font-size="15" font-weight="700" fill="#293241">blocked claim</text>',
        '<text x="905" y="72" text-anchor="middle" font-size="15" font-weight="700" fill="#293241">evidence needed</text>',
    ]
    for index, (track, current, blocked, unlock) in enumerate(rows):
        y = 120 + index * 70
        parts.append(f'<text x="50" y="{y + 6}" font-size="18" font-weight="700" fill="#293241">{_xml_escape(track)}</text>')
        parts.append(f'<circle cx="185" cy="{y}" r="10" fill="#2a9d8f"/>')
        parts.append(f'<circle cx="545" cy="{y}" r="10" fill="#c94c4c"/>')
        parts.append(f'<circle cx="905" cy="{y}" r="10" fill="#457b9d"/>')
        parts.append(f'<line x1="195" y1="{y}" x2="535" y2="{y}" stroke="#d7dde8" stroke-width="2"/>')
        parts.append(f'<line x1="555" y1="{y}" x2="895" y2="{y}" stroke="#d7dde8" stroke-width="2" stroke-dasharray="6 6"/>')
        parts.extend(_svg_text_lines(current, 185, y + 29, font_size=14, anchor="middle", line_height=16))
        parts.extend(_svg_text_lines(blocked, 545, y + 29, font_size=14, anchor="middle", line_height=16, fill="#8a3434"))
        parts.extend(_svg_text_lines(unlock, 905, y + 29, font_size=14, anchor="middle", line_height=16))
    parts.append('<rect x="44" y="394" width="952" height="28" rx="6" fill="#fbfcfe" stroke="#d7dde8" stroke-width="1"/>')
    parts.append('<text x="520" y="413" text-anchor="middle" font-size="15" fill="#5b6472">The gate preserves useful evidence while preventing unsupported promotion.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _bar_chart_svg(
    *,
    title: str,
    ylabel: str,
    values: list[tuple[str, Any, str]],
    width: int,
    height: int,
) -> str:
    plot_x = 76
    plot_y = 58
    plot_w = width - 122
    plot_h = height - 162
    clean_values = [(label, float(value) if isinstance(value, (int, float)) else 0.0, color) for label, value, color in values]
    max_value = max([1.0] + [value for _, value, _ in clean_values])
    bar_w = max(38, int(plot_w / max(1, len(clean_values)) * 0.58))
    gap = (plot_w - bar_w * len(clean_values)) / max(1, len(clean_values))
    parts = [
        _svg_header(width, height),
        f'<line x1="{plot_x}" y1="{plot_y + plot_h}" x2="{plot_x + plot_w}" y2="{plot_y + plot_h}" stroke="#293241" stroke-width="1.2"/>',
        f'<line x1="{plot_x}" y1="{plot_y}" x2="{plot_x}" y2="{plot_y + plot_h}" stroke="#293241" stroke-width="1.2"/>',
        f'<text x="{plot_x}" y="{plot_y - 16}" font-size="16" fill="#293241">{_xml_escape(ylabel)}</text>',
        f'<line x1="{plot_x}" y1="{plot_y}" x2="{plot_x + plot_w}" y2="{plot_y}" stroke="#d7dde8" stroke-width="0.8"/>',
        f'<line x1="{plot_x}" y1="{plot_y + plot_h / 2:.1f}" x2="{plot_x + plot_w}" y2="{plot_y + plot_h / 2:.1f}" stroke="#e4e8f0" stroke-width="0.8"/>',
    ]
    for index, (label, value, color) in enumerate(clean_values):
        x = plot_x + gap / 2 + index * (bar_w + gap)
        bar_h = 0 if max_value == 0 else (value / max_value) * plot_h
        y = plot_y + plot_h - bar_h
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" fill="{color}"/>')
        parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" font-size="16">{_format_metric(value)}</text>')
        parts.extend(_svg_text_lines(label.replace(" ", "\n", 1), x + bar_w / 2, plot_y + plot_h + 32, font_size=14, anchor="middle", line_height=17))
    parts.append('<text x="30" y="{0}" font-size="17" fill="#5b6472">Values come from fixed local evidence cells; rows are supporting evidence, not headline claims.</text>'.format(height - 24))
    parts.append("</svg>")
    return "\n".join(parts)


def _limitation(
    limitation_id: str,
    limitation_text: str,
    *,
    dataset_id: str,
    affected_claims: list[str],
    evidence_refs: list[str],
    blocked_reason_codes: Any,
    required_repair: str,
) -> dict[str, Any]:
    return {
        "limitation_id": limitation_id,
        "dataset_id": dataset_id,
        "limitation_text": limitation_text,
        "affected_claims": affected_claims,
        "evidence_refs": evidence_refs,
        "blocked_reason_codes": _as_list(blocked_reason_codes),
        "claim_effect": "blocks_headline_or_hard_claims",
        "required_repair": required_repair,
        "paper_section": "Limitations",
    }


def _forbidden_claim_rules() -> list[dict[str, str]]:
    return [
        {
            "rule_id": "unguarded_sota_claim",
            "phrase": "SOTA",
            "message": "SOTA language is allowed only when explicitly blocked or negated.",
        },
        {
            "rule_id": "unguarded_state_of_the_art_claim",
            "phrase": "state-of-the-art",
            "message": "State-of-the-art language is allowed only when explicitly blocked or negated.",
        },
        {
            "rule_id": "unguarded_hard_aml_superiority",
            "phrase": "hard real-world AML superiority",
            "message": "Hard real-world AML superiority language must be blocked, not asserted.",
        },
        {
            "rule_id": "unguarded_revclassify_parity",
            "phrase": "RevClassify parity",
            "message": "RevClassify parity must remain blocked unless the reference-parity gate passes.",
        },
        {
            "rule_id": "unguarded_leaderboard_winner",
            "phrase": "leaderboard winner",
            "message": "The draft must not frame Relaytic-AML as a leaderboard winner.",
        },
    ]


def _unguarded_phrase_hits(text: str, phrase: str) -> list[dict[str, Any]]:
    hits = []
    lower = text.lower()
    target = phrase.lower()
    start = 0
    while True:
        index = lower.find(target, start)
        if index == -1:
            break
        window = lower[max(0, index - 140): min(len(lower), index + len(target) + 80)]
        guarded = any(
            token in window
            for token in [
                "blocked",
                "blocks",
                "not ",
                "not.",
                "no ",
                "without",
                "does not",
                "remain unresolved",
                "separate from",
            ]
        )
        if not guarded:
            hits.append({"offset": index, "excerpt": text[index: index + len(phrase)]})
        start = index + len(target)
    return hits


def _check(check_id: str, passed: bool, message: str, *, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {"check_id": check_id, "passed": bool(passed), "message": message}
    if detail is not None:
        payload["detail"] = detail
    return payload


def _key_metric_lookup(cells: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(cell.get("cell_id")): cell for cell in cells}


def _metric_value(key: dict[str, dict[str, Any]], cell_id: str) -> str:
    return _format_metric(key.get(cell_id, {}).get("value"))


def _cell_value(cells: list[dict[str, Any]], cell_id: str) -> Any:
    for cell in cells:
        if cell.get("cell_id") == cell_id:
            return cell.get("value")
    return None


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


def _audit_cells(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    audit = _payload(inputs["p10_metric_audit"])
    cells = audit.get("numeric_cells", [])
    return [dict(cell) for cell in cells if isinstance(cell, dict)]


def _all_table_rows(table: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in table.get("table_groups", []):
        if isinstance(group, dict):
            rows.extend([dict(row) for row in group.get("rows", []) if isinstance(row, dict)])
    return rows


def _merge_reason_codes(*payloads: dict[str, Any]) -> list[Any]:
    merged = []
    for payload in payloads:
        merged.extend(_as_list(payload.get("blocked_reason_codes")))
    seen = set()
    unique = []
    for item in merged:
        key = str(item)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


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


def _payload_text(artifact: dict[str, Any]) -> str:
    text = artifact.get("text", "")
    return str(text) if text is not None else ""


def _artifact_ref(path: Path) -> str:
    parts = path.parts
    if "docs" in parts:
        return Path(*parts[parts.index("docs"):]).as_posix()
    return path.as_posix()


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|")


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _svg_header(width: int, height: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        '<style>text{font-family:Arial,Helvetica,sans-serif;letter-spacing:0}</style>'
        '<rect width="100%" height="100%" fill="#ffffff"/>'
    )


def _svg_text_lines(
    text: str,
    x: float,
    y: float,
    *,
    font_size: int,
    anchor: str,
    line_height: int,
    fill: str = "#293241",
) -> list[str]:
    lines = [line.strip() for line in str(text).split("\n") if line.strip()]
    return [
        (
            f'<text x="{x:.1f}" y="{y + index * line_height:.1f}" '
            f'text-anchor="{anchor}" font-size="{font_size}" fill="{fill}">'
            f'{_xml_escape(line)}</text>'
        )
        for index, line in enumerate(lines)
    ]

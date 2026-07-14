"""Paper Track P18 governance-invariant and adjacent-systems reports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_INVARIANT_SCHEMA_VERSION = "relaytic.paper_invariants.v1"
PAPER_INVARIANT_REPORT_DIR = Path("docs") / "reports"
NEXT_PAPER_INVARIANT_SLICE = "Paper Track P19 - hosted detector workflow demonstration, if selected"

PAPER_INVARIANT_FILENAMES = {
    "paper_governance_invariants": "paper_governance_invariants.json",
    "paper_adjacent_systems_comparison": "paper_adjacent_systems_comparison.json",
    "paper_invariant_manifest": "paper_invariant_manifest.json",
    "paper_invariant_summary": "paper_invariant_summary.md",
}

REQUIRED_PAPER_INVARIANT_INPUT_REFS = [
    "docs/reports/paper_metric_cell_audit.json",
    "docs/reports/paper_public_claims_allowed.json",
    "docs/reports/paper_publishability_matrix.json",
    "docs/reports/paper_claim_lint_report.json",
    "docs/reports/paper_release_go_no_go.json",
    "docs/reports/paper_system_task_eval.json",
    "docs/reports/paper_agent_handoff_eval.json",
    "docs/reports/paper_no_lost_user_eval.json",
    "docs/reports/paper_failure_case_eval.json",
    "docs/reports/paper_governance_ablation_eval.json",
    "docs/reports/paper_governance_ablation_manifest.json",
    "docs/reports/paysim_leakage_safe_feature_report.json",
    "docs/reports/paysim_competitive_benchmark_manifest.json",
    "docs/paper/references.bib",
]

REQUIRED_ADJACENT_FAMILIES = [
    "Model cards and model reporting",
    "Datasheets and dataset documentation",
    "ML reproducibility checklists",
    "MLOps experiment tracking",
    "Agent benchmarks and research-agent evaluations",
    "AML detector and benchmark papers",
    "AML LLM graph reasoning and triage systems",
    "Agentic SAR and compliance narrative assistants",
    "Agent governance and runtime trust layers",
]


def build_paper_invariant_pack(project_root: str | Path) -> dict[str, Any]:
    """Build deterministic P18 invariant and adjacent-systems reports."""
    root = Path(project_root)
    inputs = _collect_inputs(root)
    invariant_rows = _build_invariant_rows(inputs)
    adjacent_rows = _build_adjacent_systems_rows(inputs)
    invariant_report = _build_invariant_report(inputs=inputs, rows=invariant_rows)
    adjacent_report = _build_adjacent_systems_report(inputs=inputs, rows=adjacent_rows)
    manifest = _build_manifest(
        inputs=inputs,
        invariant_report=invariant_report,
        adjacent_report=adjacent_report,
    )
    pack = {
        "paper_governance_invariants": invariant_report,
        "paper_adjacent_systems_comparison": adjacent_report,
        "paper_invariant_manifest": manifest,
    }
    pack["paper_invariant_summary"] = render_paper_invariant_markdown(pack)
    return pack


def sync_paper_invariant_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P18 invariant reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_INVARIANT_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_invariant_pack(root)
    written: dict[str, Path] = {}
    for key, filename in PAPER_INVARIANT_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_invariant_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_invariant_manifest", {}))
    invariant_report = dict(pack.get("paper_governance_invariants", {}))
    adjacent_report = dict(pack.get("paper_adjacent_systems_comparison", {}))
    lines = [
        "# Paper P18 Governance-Invariant Pack",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Invariant status: `{invariant_report.get('status') or 'unknown'}`",
        f"- Adjacent-systems status: `{adjacent_report.get('status') or 'unknown'}`",
        f"- Current invariant count: `{invariant_report.get('current_invariant_count') or 0}`",
        f"- Adjacent family count: `{adjacent_report.get('family_count') or 0}`",
        f"- Evidence-completeness check passed: `{invariant_report.get('proof_obligation_passed')}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        "",
        "## Governance Invariants",
        "",
        "| Invariant | Enforcement | Evidence | Boundary |",
        "| --- | --- | --- | --- |",
    ]
    for row in invariant_report.get("invariants", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(row.get("name") or row.get("invariant_id") or "unknown")),
                    _escape_md(str(row.get("enforcement_mechanism") or "")),
                    _escape_md(_short_evidence_refs(row.get("evidence_refs"))),
                    _escape_md(str(row.get("limitation_or_boundary") or "")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Adjacent Systems",
            "",
            "| Family | Primary object | Relaytic-AML position |",
            "| --- | --- | --- |",
        ]
    )
    for row in adjacent_report.get("comparison_rows", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(row.get("adjacent_family") or "")),
                    _escape_md(str(row.get("primary_object") or "")),
                    _escape_md(str(row.get("relaytic_aml_position") or "")),
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _collect_inputs(root: Path) -> dict[str, Any]:
    reports = root / PAPER_INVARIANT_REPORT_DIR
    paper = root / "docs" / "paper"
    return {
        "root": root,
        "metric_cell_audit": _read_artifact(reports / "paper_metric_cell_audit.json", root=root),
        "public_claims_allowed": _read_artifact(reports / "paper_public_claims_allowed.json", root=root),
        "publishability_matrix": _read_artifact(reports / "paper_publishability_matrix.json", root=root),
        "claim_lint": _read_artifact(reports / "paper_claim_lint_report.json", root=root),
        "release_go_no_go": _read_artifact(reports / "paper_release_go_no_go.json", root=root),
        "system_task_eval": _read_artifact(reports / "paper_system_task_eval.json", root=root),
        "agent_handoff_eval": _read_artifact(reports / "paper_agent_handoff_eval.json", root=root),
        "no_lost_user_eval": _read_artifact(reports / "paper_no_lost_user_eval.json", root=root),
        "failure_case_eval": _read_artifact(reports / "paper_failure_case_eval.json", root=root),
        "governance_ablation_eval": _read_artifact(reports / "paper_governance_ablation_eval.json", root=root),
        "governance_ablation_manifest": _read_artifact(reports / "paper_governance_ablation_manifest.json", root=root),
        "paysim_feature_report": _read_artifact(reports / "paysim_leakage_safe_feature_report.json", root=root),
        "paysim_competitive_manifest": _read_artifact(reports / "paysim_competitive_benchmark_manifest.json", root=root),
        "references": _read_text_artifact(paper / "references.bib", root=root),
    }


def _build_invariant_rows(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    task_signal = _task_signal_lookup(_payload(inputs["system_task_eval"]))
    failure_signal = _failure_signal_lookup(_payload(inputs["failure_case_eval"]))
    ablation_signal = _ablation_signal_lookup(_payload(inputs["governance_ablation_eval"]))
    claim_payload = _payload(inputs["public_claims_allowed"])
    publishability = _payload(inputs["publishability_matrix"])
    metric_audit = _payload(inputs["metric_cell_audit"])
    handoff = _payload(inputs["agent_handoff_eval"])
    recovery = _payload(inputs["no_lost_user_eval"])
    feature_report = _payload(inputs["paysim_feature_report"])
    paysim_competitive_manifest = _payload(inputs["paysim_competitive_manifest"])
    go_no_go = _payload(inputs["release_go_no_go"])
    claim_lint = _payload(inputs["claim_lint"])

    return [
        _invariant(
            invariant_id="I1_metric_cell_provenance",
            name="Evidence-cell provenance",
            statement="Every reader-facing number must resolve to factual dataset, split, command, artifact, metric, budget, leakage, operating-point, and exposure fields, while interpretation resolves through a separate claim gate.",
            enforcement_mechanism="evidence-cell audit plus required-field gate",
            evidence_refs=[
                _evidence_ref(
                    "docs/reports/paper_metric_cell_audit.json",
                    "all_numeric_cells_have_required_provenance",
                    _check_signal(metric_audit, "all_numeric_cells_have_required_provenance"),
                    requirement="numeric evidence cells contain the required provenance fields",
                ),
                _evidence_ref(
                    "docs/reports/paper_system_task_eval.json",
                    "metric_cell_provenance_available",
                    task_signal.get("metric_cell_provenance_available"),
                    requirement="reader task can trace the PaySim evidence cell",
                ),
            ],
            failure_or_ablation_refs=[
                _evidence_ref(
                    "docs/reports/paper_governance_ablation_eval.json",
                    "No evidence-cell required fields",
                    ablation_signal.get("No evidence-cell required fields"),
                    requirement="disabled required-field gate exposes missing provenance",
                )
            ],
            limitation_or_boundary="The invariant checks artifact completeness. It does not establish detector optimality.",
            paper_claim_allowed="The paper may claim audited provenance for reported metrics.",
            stronger_claim_blocked="Metric provenance alone does not justify detector superiority or production AML readiness.",
        ),
        _invariant(
            invariant_id="I2_claim_strength_monotonicity",
            name="Claim-strength monotonicity",
            statement="Public wording cannot become stronger than the evidence role, gate status, and missing-evidence record allow.",
            enforcement_mechanism="claim lint, allowed-claims report, publishability matrix, and overclaim failure case",
            evidence_refs=[
                _evidence_ref(
                    "docs/reports/paper_public_claims_allowed.json",
                    "claim_safe_public_wording_allowed",
                    str(claim_payload.get("status") or ""),
                    requirement="hard and headline claims remain blocked",
                ),
                _evidence_ref(
                    "docs/reports/paper_publishability_matrix.json",
                    "hard_headline_claims_blocked",
                    str(publishability.get("claim_boundary", "")) or _claim_boundary_signal(publishability),
                    requirement="benchmark rows carry bounded evidence roles",
                ),
            ],
            failure_or_ablation_refs=[
                _evidence_ref(
                    "docs/reports/paper_failure_case_eval.json",
                    "overstrong_claim_attempt",
                    failure_signal.get("overstrong_claim_attempt"),
                    requirement="over-strong claim fixture is blocked",
                ),
                _evidence_ref(
                    "docs/reports/paper_governance_ablation_eval.json",
                    "No claim gate",
                    ablation_signal.get("No claim gate"),
                    requirement="disabled claim gate releases unsupported claims",
                ),
            ],
            limitation_or_boundary="The gate is a deterministic release check; it is not an external peer review.",
            paper_claim_allowed="The paper may claim bounded public interpretation routing.",
            stronger_claim_blocked="Hard real-bank AML superiority, graph-neural superiority, and RevClassifyDS parity stay blocked.",
        ),
        _invariant(
            invariant_id="I3_leakage_and_selection_firewall",
            name="Leakage and selection firewall",
            statement="Leakage-prone fields and test-selection paths are checked before benchmark evidence is released.",
            enforcement_mechanism="feature policy report, split contract, failure fixtures, and leakage ablation",
            evidence_refs=[
                _evidence_ref(
                    "docs/reports/paysim_leakage_safe_feature_report.json",
                    "forbidden_balance_columns_used",
                    f"used={len(feature_report.get('forbidden_balance_columns_used', []) or [])}; labels_for_features={feature_report.get('validation_or_test_labels_used_for_features')}",
                    requirement="forbidden balance fields and validation/test labels are absent from features",
                ),
                _evidence_ref(
                    "docs/reports/paper_failure_case_eval.json",
                    "test_set_selection_violation",
                    failure_signal.get("test_set_selection_violation"),
                    requirement="test-selection fixture is blocked",
                ),
                _evidence_ref(
                    "docs/reports/paysim_competitive_benchmark_manifest.json",
                    "test_exposure_contract",
                    json.dumps(paysim_competitive_manifest.get("test_exposure_contract", {}), sort_keys=True),
                    requirement="validation-only competitive selection is recorded while earlier P4/P6 test exposure remains disclosed",
                ),
            ],
            failure_or_ablation_refs=[
                _evidence_ref(
                    "docs/reports/paper_failure_case_eval.json",
                    "leakage_column_injection",
                    failure_signal.get("leakage_column_injection"),
                    requirement="leakage-column fixture is blocked",
                ),
                _evidence_ref(
                    "docs/reports/paper_governance_ablation_eval.json",
                    "No leakage policy",
                    ablation_signal.get("No leakage policy"),
                    requirement="disabled leakage policy exposes forbidden fields",
                ),
            ],
            limitation_or_boundary="The current firewall is benchmark-specific; future datasets need their own leakage taxonomy.",
            paper_claim_allowed="The paper may claim leakage-audited PaySim feature construction and validation-only competitive selection with disclosed prior test exposure.",
            stronger_claim_blocked="No untouched-holdout, separate destination-history ablation, or real-bank deployment claim is supported.",
        ),
        _invariant(
            invariant_id="I4_rowless_external_handoff",
            name="Rowless external-agent handoff",
            statement="External handoff exposes state, safe actions, and artifact references without raw rows, secrets, or private paths.",
            enforcement_mechanism="handoff evaluator plus redaction failure case",
            evidence_refs=[
                _evidence_ref(
                    "docs/reports/paper_agent_handoff_eval.json",
                    "external_context_rowless_and_redacted",
                    _task_signal_lookup(handoff).get("external_context_rowless_and_redacted"),
                    requirement="handoff is rowless and redacted",
                ),
                _evidence_ref(
                    "docs/reports/paper_system_task_eval.json",
                    "rowless_external_agent_handoff_recoverable",
                    task_signal.get("rowless_external_agent_handoff_recoverable"),
                    requirement="external-agent task sees safe next actions and tool contracts",
                ),
            ],
            failure_or_ablation_refs=[
                _evidence_ref(
                    "docs/reports/paper_failure_case_eval.json",
                    "rowless_handoff_redaction",
                    failure_signal.get("rowless_handoff_redaction"),
                    requirement="raw-row handoff fixture is redacted",
                ),
                _evidence_ref(
                    "docs/reports/paper_governance_ablation_eval.json",
                    "No rowless handoff redaction",
                    ablation_signal.get("No rowless handoff redaction"),
                    requirement="disabled redaction exposes blocked fields",
                ),
            ],
            limitation_or_boundary="The check evaluates deterministic redaction on fixtures. It is not a broad privacy certification.",
            paper_claim_allowed="The paper may claim rowless local-first handoff for the tested external-agent surfaces.",
            stronger_claim_blocked="It cannot claim production-grade privacy certification without separate review.",
        ),
        _invariant(
            invariant_id="I5_interrupted_run_recoverability",
            name="Interrupted-run recoverability",
            statement="A user or agent returning to a partial run must receive current state, missing evidence, safe next actions, and artifact shortlist.",
            enforcement_mechanism="no-lost-user guide and partial-run recovery fixtures",
            evidence_refs=[
                _evidence_ref(
                    "docs/reports/paper_no_lost_user_eval.json",
                    "partial_run_state_recovery",
                    _task_signal_lookup(recovery).get("partial_run_state_recovery"),
                    requirement="partial-run recovery exposes stage, missing evidence, and actions",
                ),
                _evidence_ref(
                    "docs/reports/paper_system_task_eval.json",
                    "partial_run_recovery_without_artifact_literacy",
                    task_signal.get("partial_run_recovery_without_artifact_literacy"),
                    requirement="inexperienced-user task can recover without artifact literacy",
                ),
            ],
            failure_or_ablation_refs=[
                _evidence_ref(
                    "docs/reports/paper_failure_case_eval.json",
                    "interrupted_run_recovery",
                    failure_signal.get("interrupted_run_recovery"),
                    requirement="interrupted-run fixture emits recovery guidance",
                ),
                _evidence_ref(
                    "docs/reports/paper_governance_ablation_eval.json",
                    "No interrupted-run recovery guide",
                    ablation_signal.get("No interrupted-run recovery guide"),
                    requirement="disabled recovery guide removes next actions",
                ),
            ],
            limitation_or_boundary="The check is deterministic; it does not measure human time-to-recovery.",
            paper_claim_allowed="The paper may claim tested recovery surfaces for partial AML runs.",
            stronger_claim_blocked="No human-subject usability or analyst-productivity claim is made.",
        ),
        _invariant(
            invariant_id="I6_benchmark_role_separation",
            name="Benchmark role separation",
            statement="Benchmark rows must preserve their evidence role: demonstration, graph-feature evidence, external context, limitation, or future unlock.",
            enforcement_mechanism="publishability matrix and allowed-claims report",
            evidence_refs=[
                _evidence_ref(
                    "docs/reports/paper_publishability_matrix.json",
                    "supporting_table_allowed",
                    _publishability_signal(publishability),
                    requirement="rows separate supporting evidence from blocked stronger claims",
                ),
                _evidence_ref(
                    "docs/reports/paper_system_task_eval.json",
                    "elliptic2_supporting_context_and_firewall_visible",
                    task_signal.get("elliptic2_supporting_context_and_firewall_visible"),
                    requirement="Elliptic2 remains context rather than parity contribution",
                ),
            ],
            failure_or_ablation_refs=[
                _evidence_ref(
                    "docs/reports/paper_public_claims_allowed.json",
                    "blocked_public_claims",
                    f"blocked={len(claim_payload.get('blocked_public_claims', []) or [])}",
                    requirement="hard/headline detector claims remain absent",
                )
            ],
            limitation_or_boundary="Rows with external or proxy roles cannot be treated as unified leaderboard evidence.",
            paper_claim_allowed="The paper may compare evidence roles, not claim detector leadership.",
            stronger_claim_blocked="RevClassifyDS parity and graph-neural detector novelty remain out of scope.",
        ),
        _invariant(
            invariant_id="I7_local_first_release_safety",
            name="Local-first release safety",
            statement="Release artifacts must be generated from local evidence and pass lint for private paths, missing evidence, and unsupported public wording.",
            enforcement_mechanism="release go/no-go, claim lint, and public-claim whitelist",
            evidence_refs=[
                _evidence_ref(
                    "docs/reports/paper_claim_lint_report.json",
                    "wording_lint",
                    str(claim_lint.get("status") or ""),
                    requirement="paper-facing wording passes blocked-claim lint",
                ),
                _evidence_ref(
                    "docs/reports/paper_release_go_no_go.json",
                    "go_for_p13_claim_safe_release_pack",
                    str(go_no_go.get("status") or ""),
                    requirement="claim-safe release is allowed only with hard/headline claims blocked",
                ),
            ],
            failure_or_ablation_refs=[
                _evidence_ref(
                    "docs/reports/paper_governance_ablation_manifest.json",
                    "detector_claim_boundary",
                    str(_payload(inputs["governance_ablation_manifest"]).get("detector_claim_boundary") or "hard/headline blocked"),
                    requirement="governance evidence records detector-claim boundary",
                )
            ],
            limitation_or_boundary="Licensed benchmark files are not redistributed; reproduction depends on local access.",
            paper_claim_allowed="The paper may claim a local-first, claim-safe release path for the published artifact pack.",
            stronger_claim_blocked="It cannot claim independent rerun of private or licensed data without dataset access.",
        ),
    ]


def _build_adjacent_systems_rows(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    del inputs
    return [
        {
            "adjacent_family": "Model cards and model reporting",
            "representative_sources": ["mitchell2019modelcards"],
            "primary_object": "trained model and intended-use report",
            "what_it_covers": "model purpose, evaluation, caveats, and intended users",
            "relaytic_aml_boundary": "does not replace model reporting",
            "relaytic_aml_position": "adds command-level metric provenance, release gating, and stronger-claim blocking around AML experiments",
        },
        {
            "adjacent_family": "Datasheets and dataset documentation",
            "representative_sources": ["gebru2021datasheets"],
            "primary_object": "dataset creation, composition, collection, and recommended use",
            "what_it_covers": "data provenance and stewardship questions",
            "relaytic_aml_boundary": "does not replace source-dataset governance",
            "relaytic_aml_position": "connects dataset posture to split contracts, leakage controls, benchmark rows, and admissible claims",
        },
        {
            "adjacent_family": "ML reproducibility checklists",
            "representative_sources": ["pineau2021reproducibility"],
            "primary_object": "reporting checklist and reproducibility discipline",
            "what_it_covers": "static items needed to make results easier to reproduce",
            "relaytic_aml_boundary": "does not claim full independent reproduction for licensed data",
            "relaytic_aml_position": "turns checklist-like obligations into executable artifact-generation and release gates",
        },
        {
            "adjacent_family": "MLOps experiment tracking",
            "representative_sources": ["zaharia2018mlflow"],
            "primary_object": "runs, metrics, parameters, artifacts, lineage, and model versions",
            "what_it_covers": "operational memory of experiments",
            "relaytic_aml_boundary": "is not a hosted tracker or production model registry",
            "relaytic_aml_position": "focuses on local AML evidence, privacy posture, rowless handoff, and public scientific claim admissibility",
        },
        {
            "adjacent_family": "Agent benchmarks and research-agent evaluations",
            "representative_sources": ["chen2025mlrbench", "starace2025paperbench", "wijk2025rebench", "yang2026skillopt"],
            "primary_object": "agent performance on research, coding, or skill-use tasks",
            "what_it_covers": "whether agents can complete tasks or produce research artifacts",
            "relaytic_aml_boundary": "does not benchmark a general-purpose agent",
            "relaytic_aml_position": "uses agents inside a governed local evaluation lab and then tests whether their outputs stay artifact-attached",
        },
        {
            "adjacent_family": "AML detector and benchmark papers",
            "representative_sources": ["weber2019elliptic", "bellei2024elliptic2", "song2024revtrack", "chen2026transxion", "poon2025linemvgnn", "ye2026blazingaml"],
            "primary_object": "detector architecture, benchmark result, graph construction, or financial-crime dataset",
            "what_it_covers": "modeling frontier for temporal and graph AML detection",
            "relaytic_aml_boundary": "is not a new graph-neural detector and does not claim detector SOTA",
            "relaytic_aml_position": "provides the local evidence and claim-governance substrate that such detector studies can run through",
        },
        {
            "adjacent_family": "AML LLM graph reasoning and triage systems",
            "representative_sources": ["pirmorad2025amlgraphllm", "naik2026llmopsaml"],
            "primary_object": "LLM reasoning, triage, serving, and evidence-rich prompts for AML workflows",
            "what_it_covers": "language-model assistance for suspiciousness reasoning, risk-factor extraction, and compliance-oriented outputs",
            "relaytic_aml_boundary": "does not claim an LLM detector or AML LLM-serving stack",
            "relaytic_aml_position": "keeps LLM or external-agent help downstream of rowless local evidence, artifact provenance, and claim gates",
        },
        {
            "adjacent_family": "Agentic SAR and compliance narrative assistants",
            "representative_sources": ["naik2025coinvestigator"],
            "primary_object": "human-in-the-loop SAR or compliance narrative drafting",
            "what_it_covers": "case narrative generation, compliance validation, investigator collaboration, and report-writing support",
            "relaytic_aml_boundary": "does not generate or validate regulatory SAR submissions",
            "relaytic_aml_position": "governs the local experimental evidence and admissible claims that such narrative workflows should cite",
        },
        {
            "adjacent_family": "Agent governance and runtime trust layers",
            "representative_sources": ["gaurav2025governanceaas", "kaptein2026runtimegovernance"],
            "primary_object": "runtime policies, enforcement, logging, trust scoring, and path-dependent agent governance",
            "what_it_covers": "general agent action control across domains and heterogeneous agent stacks",
            "relaytic_aml_boundary": "does not claim to be a general-purpose agent-governance product",
            "relaytic_aml_position": "specializes governance to local AML evidence cells, rowless handoff, benchmark context, and paper/public claim admissibility",
        },
    ]


def _build_invariant_report(*, inputs: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    proof_checks = [_invariant_is_evidence_backed(row, inputs) for row in rows]
    aspirational_current = [
        row.get("invariant_id")
        for row in rows
        if row.get("current_status") == "current_checked" and row.get("aspirational")
    ]
    status = "pass" if all(proof_checks) and not aspirational_current else "blocked"
    return {
        "schema_version": PAPER_INVARIANT_SCHEMA_VERSION,
        "slice": "Paper Track P18",
        "status": status,
        "scope": "governance_invariants_for_current_relaytic_aml_paper_claims",
        "current_invariant_count": len(rows),
        "proof_obligation_passed": status == "pass",
        "invariants": rows,
        "checks": {
            "all_current_invariants_have_evidence_refs": all(bool(row.get("evidence_refs")) for row in rows),
            "all_current_invariants_have_failure_or_ablation_or_boundary": all(
                bool(row.get("failure_or_ablation_refs")) or bool(row.get("limitation_or_boundary"))
                for row in rows
            ),
            "all_evidence_refs_exist": all(proof_checks),
            "aspirational_invariants_in_current_section": aspirational_current,
        },
        "claim_boundary": {
            "detector_superiority_claimed": False,
            "hard_real_bank_aml_superiority_claimed": False,
            "graph_neural_detector_novelty_claimed": False,
            "revclassify_parity_claimed": False,
        },
        "next_slice": NEXT_PAPER_INVARIANT_SLICE if status == "pass" else "Paper Track P18 repair",
    }


def _build_adjacent_systems_report(*, inputs: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    bib_keys = _bib_keys(_text_payload(inputs["references"]))
    citation_checks = []
    for row in rows:
        sources = [str(item) for item in row.get("representative_sources", []) if item]
        missing = [source for source in sources if source not in bib_keys]
        citation_checks.append(
            {
                "adjacent_family": row.get("adjacent_family"),
                "representative_sources": sources,
                "missing_bib_keys": missing,
                "passed": not missing,
            }
        )
    covered = {str(row.get("adjacent_family")) for row in rows}
    missing_families = [family for family in REQUIRED_ADJACENT_FAMILIES if family not in covered]
    status = "pass" if not missing_families and all(check["passed"] for check in citation_checks) else "blocked"
    return {
        "schema_version": PAPER_INVARIANT_SCHEMA_VERSION,
        "slice": "Paper Track P18",
        "status": status,
        "family_count": len(rows),
        "comparison_rows": rows,
        "covered_families": sorted(covered),
        "missing_required_families": missing_families,
        "citation_checks": citation_checks,
        "claim_boundary": "This comparison positions Relaytic-AML as an evaluation-lab and governance system, not as a detector-superiority paper.",
        "next_slice": NEXT_PAPER_INVARIANT_SLICE if status == "pass" else "Paper Track P18 repair",
    }


def _build_manifest(
    *,
    inputs: dict[str, Any],
    invariant_report: dict[str, Any],
    adjacent_report: dict[str, Any],
) -> dict[str, Any]:
    required = _required_artifact_presence(inputs)
    generated_preview = json.dumps(
        {
            "paper_governance_invariants": invariant_report,
            "paper_adjacent_systems_comparison": adjacent_report,
        },
        sort_keys=True,
    )
    generated_redaction = _scan_generated_preview(generated_preview)
    checks = [
        _check(
            "required_inputs_present",
            not required["missing_artifact_refs"],
            "P18 requires the P10-P17 governance, failure, and evidence-cell artifacts.",
            detail=required,
        ),
        _check(
            "invariant_proof_obligation_passed",
            invariant_report.get("status") == "pass" and bool(invariant_report.get("proof_obligation_passed")),
            "Every named current invariant must map to evidence refs, a failure or ablation signal, or a limitation boundary.",
        ),
        _check(
            "adjacent_systems_comparison_passed",
            adjacent_report.get("status") == "pass" and int(adjacent_report.get("family_count") or 0) >= len(REQUIRED_ADJACENT_FAMILIES),
            "Adjacent systems comparison must cover the required families with resolved citations where sources are named.",
        ),
        _check(
            "detector_claim_boundary_preserved",
            not bool(invariant_report.get("claim_boundary", {}).get("detector_superiority_claimed"))
            and not bool(invariant_report.get("claim_boundary", {}).get("hard_real_bank_aml_superiority_claimed"))
            and not bool(invariant_report.get("claim_boundary", {}).get("graph_neural_detector_novelty_claimed"))
            and not bool(invariant_report.get("claim_boundary", {}).get("revclassify_parity_claimed")),
            "P18 must not strengthen detector claims.",
        ),
        _check(
            "generated_reports_redacted",
            not generated_redaction["private_path_patterns"] and not generated_redaction["raw_row_markers"],
            "P18 reports must not expose local machine paths or raw-row markers.",
            detail=generated_redaction,
        ),
    ]
    status = "ready_for_governance_invariant_evidence" if all(check["passed"] for check in checks) else "blocked_pending_p18_repairs"
    return {
        "schema_version": PAPER_INVARIANT_SCHEMA_VERSION,
        "slice": "Paper Track P18",
        "status": status,
        "input_artifacts": _input_artifact_summary(inputs),
        "required_input_artifact_refs": REQUIRED_PAPER_INVARIANT_INPUT_REFS,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "report_refs": [
            f"docs/reports/{filename}"
            for filename in PAPER_INVARIANT_FILENAMES.values()
        ],
        "claim_boundary": "governance architecture only; detector superiority, production AML readiness, graph-neural novelty, and RevClassifyDS parity remain blocked",
        "next_slice": NEXT_PAPER_INVARIANT_SLICE if status.startswith("ready") else "Paper Track P18 repair",
    }


def _invariant(
    *,
    invariant_id: str,
    name: str,
    statement: str,
    enforcement_mechanism: str,
    evidence_refs: list[dict[str, Any]],
    failure_or_ablation_refs: list[dict[str, Any]],
    limitation_or_boundary: str,
    paper_claim_allowed: str,
    stronger_claim_blocked: str,
) -> dict[str, Any]:
    return {
        "invariant_id": invariant_id,
        "name": name,
        "statement": statement,
        "current_status": "current_checked",
        "enforcement_mechanism": enforcement_mechanism,
        "evidence_refs": evidence_refs,
        "failure_or_ablation_refs": failure_or_ablation_refs,
        "limitation_or_boundary": limitation_or_boundary,
        "paper_claim_allowed": paper_claim_allowed,
        "stronger_claim_blocked": stronger_claim_blocked,
    }


def _evidence_ref(
    artifact_ref: str,
    evidence_id: str,
    observed_signal: Any,
    *,
    requirement: str,
) -> dict[str, Any]:
    return {
        "artifact_ref": artifact_ref,
        "evidence_id": evidence_id,
        "requirement": requirement,
        "observed_signal": _compact_signal(observed_signal),
    }


def _input_artifact_summary(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key, artifact in inputs.items():
        if key == "root" or not isinstance(artifact, dict):
            continue
        rows.append(
            {
                "input_id": key,
                "artifact_ref": artifact.get("artifact_ref"),
                "exists": bool(artifact.get("exists")),
                "sha256_prefix": str(artifact.get("sha256") or "")[:12] if artifact.get("sha256") else None,
            }
        )
    return rows


def _required_artifact_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    by_ref = {
        str(artifact.get("artifact_ref")): artifact
        for artifact in inputs.values()
        if isinstance(artifact, dict) and artifact.get("artifact_ref")
    }
    present = []
    missing = []
    for ref in REQUIRED_PAPER_INVARIANT_INPUT_REFS:
        artifact = by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {
        "present_artifact_refs": present,
        "missing_artifact_refs": missing,
    }


def _invariant_is_evidence_backed(row: dict[str, Any], inputs: dict[str, Any]) -> bool:
    existing_refs = {
        str(artifact.get("artifact_ref"))
        for artifact in inputs.values()
        if isinstance(artifact, dict) and artifact.get("exists") and artifact.get("artifact_ref")
    }
    refs = []
    refs.extend(item.get("artifact_ref") for item in row.get("evidence_refs", []) if isinstance(item, dict))
    refs.extend(item.get("artifact_ref") for item in row.get("failure_or_ablation_refs", []) if isinstance(item, dict))
    refs = [str(ref) for ref in refs if ref]
    return bool(refs) and all(ref in existing_refs for ref in refs)


def _task_signal_lookup(payload: dict[str, Any]) -> dict[str, str]:
    rows = payload.get("tasks") or payload.get("evaluation_rows") or []
    out: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        task_id = str(row.get("task_id") or row.get("check_id") or "")
        if task_id:
            out[task_id] = _compact_signal(row.get("measured_signal") or row.get("observed_result") or row.get("passed"))
    return out


def _failure_signal_lookup(payload: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in payload.get("cases", []):
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("case_id") or "")
        if case_id:
            out[case_id] = _compact_signal(row.get("observed_result") or row.get("measured_signal") or row.get("passed"))
    return out


def _ablation_signal_lookup(payload: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in payload.get("ablation_rows", []):
        if not isinstance(row, dict):
            continue
        path = str(row.get("path") or row.get("condition_id") or "")
        if not path:
            continue
        values = [
            f"unsafe_claims={row.get('unsupported_claims_released')}",
            f"leakage={row.get('leakage_features_allowed')}",
            f"raw_fields={row.get('raw_fields_exported')}",
            f"missing_provenance={row.get('missing_provenance_fields')}",
            f"recovery_actions={row.get('recovery_next_actions_available')}",
            f"safe={row.get('safe_to_publish')}",
        ]
        out[path] = "; ".join(values)
    return out


def _check_signal(payload: dict[str, Any], check_id: str) -> str:
    checks = payload.get("checks")
    if isinstance(checks, dict):
        value = checks.get(check_id)
        if isinstance(value, dict):
            return _compact_signal(value.get("observed") or value.get("status") or value.get("passed"))
        if value is not None:
            return _compact_signal(value)
    if check_id in payload:
        return _compact_signal(payload.get(check_id))
    return "not observed"


def _claim_boundary_signal(payload: dict[str, Any]) -> str:
    return (
        f"hard={payload.get('hard_claims_allowed')}; "
        f"headline={payload.get('headline_claims_allowed')}; "
        f"rows={len(payload.get('rows', []) or [])}"
    )


def _publishability_signal(payload: dict[str, Any]) -> str:
    rows = [row for row in payload.get("rows", []) if isinstance(row, dict)]
    supporting = sum(1 for row in rows if row.get("supporting_table_allowed"))
    hard_blocked = not bool(payload.get("hard_claims_allowed"))
    headline_blocked = not bool(payload.get("headline_claims_allowed"))
    return f"rows={len(rows)}; supporting={supporting}; hard_blocked={hard_blocked}; headline_blocked={headline_blocked}"


def _bib_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))


def _scan_generated_preview(text: str) -> dict[str, Any]:
    private_path_patterns = re.findall(r"[A-Za-z]:\\|[A-Za-z]:/|C:/Users|C:\\Users|\\Users\\|/(?:Users|home|tmp)/", text)
    raw_row_markers = re.findall(r"\braw transaction row\b|\braw rows exposed\b", text, flags=re.IGNORECASE)
    return {
        "private_path_patterns": sorted(set(private_path_patterns)),
        "raw_row_markers": sorted(set(raw_row_markers)),
    }


def _read_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _artifact_ref(path, root)
    if not path.exists():
        return {"artifact_ref": artifact_ref, "exists": False, "payload": None, "sha256": None}
    text = path.read_text(encoding="utf-8")
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError:
        payload = {"text": text}
    return {
        "artifact_ref": artifact_ref,
        "exists": True,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "payload": payload,
    }


def _read_text_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _artifact_ref(path, root)
    if not path.exists():
        return {"artifact_ref": artifact_ref, "exists": False, "payload": "", "sha256": None}
    text = path.read_text(encoding="utf-8")
    return {
        "artifact_ref": artifact_ref,
        "exists": True,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "payload": text,
    }


def _artifact_ref(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload")
    return payload if isinstance(payload, dict) else {}


def _text_payload(artifact: dict[str, Any]) -> str:
    payload = artifact.get("payload")
    return payload if isinstance(payload, str) else ""


def _check(
    check_id: str,
    passed: bool,
    message: str,
    *,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "check_id": check_id,
        "passed": bool(passed),
        "message": message,
    }
    if detail is not None:
        row["detail"] = detail
    return row


def _short_evidence_refs(refs: Any) -> str:
    if not isinstance(refs, list):
        return ""
    labels = []
    for ref in refs:
        if isinstance(ref, dict):
            labels.append(str(ref.get("evidence_id") or ref.get("artifact_ref") or ""))
    return "; ".join(label for label in labels if label)


def _compact_signal(value: Any) -> str:
    if value is None:
        return "not observed"
    text = str(value).replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:220] if len(text) > 220 else text


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")

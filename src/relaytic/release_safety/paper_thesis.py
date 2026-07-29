"""Paper thesis and claim-contract artifacts for Paper Track P2."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_THESIS_SCHEMA_VERSION = "relaytic.paper_thesis_contract.v1"
PAPER_THESIS_REPORT_DIR = Path("docs") / "reports"
PAPER_THESIS_DOC_DIR = Path("docs") / "paper"
PAPER_THESIS_FILENAMES = {
    "paper_thesis_contract": "paper_thesis_contract.json",
    "paper_claim_taxonomy": "paper_claim_taxonomy.json",
    "paper_related_work_seed": "paper_related_work_seed.json",
}
PAPER_THESIS_DOC_FILENAME = "paper_thesis.md"

PAPER_TITLE = "Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML"
PAPER_SHORT_TITLE = "Relaytic-AML"

RESEARCH_QUESTIONS = [
    {
        "id": "rq1_environment",
        "question": (
            "Can a local-first AML evaluation environment make model score, temporal correctness, graph "
            "provenance, analyst review utility, reproducibility, and public-claim safety inspectable together?"
        ),
        "evidence_required": [
            "aml_environment_scorecard.json",
            "aml_benchmark_environment_scorecard.json",
            "paper_table_provenance.json",
        ],
    },
    {
        "id": "rq2_temporal_graph",
        "question": (
            "Can Relaytic-AML evaluate temporal transaction-fraud and graph AML workloads without collapsing "
            "proxy, flattened, raw-graph, and subgraph evidence into one overbroad claim?"
        ),
        "evidence_required": [
            "paysim_temporal_split_report.json",
            "elliptic_graph_provenance_report.json",
            "elliptic_graph_claim_scope.json",
        ],
    },
    {
        "id": "rq3_operational",
        "question": (
            "Do review-budget, case-packet, and operational metrics change the interpretation of AML model "
            "quality compared with leaderboard-only metrics?"
        ),
        "evidence_required": [
            "paper_operational_metric_table.json",
            "paper_review_budget_curve.json",
            "paper_case_packet_completeness_report.json",
        ],
    },
    {
        "id": "rq4_reproducibility",
        "question": (
            "Can the paper tables be regenerated from local artifacts with every metric cell tied to commands, "
            "datasets, splits, artifacts, and claim posture?"
        ),
        "evidence_required": [
            "paper_result_table_final.json",
            "paper_table_provenance.json",
            "paper_metric_cell_audit.json",
            "paper_external_dry_run_report.json",
        ],
    },
]

CONTRIBUTIONS = [
    {
        "id": "c1_claim_gated_environment",
        "title": "Claim-gated AML evaluation environment",
        "summary": (
            "A local-first artifact system that keeps model metrics, temporal checks, graph provenance, "
            "operational utility, reproducibility, and public-claim boundaries in one inspectable contract."
        ),
    },
    {
        "id": "c2_benchmark_track_discipline",
        "title": "Benchmark-track discipline for AML evidence",
        "summary": (
            "A benchmark doctrine that separates PaySim-style proxy evidence, Elliptic-style graph evidence, "
            "Elliptic2-style subgraph evidence, AMLSim-style synthetic-bank evidence, and generic tabular breadth."
        ),
    },
    {
        "id": "c3_operational_metrics",
        "title": "Operational AML metrics as first-class paper rows",
        "summary": (
            "Review-budget, false-positive, analyst-capacity, and case-packet metrics are required alongside "
            "PR-AUC and precision-at-k before stronger AML claims are allowed."
        ),
    },
    {
        "id": "c4_reproducible_claim_firewall",
        "title": "Reproducible claim firewall",
        "summary": (
            "Every public claim is tied to artifact paths and table provenance; unsupported SOTA and hard AML "
            "performance claims stay blocked until holdout evidence and gates pass."
        ),
    },
]

BENCHMARK_TRACKS = [
    {
        "track_id": "paysim_temporal_transaction_fraud",
        "role": "proxy_temporal_transaction_fraud",
        "paper_use": "chronological split, rare-event metrics, threshold drift, review-budget metrics",
        "claim_boundary": "supporting-only until holdout and paper gates pass",
    },
    {
        "track_id": "elliptic_flattened_graph_aml",
        "role": "temporal_graph_aml",
        "paper_use": "graph provenance, raw-vs-flattened distinction, structural baseline comparison",
        "claim_boundary": "supporting-only until raw graph, holdout, and claim-scope gates pass",
    },
    {
        "track_id": "elliptic2_subgraph_aml",
        "role": "hard_subgraph_aml_track",
        "paper_use": "subgraph AML relevance and future hard-track posture",
        "claim_boundary": "blocked until access, loader, and claim-scope support are reproducible",
    },
    {
        "track_id": "amlsim_synthetic_bank_graph",
        "role": "synthetic_bank_graph_track",
        "paper_use": "seeded typology, synthetic-bank graph, and analyst-case workflow proof",
        "claim_boundary": "blocked or proxy until generator and source manifest are frozen",
    },
    {
        "track_id": "generic_structured_supporting_pack",
        "role": "supporting_breadth_only",
        "paper_use": "structured-data breadth context",
        "claim_boundary": "supporting-only; cannot replace AML temporal, graph, or operational evidence",
    },
]

METRIC_DOCTRINE = {
    "primary_metrics": [
        "pr_auc",
        "precision_at_k",
        "recall_at_review_budget",
        "fixed_fpr_recall",
        "threshold_stability_by_time_window",
    ],
    "operational_metrics": [
        "review_capacity_recall",
        "false_positive_reduction",
        "analyst_hour_savings",
        "case_packet_completeness",
    ],
    "secondary_metrics": [
        "roc_auc",
        "log_loss",
        "calibration_error",
    ],
    "disallowed_metric_posture": "Do not reduce AML claims to AUROC-only or leaderboard-only evidence.",
}

SOURCE_SEED = [
    {
        "source_id": "elliptic_bitcoin_aml_2019",
        "title": "Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics",
        "source_type": "paper",
        "url": "https://arxiv.org/abs/1908.02591",
        "topic": "Temporal graph AML benchmark",
        "paper_relevance": (
            "Anchor for Elliptic-style temporal graph AML evidence and the need to compare graph methods "
            "against strong simpler baselines."
        ),
    },
    {
        "source_id": "elliptic2_subgraph_2024",
        "title": "The Shape of Money Laundering: Subgraph Representation Learning on the Blockchain with the Elliptic2 Dataset",
        "source_type": "paper",
        "url": "https://arxiv.org/abs/2404.19109",
        "topic": "Subgraph AML benchmark",
        "paper_relevance": (
            "Justifies treating the hardest AML graph track as subgraph-centric and blocking claims until "
            "subgraph support is reproducible."
        ),
    },
    {
        "source_id": "amlsim_amlworld_neurips_2023",
        "title": "Realistic Synthetic Financial Transactions for Anti-Money Laundering Models",
        "source_type": "paper_and_dataset_generator",
        "url": "https://research.ibm.com/publications/realistic-synthetic-financial-transactions-for-anti-money-laundering-models",
        "topic": "Synthetic AML transaction generation",
        "paper_relevance": (
            "Supports a synthetic-bank graph track while keeping synthetic evidence separate from hard "
            "real-world AML superiority claims."
        ),
    },
    {
        "source_id": "paysim_2016",
        "title": "PaySim: A financial mobile money simulator for fraud detection",
        "source_type": "conference_paper",
        "url": "https://www.diva-portal.org/smash/record.jsf?pid=diva2:1058442",
        "topic": "Mobile-money transaction fraud simulator",
        "paper_relevance": (
            "Supports the PaySim-style temporal transaction-fraud proxy track and its synthetic-source caveat."
        ),
    },
    {
        "source_id": "tabpfn_nature_2025",
        "title": "Accurate predictions on small data with a tabular foundation model",
        "source_type": "paper",
        "url": "https://www.nature.com/articles/s41586-024-08328-6",
        "topic": "Tabular foundation model baseline pressure",
        "paper_relevance": (
            "Motivates evaluating modern tabular baselines instead of comparing only against older local models."
        ),
    },
    {
        "source_id": "dgraph_finance_graph_2022",
        "title": "DGraph: A Large-Scale Financial Dataset for Graph Anomaly Detection",
        "source_type": "paper",
        "url": "https://arxiv.org/abs/2207.03579",
        "topic": "Dynamic financial graph fraud benchmark",
        "paper_relevance": (
            "Provides adjacent dynamic financial-graph benchmark pressure while staying separate from AML-specific "
            "claims until data access and task posture are frozen."
        ),
    },
    {
        "source_id": "paperbench_2025",
        "title": "PaperBench: Evaluating AI's Ability to Replicate AI Research",
        "source_type": "paper",
        "url": "https://arxiv.org/abs/2504.01848",
        "topic": "Research reproducibility and agent evaluation",
        "paper_relevance": (
            "Motivates machine-readable reproduction commands, table provenance, and claim linting."
        ),
    },
    {
        "source_id": "mlr_bench_2025",
        "title": "MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research",
        "source_type": "paper",
        "url": "https://arxiv.org/abs/2505.19955",
        "topic": "Open-ended ML research evaluation",
        "paper_relevance": (
            "Reinforces that research systems should expose executable evidence rather than narrative-only claims."
        ),
    },
]


def build_paper_thesis_artifacts(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root)
    claim_boundary = _read_claim_boundary(root)
    taxonomy = _build_claim_taxonomy(claim_boundary)
    contract = _build_thesis_contract(taxonomy)
    related_work = _build_related_work_seed()
    markdown = render_paper_thesis_markdown(contract, taxonomy, related_work)
    return {
        "paper_thesis_contract": contract,
        "paper_claim_taxonomy": taxonomy,
        "paper_related_work_seed": related_work,
        "paper_thesis_markdown": markdown,
    }


def sync_paper_thesis_artifacts(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    doc_dir: str | Path | None = None,
) -> dict[str, Path]:
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_THESIS_REPORT_DIR
    thesis_doc_dir = Path(doc_dir) if doc_dir is not None else root / PAPER_THESIS_DOC_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    thesis_doc_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paper_thesis_artifacts(root)
    written: dict[str, Path] = {}
    for key, filename in PAPER_THESIS_FILENAMES.items():
        written[key] = write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
    doc_path = thesis_doc_dir / PAPER_THESIS_DOC_FILENAME
    doc_path.write_text(str(artifacts["paper_thesis_markdown"]), encoding="utf-8")
    written["paper_thesis_markdown"] = doc_path
    return written


def build_paper_thesis_pack(project_root: str | Path) -> dict[str, Any]:
    """Compatibility-friendly alias for the P2 paper thesis artifact pack."""
    return build_paper_thesis_artifacts(project_root)


def sync_paper_thesis_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    doc_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write the P2 paper thesis artifact pack to its canonical docs paths."""
    return sync_paper_thesis_artifacts(project_root, output_dir=output_dir, doc_dir=doc_dir)


def render_paper_thesis_markdown(
    contract: dict[str, Any],
    taxonomy: dict[str, Any],
    related_work: dict[str, Any],
) -> str:
    lines = [
        f"# {contract['paper_title']}",
        "",
        "Historical pipeline status: this document records the Paper Track P2 thesis freeze. "
        "Paper Track P0-P27 is now implemented. Use `relaytic_aml_arxiv_draft.md` for the current manuscript.",
        "",
        "## Thesis",
        "",
        str(contract["thesis"]),
        "",
        "## Primary Research Question",
        "",
        str(contract["primary_research_question"]),
        "",
        "## Research Questions",
        "",
    ]
    for rq in contract["research_questions"]:
        lines.append(f"- **{rq['id']}**: {rq['question']}")
    lines.extend(["", "## Contributions", ""])
    for contribution in contract["contributions"]:
        lines.append(f"- **{contribution['title']}**: {contribution['summary']}")
    lines.extend(["", "## Benchmark Doctrine", ""])
    for track in contract["benchmark_tracks"]:
        lines.append(f"- **{track['track_id']}**: {track['paper_use']} ({track['claim_boundary']}).")
    lines.extend(["", "## Claim Boundaries", ""])
    for claim in taxonomy["claims"]:
        lines.append(f"- **{claim['claim_id']}**: `{claim['boundary']}` - {claim['allowed_public_wording']}")
    lines.extend(["", "## Related-Work Seed", ""])
    for source in related_work["sources"]:
        lines.append(f"- **{source['source_id']}**: {source['title']} - {source['url']}")
    lines.extend(
        [
            "",
            "## Non-Goals",
            "",
            "- The paper must not claim global tabular SOTA.",
            "- The paper must not claim hard AML superiority without numeric holdout evidence and passing gates.",
            "- The paper must not treat synthetic, proxy, flattened, raw-graph, and subgraph evidence as interchangeable.",
            "",
            "## Next Slice At The P2 Freeze",
            "",
            "Paper Track P3 must freeze dataset registry, access posture, split posture, hashes, and blocked reasons before any benchmark runner is treated as paper evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_thesis_contract(taxonomy: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PAPER_THESIS_SCHEMA_VERSION,
        "slice": "Paper Track P2",
        "status": "thesis_contract_frozen",
        "paper_title": PAPER_TITLE,
        "paper_short_title": PAPER_SHORT_TITLE,
        "paper_type": "systems_and_benchmark_evaluation",
        "thesis": (
            "Relaytic-AML is a local-first, claim-gated evaluation environment for financial-crime ML. "
            "Its paper claim is not that a single model wins a leaderboard, but that AML evaluation becomes "
            "more credible when model metrics, temporal correctness, graph provenance, analyst-review utility, "
            "reproducibility, and public-claim boundaries are evaluated together."
        ),
        "primary_research_question": (
            "Can Relaytic-AML make temporal graph financial-crime evaluation more reproducible and less "
            "overclaimed by binding benchmark evidence, operational utility, and public claims to local artifacts?"
        ),
        "research_questions": RESEARCH_QUESTIONS,
        "contributions": CONTRIBUTIONS,
        "benchmark_tracks": BENCHMARK_TRACKS,
        "metric_doctrine": METRIC_DOCTRINE,
        "claim_contract_refs": {
            "source_claim_boundary_report": "docs/reports/paper_claim_boundary_report.json",
            "claim_taxonomy": "docs/reports/paper_claim_taxonomy.json",
        },
        "claim_taxonomy_agrees_with_release_freeze": bool(
            taxonomy.get("agrees_with_release_freeze_claim_boundaries", False)
        ),
        "blocked_until": [
            "paper_dataset_registry_exists",
            "paysim_temporal_row_exists",
            "elliptic_graph_row_exists",
            "strong_baseline_table_exists",
            "operational_metric_table_exists",
            "paper_table_provenance_exists",
            "external_dry_run_passes",
        ],
        "next_slice": "Paper Track P3",
    }


def _build_claim_taxonomy(claim_boundary: dict[str, Any]) -> dict[str, Any]:
    claims = []
    source_claims = claim_boundary.get("claims", [])
    allowed_boundaries = list(claim_boundary.get("allowed_boundaries", []))
    allowed_boundary_set = set(allowed_boundaries)
    for item in claim_boundary.get("claims", []):
        claim = dict(item)
        claims.append(
            {
                "claim_id": claim["claim_id"],
                "boundary": claim["boundary"],
                "claim_text": claim["claim_text"],
                "allowed_public_wording": claim["allowed_public_wording"],
                "artifact_paths": claim["artifact_paths"],
                "paper_section": _claim_section(str(claim["claim_id"])),
                "taxonomy_role": _claim_role(str(claim["boundary"])),
            }
        )
    claim_ids = {item["claim_id"] for item in claims}
    required_paper_claim_ids = {
        "claim_release_freeze_pack_exists",
        "claim_paysim_temporal_transaction_fraud",
        "claim_elliptic_flattened_graph_aml",
        "claim_sota_or_hard_aml_superiority",
        "claim_generic_structured_supporting_pack",
        "claim_subgraph_or_synthetic_bank_graph",
    }
    all_claim_boundaries_known = all(item["boundary"] in allowed_boundary_set for item in claims)
    taxonomy_agrees = bool(source_claims) and all_claim_boundaries_known and required_paper_claim_ids <= claim_ids
    return {
        "schema_version": PAPER_THESIS_SCHEMA_VERSION,
        "slice": "Paper Track P2",
        "status": "claim_taxonomy_frozen",
        "source_claim_boundary_report": "docs/reports/paper_claim_boundary_report.json",
        "source_claim_boundary_schema_version": claim_boundary.get("schema_version"),
        "source_claim_boundary_status": claim_boundary.get("status"),
        "allowed_boundaries": allowed_boundaries,
        "claims": claims,
        "claim_count": len(claims),
        "blocked_claim_ids": [item["claim_id"] for item in claims if item["boundary"] == "blocked"],
        "supporting_only_claim_ids": [
            item["claim_id"] for item in claims if item["boundary"] == "supporting-only"
        ],
        "hard_non_performance_claim_ids": [
            item["claim_id"] for item in claims if item["boundary"] == "hard"
        ],
        "taxonomy_agrees_with_claim_boundary_report": taxonomy_agrees,
        "agrees_with_release_freeze_claim_boundaries": taxonomy_agrees,
        "hard_performance_claims_allowed": False,
    }


def _build_related_work_seed() -> dict[str, Any]:
    return {
        "schema_version": PAPER_THESIS_SCHEMA_VERSION,
        "slice": "Paper Track P2",
        "status": "related_work_seed_frozen",
        "source_count": len(SOURCE_SEED),
        "sources": SOURCE_SEED,
        "topic_clusters": [
            {
                "cluster_id": "temporal_graph_aml",
                "source_ids": ["elliptic_bitcoin_aml_2019", "elliptic2_subgraph_2024"],
                "paper_angle": "AML graph evidence must distinguish node, edge, temporal, and subgraph claims.",
            },
            {
                "cluster_id": "synthetic_proxy_data",
                "source_ids": ["amlsim_amlworld_neurips_2023", "paysim_2016"],
                "paper_angle": "Synthetic evidence is useful for workflow and proxy proof but cannot unlock hard real-world AML claims alone.",
            },
            {
                "cluster_id": "strong_tabular_baselines",
                "source_ids": ["tabpfn_nature_2025", "dgraph_finance_graph_2022"],
                "paper_angle": "Modern tabular baselines put pressure on Relaytic to compare against stronger references.",
            },
            {
                "cluster_id": "research_reproducibility",
                "source_ids": ["paperbench_2025", "mlr_bench_2025"],
                "paper_angle": "Machine-readable reproduction and claim linting are part of the paper contribution.",
            },
        ],
    }


def _read_claim_boundary(root: Path) -> dict[str, Any]:
    path = root / "docs" / "reports" / "paper_claim_boundary_report.json"
    if not path.exists():
        return {"allowed_boundaries": [], "claims": []}
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _claim_role(boundary: str) -> str:
    if boundary == "hard":
        return "product_surface_claim_only"
    if boundary == "supporting-only":
        return "supporting_evidence_claim"
    return "blocked_until_later_paper_gate"


def _claim_section(claim_id: str) -> str:
    if "release_freeze" in claim_id:
        return "system"
    if "paysim" in claim_id:
        return "benchmarks_pay_sim"
    if "elliptic" in claim_id:
        return "benchmarks_elliptic"
    if "sota" in claim_id or "hard_aml" in claim_id:
        return "limitations"
    if "generic" in claim_id:
        return "supporting_breadth"
    return "future_work"

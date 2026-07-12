"""Paper Track P23 novelty and adjacent-systems distinction audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_NOVELTY_SCHEMA_VERSION = "relaytic.paper_novelty_positioning.v1"
PAPER_NOVELTY_REPORT_DIR = Path("docs") / "reports"
NEXT_PAPER_NOVELTY_SLICE = "Slice 16A - capability registry and capability cards"

PAPER_NOVELTY_FILENAMES = {
    "paper_novelty_positioning_audit": "paper_novelty_positioning_audit.json",
    "paper_adjacent_systems_distinction_matrix": "paper_adjacent_systems_distinction_matrix.json",
    "paper_novelty_positioning_manifest": "paper_novelty_positioning_manifest.json",
    "paper_novelty_positioning_summary": "paper_novelty_positioning_summary.md",
}

REQUIRED_PAPER_NOVELTY_INPUT_REFS = [
    "README.md",
    "docs/paper/relaytic_aml_arxiv_draft.md",
    "docs/paper/references.bib",
    "docs/reports/paper_adjacent_systems_comparison.json",
    "docs/reports/paper_governance_invariants.json",
    "docs/reports/paper_external_score_claim_map.json",
    "docs/reports/paper_reader_guidance_audit.json",
    "docs/reports/paper_public_claims_allowed.json",
]

REQUIRED_DISTINCTION_CATEGORIES = [
    "AML detector and benchmark papers",
    "AML LLM graph reasoning and triage systems",
    "Agentic SAR and compliance narrative assistants",
    "Agent governance and runtime trust layers",
    "MLOps experiment tracking",
    "Model cards and model reporting",
    "Datasheets and dataset documentation",
    "ML reproducibility checklists",
    "Agent benchmarks and research-agent evaluations",
]


def build_paper_novelty_positioning_pack(
    project_root: str | Path,
    *,
    source_report_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build the P23 novelty and category-distinction audit pack."""
    root = Path(project_root)
    report_dir = Path(source_report_dir) if source_report_dir is not None else root / PAPER_NOVELTY_REPORT_DIR
    inputs = _collect_inputs(root=root, report_dir=report_dir)
    matrix = _build_distinction_matrix(inputs)
    audit = _build_novelty_audit(inputs=inputs, matrix=matrix)
    manifest = _build_manifest(inputs=inputs, matrix=matrix, audit=audit)
    summary = render_paper_novelty_positioning_markdown(
        {
            "paper_novelty_positioning_audit": audit,
            "paper_adjacent_systems_distinction_matrix": matrix,
            "paper_novelty_positioning_manifest": manifest,
        }
    )
    return {
        "paper_novelty_positioning_audit": audit,
        "paper_adjacent_systems_distinction_matrix": matrix,
        "paper_novelty_positioning_manifest": manifest,
        "paper_novelty_positioning_summary": summary,
    }


def sync_paper_novelty_positioning_pack(
    project_root: str | Path,
    *,
    source_report_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write the P23 novelty/distinction reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_NOVELTY_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_novelty_positioning_pack(root, source_report_dir=source_report_dir)
    written: dict[str, Path] = {}
    for key, filename in PAPER_NOVELTY_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_novelty_positioning_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_novelty_positioning_manifest", {}))
    audit = dict(pack.get("paper_novelty_positioning_audit", {}))
    matrix = dict(pack.get("paper_adjacent_systems_distinction_matrix", {}))
    lines = [
        "# Paper P23 Novelty And Adjacent-Systems Distinction",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Distinction matrix: `{matrix.get('status') or 'unknown'}`",
        f"- Manuscript audit: `{audit.get('status') or 'unknown'}`",
        f"- Covered categories: `{matrix.get('covered_category_count') or 0}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        "",
        "## Distinction Matrix",
        "",
        "| Adjacent system | What it optimizes | Relaytic-AML role |",
        "| --- | --- | --- |",
    ]
    for row in matrix.get("distinction_rows", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(row.get("adjacent_system_type") or "")),
                    _escape_md(str(row.get("optimizes_for") or "")),
                    _escape_md(str(row.get("distinct_relaytic_aml_role") or "")),
                ]
            )
            + " |"
        )
    failed = list(manifest.get("failed_checks", []))
    if failed:
        lines.extend(["", "## Failed Checks", ""])
        for check in failed:
            if isinstance(check, dict):
                lines.append(f"- `{check.get('check_id')}`: {check.get('message')}")
    return "\n".join(lines).rstrip() + "\n"


def _collect_inputs(*, root: Path, report_dir: Path) -> dict[str, Any]:
    paper = root / "docs" / "paper"
    return {
        "root": root,
        "readme": _read_text_artifact(root / "README.md", root=root),
        "draft": _read_text_artifact(paper / "relaytic_aml_arxiv_draft.md", root=root),
        "references": _read_text_artifact(paper / "references.bib", root=root),
        "adjacent_systems": _read_json_artifact(report_dir / "paper_adjacent_systems_comparison.json", root=root),
        "governance_invariants": _read_json_artifact(report_dir / "paper_governance_invariants.json", root=root),
        "external_score_claim_map": _read_json_artifact(report_dir / "paper_external_score_claim_map.json", root=root),
        "reader_guidance": _read_json_artifact(report_dir / "paper_reader_guidance_audit.json", root=root),
        "public_claims": _read_json_artifact(report_dir / "paper_public_claims_allowed.json", root=root),
    }


def _build_distinction_matrix(inputs: dict[str, Any]) -> dict[str, Any]:
    adjacent_rows = _adjacent_rows(inputs)
    bib_keys = _bib_keys(_text_payload(inputs["references"]))
    rows = []
    for template in _distinction_templates():
        adjacent = adjacent_rows.get(template["adjacent_system_type"], {})
        sources = list(template["representative_sources"])
        if adjacent.get("representative_sources"):
            sources = list(dict.fromkeys([*sources, *list(adjacent.get("representative_sources", []))]))
        missing = [source for source in sources if source not in bib_keys]
        rows.append(
            {
                **template,
                "source_artifact": "docs/reports/paper_adjacent_systems_comparison.json",
                "citation_status": "pass" if not missing else "missing_bib_keys",
                "missing_bib_keys": missing,
            }
        )
    covered = {row["adjacent_system_type"] for row in rows}
    missing_categories = [category for category in REQUIRED_DISTINCTION_CATEGORIES if category not in covered]
    status = "pass" if not missing_categories and all(not row["missing_bib_keys"] for row in rows) else "fail"
    return {
        "schema_version": PAPER_NOVELTY_SCHEMA_VERSION,
        "slice": "Paper Track P23",
        "status": status,
        "scope": "reader_facing_novelty_and_adjacent_systems_distinction",
        "covered_category_count": len(covered),
        "required_categories": REQUIRED_DISTINCTION_CATEGORIES,
        "missing_required_categories": missing_categories,
        "distinction_rows": rows,
        "claim_boundary": {
            "detector_replacement_claimed": False,
            "detector_superiority_claimed": False,
            "generic_agent_governance_claimed": False,
            "sar_generation_claimed": False,
            "production_aml_readiness_claimed": False,
        },
    }


def _build_novelty_audit(*, inputs: dict[str, Any], matrix: dict[str, Any]) -> dict[str, Any]:
    draft = _text_payload(inputs["draft"])
    readme = _text_payload(inputs["readme"])
    public_claims = _payload(inputs["public_claims"])
    normalized = _normalize(draft)
    checks = [
        _check(
            "what_is_new_section_present",
            "what is new" in normalized and "governance substrate around detectors and agent-assisted workflows" in normalized,
            "The manuscript must contain a concise reader-facing distinction section after related work.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "around_detectors_and_agents_framing_present",
            "around detectors and agent-assisted workflows" in normalized
            and "wrap detector outputs" in normalized
            and "rowless handoff" in normalized
            and "claim gates" in normalized,
            "The manuscript must frame Relaytic-AML as a layer around detectors and agents.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "aml_llm_and_sar_distinctions_present",
            "aml llm graph reasoning" in normalized
            and "agentic sar and compliance narrative assistants" in normalized
            and "not a sar drafting system" in normalized,
            "The manuscript must distinguish Relaytic-AML from AML LLM triage and SAR-writing assistants.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "agent_governance_distinction_present",
            "agent governance and runtime trust layers" in normalized
            and "not a general-purpose agent-governance product" in normalized,
            "The manuscript must distinguish Relaytic-AML from general runtime agent-governance systems.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "not_detector_replacement_boundary_present",
            "governance substrate around detectors" in normalized
            and (
                "not a new detector" in normalized
                or "rather than a replacement for them" in normalized
            ),
            "The paper must say Relaytic-AML wraps detector workflows rather than replacing detectors.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
        _check(
            "distinction_matrix_passed",
            matrix.get("status") == "pass" and int(matrix.get("covered_category_count") or 0) >= len(REQUIRED_DISTINCTION_CATEGORIES),
            "The machine-readable distinction matrix must cover all required adjacent categories with resolved citations.",
            source_artifact="docs/reports/paper_adjacent_systems_distinction_matrix.json",
            detail={
                "covered_category_count": matrix.get("covered_category_count"),
                "missing_required_categories": matrix.get("missing_required_categories"),
            },
        ),
        _check(
            "claim_boundary_preserved",
            public_claims.get("status") == "claim_safe_public_wording_allowed"
            and not bool(public_claims.get("hard_claims_allowed"))
            and not bool(public_claims.get("headline_claims_allowed"))
            and not _has_unguarded_claim_phrase(
                normalized,
                [
                    "relaytic-aml outperforms",
                    "relaytic-aml beats",
                    "detector superiority",
                    "production-ready aml",
                    "revclassifyds parity",
                    "graph-neural novelty",
                ],
            ),
            "P23 must not strengthen detector, production, RevClassifyDS, or graph-neural claims.",
            source_artifact="docs/reports/paper_public_claims_allowed.json",
        ),
        _check(
            "reader_guidance_still_simple",
            "for a paper review, use this path" in _normalize(readme)
            and _payload(inputs["reader_guidance"]).get("status") == "pass",
            "P23 positioning must not route first-time readers into internal planning files.",
            source_artifact="docs/reports/paper_reader_guidance_audit.json",
        ),
        _check(
            "tone_and_surface_clean",
            not _contains_any(
                normalized,
                [
                    "a weaker paper",
                    "weaker paper",
                    "this is the part",
                    "harder to oversell",
                    "garbage",
                ],
            )
            and not _contains_private_or_raw_markers(draft),
            "The novelty distinction should read as calm category positioning and remain leak-safe.",
            source_artifact="docs/paper/relaytic_aml_arxiv_draft.md",
        ),
    ]
    status = "pass" if all(check["passed"] for check in checks) else "fail"
    return {
        "schema_version": PAPER_NOVELTY_SCHEMA_VERSION,
        "slice": "Paper Track P23",
        "status": status,
        "claim_boundary": "local-first AML evaluation-evidence governance around detectors and agents; no detector superiority, SAR generation, production AML, or generic agent-governance claim",
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def _build_manifest(
    *,
    inputs: dict[str, Any],
    matrix: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, Any]:
    required = _required_artifact_presence(inputs)
    preview = json.dumps({"matrix": matrix, "audit": audit}, sort_keys=True)
    checks = [
        _check(
            "required_p23_inputs_present",
            not required["missing_artifact_refs"],
            "P23 requires the current manuscript, references, P18 adjacent comparison, P20 reader guidance, public-claim gate, and hosted-score claim map.",
            source_artifact="docs/reports",
            detail=required,
        ),
        _check(
            "distinction_matrix_passed",
            matrix.get("status") == "pass",
            "P23 distinction matrix must cover required adjacent systems and resolved citations.",
            source_artifact="docs/reports/paper_adjacent_systems_distinction_matrix.json",
        ),
        _check(
            "novelty_audit_passed",
            audit.get("status") == "pass",
            "P23 manuscript novelty and claim-boundary audit must pass.",
            source_artifact="docs/reports/paper_novelty_positioning_audit.json",
        ),
        _check(
            "generated_reports_redacted",
            not _contains_private_or_raw_markers(preview),
            "P23 generated reports must not expose private paths, secrets, or raw-row markers.",
            source_artifact="docs/reports/paper_novelty_positioning_manifest.json",
        ),
    ]
    ready = all(check["passed"] for check in checks)
    return {
        "schema_version": PAPER_NOVELTY_SCHEMA_VERSION,
        "slice": "Paper Track P23",
        "status": "ready_for_final_author_review" if ready else "blocked_pending_p23_repairs",
        "p23_implemented": ready,
        "arxiv_upload_ready": False,
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "required_source_artifacts": REQUIRED_PAPER_NOVELTY_INPUT_REFS,
        "report_artifact_refs": [f"docs/reports/{filename}" for filename in PAPER_NOVELTY_FILENAMES.values()],
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "next_slice": NEXT_PAPER_NOVELTY_SLICE if ready else "Paper Track P23 repair",
    }


def _distinction_templates() -> list[dict[str, Any]]:
    return [
        _row(
            "AML detector and benchmark papers",
            ["weber2019elliptic", "bellei2024elliptic2", "song2024revtrack"],
            "higher-performing detector architectures, graph features, datasets, and benchmark rows",
            "detector superiority, graph-neural novelty, or RevClassifyDS parity",
            "wrap detector runs and outputs with local provenance, leakage posture, budget context, review-budget interpretation, and claim gates",
        ),
        _row(
            "AML LLM graph reasoning and triage systems",
            ["pirmorad2025amlgraphllm", "naik2026llmopsaml"],
            "LLM reasoning over AML graph context, risk-factor extraction, serving throughput, and quality gates",
            "an LLM detector, a compliance LLM-serving stack, or raw-row export to external models",
            "keep LLM and external-agent assistance downstream of rowless local evidence cells and admissible-claim checks",
        ),
        _row(
            "Agentic SAR and compliance narrative assistants",
            ["naik2025coinvestigator"],
            "human-in-the-loop SAR narrative generation, compliance validation, and investigator-facing writing support",
            "SAR drafting, regulatory filing validation, or analyst-productivity measurement",
            "make the experimental evidence and claim boundary that downstream narratives should cite auditable before writing begins",
        ),
        _row(
            "Agent governance and runtime trust layers",
            ["gaurav2025governanceaas", "kaptein2026runtimegovernance"],
            "general runtime policy enforcement, trust scoring, path-dependent controls, and agent action logs",
            "a general-purpose agent-governance platform or broad organizational risk layer",
            "specialize governance to AML metric cells, rowless handoff, benchmark-context routing, and public paper/release wording",
        ),
        _row(
            "MLOps experiment tracking",
            ["zaharia2018mlflow"],
            "run history, artifacts, metrics, parameters, model versions, and lifecycle memory",
            "a hosted tracking server or production model registry",
            "add local AML-specific interpretation gates that decide which tracked results may become public scientific claims",
        ),
        _row(
            "Model cards and model reporting",
            ["mitchell2019modelcards"],
            "model documentation, intended use, evaluation summaries, and caveats",
            "a replacement for final model reporting",
            "materialize the provenance and claim-state inputs a model report would need to be defensible",
        ),
        _row(
            "Datasheets and dataset documentation",
            ["gebru2021datasheets"],
            "dataset composition, collection process, stewardship, and recommended use",
            "a replacement for source-dataset governance",
            "connect dataset posture to split contracts, leakage controls, benchmark rows, and admissible interpretations",
        ),
        _row(
            "ML reproducibility checklists",
            ["pineau2021reproducibility"],
            "static reporting requirements that make ML results easier to reproduce",
            "full independent reproduction of licensed or private AML data",
            "turn checklist obligations into executable local artifact generation, failure cases, and release preflight gates",
        ),
        _row(
            "Agent benchmarks and research-agent evaluations",
            ["chen2025mlrbench", "starace2025paperbench", "wijk2025rebench"],
            "measuring whether agents can complete research, coding, or tool-use tasks",
            "a benchmark of a general-purpose agent",
            "use role-scoped agents inside an AML evaluation lab and test whether their outputs stay attached to evidence",
        ),
    ]


def _row(
    adjacent_system_type: str,
    representative_sources: list[str],
    optimizes_for: str,
    relaytic_aml_does_not_claim: str,
    distinct_relaytic_aml_role: str,
) -> dict[str, Any]:
    return {
        "adjacent_system_type": adjacent_system_type,
        "representative_sources": representative_sources,
        "optimizes_for": optimizes_for,
        "relaytic_aml_does_not_claim": relaytic_aml_does_not_claim,
        "distinct_relaytic_aml_role": distinct_relaytic_aml_role,
        "paper_use": "category positioning only; no benchmark number or stronger detector claim added",
    }


def _adjacent_rows(inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    payload = _payload(inputs["adjacent_systems"])
    rows = {}
    for row in payload.get("comparison_rows", []):
        if isinstance(row, dict):
            rows[str(row.get("adjacent_family") or "")] = row
    return rows


def _required_artifact_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    by_ref = {
        str(value.get("artifact_ref")): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    present = []
    missing = []
    for ref in REQUIRED_PAPER_NOVELTY_INPUT_REFS:
        artifact = by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {"present_artifact_refs": present, "missing_artifact_refs": missing}


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
        return {"exists": False, "artifact_ref": artifact_ref, "text": "", "sha256": None}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "exists": True,
        "artifact_ref": artifact_ref,
        "byte_count": len(text.encode("utf-8")),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
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


def _bib_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in phrases)


def _has_unguarded_claim_phrase(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    guard_terms = [
        "blocked",
        "blocks",
        "not ",
        "no ",
        "does not",
        "cannot",
        "without",
        "rather than",
        "not a",
        "not as",
        "remain blocked",
        "stays blocked",
        "stay blocked",
    ]
    for phrase in phrases:
        target = phrase.lower()
        start = 0
        while True:
            index = lowered.find(target, start)
            if index == -1:
                break
            window = lowered[max(0, index - 150) : min(len(lowered), index + len(target) + 120)]
            if not any(term in window for term in guard_terms):
                return True
            start = index + len(target)
    return False


def _contains_private_or_raw_markers(text: str) -> bool:
    patterns = [
        r"[A-Za-z]:\\",
        r"C:/Users",
        r"C:\\Users",
        r"\\Users\\",
        r"/(?:Users|home|tmp)/",
        r"\braw transaction row\b",
        r"\braw rows exposed\b",
        r"api[_-]?key\s*[:=]",
        r"secret\s*[:=]",
        r"token\s*[:=]",
    ]
    return re.search("|".join(patterns), text, flags=re.IGNORECASE) is not None


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _repo_relative(path: Path, *, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


__all__ = [
    "NEXT_PAPER_NOVELTY_SLICE",
    "PAPER_NOVELTY_FILENAMES",
    "PAPER_NOVELTY_REPORT_DIR",
    "PAPER_NOVELTY_SCHEMA_VERSION",
    "REQUIRED_DISTINCTION_CATEGORIES",
    "REQUIRED_PAPER_NOVELTY_INPUT_REFS",
    "build_paper_novelty_positioning_pack",
    "render_paper_novelty_positioning_markdown",
    "sync_paper_novelty_positioning_pack",
]

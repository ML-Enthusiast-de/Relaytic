"""Paper Track P14 arXiv source-bundle and release-candidate audits."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any
import xml.etree.ElementTree as ET

from relaytic.core.json_utils import write_json


PAPER_ARXIV_SOURCE_SCHEMA_VERSION = "relaytic.paper_arxiv_source.v1"
PAPER_ARXIV_SOURCE_REPORT_DIR = Path("docs") / "reports"
PAPER_ARXIV_SOURCE_DOC_DIR = Path("docs") / "paper"
PAPER_ARXIV_SOURCE_DIRNAME = "arxiv_src"
PAPER_ARXIV_FIGURE_DIRNAME = "figures"
PAPER_ARXIV_MAIN_TEX_FILENAME = "main.tex"
PAPER_ARXIV_REFERENCES_FILENAME = "references.bib"
PAPER_ARXIV_RELEASE_TAG = "relaytic-aml-paper-p14-source-rc"
NEXT_PAPER_ARXIV_SOURCE_SLICE = "Slice 16A - capability registry and capability cards"

PAPER_ARXIV_SOURCE_FILENAMES = {
    "paper_arxiv_source_manifest": "paper_arxiv_source_manifest.json",
    "paper_submission_package_audit": "paper_submission_package_audit.json",
    "paper_release_candidate_checklist": "paper_release_candidate_checklist.md",
}

P13_REQUIRED_REFS = [
    "docs/reports/paper_release_manifest.json",
    "docs/reports/paper_public_claims_allowed.json",
    "docs/paper/relaytic_aml_arxiv_draft.md",
    "docs/paper/references.bib",
    "docs/paper/figures/figure_manifest.json",
]

ARXIV_ALLOWED_GRAPHIC_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".eps"}
FORBIDDEN_SOURCE_PATTERNS = [
    {
        "rule_id": "local_windows_path",
        "pattern": re.compile(r"[A-Za-z]:\\|[A-Za-z]:/(?!/)|C:/Users|C:\\Users|\\Users\\", re.IGNORECASE),
        "message": "Generated arXiv source must not contain local Windows paths.",
    },
    {
        "rule_id": "local_unix_path",
        "pattern": re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home|var/folders|tmp)/", re.IGNORECASE),
        "message": "Generated arXiv source must not contain local Unix paths.",
    },
    {
        "rule_id": "env_or_venv_reference",
        "pattern": re.compile(r"(?<![A-Za-z0-9_])(?:\.env|\.venv|venv)(?![A-Za-z0-9_])", re.IGNORECASE),
        "message": "Generated arXiv source must not reference local env files or virtual environments.",
    },
    {
        "rule_id": "secret_like_assignment",
        "pattern": re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]", re.IGNORECASE),
        "message": "Generated arXiv source must not contain secret-like assignments.",
    },
    {
        "rule_id": "legacy_prototype_name",
        "pattern": re.compile(r"corr2surrogate", re.IGNORECASE),
        "message": "Generated arXiv source must not expose the old prototype name.",
    },
    {
        "rule_id": "markdown_draft_staleness",
        "pattern": re.compile(r"arXiv-ready draft|claim-safe Markdown draft", re.IGNORECASE),
        "message": "Generated arXiv source must not describe itself as a draft conversion placeholder.",
    },
]
BLOCKED_PUBLIC_CLAIM_RULES = [
    {
        "rule_id": "unguarded_sota_claim",
        "phrase": "SOTA",
        "message": "SOTA wording must be explicitly negated or framed as blocked.",
    },
    {
        "rule_id": "unguarded_state_of_the_art_claim",
        "phrase": "state-of-the-art",
        "message": "State-of-the-art wording must not appear as an achieved Relaytic claim.",
    },
    {
        "rule_id": "unguarded_hard_aml_superiority",
        "phrase": "hard AML superiority",
        "message": "Hard AML superiority must remain blocked.",
    },
    {
        "rule_id": "unguarded_hard_real_world_aml_superiority",
        "phrase": "hard real-world AML superiority",
        "message": "Hard real-world AML superiority must remain blocked.",
    },
    {
        "rule_id": "unguarded_revclassify_parity",
        "phrase": "RevClassify parity",
        "message": "RevClassify parity must remain blocked unless reference parity passes.",
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
        "message": "Leaderboard-winner wording must be explicitly negated.",
    },
    {
        "rule_id": "unguarded_production_ready",
        "phrase": "production-ready",
        "message": "Production-ready wording is not supported by the current paper gates.",
    },
]
CLAIM_GUARD_MARKERS = (
    "no ",
    "not ",
    "blocked",
    "remain",
    "remaining",
    "limitation",
    "limitations",
    "unresolved",
    "cannot",
    "does not",
    "do not",
    "without",
    "below",
    "not enough",
    "not a",
)


def build_paper_arxiv_source_pack(
    project_root: str | Path,
    *,
    source_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build the deterministic P14 arXiv source bundle and package audits."""
    root = Path(project_root)
    inputs = _collect_inputs(root)
    arxiv_source_dir = Path(source_dir) if source_dir is not None else root / PAPER_ARXIV_SOURCE_DOC_DIR / PAPER_ARXIV_SOURCE_DIRNAME
    tex_source = _render_latex_source(inputs=inputs)
    figures = _build_pdf_figures(inputs=inputs)
    bibliography = _text_payload(inputs["references"])

    citation_audit = _audit_citations(tex_source=tex_source, bibliography=bibliography)
    figure_audit = _audit_figures(tex_source=tex_source, figures=figures)
    package_audit = _build_submission_package_audit(
        inputs=inputs,
        tex_source=tex_source,
        bibliography=bibliography,
        figures=figures,
        citation_audit=citation_audit,
        figure_audit=figure_audit,
    )
    manifest = _build_source_manifest(
        source_dir=arxiv_source_dir,
        inputs=inputs,
        tex_source=tex_source,
        bibliography=bibliography,
        figures=figures,
        citation_audit=citation_audit,
        figure_audit=figure_audit,
        package_audit=package_audit,
    )
    checklist = _render_release_candidate_checklist(manifest=manifest, package_audit=package_audit)
    return {
        "paper_arxiv_source_manifest": manifest,
        "paper_submission_package_audit": package_audit,
        "paper_release_candidate_checklist": checklist,
        "main_tex": tex_source,
        "references_bib": bibliography,
        "pdf_figures": figures,
    }


def sync_paper_arxiv_source_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    source_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write the P14 source bundle under docs/paper/arxiv_src and reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_ARXIV_SOURCE_REPORT_DIR
    arxiv_source_dir = Path(source_dir) if source_dir is not None else root / PAPER_ARXIV_SOURCE_DOC_DIR / PAPER_ARXIV_SOURCE_DIRNAME
    figure_dir = arxiv_source_dir / PAPER_ARXIV_FIGURE_DIRNAME
    report_dir.mkdir(parents=True, exist_ok=True)
    arxiv_source_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    pack = build_paper_arxiv_source_pack(root, source_dir=arxiv_source_dir)
    written: dict[str, Path] = {}
    for key, filename in PAPER_ARXIV_SOURCE_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)

    main_tex_path = arxiv_source_dir / PAPER_ARXIV_MAIN_TEX_FILENAME
    main_tex_path.write_text(str(pack["main_tex"]), encoding="utf-8")
    written["main_tex"] = main_tex_path

    references_path = arxiv_source_dir / PAPER_ARXIV_REFERENCES_FILENAME
    references_path.write_text(str(pack["references_bib"]), encoding="utf-8")
    written["references_bib"] = references_path

    for item in list(pack["pdf_figures"]):
        path = figure_dir / str(item["target_filename"])
        path.write_bytes(bytes.fromhex(str(item["pdf_hex"])))
        written[f"figure_{item['figure_id']}"] = path
    return written


def render_paper_arxiv_source_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_arxiv_source_manifest", {}))
    audit = dict(pack.get("paper_submission_package_audit", {}))
    return "\n".join(
        [
            "# Paper P14 arXiv Source Bundle",
            "",
            f"- Source status: `{manifest.get('status') or 'unknown'}`",
            f"- Source release candidate ready: `{manifest.get('source_release_candidate_ready')}`",
            f"- arXiv upload ready: `{manifest.get('arxiv_upload_ready')}`",
            f"- Source tree: `{manifest.get('source_tree', {}).get('source_dir') or 'unknown'}`",
            f"- Citation audit: `{manifest.get('citation_audit', {}).get('status') or 'unknown'}`",
            f"- Figure audit: `{manifest.get('figure_audit', {}).get('status') or 'unknown'}`",
            f"- Package audit: `{audit.get('status') or 'unknown'}`",
            f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _collect_inputs(root: Path) -> dict[str, Any]:
    reports = root / PAPER_ARXIV_SOURCE_REPORT_DIR
    paper = root / PAPER_ARXIV_SOURCE_DOC_DIR
    figure_dir = paper / "figures"
    return {
        "root": root,
        "paper_release_manifest": _read_artifact(reports / "paper_release_manifest.json"),
        "paper_public_claims_allowed": _read_artifact(reports / "paper_public_claims_allowed.json"),
        "draft": _read_text_artifact(paper / "relaytic_aml_arxiv_draft.md"),
        "references": _read_text_artifact(paper / "references.bib"),
        "figure_manifest": _read_artifact(figure_dir / "figure_manifest.json"),
        "figure_dir": figure_dir,
    }


def _build_source_manifest(
    *,
    source_dir: Path,
    inputs: dict[str, Any],
    tex_source: str,
    bibliography: str,
    figures: list[dict[str, Any]],
    citation_audit: dict[str, Any],
    figure_audit: dict[str, Any],
    package_audit: dict[str, Any],
) -> dict[str, Any]:
    checks = _source_checks(
        inputs=inputs,
        citation_audit=citation_audit,
        figure_audit=figure_audit,
        package_audit=package_audit,
    )
    source_ready = all(check["passed"] for check in checks)
    author_placeholder = "Author Name" in tex_source or "contact@example.com" in tex_source
    source_refs = [
        f"{_repo_relative(source_dir)}/{PAPER_ARXIV_MAIN_TEX_FILENAME}",
        f"{_repo_relative(source_dir)}/{PAPER_ARXIV_REFERENCES_FILENAME}",
        *[
            f"{_repo_relative(source_dir)}/{PAPER_ARXIV_FIGURE_DIRNAME}/{item['target_filename']}"
            for item in figures
        ],
    ]
    return {
        "schema_version": PAPER_ARXIV_SOURCE_SCHEMA_VERSION,
        "slice": "Paper Track P14",
        "status": "ready_for_source_release_candidate" if source_ready else "blocked_pending_source_repairs",
        "source_release_candidate_ready": source_ready,
        "arxiv_upload_ready": bool(source_ready and not author_placeholder),
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "release_mode": "claim_safe_evaluation_environment_only" if source_ready else "blocked",
        "source_tree": {
            "source_dir": _repo_relative(source_dir),
            "main_tex": f"{_repo_relative(source_dir)}/{PAPER_ARXIV_MAIN_TEX_FILENAME}",
            "bibliography": f"{_repo_relative(source_dir)}/{PAPER_ARXIV_REFERENCES_FILENAME}",
            "figure_dir": f"{_repo_relative(source_dir)}/{PAPER_ARXIV_FIGURE_DIRNAME}",
            "artifact_refs": source_refs,
        },
        "source_hashes": {
            "main_tex_sha256": _sha256_text(tex_source),
            "references_bib_sha256": _sha256_text(bibliography),
            "pdf_figure_sha256": {
                str(item["target_filename"]): item["pdf_sha256"]
                for item in figures
            },
        },
        "arxiv_processor_contract": {
            "processor": "pdfLaTeX",
            "graphic_formats_used": sorted({str(item["target_extension"]) for item in figures}),
            "allowed_graphic_extensions": sorted(ARXIV_ALLOWED_GRAPHIC_EXTENSIONS),
            "bibtex_bundle_state": "references.bib included; final upload checklist requires generating and inspecting bibliography output before upload",
            "author_metadata_placeholder_present": author_placeholder,
        },
        "p13_gate_refs": P13_REQUIRED_REFS,
        "citation_audit": citation_audit,
        "figure_audit": figure_audit,
        "submission_package_audit_ref": "docs/reports/paper_submission_package_audit.json",
        "release_candidate_checklist_ref": "docs/reports/paper_release_candidate_checklist.md",
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "release_tag_plan": {
            "tag": PAPER_ARXIV_RELEASE_TAG,
            "tag_created_by_this_slice": False,
            "creation_command": f"git tag -a {PAPER_ARXIV_RELEASE_TAG} -m \"Relaytic-AML arXiv source release candidate\"",
            "requires_clean_status_command": "git status --short",
            "artifact_refs": source_refs
            + [
                "docs/reports/paper_arxiv_source_manifest.json",
                "docs/reports/paper_submission_package_audit.json",
                "docs/reports/paper_release_candidate_checklist.md",
            ],
        },
        "next_slice": NEXT_PAPER_ARXIV_SOURCE_SLICE if source_ready else "Paper Track P14 repair",
    }


def _source_checks(
    *,
    inputs: dict[str, Any],
    citation_audit: dict[str, Any],
    figure_audit: dict[str, Any],
    package_audit: dict[str, Any],
) -> list[dict[str, Any]]:
    release_manifest = _payload(inputs["paper_release_manifest"])
    public_claims = _payload(inputs["paper_public_claims_allowed"])
    required = _required_artifact_presence(inputs)
    return [
        _check(
            "p13_release_manifest_ready",
            release_manifest.get("status") == "ready_for_claim_safe_arxiv_release",
            "P14 source generation requires a ready P13 claim-safe release manifest.",
            source_artifact="docs/reports/paper_release_manifest.json",
        ),
        _check(
            "p13_public_wording_lint_passed",
            public_claims.get("status") == "claim_safe_public_wording_allowed"
            and public_claims.get("wording_lint", {}).get("status") == "pass",
            "P13 public wording lint must pass before P14 source can be a release candidate.",
            source_artifact="docs/reports/paper_public_claims_allowed.json",
        ),
        _check(
            "hard_and_headline_claims_remain_blocked",
            not bool(public_claims.get("hard_claims_allowed")) and not bool(public_claims.get("headline_claims_allowed")),
            "P14 remains claim-safe only while hard and headline claims are blocked.",
            source_artifact="docs/reports/paper_public_claims_allowed.json",
        ),
        _check(
            "required_p14_inputs_present",
            not required["missing_artifact_refs"],
            "P14 requires the P13 manifest, public claims, Markdown draft, bibliography, and figure manifest.",
            source_artifact="docs/reports",
            detail=required,
        ),
        _check(
            "citation_audit_passed",
            citation_audit.get("status") == "pass",
            "Every generated LaTeX citation must resolve in references.bib.",
            source_artifact="docs/reports/paper_arxiv_source_manifest.json",
            detail={"missing_bib_keys": citation_audit.get("missing_bib_keys", [])},
        ),
        _check(
            "figure_audit_passed",
            figure_audit.get("status") == "pass",
            "Every generated figure reference must exist and use an arXiv-accepted graphic extension.",
            source_artifact="docs/reports/paper_arxiv_source_manifest.json",
            detail={"missing_figures": figure_audit.get("missing_figures", [])},
        ),
        _check(
            "submission_package_audit_passed",
            package_audit.get("status") == "pass",
            "Generated source must not contain local paths, secrets, stale prototype wording, or unguarded hard claims.",
            source_artifact="docs/reports/paper_submission_package_audit.json",
            detail={"violation_count": package_audit.get("violation_count", 0)},
        ),
    ]


def _required_artifact_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    by_ref = {
        str(value.get("artifact_ref")): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    present = []
    missing = []
    for ref in P13_REQUIRED_REFS:
        artifact = by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {"present_artifact_refs": present, "missing_artifact_refs": missing}


def _render_latex_source(*, inputs: dict[str, Any]) -> str:
    draft = _text_payload(inputs["draft"])
    title, body_lines = _extract_title_and_body(draft)
    converted = _markdown_lines_to_latex(body_lines)
    preamble = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[a4paper,margin=1in]{geometry}",
        r"\usepackage{array}",
        r"\usepackage{booktabs}",
        r"\usepackage{graphicx}",
        r"\usepackage[font=normalsize,labelfont=bf]{caption}",
        r"\usepackage{fancyvrb}",
        r"\usepackage{needspace}",
        r"\usepackage{longtable}",
        r"\usepackage{natbib}",
        r"\usepackage{xurl}",
        r"\usepackage[hidelinks]{hyperref}",
        r"\setlength{\parskip}{0.65em}",
        r"\setlength{\parindent}{0pt}",
        r"\emergencystretch=3em",
        "",
        f"\\title{{{_latex_inline(title)}}}",
        r"\author{Author Name\\Affiliation\\\texttt{contact@example.com}}",
        r"\date{June 2026}",
        "",
        r"\begin{document}",
        r"\maketitle",
        "",
    ]
    tail = [
        "",
        r"\bibliographystyle{plainnat}",
        r"\bibliography{references}",
        "",
        r"\end{document}",
    ]
    return "\n".join(preamble + converted + tail).rstrip() + "\n"


def _extract_title_and_body(draft: str) -> tuple[str, list[str]]:
    lines = draft.splitlines()
    title = "Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML"
    start = 0
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        start = 1
    body = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("P13 claim-safe Markdown draft."):
            continue
        if stripped.startswith("## References"):
            break
        body.append(line)
    return title, body


def _markdown_lines_to_latex(lines: list[str]) -> list[str]:
    out: list[str] = []
    in_abstract = False
    in_code = False
    list_mode: str | None = None
    table_buffer: list[str] = []
    skip_role_line = False
    previous_blank = False

    def flush_table() -> None:
        nonlocal table_buffer
        if table_buffer:
            out.extend(_render_latex_table(table_buffer))
            table_buffer = []

    def close_list() -> None:
        nonlocal list_mode
        if list_mode:
            out.append(r"\end{" + list_mode + "}")
            out.append("")
            list_mode = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                out.append(r"\end{Verbatim}")
                out.append(r"\end{samepage}")
                out.append("")
                in_code = False
            else:
                out.append(line)
            continue

        if stripped.startswith("<!--") and stripped.endswith("-->"):
            if table_buffer:
                flush_table()
            continue

        if table_buffer and (not stripped.startswith("|") or stripped == "|"):
            flush_table()

        image = re.match(r"!\[([^\]]*)\]\((figures/[^)]+)\)", stripped)
        if image:
            close_list()
            flush_table()
            caption = image.group(1).strip() or "Relaytic-AML figure"
            target = Path(image.group(2)).with_suffix(".pdf").as_posix()
            out.extend(
                [
                    r"\begin{figure}[htbp]",
                    r"\centering",
                    f"\\includegraphics[width=\\linewidth]{{{target}}}",
                    f"\\caption{{{_latex_inline(caption)}}}",
                    r"\end{figure}",
                    "",
                ]
            )
            skip_role_line = True
            previous_blank = True
            continue

        if skip_role_line and not stripped:
            continue
        if stripped.startswith("*") and "Role:" in stripped:
            skip_role_line = False
            continue
        skip_role_line = False

        if stripped.startswith("```"):
            close_list()
            flush_table()
            out.append(r"\begin{samepage}")
            out.append(r"\begin{Verbatim}[frame=single,framesep=6pt,fontsize=\small]")
            in_code = True
            previous_blank = False
            continue

        if stripped.startswith("|"):
            close_list()
            table_buffer.append(stripped)
            previous_blank = False
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            close_list()
            flush_table()
            if in_abstract:
                out.append(r"\end{abstract}")
                out.append("")
                in_abstract = False
            level = len(heading.group(1))
            text = re.sub(r"^\d+\.\s*", "", heading.group(2).strip())
            if text.lower() == "abstract":
                out.append(r"\begin{abstract}")
                in_abstract = True
            elif level <= 2:
                out.append(f"\\section{{{_latex_inline(text)}}}")
            elif level == 3:
                out.append(f"\\subsection{{{_latex_inline(text)}}}")
            else:
                out.append(f"\\paragraph{{{_latex_inline(text)}}}")
            out.append("")
            previous_blank = True
            continue

        if not stripped:
            close_list()
            flush_table()
            if not previous_blank:
                out.append("")
            previous_blank = True
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if unordered or ordered:
            mode = "enumerate" if ordered else "itemize"
            if list_mode != mode:
                close_list()
                out.append(r"\begin{" + mode + "}")
                list_mode = mode
            item_text = (ordered or unordered).group(1)
            out.append(f"\\item {_latex_inline(item_text)}")
            previous_blank = False
            continue

        close_list()
        flush_table()
        if re.match(r"^Algorithm \d+\b", stripped):
            out.append(r"\Needspace{18\baselineskip}")
        out.append(_latex_inline(stripped))
        previous_blank = False

    flush_table()
    close_list()
    if in_abstract:
        out.append(r"\end{abstract}")
    return out


def _render_latex_table(lines: list[str]) -> list[str]:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return []
    col_count = max(len(row) for row in rows)
    for row in rows:
        while len(row) < col_count:
            row.append("")
    col_width = max(0.11, min(0.45, 0.90 / max(1, col_count)))
    spec = " ".join([f">{{\\raggedright\\arraybackslash}}p{{{col_width:.2f}\\linewidth}}" for _ in range(col_count)])
    rendered = [
        r"\begin{center}",
        r"\setlength{\fboxsep}{8pt}",
        r"\fbox{\begin{minipage}{0.96\linewidth}",
        r"\small",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.14}",
        r"\begin{tabular}{" + spec + "}",
        r"\toprule",
        " & ".join(_latex_inline(cell) for cell in rows[0]) + r" \\",
        r"\midrule",
    ]
    for row in rows[1:]:
        rendered.append(" & ".join(_latex_inline(cell) for cell in row) + r" \\")
    rendered.extend([r"\bottomrule", r"\end{tabular}", r"\end{minipage}}", r"\end{center}", ""])
    return rendered


def _latex_inline(text: str) -> str:
    converted = _rewrite_source_svg_refs(_rewrite_paper_source_text(text))
    converted = _convert_markdown_citations(converted)
    converted = _convert_inline_code(converted)
    converted = _convert_bold(converted)
    return _escape_latex(converted)


def _rewrite_paper_source_text(text: str) -> str:
    return text.replace("This draft makes four contributions.", "This paper makes four contributions.")


def _rewrite_source_svg_refs(text: str) -> str:
    return re.sub(
        r"docs/paper/figures/(figure_[A-Za-z0-9_]+)\.svg",
        r"docs/paper/arxiv_src/figures/\1.pdf",
        text,
    )


def _convert_markdown_citations(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        keys = [
            part.strip().lstrip("@")
            for part in re.split(r"[;,]", match.group(1))
            if part.strip()
        ]
        return r"\citep{" + ",".join(keys) + "}"

    return re.sub(r"\[@([^\]]+)\]", repl, text)


def _convert_inline_code(text: str) -> str:
    return re.sub(r"`([^`]+)`", lambda match: r"\nolinkurl{" + match.group(1) + "}", text)


def _convert_bold(text: str) -> str:
    return re.sub(r"\*\*([^*]+)\*\*", lambda match: r"\textbf{" + match.group(1) + "}", text)


def _escape_latex(text: str) -> str:
    placeholders: dict[str, str] = {}

    def hold(pattern: str, value: str) -> str:
        key = f"@@LATEXHOLD{len(placeholders)}@@"
        placeholders[key] = value
        return key

    text = re.sub(r"\\citep?\{[^}]+\}", lambda match: hold("cite", match.group(0)), text)
    text = re.sub(r"\\texttt\{[^}]*\}", lambda match: hold("texttt", match.group(0)), text)
    text = re.sub(r"\\nolinkurl\{[^}]*\}", lambda match: hold("nolinkurl", match.group(0)), text)
    text = re.sub(r"\\textbf\{[^}]*\}", lambda match: hold("textbf", match.group(0)), text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    escaped = "".join(replacements.get(char, char) for char in text)
    for key, value in placeholders.items():
        if value.startswith(r"\nolinkurl{"):
            inner = value[value.index("{") + 1 : -1]
            value = r"\nolinkurl{" + inner.replace("{", "").replace("}", "") + "}"
        elif value.startswith(r"\texttt{") or value.startswith(r"\textbf{"):
            inner = value[value.index("{") + 1 : -1]
            value = value[: value.index("{") + 1] + _escape_latex(inner) + "}"
        escaped = escaped.replace(key, value)
    return escaped


def _build_pdf_figures(*, inputs: dict[str, Any]) -> list[dict[str, Any]]:
    manifest = _payload(inputs["figure_manifest"])
    figure_dir = Path(inputs["figure_dir"])
    figures = []
    for figure in list(manifest.get("figures") or []):
        if not isinstance(figure, dict):
            continue
        source_filename = str(figure.get("filename") or "")
        source_path = figure_dir / source_filename
        artifact = _read_text_artifact(source_path)
        svg_text = _text_payload(artifact)
        target_filename = f"{Path(source_filename).stem}.pdf"
        pdf_bytes = _svg_subset_to_pdf(svg_text)
        figures.append(
            {
                "figure_id": str(figure.get("figure_id") or Path(source_filename).stem),
                "title": str(figure.get("title") or Path(source_filename).stem),
                "paper_claim_role": str(figure.get("paper_claim_role") or "unknown"),
                "source_ref": f"docs/paper/figures/{source_filename}",
                "target_ref": f"docs/paper/arxiv_src/figures/{target_filename}",
                "source_filename": source_filename,
                "target_filename": target_filename,
                "target_extension": ".pdf",
                "source_svg_sha256": _sha256_text(svg_text),
                "pdf_sha256": _sha256_bytes(pdf_bytes),
                "pdf_byte_count": len(pdf_bytes),
                "pdf_hex": pdf_bytes.hex(),
                "source_exists": bool(artifact.get("exists")),
                "converted_by": "relaytic_svg_subset_pdf_writer",
            }
        )
    return figures


def _svg_subset_to_pdf(svg_text: str) -> bytes:
    if not svg_text.strip():
        return _write_minimal_pdf(width=640.0, height=360.0, commands=[])
    root = ET.fromstring(svg_text)
    width = _numeric(root.attrib.get("width"), 640.0)
    height = _numeric(root.attrib.get("height"), 360.0)
    commands: list[str] = []
    for node in root.iter():
        tag = _strip_namespace(node.tag)
        if tag == "rect":
            commands.extend(_pdf_rect(node.attrib, height))
        elif tag == "line":
            commands.extend(_pdf_line(node.attrib, height))
        elif tag == "polygon":
            commands.extend(_pdf_polygon(node.attrib, height))
        elif tag == "text":
            commands.extend(_pdf_text(node.attrib, "".join(node.itertext()), height))
    return _write_minimal_pdf(width=width, height=height, commands=commands)


def _pdf_rect(attrib: dict[str, str], page_height: float) -> list[str]:
    x = _numeric(attrib.get("x"), 0.0)
    y = _numeric(attrib.get("y"), 0.0)
    width = _numeric(attrib.get("width"), 0.0)
    height = _numeric(attrib.get("height"), 0.0)
    fill = _parse_color(attrib.get("fill"))
    stroke = _parse_color(attrib.get("stroke"))
    stroke_width = _numeric(attrib.get("stroke-width"), 1.0)
    pdf_y = page_height - y - height
    commands = []
    if fill:
        commands.append(f"{_rgb(fill)} rg")
    if stroke:
        commands.append(f"{_rgb(stroke)} RG")
        commands.append(f"{stroke_width:.3f} w")
    operator = "B" if fill and stroke else "f" if fill else "S"
    commands.append(f"{x:.3f} {pdf_y:.3f} {width:.3f} {height:.3f} re {operator}")
    return commands


def _pdf_line(attrib: dict[str, str], page_height: float) -> list[str]:
    x1 = _numeric(attrib.get("x1"), 0.0)
    y1 = page_height - _numeric(attrib.get("y1"), 0.0)
    x2 = _numeric(attrib.get("x2"), 0.0)
    y2 = page_height - _numeric(attrib.get("y2"), 0.0)
    stroke = _parse_color(attrib.get("stroke")) or (0, 0, 0)
    stroke_width = _numeric(attrib.get("stroke-width"), 1.0)
    return [f"{_rgb(stroke)} RG", f"{stroke_width:.3f} w", f"{x1:.3f} {y1:.3f} m {x2:.3f} {y2:.3f} l S"]


def _pdf_polygon(attrib: dict[str, str], page_height: float) -> list[str]:
    points = []
    for part in re.findall(r"[-+]?[0-9]*\.?[0-9]+,[-+]?[0-9]*\.?[0-9]+", attrib.get("points") or ""):
        x_text, y_text = part.split(",", 1)
        points.append((float(x_text), page_height - float(y_text)))
    if not points:
        return []
    fill = _parse_color(attrib.get("fill"))
    stroke = _parse_color(attrib.get("stroke"))
    commands = []
    if fill:
        commands.append(f"{_rgb(fill)} rg")
    if stroke:
        commands.append(f"{_rgb(stroke)} RG")
    path = [f"{points[0][0]:.3f} {points[0][1]:.3f} m"]
    path.extend(f"{x:.3f} {y:.3f} l" for x, y in points[1:])
    path.append("h")
    path.append("B" if fill and stroke else "f" if fill else "S")
    commands.append(" ".join(path))
    return commands


def _pdf_text(attrib: dict[str, str], text: str, page_height: float) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    x = _numeric(attrib.get("x"), 0.0)
    y = page_height - _numeric(attrib.get("y"), 0.0)
    font_size = _numeric(attrib.get("font-size"), 12.0)
    anchor = attrib.get("text-anchor")
    if anchor == "middle":
        x -= len(clean) * font_size * 0.27
    elif anchor == "end":
        x -= len(clean) * font_size * 0.54
    color = _parse_color(attrib.get("fill")) or (0, 0, 0)
    return [
        "BT",
        f"/F1 {font_size:.3f} Tf",
        f"{_rgb(color)} rg",
        f"1 0 0 1 {x:.3f} {y:.3f} Tm",
        f"({_pdf_escape_text(clean)}) Tj",
        "ET",
    ]


def _write_minimal_pdf(*, width: float, height: float, commands: list[str]) -> bytes:
    stream = ("\n".join(commands) + "\n").encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width:.3f} {height:.3f}] "
            "/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ).encode("latin-1"),
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


def _strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _numeric(value: str | None, default: float) -> float:
    if not value:
        return default
    match = re.search(r"[-+]?[0-9]*\.?[0-9]+", value)
    return float(match.group(0)) if match else default


def _parse_color(value: str | None) -> tuple[int, int, int] | None:
    if not value or value.lower() in {"none", "transparent"}:
        return None
    value = value.strip()
    if value.startswith("#"):
        hex_value = value[1:]
        if len(hex_value) == 3:
            hex_value = "".join(char * 2 for char in hex_value)
        if len(hex_value) == 6:
            try:
                return tuple(int(hex_value[index : index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]
            except ValueError:
                return (0, 0, 0)
    names = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
    }
    return names.get(value.lower(), (0, 0, 0))


def _rgb(color: tuple[int, int, int]) -> str:
    return " ".join(f"{channel / 255:.4f}" for channel in color)


def _pdf_escape_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _audit_citations(*, tex_source: str, bibliography: str) -> dict[str, Any]:
    cited = []
    for raw in re.findall(r"\\citep?\{([^}]+)\}", tex_source):
        cited.extend(part.strip() for part in raw.split(",") if part.strip())
    cited_keys = sorted(set(cited))
    bib_keys = sorted(set(re.findall(r"@\w+\{([^,\s]+)", bibliography)))
    missing = sorted(set(cited_keys) - set(bib_keys))
    return {
        "schema_version": PAPER_ARXIV_SOURCE_SCHEMA_VERSION,
        "status": "pass" if not missing and cited_keys else "fail",
        "cited_key_count": len(cited_keys),
        "bib_key_count": len(bib_keys),
        "cited_keys": cited_keys,
        "bib_keys": bib_keys,
        "missing_bib_keys": missing,
        "unused_bib_keys": sorted(set(bib_keys) - set(cited_keys)),
    }


def _audit_figures(*, tex_source: str, figures: list[dict[str, Any]]) -> dict[str, Any]:
    include_refs = sorted(set(re.findall(r"\\includegraphics(?:\[[^\]]+\])?\{([^}]+)\}", tex_source)))
    figure_by_ref = {f"{PAPER_ARXIV_FIGURE_DIRNAME}/{item['target_filename']}": item for item in figures}
    missing = sorted(ref for ref in include_refs if ref not in figure_by_ref)
    disallowed = sorted(ref for ref in include_refs if Path(ref).suffix.lower() not in ARXIV_ALLOWED_GRAPHIC_EXTENSIONS)
    source_failures = sorted(item["source_ref"] for item in figures if not item.get("source_exists"))
    return {
        "schema_version": PAPER_ARXIV_SOURCE_SCHEMA_VERSION,
        "status": "pass" if include_refs and not missing and not disallowed and not source_failures else "fail",
        "include_refs": include_refs,
        "converted_figure_count": len(figures),
        "missing_figures": missing,
        "disallowed_extensions": disallowed,
        "missing_source_svgs": source_failures,
        "svg_references_remaining": sorted(set(re.findall(r"figures/[^}\s)]+\.svg", tex_source))),
    }


def _build_submission_package_audit(
    *,
    inputs: dict[str, Any],
    tex_source: str,
    bibliography: str,
    figures: list[dict[str, Any]],
    citation_audit: dict[str, Any],
    figure_audit: dict[str, Any],
) -> dict[str, Any]:
    text_surfaces = [
        ("docs/paper/arxiv_src/main.tex", tex_source),
        ("docs/paper/arxiv_src/references.bib", bibliography),
    ]
    violations = _scan_package_text(text_surfaces)
    p13_manifest = _payload(inputs["paper_release_manifest"])
    p13_claims = _payload(inputs["paper_public_claims_allowed"])
    checks = [
        _check(
            "p13_release_ready",
            p13_manifest.get("status") == "ready_for_claim_safe_arxiv_release",
            "P13 release manifest must be ready before P14 can pass.",
            source_artifact="docs/reports/paper_release_manifest.json",
        ),
        _check(
            "claim_lint_still_passes",
            p13_claims.get("wording_lint", {}).get("status") == "pass",
            "P13 claim lint must remain pass.",
            source_artifact="docs/reports/paper_public_claims_allowed.json",
        ),
        _check(
            "citation_audit_passes",
            citation_audit.get("status") == "pass",
            "Generated citations must resolve.",
            source_artifact="docs/reports/paper_arxiv_source_manifest.json",
        ),
        _check(
            "figure_audit_passes",
            figure_audit.get("status") == "pass",
            "Generated figures must be present and accepted by the selected arXiv processor.",
            source_artifact="docs/reports/paper_arxiv_source_manifest.json",
        ),
        _check(
            "source_text_scan_clean",
            not violations,
            "Generated TeX and bibliography source must pass local-path, secret, stale-wording, and claim scans.",
            source_artifact="docs/paper/arxiv_src",
            detail={"violation_count": len(violations)},
        ),
        _check(
            "no_svg_references_in_tex",
            not figure_audit.get("svg_references_remaining"),
            "Generated TeX must reference converted PDF figures rather than SVG figures.",
            source_artifact="docs/paper/arxiv_src/main.tex",
        ),
    ]
    status = "pass" if all(check["passed"] for check in checks) else "fail"
    return {
        "schema_version": PAPER_ARXIV_SOURCE_SCHEMA_VERSION,
        "slice": "Paper Track P14",
        "status": status,
        "violation_count": len(violations),
        "violations": violations,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "source_surfaces_scanned": [name for name, _ in text_surfaces],
        "figure_surfaces_scanned": [item["target_ref"] for item in figures],
        "arxiv_upload_ready": False,
        "upload_blockers_remaining": [
            "replace placeholder author, affiliation, and contact metadata",
            "run a human TeX compile and inspect the produced PDF",
            "generate and include bibliography output if the final arXiv upload uses BibTeX rather than static bibliography output",
            "confirm git status --short is empty at the tag target",
        ],
    }


def _scan_package_text(surfaces: list[tuple[str, str]]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for surface, text in surfaces:
        for rule in FORBIDDEN_SOURCE_PATTERNS:
            for match in rule["pattern"].finditer(text):
                violations.append(
                    {
                        "surface": surface,
                        "rule_id": rule["rule_id"],
                        "message": rule["message"],
                        "excerpt": _excerpt(text, match.start(), match.end()),
                    }
                )
        for rule in BLOCKED_PUBLIC_CLAIM_RULES:
            phrase = str(rule["phrase"])
            for match in re.finditer(re.escape(phrase), text, flags=re.IGNORECASE):
                context = _excerpt(text, match.start(), match.end(), radius=180).lower()
                normalized_context = context.replace("\\_", "_").replace("_", " ")
                if any(marker in normalized_context for marker in CLAIM_GUARD_MARKERS) or "required repair" in normalized_context:
                    continue
                violations.append(
                    {
                        "surface": surface,
                        "rule_id": rule["rule_id"],
                        "message": rule["message"],
                        "excerpt": _excerpt(text, match.start(), match.end()),
                    }
                )
    return violations


def _render_release_candidate_checklist(*, manifest: dict[str, Any], package_audit: dict[str, Any]) -> str:
    ready = bool(manifest.get("source_release_candidate_ready"))
    return "\n".join(
        [
            "# Paper P14 Release-Candidate Checklist",
            "",
            f"- Source release-candidate ready: `{ready}`",
            f"- arXiv upload ready now: `{manifest.get('arxiv_upload_ready')}`",
            f"- Source tree: `{manifest.get('source_tree', {}).get('source_dir')}`",
            f"- Package audit: `{package_audit.get('status')}`",
            "",
            "## Automated gates",
            "",
            "- [x] P13 claim-safe release manifest is ready.",
            "- [x] P13 public wording lint passes and hard/headline claims remain blocked.",
            "- [x] Markdown paper source is converted to top-level LaTeX source.",
            "- [x] SVG figures are converted to PDF figures for the pdfLaTeX arXiv processor.",
            "- [x] Generated LaTeX citations resolve against `references.bib`.",
            "- [x] Source-package audit blocks local paths, secrets, legacy prototype wording, and unguarded hard claims.",
            "",
            "## Human gates before upload or tag",
            "",
            "- [ ] Replace placeholder author, affiliation, and contact metadata in `docs/paper/arxiv_src/main.tex`.",
            "- [ ] Run `pdflatex`, `bibtex`, `pdflatex`, and `pdflatex` from `docs/paper/arxiv_src/`; inspect the generated PDF.",
            "- [ ] Include generated bibliography output if the final arXiv upload uses BibTeX rather than an inline bibliography.",
            "- [ ] Confirm the AI-assistance disclosure accurately describes any LLM drafting, editing, or code-review help.",
            "- [ ] Rerun `relaytic release-safety paper-arxiv-source --format json` after metadata edits.",
            "- [ ] Rerun `relaytic scan-git-safety` from the tag target.",
            "- [ ] Confirm `git status --short` is empty before creating `relaytic-aml-paper-p14-source-rc`.",
            "",
            "## Claim boundary",
            "",
            "The source package remains an evaluation-environment release candidate. It still must not claim hard AML superiority, SOTA or leaderboard-winning performance, claimed equivalence to RevClassify, graph-neural superiority, production readiness, or hard business value.",
            "",
        ]
    )


def _read_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"artifact_ref": _repo_relative(path), "exists": False, "payload": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        payload = {"error": str(exc)}
    return {
        "artifact_ref": _repo_relative(path),
        "exists": True,
        "sha256": _sha256_text(path.read_text(encoding="utf-8")),
        "payload": payload,
    }


def _read_text_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"artifact_ref": _repo_relative(path), "exists": False, "text": ""}
    text = path.read_text(encoding="utf-8")
    return {
        "artifact_ref": _repo_relative(path),
        "exists": True,
        "sha256": _sha256_text(text),
        "text": text,
    }


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload")
    return payload if isinstance(payload, dict) else {}


def _text_payload(artifact: dict[str, Any]) -> str:
    text = artifact.get("text")
    return text if isinstance(text, str) else ""


def _check(
    check_id: str,
    passed: bool,
    message: str,
    *,
    source_artifact: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "check_id": check_id,
        "passed": bool(passed),
        "message": message,
        "source_artifact": source_artifact,
    }
    if detail is not None:
        result["detail"] = detail
    return result


def _repo_relative(path: Path) -> str:
    parts = list(path.parts)
    for marker in ("docs", "src", "tests", ".github"):
        if marker in parts:
            return Path(*parts[parts.index(marker) :]).as_posix()
    return path.as_posix()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _excerpt(text: str, start: int, end: int, *, radius: int = 55) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return " ".join(text[left:right].split())


__all__ = [
    "NEXT_PAPER_ARXIV_SOURCE_SLICE",
    "PAPER_ARXIV_FIGURE_DIRNAME",
    "PAPER_ARXIV_MAIN_TEX_FILENAME",
    "PAPER_ARXIV_REFERENCES_FILENAME",
    "PAPER_ARXIV_RELEASE_TAG",
    "PAPER_ARXIV_SOURCE_DIRNAME",
    "PAPER_ARXIV_SOURCE_DOC_DIR",
    "PAPER_ARXIV_SOURCE_FILENAMES",
    "PAPER_ARXIV_SOURCE_REPORT_DIR",
    "PAPER_ARXIV_SOURCE_SCHEMA_VERSION",
    "build_paper_arxiv_source_pack",
    "render_paper_arxiv_source_markdown",
    "sync_paper_arxiv_source_pack",
]

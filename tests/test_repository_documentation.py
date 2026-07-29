from __future__ import annotations

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def _tracked_markdown() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        PROJECT_ROOT / relative_path
        for relative_path in result.stdout.splitlines()
        if (PROJECT_ROOT / relative_path).is_file()
    ]


def test_public_documentation_has_no_career_or_prompt_framing() -> None:
    forbidden = (
        "get me hired",
        "hiring signal",
        "earn attention",
        "attention-seeking public",
        "top labs",
        "career page",
        "paypal-style",
        "cto-grade",
        "product deserves",
        "frontier-worthy",
        "construction site",
    )
    findings: list[str] = []
    for path in _tracked_markdown():
        content = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            if phrase in content:
                findings.append(f"{path.relative_to(PROJECT_ROOT)}: {phrase}")

    assert findings == []
    assert not (PROJECT_ROOT / "Paper_Imp.md").exists()
    assert not (PROJECT_ROOT / "docs" / "paper" / "docs").exists()


def test_current_status_and_document_roles_are_explicit() -> None:
    status = _read("IMPLEMENTATION_STATUS.md")
    docs_index = _read("docs/README.md")
    build_archive = _read("docs/build_slices/README.md")
    reports_index = _read("docs/reports/README.md")
    paper_readme = _read("docs/paper/README.md")

    assert "Paper Track `P0` through `P27` is implemented." in status
    assert "Slice `16A`" in status
    assert "Reader Documentation" in docs_index
    assert "Historical Build Records" in docs_index
    assert "product slices `00` through `15Z-R` are implemented" in build_archive
    assert "stage-scoped paper" in docs_index
    assert "evidence. These files are useful for audits" in docs_index
    assert "do not replace" in reports_index
    assert "records the P11 evidence-draft stage" in paper_readme


def test_shipped_workspace_contracts_do_not_describe_slice_12d_as_future() -> None:
    contract_paths = (
        "docs/specs/workspace_lifecycle.md",
        "docs/specs/result_contract_schema.md",
        "docs/specs/governed_learnings_schema.md",
        "docs/specs/handoff_result_migration.md",
        "docs/specs/external_agent_continuation_contract.md",
        "docs/specs/learnings_migration_contract.md",
    )
    stale_phrases = (
        "once Slice 12D lands",
        "When Slice 12D lands",
        "After Slice 12D lands",
        "Before Slice 12D lands",
        "Future role:",
        "Future tests should prove:",
    )
    findings = [
        f"{relative_path}: {phrase}"
        for relative_path in contract_paths
        for phrase in stale_phrases
        if phrase in _read(relative_path)
    ]

    assert findings == []


def test_generated_paper_intermediates_identify_their_historical_stage() -> None:
    thesis = _read("docs/paper/paper_thesis.md")
    draft = _read("docs/paper/relaytic_aml_draft.md")

    assert "Historical pipeline status" in thesis
    assert "Next Slice At The P2 Freeze" in thesis
    assert "Historical pipeline status" in draft
    assert "Paper Track P0-P27 is implemented" in draft

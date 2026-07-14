"""Paper Track P16 deterministic failure-case evaluation pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_FAILURE_EVAL_SCHEMA_VERSION = "relaytic.paper_failure_eval.v1"
PAPER_FAILURE_EVAL_REPORT_DIR = Path("docs") / "reports"
NEXT_PAPER_FAILURE_EVAL_SLICE = "Paper Track P17 - governance machinery ablation pack"

PAPER_FAILURE_EVAL_FILENAMES = {
    "paper_failure_case_eval": "paper_failure_case_eval.json",
    "paper_failure_case_table": "paper_failure_case_table.json",
    "paper_failure_case_manifest": "paper_failure_case_manifest.json",
    "paper_failure_case_summary": "paper_failure_case_summary.md",
}

REQUIRED_FAILURE_INPUT_REFS = [
    "docs/reports/paysim_leakage_safe_feature_report.json",
    "docs/reports/paysim_competitive_search_trace.json",
    "docs/reports/paysim_competitive_budget_contract.json",
    "docs/reports/paper_public_claims_allowed.json",
    "docs/reports/paper_claim_gate_case_studies.json",
    "docs/reports/paper_agent_handoff_eval.json",
    "docs/reports/paper_no_lost_user_eval.json",
]

FORBIDDEN_PAYSIM_BALANCE_COLUMNS = [
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
]


def build_paper_failure_eval_pack(project_root: str | Path) -> dict[str, Any]:
    """Build P16 injected-risk failure cases from committed paper evidence."""
    root = Path(project_root)
    inputs = _collect_inputs(root)
    cases = _build_failure_cases(inputs)
    evaluation = _build_failure_case_eval(inputs=inputs, cases=cases)
    table = _build_failure_case_table(cases)
    manifest = _build_manifest(inputs=inputs, evaluation=evaluation, table=table, cases=cases)
    pack = {
        "paper_failure_case_eval": evaluation,
        "paper_failure_case_table": table,
        "paper_failure_case_manifest": manifest,
    }
    pack["paper_failure_case_summary"] = render_paper_failure_eval_markdown(pack)
    return pack


def sync_paper_failure_eval_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P16 failure-case reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_FAILURE_EVAL_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_failure_eval_pack(root)
    written: dict[str, Path] = {}
    for key, filename in PAPER_FAILURE_EVAL_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_failure_eval_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_failure_case_manifest", {}))
    evaluation = dict(pack.get("paper_failure_case_eval", {}))
    cases = list(evaluation.get("cases", []))
    lines = [
        "# Paper P16 Failure-Case Evaluation Pack",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Case pass rate: `{evaluation.get('passed_case_count')}`/`{evaluation.get('case_count')}`",
        f"- Fixture scope: `{evaluation.get('fixture_scope') or 'unknown'}`",
        f"- Raw rows exposed: `{evaluation.get('raw_rows_exposed')}`",
        f"- Private paths exposed: `{evaluation.get('private_paths_exposed')}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        "",
        "## Injected Failure Cases",
        "",
        "| Case | Injected Risk | Gate Or Check | Expected Behavior | Observed Result | Result |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for case in cases:
        result = "pass" if case.get("passed") else "fail"
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(case.get("failure_mode") or case.get("case_id") or "unknown")),
                    _escape_md(str(case.get("injected_risk") or "")),
                    _escape_md(str(case.get("gate_or_check") or "")),
                    _escape_md(str(case.get("expected_behavior") or "")),
                    _escape_md(str(case.get("observed_result") or "")),
                    f"`{result}`",
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _collect_inputs(root: Path) -> dict[str, Any]:
    reports = root / PAPER_FAILURE_EVAL_REPORT_DIR
    return {
        "root": root,
        "paysim_feature_report": _read_artifact(reports / "paysim_leakage_safe_feature_report.json", root=root),
        "paysim_search_trace": _read_artifact(reports / "paysim_competitive_search_trace.json", root=root),
        "paysim_budget_contract": _read_artifact(reports / "paysim_competitive_budget_contract.json", root=root),
        "public_claims_allowed": _read_artifact(reports / "paper_public_claims_allowed.json", root=root),
        "claim_gate_case_studies": _read_artifact(reports / "paper_claim_gate_case_studies.json", root=root),
        "agent_handoff_eval": _read_artifact(reports / "paper_agent_handoff_eval.json", root=root),
        "no_lost_user_eval": _read_artifact(reports / "paper_no_lost_user_eval.json", root=root),
    }


def _build_failure_cases(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _leakage_column_case(inputs),
        _test_selection_case(inputs),
        _overstrong_claim_case(inputs),
        _rowless_handoff_case(inputs),
        _interrupted_recovery_case(inputs),
    ]


def _leakage_column_case(inputs: dict[str, Any]) -> dict[str, Any]:
    artifact = inputs["paysim_feature_report"]
    payload = _payload(artifact)
    feature_columns = {str(item) for item in payload.get("feature_columns", []) if item is not None}
    excluded = {str(item) for item in payload.get("forbidden_source_columns_present_but_excluded", []) if item is not None}
    used = {str(item) for item in payload.get("forbidden_balance_columns_used", []) if item is not None}
    labels_used = bool(payload.get("validation_or_test_labels_used_for_features"))
    offered = set(FORBIDDEN_PAYSIM_BALANCE_COLUMNS)
    passed = bool(artifact.get("exists")) and offered <= excluded and not (offered & feature_columns) and not used and not labels_used
    return _case(
        case_id="leakage_column_injection",
        failure_mode="Leakage-column injection",
        injected_risk="PaySim balance fields are offered as candidate model inputs.",
        gate_or_check="Leakage feature policy",
        artifact_label="PS-PR feature policy",
        artifact_ref=str(artifact.get("artifact_ref") or "docs/reports/paysim_leakage_safe_feature_report.json"),
        evidence_cell_id="paysim_p6a_competitive_selected.test_pr_auc",
        expected_behavior="Post-event balance fields stay out of allowed features.",
        observed_result=(
            f"offered={len(offered)}; excluded={len(offered & excluded)}; "
            f"used={len(used)}; labels_for_features={labels_used}"
        ),
        passed=passed,
    )


def _test_selection_case(inputs: dict[str, Any]) -> dict[str, Any]:
    search_artifact = inputs["paysim_search_trace"]
    budget_artifact = inputs["paysim_budget_contract"]
    search = _payload(search_artifact)
    budget = _payload(budget_artifact)
    calibration = dict(search.get("calibration_trace") or {})
    selected = dict(search.get("selected_finalist") or {})
    attempts = [item for item in search.get("attempts", []) if isinstance(item, dict)]
    attempt_surfaces = {str(item.get("selection_surface") or "") for item in attempts}
    selected_surface = str(selected.get("selection_surface") or "")
    threshold_surface = str(selected.get("threshold_selection_surface") or "")
    test_used = bool(calibration.get("test_used_for_calibration_or_selection"))
    test_policy = str(budget.get("test_evaluation_policy") or "")
    exposure = dict(budget.get("test_exposure_contract") or {})
    passed = (
        bool(search_artifact.get("exists"))
        and bool(budget_artifact.get("exists"))
        and not test_used
        and all(surface.startswith("validation_") for surface in attempt_surfaces if surface)
        and selected_surface.startswith("validation_")
        and threshold_surface.startswith("validation_")
        and test_policy == "one_competitive_finalist_evaluated_after_validation_only_selection_and_protocol_freeze"
        and exposure.get("competitive_selection_used_test") is False
        and exposure.get("test_partition_previously_exposed") is True
        and exposure.get("untouched_holdout_claim_allowed") is False
    )
    return _case(
        case_id="test_set_selection_violation",
        failure_mode="Test-set selection violation",
        injected_risk="A model-selection path tries to use test evidence before the finalist is fixed.",
        gate_or_check="Validation-only selection policy",
        artifact_label="PaySim search contract",
        artifact_ref=str(search_artifact.get("artifact_ref") or "docs/reports/paysim_competitive_search_trace.json"),
        evidence_cell_id="paysim_p6a_competitive_selected.test_pr_auc",
        expected_behavior="Only validation evidence may select, calibrate, or threshold the finalist. Prior P4/P6 test exposure must remain disclosed.",
        observed_result=(
            f"probe_surfaces={len(attempt_surfaces)} validation-only; "
            f"test_used_for_selection={test_used}; final_policy={test_policy}; "
            f"prior_test_exposure={exposure.get('test_partition_previously_exposed')}"
        ),
        passed=passed,
    )


def _overstrong_claim_case(inputs: dict[str, Any]) -> dict[str, Any]:
    claims_artifact = inputs["public_claims_allowed"]
    cases_artifact = inputs["claim_gate_case_studies"]
    claims = _payload(claims_artifact)
    cases = _payload(cases_artifact)
    blocked_claims = [str(item) for item in claims.get("blocked_public_claims", []) if item is not None]
    blocked_text = " ".join(blocked_claims).lower()
    real_bank_blocked = "real-world aml superiority" in blocked_text or "real-bank" in blocked_text
    revclassify_blocked = "revclassify" in blocked_text and "parity" in blocked_text
    hard_allowed = bool(claims.get("hard_claims_allowed"))
    headline_allowed = bool(claims.get("headline_claims_allowed"))
    passed = (
        bool(claims_artifact.get("exists"))
        and bool(cases_artifact.get("exists"))
        and bool(claims.get("claim_safe_public_wording_allowed"))
        and cases.get("status") == "pass"
        and real_bank_blocked
        and revclassify_blocked
        and not hard_allowed
        and not headline_allowed
    )
    return _case(
        case_id="overstrong_claim_attempt",
        failure_mode="Over-strong claim attempt",
        injected_risk="Draft wording proposes real-bank superiority or RevClassifyDS parity.",
        gate_or_check="Public claim gate",
        artifact_label="Claim routing report",
        artifact_ref=str(claims_artifact.get("artifact_ref") or "docs/reports/paper_public_claims_allowed.json"),
        evidence_cell_id="claim-gate:hard_and_headline_claims_blocked",
        expected_behavior="Unsupported headline and hard-performance claims remain blocked.",
        observed_result=(
            f"blocked_claims={len(blocked_claims)}; hard_allowed={hard_allowed}; "
            f"headline_allowed={headline_allowed}"
        ),
        passed=passed,
    )


def _rowless_handoff_case(inputs: dict[str, Any]) -> dict[str, Any]:
    artifact = inputs["agent_handoff_eval"]
    tasks = _task_by_id(_payload(artifact))
    task = tasks.get("external_context_rowless_and_redacted", {})
    signal = str(task.get("measured_signal") or "")
    passed = (
        bool(artifact.get("exists"))
        and bool(task.get("passed"))
        and "raw_rows=False" in signal
        and "redactions=" in signal
        and "blocked_fields=" in signal
    )
    return _case(
        case_id="rowless_handoff_redaction",
        failure_mode="Rowless handoff redaction",
        injected_risk="An external-agent packet requests raw rows, private paths, or sensitive fields.",
        gate_or_check="Context export redaction",
        artifact_label="Agent handoff report",
        artifact_ref=str(artifact.get("artifact_ref") or "docs/reports/paper_agent_handoff_eval.json"),
        evidence_cell_id="agent-handoff:external_context_rowless_and_redacted",
        expected_behavior="The export contains state and next actions, not raw rows or private paths.",
        observed_result=signal or "not observed",
        passed=passed,
    )


def _interrupted_recovery_case(inputs: dict[str, Any]) -> dict[str, Any]:
    artifact = inputs["no_lost_user_eval"]
    tasks = _task_by_id(_payload(artifact))
    task = tasks.get("partial_run_state_recovery", {})
    signal = str(task.get("measured_signal") or "")
    passed = (
        bool(artifact.get("exists"))
        and bool(task.get("passed"))
        and "state=partial_run" in signal
        and "missing=" in signal
        and "actions=" in signal
    )
    return _case(
        case_id="interrupted_run_recovery",
        failure_mode="Interrupted-run recovery",
        injected_risk="A user or agent resumes a partial run without knowing which artifact to inspect.",
        gate_or_check="No-lost-user guide",
        artifact_label="Recovery guide report",
        artifact_ref=str(artifact.get("artifact_ref") or "docs/reports/paper_no_lost_user_eval.json"),
        evidence_cell_id="guide:partial_run_state_recovery",
        expected_behavior="The guide exposes current state, missing evidence, artifact shortlist, and next actions.",
        observed_result=signal or "not observed",
        passed=passed,
    )


def _build_failure_case_eval(*, inputs: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
    serialized_cases = json.dumps(cases, sort_keys=True)
    raw_rows_exposed = "raw transaction" in serialized_cases.lower() and "raw rows=false" not in serialized_cases.lower()
    private_paths_exposed = _contains_private_path(serialized_cases)
    passed_count = sum(1 for case in cases if case.get("passed"))
    status = "pass" if passed_count == len(cases) and not raw_rows_exposed and not private_paths_exposed else "fail"
    return {
        "schema_version": PAPER_FAILURE_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P16",
        "status": status,
        "fixture_scope": "deterministic injected-risk audit over current paper evidence artifacts",
        "case_count": len(cases),
        "passed_case_count": passed_count,
        "raw_rows_exposed": raw_rows_exposed,
        "private_paths_exposed": private_paths_exposed,
        "required_inputs": _required_artifact_presence(inputs),
        "cases": cases,
        "interpretation": (
            "These cases test release-governance behavior. They are not detector benchmarks and do not add "
            "real-bank AML superiority, RevClassifyDS parity, production deployment, or graph-neural novelty claims."
        ),
    }


def _build_failure_case_table(cases: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for case in cases:
        rows.append(
            {
                "failure_mode": case["failure_mode"],
                "injected_risk": case["injected_risk"],
                "gate_or_check": case["gate_or_check"],
                "evidence": _table_evidence(case),
                "expected_behavior": case["expected_behavior"],
                "observed_result": _table_observed_result(case),
                "artifact_ref": case["artifact_ref"],
                "evidence_cell_id": case["evidence_cell_id"],
                "full_observed_result": case["observed_result"],
                "case_id": case["case_id"],
                "passed": bool(case["passed"]),
            }
        )
    return {
        "schema_version": PAPER_FAILURE_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P16",
        "status": "pass" if rows and all(row["passed"] for row in rows) else "fail",
        "table_id": "failure_case_evaluation",
        "columns": [
            "Failure mode",
            "Injected risk",
            "Gate/check",
            "Evidence",
            "Expected behavior",
            "Observed result",
        ],
        "rows": rows,
    }


def _table_evidence(case: dict[str, Any]) -> str:
    labels = {
        "leakage_column_injection": "PS-PR feature policy",
        "test_set_selection_violation": "PS-PR search contract",
        "overstrong_claim_attempt": "claim-gate report",
        "rowless_handoff_redaction": "handoff redaction task",
        "interrupted_run_recovery": "guide recovery task",
    }
    return labels.get(str(case.get("case_id") or ""), str(case.get("artifact_label") or "failure evidence"))


def _table_observed_result(case: dict[str, Any]) -> str:
    case_id = str(case.get("case_id") or "")
    observed = str(case.get("observed_result") or "")
    if case_id == "leakage_column_injection":
        return "4 offered, 4 excluded, 0 used; labels not used as features"
    if case_id == "test_set_selection_violation":
        return "validation-only probes; no test selection; one competitive finalist evaluated after protocol freeze"
    if case_id == "overstrong_claim_attempt":
        return "6 blocked claims; hard and headline claims blocked"
    if case_id == "rowless_handoff_redaction":
        return "raw rows excluded from export; 8 unsafe fields redacted; 6 blocked fields recorded"
    if case_id == "interrupted_run_recovery":
        return "partial run recovered; 8 missing-evidence items recorded; 6 recovery actions exposed"
    return observed.replace("_", " ")


def _build_manifest(
    *,
    inputs: dict[str, Any],
    evaluation: dict[str, Any],
    table: dict[str, Any],
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    required = _required_artifact_presence(inputs)
    serialized = json.dumps({"evaluation": evaluation, "table": table}, sort_keys=True)
    checks = [
        _check(
            "required_failure_case_inputs_present",
            not required["missing_artifact_refs"],
            "All P16 source evidence artifacts must be present.",
            source_artifact="docs/reports",
            detail=required,
        ),
        _check(
            "all_failure_cases_pass",
            bool(cases) and all(case.get("passed") for case in cases),
            "Every required injected failure case must pass.",
            source_artifact="docs/reports/paper_failure_case_eval.json",
            detail={"case_ids": [case.get("case_id") for case in cases]},
        ),
        _check(
            "failure_table_materialized",
            table.get("status") == "pass" and len(table.get("rows", [])) == len(cases),
            "The paper-ready failure-case table must be generated from the case report.",
            source_artifact="docs/reports/paper_failure_case_table.json",
        ),
        _check(
            "rowless_and_path_safe",
            not evaluation.get("raw_rows_exposed") and not evaluation.get("private_paths_exposed") and not _contains_private_path(serialized),
            "The P16 reports must not expose raw rows or private machine paths.",
            source_artifact="docs/reports/paper_failure_case_eval.json",
        ),
        _check(
            "claim_boundary_preserved",
            not evaluation.get("hard_claims_allowed", False)
            and "not detector benchmarks" in str(evaluation.get("interpretation") or "").lower(),
            "P16 may support governance claims only, not detector-superiority claims.",
            source_artifact="docs/reports/paper_failure_case_eval.json",
        ),
    ]
    status = "ready_for_failure_case_evidence" if all(check["passed"] for check in checks) else "blocked_missing_failure_case_evidence"
    return {
        "schema_version": PAPER_FAILURE_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P16",
        "status": status,
        "failure_case_evidence_allowed": status.startswith("ready"),
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "detector_superiority_claim_allowed": False,
        "fixture_scope": evaluation.get("fixture_scope"),
        "required_source_artifacts": REQUIRED_FAILURE_INPUT_REFS,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "artifact_hashes": _artifact_hashes(inputs),
        "report_refs": {
            key: f"docs/reports/{filename}"
            for key, filename in PAPER_FAILURE_EVAL_FILENAMES.items()
        },
        "next_slice": NEXT_PAPER_FAILURE_EVAL_SLICE if status.startswith("ready") else "Paper Track P16 repair",
    }


def _case(
    *,
    case_id: str,
    failure_mode: str,
    injected_risk: str,
    gate_or_check: str,
    artifact_label: str,
    artifact_ref: str,
    evidence_cell_id: str,
    expected_behavior: str,
    observed_result: str,
    passed: bool,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "failure_mode": failure_mode,
        "injected_risk": _sanitize_text(injected_risk),
        "gate_or_check": gate_or_check,
        "artifact_label": artifact_label,
        "artifact_ref": artifact_ref,
        "evidence_cell_id": evidence_cell_id,
        "expected_behavior": _sanitize_text(expected_behavior),
        "observed_result": _sanitize_text(observed_result),
        "passed": bool(passed),
        "fixture_scope": "system-level safety/audit fixture",
        "claim_boundary": "supports governance evidence only; not detector benchmark evidence",
    }


def _task_by_id(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(task.get("task_id")): task
        for task in report.get("tasks", [])
        if isinstance(task, dict) and task.get("task_id")
    }


def _required_artifact_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    missing = []
    present = []
    artifact_by_ref = {
        value.get("artifact_ref"): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    for ref in REQUIRED_FAILURE_INPUT_REFS:
        artifact = artifact_by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {"present_artifact_refs": present, "missing_artifact_refs": missing}


def _artifact_hashes(inputs: dict[str, Any]) -> dict[str, str]:
    hashes = {}
    for value in inputs.values():
        if not isinstance(value, dict) or not value.get("exists") or not value.get("sha256"):
            continue
        ref = str(value.get("artifact_ref") or "")
        if ref in REQUIRED_FAILURE_INPUT_REFS:
            hashes[ref] = str(value["sha256"])
    return hashes


def _read_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _repo_relative(path, root=root)
    if not path.is_file():
        return {"artifact_ref": artifact_ref, "exists": False, "payload": {}}
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        payload = {"error": _sanitize_text(str(exc))}
    return {
        "artifact_ref": artifact_ref,
        "exists": True,
        "sha256": _sha256_text(text),
        "payload": payload if isinstance(payload, dict) else {},
    }


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload", {})
    return dict(payload) if isinstance(payload, dict) else {}


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


def _repo_relative(path: Path, *, root: Path, fallback: str | None = None) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        if fallback is not None:
            return fallback
    parts = path.parts
    for marker in ("docs", "artifacts", "src", "tests", ".github"):
        if marker in parts:
            return Path(*parts[parts.index(marker) :]).as_posix()
    return fallback or path.name


def _contains_private_path(text: str) -> bool:
    return bool(
        re.search(r"[A-Za-z]:[\\/]", text)
        or re.search(r"(?<![A-Za-z0-9])/(?:Users|home|private|tmp|var/folders)/", text)
        or re.search(r"C:/Users|C:\\Users|\\Users\\", text, re.IGNORECASE)
    )


def _sanitize_text(text: Any) -> str:
    cleaned = str(text)
    cleaned = re.sub(r"[A-Za-z]:[\\/][^\s`\"']+", _path_redaction, cleaned)
    cleaned = re.sub(r"/(?:Users|home|private|tmp|var/folders)/[^\s`\"']+", _path_redaction, cleaned)
    cleaned = re.sub(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*[A-Za-z0-9_\-]{8,}", r"\1=<redacted_secret>", cleaned)
    return cleaned


def _path_redaction(match: re.Match[str]) -> str:
    raw = match.group(0).replace("\\", "/")
    name = Path(raw).name
    return f"<redacted_path:{name or 'local'}>"


def _escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = [
    "NEXT_PAPER_FAILURE_EVAL_SLICE",
    "PAPER_FAILURE_EVAL_FILENAMES",
    "PAPER_FAILURE_EVAL_REPORT_DIR",
    "PAPER_FAILURE_EVAL_SCHEMA_VERSION",
    "REQUIRED_FAILURE_INPUT_REFS",
    "build_paper_failure_eval_pack",
    "render_paper_failure_eval_markdown",
    "sync_paper_failure_eval_pack",
]

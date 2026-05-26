"""Hard graph-track readiness decisions for Paper Track P8."""

from __future__ import annotations

import csv
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_HARD_GRAPH_SCHEMA_VERSION = "relaytic.paper_hard_graph_track_decision.v1"
PAPER_HARD_GRAPH_REPORT_DIR = Path("docs") / "reports"
PAPER_HARD_GRAPH_FILENAMES = {
    "amlsim_generation_manifest": "amlsim_generation_manifest.json",
    "amlsim_typology_manifest": "amlsim_typology_manifest.json",
    "elliptic2_subgraph_access_report": "elliptic2_subgraph_access_report.json",
    "subgraph_benchmark_blocker_report": "subgraph_benchmark_blocker_report.json",
}
DEFAULT_ELLIPTIC2_DIR = Path("data") / "paper_benchmarks" / "elliptic2"
DEFAULT_AMLSIM_DIR = Path("data") / "paper_benchmarks" / "amlsim"
ELLIPTIC2_REQUIRED_FILES = [
    "background_edges.csv",
    "background_nodes.csv",
    "connected_components.csv",
    "edges.csv",
    "nodes.csv",
]
ELLIPTIC2_OPTIONAL_FILES = ["dataset-metadata.json", "README.md"]
AMLSIM_REQUIRED_FILES = ["conf.json", "tx_log.csv", "alert_transactions.csv", "sar_accounts.csv"]
AMLSIM_OPTIONAL_FILES = ["generator_commit.txt", "generated_dataset_manifest.json"]


def build_paper_hard_graph_track_pack(
    project_root: str | Path,
    *,
    elliptic2_dir: str | Path | None = None,
    amlsim_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build P8 supported/proxy/blocked artifacts without downloading sources."""
    root = Path(project_root)
    resolved_elliptic2_dir = _resolve_dir(root, elliptic2_dir, DEFAULT_ELLIPTIC2_DIR)
    resolved_amlsim_dir = _resolve_dir(root, amlsim_dir, DEFAULT_AMLSIM_DIR)
    registry = _read_json(root / "docs" / "reports" / "paper_dataset_registry.json")
    splits = _read_json(root / "docs" / "reports" / "paper_split_contracts.json")
    elliptic2_spec = _find_item(registry.get("datasets", []), "dataset_id", "elliptic2_subgraph_aml")
    amlsim_spec = _find_item(registry.get("datasets", []), "dataset_id", "amlsim_synthetic_bank_graph")
    elliptic2_split = _find_item(splits.get("contracts", []), "dataset_id", "elliptic2_subgraph_aml")
    amlsim_split = _find_item(splits.get("contracts", []), "dataset_id", "amlsim_synthetic_bank_graph")

    amlsim_generation = _build_amlsim_generation_manifest(
        root=root,
        data_dir=resolved_amlsim_dir,
        dataset_spec=amlsim_spec,
        split_contract=amlsim_split,
    )
    amlsim_typology = _build_amlsim_typology_manifest(
        root=root,
        data_dir=resolved_amlsim_dir,
        generation_manifest=amlsim_generation,
        split_contract=amlsim_split,
    )
    elliptic2_access = _build_elliptic2_access_report(
        root=root,
        data_dir=resolved_elliptic2_dir,
        dataset_spec=elliptic2_spec,
        split_contract=elliptic2_split,
    )
    blocker_report = _build_blocker_report(
        root=root,
        amlsim_generation=amlsim_generation,
        amlsim_typology=amlsim_typology,
        elliptic2_access=elliptic2_access,
    )
    return {
        "amlsim_generation_manifest": amlsim_generation,
        "amlsim_typology_manifest": amlsim_typology,
        "elliptic2_subgraph_access_report": elliptic2_access,
        "subgraph_benchmark_blocker_report": blocker_report,
    }


def sync_paper_hard_graph_track_pack(
    project_root: str | Path,
    *,
    elliptic2_dir: str | Path | None = None,
    amlsim_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P8 artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_HARD_GRAPH_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paper_hard_graph_track_pack(
        root,
        elliptic2_dir=elliptic2_dir,
        amlsim_dir=amlsim_dir,
    )
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in PAPER_HARD_GRAPH_FILENAMES.items()
    }


def render_paper_hard_graph_track_markdown(pack: dict[str, Any]) -> str:
    report = dict(pack.get("subgraph_benchmark_blocker_report", {}))
    tracks = {row["dataset_id"]: row for row in report.get("track_decisions", [])}
    elliptic2 = tracks.get("elliptic2_subgraph_aml", {})
    amlsim = tracks.get("amlsim_synthetic_bank_graph", {})
    return "\n".join(
        [
            "# Paper Hard Graph Track Decision",
            "",
            f"- Status: `{report.get('decision_state') or 'unknown'}`",
            f"- Elliptic2 state: `{elliptic2.get('support_level') or 'unknown'}`",
            f"- AMLSim state: `{amlsim.get('support_level') or 'unknown'}`",
            f"- Hard performance claims allowed: `{report.get('hard_performance_claims_allowed')}`",
            f"- Paper may continue to P9: `{report.get('paper_can_continue_to_p9')}`",
            f"- Next slice: `{report.get('next_slice') or 'unknown'}`",
        ]
    )


def _build_amlsim_generation_manifest(
    *,
    root: Path,
    data_dir: Path,
    dataset_spec: dict[str, Any],
    split_contract: dict[str, Any],
) -> dict[str, Any]:
    required_checks = _check_files(root, data_dir, AMLSIM_REQUIRED_FILES)
    optional_checks = _check_files(root, data_dir, AMLSIM_OPTIONAL_FILES)
    by_name = {row["filename"]: row for row in required_checks + optional_checks}
    missing_required = [row["filename"] for row in required_checks if not row["exists"]]
    blockers: list[dict[str, str]] = []
    if missing_required:
        blockers.append(
            _blocker(
                "amlsim_local_generated_bundle_missing",
                "Generated AMLSim files are not locally present and cannot support a paper run.",
                "Generate a frozen AMLSim bundle locally with one declared configuration and temporal split contract.",
            )
        )
    if not by_name["generator_commit.txt"]["exists"]:
        blockers.append(
            _blocker(
                "amlsim_generator_commit_not_frozen",
                "The AMLSim generator revision has not been recorded.",
                "Write the exact generator commit to `generator_commit.txt` beside generated files.",
            )
        )
    if not by_name["generated_dataset_manifest.json"]["exists"]:
        blockers.append(
            _blocker(
                "amlsim_seed_manifest_not_frozen",
                "No generated dataset manifest records the random seed, license posture, and output hashes.",
                "Create `generated_dataset_manifest.json` with generator commit, seed, data license, config hash, and output hashes.",
            )
        )

    manifest_payload: dict[str, Any] = {}
    validation_errors: list[str] = []
    if by_name["generated_dataset_manifest.json"]["exists"]:
        try:
            manifest_payload = _read_json(data_dir / "generated_dataset_manifest.json")
            validation_errors = _validate_amlsim_reproducibility_manifest(
                data_dir=data_dir,
                manifest=manifest_payload,
                required_files_present=not missing_required,
                generator_commit_present=by_name["generator_commit.txt"]["exists"],
            )
        except (json.JSONDecodeError, OSError, TypeError) as exc:
            validation_errors = [f"generated_dataset_manifest.json could not be parsed: {exc}"]
    if validation_errors:
        blockers.append(
            _blocker(
                "amlsim_reproducibility_manifest_invalid",
                "The generated AMLSim bundle does not pass seed, commit, config, output-hash, and license verification.",
                "Correct the generation manifest or regenerate the bundle, then rerun the P8 decision command.",
            )
        )

    support_level = "proxy" if not blockers else "blocked"
    status = "proxy_ready" if support_level == "proxy" else "blocked"
    return {
        "schema_version": PAPER_HARD_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P8",
        "dataset_id": "amlsim_synthetic_bank_graph",
        "claim_id": dataset_spec.get("claim_id"),
        "registry_paper_claim_posture": dataset_spec.get("paper_claim_posture"),
        "status": status,
        "support_level": support_level,
        "paper_role": "synthetic_typology_workflow_proxy_only" if support_level == "proxy" else "excluded_pending_reproducible_generation",
        "source_posture": dataset_spec.get("source_posture"),
        "source_path": _display_path(root, data_dir),
        "local_generated_bundle_present": not missing_required,
        "required_file_checks": required_checks,
        "optional_file_checks": optional_checks,
        "split_contract_id": split_contract.get("split_contract_id"),
        "required_audits": split_contract.get("required_audits", []),
        "generator_commit": manifest_payload.get("generator_commit"),
        "random_seed": manifest_payload.get("random_seed"),
        "random_seeds": manifest_payload.get("random_seeds"),
        "generated_data_license": manifest_payload.get("generated_data_license"),
        "blocked_reason_codes": [row["code"] for row in blockers],
        "blockers": blockers,
        "reproducibility_validation_errors": validation_errors,
        "public_performance_claim_allowed": False,
        "hard_aml_claim_allowed": False,
        "next_action": (
            "Use this as a synthetic operational/typology proxy only; P9 may consume its aggregates."
            if support_level == "proxy"
            else "Generate a seeded AMLSim bundle and freeze commit, configuration, output hashes, typologies, and generated-data license."
        ),
    }


def _build_amlsim_typology_manifest(
    *,
    root: Path,
    data_dir: Path,
    generation_manifest: dict[str, Any],
    split_contract: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    alert_row_count = 0
    sar_account_row_count = 0
    typology_field: str | None = None
    if generation_manifest["support_level"] != "proxy":
        blockers.append(
            _blocker(
                "amlsim_generation_not_proxy_ready",
                "Typology evidence requires a reproducibly generated AMLSim proxy bundle.",
                "Resolve generation-manifest blockers before attempting a typology audit.",
            )
        )
    else:
        try:
            counts, alert_row_count, typology_field = _read_typology_counts(data_dir / "alert_transactions.csv")
            sar_account_row_count = _csv_data_row_count(data_dir / "sar_accounts.csv")
        except (OSError, UnicodeError, csv.Error):
            blockers.append(
                _blocker(
                    "amlsim_typology_files_not_readable",
                    "AMLSim typology CSV outputs could not be read for a stable audit.",
                    "Regenerate readable CSV outputs and rerun the P8 decision command.",
                )
            )
        if not blockers and not counts:
            blockers.append(
                _blocker(
                    "amlsim_typology_distribution_not_observable",
                    "No recognized non-empty typology field was found in `alert_transactions.csv`.",
                    "Regenerate or map AMLSim alert outputs so the typology distribution can be audited.",
                )
            )
    support_level = "proxy" if not blockers else "blocked"
    return {
        "schema_version": PAPER_HARD_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P8",
        "dataset_id": "amlsim_synthetic_bank_graph",
        "status": "proxy_ready" if support_level == "proxy" else "blocked",
        "support_level": support_level,
        "source_path": _display_path(root, data_dir),
        "split_contract_id": split_contract.get("split_contract_id"),
        "typology_field": typology_field,
        "typology_distribution": counts,
        "alert_transaction_row_count": alert_row_count,
        "sar_account_row_count": sar_account_row_count,
        "blocked_reason_codes": [row["code"] for row in blockers],
        "blockers": blockers,
        "claim_scope": "synthetic_typology_workflow_proxy_only",
        "public_performance_claim_allowed": False,
        "hard_aml_claim_allowed": False,
    }


def _build_elliptic2_access_report(
    *,
    root: Path,
    data_dir: Path,
    dataset_spec: dict[str, Any],
    split_contract: dict[str, Any],
) -> dict[str, Any]:
    required_checks = _check_files(root, data_dir, ELLIPTIC2_REQUIRED_FILES, include_hash=False)
    optional_checks = _check_files(root, data_dir, ELLIPTIC2_OPTIONAL_FILES, include_hash=False)
    missing_required = [row["filename"] for row in required_checks if not row["exists"]]
    blockers: list[dict[str, str]] = []
    if missing_required:
        blockers.extend(
            [
                _blocker(
                    "elliptic2_local_source_missing",
                    "The official Elliptic2 local source bundle is not present.",
                    "Acquire the dataset outside git and place the five official CSV files in the expected local directory.",
                ),
                _blocker(
                    "elliptic2_authenticated_manual_download_required",
                    "Elliptic2 acquisition requires an authenticated manual download and license-aware handling.",
                    "Download only after accepting the dataset terms and keep raw files outside version control.",
                ),
            ]
        )
    blockers.extend(
        [
            _blocker(
                "elliptic2_official_loader_not_validated",
                "P8 has not validated an official-schema Elliptic2 subgraph loader.",
                "Implement and fixture-test an official-schema loader before executing performance experiments.",
            ),
            _blocker(
                "elliptic2_split_and_overlap_audit_not_run",
                "The subgraph split and overlap audit required by the claim contract have not run.",
                "Freeze an official or deterministic subgraph split and prove overlap controls before model comparison.",
            ),
            _blocker(
                "elliptic2_resource_budget_not_frozen",
                "The large Elliptic2 workload has no accepted local execution budget.",
                "Measure ingestion and training memory/runtime on a pilot, then freeze the feasible model budget.",
            ),
            _blocker(
                "elliptic2_noncommercial_no_derivatives_claim_boundary",
                "The dataset license requires noncommercial, no-derivatives handling and prevents bundling raw data.",
                "Retain license and redistribution boundaries in every release and paper artifact.",
            ),
        ]
    )
    source_present = not missing_required
    return {
        "schema_version": PAPER_HARD_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P8",
        "dataset_id": "elliptic2_subgraph_aml",
        "claim_id": dataset_spec.get("claim_id"),
        "registry_paper_claim_posture": dataset_spec.get("paper_claim_posture"),
        "status": "blocked",
        "support_level": "blocked",
        "access_state": "source_present_requires_loader_split_resource_proof" if source_present else "source_not_present",
        "source_path": _display_path(root, data_dir),
        "local_source_ready": source_present,
        "required_file_checks": required_checks,
        "optional_file_checks": optional_checks,
        "source_hashing_posture": "deferred_until_official_loader_and_resource_pilot_due_to_large_source_bundle",
        "known_source_facts": dataset_spec.get("known_source_facts", {}),
        "license": dataset_spec.get("license", {}),
        "split_contract_id": split_contract.get("split_contract_id"),
        "required_audits": split_contract.get("required_audits", []),
        "forbidden_split_methods": split_contract.get("forbidden_split_methods", []),
        "blocked_reason_codes": [row["code"] for row in blockers],
        "blockers": blockers,
        "public_performance_claim_allowed": False,
        "hard_aml_claim_allowed": False,
        "next_action": "Treat Elliptic2 as the highest-upside hard graph recovery track: acquire it only with an official-loader, overlap-audit, and resource-budget implementation slice.",
    }


def _build_blocker_report(
    *,
    root: Path,
    amlsim_generation: dict[str, Any],
    amlsim_typology: dict[str, Any],
    elliptic2_access: dict[str, Any],
) -> dict[str, Any]:
    graph_manifest = _read_json_if_exists(root / "docs" / "reports" / "paper_graph_baseline_manifest.json")
    graph_gate = _read_json_if_exists(root / "docs" / "reports" / "paper_graph_publishability_gate.json")
    graph_shadow = _read_json_if_exists(root / "docs" / "reports" / "paper_graph_model_shadow_scorecard.json")
    amlsim_support = "proxy" if (
        amlsim_generation["support_level"] == "proxy" and amlsim_typology["support_level"] == "proxy"
    ) else "blocked"
    track_decisions = [
        {
            "dataset_id": "elliptic2_subgraph_aml",
            "support_level": elliptic2_access["support_level"],
            "first_paper_inclusion_decision": "exclude_pending_loader_split_resource_proof",
            "artifact_refs": ["docs/reports/elliptic2_subgraph_access_report.json"],
            "blocked_reason_codes": elliptic2_access["blocked_reason_codes"],
        },
        {
            "dataset_id": "amlsim_synthetic_bank_graph",
            "support_level": amlsim_support,
            "first_paper_inclusion_decision": (
                "supplementary_proxy_candidate" if amlsim_support == "proxy" else "exclude_pending_reproducible_generation"
            ),
            "artifact_refs": [
                "docs/reports/amlsim_generation_manifest.json",
                "docs/reports/amlsim_typology_manifest.json",
            ],
            "blocked_reason_codes": sorted(
                set(amlsim_generation["blocked_reason_codes"] + amlsim_typology["blocked_reason_codes"])
            ),
        },
    ]
    counts = {
        label: sum(1 for row in track_decisions if row["support_level"] == label)
        for label in ["supported", "proxy", "blocked"]
    }
    shadow_rows = graph_shadow.get("rows", [])
    graph_shadow_test_pr_auc = None
    if shadow_rows:
        graph_shadow_test_pr_auc = dict(shadow_rows[0].get("test_metrics", {})).get("pr_auc")
    decision_state = (
        "synthetic_proxy_available_real_subgraph_track_blocked"
        if counts["proxy"]
        else "hard_tracks_blocked_recorded"
    )
    return {
        "schema_version": PAPER_HARD_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P8",
        "status": "ok",
        "decision_state": decision_state,
        "track_decisions": track_decisions,
        "supported_track_count": counts["supported"],
        "proxy_track_count": counts["proxy"],
        "blocked_track_count": counts["blocked"],
        "hard_performance_claims_allowed": False,
        "headline_or_sota_claim_allowed": False,
        "paper_can_continue_to_p9": True,
        "p7_context": {
            "supporting_graph_table_candidate_allowed": graph_gate.get("supporting_graph_table_candidate_allowed", False),
            "selected_graph_test_pr_auc": graph_manifest.get("selected_test_pr_auc"),
            "graph_neural_claim_allowed": graph_gate.get("graph_neural_model_claim_allowed", False),
            "graph_shadow_test_pr_auc": graph_shadow_test_pr_auc,
            "interpretation": "P7 supplies supporting flattened-graph evidence only; it does not substitute for modern subgraph AML evidence.",
        },
        "paper_strategy_recommendation": [
            "Continue to P9 operational evaluation without presenting either hard track as implemented evidence.",
            "Before final result tables, choose a bounded Elliptic2 acquisition and pilot slice if resources permit; it offers the strongest scientific breadth upside.",
            "Use AMLSim only as seeded synthetic typology and operations evidence after its proxy audit passes; it cannot replace a real subgraph benchmark.",
        ],
        "paper_limitation_text": "Elliptic2 and AMLSim were evaluated as candidate hard tracks but excluded from first-paper performance claims pending, respectively, validated subgraph execution proof and reproducible synthetic-generation proof.",
        "next_slice": "Paper Track P9",
        "command": "relaytic release-safety hard-graph-tracks --format json",
    }


def _validate_amlsim_reproducibility_manifest(
    *,
    data_dir: Path,
    manifest: dict[str, Any],
    required_files_present: bool,
    generator_commit_present: bool,
) -> list[str]:
    errors: list[str] = []
    declared_commit = str(manifest.get("generator_commit") or "").strip()
    if not declared_commit:
        errors.append("generator_commit is missing")
    elif generator_commit_present:
        recorded_lines = (data_dir / "generator_commit.txt").read_text(encoding="utf-8").strip().splitlines()
        if not recorded_lines:
            errors.append("generator_commit.txt is empty")
        elif recorded_lines[0] != declared_commit:
            errors.append("generator_commit does not match generator_commit.txt")
    seed = manifest.get("random_seed")
    seeds = manifest.get("random_seeds")
    if seed is None and not (isinstance(seeds, list) and seeds):
        errors.append("random_seed or non-empty random_seeds is missing")
    if not str(manifest.get("generated_data_license") or "").strip():
        errors.append("generated_data_license is missing")
    if required_files_present:
        config_hash = str(manifest.get("config_sha256") or "").strip()
        if config_hash != _sha256(data_dir / "conf.json"):
            errors.append("config_sha256 does not match conf.json")
        declared_hashes = manifest.get("output_sha256")
        if not isinstance(declared_hashes, dict):
            errors.append("output_sha256 is missing")
        else:
            for filename in ["tx_log.csv", "alert_transactions.csv", "sar_accounts.csv"]:
                if declared_hashes.get(filename) != _sha256(data_dir / filename):
                    errors.append(f"output_sha256 does not match {filename}")
    return errors


def _read_typology_counts(path: Path) -> tuple[dict[str, int], int, str | None]:
    candidate_names = ["alerttype", "typology", "type", "modeltype", "reason"]
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        field_map = {_normalize_column(name): name for name in (reader.fieldnames or [])}
        selected = next((field_map[name] for name in candidate_names if name in field_map), None)
        counts: dict[str, int] = {}
        row_count = 0
        for row in reader:
            row_count += 1
            if selected:
                label = str(row.get(selected) or "").strip()
                if label:
                    counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items())), row_count, selected


def _csv_data_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _check_files(
    root: Path,
    data_dir: Path,
    filenames: list[str],
    *,
    include_hash: bool = True,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for filename in filenames:
        path = data_dir / filename
        exists = path.is_file()
        checks.append(
            {
                "filename": filename,
                "path": _display_path(root, path),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else None,
                "sha256": _sha256(path) if exists and include_hash else None,
            }
        )
    return checks


def _blocker(code: str, reason: str, next_action: str) -> dict[str, str]:
    return {"code": code, "reason": reason, "next_action": next_action}


def _resolve_dir(root: Path, provided: str | Path | None, default: Path) -> Path:
    resolved = Path(provided) if provided is not None else root / default
    return resolved if resolved.is_absolute() else root / resolved


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    return _read_json(path) if path.is_file() else {}


def _find_item(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    return next((dict(item) for item in items if item.get(key) == value), {})


def _normalize_column(value: str) -> str:
    return "".join(char for char in value.lower() if char.isalnum())

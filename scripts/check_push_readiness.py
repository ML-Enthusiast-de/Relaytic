"""Run the highest-risk Relaytic regression shards before pushing."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import sys
from pathlib import Path


_QUICK_SHARDS = (
    [
        "tests/test_cli_slice09b.py::test_cli_runtime_surfaces_materialize_for_public_binary_run",
        "tests/test_cli_slice09d.py::test_cli_research_slice_materializes_and_influences_autonomy_on_public_dataset",
        "tests/test_cli_slice09e.py::test_cli_assist_show_turn_and_takeover_work_on_public_dataset",
        "tests/test_cli_slice10.py::test_cli_feedback_add_show_and_rollback_work_on_public_run",
    ],
    [
        "tests/test_cli_slice11.py::test_cli_run_and_benchmark_show_materialize_reference_parity_for_public_binary_run",
        "tests/test_cli_slice11a.py::test_cli_autonomy_consumes_unmet_beat_target_contract",
        "tests/test_cli_slice12.py::test_cli_dojo_review_rejects_when_imported_incumbent_is_stronger",
        "tests/test_cli_slice12b.py::test_cli_trace_and_evals_surfaces_materialize_for_public_dataset",
    ],
    [
        "tests/test_cli_slice13.py::test_cli_search_slice_materializes_and_surfaces_search_controller_artifacts",
        "tests/test_cli_slice13c.py::test_cli_daemon_slice_materializes_and_resumes_background_search",
        "tests/test_domain_datasets.py::test_write_uci_bank_marketing_dataset_honors_requested_max_rows",
        "tests/test_external_agent_readiness.py::test_external_agent_wrappers_support_a_real_run_and_proof_flow",
    ],
)

_FULL_ONLY_SHARDS = (
    ["tests/test_interoperability_mcp.py::test_streamable_http_mcp_can_run_relaytic_end_to_end_on_public_dataset"],
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _preferred_python(root: Path) -> Path:
    candidates = [
        root / ".venv" / "Scripts" / "python.exe",
        root / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(sys.executable)


def _run_shard(python: Path, root: Path, shard: list[str]) -> int:
    command = [str(python), "-m", "pytest", *shard, "-q"]
    print(f"[push-readiness] running: {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=root)
    return int(completed.returncode)


def _run_parallel_quick_shards(python: Path, root: Path, shards: list[list[str]]) -> int:
    with ThreadPoolExecutor(max_workers=min(3, max(1, len(shards)))) as pool:
        future_map = {
            pool.submit(_run_shard, python, root, list(shard)): list(shard)
            for shard in shards
        }
        for future in as_completed(future_map):
            returncode = int(future.result())
            if returncode != 0:
                print("[push-readiness] failed shard above. Stop and fix before push.", flush=True)
                return returncode
    print("[push-readiness] all selected shards passed.", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Relaytic pre-push regression shards.")
    parser.add_argument(
        "--mode",
        choices=("quick", "full"),
        default="quick",
        help="`quick` runs the highest-risk local shards; `full` adds the MCP end-to-end shard.",
    )
    args = parser.parse_args()

    root = _repo_root()
    python = _preferred_python(root)
    shards = list(_QUICK_SHARDS)
    if args.mode == "full":
        shards.extend(_FULL_ONLY_SHARDS)
    else:
        return _run_parallel_quick_shards(python, root, [list(shard) for shard in shards])

    for shard in shards:
        returncode = _run_shard(python, root, list(shard))
        if returncode != 0:
            print("[push-readiness] failed shard above. Stop and fix before push.", flush=True)
            return returncode

    print("[push-readiness] all selected shards passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

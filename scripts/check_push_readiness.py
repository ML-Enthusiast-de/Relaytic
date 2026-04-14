"""Run tiered Relaytic regression walls before pushing."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


_QUICK_GROUPS = (
    [
        "-m",
        "smoke",
        "tests/test_push_smoke.py",
    ],
    [
        "tests/test_architecture_routing.py",
        "tests/test_assist_agents.py",
    ],
)

_PREPUSH_ONLY_GROUPS = (
    [
        "-m",
        "prepush",
        "tests/test_push_prepush.py",
        "tests/test_hpo_loop.py",
        "tests/test_splitters.py",
        "tests/test_search_agents.py",
        "tests/test_model_training_candidates.py",
        "tests/test_planning_agents.py",
        "tests/test_cli_slice15h.py",
        "tests/test_cli_slice15i.py",
        "tests/test_cli_slice15j.py",
        "tests/test_operating_points.py",
        "tests/test_cli_slice15k.py",
        "tests/test_cli_slice15d.py::test_cli_slice15d_benchmark_run_materializes_paper_artifacts_for_public_binary_run",
    ],
)

_FULL_ONLY_GROUPS = (
    [
        "tests/test_domain_datasets.py::test_write_uci_bank_marketing_dataset_honors_requested_max_rows",
        "tests/test_external_agent_readiness.py::test_external_agent_wrappers_support_a_real_run_and_proof_flow",
        "tests/test_interoperability_mcp.py::test_streamable_http_mcp_can_run_relaytic_end_to_end_on_public_dataset",
    ],
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


def _run_group(python: Path, root: Path, args: list[str]) -> int:
    command = [str(python), "-m", "pytest", "-q", "--maxfail=1", *args]
    print(f"[push-readiness] running: {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=root)
    return int(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Relaytic pre-push regression walls.")
    parser.add_argument(
        "--mode",
        choices=("quick", "prepush", "full"),
        default="quick",
        help=(
            "`quick` runs the fast local smoke wall, `prepush` adds the broader local regression wall, "
            "and `full` adds the heavyweight network/MCP/agent checks."
        ),
    )
    args = parser.parse_args()

    root = _repo_root()
    python = _preferred_python(root)
    groups = list(_QUICK_GROUPS)
    if args.mode in {"prepush", "full"}:
        groups.extend(_PREPUSH_ONLY_GROUPS)
    if args.mode == "full":
        groups.extend(_FULL_ONLY_GROUPS)

    for group in groups:
        returncode = _run_group(python, root, list(group))
        if returncode != 0:
            print("[push-readiness] failed group above. Stop and fix before push.", flush=True)
            return returncode

    print("[push-readiness] all selected groups passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

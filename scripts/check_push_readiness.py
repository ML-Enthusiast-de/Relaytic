"""Run the highest-risk Relaytic regression shards before pushing."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


_QUICK_SHARDS = (
    [
        "tests/test_cli_slice09b.py",
        "tests/test_cli_slice09d.py",
        "tests/test_cli_slice09e.py",
        "tests/test_cli_slice10.py",
    ],
    [
        "tests/test_cli_slice11.py",
        "tests/test_cli_slice11a.py",
        "tests/test_cli_slice12.py",
        "tests/test_cli_slice12b.py",
    ],
    [
        "tests/test_cli_slice13.py",
        "tests/test_cli_slice13c.py",
        "tests/test_domain_datasets.py",
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

    for shard in shards:
        returncode = _run_shard(python, root, list(shard))
        if returncode != 0:
            print("[push-readiness] failed shard above. Stop and fix before push.", flush=True)
            return returncode

    print("[push-readiness] all selected shards passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

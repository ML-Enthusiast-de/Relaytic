"""One-line Relaytic bootstrap installer with post-install verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install Relaytic and run doctor checks.")
    parser.add_argument("--extras", default="full", help="Editable-install extra set to request.")
    parser.add_argument("--skip-install", action="store_true", help="Skip the pip install step and only run doctor.")
    parser.add_argument("--format", choices=["human", "json", "both"], default="human", help="Doctor output format.")
    parser.add_argument("--expected-profile", choices=["core", "full"], default="full", help="Doctor profile to verify after install.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    if not args.skip_install:
        install_cmd = [sys.executable, "-m", "pip", "install", "-e", f".[{args.extras}]"]
        install = subprocess.run(install_cmd, cwd=repo_root, check=False)
        if install.returncode != 0:
            return int(install.returncode)
    doctor_cmd = [
        sys.executable,
        "-m",
        "relaytic.ui.cli",
        "doctor",
        "--expected-profile",
        args.expected_profile,
        "--format",
        args.format,
    ]
    doctor = subprocess.run(doctor_cmd, cwd=repo_root, capture_output=False, check=False)
    return int(doctor.returncode)


if __name__ == "__main__":
    raise SystemExit(main())

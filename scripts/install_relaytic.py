"""One-line Relaytic bootstrap installer with post-install verification and launch."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install Relaytic, verify the environment, and optionally launch mission control.")
    parser.add_argument("--profile", choices=["core", "full", "dev"], default="full", help="Named install profile. `core` installs the base package, `full` installs the recommended local stack, and `dev` installs the contributor profile.")
    parser.add_argument("--extras", default=None, help="Optional editable-install extra set to request. Overrides --profile when provided.")
    parser.add_argument("--skip-install", action="store_true", help="Skip the pip install step and only run verification and optional launch.")
    parser.add_argument("--format", choices=["human", "json", "both"], default="human", help="Output format for verification and launch surfaces.")
    parser.add_argument("--expected-profile", choices=["core", "full"], default=None, help="Doctor profile to verify after install. Defaults to `core` for --profile core, otherwise `full`.")
    parser.add_argument("--launch-control-center", action="store_true", help="Launch the local Relaytic mission-control surface after doctor succeeds.")
    parser.add_argument("--run-dir", default=None, help="Optional Relaytic run directory to open inside mission control.")
    parser.add_argument("--output-dir", default=None, help="Optional onboarding-only state directory for mission control when no run dir is provided.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the mission-control report in the default browser.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    relaytic_env = _relaytic_env(repo_root)
    extras = args.extras if args.extras is not None else _extras_for_profile(args.profile)
    expected_profile = args.expected_profile or ("core" if args.profile == "core" and args.extras is None else "full")

    if not args.skip_install:
        install_cmd = [sys.executable, "-m", "pip", "install", "-e", _editable_target(extras)]
        install = subprocess.run(install_cmd, cwd=repo_root, check=False)
        if install.returncode != 0:
            return int(install.returncode)

    doctor_cmd = [
        sys.executable,
        "-m",
        "relaytic.ui.cli",
        "doctor",
        "--expected-profile",
        expected_profile,
        "--format",
        args.format,
    ]
    doctor = subprocess.run(
        doctor_cmd,
        cwd=repo_root,
        env=relaytic_env,
        capture_output=True,
        text=True,
        check=False,
    )
    if args.format == "json":
        if not args.launch_control_center:
            sys.stdout.write(doctor.stdout)
            sys.stderr.write(doctor.stderr)
            return int(doctor.returncode)
    else:
        sys.stdout.write(doctor.stdout)
        sys.stderr.write(doctor.stderr)
    if doctor.returncode != 0:
        return int(doctor.returncode)

    if not args.launch_control_center:
        return int(doctor.returncode)

    launch_cmd = [
        sys.executable,
        "-m",
        "relaytic.ui.cli",
        "mission-control",
        "launch",
        "--expected-profile",
        expected_profile,
        "--format",
        args.format,
    ]
    if args.run_dir:
        launch_cmd.extend(["--run-dir", str(args.run_dir)])
    if args.output_dir:
        launch_cmd.extend(["--output-dir", str(args.output_dir)])
    if args.no_browser:
        launch_cmd.append("--no-browser")

    launch = subprocess.run(
        launch_cmd,
        cwd=repo_root,
        env=relaytic_env,
        capture_output=True,
        text=True,
        check=False,
    )
    if args.format == "json":
        payload: dict[str, Any] = {
            "status": "ok" if launch.returncode == 0 else "error",
            "install": {
                "skip_install": bool(args.skip_install),
                "profile": args.profile,
                "extras": extras or "",
                "expected_profile": expected_profile,
                "mission_control_requested": True,
            },
            "doctor": _parse_json_payload(doctor.stdout),
            "mission_control": _parse_json_payload(launch.stdout),
        }
        sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False))
        sys.stdout.write("\n")
        if doctor.stderr:
            sys.stderr.write(doctor.stderr)
        if launch.stderr:
            sys.stderr.write(launch.stderr)
    else:
        sys.stdout.write(launch.stdout)
        sys.stderr.write(launch.stderr)
    return int(launch.returncode)


def _extras_for_profile(profile: str) -> str:
    normalized = str(profile).strip().lower() or "full"
    if normalized == "core":
        return ""
    if normalized == "dev":
        return "dev"
    return "full"


def _editable_target(extras: str) -> str:
    normalized = str(extras).strip()
    return "." if not normalized else f".[{normalized}]"


def _relaytic_env(repo_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    src_dir = str(repo_root / "src")
    current = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_dir if not current else src_dir + os.pathsep + current
    return env


def _parse_json_payload(raw: str) -> dict[str, Any]:
    text = str(raw).strip()
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"status": "parse_error", "raw_output": text}
    return payload if isinstance(payload, dict) else {"status": "unexpected_output", "raw_output": text}


if __name__ == "__main__":
    raise SystemExit(main())

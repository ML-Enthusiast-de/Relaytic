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
    parser.add_argument("--no-setup-onboarding-llm", action="store_true", help="Skip provisioning the lightweight local onboarding LLM during the full install flow.")
    parser.add_argument("--onboarding-llm-provider", choices=["llama_cpp", "llama.cpp", "ollama"], default="llama_cpp", help="Preferred local provider for the lightweight onboarding LLM.")
    parser.add_argument("--onboarding-llm-model", default=None, help="Optional local onboarding model override. Defaults to Relaytic's CPU-safe Qwen 3 4B profile.")
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
    if args.format != "json":
        sys.stdout.write(doctor.stdout)
        sys.stderr.write(doctor.stderr)
    if doctor.returncode != 0:
        return int(doctor.returncode)

    llm_payload: dict[str, Any] | None = None
    should_setup_onboarding_llm = (
        not bool(args.no_setup_onboarding_llm)
        and (args.profile in {"full", "dev"} or (args.extras or "").strip().lower() == "full")
    )
    if should_setup_onboarding_llm:
        llm_cmd = [
            sys.executable,
            "-m",
            "relaytic.ui.cli",
            "setup-local-llm",
            "--provider",
            args.onboarding_llm_provider,
        ]
        if not args.skip_install:
            llm_cmd.append("--install-provider")
        if args.onboarding_llm_model:
            llm_cmd.extend(["--model", args.onboarding_llm_model])
        llm_setup = subprocess.run(
            llm_cmd,
            cwd=repo_root,
            env=relaytic_env,
            capture_output=True,
            text=True,
            check=False,
        )
        llm_payload = _parse_json_payload(llm_setup.stdout)
        if args.format != "json":
            sys.stdout.write(llm_setup.stdout)
            sys.stderr.write(llm_setup.stderr)

    if not args.launch_control_center:
        if args.format == "json":
            payload: dict[str, Any] = {
                "status": "ok" if doctor.returncode == 0 else "error",
                "install": {
                    "skip_install": bool(args.skip_install),
                    "profile": args.profile,
                    "extras": extras or "",
                    "expected_profile": expected_profile,
                    "mission_control_requested": False,
                    "onboarding_llm_requested": should_setup_onboarding_llm,
                },
                "doctor": _parse_json_payload(doctor.stdout),
            }
            if llm_payload is not None:
                payload["onboarding_local_llm"] = llm_payload
            sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False))
            sys.stdout.write("\n")
            sys.stderr.write(doctor.stderr)
            return int(doctor.returncode)
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
                "onboarding_llm_requested": should_setup_onboarding_llm,
            },
            "doctor": _parse_json_payload(doctor.stdout),
            "mission_control": _parse_json_payload(launch.stdout),
        }
        if llm_payload is not None:
            payload["onboarding_local_llm"] = llm_payload
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

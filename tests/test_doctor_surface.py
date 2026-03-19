import json
import subprocess
import sys
from pathlib import Path

from relaytic.ui.cli import main


def test_cli_doctor_core_profile_is_machine_readable(capsys) -> None:
    assert main(["doctor", "--expected-profile", "core", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "relaytic.doctor_report.v1"
    assert payload["python"]["compatible"] is True
    assert payload["core_dependencies"]


def test_install_script_skip_install_runs_doctor(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "install_relaytic.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--skip-install",
            "--expected-profile",
            "core",
            "--format",
            "json",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] in {"ok", "warn"}

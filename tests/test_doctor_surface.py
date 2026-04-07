import importlib.util
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


def test_install_script_prefers_repo_local_venv_when_available(tmp_path: Path) -> None:
    repo_root = tmp_path
    repo_python = repo_root / ".venv" / "Scripts" / "python.exe"
    repo_python.parent.mkdir(parents=True, exist_ok=True)
    repo_python.write_text("", encoding="utf-8")
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "install_relaytic.py"
    spec = importlib.util.spec_from_file_location("relaytic_install_script", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    preferred = module._preferred_repo_python(
        repo_root=repo_root,
        current_executable=tmp_path / "system_python.exe",
    )

    assert preferred == repo_python
    assert (
        module._preferred_repo_python(
            repo_root=repo_root,
            current_executable=repo_python,
        )
        is None
    )


def test_bootstrap_wrappers_exist_and_target_install_script() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    powershell_wrapper = repo_root / "scripts" / "bootstrap.ps1"
    shell_wrapper = repo_root / "scripts" / "bootstrap.sh"

    assert powershell_wrapper.exists()
    assert shell_wrapper.exists()
    assert "install_relaytic.py" in powershell_wrapper.read_text(encoding="utf-8")
    assert "install_relaytic.py" in shell_wrapper.read_text(encoding="utf-8")


def test_install_script_emits_json_next_steps_when_doctor_fails(monkeypatch, capsys) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "install_relaytic.py"
    spec = importlib.util.spec_from_file_location("relaytic_install_script_failure", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def fake_run(cmd, **kwargs):
        if "doctor" in cmd:
            return subprocess.CompletedProcess(cmd, 1, stdout=json.dumps({"status": "error"}), stderr="doctor failed")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.main(["--skip-install", "--expected-profile", "core", "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert payload["doctor"]["status"] == "error"
    assert payload["next_steps"]

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.interoperability import relaytic_show_mission_control
from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset
from tests.test_cli_slice11a import _write_memorized_incumbent_model


def test_cli_mission_control_show_and_launch_reuse_current_run_truth(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "mission_control_run"
    data_path = write_public_breast_cancer_dataset(tmp_path / "mission_control_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the provided features and benchmark against strong references.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    model_path = _write_memorized_incumbent_model(
        path=tmp_path / "strong_incumbent.pkl",
        data_path=data_path,
        plan=plan,
    )

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--incumbent-path",
            str(model_path),
            "--incumbent-kind",
            "model",
            "--incumbent-name",
            "strong_incumbent",
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "Go back to planning and try a simpler route.",
            "--format",
            "json",
        ]
    ) == 0
    assist_payload = json.loads(capsys.readouterr().out)
    assert assist_payload["status"] == "ok"

    assert main(
        [
            "mission-control",
            "show",
            "--run-dir",
            str(run_dir),
            "--expected-profile",
            "full",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    mission_control = dict(payload["mission_control"])
    bundle = dict(payload["bundle"])

    assert payload["status"] == "ok"
    assert mission_control["current_stage"] is not None
    assert mission_control["html_report_path"] is not None
    assert mission_control["review_queue_pending_count"] >= 1
    assert dict(bundle["mission_control_state"])["card_count"] >= 6
    assert dict(bundle["review_queue_state"])["pending_count"] >= 1
    assert dict(bundle["onboarding_status"])["launch_ready"] is True
    assert dict(bundle["launch_manifest"])["browser_requested"] is False
    assert dict(bundle["demo_session_manifest"])["incumbent_visible"] is True

    for filename in (
        "mission_control_state.json",
        "review_queue_state.json",
        "control_center_layout.json",
        "onboarding_status.json",
        "install_experience_report.json",
        "launch_manifest.json",
        "demo_session_manifest.json",
        "ui_preferences.json",
        "manifest.json",
    ):
        assert (run_dir / filename).exists(), filename
    assert (run_dir / "reports" / "mission_control.html").exists()

    assert main(
        [
            "mission-control",
            "launch",
            "--run-dir",
            str(run_dir),
            "--expected-profile",
            "full",
            "--no-browser",
            "--format",
            "json",
        ]
    ) == 0
    launch_payload = json.loads(capsys.readouterr().out)
    assert launch_payload["mission_control"]["browser_requested"] is False
    assert launch_payload["mission_control"]["browser_opened"] is False

    interop_payload = relaytic_show_mission_control(run_dir=str(run_dir))
    assert (
        interop_payload["surface_payload"]["mission_control"]["current_stage"]
        == mission_control["current_stage"]
    )
    assert (
        interop_payload["surface_payload"]["bundle"]["review_queue_state"]["pending_count"]
        == bundle["review_queue_state"]["pending_count"]
    )


def test_install_script_can_launch_onboarding_mission_control(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "install_relaytic.py"
    output_dir = tmp_path / "mission_control_onboarding"
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--skip-install",
            "--profile",
            "core",
            "--expected-profile",
            "core",
            "--launch-control-center",
            "--output-dir",
            str(output_dir),
            "--no-browser",
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
    assert payload["doctor"]["status"] in {"ok", "warn"}
    mission_control = dict(payload["mission_control"]["mission_control"])
    assert mission_control["launch_ready"] is True
    assert (output_dir / "reports" / "mission_control.html").exists()
    assert (output_dir / "launch_manifest.json").exists()

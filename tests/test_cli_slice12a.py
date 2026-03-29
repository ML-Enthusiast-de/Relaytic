from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.core.json_utils import write_json
from relaytic.interoperability import relaytic_review_pulse, relaytic_show_pulse
from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def _write_pulse_memory_inputs(run_dir: Path) -> None:
    write_json(
        run_dir / "reflection_memory.json",
        {
            "summary": "Retain the stable route lesson for later analog retrieval.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "causal_memory_index.json",
        {
            "similar_harmful_override_count": 1,
            "patterns": ["unsafe forced promotion"],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "method_memory_index.json",
        {
            "entries": [{"method": "benchmark_refresh", "outcome": "helpful"}],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def test_cli_pulse_review_show_and_interop_surfaces_work_on_public_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "pulse_cli"
    data_path = write_public_breast_cancer_dataset(tmp_path / "pulse_cli_breast_cancer.csv")
    config_path = tmp_path / "pulse_config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "pulse:",
                "  enabled: true",
                "  mode: bounded_execute",
                "  throttle_minutes: 0",
                "  allow_innovation_watch: true",
                "  allow_memory_maintenance: true",
                "  allow_queue_refresh: true",
            ]
        ),
        encoding="utf-8",
    )

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

    _write_pulse_memory_inputs(run_dir)

    assert main(
        [
            "pulse",
            "review",
            "--run-dir",
            str(run_dir),
            "--config",
            str(config_path),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["pulse"]["status"] == "ok"
    assert payload["pulse"]["mode"] == "bounded_execute"
    assert payload["pulse"]["compaction_executed"] is True
    assert payload["pulse"]["memory_pinned_count"] >= 1
    assert payload["run_summary"]["stage_completed"] == "pulse_reviewed"
    assert (run_dir / "pulse_run_report.json").exists()
    assert (run_dir / "memory_pinning_index.json").exists()

    assert main(["pulse", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["pulse"]["memory_pinned_count"] == payload["pulse"]["memory_pinned_count"]
    assert show_payload["pulse"]["compaction_executed"] is True

    assert main(["mission-control", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    mission_control = json.loads(capsys.readouterr().out)
    cards = list(mission_control["bundle"]["mission_control_state"]["cards"])
    assert any(str(item.get("card_id")) == "pulse" for item in cards)

    interop_show = relaytic_show_pulse(run_dir=str(run_dir))
    assert interop_show["surface_payload"]["pulse"]["memory_pinned_count"] == payload["pulse"]["memory_pinned_count"]

    interop_review = relaytic_review_pulse(run_dir=str(run_dir), config_path=str(config_path), overwrite=True)
    assert interop_review["surface_payload"]["pulse"]["status"] == "ok"
    assert interop_review["surface_payload"]["pulse"]["mode"] == "bounded_execute"

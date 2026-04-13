from __future__ import annotations

import json

from relaytic.interoperability import relaytic_show_agent_evals, relaytic_show_trace
from relaytic.ui.cli import main


def test_push_prepush_assist_and_feedback_surfaces(push_smoke_run: dict[str, object], capsys) -> None:
    run_dir = push_smoke_run["run_dir"]

    assert main(
        ["assist", "turn", "--run-dir", str(run_dir), "--message", "what can you do?", "--format", "json"]
    ) == 0
    assist_payload = json.loads(capsys.readouterr().out)
    assert assist_payload["status"] == "ok"
    assert assist_payload["turn"]["intent_type"] == "capabilities"

    assert main(
        [
            "feedback",
            "add",
            "--run-dir",
            str(run_dir),
            "--source-type",
            "human",
            "--feedback-type",
            "route_quality",
            "--message",
            "Boosted tree quality should stay in consideration when recall matters.",
            "--suggested-route-family",
            "boosted_tree_classifier",
            "--evidence-level",
            "medium",
            "--source-artifact",
            "benchmark_gap_report.json",
            "--format",
            "json",
        ]
    ) == 0
    add_payload = json.loads(capsys.readouterr().out)
    assert add_payload["status"] == "ok"
    assert add_payload["feedback"]["accepted_count"] >= 1

    assert main(["feedback", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["status"] == "ok"
    assert show_payload["feedback"]["accepted_count"] >= 1


def test_push_prepush_search_trace_and_eval_surfaces(push_smoke_run: dict[str, object], capsys) -> None:
    run_dir = push_smoke_run["run_dir"]

    assert main(["search", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    search_payload = json.loads(capsys.readouterr().out)
    assert search_payload["status"] == "ok"
    assert search_payload["search"]["recommended_action"] is not None

    assert main(["trace", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    trace_payload = json.loads(capsys.readouterr().out)
    assert trace_payload["status"] == "ok"
    assert trace_payload["trace"]["winning_claim_id"] is not None

    assert main(["evals", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    eval_show_payload = json.loads(capsys.readouterr().out)
    assert eval_show_payload["status"] == "ok"
    assert eval_show_payload["evals"]["protocol_status"] == "ok"

    interop_trace = relaytic_show_trace(run_dir=str(run_dir))
    assert interop_trace["surface_payload"]["status"] == "ok"

    interop_evals = relaytic_show_agent_evals(run_dir=str(run_dir))
    assert interop_evals["surface_payload"]["status"] == "ok"

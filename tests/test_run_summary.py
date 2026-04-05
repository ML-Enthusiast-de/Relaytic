from __future__ import annotations

from pathlib import Path

from relaytic.core.json_utils import write_json
from relaytic.runs.summary import build_run_summary


def test_run_summary_prefers_newer_feedback_action_over_stale_decision_action(tmp_path: Path) -> None:
    run_dir = tmp_path / "summary_feedback_newer"
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "manifest.json", {"run_id": "run_feedback_newer"}, indent=2, ensure_ascii=False, sort_keys=True)
    write_json(
        run_dir / "decision_constraint_report.json",
        {
            "generated_at": "2026-04-04T10:00:00+00:00",
            "feasible_selected_action": "request_operator_review",
            "summary": "Older decision review still asked for operator review.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "feedback_effect_report.json",
        {
            "generated_at": "2026-04-04T10:05:00+00:00",
            "primary_recommended_action": "raise_review_threshold",
            "summary": "Newer accepted feedback recommends raising the review threshold.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    summary = build_run_summary(run_dir=run_dir)

    assert summary["next_step"]["recommended_action"] == "raise_review_threshold"
    assert summary["next_step"]["recommended_action_source"] == "feedback_effect_report"
    assert "raising the review threshold" in summary["next_step"]["rationale"].lower()


def test_run_summary_prefers_newer_decision_action_after_feedback_when_review_is_rerun(tmp_path: Path) -> None:
    run_dir = tmp_path / "summary_decision_newer"
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "manifest.json", {"run_id": "run_decision_newer"}, indent=2, ensure_ascii=False, sort_keys=True)
    write_json(
        run_dir / "feedback_effect_report.json",
        {
            "generated_at": "2026-04-04T10:00:00+00:00",
            "primary_recommended_action": "raise_review_threshold",
            "summary": "Older feedback wanted a stricter review threshold.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "decision_constraint_report.json",
        {
            "generated_at": "2026-04-04T10:07:00+00:00",
            "feasible_selected_action": "request_operator_review",
            "summary": "A newer decision review found the action still needs operator review.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    summary = build_run_summary(run_dir=run_dir)

    assert summary["next_step"]["recommended_action"] == "request_operator_review"
    assert summary["next_step"]["recommended_action_source"] == "decision_constraint_report"
    assert "needs operator review" in summary["next_step"]["rationale"].lower()

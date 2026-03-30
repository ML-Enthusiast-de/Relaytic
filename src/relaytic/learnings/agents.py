"""Slice 12C durable learnings sync and reset."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any

from .models import (
    LAB_LEARNINGS_SNAPSHOT_SCHEMA_VERSION,
    LEARNINGS_RESET_SCHEMA_VERSION,
    LEARNINGS_STATE_SCHEMA_VERSION,
    LabLearningsSnapshotArtifact,
    LearningControls,
    LearningTrace,
    LearningsResetArtifact,
    LearningsStateArtifact,
    build_learning_controls_from_policy,
)
from .storage import (
    LEARNINGS_MARKDOWN_FILENAME,
    LEARNINGS_STATE_FILENAME,
    default_learnings_state_dir,
    read_learnings_snapshot,
    read_learnings_state,
    write_learnings_markdown,
    write_learnings_snapshot,
    write_learnings_state,
)


@dataclass(frozen=True)
class LearningSyncResult:
    """Result of syncing durable learnings from a run."""

    state: LearningsStateArtifact
    snapshot: LabLearningsSnapshotArtifact
    markdown: str


def sync_learnings_from_run(
    *,
    run_dir: str | Path,
    summary_payload: dict[str, Any],
    handoff_bundle: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> LearningSyncResult:
    """Harvest durable learnings from one run and refresh the shared learnings state."""

    root = Path(run_dir)
    state_dir = default_learnings_state_dir(run_dir=root)
    controls = build_learning_controls_from_policy(policy)
    existing_state = read_learnings_state(state_dir)
    existing_entries = [
        dict(item)
        for item in existing_state.get("entries", [])
        if isinstance(item, dict)
    ]
    run_id = _clean_text(summary_payload.get("run_id")) or root.name or "run"
    harvested = _harvest_learnings(
        summary_payload=summary_payload,
        handoff_bundle=handoff_bundle or {},
        controls=controls,
    )
    retained = [item for item in existing_entries if _clean_text(item.get("source_run_id")) != run_id]
    merged = retained + harvested
    merged.sort(key=lambda item: str(item.get("last_updated_at") or ""), reverse=True)
    merged = merged[: controls.max_entries]
    trace = _trace()
    state_artifact = LearningsStateArtifact(
        schema_version=LEARNINGS_STATE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        state_dir=str(state_dir),
        entry_count=len(merged),
        entries=merged,
        summary=f"Relaytic keeps `{len(merged)}` durable learnings in the shared local memory for later runs.",
        trace=trace,
    )
    active = _select_active_learnings(entries=merged, summary_payload=summary_payload, controls=controls)
    snapshot = LabLearningsSnapshotArtifact(
        schema_version=LAB_LEARNINGS_SNAPSHOT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        run_id=run_id,
        state_dir=str(state_dir),
        learnings_state_path=str(state_dir / LEARNINGS_STATE_FILENAME),
        learnings_md_path=str(state_dir / LEARNINGS_MARKDOWN_FILENAME),
        state_entry_count=len(merged),
        harvested_count=len(harvested),
        active_count=len(active),
        harvested_learnings=harvested,
        active_learnings=active,
        summary=(
            f"Relaytic harvested `{len(harvested)}` learning(s) from this run and selected `{len(active)}` active learning(s) "
            "for later reuse."
        ),
        trace=trace,
    )
    markdown = render_learnings_markdown(state_artifact.to_dict(), snapshot=snapshot.to_dict())
    write_learnings_state(state_dir, artifact=state_artifact)
    write_learnings_markdown(state_dir, markdown=markdown)
    write_learnings_snapshot(root, artifact=snapshot)
    return LearningSyncResult(state=state_artifact, snapshot=snapshot, markdown=markdown)


def reset_learnings(
    *,
    run_dir: str | Path | None = None,
    state_dir: str | Path | None = None,
    policy: dict[str, Any] | None = None,
) -> LearningsResetArtifact:
    """Reset the durable learnings state."""

    resolved_state_dir = Path(state_dir) if state_dir is not None else default_learnings_state_dir(run_dir=run_dir)
    controls = build_learning_controls_from_policy(policy)
    existing_state = read_learnings_state(resolved_state_dir)
    removed_count = len([item for item in existing_state.get("entries", []) if isinstance(item, dict)])
    trace = _trace()
    state_artifact = LearningsStateArtifact(
        schema_version=LEARNINGS_STATE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="reset",
        state_dir=str(resolved_state_dir),
        entry_count=0,
        entries=[],
        summary="Relaytic reset the durable learnings state. Future runs can rebuild it from fresh evidence.",
        trace=trace,
    )
    markdown = render_learnings_markdown(state_artifact.to_dict(), snapshot=None)
    write_learnings_state(resolved_state_dir, artifact=state_artifact)
    write_learnings_markdown(resolved_state_dir, markdown=markdown)
    if run_dir is not None:
        run_root = Path(run_dir)
        existing_snapshot = read_learnings_snapshot(run_root)
        run_id = _clean_text(existing_snapshot.get("run_id")) or run_root.name or "run"
        snapshot = LabLearningsSnapshotArtifact(
            schema_version=LAB_LEARNINGS_SNAPSHOT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="reset",
            run_id=run_id,
            state_dir=str(resolved_state_dir),
            learnings_state_path=str(resolved_state_dir / LEARNINGS_STATE_FILENAME),
            learnings_md_path=str(resolved_state_dir / LEARNINGS_MARKDOWN_FILENAME),
            state_entry_count=0,
            harvested_count=0,
            active_count=0,
            harvested_learnings=[],
            active_learnings=[],
            summary="Relaytic reset durable learnings for this workspace and cleared the active learnings snapshot.",
            trace=trace,
        )
        write_learnings_snapshot(run_root, artifact=snapshot)
    return LearningsResetArtifact(
        schema_version=LEARNINGS_RESET_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        state_dir=str(resolved_state_dir),
        removed_entry_count=removed_count,
        summary=f"Relaytic removed `{removed_count}` durable learning(s) from local memory.",
        trace=trace,
    )


def render_learnings_markdown(state_payload: dict[str, Any], *, snapshot: dict[str, Any] | None = None) -> str:
    """Render a concise human-readable learnings view."""

    entries = [dict(item) for item in state_payload.get("entries", []) if isinstance(item, dict)]
    active = [dict(item) for item in dict(snapshot or {}).get("active_learnings", []) if isinstance(item, dict)]
    harvested = [dict(item) for item in dict(snapshot or {}).get("harvested_learnings", []) if isinstance(item, dict)]
    lines = [
        "# Relaytic Learnings",
        "",
        f"- State status: `{state_payload.get('status') or 'unknown'}`",
        f"- Stored learnings: `{state_payload.get('entry_count', 0)}`",
        f"- State directory: `{state_payload.get('state_dir') or 'unknown'}`",
    ]
    if snapshot:
        lines.extend(
            [
                f"- Active for this run: `{snapshot.get('active_count', 0)}`",
                f"- Harvested from this run: `{snapshot.get('harvested_count', 0)}`",
            ]
        )
    if active:
        lines.extend(["", "## Active Learnings For This Run"])
        for item in active[:6]:
            lines.append(f"- `{item.get('kind') or 'learning'}`: {item.get('lesson') or 'No lesson recorded.'}")
    if harvested:
        lines.extend(["", "## Fresh Learnings From This Run"])
        for item in harvested[:6]:
            lines.append(f"- `{item.get('kind') or 'learning'}`: {item.get('lesson') or 'No lesson recorded.'}")
    if entries:
        lines.extend(["", "## Durable Learnings"])
        for item in entries[:8]:
            tags = [str(tag).strip() for tag in item.get("applicability_tags", []) if str(tag).strip()]
            tag_text = f" | tags `{', '.join(tags)}`" if tags else ""
            lines.append(f"- `{item.get('kind') or 'learning'}`: {item.get('lesson') or 'No lesson recorded.'}{tag_text}")
    lines.extend(
        [
            "",
            "## Controls",
            "- Reset durable learnings: `relaytic learnings reset --run-dir <run_dir>`",
            "- Show durable learnings: `relaytic learnings show --run-dir <run_dir>`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _harvest_learnings(
    *,
    summary_payload: dict[str, Any],
    handoff_bundle: dict[str, Any],
    controls: LearningControls,
) -> list[dict[str, Any]]:
    run_id = _clean_text(summary_payload.get("run_id")) or "run"
    generated_at = _utc_now()
    entries: list[dict[str, Any]] = []
    assumptions = dict(summary_payload.get("assumptions", {}))
    if controls.track_assumptions:
        for item in list(assumptions.get("items", []))[:3]:
            text = _clean_text(item)
            if not text:
                continue
            entries.append(
                _entry(
                    run_id=run_id,
                    kind="assumption",
                    lesson=f"Earlier runs with this context assumed: {text}",
                    tags=_summary_tags(summary_payload) + ["assumption"],
                    refs=["run_summary.json", "assumption_log.json"],
                    generated_at=generated_at,
                )
            )
    feedback = dict(summary_payload.get("feedback", {}))
    if controls.track_feedback and _clean_text(feedback.get("primary_recommended_action")):
        entries.append(
            _entry(
                run_id=run_id,
                kind="feedback",
                lesson=(
                    f"Accepted feedback in this run pushed Relaytic toward `{feedback.get('primary_recommended_action')}`."
                ),
                tags=_summary_tags(summary_payload) + ["feedback"],
                refs=["feedback_effect_report.json", "feedback_casebook.json"],
                generated_at=generated_at,
            )
        )
    control = dict(summary_payload.get("control", {}))
    if controls.track_control_lessons and int(control.get("suspicious_count", 0) or 0) > 0:
        entries.append(
            _entry(
                run_id=run_id,
                kind="control",
                lesson=(
                    f"Unsafe or bypass-like steering appeared `{control.get('suspicious_count', 0)}` time(s); "
                    "Relaytic should stay skeptical with similar requests."
                ),
                tags=_summary_tags(summary_payload) + ["control"],
                refs=["control_challenge_report.json", "control_injection_audit.json"],
                generated_at=generated_at,
            )
        )
    benchmark = dict(summary_payload.get("benchmark", {}))
    incumbent_name = _clean_text(benchmark.get("incumbent_name"))
    if incumbent_name:
        if bool(benchmark.get("relaytic_beats_incumbent")):
            lesson = f"Relaytic beat incumbent `{incumbent_name}` under the same contract."
        else:
            lesson = f"Incumbent `{incumbent_name}` remained stronger or not yet beaten under the same contract."
        entries.append(
            _entry(
                run_id=run_id,
                kind="benchmark",
                lesson=lesson,
                tags=_summary_tags(summary_payload) + ["benchmark"],
                refs=["incumbent_parity_report.json", "benchmark_parity_report.json"],
                generated_at=generated_at,
            )
        )
    next_focus = dict(handoff_bundle.get("next_run_focus") or {}) if isinstance(handoff_bundle, dict) else {}
    if _clean_text(next_focus.get("selection_id")):
        lesson_text = f"The selected next-run focus for this problem is `{next_focus.get('selection_id')}`."
        if _clean_text(next_focus.get("notes")):
            lesson_text += f" Notes: {next_focus.get('notes')}."
        entries.append(
            _entry(
                run_id=run_id,
                kind="focus",
                lesson=lesson_text,
                tags=_summary_tags(summary_payload) + ["focus", _clean_text(next_focus.get("selection_id")) or "focus"],
                refs=["next_run_focus.json", "run_handoff.json"],
                generated_at=generated_at,
            )
        )
    evals = dict(summary_payload.get("evals", {}))
    if int(evals.get("failed_count", 0) or 0) > 0 or int(evals.get("security_open_finding_count", 0) or 0) > 0:
        entries.append(
            _entry(
                run_id=run_id,
                kind="safety",
                lesson=(
                    f"Agent/security evals still show `{evals.get('failed_count', 0)}` failed case(s) and "
                    f"`{evals.get('security_open_finding_count', 0)}` open security finding(s)."
                ),
                tags=_summary_tags(summary_payload) + ["safety"],
                refs=["agent_eval_matrix.json", "security_eval_report.json"],
                generated_at=generated_at,
            )
        )
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in entries:
        if item["entry_id"] in seen:
            continue
        seen.add(item["entry_id"])
        deduped.append(item)
    return deduped


def _select_active_learnings(
    *,
    entries: list[dict[str, Any]],
    summary_payload: dict[str, Any],
    controls: LearningControls,
) -> list[dict[str, Any]]:
    tags = set(_summary_tags(summary_payload))
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in entries:
        item_tags = {str(tag).strip() for tag in item.get("applicability_tags", []) if str(tag).strip()}
        overlap = len(tags.intersection(item_tags))
        recency_bonus = 1 if _clean_text(item.get("source_run_id")) == _clean_text(summary_payload.get("run_id")) else 0
        scored.append((overlap * 3 + recency_bonus, item))
    scored.sort(key=lambda pair: (pair[0], str(pair[1].get("last_updated_at") or "")), reverse=True)
    return [item for _, item in scored[: controls.max_active_entries] if _]


def _summary_tags(summary_payload: dict[str, Any]) -> list[str]:
    decision = dict(summary_payload.get("decision", {}))
    intent = dict(summary_payload.get("intent", {}))
    tags = [
        _clean_text(summary_payload.get("stage_completed")),
        _clean_text(decision.get("task_type")),
        _clean_text(decision.get("target_column")),
        _clean_text(intent.get("domain_archetype")),
    ]
    return [item for item in tags if item]


def _entry(
    *,
    run_id: str,
    kind: str,
    lesson: str,
    tags: list[str],
    refs: list[str],
    generated_at: str,
) -> dict[str, Any]:
    normalized_lesson = " ".join(lesson.strip().lower().split())
    digest = hashlib.sha1(f"{run_id}|{kind}|{normalized_lesson}".encode("utf-8")).hexdigest()[:12]
    return {
        "entry_id": f"learning_{digest}",
        "source_run_id": run_id,
        "kind": kind,
        "lesson": lesson,
        "applicability_tags": [str(tag).strip() for tag in tags if str(tag).strip()],
        "evidence_refs": [str(ref).strip() for ref in refs if str(ref).strip()],
        "last_updated_at": generated_at,
    }


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trace() -> LearningTrace:
    return LearningTrace(
        agent="learning_memory_coordinator",
        operating_mode="deterministic_cross_run_memory",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "run_summary",
            "handoff_bundle",
            "feedback_posture",
            "control_posture",
            "benchmark_posture",
            "agent_evals",
        ],
    )

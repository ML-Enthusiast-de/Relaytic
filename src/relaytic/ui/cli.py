"""Command line interface for local harness operations."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import re
import shutil
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


def artifact_entry(*args: Any, **kwargs: Any) -> Any:
    from relaytic.artifacts import artifact_entry as _artifact_entry

    return _artifact_entry(*args, **kwargs)


def write_manifest(*args: Any, **kwargs: Any) -> Path:
    from relaytic.artifacts import write_manifest as _write_manifest

    return _write_manifest(*args, **kwargs)


def _supported_task_types() -> list[str]:
    from relaytic.analytics import SUPPORTED_TASK_TYPES

    return sorted(SUPPORTED_TASK_TYPES)


def normalize_task_type_hint(value: str | None) -> str | None:
    from relaytic.analytics import normalize_task_type_hint as _normalize_task_type_hint

    return _normalize_task_type_hint(value)


def dumps_json(*args: Any, **kwargs: Any) -> str:
    from relaytic.core.json_utils import dumps_json as _dumps_json

    return _dumps_json(*args, **kwargs)


def normalize_candidate_model_family(value: str | None) -> str | None:
    from relaytic.modeling import normalize_candidate_model_family as _normalize_candidate_model_family

    return _normalize_candidate_model_family(value)


def run_inference_from_artifacts(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from relaytic.modeling import run_inference_from_artifacts as _run_inference_from_artifacts

    return _run_inference_from_artifacts(*args, **kwargs)


def build_default_registry() -> Any:
    from relaytic.orchestration.default_tools import build_default_registry as _build_default_registry

    return _build_default_registry()


def build_agent2_handoff_from_report_payload(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from relaytic.orchestration.handoff_contract import (
        build_agent2_handoff_from_report_payload as _build_agent2_handoff_from_report_payload,
    )

    return _build_agent2_handoff_from_report_payload(*args, **kwargs)


def run_local_agent_once(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from relaytic.orchestration.harness_runner import run_local_agent_once as _run_local_agent_once

    return _run_local_agent_once(*args, **kwargs)


def setup_local_llm(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from relaytic.orchestration.local_llm_setup import setup_local_llm as _setup_local_llm

    return _setup_local_llm(*args, **kwargs)


def git_guard_main(argv: list[str] | None = None) -> int:
    from relaytic.security.git_guard import main as _git_guard_main

    return _git_guard_main(argv)


def run_release_safety_scan(*args: Any, **kwargs: Any) -> Any:
    from relaytic.release_safety import run_release_safety_scan as _run_release_safety_scan

    return _run_release_safety_scan(*args, **kwargs)


def render_release_safety_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.release_safety import render_release_safety_markdown as _render_release_safety_markdown

    return _render_release_safety_markdown(*args, **kwargs)


def read_release_safety_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.release_safety import read_release_safety_bundle as _read_release_safety_bundle

    return _read_release_safety_bundle(*args, **kwargs)


def default_release_safety_state_dir(*args: Any, **kwargs: Any) -> Any:
    from relaytic.release_safety import (
        default_release_safety_state_dir as _default_release_safety_state_dir,
    )

    return _default_release_safety_state_dir(*args, **kwargs)


def latest_release_safety_state_dir(*args: Any, **kwargs: Any) -> Any:
    from relaytic.release_safety import (
        latest_release_safety_state_dir as _latest_release_safety_state_dir,
    )

    return _latest_release_safety_state_dir(*args, **kwargs)


def build_integration_inventory(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from relaytic.integrations import build_integration_inventory as _build_integration_inventory

    return _build_integration_inventory(*args, **kwargs)


def render_integration_inventory_markdown(*args: Any, **kwargs: Any) -> str:
    from relaytic.integrations import (
        render_integration_inventory_markdown as _render_integration_inventory_markdown,
    )

    return _render_integration_inventory_markdown(*args, **kwargs)


def build_integration_self_check_report(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from relaytic.integrations import (
        build_integration_self_check_report as _build_integration_self_check_report,
    )

    return _build_integration_self_check_report(*args, **kwargs)


def render_integration_self_check_markdown(*args: Any, **kwargs: Any) -> str:
    from relaytic.integrations import (
        render_integration_self_check_markdown as _render_integration_self_check_markdown,
    )

    return _render_integration_self_check_markdown(*args, **kwargs)


def load_policy(*args: Any, **kwargs: Any) -> Any:
    from relaytic.policies import load_policy as _load_policy

    return _load_policy(*args, **kwargs)


def write_resolved_policy(*args: Any, **kwargs: Any) -> Path:
    from relaytic.policies import write_resolved_policy as _write_resolved_policy

    return _write_resolved_policy(*args, **kwargs)


def run_investigation(*args: Any, **kwargs: Any) -> Any:
    from relaytic.investigation import run_investigation as _run_investigation

    return _run_investigation(*args, **kwargs)


def run_intake_interpretation(*args: Any, **kwargs: Any) -> Any:
    from relaytic.intake import run_intake_interpretation as _run_intake_interpretation

    return _run_intake_interpretation(*args, **kwargs)


def run_planning(*args: Any, **kwargs: Any) -> Any:
    from relaytic.planning import run_planning as _run_planning

    return _run_planning(*args, **kwargs)


def run_event_bus_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.events import run_event_bus_review as _run_event_bus_review

    return _run_event_bus_review(*args, **kwargs)


def render_event_bus_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.events import render_event_bus_markdown as _render_event_bus_markdown

    return _render_event_bus_markdown(*args, **kwargs)


def read_event_bus_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.events import read_event_bus_bundle as _read_event_bus_bundle

    return _read_event_bus_bundle(*args, **kwargs)


def run_permission_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.permissions import run_permission_review as _run_permission_review

    return _run_permission_review(*args, **kwargs)


def render_permission_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.permissions import render_permission_markdown as _render_permission_markdown

    return _render_permission_markdown(*args, **kwargs)


def evaluate_permission_action(*args: Any, **kwargs: Any) -> Any:
    from relaytic.permissions import evaluate_permission_action as _evaluate_permission_action

    return _evaluate_permission_action(*args, **kwargs)


def apply_permission_decision(*args: Any, **kwargs: Any) -> Any:
    from relaytic.permissions import apply_permission_decision as _apply_permission_decision

    return _apply_permission_decision(*args, **kwargs)


def run_daemon_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.daemon import run_daemon_review as _run_daemon_review

    return _run_daemon_review(*args, **kwargs)


def render_daemon_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.daemon import render_daemon_review_markdown as _render_daemon_review_markdown

    return _render_daemon_review_markdown(*args, **kwargs)


def read_daemon_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.daemon import read_daemon_bundle as _read_daemon_bundle

    return _read_daemon_bundle(*args, **kwargs)


def run_background_job(*args: Any, **kwargs: Any) -> Any:
    from relaytic.daemon import run_background_job as _run_background_job

    return _run_background_job(*args, **kwargs)


def resume_background_job(*args: Any, **kwargs: Any) -> Any:
    from relaytic.daemon import resume_background_job as _resume_background_job

    return _resume_background_job(*args, **kwargs)


def run_remote_control_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.remote_control import run_remote_control_review as _run_remote_control_review

    return _run_remote_control_review(*args, **kwargs)


def apply_remote_approval_decision(*args: Any, **kwargs: Any) -> Any:
    from relaytic.remote_control import (
        apply_remote_approval_decision as _apply_remote_approval_decision,
    )

    return _apply_remote_approval_decision(*args, **kwargs)


def apply_remote_supervision_handoff(*args: Any, **kwargs: Any) -> Any:
    from relaytic.remote_control import (
        apply_remote_supervision_handoff as _apply_remote_supervision_handoff,
    )

    return _apply_remote_supervision_handoff(*args, **kwargs)


def execute_planned_route(*args: Any, **kwargs: Any) -> Any:
    from relaytic.planning import execute_planned_route as _execute_planned_route

    return _execute_planned_route(*args, **kwargs)


def run_evidence_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.evidence import run_evidence_review as _run_evidence_review

    return _run_evidence_review(*args, **kwargs)


def run_memory_retrieval(*args: Any, **kwargs: Any) -> Any:
    from relaytic.memory import run_memory_retrieval as _run_memory_retrieval

    return _run_memory_retrieval(*args, **kwargs)


def read_memory_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.memory import read_memory_bundle as _read_memory_bundle

    return _read_memory_bundle(*args, **kwargs)


def render_memory_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.memory import render_memory_review_markdown as _render_memory_review_markdown

    return _render_memory_review_markdown(*args, **kwargs)


def run_intelligence_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.intelligence import run_intelligence_review as _run_intelligence_review

    return _run_intelligence_review(*args, **kwargs)


def run_research_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.research import run_research_review as _run_research_review

    return _run_research_review(*args, **kwargs)


def render_research_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.research import render_research_review_markdown as _render_research_review_markdown

    return _render_research_review_markdown(*args, **kwargs)


def run_benchmark_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.benchmark import run_benchmark_review as _run_benchmark_review

    return _run_benchmark_review(*args, **kwargs)


def read_benchmark_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.benchmark import read_benchmark_bundle as _read_benchmark_bundle

    return _read_benchmark_bundle(*args, **kwargs)


def render_benchmark_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.benchmark import render_benchmark_review_markdown as _render_benchmark_review_markdown

    return _render_benchmark_review_markdown(*args, **kwargs)


def run_feedback_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.feedback import run_feedback_review as _run_feedback_review

    return _run_feedback_review(*args, **kwargs)


def append_feedback_entries(*args: Any, **kwargs: Any) -> Any:
    from relaytic.feedback import append_feedback_entries as _append_feedback_entries

    return _append_feedback_entries(*args, **kwargs)


def rollback_feedback_entry(*args: Any, **kwargs: Any) -> Any:
    from relaytic.feedback import rollback_feedback_entry as _rollback_feedback_entry

    return _rollback_feedback_entry(*args, **kwargs)


def read_feedback_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.feedback import read_feedback_bundle as _read_feedback_bundle

    return _read_feedback_bundle(*args, **kwargs)


def render_feedback_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.feedback import render_feedback_review_markdown as _render_feedback_review_markdown

    return _render_feedback_review_markdown(*args, **kwargs)


def run_profiles_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.profiles import run_profiles_review as _run_profiles_review

    return _run_profiles_review(*args, **kwargs)


def read_profiles_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.profiles import read_profiles_bundle as _read_profiles_bundle

    return _read_profiles_bundle(*args, **kwargs)


def render_profiles_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.profiles import render_profiles_review_markdown as _render_profiles_review_markdown

    return _render_profiles_review_markdown(*args, **kwargs)


def run_dojo_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.dojo import run_dojo_review as _run_dojo_review

    return _run_dojo_review(*args, **kwargs)


def rollback_dojo_promotion(*args: Any, **kwargs: Any) -> Any:
    from relaytic.dojo import rollback_dojo_promotion as _rollback_dojo_promotion

    return _rollback_dojo_promotion(*args, **kwargs)


def read_dojo_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.dojo import read_dojo_bundle as _read_dojo_bundle

    return _read_dojo_bundle(*args, **kwargs)


def render_dojo_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.dojo import render_dojo_review_markdown as _render_dojo_review_markdown

    return _render_dojo_review_markdown(*args, **kwargs)


def run_pulse_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.pulse import run_pulse_review as _run_pulse_review

    return _run_pulse_review(*args, **kwargs)


def read_pulse_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.pulse import read_pulse_bundle as _read_pulse_bundle

    return _read_pulse_bundle(*args, **kwargs)


def render_pulse_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.pulse import render_pulse_review_markdown as _render_pulse_review_markdown

    return _render_pulse_review_markdown(*args, **kwargs)


def run_mission_control_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.mission_control import run_mission_control_review as _run_mission_control_review

    return _run_mission_control_review(*args, **kwargs)


def read_mission_control_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.mission_control import read_mission_control_bundle as _read_mission_control_bundle

    return _read_mission_control_bundle(*args, **kwargs)


def render_mission_control_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.mission_control import render_mission_control_markdown as _render_mission_control_markdown

    return _render_mission_control_markdown(*args, **kwargs)


def run_handoff_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.handoff import run_handoff_review as _run_handoff_review

    return _run_handoff_review(*args, **kwargs)


def apply_next_run_focus(*args: Any, **kwargs: Any) -> Any:
    from relaytic.handoff import apply_next_run_focus as _apply_next_run_focus

    return _apply_next_run_focus(*args, **kwargs)


def read_handoff_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.handoff import read_handoff_bundle as _read_handoff_bundle

    return _read_handoff_bundle(*args, **kwargs)


def render_handoff_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.handoff import render_handoff_review_markdown as _render_handoff_review_markdown

    return _render_handoff_review_markdown(*args, **kwargs)


def write_next_run_focus(*args: Any, **kwargs: Any) -> Any:
    from relaytic.handoff import write_next_run_focus as _write_next_run_focus

    return _write_next_run_focus(*args, **kwargs)


def default_learnings_state_dir(*args: Any, **kwargs: Any) -> Any:
    from relaytic.learnings import default_learnings_state_dir as _default_learnings_state_dir

    return _default_learnings_state_dir(*args, **kwargs)


def read_learnings_state(*args: Any, **kwargs: Any) -> Any:
    from relaytic.learnings import read_learnings_state as _read_learnings_state

    return _read_learnings_state(*args, **kwargs)


def read_learnings_snapshot(*args: Any, **kwargs: Any) -> Any:
    from relaytic.learnings import read_learnings_snapshot as _read_learnings_snapshot

    return _read_learnings_snapshot(*args, **kwargs)


def reset_learnings(*args: Any, **kwargs: Any) -> Any:
    from relaytic.learnings import reset_learnings as _reset_learnings

    return _reset_learnings(*args, **kwargs)


def render_learnings_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.learnings import render_learnings_markdown as _render_learnings_markdown

    return _render_learnings_markdown(*args, **kwargs)


def default_workspace_dir(*args: Any, **kwargs: Any) -> Any:
    from relaytic.workspace import default_workspace_dir as _default_workspace_dir

    return _default_workspace_dir(*args, **kwargs)


def read_workspace_bundle_for_run(*args: Any, **kwargs: Any) -> Any:
    from relaytic.workspace import read_workspace_bundle_for_run as _read_workspace_bundle_for_run

    return _read_workspace_bundle_for_run(*args, **kwargs)


def read_result_contract_artifacts(*args: Any, **kwargs: Any) -> Any:
    from relaytic.workspace import read_result_contract_artifacts as _read_result_contract_artifacts

    return _read_result_contract_artifacts(*args, **kwargs)


def render_workspace_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.workspace import render_workspace_review_markdown as _render_workspace_review_markdown

    return _render_workspace_review_markdown(*args, **kwargs)


def read_iteration_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.iteration import read_iteration_bundle as _read_iteration_bundle

    return _read_iteration_bundle(*args, **kwargs)


def run_control_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.control import run_control_review as _run_control_review

    return _run_control_review(*args, **kwargs)


def read_control_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.control import read_control_bundle as _read_control_bundle

    return _read_control_bundle(*args, **kwargs)


def render_control_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.control import render_control_review_markdown as _render_control_review_markdown

    return _render_control_review_markdown(*args, **kwargs)


def build_assist_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.assist import build_assist_bundle as _build_assist_bundle

    return _build_assist_bundle(*args, **kwargs)


def plan_assist_turn(*args: Any, **kwargs: Any) -> Any:
    from relaytic.assist import plan_assist_turn as _plan_assist_turn

    return _plan_assist_turn(*args, **kwargs)


def render_assist_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.assist import render_assist_markdown as _render_assist_markdown

    return _render_assist_markdown(*args, **kwargs)


def render_intelligence_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.intelligence import (
        render_intelligence_review_markdown as _render_intelligence_review_markdown,
    )

    return _render_intelligence_review_markdown(*args, **kwargs)


def run_autonomy_loop(*args: Any, **kwargs: Any) -> Any:
    from relaytic.autonomy import run_autonomy_loop as _run_autonomy_loop

    return _run_autonomy_loop(*args, **kwargs)


def render_autonomy_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.autonomy import render_autonomy_review_markdown as _render_autonomy_review_markdown

    return _render_autonomy_review_markdown(*args, **kwargs)


def ensure_runtime_initialized(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import ensure_runtime_initialized as _ensure_runtime_initialized

    return _ensure_runtime_initialized(*args, **kwargs)


def build_runtime_surface(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import build_runtime_surface as _build_runtime_surface

    return _build_runtime_surface(*args, **kwargs)


def build_runtime_events_surface(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import build_runtime_events_surface as _build_runtime_events_surface

    return _build_runtime_events_surface(*args, **kwargs)


def build_materialization_surface(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import build_materialization_surface as _build_materialization_surface

    return _build_materialization_surface(*args, **kwargs)


def render_runtime_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import render_runtime_markdown as _render_runtime_markdown

    return _render_runtime_markdown(*args, **kwargs)


def render_runtime_events_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import render_runtime_events_markdown as _render_runtime_events_markdown

    return _render_runtime_events_markdown(*args, **kwargs)


def render_materialization_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import render_materialization_markdown as _render_materialization_markdown

    return _render_materialization_markdown(*args, **kwargs)


def record_runtime_stage_start(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import record_stage_start as _record_stage_start

    return _record_stage_start(*args, **kwargs)


def record_runtime_stage_completion(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import record_stage_completion as _record_stage_completion

    return _record_stage_completion(*args, **kwargs)


def record_runtime_stage_failure(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import record_stage_failure as _record_stage_failure

    return _record_stage_failure(*args, **kwargs)


def record_runtime_event(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import record_runtime_event as _record_runtime_event

    return _record_runtime_event(*args, **kwargs)


def sync_materialization_runtime_artifacts(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import sync_materialization_runtime_artifacts as _sync_materialization_runtime_artifacts

    return _sync_materialization_runtime_artifacts(*args, **kwargs)


def stage_recompute_entry(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runtime import stage_recompute_entry as _stage_recompute_entry

    return _stage_recompute_entry(*args, **kwargs)


def materialize_run_summary(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runs import materialize_run_summary as _materialize_run_summary

    return _materialize_run_summary(*args, **kwargs)


def read_run_summary(*args: Any, **kwargs: Any) -> Any:
    from relaytic.runs import read_run_summary as _read_run_summary

    return _read_run_summary(*args, **kwargs)


def read_evidence_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.evidence import read_evidence_bundle as _read_evidence_bundle

    return _read_evidence_bundle(*args, **kwargs)


def run_completion_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.completion import run_completion_review as _run_completion_review

    return _run_completion_review(*args, **kwargs)


def read_completion_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.completion import read_completion_bundle as _read_completion_bundle

    return _read_completion_bundle(*args, **kwargs)


def render_completion_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.completion import (
        render_completion_review_markdown as _render_completion_review_markdown,
    )

    return _render_completion_review_markdown(*args, **kwargs)


def run_lifecycle_review(*args: Any, **kwargs: Any) -> Any:
    from relaytic.lifecycle import run_lifecycle_review as _run_lifecycle_review

    return _run_lifecycle_review(*args, **kwargs)


def read_lifecycle_bundle(*args: Any, **kwargs: Any) -> Any:
    from relaytic.lifecycle import read_lifecycle_bundle as _read_lifecycle_bundle

    return _read_lifecycle_bundle(*args, **kwargs)


def render_lifecycle_review_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.lifecycle import (
        render_lifecycle_review_markdown as _render_lifecycle_review_markdown,
    )

    return _render_lifecycle_review_markdown(*args, **kwargs)


def build_doctor_report(*args: Any, **kwargs: Any) -> Any:
    from relaytic.ui.doctor import build_doctor_report as _build_doctor_report

    return _build_doctor_report(*args, **kwargs)


def render_doctor_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.ui.doctor import render_doctor_markdown as _render_doctor_markdown

    return _render_doctor_markdown(*args, **kwargs)


def build_interoperability_inventory(*args: Any, **kwargs: Any) -> Any:
    from relaytic.interoperability import build_interoperability_inventory as _build_interoperability_inventory

    return _build_interoperability_inventory(*args, **kwargs)


def render_interoperability_inventory_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.interoperability import (
        render_interoperability_inventory_markdown as _render_interoperability_inventory_markdown,
    )

    return _render_interoperability_inventory_markdown(*args, **kwargs)


def build_interoperability_self_check_report(*args: Any, **kwargs: Any) -> Any:
    from relaytic.interoperability import (
        build_interoperability_self_check_report as _build_interoperability_self_check_report,
    )

    return _build_interoperability_self_check_report(*args, **kwargs)


def render_interoperability_self_check_markdown(*args: Any, **kwargs: Any) -> Any:
    from relaytic.interoperability import (
        render_interoperability_self_check_markdown as _render_interoperability_self_check_markdown,
    )

    return _render_interoperability_self_check_markdown(*args, **kwargs)


def export_host_bundles(*args: Any, **kwargs: Any) -> Any:
    from relaytic.interoperability import export_host_bundles as _export_host_bundles

    return _export_host_bundles(*args, **kwargs)


def serve_relaytic_mcp(*args: Any, **kwargs: Any) -> Any:
    from relaytic.interoperability import serve_relaytic_mcp as _serve_relaytic_mcp

    return _serve_relaytic_mcp(*args, **kwargs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="relaytic", description="Relaytic CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run_agent = sub.add_parser(
        "run-agent-once",
        help="Run one local agent loop (tool-calling + response).",
    )
    run_agent.add_argument(
        "--agent",
        choices=["analyst", "modeler"],
        required=True,
        help="Which agent system prompt to use.",
    )
    run_agent.add_argument(
        "--message",
        required=True,
        help="User message injected into loop context.",
    )
    run_agent.add_argument(
        "--context-json",
        default="{}",
        help="Additional JSON context object passed to the loop.",
    )
    run_agent.add_argument(
        "--config",
        default=None,
        help="Optional config path (otherwise default config resolution is used).",
    )

    run_session = sub.add_parser(
        "run-agent-session",
        help="Run interactive multi-turn local agent session.",
    )
    run_session.add_argument(
        "--agent",
        choices=["analyst", "modeler"],
        required=True,
        help="Which agent system prompt to use.",
    )
    run_session.add_argument(
        "--context-json",
        default="{}",
        help="Base JSON context object persisted across turns.",
    )
    run_session.add_argument(
        "--config",
        default=None,
        help="Optional config path (otherwise default config resolution is used).",
    )
    run_session.add_argument(
        "--show-json",
        action="store_true",
        help="Print full JSON payload for each turn in addition to assistant text.",
    )
    run_session.add_argument(
        "--max-turns",
        type=int,
        default=0,
        help="Optional positive turn cap. 0 means unlimited until /exit.",
    )

    setup_llm = sub.add_parser(
        "setup-local-llm",
        help="Install/check local LLM runtime and ensure model availability.",
    )
    setup_llm.add_argument(
        "--provider",
        choices=["ollama", "llama_cpp", "llama.cpp", "openai", "openai_compatible"],
        default=None,
        help="Override provider. Defaults to configured runtime provider.",
    )
    setup_llm.add_argument(
        "--profile",
        default=None,
        help="Optional runtime profile name.",
    )
    setup_llm.add_argument(
        "--model",
        default=None,
        help="Optional model override (ollama tag or llama.cpp alias/path).",
    )
    setup_llm.add_argument(
        "--endpoint",
        default=None,
        help="Optional endpoint override.",
    )
    setup_llm.add_argument(
        "--config",
        default=None,
        help="Optional config path.",
    )
    setup_llm.add_argument(
        "--install-provider",
        action="store_true",
        help="Attempt to install runtime provider if missing (via winget on Windows).",
    )
    setup_llm.add_argument(
        "--no-start-runtime",
        action="store_true",
        help="Skip runtime auto-start.",
    )
    setup_llm.add_argument(
        "--no-pull-model",
        action="store_true",
        help="Skip `ollama pull` when provider is ollama.",
    )
    setup_llm.add_argument(
        "--no-download-model",
        action="store_true",
        help="Skip GGUF download when provider is llama.cpp and file is missing.",
    )
    setup_llm.add_argument(
        "--llama-model-path",
        default=None,
        help="Override local GGUF path for llama.cpp setup.",
    )
    setup_llm.add_argument(
        "--llama-model-url",
        default=None,
        help="Optional GGUF download URL for llama.cpp setup.",
    )
    setup_llm.add_argument(
        "--timeout-seconds",
        type=int,
        default=120,
        help="HTTP timeout for setup checks.",
    )

    run_agent1 = sub.add_parser(
        "run-agent1-analysis",
        help="Run deterministic Agent 1 analysis directly (no LLM call).",
    )
    run_agent1.add_argument("--data-path", required=True, help="Structured data source path such as CSV, Parquet, JSONL, or Excel.")
    run_agent1.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    run_agent1.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    run_agent1.add_argument(
        "--data-start-row",
        type=int,
        default=None,
        help="Optional data start row.",
    )
    run_agent1.add_argument("--timestamp-column", default=None, help="Timestamp column name.")
    run_agent1.add_argument(
        "--task-type",
        default=None,
        help=(
            "Optional task override: regression, binary_classification, "
            "multiclass_classification, fraud_detection, anomaly_detection."
        ),
    )
    run_agent1.add_argument(
        "--target-signals",
        nargs="*",
        default=None,
        help="Optional target signal list.",
    )
    run_agent1.add_argument(
        "--predictor-map-json",
        default="{}",
        help="JSON object mapping target->predictor list, optional wildcard '*' key.",
    )
    run_agent1.add_argument(
        "--forced-requests-json",
        default="[]",
        help="JSON array of forced requests: [{target_signal,predictor_signals,user_reason}]",
    )
    run_agent1.add_argument(
        "--user-hypotheses-json",
        default="[]",
        help="JSON array of correlation hypotheses: [{target_signal,predictor_signals,user_reason}]",
    )
    run_agent1.add_argument(
        "--feature-hypotheses-json",
        default="[]",
        help=(
            "JSON array of feature hypotheses: "
            "[{target_signal?,base_signal,transformation,user_reason}]"
        ),
    )
    run_agent1.add_argument("--max-lag", type=int, default=8)
    run_agent1.add_argument("--no-feature-engineering", action="store_true")
    run_agent1.add_argument("--feature-gain-threshold", type=float, default=0.05)
    run_agent1.add_argument("--confidence-top-k", type=int, default=10)
    run_agent1.add_argument("--bootstrap-rounds", type=int, default=40)
    run_agent1.add_argument("--stability-windows", type=int, default=4)
    run_agent1.add_argument("--max-samples", type=int, default=None)
    run_agent1.add_argument(
        "--sample-selection",
        choices=["uniform", "head", "tail"],
        default="uniform",
    )
    run_agent1.add_argument(
        "--missing-data-strategy",
        choices=["keep", "drop_rows", "fill_median", "fill_constant"],
        default="keep",
    )
    run_agent1.add_argument("--fill-constant-value", type=float, default=None)
    run_agent1.add_argument(
        "--row-coverage-strategy",
        choices=["keep", "drop_sparse_rows", "trim_dense_window", "manual_range"],
        default="keep",
    )
    run_agent1.add_argument("--sparse-row-min-fraction", type=float, default=0.8)
    run_agent1.add_argument("--row-range-start", type=int, default=None)
    run_agent1.add_argument("--row-range-end", type=int, default=None)
    run_agent1.add_argument("--no-strategy-search", action="store_true")
    run_agent1.add_argument("--strategy-search-candidates", type=int, default=4)
    run_agent1.add_argument("--no-save-artifacts", action="store_true")
    run_agent1.add_argument("--run-id", default=None)
    run_agent1.add_argument("--no-save-report", action="store_true")

    run_inference = sub.add_parser(
        "run-inference",
        help="Run deterministic inference from a saved checkpoint or run directory.",
    )
    source = run_inference.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--checkpoint-id",
        default=None,
        help="Checkpoint id from artifacts/checkpoints (e.g., ckpt_...).",
    )
    source.add_argument(
        "--run-dir",
        default=None,
        help="Run directory containing model_params.json and model state (e.g., artifacts/run_...).",
    )
    run_inference.add_argument("--data-path", required=True, help="Structured data source path such as CSV, Parquet, JSONL, a dataset directory, or a DuckDB file.")
    run_inference.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    run_inference.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    run_inference.add_argument(
        "--data-start-row",
        type=int,
        default=None,
        help="Optional data start row.",
    )
    run_inference.add_argument(
        "--delimiter",
        default=None,
        help="Optional CSV delimiter override.",
    )
    run_inference.add_argument("--source-type", choices=["auto", "snapshot", "stream", "lakehouse"], default="auto", help="How Relaytic should interpret the structured source.")
    run_inference.add_argument("--source-table", default=None, help="Optional table name for local DuckDB or lakehouse-style sources.")
    run_inference.add_argument("--sql-query", default=None, help="Optional read-only SQL query for local DuckDB sources.")
    run_inference.add_argument("--stream-window-rows", type=int, default=5000, help="When --source-type=stream, materialize only the most recent N rows into the inference snapshot.")
    run_inference.add_argument("--stream-format", choices=["auto", "csv", "tsv", "jsonl"], default="auto", help="Optional stream file format override.")
    run_inference.add_argument("--materialized-format", choices=["auto", "parquet", "csv"], default="auto", help="Preferred run-local snapshot format for stream and lakehouse inference sources.")
    run_inference.add_argument(
        "--decision-threshold",
        type=float,
        default=None,
        help="Optional binary threshold override (0..1) for classification inference.",
    )
    run_inference.add_argument(
        "--output-path",
        default=None,
        help="Optional output JSON path; defaults to reports/inference/<dataset>/inference_<timestamp>.json",
    )

    scan = sub.add_parser(
        "scan-git-safety",
        help="Scan repository for potential secret/system-path leaks.",
    )
    scan.add_argument(
        "paths",
        nargs="*",
        help="Optional files/directories. If omitted, scans git-tracked files.",
    )

    release_safety = sub.add_parser(
        "release-safety",
        help="Scan a workspace or built bundle for release leaks, package drift, and attestation posture.",
    )
    release_safety_sub = release_safety.add_subparsers(dest="release_safety_command", required=True)

    release_safety_scan = release_safety_sub.add_parser(
        "scan",
        help="Scan a built bundle or the tracked workspace and write release-safety artifacts plus attestation.",
    )
    release_safety_scan.add_argument(
        "--target-path",
        default=None,
        help="Optional built bundle path (file or directory). If omitted, scans git-tracked workspace files in pre-release mode.",
    )
    release_safety_scan.add_argument(
        "--state-dir",
        default=None,
        help="Optional output directory for release-safety artifacts. Defaults under artifacts/release_safety/.",
    )
    release_safety_scan.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    release_safety_show = release_safety_sub.add_parser(
        "show",
        help="Render the current release-safety bundle from a state directory.",
    )
    release_safety_show.add_argument(
        "--state-dir",
        default=None,
        help="Optional release-safety artifact directory. Defaults to the latest scan state.",
    )
    release_safety_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    doctor = sub.add_parser(
        "doctor",
        help="Verify install health, required dependencies, and wired integration compatibility.",
    )
    doctor.add_argument(
        "--expected-profile",
        choices=["core", "full"],
        default="core",
        help="Dependency profile to verify.",
    )
    doctor.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    integrations = sub.add_parser(
        "integrations",
        help="Inspect optional OSS capabilities Relaytic can adopt through explicit adapters.",
    )
    integrations_sub = integrations.add_subparsers(dest="integrations_command", required=True)

    integrations_show = integrations_sub.add_parser(
        "show",
        help="List optional integrations and whether they are installed locally.",
    )
    integrations_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    integrations_self_check = integrations_sub.add_parser(
        "self-check",
        help="Run compatibility smoke checks for the currently wired optional integrations.",
    )
    integrations_self_check.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    interoperability = sub.add_parser(
        "interoperability",
        help="Inspect, export, or serve Relaytic interoperability surfaces for common agent hosts.",
    )
    interoperability_sub = interoperability.add_subparsers(dest="interoperability_command", required=True)

    interoperability_show = interoperability_sub.add_parser(
        "show",
        help="Describe the current Relaytic MCP/tool surface and checked-in host bundles.",
    )
    interoperability_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    interoperability_self_check = interoperability_sub.add_parser(
        "self-check",
        help="Validate checked-in host bundles and optionally run a live Relaytic MCP stdio smoke test.",
    )
    interoperability_self_check.add_argument(
        "--live",
        action="store_true",
        help="Run a live stdio MCP smoke check in addition to static bundle validation.",
    )
    interoperability_self_check.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    interoperability_export = interoperability_sub.add_parser(
        "export",
        help="Export Relaytic host bundles for Claude, Codex/OpenAI, OpenClaw, or ChatGPT.",
    )
    interoperability_export.add_argument(
        "--host",
        choices=["claude", "codex", "openclaw", "chatgpt", "all"],
        default="all",
        help="Which host bundle to export.",
    )
    interoperability_export.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the host bundle should be written.",
    )
    interoperability_export.add_argument(
        "--mcp-command",
        default="python",
        help="Command that host wrappers should use to launch Relaytic MCP locally.",
    )
    interoperability_export.add_argument(
        "--public-mcp-url",
        default="https://example.com/mcp",
        help="Public HTTPS `/mcp` URL placeholder used in ChatGPT connector guidance.",
    )
    interoperability_export.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting existing bundle files in the output directory.",
    )
    interoperability_export.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    interoperability_serve = interoperability_sub.add_parser(
        "serve-mcp",
        help="Serve Relaytic over MCP using stdio or streamable HTTP.",
    )
    interoperability_serve.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="MCP transport to expose.",
    )
    interoperability_serve.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for streamable HTTP transport. Relaytic stays local-only by default.",
    )
    interoperability_serve.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for streamable HTTP transport.",
    )
    interoperability_serve.add_argument(
        "--mount-path",
        default="/mcp",
        help="HTTP mount path for streamable HTTP transport.",
    )

    manifest = sub.add_parser(
        "manifest",
        help="Create or inspect Relaytic artifact manifest scaffolds.",
    )
    manifest_sub = manifest.add_subparsers(dest="manifest_command", required=True)

    manifest_init = manifest_sub.add_parser(
        "init",
        help="Initialize `manifest.json` in a run directory.",
    )
    manifest_init.add_argument(
        "--run-dir",
        required=True,
        help="Run directory where `manifest.json` should be written.",
    )
    manifest_init.add_argument(
        "--run-id",
        default=None,
        help="Optional stable run id override. Defaults to the run directory name.",
    )
    manifest_init.add_argument(
        "--policy-source",
        default=None,
        help="Optional policy source path to record in the manifest.",
    )
    manifest_init.add_argument(
        "--label",
        action="append",
        default=[],
        help="Optional `key=value` labels. May be provided multiple times.",
    )
    manifest_init.add_argument(
        "--entry",
        action="append",
        default=[],
        help="Optional relative artifact path to register. May be provided multiple times.",
    )

    policy = sub.add_parser(
        "policy",
        help="Resolve and materialize Relaytic policy/config scaffolds.",
    )
    policy_sub = policy.add_subparsers(dest="policy_command", required=True)

    policy_resolve = policy_sub.add_parser(
        "resolve",
        help="Write `policy_resolved.yaml` from the configured policy source.",
    )
    policy_resolve.add_argument(
        "--config",
        default=None,
        help="Optional source config path. Defaults to standard Relaytic config resolution.",
    )
    policy_resolve.add_argument(
        "--output",
        required=True,
        help="Destination for the resolved policy YAML.",
    )

    mandate = sub.add_parser(
        "mandate",
        help="Initialize or inspect mandate foundation artifacts.",
    )
    mandate_sub = mandate.add_subparsers(dest="mandate_command", required=True)

    mandate_init = mandate_sub.add_parser(
        "init",
        help="Write `lab_mandate.json`, `work_preferences.json`, and `run_brief.json`.",
    )
    mandate_init.add_argument("--run-dir", required=True, help="Run directory for mandate artifacts.")
    mandate_init.add_argument("--config", default=None, help="Optional config/policy source.")
    mandate_init.add_argument("--overwrite", action="store_true", help="Allow overwriting existing mandate artifacts.")
    mandate_init.add_argument("--disable-mandate", action="store_true", help="Disable mandate influence in the written controls.")
    mandate_init.add_argument("--influence-mode", choices=["off", "advisory", "weighted", "binding", "constitutional"], default=None)
    mandate_init.add_argument("--lab-value", action="append", default=[], help="Repeatable long-term lab value.")
    mandate_init.add_argument("--hard-constraint", action="append", default=[], help="Repeatable hard constraint.")
    mandate_init.add_argument("--soft-preference", action="append", default=[], help="Repeatable soft preference.")
    mandate_init.add_argument("--prohibited-action", action="append", default=[], help="Repeatable prohibited action.")
    mandate_init.add_argument("--lab-notes", default="", help="Free-form lab mandate notes.")
    mandate_init.add_argument("--work-execution-mode", default=None, help="Preferred execution mode.")
    mandate_init.add_argument("--work-operation-mode", default=None, help="Preferred operation mode.")
    mandate_init.add_argument("--report-style", default="concise", help="Preferred report style.")
    mandate_init.add_argument("--effort-tier", default=None, help="Preferred effort tier.")
    mandate_init.add_argument("--work-notes", default="", help="Free-form work-preferences notes.")
    mandate_init.add_argument("--objective", default=None, help="Run objective override.")
    mandate_init.add_argument("--target-column", default=None, help="Target column for this run.")
    mandate_init.add_argument("--deployment-target", default=None, help="Deployment target description.")
    mandate_init.add_argument("--success-criterion", action="append", default=[], help="Repeatable success criterion.")
    mandate_init.add_argument("--binding-constraint", action="append", default=[], help="Repeatable run-level binding constraint.")
    mandate_init.add_argument("--run-notes", default="", help="Free-form run-brief notes.")

    mandate_show = mandate_sub.add_parser(
        "show",
        help="Print mandate artifacts from a run directory.",
    )
    mandate_show.add_argument("--run-dir", required=True, help="Run directory containing mandate artifacts.")

    context = sub.add_parser(
        "context",
        help="Initialize or inspect context foundation artifacts.",
    )
    context_sub = context.add_subparsers(dest="context_command", required=True)

    context_init = context_sub.add_parser(
        "init",
        help="Write `data_origin.json`, `domain_brief.json`, and `task_brief.json`.",
    )
    context_init.add_argument("--run-dir", required=True, help="Run directory for context artifacts.")
    context_init.add_argument("--config", default=None, help="Optional config/policy source.")
    context_init.add_argument("--overwrite", action="store_true", help="Allow overwriting existing context artifacts.")
    context_init.add_argument("--source-name", default=None, help="Human-readable data source name.")
    context_init.add_argument("--source-type", default=None, help="Source type such as snapshot, table, or stream.")
    context_init.add_argument("--acquisition-notes", default=None, help="How the data was acquired.")
    context_init.add_argument("--owner", default=None, help="Owning team or system.")
    context_init.add_argument("--contains-pii", action="store_true", help="Mark the dataset as containing PII.")
    context_init.add_argument("--access-constraint", action="append", default=[], help="Repeatable access constraint.")
    context_init.add_argument("--refresh-cadence", default=None, help="Expected data refresh cadence.")
    context_init.add_argument("--system-name", default=None, help="Name of the real-world system.")
    context_init.add_argument("--domain-summary", default=None, help="Domain summary.")
    context_init.add_argument("--target-meaning", default=None, help="Meaning of the target in domain terms.")
    context_init.add_argument("--known-caveat", action="append", default=[], help="Repeatable domain caveat.")
    context_init.add_argument("--suspicious-column", action="append", default=[], help="Repeatable suspicious column.")
    context_init.add_argument("--forbidden-feature", action="append", default=[], help="Repeatable forbidden feature.")
    context_init.add_argument("--domain-binding-constraint", action="append", default=[], help="Repeatable binding domain constraint.")
    context_init.add_argument("--domain-assumption", action="append", default=[], help="Repeatable domain assumption.")
    context_init.add_argument("--problem-statement", default=None, help="Task problem statement.")
    context_init.add_argument("--task-target-column", default=None, help="Target column referenced by the task brief.")
    context_init.add_argument("--prediction-horizon", default=None, help="Prediction horizon if applicable.")
    context_init.add_argument("--decision-type", default=None, help="Decision type description.")
    context_init.add_argument("--primary-stakeholder", default=None, help="Primary stakeholder for the task.")
    context_init.add_argument("--task-success-criterion", action="append", default=[], help="Repeatable task success criterion.")
    context_init.add_argument("--failure-cost", action="append", default=[], help="Repeatable failure cost note.")
    context_init.add_argument("--task-notes", default="", help="Free-form task-brief notes.")

    context_show = context_sub.add_parser(
        "show",
        help="Print context artifacts from a run directory.",
    )
    context_show.add_argument("--run-dir", required=True, help="Run directory containing context artifacts.")

    foundation = sub.add_parser(
        "foundation",
        help="Create the full Slice 02 run foundation in one command.",
    )
    foundation_sub = foundation.add_subparsers(dest="foundation_command", required=True)

    foundation_init = foundation_sub.add_parser(
        "init",
        help="Write policy, mandate, context, and manifest artifacts for a run directory.",
    )
    foundation_init.add_argument("--run-dir", required=True, help="Run directory to initialize.")
    foundation_init.add_argument("--config", default=None, help="Optional config/policy source.")
    foundation_init.add_argument("--run-id", default=None, help="Optional manifest run id.")
    foundation_init.add_argument("--overwrite", action="store_true", help="Allow overwriting existing foundation artifacts.")
    foundation_init.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")

    run_surface = sub.add_parser(
        "run",
        help="Run the first Relaytic MVP flow end to end on a dataset.",
    )
    run_surface.add_argument("--data-path", required=True, help="Structured data source path such as CSV, Parquet, JSONL, a dataset directory, or a DuckDB file.")
    run_surface.add_argument("--run-dir", default=None, help="Optional run directory. Defaults to a generated path under `artifacts/`.")
    run_surface.add_argument("--config", default=None, help="Optional config/policy source.")
    run_surface.add_argument("--run-id", default=None, help="Optional manifest run id.")
    run_surface.add_argument("--text", default=None, help="Optional free-form request text.")
    run_surface.add_argument(
        "--text-file",
        default=None,
        help="Optional UTF-8 text file containing the run request.",
    )
    run_surface.add_argument(
        "--actor-type",
        choices=["user", "operator", "agent"],
        default="user",
        help="Who produced the run request.",
    )
    run_surface.add_argument("--actor-name", default=None, help="Optional actor display name.")
    run_surface.add_argument("--channel", default="cli", help="Run-request channel label.")
    run_surface.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    run_surface.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    run_surface.add_argument("--data-start-row", type=int, default=None, help="Optional data start row.")
    run_surface.add_argument("--source-type", choices=["auto", "snapshot", "stream", "lakehouse"], default="auto", help="How Relaytic should interpret the structured source.")
    run_surface.add_argument("--source-table", default=None, help="Optional table name for local DuckDB or lakehouse-style sources.")
    run_surface.add_argument("--sql-query", default=None, help="Optional read-only SQL query for local DuckDB sources.")
    run_surface.add_argument("--stream-window-rows", type=int, default=5000, help="When --source-type=stream, materialize only the most recent N rows into the run snapshot.")
    run_surface.add_argument("--stream-format", choices=["auto", "csv", "tsv", "jsonl"], default="auto", help="Optional stream file format override.")
    run_surface.add_argument("--materialized-format", choices=["auto", "parquet", "csv"], default="auto", help="Preferred run-local snapshot format for stream and lakehouse sources.")
    run_surface.add_argument("--timestamp-column", default=None, help="Optional timestamp column override for investigation.")
    run_surface.add_argument("--overwrite", action="store_true", help="Allow overwriting existing intake, planning, and model artifacts.")
    run_surface.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    run_surface.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    show_surface = sub.add_parser(
        "show",
        help="Render a concise Relaytic run summary for humans or agents.",
    )
    show_surface.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    show_surface.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    predict_surface = sub.add_parser(
        "predict",
        help="Run inference through the accessible Relaytic prediction surface.",
    )
    predict_surface.add_argument("--run-dir", required=True, help="Run directory containing model artifacts.")
    predict_surface.add_argument("--data-path", required=True, help="Structured data source path such as CSV, Parquet, JSONL, a dataset directory, or a DuckDB file.")
    predict_surface.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    predict_surface.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    predict_surface.add_argument("--data-start-row", type=int, default=None, help="Optional data start row.")
    predict_surface.add_argument("--delimiter", default=None, help="Optional CSV delimiter override.")
    predict_surface.add_argument("--source-type", choices=["auto", "snapshot", "stream", "lakehouse"], default="auto", help="How Relaytic should interpret the structured source.")
    predict_surface.add_argument("--source-table", default=None, help="Optional table name for local DuckDB or lakehouse-style sources.")
    predict_surface.add_argument("--sql-query", default=None, help="Optional read-only SQL query for local DuckDB sources.")
    predict_surface.add_argument("--stream-window-rows", type=int, default=5000, help="When --source-type=stream, materialize only the most recent N rows into the inference snapshot.")
    predict_surface.add_argument("--stream-format", choices=["auto", "csv", "tsv", "jsonl"], default="auto", help="Optional stream file format override.")
    predict_surface.add_argument("--materialized-format", choices=["auto", "parquet", "csv"], default="auto", help="Preferred run-local snapshot format for stream and lakehouse inference sources.")
    predict_surface.add_argument(
        "--decision-threshold",
        type=float,
        default=None,
        help="Optional binary threshold override (0..1).",
    )
    predict_surface.add_argument(
        "--output-path",
        default=None,
        help="Optional output JSON path for persisted prediction payloads.",
    )
    predict_surface.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    source_surface = sub.add_parser(
        "source",
        help="Inspect or materialize structured sources into Relaytic's immutable run-local snapshot boundary.",
    )
    source_sub = source_surface.add_subparsers(dest="source_command", required=True)

    source_inspect = source_sub.add_parser(
        "inspect",
        help="Inspect how Relaytic will interpret a local structured source.",
    )
    source_inspect.add_argument("--source-path", required=True, help="Structured source path such as CSV, Parquet, JSONL, a dataset directory, or a DuckDB file.")
    source_inspect.add_argument("--source-type", choices=["auto", "snapshot", "stream", "lakehouse"], default="auto", help="How Relaytic should interpret the source.")
    source_inspect.add_argument("--source-table", default=None, help="Optional table name for local DuckDB or lakehouse-style sources.")
    source_inspect.add_argument("--sql-query", default=None, help="Optional read-only SQL query for local DuckDB sources.")
    source_inspect.add_argument("--stream-window-rows", type=int, default=5000, help="Preview the planned bounded stream window size.")
    source_inspect.add_argument("--stream-format", choices=["auto", "csv", "tsv", "jsonl"], default="auto", help="Optional stream file format override.")
    source_inspect.add_argument("--materialized-format", choices=["auto", "parquet", "csv"], default="auto", help="Preferred run-local snapshot format when materialization is needed.")
    source_inspect.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    source_materialize = source_sub.add_parser(
        "materialize",
        help="Materialize a local stream or lakehouse source into an immutable run-local snapshot.",
    )
    source_materialize.add_argument("--source-path", required=True, help="Structured source path such as CSV, Parquet, JSONL, a dataset directory, or a DuckDB file.")
    source_materialize.add_argument("--run-dir", required=True, help="Run directory where the staged snapshot should be created.")
    source_materialize.add_argument("--source-type", choices=["auto", "snapshot", "stream", "lakehouse"], default="auto", help="How Relaytic should interpret the source.")
    source_materialize.add_argument("--source-table", default=None, help="Optional table name for local DuckDB or lakehouse-style sources.")
    source_materialize.add_argument("--sql-query", default=None, help="Optional read-only SQL query for local DuckDB sources.")
    source_materialize.add_argument("--stream-window-rows", type=int, default=5000, help="When --source-type=stream, materialize only the most recent N rows.")
    source_materialize.add_argument("--stream-format", choices=["auto", "csv", "tsv", "jsonl"], default="auto", help="Optional stream file format override.")
    source_materialize.add_argument("--materialized-format", choices=["auto", "parquet", "csv"], default="auto", help="Preferred run-local snapshot format when materialization is needed.")
    source_materialize.add_argument("--purpose", choices=["primary", "evaluation", "inference"], default="primary", help="Why this snapshot is being materialized.")
    source_materialize.add_argument("--alias", default=None, help="Optional stable snapshot alias.")
    source_materialize.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    intake = sub.add_parser(
        "intake",
        help="Capture and interpret free-form user or agent input into foundation artifacts.",
    )
    intake_sub = intake.add_subparsers(dest="intake_command", required=True)

    intake_interpret = intake_sub.add_parser(
        "interpret",
        help="Write Slice 04 intake artifacts and update mandate/context bundles.",
    )
    intake_interpret.add_argument("--run-dir", required=True, help="Run directory for intake artifacts.")
    intake_interpret.add_argument("--config", default=None, help="Optional config/policy source.")
    intake_interpret.add_argument("--run-id", default=None, help="Optional manifest run id.")
    intake_interpret.add_argument("--text", default=None, help="Free-form intake text.")
    intake_interpret.add_argument(
        "--text-file",
        default=None,
        help="Optional UTF-8 text file containing the intake note.",
    )
    intake_interpret.add_argument(
        "--actor-type",
        choices=["user", "operator", "agent"],
        default="user",
        help="Who produced the intake text.",
    )
    intake_interpret.add_argument("--actor-name", default=None, help="Optional actor display name.")
    intake_interpret.add_argument("--channel", default="cli", help="Intake channel label.")
    intake_interpret.add_argument("--data-path", default=None, help="Optional structured dataset for schema alignment.")
    intake_interpret.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    intake_interpret.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    intake_interpret.add_argument("--data-start-row", type=int, default=None, help="Optional data start row.")
    intake_interpret.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing Slice 04 intake artifacts.",
    )
    intake_interpret.add_argument(
        "--label",
        action="append",
        default=[],
        help="Optional `key=value` label for the manifest.",
    )

    intake_show = intake_sub.add_parser(
        "show",
        help="Print Slice 04 intake artifacts from a run directory.",
    )
    intake_show.add_argument("--run-dir", required=True, help="Run directory containing intake artifacts.")

    intake_questions = intake_sub.add_parser(
        "questions",
        help="Print the optional clarification queue and assumption log for a run directory.",
    )
    intake_questions.add_argument("--run-dir", required=True, help="Run directory containing intake artifacts.")

    memory = sub.add_parser(
        "memory",
        help="Retrieve local analog-run memory and inspect the current memory bundle.",
    )
    memory_sub = memory.add_subparsers(dest="memory_command", required=True)

    memory_retrieve = memory_sub.add_parser(
        "retrieve",
        help="Refresh Slice 09A memory artifacts for the current run state.",
    )
    memory_retrieve.add_argument("--run-dir", required=True, help="Run directory for memory artifacts.")
    memory_retrieve.add_argument("--data-path", default=None, help="Optional structured data source path when the run has not recorded one yet.")
    memory_retrieve.add_argument("--config", default=None, help="Optional config/policy source.")
    memory_retrieve.add_argument("--run-id", default=None, help="Optional manifest run id.")
    memory_retrieve.add_argument(
        "--search-root",
        action="append",
        default=[],
        help="Optional local directory to scan for prior Relaytic runs. May be provided multiple times.",
    )
    memory_retrieve.add_argument(
        "--label",
        action="append",
        default=[],
        help="Optional `key=value` label for the manifest.",
    )
    memory_retrieve.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    memory_show = memory_sub.add_parser(
        "show",
        help="Print the current Slice 09A memory artifacts from a run directory.",
    )
    memory_show.add_argument("--run-dir", required=True, help="Run directory containing memory artifacts.")
    memory_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    intelligence_surface = sub.add_parser(
        "intelligence",
        help="Run or inspect Slice 09 structured semantic-task and debate artifacts.",
    )
    intelligence_sub = intelligence_surface.add_subparsers(dest="intelligence_command", required=True)

    intelligence_run = intelligence_sub.add_parser(
        "run",
        help="Execute Slice 09 semantic debate, context assembly, and document grounding for an existing run.",
    )
    intelligence_run.add_argument("--run-dir", required=True, help="Run directory for intelligence artifacts.")
    intelligence_run.add_argument("--config", default=None, help="Optional config/policy source.")
    intelligence_run.add_argument("--run-id", default=None, help="Optional manifest run id.")
    intelligence_run.add_argument("--overwrite", action="store_true", help="Allow overwriting existing intelligence artifacts.")
    intelligence_run.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    intelligence_run.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    intelligence_show = intelligence_sub.add_parser(
        "show",
        help="Render the current Slice 09 intelligence artifacts for a run.",
    )
    intelligence_show.add_argument("--run-dir", required=True, help="Run directory containing intelligence artifacts.")
    intelligence_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    research_surface = sub.add_parser(
        "research",
        help="Run or inspect Slice 09D privacy-safe external research retrieval.",
    )
    research_sub = research_surface.add_subparsers(dest="research_command", required=True)

    research_gather = research_sub.add_parser(
        "gather",
        help="Execute Slice 09D research retrieval, method transfer, and benchmark-reference distillation for an existing run.",
    )
    research_gather.add_argument("--run-dir", required=True, help="Run directory for research artifacts.")
    research_gather.add_argument("--config", default=None, help="Optional config/policy source.")
    research_gather.add_argument("--run-id", default=None, help="Optional manifest run id.")
    research_gather.add_argument("--overwrite", action="store_true", help="Allow overwriting existing research artifacts.")
    research_gather.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    research_gather.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    research_show = research_sub.add_parser(
        "show",
        help="Render the current Slice 09D research artifacts for a run.",
    )
    research_show.add_argument("--run-dir", required=True, help="Run directory containing research artifacts.")
    research_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    research_sources = research_sub.add_parser(
        "sources",
        help="List the typed external sources captured by Slice 09D for a run.",
    )
    research_sources.add_argument("--run-dir", required=True, help="Run directory containing research artifacts.")
    research_sources.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    benchmark_surface = sub.add_parser(
        "benchmark",
        help="Run or inspect Slice 11/11A benchmark parity, reference comparison, and incumbent-challenge artifacts.",
    )
    benchmark_sub = benchmark_surface.add_subparsers(dest="benchmark_command", required=True)

    benchmark_run = benchmark_sub.add_parser(
        "run",
        help="Execute Slice 11/11A same-contract benchmark parity review, optionally against an imported incumbent.",
    )
    benchmark_run.add_argument("--run-dir", required=True, help="Run directory for benchmark artifacts.")
    benchmark_run.add_argument("--data-path", default=None, help="Optional dataset override; defaults to the run dataset when discoverable.")
    benchmark_run.add_argument("--config", default=None, help="Optional config/policy source.")
    benchmark_run.add_argument("--run-id", default=None, help="Optional manifest run id.")
    benchmark_run.add_argument("--overwrite", action="store_true", help="Allow overwriting existing benchmark artifacts.")
    benchmark_run.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    benchmark_run.add_argument("--incumbent-path", default=None, help="Optional path to an imported incumbent model, prediction file, or ruleset.")
    benchmark_run.add_argument(
        "--incumbent-kind",
        choices=["auto", "model", "predictions", "ruleset"],
        default="auto",
        help="Optional incumbent type hint. Auto inspects the path when possible.",
    )
    benchmark_run.add_argument("--incumbent-name", default=None, help="Optional display name for the imported incumbent.")
    benchmark_run.add_argument(
        "--trust-incumbent-model",
        action="store_true",
        help=(
            "Allow Relaytic to deserialize an imported `.pkl` or `.joblib` incumbent model. "
            "This executes local pickle/joblib payloads and should only be used for trusted files."
        ),
    )
    benchmark_run.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    benchmark_show = benchmark_sub.add_parser(
        "show",
        help="Render the current Slice 11/11A benchmark and incumbent-challenge artifacts for a run.",
    )
    benchmark_show.add_argument("--run-dir", required=True, help="Run directory containing benchmark artifacts.")
    benchmark_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    decision_surface = sub.add_parser(
        "decision",
        help="Run or inspect Slice 10A decision-world modeling, controller logic, and local data-fabric artifacts.",
    )
    decision_sub = decision_surface.add_subparsers(dest="decision_command", required=True)

    decision_review = decision_sub.add_parser(
        "review",
        help="Execute Slice 10A decision-world reasoning for an existing run.",
    )
    decision_review.add_argument("--run-dir", required=True, help="Run directory for Slice 10A artifacts.")
    decision_review.add_argument("--config", default=None, help="Optional config/policy source.")
    decision_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    decision_review.add_argument("--overwrite", action="store_true", help="Allow overwriting existing decision artifacts.")
    decision_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    decision_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    decision_show = decision_sub.add_parser(
        "show",
        help="Render the current Slice 10A decision-lab artifacts for a run.",
    )
    decision_show.add_argument("--run-dir", required=True, help="Run directory containing Slice 10A artifacts.")
    decision_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    dojo_surface = sub.add_parser(
        "dojo",
        help="Run, inspect, or roll back Slice 12 guarded self-improvement artifacts.",
    )
    dojo_sub = dojo_surface.add_subparsers(dest="dojo_command", required=True)

    dojo_review = dojo_sub.add_parser(
        "review",
        help="Execute Slice 12 dojo review for an existing run under explicit quarantine gates.",
    )
    dojo_review.add_argument("--run-dir", required=True, help="Run directory for Slice 12 dojo artifacts.")
    dojo_review.add_argument("--config", default=None, help="Optional config/policy source.")
    dojo_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    dojo_review.add_argument("--overwrite", action="store_true", help="Allow overwriting existing dojo artifacts.")
    dojo_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    dojo_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    dojo_show = dojo_sub.add_parser(
        "show",
        help="Render the current Slice 12 dojo artifacts for a run.",
    )
    dojo_show.add_argument("--run-dir", required=True, help="Run directory containing Slice 12 dojo artifacts.")
    dojo_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    dojo_rollback = dojo_sub.add_parser(
        "rollback",
        help="Roll back one active Slice 12 dojo promotion while preserving the promotion ledger.",
    )
    dojo_rollback.add_argument("--run-dir", required=True, help="Run directory containing Slice 12 dojo artifacts.")
    dojo_rollback.add_argument("--proposal-id", required=True, help="Proposal id to roll back.")
    dojo_rollback.add_argument("--reason", default=None, help="Optional rollback reason recorded in the dojo ledger.")
    dojo_rollback.add_argument("--config", default=None, help="Optional config/policy source.")
    dojo_rollback.add_argument("--run-id", default=None, help="Optional manifest run id.")
    dojo_rollback.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    dojo_rollback.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    pulse_surface = sub.add_parser(
        "pulse",
        help="Run or inspect Slice 12A lab pulse artifacts for periodic awareness, watchlists, and bounded follow-up.",
    )
    pulse_sub = pulse_surface.add_subparsers(dest="pulse_command", required=True)

    pulse_review = pulse_sub.add_parser(
        "review",
        help="Execute Slice 12A pulse review for an existing run and record explicit skip/recommend/action artifacts.",
    )
    pulse_review.add_argument("--run-dir", required=True, help="Run directory for Slice 12A pulse artifacts.")
    pulse_review.add_argument("--config", default=None, help="Optional config/policy source.")
    pulse_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    pulse_review.add_argument("--overwrite", action="store_true", help="Allow overwriting existing pulse artifacts.")
    pulse_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    pulse_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    pulse_show = pulse_sub.add_parser(
        "show",
        help="Render the current Slice 12A pulse artifacts for a run.",
    )
    pulse_show.add_argument("--run-dir", required=True, help="Run directory containing Slice 12A pulse artifacts.")
    pulse_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    trace_surface = sub.add_parser(
        "trace",
        help="Inspect Slice 12B trace spans, competing claim packets, deterministic adjudication, and replay truth.",
    )
    trace_sub = trace_surface.add_subparsers(dest="trace_command", required=True)

    trace_show = trace_sub.add_parser(
        "show",
        help="Materialize and render the current Slice 12B trace review for a run.",
    )
    trace_show.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    trace_show.add_argument("--config", default=None, help="Optional config/policy source used when trace needs to be materialized.")
    trace_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    trace_replay = trace_sub.add_parser(
        "replay",
        help="Render the current Slice 12B replay timeline and winning-vs-losing claim story for a run.",
    )
    trace_replay.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    trace_replay.add_argument("--config", default=None, help="Optional config/policy source used when trace needs to be materialized.")
    trace_replay.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    evals_surface = sub.add_parser(
        "evals",
        help="Run or inspect Slice 12B protocol, security, and deterministic-debate proof evals.",
    )
    evals_sub = evals_surface.add_subparsers(dest="evals_command", required=True)

    evals_run = evals_sub.add_parser(
        "run",
        help="Execute the Slice 12B eval harness for an existing run and record protocol/security proof artifacts.",
    )
    evals_run.add_argument("--run-dir", required=True, help="Run directory for Slice 12B eval artifacts.")
    evals_run.add_argument("--config", default=None, help="Optional config/policy source.")
    evals_run.add_argument("--run-id", default=None, help="Optional manifest run id.")
    evals_run.add_argument("--overwrite", action="store_true", help="Allow overwriting existing eval artifacts.")
    evals_run.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    evals_run.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    evals_show = evals_sub.add_parser(
        "show",
        help="Render the current Slice 12B eval proof surface for a run.",
    )
    evals_show.add_argument("--run-dir", required=True, help="Run directory containing Slice 12B eval artifacts.")
    evals_show.add_argument("--config", default=None, help="Optional config/policy source used when evals need to be materialized.")
    evals_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    feedback_surface = sub.add_parser(
        "feedback",
        help="Record, review, rollback, or inspect Slice 10 feedback and downstream outcome artifacts.",
    )
    feedback_sub = feedback_surface.add_subparsers(dest="feedback_command", required=True)

    feedback_add = feedback_sub.add_parser(
        "add",
        help="Append one human, agent, runtime, benchmark, or outcome packet and refresh Slice 10 artifacts.",
    )
    feedback_add.add_argument("--run-dir", required=True, help="Run directory for feedback artifacts.")
    feedback_add.add_argument("--config", default=None, help="Optional config/policy source.")
    feedback_add.add_argument("--run-id", default=None, help="Optional manifest run id.")
    feedback_add.add_argument("--input-file", default=None, help="Optional JSON file containing one feedback dict or a list of feedback dicts.")
    feedback_add.add_argument("--feedback-id", default=None, help="Optional explicit feedback id when adding one inline packet.")
    feedback_add.add_argument(
        "--source-type",
        choices=["human", "external_agent", "runtime_failure", "benchmark_review", "outcome_observation"],
        default="human",
        help="Source type for inline feedback entry creation.",
    )
    feedback_add.add_argument(
        "--feedback-type",
        choices=["route_quality", "decision_policy", "data_quality", "outcome_evidence"],
        default="decision_policy",
        help="Feedback type for inline feedback entry creation.",
    )
    feedback_add.add_argument("--message", default="", help="Inline feedback message or rationale.")
    feedback_add.add_argument("--actor-name", default=None, help="Optional human or agent name.")
    feedback_add.add_argument("--suggested-route-family", default=None, help="Optional suggested model family.")
    feedback_add.add_argument("--suggested-action", default=None, help="Optional suggested decision-policy or follow-up action.")
    feedback_add.add_argument("--observed-outcome", default=None, help="Optional observed outcome, e.g. false_positive or false_negative.")
    feedback_add.add_argument("--evidence-level", choices=["weak", "medium", "strong"], default=None, help="Optional evidence strength override.")
    feedback_add.add_argument("--metric-name", default=None, help="Optional metric name attached to the feedback.")
    feedback_add.add_argument("--metric-value", default=None, help="Optional metric value attached to the feedback.")
    feedback_add.add_argument("--source-artifact", action="append", default=[], help="Optional cited artifact path. May be provided multiple times.")
    feedback_add.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    feedback_add.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    feedback_review = feedback_sub.add_parser(
        "review",
        help="Recompute Slice 10 feedback validation and reversible effect artifacts for an existing run.",
    )
    feedback_review.add_argument("--run-dir", required=True, help="Run directory for feedback artifacts.")
    feedback_review.add_argument("--config", default=None, help="Optional config/policy source.")
    feedback_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    feedback_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    feedback_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    feedback_show = feedback_sub.add_parser(
        "show",
        help="Render the current Slice 10 feedback artifacts for a run.",
    )
    feedback_show.add_argument("--run-dir", required=True, help="Run directory containing feedback artifacts.")
    feedback_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    feedback_rollback = feedback_sub.add_parser(
        "rollback",
        help="Mark one feedback packet as reverted and refresh Slice 10 artifacts.",
    )
    feedback_rollback.add_argument("--run-dir", required=True, help="Run directory for feedback artifacts.")
    feedback_rollback.add_argument("--feedback-id", required=True, help="Feedback id to revert.")
    feedback_rollback.add_argument("--config", default=None, help="Optional config/policy source.")
    feedback_rollback.add_argument("--run-id", default=None, help="Optional manifest run id.")
    feedback_rollback.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    feedback_rollback.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    profiles_surface = sub.add_parser(
        "profiles",
        help="Run or inspect Slice 10B quality contracts, budget contracts, and operator/lab profiles.",
    )
    profiles_sub = profiles_surface.add_subparsers(dest="profiles_command", required=True)

    profiles_review = profiles_sub.add_parser(
        "review",
        help="Recompute Slice 10B contracts and budget-consumption artifacts for an existing run.",
    )
    profiles_review.add_argument("--run-dir", required=True, help="Run directory for Slice 10B artifacts.")
    profiles_review.add_argument("--config", default=None, help="Optional config/policy source.")
    profiles_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    profiles_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    profiles_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    profiles_show = profiles_sub.add_parser(
        "show",
        help="Render the current Slice 10B quality and budget contract artifacts for a run.",
    )
    profiles_show.add_argument("--run-dir", required=True, help="Run directory containing Slice 10B artifacts.")
    profiles_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    control_surface = sub.add_parser(
        "control",
        help="Run or inspect Slice 10C behavioral control contracts, override decisions, and causal steering memory.",
    )
    control_sub = control_surface.add_subparsers(dest="control_command", required=True)

    control_review = control_sub.add_parser(
        "review",
        help="Review one intervention request against Relaytic's skeptical control contract without scraping prose.",
    )
    control_review.add_argument("--run-dir", required=True, help="Run directory for Slice 10C control artifacts.")
    control_review.add_argument("--message", required=True, help="Human or agent request to review.")
    control_review.add_argument("--config", default=None, help="Optional config/policy source.")
    control_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    control_review.add_argument("--actor-type", default="user", help="Actor type, e.g. user, operator, or agent.")
    control_review.add_argument("--actor-name", default=None, help="Optional actor name for the intervention request.")
    control_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    control_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    control_show = control_sub.add_parser(
        "show",
        help="Render the current Slice 10C control artifacts for a run.",
    )
    control_show.add_argument("--run-dir", required=True, help="Run directory containing Slice 10C control artifacts.")
    control_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    autonomy_surface = sub.add_parser(
        "autonomy",
        help="Run or inspect Slice 09C bounded autonomous follow-up loops.",
    )
    autonomy_sub = autonomy_surface.add_subparsers(dest="autonomy_command", required=True)

    autonomy_run = autonomy_sub.add_parser(
        "run",
        help="Execute one bounded autonomous follow-up round for an existing run.",
    )
    autonomy_run.add_argument("--run-dir", required=True, help="Run directory for autonomy artifacts.")
    autonomy_run.add_argument("--data-path", default=None, help="Optional dataset override; defaults to the run dataset when discoverable.")
    autonomy_run.add_argument("--config", default=None, help="Optional config/policy source.")
    autonomy_run.add_argument("--run-id", default=None, help="Optional manifest run id.")
    autonomy_run.add_argument("--overwrite", action="store_true", help="Allow overwriting existing autonomy artifacts.")
    autonomy_run.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    autonomy_run.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    autonomy_show = autonomy_sub.add_parser(
        "show",
        help="Render the current Slice 09C autonomy review for a run.",
    )
    autonomy_show.add_argument("--run-dir", required=True, help="Run directory containing autonomy artifacts.")
    autonomy_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    assist_surface = sub.add_parser(
        "assist",
        help="Run or inspect Slice 09E communicative Relaytic assistance for humans and agents.",
    )
    assist_sub = assist_surface.add_subparsers(dest="assist_command", required=True)

    assist_show = assist_sub.add_parser(
        "show",
        help="Render the current communicative assist state and connection guidance for a run.",
    )
    assist_show.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    assist_show.add_argument("--config", default=None, help="Optional config/policy source.")
    assist_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    assist_turn = assist_sub.add_parser(
        "turn",
        help="Send one communicative turn to Relaytic so it can explain, guide, rerun a stage, or take over.",
    )
    assist_turn.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    assist_turn.add_argument("--message", required=True, help="Human or agent message for Relaytic assist.")
    assist_turn.add_argument("--data-path", default=None, help="Optional dataset override for rerun/takeover flows.")
    assist_turn.add_argument("--config", default=None, help="Optional config/policy source.")
    assist_turn.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    assist_chat = assist_sub.add_parser(
        "chat",
        help="Run an interactive communicative Relaytic session over an existing run directory.",
    )
    assist_chat.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    assist_chat.add_argument("--data-path", default=None, help="Optional dataset override for rerun/takeover flows.")
    assist_chat.add_argument("--config", default=None, help="Optional config/policy source.")
    assist_chat.add_argument("--show-json", action="store_true", help="Print structured JSON payloads after each turn.")
    assist_chat.add_argument("--max-turns", type=int, default=0, help="Optional positive turn cap. 0 means unlimited until /exit.")

    runtime_surface = sub.add_parser(
        "runtime",
        help="Inspect the Slice 09B local lab gateway, event stream, hooks, and capability profiles.",
    )
    runtime_sub = runtime_surface.add_subparsers(dest="runtime_command", required=True)

    runtime_show = runtime_sub.add_parser(
        "show",
        help="Render the current runtime gateway surface for a run directory.",
    )
    runtime_show.add_argument("--run-dir", required=True, help="Run directory containing Relaytic runtime artifacts.")
    runtime_show.add_argument(
        "--limit",
        type=int,
        default=20,
        help="How many recent runtime events to include in the summary.",
    )
    runtime_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    runtime_events = runtime_sub.add_parser(
        "events",
        help="Show recent append-only runtime events for a run directory.",
    )
    runtime_events.add_argument("--run-dir", required=True, help="Run directory containing Relaytic runtime artifacts.")
    runtime_events.add_argument(
        "--limit",
        type=int,
        default=20,
        help="How many recent runtime events to return.",
    )
    runtime_events.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    runtime_reuse = runtime_sub.add_parser(
        "reuse",
        help="Inspect Slice 15E dependency graphs, freshness contracts, and recompute plans.",
    )
    runtime_reuse.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    runtime_reuse.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    events_surface = sub.add_parser(
        "events",
        help="Inspect the Slice 13B typed event bus, subscription registry, and hook dispatch projection.",
    )
    events_sub = events_surface.add_subparsers(dest="events_command", required=True)

    events_show = events_sub.add_parser(
        "show",
        help="Render the current event-bus surface for a run directory.",
    )
    events_show.add_argument("--run-dir", required=True, help="Run directory containing Relaytic runtime artifacts.")
    events_show.add_argument("--config", default=None, help="Optional config/policy source.")
    events_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    permissions_surface = sub.add_parser(
        "permissions",
        help="Inspect or evaluate the Slice 13B permission modes, approval posture, and session capability contract.",
    )
    permissions_sub = permissions_surface.add_subparsers(dest="permissions_command", required=True)

    permissions_show = permissions_sub.add_parser(
        "show",
        help="Render the current permission-mode and approval posture for a run directory.",
    )
    permissions_show.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    permissions_show.add_argument("--config", default=None, help="Optional config/policy source.")
    permissions_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    permissions_check = permissions_sub.add_parser(
        "check",
        help="Evaluate one tool or action against the current permission mode and append the decision to the permission log.",
    )
    permissions_check.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    permissions_check.add_argument("--action", required=True, help="Tool or action id such as `relaytic_run_autonomy` or `relaytic_review_search`.")
    permissions_check.add_argument("--config", default=None, help="Optional config/policy source.")
    permissions_check.add_argument("--mode", default=None, help="Optional mode override such as `review` or `bounded_autonomy` for simulation.")
    permissions_check.add_argument("--actor-type", default="operator", help="Actor type for the decision log.")
    permissions_check.add_argument("--actor-name", default=None, help="Optional actor name for the decision log.")
    permissions_check.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    permissions_decide = permissions_sub.add_parser(
        "decide",
        help="Resolve a pending approval request by explicitly approving or denying it.",
    )
    permissions_decide.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    permissions_decide.add_argument("--request-id", required=True, help="Pending approval request id from `permission_decision_log.jsonl`.")
    permissions_decide.add_argument("--decision", required=True, choices=["approve", "deny"], help="Explicit approval outcome.")
    permissions_decide.add_argument("--config", default=None, help="Optional config/policy source.")
    permissions_decide.add_argument("--actor-type", default="operator", help="Actor type for the decision log.")
    permissions_decide.add_argument("--actor-name", default=None, help="Optional actor name for the decision log.")
    permissions_decide.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    mission_control = sub.add_parser(
        "mission-control",
        help="Launch or inspect the local control center, onboarding surface, and terminal mission-control chat.",
    )
    mission_control_sub = mission_control.add_subparsers(dest="mission_control_command", required=True)

    mission_control_show = mission_control_sub.add_parser(
        "show",
        help="Materialize and render the current mission-control state as CLI/MCP-friendly output.",
    )
    mission_control_show.add_argument("--run-dir", default=None, help="Optional run directory to render inside mission control.")
    mission_control_show.add_argument("--output-dir", default=None, help="Optional state directory for onboarding-only mission control output.")
    mission_control_show.add_argument("--config", default=None, help="Optional config/policy source.")
    mission_control_show.add_argument(
        "--expected-profile",
        choices=["core", "full"],
        default="full",
        help="Doctor profile mission control should reflect.",
    )
    mission_control_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    mission_control_launch = mission_control_sub.add_parser(
        "launch",
        help="Write the local mission-control HTML report, optionally open it in the browser, and optionally continue in terminal chat.",
    )
    mission_control_launch.add_argument("--run-dir", default=None, help="Optional run directory to render inside mission control.")
    mission_control_launch.add_argument("--output-dir", default=None, help="Optional state directory for onboarding-only mission control output.")
    mission_control_launch.add_argument("--config", default=None, help="Optional config/policy source.")
    mission_control_launch.add_argument(
        "--expected-profile",
        choices=["core", "full"],
        default="full",
        help="Doctor profile mission control should reflect.",
    )
    mission_control_launch.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the generated static mission-control report in the default browser.",
    )
    mission_control_launch.add_argument(
        "--interactive",
        action="store_true",
        help="After launch, continue in terminal mission-control chat so questions work immediately.",
    )
    mission_control_launch.add_argument(
        "--show-json",
        action="store_true",
        help="When using --interactive, print structured payloads after each terminal answer.",
    )
    mission_control_launch.add_argument(
        "--max-turns",
        type=int,
        default=0,
        help="Optional positive turn cap for --interactive. 0 means unlimited until /exit.",
    )
    mission_control_launch.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    mission_control_chat = mission_control_sub.add_parser(
        "chat",
        help="Run an interactive mission-control terminal chat for onboarding or an existing run.",
    )
    mission_control_chat.add_argument("--run-dir", default=None, help="Optional run directory to chat against.")
    mission_control_chat.add_argument("--output-dir", default=None, help="Optional state directory for onboarding-only mission control output.")
    mission_control_chat.add_argument("--config", default=None, help="Optional config/policy source.")
    mission_control_chat.add_argument(
        "--expected-profile",
        choices=["core", "full"],
        default="full",
        help="Doctor profile mission control should reflect.",
    )
    mission_control_chat.add_argument("--data-path", default=None, help="Optional dataset override for rerun/takeover flows when a run exists.")
    mission_control_chat.add_argument("--show-json", action="store_true", help="Print structured payloads after each turn.")
    mission_control_chat.add_argument("--max-turns", type=int, default=0, help="Optional positive turn cap. 0 means unlimited until /exit.")

    handoff_surface = sub.add_parser(
        "handoff",
        help="Inspect differentiated post-run reports or set the explicit next-run focus for humans and agents.",
    )
    handoff_sub = handoff_surface.add_subparsers(dest="handoff_command", required=True)

    handoff_show = handoff_sub.add_parser(
        "show",
        help="Render the current differentiated post-run handoff for a run.",
    )
    handoff_show.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    handoff_show.add_argument(
        "--audience",
        choices=["user", "agent", "both"],
        default="both",
        help="Which report audience to render.",
    )
    handoff_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    handoff_focus = handoff_sub.add_parser(
        "focus",
        help="Persist the explicit next-run focus for a completed run.",
    )
    handoff_focus.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    handoff_focus.add_argument(
        "--selection",
        choices=["same_data", "add_data", "new_dataset"],
        required=True,
        help="How the next run should relate to the current one.",
    )
    handoff_focus.add_argument("--notes", default=None, help="Optional notes for the next run.")
    handoff_focus.add_argument("--source", default="cli", help="Source label for this focus selection.")
    handoff_focus.add_argument("--actor-type", default="user", help="Actor type creating the focus selection.")
    handoff_focus.add_argument("--actor-name", default=None, help="Optional actor name.")
    handoff_focus.add_argument(
        "--reset-learnings",
        action="store_true",
        help="Reset durable learnings now so the next run starts from a fresh memory state.",
    )
    handoff_focus.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    learnings_surface = sub.add_parser(
        "learnings",
        help="Inspect or reset Relaytic's durable cross-run learnings memory.",
    )
    learnings_sub = learnings_surface.add_subparsers(dest="learnings_command", required=True)

    learnings_show = learnings_sub.add_parser(
        "show",
        help="Render the durable learnings state and any current run snapshot.",
    )
    learnings_show.add_argument("--run-dir", default=None, help="Optional run directory for the current run snapshot.")
    learnings_show.add_argument("--state-dir", default=None, help="Optional explicit learnings state directory.")
    learnings_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    learnings_reset = learnings_sub.add_parser(
        "reset",
        help="Reset durable learnings for this workspace or explicit state directory.",
    )
    learnings_reset.add_argument("--run-dir", default=None, help="Optional run directory whose workspace learnings should be reset.")
    learnings_reset.add_argument("--state-dir", default=None, help="Optional explicit learnings state directory.")
    learnings_reset.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    workspace_surface = sub.add_parser(
        "workspace",
        help="Inspect or continue the explicit Relaytic multi-run workspace continuity layer.",
    )
    workspace_sub = workspace_surface.add_subparsers(dest="workspace_command", required=True)

    workspace_show = workspace_sub.add_parser(
        "show",
        help="Render the current workspace state, result contract, and next-run plan for a run.",
    )
    workspace_show.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    workspace_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    workspace_continue = workspace_sub.add_parser(
        "continue",
        help="Persist the current workspace continuation direction without starting a fresh run yet.",
    )
    workspace_continue.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    workspace_continue.add_argument(
        "--direction",
        choices=["same_data", "add_data", "new_dataset"],
        required=True,
        help="How the next run should relate to the current workspace.",
    )
    workspace_continue.add_argument("--notes", default=None, help="Optional notes for the next run.")
    workspace_continue.add_argument("--source", default="cli", help="Source label for this continuation choice.")
    workspace_continue.add_argument("--actor-type", default="user", help="Actor type creating the continuation choice.")
    workspace_continue.add_argument("--actor-name", default=None, help="Optional actor name.")
    workspace_continue.add_argument(
        "--reset-learnings",
        action="store_true",
        help="Reset durable learnings now so the next run starts from a fresh workspace memory state.",
    )
    workspace_continue.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    search_surface = sub.add_parser(
        "search",
        help="Run or inspect Slice 13 search-controller artifacts.",
    )
    search_sub = search_surface.add_subparsers(dest="search_command", required=True)

    search_review = search_sub.add_parser(
        "review",
        help="Execute the Slice 13 search-controller review for an existing run.",
    )
    search_review.add_argument("--run-dir", required=True, help="Run directory for search-controller artifacts.")
    search_review.add_argument("--config", default=None, help="Optional config/policy source.")
    search_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    search_review.add_argument("--overwrite", action="store_true", help="Allow overwriting existing search-controller artifacts.")
    search_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    search_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    search_show = search_sub.add_parser(
        "show",
        help="Render the current Slice 13 search-controller review for a run.",
    )
    search_show.add_argument("--run-dir", required=True, help="Run directory containing search-controller artifacts.")
    search_show.add_argument("--config", default=None, help="Optional config/policy source if artifacts must be materialized.")
    search_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    daemon_surface = sub.add_parser(
        "daemon",
        help="Run or inspect Slice 13C bounded background jobs and resume artifacts.",
    )
    daemon_sub = daemon_surface.add_subparsers(dest="daemon_command", required=True)

    daemon_review = daemon_sub.add_parser(
        "review",
        help="Materialize the Slice 13C daemon state for an existing run.",
    )
    daemon_review.add_argument("--run-dir", required=True, help="Run directory for daemon artifacts.")
    daemon_review.add_argument("--config", default=None, help="Optional config/policy source.")
    daemon_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    daemon_show = daemon_sub.add_parser(
        "show",
        help="Render the current Slice 13C daemon state for a run.",
    )
    daemon_show.add_argument("--run-dir", required=True, help="Run directory containing daemon artifacts.")
    daemon_show.add_argument("--config", default=None, help="Optional config/policy source if artifacts must be materialized.")
    daemon_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    daemon_run_job = daemon_sub.add_parser(
        "run-job",
        help="Start one bounded background job, requesting approval first when policy requires it.",
    )
    daemon_run_job.add_argument("--run-dir", required=True, help="Run directory containing daemon artifacts.")
    daemon_run_job.add_argument("--job-id", required=True, help="Background job id such as `job_search_campaign`.")
    daemon_run_job.add_argument("--config", default=None, help="Optional config/policy source.")
    daemon_run_job.add_argument("--actor-type", default="operator", help="Actor type for the daemon job request.")
    daemon_run_job.add_argument("--actor-name", default=None, help="Optional actor name for the daemon job request.")
    daemon_run_job.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    daemon_resume_job = daemon_sub.add_parser(
        "resume-job",
        help="Resume one paused or stale background job from its explicit checkpoint.",
    )
    daemon_resume_job.add_argument("--run-dir", required=True, help="Run directory containing daemon artifacts.")
    daemon_resume_job.add_argument("--job-id", required=True, help="Background job id such as `job_search_campaign`.")
    daemon_resume_job.add_argument("--config", default=None, help="Optional config/policy source.")
    daemon_resume_job.add_argument("--actor-type", default="operator", help="Actor type for the daemon job resume.")
    daemon_resume_job.add_argument("--actor-name", default=None, help="Optional actor name for the daemon job resume.")
    daemon_resume_job.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    remote_surface = sub.add_parser(
        "remote",
        help="Inspect or act through Slice 14A remote supervision, approval, and handoff surfaces.",
    )
    remote_sub = remote_surface.add_subparsers(dest="remote_command", required=True)

    remote_show = remote_sub.add_parser(
        "show",
        help="Render the current Slice 14A remote supervision state for a run.",
    )
    remote_show.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    remote_show.add_argument("--config", default=None, help="Optional config/policy source if artifacts must be materialized.")
    remote_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    remote_decide = remote_sub.add_parser(
        "decide",
        help="Approve or deny one pending request through the Slice 14A remote supervision surface.",
    )
    remote_decide.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    remote_decide.add_argument("--request-id", required=True, help="Pending approval request id.")
    remote_decide.add_argument("--decision", choices=["approve", "deny"], required=True, help="Remote decision to record.")
    remote_decide.add_argument("--config", default=None, help="Optional config/policy source.")
    remote_decide.add_argument("--actor-type", default="operator", help="Actor type taking the remote decision.")
    remote_decide.add_argument("--actor-name", default=None, help="Optional actor name taking the remote decision.")
    remote_decide.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    remote_handoff = remote_sub.add_parser(
        "handoff",
        help="Transfer remote supervision between a human and an external agent without creating a second authority path.",
    )
    remote_handoff.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    remote_handoff.add_argument("--to-actor-type", choices=["user", "operator", "agent"], required=True, help="Who should become the current remote supervisor.")
    remote_handoff.add_argument("--to-actor-name", default=None, help="Optional display name for the new supervisor.")
    remote_handoff.add_argument("--from-actor-type", choices=["user", "operator", "agent"], default="operator", help="Who is handing off supervision.")
    remote_handoff.add_argument("--from-actor-name", default=None, help="Optional display name for the previous supervisor.")
    remote_handoff.add_argument("--reason", default=None, help="Optional handoff rationale.")
    remote_handoff.add_argument("--config", default=None, help="Optional config/policy source.")
    remote_handoff.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    plan = sub.add_parser(
        "plan",
        help="Create Slice 05 planning artifacts and execute the first deterministic route.",
    )
    plan_sub = plan.add_subparsers(dest="plan_command", required=True)

    plan_create = plan_sub.add_parser(
        "create",
        help="Write Slice 05 planning artifacts.",
    )
    plan_create.add_argument("--run-dir", required=True, help="Run directory for planning artifacts.")
    plan_create.add_argument("--data-path", required=True, help="Structured data source path such as CSV, Parquet, JSONL, or Excel.")
    plan_create.add_argument("--config", default=None, help="Optional config/policy source.")
    plan_create.add_argument("--run-id", default=None, help="Optional manifest run id.")
    plan_create.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    plan_create.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    plan_create.add_argument("--data-start-row", type=int, default=None, help="Optional data start row.")
    plan_create.add_argument("--timestamp-column", default=None, help="Optional timestamp column override for investigation.")
    plan_create.add_argument("--overwrite", action="store_true", help="Allow overwriting existing Slice 05 artifacts.")
    plan_create.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")

    plan_run = plan_sub.add_parser(
        "run",
        help="Write Slice 05 planning artifacts and execute the first deterministic Builder route.",
    )
    plan_run.add_argument("--run-dir", required=True, help="Run directory for planning and model artifacts.")
    plan_run.add_argument("--data-path", required=True, help="Structured data source path such as CSV, Parquet, JSONL, or Excel.")
    plan_run.add_argument("--config", default=None, help="Optional config/policy source.")
    plan_run.add_argument("--run-id", default=None, help="Optional manifest run id.")
    plan_run.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    plan_run.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    plan_run.add_argument("--data-start-row", type=int, default=None, help="Optional data start row.")
    plan_run.add_argument("--timestamp-column", default=None, help="Optional timestamp column override for investigation.")
    plan_run.add_argument("--overwrite", action="store_true", help="Allow overwriting existing Slice 05 and model artifacts.")
    plan_run.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")

    plan_show = plan_sub.add_parser(
        "show",
        help="Print Slice 05 planning artifacts from a run directory.",
    )
    plan_show.add_argument("--run-dir", required=True, help="Run directory containing planning artifacts.")

    evidence = sub.add_parser(
        "evidence",
        help="Run or inspect Slice 06 challenger, ablation, audit, and report artifacts.",
    )
    evidence_sub = evidence.add_subparsers(dest="evidence_command", required=True)

    evidence_run = evidence_sub.add_parser(
        "run",
        help="Execute the Slice 06 evidence layer for an existing or freshly planned run.",
    )
    evidence_run.add_argument("--run-dir", required=True, help="Run directory for evidence artifacts.")
    evidence_run.add_argument("--data-path", required=True, help="Structured data source path such as CSV, Parquet, JSONL, or Excel.")
    evidence_run.add_argument("--config", default=None, help="Optional config/policy source.")
    evidence_run.add_argument("--run-id", default=None, help="Optional manifest run id.")
    evidence_run.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    evidence_run.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    evidence_run.add_argument("--data-start-row", type=int, default=None, help="Optional data start row.")
    evidence_run.add_argument("--timestamp-column", default=None, help="Optional timestamp column override for investigation.")
    evidence_run.add_argument("--overwrite", action="store_true", help="Allow overwriting existing evidence artifacts.")
    evidence_run.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    evidence_run.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    evidence_show = evidence_sub.add_parser(
        "show",
        help="Render the current Slice 06 decision memo and evidence summary.",
    )
    evidence_show.add_argument("--run-dir", required=True, help="Run directory containing evidence artifacts.")
    evidence_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    status_surface = sub.add_parser(
        "status",
        help="Render the current Slice 07 completion-governor status for a run.",
    )
    status_surface.add_argument("--run-dir", required=True, help="Run directory containing Relaytic artifacts.")
    status_surface.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    completion = sub.add_parser(
        "completion",
        help="Run or inspect Slice 07 completion-governor artifacts.",
    )
    completion_sub = completion.add_subparsers(dest="completion_command", required=True)

    completion_review = completion_sub.add_parser(
        "review",
        help="Execute Slice 07 completion judgment for an existing run.",
    )
    completion_review.add_argument("--run-dir", required=True, help="Run directory for completion artifacts.")
    completion_review.add_argument("--config", default=None, help="Optional config/policy source.")
    completion_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    completion_review.add_argument("--overwrite", action="store_true", help="Allow overwriting existing completion artifacts.")
    completion_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    completion_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    lifecycle = sub.add_parser(
        "lifecycle",
        help="Run or inspect Slice 08 lifecycle-governor artifacts.",
    )
    lifecycle_sub = lifecycle.add_subparsers(dest="lifecycle_command", required=True)

    lifecycle_review = lifecycle_sub.add_parser(
        "review",
        help="Execute Slice 08 lifecycle review for an existing run.",
    )
    lifecycle_review.add_argument("--run-dir", required=True, help="Run directory for lifecycle artifacts.")
    lifecycle_review.add_argument("--data-path", default=None, help="Optional fresh-data path; defaults to the run dataset when discoverable.")
    lifecycle_review.add_argument("--config", default=None, help="Optional config/policy source.")
    lifecycle_review.add_argument("--run-id", default=None, help="Optional manifest run id.")
    lifecycle_review.add_argument("--overwrite", action="store_true", help="Allow overwriting existing lifecycle artifacts.")
    lifecycle_review.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    lifecycle_review.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    lifecycle_show = lifecycle_sub.add_parser(
        "show",
        help="Render the current Slice 08 lifecycle review for a run.",
    )
    lifecycle_show.add_argument("--run-dir", required=True, help="Run directory containing lifecycle artifacts.")
    lifecycle_show.add_argument("--data-path", default=None, help="Optional fresh-data path if lifecycle artifacts must be materialized.")
    lifecycle_show.add_argument(
        "--format",
        choices=["human", "json", "both"],
        default="human",
        help="CLI output format. Human is default; JSON is stable for agents.",
    )

    investigate = sub.add_parser(
        "investigate",
        help="Run the Slice 03 investigation layer and write specialist artifacts.",
    )
    investigate.add_argument("--run-dir", required=True, help="Run directory for investigation artifacts.")
    investigate.add_argument("--data-path", required=True, help="Structured data source path such as CSV, Parquet, JSONL, Excel, or a local dataset directory.")
    investigate.add_argument("--config", default=None, help="Optional config/policy source.")
    investigate.add_argument("--run-id", default=None, help="Optional manifest run id.")
    investigate.add_argument("--sheet-name", default=None, help="Excel sheet name if needed.")
    investigate.add_argument("--header-row", type=int, default=None, help="Optional header row.")
    investigate.add_argument("--data-start-row", type=int, default=None, help="Optional data start row.")
    investigate.add_argument("--timestamp-column", default=None, help="Optional timestamp column override.")
    investigate.add_argument("--overwrite", action="store_true", help="Allow overwriting existing Slice 03 artifacts.")
    investigate.add_argument("--label", action="append", default=[], help="Optional `key=value` label for the manifest.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan-git-safety":
        payload = _scan_git_safety_passthrough(paths=args.paths)
        findings = list(payload["surface_payload"].get("findings", []))
        if findings:
            print("Potential leak findings:")
            for finding in findings:
                line_number = finding.get("line_number")
                line_suffix = f":{line_number}" if line_number is not None else ""
                print(
                    f"- {finding.get('path', 'unknown')}{line_suffix} "
                    f"[{finding.get('rule_id', 'unknown')}] {finding.get('excerpt') or finding.get('reason', '')}"
                )
            return 1
        print("No leak patterns detected.")
        return 0

    if args.command == "release-safety":
        try:
            if args.release_safety_command == "scan":
                payload = _run_release_safety_scan_surface(
                    target_path=args.target_path,
                    state_dir=args.state_dir,
                )
            elif args.release_safety_command == "show":
                payload = _show_release_safety_surface(state_dir=args.state_dir)
            else:
                parser.error("Unsupported release-safety subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 1 if str(payload["surface_payload"].get("status", "")).strip() == "error" else 0

    if args.command == "doctor":
        payload = build_doctor_report(expected_profile=args.expected_profile)
        _emit_structured_surface_output(
            payload=payload,
            human_text=render_doctor_markdown(payload),
            output_format=args.format,
        )
        return 1 if str(payload.get("status", "")).strip() == "error" else 0

    if args.command == "events":
        try:
            if args.events_command == "show":
                payload = _show_event_bus_surface(run_dir=args.run_dir, config_path=args.config)
            else:
                parser.error("Unsupported events subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "permissions":
        try:
            if args.permissions_command == "show":
                payload = _show_permission_surface(run_dir=args.run_dir, config_path=args.config)
            elif args.permissions_command == "check":
                payload = _check_permission_surface(
                    run_dir=args.run_dir,
                    action_id=args.action,
                    config_path=args.config,
                    mode=args.mode,
                    actor_type=args.actor_type,
                    actor_name=args.actor_name,
                )
            elif args.permissions_command == "decide":
                payload = _decide_permission_surface(
                    run_dir=args.run_dir,
                    request_id=args.request_id,
                    decision=args.decision,
                    config_path=args.config,
                    actor_type=args.actor_type,
                    actor_name=args.actor_name,
                )
            else:
                parser.error("Unsupported permissions subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "mission-control":
        if args.mission_control_command == "show":
            payload = _show_mission_control_surface(
                run_dir=args.run_dir,
                output_dir=args.output_dir,
                config_path=args.config,
                expected_profile=args.expected_profile,
            )
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.mission_control_command == "chat":
            return _run_mission_control_chat(
                run_dir=args.run_dir,
                output_dir=args.output_dir,
                config_path=args.config,
                expected_profile=args.expected_profile,
                data_path=args.data_path,
                show_json=bool(args.show_json),
                max_turns=int(args.max_turns),
            )
        if args.mission_control_command == "launch":
            payload = _launch_mission_control_surface(
                run_dir=args.run_dir,
                output_dir=args.output_dir,
                config_path=args.config,
                expected_profile=args.expected_profile,
                open_browser=not args.no_browser,
            )
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            if bool(args.interactive):
                return _run_mission_control_chat(
                    run_dir=args.run_dir,
                    output_dir=args.output_dir,
                    config_path=args.config,
                    expected_profile=args.expected_profile,
                    data_path=None,
                    show_json=bool(args.show_json),
                    max_turns=int(args.max_turns),
                )
            return 0

    if args.command == "handoff":
        try:
            if args.handoff_command == "show":
                payload = _show_handoff_surface(
                    run_dir=args.run_dir,
                    audience=args.audience,
                )
            elif args.handoff_command == "focus":
                payload = _set_next_run_focus_surface(
                    run_dir=args.run_dir,
                    selection_id=args.selection,
                    notes=args.notes,
                    source=args.source,
                    actor_type=args.actor_type,
                    actor_name=args.actor_name,
                    reset_requested=bool(args.reset_learnings),
                )
            else:
                parser.error("Unsupported handoff subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "learnings":
        try:
            if args.learnings_command == "show":
                payload = _show_learnings_surface(
                    run_dir=args.run_dir,
                    state_dir=args.state_dir,
                )
            elif args.learnings_command == "reset":
                payload = _reset_learnings_surface(
                    run_dir=args.run_dir,
                    state_dir=args.state_dir,
                )
            else:
                parser.error("Unsupported learnings subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "workspace":
        try:
            if args.workspace_command == "show":
                payload = _show_workspace_surface(run_dir=args.run_dir)
            elif args.workspace_command == "continue":
                payload = _continue_workspace_surface(
                    run_dir=args.run_dir,
                    direction=args.direction,
                    notes=args.notes,
                    source=args.source,
                    actor_type=args.actor_type,
                    actor_name=args.actor_name,
                    reset_requested=bool(args.reset_learnings),
                )
            else:
                parser.error("Unsupported workspace subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "remote":
        try:
            if args.remote_command == "show":
                payload = _show_remote_control_surface(
                    run_dir=args.run_dir,
                    config_path=args.config,
                )
            elif args.remote_command == "decide":
                payload = _decide_remote_approval_surface(
                    run_dir=args.run_dir,
                    request_id=args.request_id,
                    decision=args.decision,
                    config_path=args.config,
                    actor_type=args.actor_type,
                    actor_name=args.actor_name,
                )
            elif args.remote_command == "handoff":
                payload = _handoff_remote_supervision_surface(
                    run_dir=args.run_dir,
                    to_actor_type=args.to_actor_type,
                    to_actor_name=args.to_actor_name,
                    from_actor_type=args.from_actor_type,
                    from_actor_name=args.from_actor_name,
                    reason=args.reason,
                    config_path=args.config,
                )
            else:
                parser.error("Unsupported remote subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "search":
        try:
            if args.search_command == "review":
                    payload = _run_search_phase(
                        run_dir=args.run_dir,
                        config_path=args.config,
                        run_id=args.run_id,
                        overwrite=args.overwrite,
                        labels=_parse_key_value_pairs(args.label),
                    )
            elif args.search_command == "show":
                payload = _show_search_surface(
                    run_dir=args.run_dir,
                    config_path=args.config,
                )
            else:
                parser.error("Unsupported search subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "daemon":
        try:
            if args.daemon_command == "review":
                payload = _run_daemon_phase(
                    run_dir=args.run_dir,
                    config_path=args.config,
                )
            elif args.daemon_command == "show":
                payload = _show_daemon_surface(
                    run_dir=args.run_dir,
                    config_path=args.config,
                )
            elif args.daemon_command == "run-job":
                payload = _run_background_job_surface(
                    run_dir=args.run_dir,
                    job_id=args.job_id,
                    config_path=args.config,
                    actor_type=args.actor_type,
                    actor_name=args.actor_name,
                )
            elif args.daemon_command == "resume-job":
                payload = _resume_background_job_surface(
                    run_dir=args.run_dir,
                    job_id=args.job_id,
                    config_path=args.config,
                    actor_type=args.actor_type,
                    actor_name=args.actor_name,
                )
            else:
                parser.error("Unsupported daemon subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "integrations":
        if args.integrations_command == "show":
            payload = {
                "status": "ok",
                **build_integration_inventory(),
            }
            _emit_structured_surface_output(
                payload=payload,
                human_text=render_integration_inventory_markdown(payload["integrations"]),
                output_format=args.format,
            )
            return 0
        if args.integrations_command == "self-check":
            payload = {
                "status": "ok",
                **build_integration_self_check_report(),
            }
            _emit_structured_surface_output(
                payload=payload,
                human_text=render_integration_self_check_markdown(payload),
                output_format=args.format,
            )
            return 0
        else:
            parser.error("Unsupported integrations subcommand.")
            return 2

    if args.command == "interoperability":
        if args.interoperability_command == "show":
            payload = build_interoperability_inventory()
            _emit_structured_surface_output(
                payload=payload,
                human_text=render_interoperability_inventory_markdown(payload),
                output_format=args.format,
            )
            return 0
        if args.interoperability_command == "self-check":
            payload = build_interoperability_self_check_report(live=args.live)
            _emit_structured_surface_output(
                payload=payload,
                human_text=render_interoperability_self_check_markdown(payload),
                output_format=args.format,
            )
            return 1 if str(payload.get("status", "")).strip() == "error" else 0
        if args.interoperability_command == "export":
            try:
                payload = export_host_bundles(
                    output_dir=args.output_dir,
                    host=args.host,
                    force=args.force,
                    mcp_command=args.mcp_command,
                    public_mcp_url=args.public_mcp_url,
                )
            except Exception as exc:
                print(dumps_json({"status": "error", "message": str(exc)}, indent=2, ensure_ascii=False))
                return 1
            human_lines = [
                "# Relaytic Host Bundle Export",
                "",
                f"- Status: `{payload.get('status', 'unknown')}`",
                f"- Output directory: `{payload.get('output_dir', 'unknown')}`",
                f"- Manifest: `{payload.get('manifest_path', 'unknown')}`",
            ]
            for host in payload.get("hosts", []):
                human_lines.append(f"- Host `{host.get('host')}` -> `{', '.join(host.get('files', []))}`")
            _emit_structured_surface_output(
                payload=payload,
                human_text="\n".join(human_lines) + "\n",
                output_format=args.format,
            )
            return 0
        if args.interoperability_command == "serve-mcp":
            try:
                serve_relaytic_mcp(
                    transport=args.transport,
                    host=args.host,
                    port=args.port,
                    mount_path=args.mount_path,
                )
            except Exception as exc:
                print(dumps_json({"status": "error", "message": str(exc)}, indent=2, ensure_ascii=False))
                return 1
            return 0
        parser.error("Unsupported interoperability subcommand.")
        return 2

    if args.command == "manifest":
        if args.manifest_command != "init":
            parser.error("Unsupported manifest subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        entries = [
            artifact_entry(item, run_dir=args.run_dir, kind="artifact")
            for item in args.entry
        ]
        path = write_manifest(
            run_dir=args.run_dir,
            run_id=args.run_id,
            policy_source=args.policy_source,
            labels=labels,
            entries=entries,
        )
        print(
            dumps_json(
                {
                    "status": "ok",
                    "manifest_path": str(path),
                    "run_dir": str(Path(args.run_dir)),
                    "entry_count": len(entries) + 1,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "policy":
        if args.policy_command != "resolve":
            parser.error("Unsupported policy subcommand.")
            return 2
        resolved = load_policy(args.config)
        output_path = write_resolved_policy(args.output, path=args.config)
        print(
            dumps_json(
                {
                    "status": "ok",
                    "output_path": str(output_path),
                    "source_path": resolved.source_path,
                    "schema_version": resolved.schema_version,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "mandate":
        if args.mandate_command == "init":
            try:
                payload = _init_mandate_foundation(args)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            print(dumps_json(payload, indent=2, ensure_ascii=False))
            return 0
        if args.mandate_command == "show":
            print(dumps_json(_read_json_bundle(args.run_dir, bundle="mandate"), indent=2, ensure_ascii=False))
            return 0
        parser.error("Unsupported mandate subcommand.")
        return 2

    if args.command == "context":
        if args.context_command == "init":
            try:
                payload = _init_context_foundation(args)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            print(dumps_json(payload, indent=2, ensure_ascii=False))
            return 0
        if args.context_command == "show":
            print(dumps_json(_read_json_bundle(args.run_dir, bundle="context"), indent=2, ensure_ascii=False))
            return 0
        parser.error("Unsupported context subcommand.")
        return 2

    if args.command == "foundation":
        if args.foundation_command != "init":
            parser.error("Unsupported foundation subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _init_run_foundation(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        print(dumps_json(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "run":
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_access_flow(
                run_dir=args.run_dir,
                data_path=args.data_path,
                source_type=args.source_type,
                source_table=args.source_table,
                sql_query=args.sql_query,
                stream_window_rows=args.stream_window_rows,
                stream_format=args.stream_format,
                materialized_format=args.materialized_format,
                config_path=args.config,
                run_id=args.run_id,
                text=args.text,
                text_file=args.text_file,
                actor_type=args.actor_type,
                actor_name=args.actor_name,
                channel=args.channel,
                sheet_name=args.sheet_name,
                header_row=args.header_row,
                data_start_row=args.data_start_row,
                timestamp_column=args.timestamp_column,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "show":
        try:
            payload = _show_access_run(run_dir=args.run_dir)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "predict":
        try:
            prediction = run_inference_from_artifacts(
                data_path=args.data_path,
                run_dir=args.run_dir,
                source_type=args.source_type,
                source_table=args.source_table,
                sql_query=args.sql_query,
                stream_window_rows=args.stream_window_rows,
                stream_format=args.stream_format,
                materialized_format=args.materialized_format,
                sheet_name=args.sheet_name,
                header_row=args.header_row,
                data_start_row=args.data_start_row,
                delimiter=args.delimiter,
                decision_threshold=args.decision_threshold,
                output_path=args.output_path,
            )
        except Exception as exc:
            print(dumps_json({"status": "error", "message": str(exc)}, indent=2, ensure_ascii=False))
            return 1
        _emit_structured_surface_output(
            payload=prediction,
            human_text=_render_prediction_output(prediction),
            output_format=args.format,
        )
        return 0

    if args.command == "source":
        try:
            if args.source_command == "inspect":
                payload = _run_source_inspection(
                    source_path=args.source_path,
                    source_type=args.source_type,
                    source_table=args.source_table,
                    sql_query=args.sql_query,
                    stream_window_rows=args.stream_window_rows,
                    stream_format=args.stream_format,
                    materialized_format=args.materialized_format,
                )
            elif args.source_command == "materialize":
                payload = _materialize_source_surface(
                    source_path=args.source_path,
                    run_dir=args.run_dir,
                    source_type=args.source_type,
                    source_table=args.source_table,
                    sql_query=args.sql_query,
                    stream_window_rows=args.stream_window_rows,
                    stream_format=args.stream_format,
                    materialized_format=args.materialized_format,
                    purpose=args.purpose,
                    alias=args.alias,
                )
            else:
                parser.error("Unsupported source subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "intake":
        if args.intake_command == "show":
            print(dumps_json(_read_json_bundle(args.run_dir, bundle="intake"), indent=2, ensure_ascii=False))
            return 0
        if args.intake_command == "questions":
            bundle = _read_json_bundle(args.run_dir, bundle="intake")
            print(
                dumps_json(
                    {
                        "autonomy_mode": bundle.get("autonomy_mode", {}),
                        "clarification_queue": bundle.get("clarification_queue", {}),
                        "assumption_log": bundle.get("assumption_log", {}),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 0
        if args.intake_command != "interpret":
            parser.error("Unsupported intake subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            intake_text = _resolve_intake_text(text=args.text, text_file=args.text_file)
            payload = _run_intake_phase(
                run_dir=args.run_dir,
                message=intake_text,
                actor_type=args.actor_type,
                actor_name=args.actor_name,
                channel=args.channel,
                config_path=args.config,
                run_id=args.run_id,
                data_path=args.data_path,
                sheet_name=args.sheet_name,
                header_row=args.header_row,
                data_start_row=args.data_start_row,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        print(dumps_json(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "memory":
        if args.memory_command == "show":
            bundle = _read_json_bundle(args.run_dir, bundle="memory")
            retrieval = dict(bundle.get("memory_retrieval", {}))
            route_prior = dict(bundle.get("route_prior_context", {}))
            challenger_prior = dict(bundle.get("challenger_prior_suggestions", {}))
            _emit_structured_surface_output(
                payload={
                    "status": "ok",
                    "run_dir": str(Path(args.run_dir)),
                    "memory": {
                        "status": retrieval.get("status"),
                        "analog_count": retrieval.get("selected_analog_count", 0),
                        "route_prior_applied": route_prior.get("status") == "memory_influenced",
                        "preferred_challenger_family": challenger_prior.get("preferred_challenger_family"),
                    },
                    "bundle": bundle,
                },
                human_text=render_memory_review_markdown(bundle),
                output_format=args.format,
            )
            return 0
        if args.memory_command != "retrieve":
            parser.error("Unsupported memory subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_memory_phase(
                run_dir=args.run_dir,
                data_path=args.data_path,
                config_path=args.config,
                run_id=args.run_id,
                labels=labels,
                search_roots=args.search_root,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "feedback":
        if args.feedback_command == "show":
            try:
                payload = _show_feedback_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.feedback_command == "add":
            try:
                labels = _parse_key_value_pairs(args.label)
                entries = _load_feedback_entries_from_args(args)
                foundation_state = _ensure_run_foundation_present(
                    run_dir=args.run_dir,
                    config_path=args.config,
                    run_id=args.run_id,
                    labels=labels,
                )
                intake_payload = append_feedback_entries(
                    args.run_dir,
                    entries=entries,
                    policy=foundation_state["resolved"].policy,
                )
                payload = _run_feedback_phase(
                    run_dir=args.run_dir,
                    config_path=args.config,
                    run_id=args.run_id,
                    labels=labels,
                )
                payload["surface_payload"]["feedback"]["added_count"] = len(entries)
                payload["surface_payload"]["feedback"]["total_recorded_count"] = len(intake_payload.get("entries", []))
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.feedback_command == "rollback":
            try:
                labels = _parse_key_value_pairs(args.label)
                foundation_state = _ensure_run_foundation_present(
                    run_dir=args.run_dir,
                    config_path=args.config,
                    run_id=args.run_id,
                    labels=labels,
                )
                rollback_feedback_entry(
                    args.run_dir,
                    feedback_id=args.feedback_id,
                    policy=foundation_state["resolved"].policy,
                )
                payload = _run_feedback_phase(
                    run_dir=args.run_dir,
                    config_path=args.config,
                    run_id=args.run_id,
                    labels=labels,
                )
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.feedback_command != "review":
            parser.error("Unsupported feedback subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_feedback_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "profiles":
        if args.profiles_command == "show":
            try:
                payload = _show_profiles_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.profiles_command != "review":
            parser.error("Unsupported profiles subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_profiles_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "decision":
        if args.decision_command == "show":
            try:
                payload = _show_decision_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.decision_command != "review":
            parser.error("Unsupported decision subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_decision_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "dojo":
        if args.dojo_command == "show":
            try:
                payload = _show_dojo_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.dojo_command == "rollback":
            try:
                labels = _parse_key_value_pairs(args.label)
                payload = _run_dojo_rollback(
                    run_dir=args.run_dir,
                    proposal_id=args.proposal_id,
                    reason=args.reason,
                    config_path=args.config,
                    run_id=args.run_id,
                    labels=labels,
                )
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.dojo_command != "review":
            parser.error("Unsupported dojo subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_dojo_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "pulse":
        if args.pulse_command == "show":
            try:
                payload = _show_pulse_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.pulse_command != "review":
            parser.error("Unsupported pulse subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_pulse_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "trace":
        try:
            if args.trace_command == "show":
                payload = _show_trace_surface(run_dir=args.run_dir, config_path=args.config)
            elif args.trace_command == "replay":
                payload = _replay_trace_surface(run_dir=args.run_dir, config_path=args.config)
            else:
                parser.error("Unsupported trace subcommand.")
                return 2
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "evals":
        if args.evals_command == "show":
            try:
                payload = _show_evals_surface(run_dir=args.run_dir, config_path=args.config)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.evals_command != "run":
            parser.error("Unsupported evals subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_evals_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "control":
        if args.control_command == "show":
            try:
                payload = _show_control_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.control_command != "review":
            parser.error("Unsupported control subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            assist_payload = _materialize_assist_surface(
                run_dir=args.run_dir,
                config_path=args.config,
                last_user_intent=None,
                last_requested_stage=None,
                last_action_kind=None,
                increment_turn_count=False,
            )
            plan = plan_assist_turn(
                message=args.message,
                run_summary=dict(assist_payload["run_summary"]),
                assist_bundle=dict(assist_payload["bundle"]),
            )
            payload = _run_control_phase(
                run_dir=args.run_dir,
                message=args.message,
                action_kind=plan.action_kind,
                requested_stage=plan.requested_stage,
                config_path=args.config,
                run_id=args.run_id,
                labels=labels,
                actor_type=args.actor_type,
                actor_name=args.actor_name,
                runtime_surface="cli",
                runtime_command="relaytic control review",
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "runtime":
        if args.runtime_command == "show":
            try:
                payload = _show_runtime_surface(run_dir=args.run_dir, limit=max(1, int(args.limit)))
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.runtime_command == "events":
            try:
                payload = _show_runtime_events(run_dir=args.run_dir, limit=max(1, int(args.limit)))
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.runtime_command == "reuse":
            try:
                payload = _show_runtime_reuse_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        parser.error("Unsupported runtime subcommand.")
        return 2

    if args.command == "intelligence":
        if args.intelligence_command == "show":
            try:
                payload = _show_intelligence_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.intelligence_command != "run":
            parser.error("Unsupported intelligence subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_intelligence_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "research":
        if args.research_command == "show":
            try:
                payload = _show_research_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.research_command == "sources":
            try:
                bundle = _read_json_bundle(args.run_dir, bundle="research")
                inventory = dict(bundle.get("research_source_inventory", {}))
                payload = {
                    "surface_payload": {
                        "status": "ok",
                        "run_dir": str(Path(args.run_dir)),
                        "source_count": len(inventory.get("sources", [])),
                        "sources": list(inventory.get("sources", [])),
                    },
                    "human_output": _render_research_sources_markdown(inventory),
                }
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.research_command != "gather":
            parser.error("Unsupported research subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_research_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "autonomy":
        if args.autonomy_command == "show":
            try:
                payload = _show_autonomy_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.autonomy_command != "run":
            parser.error("Unsupported autonomy subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_autonomy_phase(
                run_dir=args.run_dir,
                data_path=args.data_path,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "benchmark":
        if args.benchmark_command == "show":
            try:
                payload = _show_benchmark_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.benchmark_command != "run":
            parser.error("Unsupported benchmark subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_benchmark_phase(
                run_dir=args.run_dir,
                data_path=args.data_path,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
                incumbent_path=args.incumbent_path,
                incumbent_kind=args.incumbent_kind,
                incumbent_name=args.incumbent_name,
                trust_model_deserialization=bool(args.trust_incumbent_model),
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "assist":
        if args.assist_command == "show":
            try:
                payload = _show_assist_surface(run_dir=args.run_dir, config_path=args.config)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.assist_command == "turn":
            try:
                payload = _run_assist_turn(
                    run_dir=args.run_dir,
                    message=args.message,
                    config_path=args.config,
                    data_path=args.data_path,
                )
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.assist_command == "chat":
            return _run_assist_chat(
                run_dir=args.run_dir,
                config_path=args.config,
                data_path=args.data_path,
                show_json=bool(args.show_json),
                max_turns=int(args.max_turns),
            )
        parser.error("Unsupported assist subcommand.")
        return 2

    if args.command == "plan":
        if args.plan_command == "show":
            print(dumps_json(_read_json_bundle(args.run_dir, bundle="planning"), indent=2, ensure_ascii=False))
            return 0
        if args.plan_command not in {"create", "run"}:
            parser.error("Unsupported plan subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_planning_phase(
                run_dir=args.run_dir,
                data_path=args.data_path,
                config_path=args.config,
                run_id=args.run_id,
                sheet_name=args.sheet_name,
                header_row=args.header_row,
                data_start_row=args.data_start_row,
                timestamp_column=args.timestamp_column,
                overwrite=bool(args.overwrite),
                labels=labels,
                execute_route=args.plan_command == "run",
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        print(dumps_json(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "evidence":
        if args.evidence_command == "show":
            try:
                payload = _show_evidence_surface(run_dir=args.run_dir)
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.evidence_command != "run":
            parser.error("Unsupported evidence subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_evidence_phase(
                run_dir=args.run_dir,
                data_path=args.data_path,
                config_path=args.config,
                run_id=args.run_id,
                sheet_name=args.sheet_name,
                header_row=args.header_row,
                data_start_row=args.data_start_row,
                timestamp_column=args.timestamp_column,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "status":
        try:
            payload = _show_completion_status(run_dir=args.run_dir)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "completion":
        if args.completion_command != "review":
            parser.error("Unsupported completion subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_completion_phase(
                run_dir=args.run_dir,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "lifecycle":
        if args.lifecycle_command == "show":
            try:
                payload = _show_lifecycle_surface(
                    run_dir=args.run_dir,
                    data_path=args.data_path,
                )
            except ValueError as exc:
                parser.error(str(exc))
                return 2
            _emit_structured_surface_output(
                payload=payload["surface_payload"],
                human_text=payload["human_output"],
                output_format=args.format,
            )
            return 0
        if args.lifecycle_command != "review":
            parser.error("Unsupported lifecycle subcommand.")
            return 2
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_lifecycle_phase(
                run_dir=args.run_dir,
                data_path=args.data_path,
                config_path=args.config,
                run_id=args.run_id,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        _emit_structured_surface_output(
            payload=payload["surface_payload"],
            human_text=payload["human_output"],
            output_format=args.format,
        )
        return 0

    if args.command == "investigate":
        try:
            labels = _parse_key_value_pairs(args.label)
            payload = _run_investigation_phase(
                run_dir=args.run_dir,
                data_path=args.data_path,
                config_path=args.config,
                run_id=args.run_id,
                sheet_name=args.sheet_name,
                header_row=args.header_row,
                data_start_row=args.data_start_row,
                timestamp_column=args.timestamp_column,
                overwrite=bool(args.overwrite),
                labels=labels,
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        print(dumps_json(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "run-agent-once":
        try:
            context = _parse_context(args.context_json)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        try:
            result = _invoke_agent_once_with_recovery(
                agent=args.agent,
                user_message=args.message,
                context=context,
                config_path=args.config,
            )
        except Exception as exc:
            message = _runtime_error_fallback_message(
                agent=args.agent,
                user_message=args.message,
                error=exc,
            )
            print(dumps_json({"status": "error", "message": message}, indent=2))
            return 1
        print(dumps_json(result, indent=2))
        return 0

    if args.command == "run-agent-session":
        try:
            context = _parse_context(args.context_json)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        return _run_agent_session(
            agent=args.agent,
            base_context=context,
            config_path=args.config,
            show_json=bool(args.show_json),
            max_turns=int(args.max_turns),
        )

    if args.command == "setup-local-llm":
        try:
            result = setup_local_llm(
                config_path=args.config,
                provider=args.provider,
                profile_name=args.profile,
                model=args.model,
                endpoint=args.endpoint,
                install_provider=bool(args.install_provider),
                start_runtime=not bool(args.no_start_runtime),
                pull_model=not bool(args.no_pull_model),
                download_model=not bool(args.no_download_model),
                llama_model_path=args.llama_model_path,
                llama_model_url=args.llama_model_url,
                timeout_seconds=int(args.timeout_seconds),
            )
        except Exception as exc:
            print(dumps_json({"ready": False, "error": str(exc)}, indent=2))
            return 1
        print(dumps_json(result, indent=2))
        return 0

    if args.command == "run-agent1-analysis":
        try:
            predictor_map = _parse_json_object(args.predictor_map_json, arg_name="--predictor-map-json")
            forced_requests = _parse_json_array(
                args.forced_requests_json, arg_name="--forced-requests-json"
            )
            user_hypotheses = _parse_json_array(
                args.user_hypotheses_json, arg_name="--user-hypotheses-json"
            )
            feature_hypotheses = _parse_json_array(
                args.feature_hypotheses_json, arg_name="--feature-hypotheses-json"
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        registry = build_default_registry()
        tool_args: dict[str, Any] = {
            "data_path": args.data_path,
            "predictor_signals_by_target": predictor_map,
            "forced_requests": forced_requests,
            "user_hypotheses": user_hypotheses,
            "feature_hypotheses": feature_hypotheses,
            "max_lag": int(args.max_lag),
            "include_feature_engineering": not args.no_feature_engineering,
            "feature_gain_threshold": float(args.feature_gain_threshold),
            "confidence_top_k": int(args.confidence_top_k),
            "bootstrap_rounds": int(args.bootstrap_rounds),
            "stability_windows": int(args.stability_windows),
            "max_samples": args.max_samples,
            "sample_selection": args.sample_selection,
            "missing_data_strategy": args.missing_data_strategy,
            "fill_constant_value": args.fill_constant_value,
            "row_coverage_strategy": args.row_coverage_strategy,
            "sparse_row_min_fraction": float(args.sparse_row_min_fraction),
            "row_range_start": args.row_range_start,
            "row_range_end": args.row_range_end,
            "enable_strategy_search": not args.no_strategy_search,
            "strategy_search_candidates": int(args.strategy_search_candidates),
            "save_artifacts": not args.no_save_artifacts,
            "save_report": not args.no_save_report,
        }
        if args.sheet_name:
            tool_args["sheet_name"] = args.sheet_name
        if args.header_row is not None:
            tool_args["header_row"] = int(args.header_row)
        if args.data_start_row is not None:
            tool_args["data_start_row"] = int(args.data_start_row)
        if args.timestamp_column:
            tool_args["timestamp_column"] = args.timestamp_column
        if args.task_type:
            tool_args["task_type_hint"] = args.task_type
        if args.target_signals:
            tool_args["target_signals"] = args.target_signals
        if args.run_id:
            tool_args["run_id"] = args.run_id

        result = registry.execute("run_agent1_analysis", _drop_none_fields(tool_args))
        print(dumps_json(result.output, indent=2))
        return 0

    if args.command == "run-inference":
        try:
            payload = run_inference_from_artifacts(
                data_path=args.data_path,
                checkpoint_id=args.checkpoint_id,
                run_dir=args.run_dir,
                source_type=args.source_type,
                source_table=args.source_table,
                sql_query=args.sql_query,
                stream_window_rows=args.stream_window_rows,
                stream_format=args.stream_format,
                materialized_format=args.materialized_format,
                sheet_name=args.sheet_name,
                header_row=args.header_row,
                data_start_row=args.data_start_row,
                delimiter=args.delimiter,
                decision_threshold=args.decision_threshold,
                output_path=args.output_path,
            )
        except Exception as exc:
            print(dumps_json({"status": "error", "message": str(exc)}, indent=2))
            return 1
        print(dumps_json(payload, indent=2))
        return 0

    parser.error(f"Unsupported command '{args.command}'.")
    return 2


def _parse_context(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid --context-json value: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("--context-json must decode to a JSON object.")
    return parsed


def _parse_key_value_pairs(raw_pairs: list[str]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for raw in raw_pairs:
        if "=" not in raw:
            raise ValueError(f"Expected key=value label, got: {raw!r}")
        key, value = raw.split("=", 1)
        normalized_key = key.strip()
        if not normalized_key:
            raise ValueError(f"Expected non-empty label key, got: {raw!r}")
        labels[normalized_key] = value.strip()
    return labels


def _load_feedback_entries_from_args(args: argparse.Namespace) -> list[dict[str, Any]]:
    if getattr(args, "input_file", None):
        payload = json.loads(Path(args.input_file).read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [dict(item) for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            return [dict(payload)]
        raise ValueError("Feedback input file must contain one JSON object or a list of JSON objects.")
    return [
        {
            "feedback_id": getattr(args, "feedback_id", None),
            "source_type": getattr(args, "source_type", "human"),
            "feedback_type": getattr(args, "feedback_type", "decision_policy"),
            "message": getattr(args, "message", ""),
            "actor_name": getattr(args, "actor_name", None),
            "suggested_route_family": getattr(args, "suggested_route_family", None),
            "suggested_action": getattr(args, "suggested_action", None),
            "observed_outcome": getattr(args, "observed_outcome", None),
            "evidence_level": getattr(args, "evidence_level", None),
            "metric_name": getattr(args, "metric_name", None),
            "metric_value": getattr(args, "metric_value", None),
            "source_artifacts": list(getattr(args, "source_artifact", [])),
        }
    ]


def _resolve_intake_text(*, text: str | None, text_file: str | None) -> str:
    if bool(text) == bool(text_file):
        raise ValueError("Provide exactly one of --text or --text-file.")
    if text:
        resolved = text.strip()
    else:
        resolved = Path(str(text_file)).read_text(encoding="utf-8").strip()
    if not resolved:
        raise ValueError("Intake text must not be empty.")
    return resolved


def _resolve_access_request(
    *,
    run_dir: str | Path,
    text: str | None,
    text_file: str | None,
) -> tuple[str | None, str]:
    if text and text_file:
        raise ValueError("Provide at most one of --text or --text-file.")
    if text:
        resolved = text.strip()
        if not resolved:
            raise ValueError("Run request text must not be empty.")
        return resolved, "inline_text"
    if text_file:
        resolved = Path(text_file).read_text(encoding="utf-8").strip()
        if not resolved:
            raise ValueError("Run request text must not be empty.")
        return resolved, "text_file"
    if (Path(run_dir) / "intake_record.json").exists():
        return None, "existing_intake_artifacts"
    return _default_access_request_text(), "autonomous_default"


def _default_access_request_text() -> str:
    return (
        "Do everything on your own. Infer the target if it is not explicit, keep the run local-first, "
        "avoid future, post-outcome, or leakage-prone features, and build the strongest auditable first route."
    )


def _default_access_run_dir(*, data_path: str | Path) -> Path:
    dataset_stem = re.sub(r"[^A-Za-z0-9]+", "_", Path(data_path).stem).strip("_").lower() or "dataset"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return Path("artifacts") / f"run_{dataset_stem}_{stamp}"


def _emit_structured_surface_output(
    *,
    payload: dict[str, Any],
    human_text: str,
    output_format: str,
) -> None:
    if output_format == "human":
        print(human_text.rstrip())
        return
    if output_format == "json":
        print(dumps_json(payload, indent=2, ensure_ascii=False))
        return
    print(human_text.rstrip())
    print()
    print(dumps_json(payload, indent=2, ensure_ascii=False))


def _render_prediction_output(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Relaytic Prediction Summary",
            "",
            f"- Status: `{payload.get('status', 'unknown')}`",
            f"- Model: `{payload.get('model_name', 'unknown')}`",
            f"- Predictions: `{payload.get('prediction_count', 0)}`",
            f"- Rows after preprocessing: `{payload.get('rows_after_preprocessing', 0)}`",
            f"- Output path: `{payload.get('output_path') or 'not persisted'}`",
        ]
    ) + "\n"


def _render_source_inspection_output(payload: dict[str, Any]) -> str:
    notes = [f"- {item}" for item in payload.get("notes", [])]
    if not notes:
        notes = ["- no additional notes"]
    return "\n".join(
        [
            "# Relaytic Source Inspection",
            "",
            f"- Source path: `{payload.get('source_path', 'unknown')}`",
            f"- Source type: `{payload.get('source_type', 'unknown')}`",
            f"- Path kind: `{payload.get('path_kind', 'unknown')}`",
            f"- Detected format: `{payload.get('detected_format', 'unknown')}`",
            f"- Direct copy supported: `{payload.get('supports_direct_copy')}`",
            f"- Recommended materialization: `{payload.get('recommended_materialization', 'unknown')}`",
            f"- File count: `{payload.get('file_count', 0)}`",
            "",
            "## Notes",
            *notes,
        ]
    ) + "\n"


def _render_source_materialization_output(payload: dict[str, Any]) -> str:
    notes = [f"- {item}" for item in payload.get("notes", [])]
    if not notes:
        notes = ["- no additional notes"]
    row_count = payload.get("row_count")
    column_count = payload.get("column_count")
    return "\n".join(
        [
            "# Relaytic Source Materialization",
            "",
            f"- Source path: `{payload.get('source_path', 'unknown')}`",
            f"- Source type: `{payload.get('source_type', 'unknown')}`",
            f"- Detected format: `{payload.get('detected_format', 'unknown')}`",
            f"- Staged path: `{payload.get('staged_path', 'unknown')}`",
            f"- Materialized format: `{payload.get('materialized_format') or payload.get('detected_format', 'unknown')}`",
            f"- Rows: `{row_count if row_count is not None else 'not_materialized'}`",
            f"- Columns: `{column_count if column_count is not None else 'not_materialized'}`",
            "",
            "## Notes",
            *notes,
        ]
    ) + "\n"


def _run_access_flow(
    *,
    run_dir: str | None,
    data_path: str,
    source_type: str,
    source_table: str | None,
    sql_query: str | None,
    stream_window_rows: int,
    stream_format: str,
    materialized_format: str,
    config_path: str | None,
    run_id: str | None,
    text: str | None,
    text_file: str | None,
    actor_type: str,
    actor_name: str | None,
    channel: str,
    sheet_name: str | None,
    header_row: int | None,
    data_start_row: int | None,
    timestamp_column: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
) -> dict[str, Any]:
    root = Path(run_dir) if run_dir else _default_access_run_dir(data_path=data_path)
    staged_primary_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="primary",
        source_type=source_type,
        source_table=source_table,
        sql_query=sql_query,
        stream_window_rows=stream_window_rows,
        stream_format=stream_format,
        materialized_format=materialized_format,
    ) or str(Path(data_path))
    runtime_surface = _runtime_surface_from_channel(channel)
    request_text, request_source = _resolve_access_request(
        run_dir=root,
        text=text,
        text_file=text_file,
    )
    intake_payload: dict[str, Any] | None = None
    if request_text is not None:
        intake_payload = _run_intake_phase(
            run_dir=root,
            message=request_text,
            actor_type=actor_type,
            actor_name=actor_name,
            channel=channel,
            config_path=config_path,
            run_id=run_id,
            data_path=staged_primary_data_path,
            sheet_name=sheet_name,
            header_row=header_row,
            data_start_row=data_start_row,
            overwrite=overwrite,
            labels=labels,
            runtime_surface=runtime_surface,
            runtime_command="relaytic run",
        )
    investigation_payload = _run_investigation_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        overwrite=overwrite,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    memory_pre_payload = _run_memory_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        search_roots=None,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    profiles_pre_execution_payload = _run_profiles_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    planning_payload = _run_planning_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        overwrite=overwrite,
        labels=labels,
        execute_route=True,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    evidence_payload = _run_evidence_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        overwrite=overwrite,
        labels=labels,
        planning_state=planning_payload,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    memory_post_evidence_payload = _run_memory_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        search_roots=None,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    intelligence_payload = _run_intelligence_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    research_payload = _run_research_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    benchmark_payload = _run_benchmark_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    profiles_pre_completion_payload = _run_profiles_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    decision_payload = _run_decision_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    completion_payload = _run_completion_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    memory_post_completion_payload = _run_memory_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        search_roots=None,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    lifecycle_payload = _run_lifecycle_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    autonomy_payload = _run_autonomy_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    profiles_final_payload = _run_profiles_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    memory_final_payload = _run_memory_phase(
        run_dir=root,
        data_path=staged_primary_data_path,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        search_roots=None,
        runtime_surface=runtime_surface,
        runtime_command="relaytic run",
    )
    summary_materialized = materialize_run_summary(
        run_dir=root,
        data_path=staged_primary_data_path,
        request_source=request_source,
        request_text=request_text,
    )
    manifest_path = _refresh_access_manifest(
        root,
        run_id=run_id,
        policy_source=planning_payload.get("policy_resolved"),
        labels=labels,
        training_result=planning_payload.get("training_result"),
    )
    surface_payload = {
        "status": "ok",
        "run_dir": str(root),
        "data_path": staged_primary_data_path,
        "request_source": request_source,
        "intake_skipped": request_text is None,
        "manifest_path": str(manifest_path),
        "summary_path": str(summary_materialized["summary_path"]),
        "report_path": str(summary_materialized["report_path"]),
        "run_summary": summary_materialized["summary"],
    }
    if intake_payload is not None:
        surface_payload["intake"] = {
            "autonomy_mode": intake_payload.get("autonomy_mode", {}),
            "assumptions": intake_payload.get("assumptions", []),
        }
    surface_payload["investigation"] = {
        "focus_profile": investigation_payload.get("focus_profile", {}),
        "optimization_profile": investigation_payload.get("optimization_profile", {}),
    }
    surface_payload["plan"] = planning_payload.get("plan", {})
    surface_payload["training_result"] = planning_payload.get("training_result", {})
    surface_payload["evidence"] = evidence_payload["surface_payload"].get("evidence", {})
    surface_payload["intelligence"] = intelligence_payload["surface_payload"].get("intelligence", {})
    surface_payload["research"] = research_payload["surface_payload"].get("research", {})
    surface_payload["benchmark"] = benchmark_payload["surface_payload"].get("benchmark", {})
    surface_payload["decision_lab"] = decision_payload["surface_payload"].get("decision_lab", {})
    surface_payload["profiles"] = profiles_final_payload["surface_payload"].get("profiles", {})
    surface_payload["completion"] = completion_payload["surface_payload"].get("completion", {})
    surface_payload["memory"] = memory_final_payload["surface_payload"].get("memory", {})
    surface_payload["lifecycle"] = lifecycle_payload["surface_payload"].get("lifecycle", {})
    surface_payload["autonomy"] = autonomy_payload["surface_payload"].get("autonomy", {})
    return {
        "surface_payload": surface_payload,
        "human_output": summary_materialized["report_markdown"],
    }


def _run_source_inspection(
    *,
    source_path: str,
    source_type: str,
    source_table: str | None,
    sql_query: str | None,
    stream_window_rows: int,
    stream_format: str,
    materialized_format: str,
) -> dict[str, Any]:
    from relaytic.ingestion import build_source_spec, inspect_structured_source

    spec = build_source_spec(
        source_path=source_path,
        source_type=source_type,
        source_table=source_table,
        sql_query=sql_query,
        stream_window_rows=stream_window_rows,
        stream_format=stream_format,
        materialized_format=materialized_format,
    )
    inspection = inspect_structured_source(spec)
    payload = inspection.to_dict()
    return {
        "surface_payload": payload,
        "human_output": _render_source_inspection_output(payload),
    }


def _materialize_source_surface(
    *,
    source_path: str,
    run_dir: str | Path,
    source_type: str,
    source_table: str | None,
    sql_query: str | None,
    stream_window_rows: int,
    stream_format: str,
    materialized_format: str,
    purpose: str,
    alias: str | None,
) -> dict[str, Any]:
    from relaytic.ingestion import build_source_spec, materialize_structured_source

    spec = build_source_spec(
        source_path=source_path,
        source_type=source_type,
        source_table=source_table,
        sql_query=sql_query,
        stream_window_rows=stream_window_rows,
        stream_format=stream_format,
        materialized_format=materialized_format,
    )
    materialized = materialize_structured_source(
        spec=spec,
        run_dir=run_dir,
        purpose=purpose,
        alias=alias,
    )
    payload = materialized.to_dict()
    return {
        "surface_payload": payload,
        "human_output": _render_source_materialization_output(payload),
    }


def _show_access_run(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    existing_summary = read_run_summary(root)
    request = dict(existing_summary.get("request", {})) if isinstance(existing_summary, dict) else {}
    summary_materialized = _load_or_materialize_summary(
        run_dir=root,
        data_path=dict(existing_summary.get("data", {})).get("data_path") if isinstance(existing_summary, dict) else None,
        request_source=str(request.get("source", "")).strip() or None,
        request_text=str(request.get("text_preview", "")).strip() or None,
    )
    manifest_path = _refresh_access_manifest(root)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(summary_materialized["report_path"]),
            "run_summary": summary_materialized["summary"],
        },
        "human_output": summary_materialized["report_markdown"],
    }


def _load_or_materialize_summary(
    *,
    run_dir: str | Path,
    data_path: str | Path | None = None,
    request_source: str | None = None,
    request_text: str | None = None,
) -> dict[str, Any]:
    root = Path(run_dir)
    summary_path = root / "run_summary.json"
    report_path = root / "reports" / "summary.md"
    existing_summary = read_run_summary(root)
    if summary_path.exists() and report_path.exists() and isinstance(existing_summary, dict) and existing_summary:
        return {
            "summary": existing_summary,
            "summary_path": summary_path,
            "report_path": report_path,
            "report_markdown": report_path.read_text(encoding="utf-8"),
        }
    return materialize_run_summary(
        run_dir=root,
        data_path=data_path,
        request_source=request_source,
        request_text=request_text,
    )


def _show_handoff_surface(*, run_dir: str | Path, audience: str = "both") -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    summary_materialized = _load_or_materialize_summary(run_dir=root)
    summary = dict(summary_materialized["summary"])
    bundle = read_handoff_bundle(root)
    if not bundle:
        raise ValueError(f"No differentiated handoff artifacts found in {root}.")
    handoff = dict(summary.get("handoff", {}))
    user_report_path = Path(str(handoff.get("user_report_path", "")).strip()) if str(handoff.get("user_report_path", "")).strip() else None
    agent_report_path = Path(str(handoff.get("agent_report_path", "")).strip()) if str(handoff.get("agent_report_path", "")).strip() else None
    if audience == "user" and user_report_path is not None and user_report_path.exists():
        human_output = user_report_path.read_text(encoding="utf-8")
    elif audience == "agent" and agent_report_path is not None and agent_report_path.exists():
        human_output = agent_report_path.read_text(encoding="utf-8")
    else:
        human_output = render_handoff_review_markdown(bundle, audience=audience)
    manifest_path = _refresh_access_manifest(root)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "handoff": handoff,
            "bundle": bundle,
            "run_summary": summary,
        },
        "human_output": human_output,
    }


def _set_next_run_focus_surface(
    *,
    run_dir: str | Path,
    selection_id: str,
    notes: str | None,
    source: str,
    actor_type: str,
    actor_name: str | None,
    reset_requested: bool,
) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    policy = _load_mission_control_policy(run_dir=str(root), config_path=None)
    artifact = apply_next_run_focus(
        run_dir=root,
        selection_id=selection_id,
        notes=notes,
        source=source,
        actor_type=actor_type,
        actor_name=actor_name,
        reset_learnings_requested=reset_requested,
        policy=policy,
    )
    write_next_run_focus(root, artifact=artifact)
    if reset_requested:
        reset_learnings(run_dir=root, policy=policy)
    summary_materialized = materialize_run_summary(run_dir=root)
    manifest_path = _refresh_access_manifest(root)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "next_run_focus": artifact.to_dict(),
            "handoff": dict(summary_materialized["summary"].get("handoff", {})),
            "learnings": dict(summary_materialized["summary"].get("learnings", {})),
            "run_summary": summary_materialized["summary"],
        },
        "human_output": (
            f"Relaytic saved the next-run focus `{artifact.selection_id}`.\n"
            + (
                f"{artifact.summary}\n"
                if artifact.summary
                else ""
            )
            + (
                "Durable learnings were reset for the workspace.\n"
                if reset_requested
                else ""
            )
        ),
    }


def _show_learnings_surface(*, run_dir: str | None, state_dir: str | None) -> dict[str, Any]:
    root = Path(run_dir) if run_dir else None
    resolved_state_dir = Path(state_dir) if state_dir else default_learnings_state_dir(run_dir=root)
    state = read_learnings_state(resolved_state_dir)
    snapshot = read_learnings_snapshot(root) if root is not None and root.exists() else {}
    human_output = render_learnings_markdown(state, snapshot=snapshot or None)
    surface_payload: dict[str, Any] = {
        "status": "ok",
        "state_dir": str(resolved_state_dir),
        "learnings_state": state,
        "snapshot": snapshot,
    }
    if root is not None:
        surface_payload["run_dir"] = str(root)
    return {
        "surface_payload": surface_payload,
        "human_output": human_output,
    }


def _reset_learnings_surface(*, run_dir: str | None, state_dir: str | None) -> dict[str, Any]:
    root = Path(run_dir) if run_dir else None
    policy = _load_mission_control_policy(run_dir=str(root) if root is not None else None, config_path=None)
    artifact = reset_learnings(run_dir=root, state_dir=state_dir, policy=policy)
    human_output = (
        "# Relaytic Learnings Reset\n\n"
        f"- Status: `{artifact.status}`\n"
        f"- Removed entries: `{artifact.removed_entry_count}`\n"
        f"- State directory: `{artifact.state_dir}`\n"
        f"- Summary: {artifact.summary}\n"
    )
    surface_payload: dict[str, Any] = {
        "status": "ok",
        "reset": artifact.to_dict(),
    }
    if root is not None and root.exists():
        summary_materialized = materialize_run_summary(run_dir=root)
        surface_payload["run_dir"] = str(root)
        surface_payload["run_summary"] = summary_materialized["summary"]
        human_output = human_output + "\n" + summary_materialized["summary"].get("headline", "")
    return {
        "surface_payload": surface_payload,
        "human_output": human_output,
    }


def _show_workspace_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = read_workspace_bundle_for_run(root)
    result_contract_bundle = read_result_contract_artifacts(root)
    next_run_plan = read_iteration_bundle(workspace_dir=default_workspace_dir(run_dir=root), run_dir=root).get("next_run_plan", {})
    summary_bundle = _load_or_materialize_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    if not bundle and not result_contract_bundle:
        raise ValueError(f"No workspace continuity artifacts found in {root}.")
    human_output = render_workspace_review_markdown(
        workspace_bundle=bundle,
        result_contract_bundle=result_contract_bundle,
        next_run_plan=next_run_plan if isinstance(next_run_plan, dict) else None,
    )
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "workspace": bundle,
            "result_contract": result_contract_bundle,
            "next_run_plan": next_run_plan if isinstance(next_run_plan, dict) else {},
            "run_summary": summary_bundle["summary"],
        },
        "human_output": human_output,
    }


def _materialize_search_bundle(*, run_dir: Path, config_path: str | None) -> tuple[dict[str, Any], dict[str, Any], str | Path]:
    from relaytic.search import run_search_review, write_search_bundle

    foundation_state = _ensure_run_foundation_present(
        run_dir=run_dir,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    effective_policy_source: str | Path = foundation_state["policy_path"]
    if config_path:
        resolved_override = load_policy(config_path)
        effective_policy = resolved_override.policy
        effective_policy_source = config_path
    search_result = run_search_review(run_dir=run_dir, policy=effective_policy)
    written = write_search_bundle(run_dir, bundle=search_result.bundle)
    return search_result.bundle.to_dict(), written, effective_policy_source


def _run_search_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str = "relaytic search review",
) -> dict[str, Any]:
    from relaytic.search import run_search_review, write_search_bundle

    root = Path(run_dir)
    targets = _search_output_paths(root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    effective_policy = foundation_state["resolved"].policy
    effective_policy_source: str | Path = foundation_state["policy_path"]
    if config_path:
        resolved_override = load_policy(config_path)
        effective_policy = resolved_override.policy
        effective_policy_source = config_path
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=effective_policy,
        stage="search",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "run_summary.json",
            "result_contract.json",
            "next_run_plan.json",
            "budget_contract.json",
            "beat_target_contract.json",
            "trace_model.json",
        ],
    )
    try:
        search_result = run_search_review(run_dir=root, policy=effective_policy)
        written = write_search_bundle(root, bundle=search_result.bundle)
        manifest_path = _refresh_search_manifest(
            root,
            run_id=run_id,
            policy_source=effective_policy_source,
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=effective_policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic scored the value of more search, widened or pruned the challenger frontier, selected a bounded execution strategy, and recorded explicit proof artifacts for the chosen search posture.",
        )
        summary_bundle = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        surface_search = dict(summary_bundle["summary"].get("search", {}))
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "search": surface_search,
                "bundle": search_result.bundle.to_dict(),
                "run_summary": summary_bundle["summary"],
            },
            "human_output": search_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=effective_policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_search_surface(*, run_dir: str | Path, config_path: str | None = None) -> dict[str, Any]:
    from relaytic.search import render_search_review_markdown

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="search")
    effective_policy_source: str | Path | None = None
    if not bundle or not isinstance(bundle.get("search_controller_plan"), dict) or not bundle.get("search_controller_plan"):
        bundle, _, effective_policy_source = _materialize_search_bundle(run_dir=root, config_path=config_path)
    summary_materialized = _load_or_materialize_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    manifest_path = _refresh_search_manifest(root, policy_source=effective_policy_source)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(summary_materialized["report_path"]),
            "search": dict(summary_materialized["summary"].get("search", {})),
            "bundle": bundle,
            "run_summary": summary_materialized["summary"],
        },
        "human_output": render_search_review_markdown(bundle),
    }


def _materialize_daemon_bundle(*, run_dir: Path, config_path: str | None) -> tuple[dict[str, Any], dict[str, Any], str | Path]:
    from relaytic.daemon import run_daemon_review, write_daemon_bundle

    foundation_state = _ensure_run_foundation_present(
        run_dir=run_dir,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    effective_policy_source: str | Path = foundation_state["policy_path"]
    if config_path:
        resolved_override = load_policy(config_path)
        effective_policy = resolved_override.policy
        effective_policy_source = config_path
    daemon_result = run_daemon_review(run_dir=run_dir, policy=effective_policy)
    written = write_daemon_bundle(run_dir, bundle=daemon_result.bundle)
    return daemon_result.bundle.to_dict(), written, effective_policy_source


def _run_daemon_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    runtime_surface: str = "cli",
    runtime_command: str = "relaytic daemon review",
) -> dict[str, Any]:
    from relaytic.daemon import run_daemon_review, write_daemon_bundle

    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    effective_policy_source: str | Path = foundation_state["policy_path"]
    if config_path:
        resolved_override = load_policy(config_path)
        effective_policy = resolved_override.policy
        effective_policy_source = config_path
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=effective_policy,
        stage="daemon",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "run_summary.json",
            "search_controller_plan.json",
            "pulse_recommendations.json",
            "memory_compaction_plan.json",
            "result_contract.json",
            "workspace_state.json",
            "permission_mode.json",
        ],
    )
    try:
        daemon_result = run_daemon_review(run_dir=root, policy=effective_policy)
        written = write_daemon_bundle(root, bundle=daemon_result.bundle)
        manifest_path = _refresh_daemon_manifest(root, policy_source=effective_policy_source)
        record_runtime_stage_completion(
            run_dir=root,
            policy=effective_policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic materialized the bounded background-job registry, checkpoint posture, approval queue, memory-maintenance queue, and resumable daemon artifacts.",
        )
        summary_bundle = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        surface_daemon = dict(summary_bundle["summary"].get("daemon", {}))
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "daemon": surface_daemon,
                "bundle": daemon_result.bundle.to_dict(),
                "run_summary": summary_bundle["summary"],
            },
            "human_output": daemon_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=effective_policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_daemon_surface(*, run_dir: str | Path, config_path: str | None = None) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle, _, effective_policy_source = _materialize_daemon_bundle(run_dir=root, config_path=config_path)
    summary_materialized = _load_or_materialize_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    manifest_path = _refresh_daemon_manifest(root, policy_source=effective_policy_source)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(summary_materialized["report_path"]),
            "daemon": dict(summary_materialized["summary"].get("daemon", {})),
            "bundle": bundle,
            "run_summary": summary_materialized["summary"],
        },
        "human_output": render_daemon_review_markdown(bundle),
    }


def _show_remote_control_surface(*, run_dir: str | Path, config_path: str | None = None) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    if config_path:
        effective_policy = load_policy(config_path).policy
    result = run_remote_control_review(run_dir=root, policy=effective_policy)
    summary_materialized = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "remote": dict(summary_materialized["summary"].get("remote", {})),
            "bundle": result.bundle.to_dict(),
            "run_summary": summary_materialized["summary"],
        },
        "human_output": result.review_markdown,
    }


def _decide_remote_approval_surface(
    *,
    run_dir: str | Path,
    request_id: str,
    decision: str,
    config_path: str | None,
    actor_type: str,
    actor_name: str | None,
) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    if config_path:
        effective_policy = load_policy(config_path).policy
    result = apply_remote_approval_decision(
        run_dir=root,
        request_id=request_id,
        decision=decision,
        policy=effective_policy,
        actor_type=actor_type,
        actor_name=actor_name,
        source_surface="cli",
        source_command="relaytic remote decide",
    )
    summary_materialized = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "decision": result.decision,
            "remote": dict(summary_materialized["summary"].get("remote", {})),
            "bundle": result.bundle.to_dict(),
            "run_summary": summary_materialized["summary"],
        },
        "human_output": result.review_markdown,
    }


def _handoff_remote_supervision_surface(
    *,
    run_dir: str | Path,
    to_actor_type: str,
    to_actor_name: str | None,
    from_actor_type: str,
    from_actor_name: str | None,
    reason: str | None,
    config_path: str | None,
) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    if config_path:
        effective_policy = load_policy(config_path).policy
    result = apply_remote_supervision_handoff(
        run_dir=root,
        to_actor_type=to_actor_type,
        to_actor_name=to_actor_name,
        from_actor_type=from_actor_type,
        from_actor_name=from_actor_name,
        reason=reason,
        policy=effective_policy,
        source_surface="cli",
        source_command="relaytic remote handoff",
    )
    summary_materialized = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "handoff": result.decision,
            "remote": dict(summary_materialized["summary"].get("remote", {})),
            "bundle": result.bundle.to_dict(),
            "run_summary": summary_materialized["summary"],
        },
        "human_output": result.review_markdown,
    }


def _run_background_job_surface(
    *,
    run_dir: str | Path,
    job_id: str,
    config_path: str | None,
    actor_type: str,
    actor_name: str | None,
) -> dict[str, Any]:
    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    if config_path:
        effective_policy = load_policy(config_path).policy
    result = run_background_job(
        run_dir=root,
        job_id=job_id,
        policy=effective_policy,
        actor_type=actor_type,
        actor_name=actor_name,
    )
    summary_materialized = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    manifest_path = _refresh_daemon_manifest(root, policy_source=config_path or foundation_state["policy_path"])
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "daemon": dict(summary_materialized["summary"].get("daemon", {})),
            "job": result.job,
            "bundle": result.bundle.to_dict(),
            "run_summary": summary_materialized["summary"],
        },
        "human_output": result.review_markdown,
    }


def _resume_background_job_surface(
    *,
    run_dir: str | Path,
    job_id: str,
    config_path: str | None,
    actor_type: str,
    actor_name: str | None,
) -> dict[str, Any]:
    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    if config_path:
        effective_policy = load_policy(config_path).policy
    result = resume_background_job(
        run_dir=root,
        job_id=job_id,
        policy=effective_policy,
        actor_type=actor_type,
        actor_name=actor_name,
    )
    summary_materialized = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    manifest_path = _refresh_daemon_manifest(root, policy_source=config_path or foundation_state["policy_path"])
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "daemon": dict(summary_materialized["summary"].get("daemon", {})),
            "job": result.job,
            "bundle": result.bundle.to_dict(),
            "run_summary": summary_materialized["summary"],
        },
        "human_output": result.review_markdown,
    }


def _run_release_safety_scan_surface(
    *,
    target_path: str | None,
    state_dir: str | None,
) -> dict[str, Any]:
    scan_result = run_release_safety_scan(
        target_path=target_path,
        state_dir=state_dir,
        tracked_only=target_path is None,
    )
    bundle = scan_result.bundle.to_dict()
    return {
        "surface_payload": {
            "status": bundle["release_safety_scan"]["status"],
            "state_dir": str(scan_result.state_dir),
            "target_path": target_path,
            "release_safety": bundle["release_safety_scan"],
            "bundle": bundle,
        },
        "human_output": scan_result.review_markdown,
    }


def _show_release_safety_surface(*, state_dir: str | None) -> dict[str, Any]:
    resolved_state_dir = Path(state_dir) if state_dir else latest_release_safety_state_dir()
    bundle = read_release_safety_bundle(resolved_state_dir)
    if not bundle or not isinstance(bundle.get("release_safety_scan"), dict):
        raise ValueError(
            f"Release-safety artifacts are missing in `{resolved_state_dir}`. Run `relaytic release-safety scan` first."
        )
    return {
        "surface_payload": {
            "status": bundle["release_safety_scan"]["status"],
            "state_dir": str(resolved_state_dir),
            "release_safety": bundle["release_safety_scan"],
            "bundle": bundle,
        },
        "human_output": render_release_safety_markdown(bundle),
    }


def _scan_git_safety_passthrough(*, paths: list[str]) -> dict[str, Any]:
    explicit_paths = [Path(item) for item in paths] if paths else None
    scan_result = run_release_safety_scan(
        target_path=None,
        state_dir=default_release_safety_state_dir(target_path=None),
        explicit_paths=explicit_paths,
        tracked_only=not bool(explicit_paths),
    )
    bundle = scan_result.bundle.to_dict()
    sensitive = list(bundle.get("sensitive_string_audit", {}).get("findings", []))
    source_maps = list(bundle.get("source_map_audit", {}).get("findings", []))
    packaging = list(bundle.get("packaging_regression_report", {}).get("findings", []))
    findings = sensitive + source_maps + packaging
    return {
        "surface_payload": {
            "status": bundle["release_safety_scan"]["status"],
            "findings": findings,
            "bundle": bundle,
        },
        "human_output": scan_result.review_markdown,
    }


def _continue_workspace_surface(
    *,
    run_dir: str | Path,
    direction: str,
    notes: str | None,
    source: str,
    actor_type: str,
    actor_name: str | None,
    reset_requested: bool,
) -> dict[str, Any]:
    focus_payload = _set_next_run_focus_surface(
        run_dir=run_dir,
        selection_id=direction,
        notes=notes,
        source=source,
        actor_type=actor_type,
        actor_name=actor_name,
        reset_requested=reset_requested,
    )
    root = Path(run_dir)
    policy = _load_mission_control_policy(run_dir=str(root), config_path=None)
    try:
        runtime = build_runtime_surface(run_dir=root)
        stage = str(dict(runtime.get("runtime", {})).get("current_stage", "")).strip() or "workspace"
        record_runtime_event(
            run_dir=root,
            policy=policy,
            event_type="workspace_resumed",
            stage=stage,
            source_surface="cli",
            source_command="relaytic workspace continue",
            status="ok",
            summary=f"Relaytic continued the workspace on direction `{direction}`.",
            metadata={"direction": direction, "actor_type": actor_type, "actor_name": actor_name},
        )
    except Exception:
        pass
    workspace_payload = _show_workspace_surface(run_dir=run_dir)
    return {
        "surface_payload": {
            "status": "ok",
            "continuation": focus_payload["surface_payload"]["next_run_focus"],
            "workspace": workspace_payload["surface_payload"]["workspace"],
            "result_contract": workspace_payload["surface_payload"]["result_contract"],
            "next_run_plan": workspace_payload["surface_payload"]["next_run_plan"],
            "run_summary": focus_payload["surface_payload"]["run_summary"],
        },
        "human_output": (
            f"Relaytic updated the workspace continuation direction to `{direction}`.\n\n"
            + str(workspace_payload["human_output"]).rstrip()
        ),
    }


def _show_assist_surface(*, run_dir: str | Path, config_path: str | None) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    assist_payload = _materialize_assist_surface(
        run_dir=root,
        config_path=config_path,
        last_user_intent=None,
        last_requested_stage=None,
        last_action_kind=None,
        increment_turn_count=False,
    )
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(assist_payload["manifest_path"]),
            "assist": assist_payload["bundle"],
            "run_summary": assist_payload["run_summary"],
        },
        "human_output": render_assist_markdown(assist_payload["bundle"]),
    }


def _run_assist_turn(
    *,
    run_dir: str | Path,
    message: str,
    config_path: str | None,
    data_path: str | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
    actor_type: str = "user",
    actor_name: str | None = None,
) -> dict[str, Any]:
    from relaytic.assist import build_assist_audit_explanation

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    base_payload = _materialize_assist_surface(
        run_dir=root,
        config_path=config_path,
        last_user_intent=None,
        last_requested_stage=None,
        last_action_kind=None,
        increment_turn_count=False,
    )
    bundle = dict(base_payload["bundle"])
    run_summary = dict(base_payload["run_summary"])
    stage_before = str(run_summary.get("stage_completed", "")).strip() or "unknown"
    plan = plan_assist_turn(
        message=message,
        run_summary=run_summary,
        assist_bundle=bundle,
    )
    control_payload = _run_control_phase(
        run_dir=root,
        message=message,
        action_kind=plan.action_kind,
        requested_stage=plan.requested_stage,
        config_path=config_path,
        run_id=None,
        labels=None,
        actor_type=actor_type,
        actor_name=actor_name,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command or "relaytic assist turn",
    )
    control_summary = dict(control_payload["surface_payload"].get("control", {}))
    control_bundle = dict(control_payload["surface_payload"].get("bundle", {}))
    control_decision = str(control_summary.get("decision", "")).strip() or "accept"
    approved_action_kind = str(control_summary.get("approved_action_kind", "")).strip() or plan.action_kind
    approved_stage_text = str(control_summary.get("approved_stage", "")).strip()
    approved_stage = approved_stage_text or (plan.requested_stage if control_decision in {"accept", "accept_with_modification"} else None)
    executed_stages: list[str] = []
    audit_payload: dict[str, Any] | None = None
    if control_decision in {"reject", "defer"}:
        action_message = str(dict(control_bundle.get("override_decision", {})).get("summary") or plan.response_message)
    else:
        action_message = str(plan.response_message)
    if control_decision in {"accept", "accept_with_modification"} and approved_action_kind == "show_handoff":
        handoff_payload = _show_handoff_surface(
            run_dir=root,
            audience="agent" if str(actor_type).strip().lower() == "agent" else "user",
        )
        action_message = str(handoff_payload["human_output"]).rstrip()
    elif control_decision in {"accept", "accept_with_modification"} and approved_action_kind == "show_learnings":
        learnings_payload = _show_learnings_surface(run_dir=str(root), state_dir=None)
        action_message = str(learnings_payload["human_output"]).rstrip()
    elif control_decision in {"accept", "accept_with_modification"} and approved_action_kind == "show_workspace":
        workspace_payload = _show_workspace_surface(run_dir=root)
        action_message = str(workspace_payload["human_output"]).rstrip()
    elif control_decision in {"accept", "accept_with_modification"} and approved_action_kind == "reset_learnings":
        learnings_payload = _reset_learnings_surface(run_dir=str(root), state_dir=None)
        action_message = str(learnings_payload["human_output"]).rstrip()
    elif control_decision in {"accept", "accept_with_modification"} and approved_action_kind == "focus_next_run":
        selection_id = plan.intent.next_run_selection
        if not selection_id:
            action_message = (
                "Relaytic did not detect a concrete next-run selection. "
                "Use `same_data`, `add_data`, or `new_dataset` in the message."
            )
        else:
            focus_payload = _set_next_run_focus_surface(
                run_dir=root,
                selection_id=selection_id,
                notes=plan.intent.focus_notes,
                source="assist",
                actor_type=actor_type,
                actor_name=actor_name,
                reset_requested=bool(plan.intent.reset_learnings_requested),
            )
            action_message = str(focus_payload["human_output"]).rstrip()
    elif control_decision in {"accept", "accept_with_modification"} and approved_action_kind == "rerun_stage" and approved_stage:
        executed_stages = _run_assist_stage_pipeline(
            run_dir=root,
            start_stage=approved_stage,
            config_path=config_path,
            data_path=data_path,
            overwrite=True,
        )
        action_message = (
            f"Relaytic reran `{approved_stage}` and refreshed downstream stages: "
            + ", ".join(executed_stages)
            + "."
        )
    elif control_decision in {"accept", "accept_with_modification"} and approved_action_kind == "take_over":
        start_stage = _next_takeover_stage(run_dir=root, run_summary=run_summary)
        if start_stage is None:
            action_message = (
                "Relaytic does not see a further safe automatic step from the current state. "
                "You can ask for an explanation, a specific rerun like `go back to research`, "
                "or continue once a new benchmark or feedback slice exists."
            )
        else:
            executed_stages = _run_assist_stage_pipeline(
                run_dir=root,
                start_stage=start_stage,
                config_path=config_path,
                data_path=data_path,
                overwrite=True,
            )
            action_message = (
                f"Relaytic took over from `{start_stage}` and refreshed: "
                + ", ".join(executed_stages)
                + "."
            )
    elif control_decision in {"accept", "accept_with_modification"} and approved_action_kind == "respond" and plan.intent.intent_type == "explain":
        audit_payload = build_assist_audit_explanation(
            message=message,
            run_summary=run_summary,
            actor_type=actor_type,
        )
        audit_payload = _maybe_enhance_audit_explanation_with_local_advisor(
            run_dir=root,
            config_path=config_path,
            actor_type=actor_type,
            message=message,
            audit_payload=audit_payload,
        )
        action_message = str(audit_payload.get("answer") or action_message).rstrip()
    refreshed = _materialize_assist_surface(
        run_dir=root,
        config_path=config_path,
        last_user_intent=plan.intent.intent_type,
        last_requested_stage=approved_stage,
        last_action_kind=approved_action_kind,
        increment_turn_count=True,
    )
    stage_after = str(refreshed["run_summary"].get("stage_completed", "")).strip() or "unknown"
    log_entry = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "message": str(message),
        "intent_type": plan.intent.intent_type,
        "requested_stage": plan.requested_stage,
        "requested_action_kind": plan.action_kind,
        "action_kind": approved_action_kind,
        "control_decision": control_decision,
        "checkpoint_id": control_summary.get("checkpoint_id"),
        "skepticism_level": control_summary.get("skepticism_level"),
        "stage_before": stage_before,
        "stage_after": stage_after,
        "executed_stages": executed_stages,
        "response_message": action_message,
        "next_recommended_action": dict(refreshed["run_summary"].get("next_step", {})).get("recommended_action"),
        "audit_question_type": None if audit_payload is None else audit_payload.get("question_type"),
        "audit_llm_enhanced": None if audit_payload is None else audit_payload.get("llm_enhanced"),
    }
    from relaytic.assist import append_assist_turn_log

    log_path = append_assist_turn_log(root, entry=log_entry)
    _refresh_control_manifest(root)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(refreshed["manifest_path"]),
            "assist": refreshed["bundle"],
            "run_summary": refreshed["run_summary"],
            "control": control_summary,
            "control_bundle": control_bundle,
            "audit": audit_payload,
            "turn": log_entry,
            "log_path": str(log_path),
        },
        "human_output": action_message + "\n",
    }


def _maybe_enhance_audit_explanation_with_local_advisor(
    *,
    run_dir: Path,
    config_path: str | None,
    actor_type: str,
    message: str,
    audit_payload: dict[str, Any],
) -> dict[str, Any]:
    if str(actor_type).strip().lower() != "user":
        return audit_payload
    try:
        from relaytic.intelligence import build_intelligence_controls_from_policy
        from relaytic.intelligence.backends import discover_backend

        foundation_state = _ensure_run_foundation_present(
            run_dir=run_dir,
            config_path=config_path,
            run_id=None,
            labels=None,
        )
        discovery = discover_backend(
            controls=build_intelligence_controls_from_policy(foundation_state["resolved"].policy),
            config_path=config_path,
        )
        if discovery.status != "available" or discovery.advisor is None:
            return audit_payload
        advisory = discovery.advisor.complete_json(
            task_name="assist_audit_explanation",
            system_prompt=(
                "Rewrite the provided deterministic Relaytic audit explanation for a human operator. "
                "Do not add facts. Keep the answer concise, exact, and grounded in the supplied reasons. "
                "Return JSON with keys answer and bullets. answer must be a short paragraph string. "
                "bullets must be a short list of plain-English points."
            ),
            payload={
                "user_question": message,
                "deterministic_answer": audit_payload.get("answer"),
                "reasons": audit_payload.get("reasons"),
                "evidence_refs": audit_payload.get("evidence_refs"),
            },
        )
        if advisory.status != "ok" or not isinstance(advisory.payload, dict):
            return audit_payload
        answer = str(advisory.payload.get("answer", "")).strip()
        bullets = advisory.payload.get("bullets")
        updated = dict(audit_payload)
        if answer:
            updated["answer"] = answer
        if isinstance(bullets, list):
            updated["reasons"] = [str(item).strip() for item in bullets if str(item).strip()] or updated.get("reasons", [])
        updated["llm_enhanced"] = bool(answer or bullets)
        return updated
    except Exception:
        return audit_payload


def _run_assist_chat(
    *,
    run_dir: str | Path,
    config_path: str | None,
    data_path: str | None,
    show_json: bool,
    max_turns: int,
) -> int:
    if max_turns < 0:
        print("max-turns must be >= 0")
        return 2
    print(
        "relaytic> Communicative assist session started. "
        "Assist chat is the live terminal conversation for an existing run. "
        "Ask things like `what can you do?`, `why did you choose this route?`, "
        "`what did you find?`, `show the workspace`, `what would change your mind?`, "
        "`use the same data next time but focus on recall`, `show learnings`, "
        "`go back to planning`, or `i'm not sure, take over`. "
        "Commands: /help, /show, /capabilities, /report, /workspace, /learnings, /stages, /next, /takeover, /exit."
    )
    turns = 0
    while True:
        try:
            raw = input("you> ")
        except EOFError:
            print("\nSession ended.")
            return 0
        except KeyboardInterrupt:
            print("\nSession interrupted.")
            return 0
        message = raw.strip()
        if not message:
            continue
        lowered = message.lower()
        if lowered in {"/exit", "/quit"}:
            print("Session ended.")
            return 0
        if lowered == "/help":
            print(
                "relaytic> Ask for `status`, `why`, `what can you do?`, `connect claude`, "
                "`what did you find?`, `show the workspace`, `what would change your mind?`, "
                "`show learnings`, `go back to research`, or `take over`. "
                "Shortcuts: /show, /capabilities, /report, /workspace, /learnings, /stages, /next, /takeover, /exit."
            )
            continue
        if lowered == "/show":
            payload = _show_assist_surface(run_dir=run_dir, config_path=config_path)
            print(payload["human_output"].rstrip())
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            continue
        if lowered == "/capabilities":
            payload = _run_assist_turn(
                run_dir=run_dir,
                message="what can you do?",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if lowered == "/report":
            payload = _run_assist_turn(
                run_dir=run_dir,
                message="what did you find?",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if lowered == "/workspace":
            payload = _run_assist_turn(
                run_dir=run_dir,
                message="show the workspace",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if lowered == "/learnings":
            payload = _run_assist_turn(
                run_dir=run_dir,
                message="show learnings",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if lowered == "/stages":
            payload = _show_assist_surface(run_dir=run_dir, config_path=config_path)
            assist_state = dict(payload["surface_payload"].get("assist", {}).get("assist_session_state", {}))
            stages = [str(item).strip() for item in assist_state.get("available_stage_targets", []) if str(item).strip()]
            if stages:
                print(
                    "relaytic> Relaytic currently supports bounded stage reruns for: "
                    + ", ".join(f"`{item}`" for item in stages)
                    + ". This is not arbitrary checkpoint time travel."
                )
            else:
                print("relaytic> No bounded stage reruns are available yet for this run.")
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            continue
        if lowered == "/next":
            payload = _show_run_summary_surface(run_dir=run_dir)
            next_step = dict(payload["surface_payload"].get("run_summary", {}).get("next_step", {}))
            print(
                "relaytic> "
                + (
                    f"Next recommended action is `{str(next_step.get('recommended_action', '')).strip() or 'none'}`. "
                    f"{str(next_step.get('rationale', '')).strip() or 'Relaytic has no further rationale yet.'}"
                )
            )
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            continue
        if lowered == "/takeover":
            payload = _run_assist_turn(
                run_dir=run_dir,
                message="i'm not sure, take over",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        payload = _run_assist_turn(
            run_dir=run_dir,
            message=message,
            config_path=config_path,
            data_path=data_path,
        )
        print("relaytic> " + payload["human_output"].strip())
        if show_json:
            print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
        turns += 1
        if max_turns > 0 and turns >= max_turns:
            print("Session ended.")
            return 0


def _run_mission_control_chat(
    *,
    run_dir: str | None,
    output_dir: str | None,
    config_path: str | None,
    expected_profile: str,
    data_path: str | None,
    show_json: bool,
    max_turns: int,
) -> int:
    if max_turns < 0:
        print("max-turns must be >= 0")
        return 2
    active_run_dir = run_dir
    run_context = bool(active_run_dir)
    if not run_context:
        from relaytic.mission_control import write_mission_control_artifact

        state_root = _resolve_mission_control_root(run_dir=None, output_dir=output_dir)
        policy = _load_mission_control_policy(run_dir=None, config_path=config_path)
        communication_cfg = dict(policy.get("communication", {}))
        if not bool(communication_cfg.get("adaptive_onboarding_resume_existing_session", False)):
            write_mission_control_artifact(
                state_root,
                key="onboarding_chat_session_state",
                payload=_fresh_onboarding_chat_session_state(policy=policy),
            )
    current_payload = _show_mission_control_surface(
        run_dir=active_run_dir,
        output_dir=output_dir,
        config_path=config_path,
        expected_profile=expected_profile,
    )

    def _current_chat_stage() -> str:
        mission = dict(current_payload.get("surface_payload", {}).get("mission_control", {}))
        return str(mission.get("current_stage", "")).strip() or "runtime"

    def _record_chat_event(event_type: str, *, status: str, summary: str, metadata: dict[str, Any] | None = None) -> None:
        if not active_run_dir:
            return
        try:
            policy = _load_mission_control_policy(run_dir=active_run_dir, config_path=config_path)
            record_runtime_event(
                run_dir=active_run_dir,
                policy=policy,
                event_type=event_type,
                stage=_current_chat_stage(),
                source_surface="cli",
                source_command="relaytic mission-control chat",
                status=status,
                summary=summary,
                metadata=metadata,
            )
        except Exception:
            return

    if run_context:
        _record_chat_event(
            "session_started",
            status="ok",
            summary="Relaytic started a mission-control chat session for an existing run.",
            metadata={"interaction_mode": "mission_control_chat"},
        )
    if run_context:
        print(
            "relaytic> Mission-control chat is the terminal companion to the dashboard. "
            "Ask things like `what can you do?`, `why did you choose this route?`, "
            "`what did you find?`, `use the same data next time but focus on recall`, "
            "`show learnings`, `go back to planning`, or `i'm not sure, take over`. "
            "Commands: /help, /show, /capabilities, /report, /learnings, /stages, /next, /takeover, /modes, /stuck, /handbook, /exit."
        )
    else:
        print(
            "relaytic> Mission-control chat is the terminal onboarding surface. "
            "You can paste a dataset path directly, describe the goal in plain language, or do both in one message. "
            "Ask things like `what is relaytic?`, `how do i start?`, `what data formats do you support?`, "
            "or `why are some capabilities disabled?`. "
            "Commands: /help, /show, /start, /demo, /formats, /hosts, /modes, /stuck, /handbook, /state, /reset, /exit."
        )
    turns = 0
    while True:
        try:
            raw = input("you> ")
        except EOFError:
            _record_chat_event("session_ended", status="ok", summary="Mission-control chat ended after EOF.")
            print("\nSession ended.")
            return 0
        except KeyboardInterrupt:
            _record_chat_event("session_ended", status="ok", summary="Mission-control chat ended after keyboard interrupt.")
            print("\nSession interrupted.")
            return 0
        message = raw.strip()
        if not message:
            continue
        if run_context:
            _record_chat_event(
                "prompt_submitted",
                status="ok",
                summary="Mission-control chat received one operator prompt.",
                metadata={"message_length": len(message), "is_command": message.startswith("/")},
            )
        lowered = message.lower()
        if lowered in {"/exit", "/quit"}:
            _record_chat_event("session_ended", status="ok", summary="Mission-control chat ended explicitly.")
            print("Session ended.")
            return 0
        if lowered == "/help":
            if run_context:
                print(
                    "relaytic> Use /show for the dashboard summary, /capabilities for current options, "
                    "/report for the differentiated result handoff, /learnings for durable memory, "
                    "/stages for bounded reruns, /next for the next recommended step, /takeover to let Relaytic continue, "
                    "/modes for surface explanations, /stuck for recovery guidance, /handbook for the user/agent guides, or /exit."
                )
            else:
                print(
                    "relaytic> Use /show for the dashboard summary, /start for first steps, /demo for a guided walkthrough, "
                    "/formats for supported data sources, /hosts for Claude/Codex/OpenClaw guidance, /modes for surface explanations, "
                    "/stuck for recovery guidance, /handbook for the role-specific guides, /state to show captured inputs, "
                    "/reset to start over, or /exit."
                )
            continue
        if lowered == "/show":
            current_payload = _show_mission_control_surface(
                run_dir=active_run_dir,
                output_dir=output_dir,
                config_path=config_path,
                expected_profile=expected_profile,
            )
            print(current_payload["human_output"].rstrip())
            if show_json:
                print(dumps_json(current_payload["surface_payload"], indent=2, ensure_ascii=False))
            continue
        if lowered == "/handbook":
            print("relaytic> " + _onboarding_chat_response(message="where is the handbook?", mission_control_payload=current_payload))
            if show_json:
                print(dumps_json(current_payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if not run_context:
            if lowered == "/start":
                print("relaytic> " + _onboarding_chat_response(message="how do i start", mission_control_payload=current_payload))
                turns += 1
            elif lowered == "/demo":
                print("relaytic> " + _onboarding_chat_response(message="show me a demo flow", mission_control_payload=current_payload))
                turns += 1
            elif lowered == "/formats":
                print("relaytic> " + _onboarding_chat_response(message="what data formats do you support", mission_control_payload=current_payload))
                turns += 1
            elif lowered == "/hosts":
                print("relaytic> " + _onboarding_chat_response(message="how do i use this with claude, codex, or openclaw", mission_control_payload=current_payload))
                turns += 1
            elif lowered == "/modes":
                print("relaytic> " + _onboarding_chat_response(message="what do the modes mean", mission_control_payload=current_payload))
                turns += 1
            elif lowered == "/stuck":
                print("relaytic> " + _onboarding_chat_response(message="i'm stuck, what should i do", mission_control_payload=current_payload))
                turns += 1
            elif lowered == "/state":
                adaptive = _run_adaptive_onboarding_turn(
                    message="/state",
                    mission_control_payload=current_payload,
                    output_dir=output_dir,
                    config_path=config_path,
                    expected_profile=expected_profile,
                )
                current_payload = _show_mission_control_surface(
                    run_dir=None,
                    output_dir=output_dir,
                    config_path=config_path,
                    expected_profile=expected_profile,
                )
                print("relaytic> " + adaptive["response_text"])
                turns += 1
            elif lowered == "/reset":
                adaptive = _run_adaptive_onboarding_turn(
                    message="/reset",
                    mission_control_payload=current_payload,
                    output_dir=output_dir,
                    config_path=config_path,
                    expected_profile=expected_profile,
                )
                current_payload = _show_mission_control_surface(
                    run_dir=None,
                    output_dir=output_dir,
                    config_path=config_path,
                    expected_profile=expected_profile,
                )
                print("relaytic> " + adaptive["response_text"])
                turns += 1
            else:
                adaptive = _run_adaptive_onboarding_turn(
                    message=message,
                    mission_control_payload=current_payload,
                    output_dir=output_dir,
                    config_path=config_path,
                    expected_profile=expected_profile,
                )
                print("relaytic> " + adaptive["response_text"])
                if adaptive["started_run_dir"] is not None:
                    active_run_dir = adaptive["started_run_dir"]
                    run_context = True
                    current_payload = _show_mission_control_surface(
                        run_dir=active_run_dir,
                        output_dir=output_dir,
                        config_path=config_path,
                        expected_profile=expected_profile,
                    )
                    _record_chat_event(
                        "session_started",
                        status="ok",
                        summary="Relaytic promoted onboarding chat into a run-specific mission-control session.",
                        metadata={"interaction_mode": "mission_control_chat"},
                    )
                    print(
                        "relaytic> Relaytic is now in run-specific mode. "
                        "You can ask `what can you do?`, `why did you choose this route?`, `go back to planning`, "
                        "or `i'm not sure, take over`."
                    )
                else:
                    current_payload = _show_mission_control_surface(
                        run_dir=None,
                        output_dir=output_dir,
                        config_path=config_path,
                        expected_profile=expected_profile,
                    )
                turns += 1
            if show_json:
                print(dumps_json(current_payload["surface_payload"], indent=2, ensure_ascii=False))
            if max_turns > 0 and turns >= max_turns:
                _record_chat_event("session_ended", status="ok", summary="Mission-control chat ended after reaching the turn cap.")
                print("Session ended.")
                return 0
            continue

        if lowered == "/capabilities":
            payload = _run_assist_turn(
                run_dir=active_run_dir,
                message="what can you do?",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            current_payload = _show_mission_control_surface(
                run_dir=active_run_dir,
                output_dir=output_dir,
                config_path=config_path,
                expected_profile=expected_profile,
            )
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                _record_chat_event("session_ended", status="ok", summary="Mission-control chat ended after reaching the turn cap.")
                print("Session ended.")
                return 0
            continue
        if lowered == "/report":
            payload = _run_assist_turn(
                run_dir=active_run_dir,
                message="what did you find?",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            current_payload = _show_mission_control_surface(
                run_dir=active_run_dir,
                output_dir=output_dir,
                config_path=config_path,
                expected_profile=expected_profile,
            )
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if lowered == "/learnings":
            payload = _run_assist_turn(
                run_dir=active_run_dir,
                message="show learnings",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            current_payload = _show_mission_control_surface(
                run_dir=active_run_dir,
                output_dir=output_dir,
                config_path=config_path,
                expected_profile=expected_profile,
            )
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if lowered == "/stages":
            navigator = dict(current_payload["surface_payload"].get("bundle", {}).get("stage_navigator", {}))
            stages = [dict(item) for item in navigator.get("available_stages", []) if isinstance(item, dict)]
            if stages:
                stage_text = ", ".join(f"`{str(item.get('stage', '')).strip()}`" for item in stages if str(item.get("stage", "")).strip())
                print(
                    "relaytic> Relaytic currently supports bounded stage reruns for "
                    + (stage_text or "`none`")
                    + ". This is not arbitrary checkpoint time travel."
                )
            else:
                print("relaytic> No bounded stage reruns are available yet for this run.")
            if show_json:
                print(dumps_json(current_payload["surface_payload"], indent=2, ensure_ascii=False))
            continue
        if lowered == "/next":
            mission = dict(current_payload["surface_payload"].get("mission_control", {}))
            print(
                "relaytic> "
                + f"Next actor is `{str(mission.get('next_actor') or 'operator')}` and the recommended action is "
                + f"`{str(mission.get('recommended_action') or 'none')}`."
            )
            if show_json:
                print(dumps_json(current_payload["surface_payload"], indent=2, ensure_ascii=False))
            continue
        if lowered == "/takeover":
            payload = _run_assist_turn(
                run_dir=active_run_dir,
                message="i'm not sure, take over",
                config_path=config_path,
                data_path=data_path,
            )
            print("relaytic> " + payload["human_output"].strip())
            current_payload = _show_mission_control_surface(
                run_dir=active_run_dir,
                output_dir=output_dir,
                config_path=config_path,
                expected_profile=expected_profile,
            )
            if show_json:
                print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if lowered == "/modes":
            print("relaytic> " + _onboarding_chat_response(message="what do the modes mean", mission_control_payload=current_payload))
            if show_json:
                print(dumps_json(current_payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        if lowered == "/stuck":
            print("relaytic> " + _onboarding_chat_response(message="i'm stuck, what should i do", mission_control_payload=current_payload))
            if show_json:
                print(dumps_json(current_payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        onboarding_response = _maybe_onboarding_chat_response(message=message, mission_control_payload=current_payload)
        if onboarding_response is not None:
            print("relaytic> " + onboarding_response)
            if show_json:
                print(dumps_json(current_payload["surface_payload"], indent=2, ensure_ascii=False))
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print("Session ended.")
                return 0
            continue
        payload = _run_assist_turn(
            run_dir=active_run_dir,
            message=message,
            config_path=config_path,
            data_path=data_path,
        )
        print("relaytic> " + payload["human_output"].strip())
        current_payload = _show_mission_control_surface(
            run_dir=active_run_dir,
            output_dir=output_dir,
            config_path=config_path,
            expected_profile=expected_profile,
        )
        if show_json:
            print(dumps_json(payload["surface_payload"], indent=2, ensure_ascii=False))
        turns += 1
        if max_turns > 0 and turns >= max_turns:
            print("Session ended.")
            return 0


def _maybe_onboarding_chat_response(*, message: str, mission_control_payload: dict[str, Any]) -> str | None:
    normalized = " ".join(str(message).strip().lower().split())
    onboarding_tokens = (
        "what is relaytic",
        "how do i start",
        "first step",
        "data format",
        "formats",
        "why are some capabilities disabled",
        "capabilities disabled",
        "what can you do",
        "where is the handbook",
        "handbook",
        "what should an agent read first",
        "show me a demo flow",
        "demo flow",
        "what do the modes mean",
        "mode",
        "i'm stuck",
        "im stuck",
        "stuck",
        "what happens next",
        "claude",
        "codex",
        "openclaw",
        "mcp",
        "host",
    )
    if any(token in normalized for token in onboarding_tokens):
        return _onboarding_chat_response(message=message, mission_control_payload=mission_control_payload)
    return None


def _onboarding_chat_response(*, message: str, mission_control_payload: dict[str, Any]) -> str:
    normalized = " ".join(str(message).strip().lower().split())
    bundle = dict(mission_control_payload.get("surface_payload", {}).get("bundle", {}))
    onboarding = dict(bundle.get("onboarding_status", {}))
    capabilities = [dict(item) for item in dict(bundle.get("capability_manifest", {})).get("capabilities", []) if isinstance(item, dict)]
    actions = [dict(item) for item in dict(bundle.get("action_affordances", {})).get("actions", []) if isinstance(item, dict)]
    questions = [dict(item) for item in dict(bundle.get("question_starters", {})).get("starters", []) if isinstance(item, dict)]
    guided_demo_flow = [str(item).strip() for item in onboarding.get("guided_demo_flow", []) if str(item).strip()]
    stuck_guide = [str(item).strip() for item in onboarding.get("stuck_guide", []) if str(item).strip()]
    mode_explanations = [dict(item) for item in onboarding.get("mode_explanations", []) if isinstance(item, dict)]
    host_summary = dict(onboarding.get("host_summary", {}))
    live_chat_command = str(onboarding.get("live_chat_command") or "relaytic mission-control chat").strip()
    first_steps = [str(item).strip() for item in onboarding.get("first_steps", []) if str(item).strip()]
    current_requirements = [str(item).strip() for item in onboarding.get("current_requirements", []) if str(item).strip()]
    if any(token in normalized for token in ("what is relaytic", "what's relaytic", "what does relaytic do")):
        return (
            f"{str(onboarding.get('what_relaytic_is') or 'Relaytic is a local-first structured-data research lab.').strip()} "
            f"It becomes useful after you point it to data and describe the goal."
        )
    if any(token in normalized for token in ("how do i start", "how to start", "first step", "get started", "/start")):
        step_text = " ".join(first_steps[:3]) or "Point Relaytic to a dataset and describe the goal."
        return f"Relaytic needs {', '.join(current_requirements[:2]) or 'data plus a goal'}. {step_text}"
    if any(token in normalized for token in ("show me a demo flow", "demo flow", "/demo", "what happens next")):
        demo_text = " ".join(guided_demo_flow[:4]) or "Run doctor, point Relaytic to data, create a run, and inspect mission control."
        return f"Here is the shortest useful demo path. {demo_text}"
    if any(token in normalized for token in ("data format", "formats", "/formats", "what data do you support")):
        return (
            "Relaytic supports local snapshot files like `.csv`, `.tsv`, `.xlsx`, `.xls`, `.parquet`, `.pq`, "
            "`.feather`, `.json`, `.jsonl`, and `.ndjson`. It also supports local stream-style sources "
            "materialized into snapshots and local lakehouse-style sources such as partitioned directories and DuckDB files."
        )
    if any(token in normalized for token in ("what do the modes mean", "/modes", "mode")):
        parts = [
            f"{str(item.get('name', 'Mode')).strip()}: {str(item.get('detail', '')).strip()}"
            for item in mode_explanations[:4]
            if str(item.get("name", "")).strip()
        ]
        return "Relaytic exposes different surfaces on purpose. " + (" ".join(parts) if parts else "Mission control is the dashboard, mission-control chat is for onboarding questions, assist is for run-specific help, and host mode is for Claude/Codex/OpenClaw style integration.")
    if any(token in normalized for token in ("i'm stuck", "im stuck", "stuck", "/stuck")):
        stuck_text = " ".join(stuck_guide[:4]) or "Run doctor, ask how to start, and let mission control explain the next safe step."
        return f"If you are stuck, do not guess. {stuck_text}"
    if any(token in normalized for token in ("why are some capabilities disabled", "capabilities disabled", "why disabled")):
        blocked = [
            item
            for item in capabilities
            if str(dict(item).get("status", "")).strip().lower() not in {"enabled", "ready", "ok"}
        ]
        if not blocked:
            return "Nothing important is blocked right now. Current capabilities are already available."
        top = blocked[:3]
        details = []
        for item in top:
            name = str(item.get("name", "capability")).strip() or "capability"
            reason = str(item.get("status_reason", "")).strip() or "Needs additional setup or run context."
            hint = str(item.get("activation_hint", "")).strip()
            details.append(f"{name}: {reason}" + (f" Next: {hint}" if hint else ""))
        return "A lot of the deeper capabilities are waiting on real run context rather than being broken. " + " ".join(details)
    if any(token in normalized for token in ("what can you do", "capabilities", "what are my options")):
        action_bits = ", ".join(
            f"`{str(item.get('title', '')).strip()}`" for item in actions[:4] if str(item.get("title", "")).strip()
        ) or "`Start With Data`"
        question_bits = ", ".join(
            f"`{str(item.get('question', '')).strip()}`" for item in questions[:4] if str(item.get("question", "")).strip()
        ) or "`what is relaytic?`"
        return (
            "Relaytic is a local-first structured-data research lab. It needs data plus a goal before the deeper run capabilities activate. "
            "Right now I can explain what Relaytic is, show you the first steps, describe supported data sources, "
            "explain why a capability needs setup, walk you through a short demo flow, explain what the modes mean, help you recover when you are stuck, and point you to local host integrations. "
            "If you paste a dataset path, I can also help you choose between a quick analysis-first pass for things like top signals or correlation review and the full governed modeling path. "
            f"Good next actions are {action_bits}. Good starter questions are {question_bits}. "
            f"This terminal chat lives at `{live_chat_command}`, while `relaytic mission-control launch` opens the dashboard. "
            "The role-specific guides live at `docs/handbooks/relaytic_user_handbook.md` and `docs/handbooks/relaytic_agent_handbook.md`, and the guided walkthrough lives at `docs/handbooks/relaytic_demo_walkthrough.md`."
        )
    if any(token in normalized for token in ("where is the handbook", "handbook", "what should an agent read first")):
        return (
            "Relaytic ships with two handbook paths. Human operators should start with "
            "`docs/handbooks/relaytic_user_handbook.md`, which explains what Relaytic is, what it needs, "
            "and how to navigate the control center. External agents should start with "
            "`docs/handbooks/relaytic_agent_handbook.md`, which is command-first and points directly to the key repo contracts and artifacts."
        )
    if any(token in normalized for token in ("claude", "codex", "openclaw", "mcp", "/hosts", "host")):
        discoverable = ", ".join(host_summary.get("discoverable_now", [])) or "none"
        activation = ", ".join(host_summary.get("requires_activation", [])) or "none"
        remote = ", ".join(host_summary.get("requires_public_https", [])) or "none"
        return (
            f"Relaytic stays local-first and can sit under familiar hosts. Discoverable locally now: `{discoverable}`. "
            f"Needs activation: `{activation}`. Needs public HTTPS: `{remote}`. "
            "Use `relaytic interoperability show` to see the exact next step for Claude, Codex, OpenClaw, or other MCP-style hosts."
        )
    return (
        "Relaytic is a local-first structured-data lab. It needs data plus a goal before deeper run capabilities activate. "
        "Ask `what is relaytic?`, `how do i start?`, `show me a demo flow`, `what do the modes mean?`, "
        "`i'm stuck, what should i do?`, or `why are some capabilities disabled?`."
    )


def _run_adaptive_onboarding_turn(
    *,
    message: str,
    mission_control_payload: dict[str, Any],
    output_dir: str | None,
    config_path: str | None,
    expected_profile: str,
) -> dict[str, Any]:
    from relaytic.intelligence import build_intelligence_controls_from_policy
    from relaytic.intelligence.backends import discover_backend
    from relaytic.mission_control import write_mission_control_artifact

    state_root = _resolve_mission_control_root(run_dir=None, output_dir=output_dir)
    state_root.mkdir(parents=True, exist_ok=True)
    policy = _load_mission_control_policy(run_dir=None, config_path=config_path)
    communication_cfg = dict(policy.get("communication", {}))
    if not bool(communication_cfg.get("adaptive_onboarding_chat_enabled", True)):
        return {
            "response_text": _onboarding_chat_response(message=message, mission_control_payload=mission_control_payload),
            "started_run_dir": None,
        }
    confirmation_required = bool(communication_cfg.get("adaptive_onboarding_confirmation_required", True))
    session_state = _read_onboarding_chat_session_state_from_payload(mission_control_payload)
    session_state.setdefault("schema_version", "relaytic.onboarding_chat_session_state.v1")
    session_state.setdefault("generated_at", datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    session_state.setdefault("status", "ready")
    session_state.setdefault("current_phase", "need_data")
    session_state.setdefault("suggested_run_dir", _suggested_onboarding_run_dir(policy=policy))
    session_state.setdefault("suggested_run_dir_reason", None)
    session_state.setdefault("next_expected_input", "dataset path")
    session_state.setdefault("turn_count", 0)
    configured_run_dir = _suggested_onboarding_run_dir(policy=policy)
    if _clean_text(session_state.get("suggested_run_dir")) in {None, "artifacts/demo", r"artifacts\demo"}:
        session_state["suggested_run_dir"] = configured_run_dir
    previous_suggested_run_dir = _clean_text(session_state.get("suggested_run_dir"))
    previous_suggested_run_dir_reason = _clean_text(session_state.get("suggested_run_dir_reason"))
    safe_run_dir, safe_reason = _resolve_safe_onboarding_run_dir(
        suggested_run_dir=previous_suggested_run_dir or configured_run_dir,
        state_root=state_root,
    )
    if (
        safe_reason is None
        and previous_suggested_run_dir_reason
        and previous_suggested_run_dir
        and previous_suggested_run_dir == safe_run_dir
        and previous_suggested_run_dir != configured_run_dir
    ):
        safe_reason = previous_suggested_run_dir_reason
    session_state["suggested_run_dir"] = safe_run_dir
    session_state["suggested_run_dir_reason"] = safe_reason
    session_state["turn_count"] = int(session_state.get("turn_count", 0) or 0) + 1
    session_state["last_user_message"] = message

    semantic_result = _extract_onboarding_semantics(
        message=message,
        session_state=session_state,
        policy=policy,
        config_path=config_path,
    )
    llm_status = str(semantic_result.get("backend_status") or "not_used")
    llm_model = _clean_text(semantic_result.get("model"))
    llm_used = bool(semantic_result.get("llm_used"))
    session_state["semantic_backend_status"] = llm_status
    session_state["semantic_model"] = llm_model
    session_state["llm_used_last_turn"] = llm_used

    current_data_path_before = _clean_text(session_state.get("detected_data_path"))
    current_incumbent_path_before = _clean_text(session_state.get("incumbent_path"))
    current_objective_before = _clean_text(session_state.get("detected_objective"))

    path_detection = _resolve_onboarding_data_path(
        message=message,
        semantic_result=semantic_result,
    )
    if path_detection["candidate"] is not None:
        session_state["detected_data_path"] = path_detection["candidate"]
        session_state["data_path_exists"] = path_detection["exists"]

    incumbent_detection = _resolve_onboarding_incumbent_path(
        message=message,
        semantic_result=semantic_result,
        current_data_path=_clean_text(session_state.get("detected_data_path")),
    )
    if incumbent_detection["candidate"] is not None:
        session_state["incumbent_path"] = incumbent_detection["candidate"]
        session_state["incumbent_path_exists"] = incumbent_detection["exists"]

    objective = _resolve_onboarding_objective(
        message=message,
        semantic_result=semantic_result,
        current_data_path=_clean_text(session_state.get("detected_data_path")),
        incumbent_path=_clean_text(session_state.get("incumbent_path")),
        current_objective=_clean_text(session_state.get("detected_objective")),
    )
    if objective is not None:
        session_state["detected_objective"] = objective
    objective_family = _classify_onboarding_objective_family(
        message=message,
        semantic_result=semantic_result,
        detected_objective=_clean_text(session_state.get("detected_objective")),
        incumbent_path=_clean_text(session_state.get("incumbent_path")),
        current_family=_clean_text(session_state.get("objective_family")),
    )
    if objective_family is not None:
        session_state["objective_family"] = objective_family
        if objective_family != "analysis":
            session_state["last_analysis_report_path"] = None
            session_state["last_analysis_summary"] = None

    if _looks_like_reset_request(message):
        session_state = _fresh_onboarding_chat_session_state(policy=policy)
        session_state["last_user_message"] = message
        session_state["semantic_backend_status"] = llm_status
        session_state["semantic_model"] = llm_model
        session_state["llm_used_last_turn"] = llm_used
        session_state["last_system_question"] = "Paste a dataset path or describe the goal."
        session_state["summary"] = "Relaytic cleared the captured onboarding state and is ready to start again."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": "I cleared the captured onboarding state. Paste a dataset path, describe the objective, or do both in one message.",
            "started_run_dir": None,
        }

    if _looks_like_state_request(message):
        _finalize_onboarding_session_state(session_state)
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": _render_onboarding_state_response(session_state=session_state),
            "started_run_dir": None,
        }

    if path_detection["candidate"] is not None and not path_detection["exists"]:
        session_state["current_phase"] = "need_valid_data"
        session_state["ready_to_start_run"] = False
        session_state["next_expected_input"] = "existing dataset path"
        session_state["last_system_question"] = "Please paste a dataset path that exists on this machine."
        session_state["notes"] = [f"Relaytic saw a path-like value but it does not exist: {path_detection['candidate']}"]
        session_state["summary"] = "Relaytic needs a valid local dataset path before it can start a run."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": f"I found a dataset path candidate, but it does not exist here: `{path_detection['candidate']}`. Paste the correct local path and I’ll keep going.",
            "started_run_dir": None,
        }

    if incumbent_detection["candidate"] is not None and not incumbent_detection["exists"]:
        session_state["notes"] = [f"Relaytic saw an incumbent path candidate but it does not exist: {incumbent_detection['candidate']}"]

    has_data = bool(_clean_text(session_state.get("detected_data_path"))) and bool(session_state.get("data_path_exists"))
    has_objective = bool(_clean_text(session_state.get("detected_objective")))
    wants_start = _looks_like_run_confirmation(message) or bool(semantic_result.get("confirm_start"))
    objective_family = _clean_text(session_state.get("objective_family")) or "governed_run"
    informational_response = _maybe_onboarding_chat_response(
        message=message,
        mission_control_payload=mission_control_payload,
    )
    message_updates_workflow = (
        (path_detection["candidate"] is not None and _clean_text(path_detection["candidate"]) != current_data_path_before)
        or (
            incumbent_detection["candidate"] is not None
            and _clean_text(incumbent_detection["candidate"]) != current_incumbent_path_before
        )
        or (objective is not None and _clean_text(objective) != current_objective_before)
        or wants_start
        or _looks_like_off_topic_detour(message)
    )

    if informational_response is not None and not message_updates_workflow:
        session_state["last_system_question"] = (
            "Relaytic answered an informational onboarding question without changing the captured workflow state."
        )
        existing_notes = [str(item).strip() for item in session_state.get("notes", []) if str(item).strip()]
        existing_notes.append("Relaytic answered an informational onboarding question without starting new work.")
        session_state["notes"] = existing_notes[-4:]
        if not _clean_text(session_state.get("summary")):
            session_state["summary"] = "Relaytic answered an onboarding question and kept the current onboarding state unchanged."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": informational_response,
            "started_run_dir": None,
        }

    if _looks_like_off_topic_detour(message):
        response_text = _render_off_topic_redirect_response(
            session_state=session_state,
            has_data=has_data,
            has_objective=has_objective,
        )
        _finalize_onboarding_session_state(session_state)
        session_state["last_system_question"] = (
            "Relaytic redirected an off-topic detour back to the current onboarding need."
        )
        existing_notes = [str(item).strip() for item in session_state.get("notes", []) if str(item).strip()]
        existing_notes.append("Relaytic ignored an off-topic detour and kept the onboarding state intact.")
        session_state["notes"] = existing_notes[-4:]
        session_state["summary"] = "Relaytic kept the onboarding state and redirected the conversation back to the dataset workflow."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": response_text,
            "started_run_dir": None,
        }

    if has_data and has_objective and objective_family == "analysis":
        analysis_payload = _run_direct_onboarding_analysis(
            data_path=str(session_state["detected_data_path"]),
            objective=str(session_state["detected_objective"]),
            config_path=config_path,
            output_dir=output_dir,
        )
        session_state["current_phase"] = "analysis_completed"
        session_state["ready_to_start_run"] = False
        session_state["created_run_dir"] = None
        session_state["last_analysis_report_path"] = analysis_payload.get("report_path")
        session_state["last_analysis_summary"] = analysis_payload.get("summary")
        session_state["next_expected_input"] = "optional follow-up objective"
        session_state["last_system_question"] = (
            "Ask for another analysis question or say that you want a governed model if you want Relaytic to start the full run."
        )
        session_state["notes"] = [
            "Relaytic handled this as a direct analysis-first request instead of forcing the full governed modeling path.",
            "If you now want a model, say so explicitly and Relaytic will switch to the governed run flow.",
        ]
        session_state["summary"] = "Relaytic completed a direct analysis-first pass without creating a governed run."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": analysis_payload["response_text"],
            "started_run_dir": None,
        }

    if has_data and has_objective and (wants_start or not confirmation_required):
        chosen_run_dir = str(
            Path(
                _clean_text(session_state.get("suggested_run_dir")) or _suggested_onboarding_run_dir(policy=policy)
            ).expanduser()
        )
        access_payload = _run_access_flow(
            run_dir=chosen_run_dir,
            data_path=str(session_state["detected_data_path"]),
            source_type="auto",
            source_table=None,
            sql_query=None,
            stream_window_rows=5000,
            stream_format="auto",
            materialized_format="auto",
            config_path=config_path,
            run_id=None,
            text=str(session_state["detected_objective"]),
            text_file=None,
            actor_type="operator",
            actor_name=None,
            channel="mission_control_chat",
            sheet_name=None,
            header_row=None,
            data_start_row=None,
            timestamp_column=None,
            overwrite=False,
            labels=None,
        )
        started_run_dir = str(access_payload["surface_payload"]["run_dir"])
        session_state["current_phase"] = "run_started"
        session_state["created_run_dir"] = started_run_dir
        session_state["ready_to_start_run"] = False
        session_state["next_expected_input"] = None
        session_state["last_system_question"] = "Relaytic created the run and switched into run-specific control."
        session_state["notes"] = ["Relaytic started the first governed run from onboarding chat after explicit confirmation."]
        session_state["summary"] = f"Relaytic created `{started_run_dir}` from the captured data path and objective."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": (
                f"I've started a governed run at `{started_run_dir}` using `{session_state['detected_data_path']}` "
                f"with objective `{session_state['detected_objective']}`. Mission control will now follow that run."
            ),
            "started_run_dir": started_run_dir,
        }

    if has_data and not has_objective:
        session_state["current_phase"] = "need_objective"
        session_state["ready_to_start_run"] = False
        session_state["next_expected_input"] = "objective"
        session_state["last_system_question"] = "What do you want to do with this dataset: a quick analysis first or a governed model/benchmark run?"
        session_state["notes"] = ["Relaytic captured a dataset path and is waiting for the objective."]
        session_state["summary"] = "Relaytic has a dataset path and now needs the plain-language objective."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": (
                f"I found a dataset path: `{session_state['detected_data_path']}`. "
                "It exists and looks usable. Do you want a quick analysis first, or should I start the full governed path for modeling, benchmarking, or comparison?"
            ),
            "started_run_dir": None,
        }

    if has_objective and not has_data:
        session_state["current_phase"] = "need_data"
        session_state["ready_to_start_run"] = False
        session_state["next_expected_input"] = "dataset path"
        session_state["last_system_question"] = "Please paste the dataset path you want Relaytic to use."
        session_state["notes"] = ["Relaytic captured the objective and is waiting for the dataset path."]
        session_state["summary"] = "Relaytic has an objective and now needs the dataset path."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {
            "response_text": (
                f"I understand the objective as `{session_state['detected_objective']}`. "
                "Now paste the dataset path you want me to use."
            ),
            "started_run_dir": None,
        }

    if has_data and has_objective:
        session_state["current_phase"] = "confirm_start"
        session_state["ready_to_start_run"] = True
        session_state["next_expected_input"] = "confirmation"
        session_state["last_system_question"] = "Should I start the run now?"
        notes = ["Relaytic has the data path and the objective and is waiting for confirmation."]
        incumbent_path = _clean_text(session_state.get("incumbent_path"))
        if incumbent_path and bool(session_state.get("incumbent_path_exists")):
            notes.append(f"An incumbent path was also captured: {incumbent_path}")
        session_state["notes"] = notes
        session_state["summary"] = "Relaytic is ready to start the first run once the human confirms."
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        extra = ""
        if incumbent_path and bool(session_state.get("incumbent_path_exists")):
            extra = f" I also noticed an incumbent path at `{incumbent_path}` and can compare against it after the run exists."
        return {
            "response_text": (
                f"I have both the data and the objective. Dataset: `{session_state['detected_data_path']}`. "
                f"Objective: `{session_state['detected_objective']}`. "
                f"Objective family: `{objective_family}`. "
                + (
                    f"The default run folder was already in use because {session_state['suggested_run_dir_reason']}, "
                    f"so I’ll create the governed run in `{session_state['suggested_run_dir']}` instead. "
                    if _clean_text(session_state.get("suggested_run_dir_reason"))
                    else f"I’ll use run directory `{session_state['suggested_run_dir']}` unless you want a different one. "
                )
                + (
                    f"Say `yes`, `start`, or `go` when you want me to create the run.{extra}"
                    if confirmation_required
                    else f"I am ready to create the run now.{extra}"
                )
            ),
            "started_run_dir": None,
        }

    faq_response = _maybe_onboarding_chat_response(message=message, mission_control_payload=mission_control_payload)
    if faq_response is not None:
        _finalize_onboarding_session_state(session_state)
        write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
        return {"response_text": faq_response, "started_run_dir": None}

    session_state["current_phase"] = "need_data"
    session_state["ready_to_start_run"] = False
    session_state["next_expected_input"] = "dataset path or objective"
    session_state["last_system_question"] = "Paste a dataset path, describe the objective, or ask for the demo flow."
    session_state["notes"] = [
        "Relaytic is waiting for a dataset path, a plain-language objective, or both in one message."
    ]
    session_state["summary"] = "Relaytic is waiting for the first useful onboarding input."
    write_mission_control_artifact(state_root, key="onboarding_chat_session_state", payload=session_state)
    return {
        "response_text": (
            "I can work with a pasted dataset path, a plain-language objective, or both in one messy message. "
            "For example: `C:\\data\\churn.csv`, `analyze this data and give me the top 3 signals`, "
            "or `predict customer churn from this file`."
        ),
        "started_run_dir": None,
    }


def _extract_onboarding_semantics(
    *,
    message: str,
    session_state: dict[str, Any],
    policy: dict[str, Any],
    config_path: str | None,
) -> dict[str, Any]:
    from relaytic.intelligence import build_intelligence_controls_from_policy
    from relaytic.intelligence.backends import discover_backend

    communication_cfg = dict(policy.get("communication", {}))
    if not bool(communication_cfg.get("adaptive_onboarding_semantic_assist", True)):
        return {"backend_status": "disabled", "llm_used": False}
    try:
        controls = build_intelligence_controls_from_policy(policy)
        controls = replace(
            controls,
            enabled=True,
            intelligence_mode="assist",
            prefer_local_llm=True,
            allow_frontier_llm=False,
            minimum_local_llm_enabled=True,
            minimum_local_llm_profile=(
                controls.minimum_local_llm_profile
                if str(controls.minimum_local_llm_profile).strip().lower() not in {"", "none"}
                else "small_cpu"
            ),
        )
        discovery = discover_backend(controls=controls, config_path=config_path)
        if discovery.advisor is None:
            return {
                "backend_status": discovery.status,
                "model": discovery.resolved_model,
                "llm_used": False,
            }
        result = discovery.advisor.complete_json(
            task_name="mission_control_onboarding",
            system_prompt=(
                "You are Relaytic's bounded onboarding extractor. "
                "Return only JSON with keys: intent, data_path, objective, objective_family, incumbent_path, confirm_start, wants_reset, question_focus, confidence. "
                "Extract useful structured hints from messy human input, but do not invent file paths. "
                "If the message is mostly a question, keep data_path and objective null unless clearly stated. "
                "objective_family should be one of analysis, governed_run, benchmark, or prediction when you can tell."
            ),
            payload={
                "message": message,
                "current_phase": session_state.get("current_phase"),
                "captured_data_path": session_state.get("detected_data_path"),
                "captured_objective": session_state.get("detected_objective"),
                "captured_incumbent_path": session_state.get("incumbent_path"),
                "next_expected_input": session_state.get("next_expected_input"),
            },
        )
        if result.status != "ok" or not isinstance(result.payload, dict):
            return {
                "backend_status": discovery.status if result.status == "ok" else result.status,
                "model": discovery.resolved_model,
                "llm_used": False,
            }
        payload = dict(result.payload)
        payload["backend_status"] = discovery.status
        payload["model"] = discovery.resolved_model
        payload["llm_used"] = True
        return payload
    except Exception as exc:
        return {
            "backend_status": "error",
            "model": None,
            "llm_used": False,
            "notes": [str(exc)],
        }


def _classify_onboarding_objective_family(
    *,
    message: str,
    semantic_result: dict[str, Any],
    detected_objective: str | None,
    incumbent_path: str | None,
    current_family: str | None,
) -> str | None:
    semantic_family = _normalize_objective_family(semantic_result.get("objective_family"))
    if semantic_family is not None:
        return semantic_family
    objective_text = _clean_text(detected_objective) or _clean_text(message)
    if not objective_text:
        return current_family
    normalized = " ".join(objective_text.lower().split())
    explicit_modeling = _looks_like_explicit_modeling_request(normalized)
    if incumbent_path and any(token in normalized for token in ("benchmark", "compare", "beat", "evaluate", "incumbent", "baseline")):
        return "benchmark"
    if _looks_like_analysis_objective(normalized) and not explicit_modeling:
        return "analysis"
    if any(token in normalized for token in ("predict on", "score these rows", "run inference", "predict these")):
        return "prediction"
    if explicit_modeling or _looks_like_modeling_objective(normalized):
        return "governed_run"
    return current_family or "governed_run"


def _normalize_objective_family(value: Any) -> str | None:
    normalized = _clean_text(value)
    if normalized is None:
        return None
    normalized = normalized.lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "analysis_only": "analysis",
        "analysis_first": "analysis",
        "exploration": "analysis",
        "exploratory_analysis": "analysis",
        "explore": "analysis",
        "model": "governed_run",
        "modeling": "governed_run",
        "governed_modeling": "governed_run",
        "governed_run": "governed_run",
        "benchmark": "benchmark",
        "comparison": "benchmark",
        "prediction": "prediction",
        "inference": "prediction",
    }
    resolved = aliases.get(normalized, normalized)
    if resolved in {"analysis", "governed_run", "benchmark", "prediction"}:
        return resolved
    return None


def _looks_like_analysis_objective(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    analysis_tokens = (
        "analyze",
        "analysis",
        "explore",
        "exploration",
        "correlation",
        "correlations",
        "top 3",
        "top three",
        "top signals",
        "top predictors",
        "find signals",
        "important signals",
        "inspect this data",
        "look at this data",
        "understand this dataset",
    )
    return any(token in normalized for token in analysis_tokens)


def _looks_like_modeling_objective(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    modeling_tokens = (
        "predict",
        "prediction",
        "classify",
        "classification",
        "forecast",
        "regression",
        "detect",
        "detection",
        "identify",
        "estimate",
        "score",
        "rank",
        "segment",
        "evaluate",
        "beat",
        "benchmark",
        "diagnosis",
        "churn",
        "fraud",
        "default",
        "failure",
        "target",
        "malignant",
        "benign",
        "disease",
        "customer",
        "build a model",
        "train a model",
        "model for",
    )
    return any(token in normalized for token in modeling_tokens)


def _looks_like_explicit_modeling_request(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    explicit_tokens = (
        "predict",
        "prediction",
        "classify",
        "classification",
        "forecast",
        "regression",
        "detect",
        "detection",
        "identify",
        "estimate",
        "score",
        "rank",
        "segment",
        "evaluate",
        "beat",
        "benchmark",
        "build a model",
        "train a model",
        "model for",
    )
    return any(token in normalized for token in explicit_tokens)


def _run_direct_onboarding_analysis(
    *,
    data_path: str,
    objective: str,
    config_path: str | None,
    output_dir: str | None,
) -> dict[str, Any]:
    try:
        registry = build_default_registry()
        task_type_hint = _infer_analysis_task_type_hint(objective)
        tool_args: dict[str, Any] = {
            "data_path": data_path,
            "save_artifacts": True,
            "save_report": True,
            "enable_strategy_search": True,
            "strategy_search_candidates": 3,
        }
        if task_type_hint is not None:
            tool_args["task_type_hint"] = task_type_hint
        result = registry.execute("run_agent1_analysis", tool_args)
        output = result.output if isinstance(result.output, dict) else {}
    except Exception as exc:
        message = str(exc).strip() or "The direct analysis-first path raised an unexpected error."
        return {
            "report_path": None,
            "summary": "Relaytic could not complete the direct analysis-first request.",
            "response_text": (
                "I understood this as a quick analysis-first request, but the analysis path did not complete successfully. "
                f"{message} If you want, we can still switch to the full governed run path."
            ),
        }
    if result.status != "ok" or not isinstance(output, dict):
        message = str(output.get("message") or f"Direct analysis failed with status `{result.status}`.").strip()
        return {
            "report_path": None,
            "summary": "Relaytic could not complete the direct analysis-first request.",
            "response_text": (
                "I understood this as a quick analysis-first request, but the analysis path did not complete successfully. "
                f"{message} If you want, we can still switch to the full governed run path."
            ),
        }
    summary = _summarize_direct_analysis_output(output=output)
    report_path = _clean_text(output.get("report_path"))
    report_detail = f" Report saved at `{report_path}`." if report_path else ""
    return {
        "report_path": report_path,
        "summary": summary,
        "response_text": (
            f"I ran a direct analysis-first pass on `{data_path}` instead of forcing the full governed modeling path. "
            f"{summary}.{report_detail} If you want, the next step can be a governed model run on the same data."
        ),
    }


def _infer_analysis_task_type_hint(objective: str) -> str | None:
    normalized = " ".join(str(objective).strip().lower().split())
    if "fraud" in normalized:
        return "fraud_detection"
    if "anomaly" in normalized or "outlier" in normalized:
        return "anomaly_detection"
    if any(token in normalized for token in ("regression", "forecast", "estimate")):
        return "regression"
    if any(token in normalized for token in ("multiclass", "three classes", "multiple classes")):
        return "multiclass_classification"
    if any(token in normalized for token in ("classify", "classification", "diagnosis", "malignant", "benign", "churn")):
        return "binary_classification"
    return None


def _summarize_direct_analysis_output(*, output: dict[str, Any]) -> str:
    ranking = [dict(item) for item in output.get("ranking", []) if isinstance(item, dict)]
    target_analyses = [
        dict(item)
        for item in output.get("correlations", {}).get("target_analyses", [])
        if isinstance(item, dict)
    ]
    top_signals = [
        str(item.get("target_signal", "")).strip()
        for item in ranking[:3]
        if str(item.get("target_signal", "")).strip()
    ]
    if not top_signals:
        top_signals = [
            str(item.get("target_signal", "")).strip()
            for item in target_analyses[:3]
            if str(item.get("target_signal", "")).strip()
        ]
    if target_analyses:
        primary_target = target_analyses[0]
        predictors = list(primary_target.get("top_predictors") or [])
        predictor_text = ", ".join(f"`{item}`" for item in predictors[:3] if str(item).strip()) or "no strong predictors surfaced yet"
        target_name = str(primary_target.get("target_signal", "the leading target")).strip() or "the leading target"
        signal_text = ", ".join(f"`{item}`" for item in top_signals[:3]) if top_signals else "no ranked signals yet"
        return (
            f"Top candidate signals: {signal_text}. "
            f"For `{target_name}`, the strongest predictors were {predictor_text}"
        )
    if top_signals:
        signal_text = ", ".join(f"`{item}`" for item in top_signals[:3])
        return f"Top candidate signals: {signal_text}"
    return "Relaytic completed the quick analysis, but there were no strong ranked signal candidates to summarize yet"


def _resolve_onboarding_data_path(
    *,
    message: str,
    semantic_result: dict[str, Any],
) -> dict[str, Any]:
    semantic_candidate = _clean_text(semantic_result.get("data_path"))
    candidates = []
    if semantic_candidate:
        candidates.append(semantic_candidate)
    candidates.extend(_extract_path_candidates(message))
    seen: set[str] = set()
    for candidate in candidates:
        normalized = candidate.strip().strip("\"'").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        path = Path(normalized).expanduser()
        if path.exists():
            return {"candidate": str(path), "exists": True}
    for candidate in candidates:
        normalized = candidate.strip().strip("\"'").strip()
        if _looks_like_path(normalized):
            return {"candidate": normalized, "exists": False}
    return {"candidate": None, "exists": None}


def _resolve_onboarding_incumbent_path(
    *,
    message: str,
    semantic_result: dict[str, Any],
    current_data_path: str | None,
) -> dict[str, Any]:
    semantic_candidate = _clean_text(semantic_result.get("incumbent_path"))
    if semantic_candidate:
        path = Path(semantic_candidate).expanduser()
        if current_data_path and str(path) == str(current_data_path):
            return {"candidate": None, "exists": None}
        return {"candidate": str(path), "exists": path.exists()}
    lowered = " ".join(message.lower().split())
    if "incumbent" not in lowered and "baseline" not in lowered and "existing model" not in lowered:
        return {"candidate": None, "exists": None}
    for candidate in _extract_path_candidates(message):
        normalized = candidate.strip().strip("\"'").strip()
        if current_data_path and normalized == current_data_path:
            continue
        path = Path(normalized).expanduser()
        return {"candidate": str(path), "exists": path.exists()}
    return {"candidate": None, "exists": None}


def _resolve_onboarding_objective(
    *,
    message: str,
    semantic_result: dict[str, Any],
    current_data_path: str | None,
    incumbent_path: str | None,
    current_objective: str | None,
) -> str | None:
    semantic_objective = _clean_text(semantic_result.get("objective"))
    if semantic_objective:
        return semantic_objective
    cleaned = str(message)
    for candidate in _extract_path_candidates(message):
        cleaned = cleaned.replace(candidate, " ")
    if current_data_path:
        cleaned = cleaned.replace(current_data_path, " ")
    if incumbent_path:
        cleaned = cleaned.replace(incumbent_path, " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;:-")
    normalized = " ".join(cleaned.lower().split())
    if not normalized:
        return current_objective
    if _looks_like_question(cleaned) and not _looks_like_objective(cleaned):
        return current_objective
    if _looks_like_objective(cleaned):
        return cleaned
    if current_data_path and len(cleaned.split()) >= 3 and not normalized.startswith("/"):
        return cleaned
    return current_objective


def _extract_path_candidates(message: str) -> list[str]:
    raw = str(message).strip()
    candidates: list[str] = []
    whole = raw.strip("\"'")
    whole_path = Path(whole).expanduser() if whole else None
    if whole and (whole_path.exists() or (len(whole.split()) == 1 and _looks_like_path(whole))):
        candidates.append(whole)
    quoted = re.findall(r"['\"]([^'\"]+)['\"]", raw)
    candidates.extend(item for item in quoted if item.strip())
    tokens = re.split(r"\s+", raw)
    for token in tokens:
        cleaned = token.strip().strip("\"'`,;()[]{}")
        if cleaned:
            candidates.append(cleaned)
    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = candidate.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        if _looks_like_path(normalized):
            result.append(normalized)
    return result


def _looks_like_path(candidate: str) -> bool:
    text = str(candidate).strip()
    if not text:
        return False
    if text.startswith("~"):
        return True
    if re.match(r"^[A-Za-z]:[\\/]", text):
        return True
    if text.startswith("/") or text.startswith("./") or text.startswith("../"):
        return True
    if "\\" in text or "/" in text:
        suffix = Path(text).suffix.lower()
        return bool(suffix) or Path(text).name.lower() in {"duckdb"}
    suffix = Path(text).suffix.lower()
    return suffix in {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".pq", ".feather", ".json", ".jsonl", ".ndjson", ".duckdb", ".pkl", ".joblib"}


def _looks_like_question(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    if not normalized:
        return False
    if normalized.endswith("?"):
        return True
    return normalized.startswith(("what ", "why ", "how ", "can ", "should ", "could ", "where ", "when "))


def _looks_like_objective(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    return _looks_like_modeling_objective(normalized) or _looks_like_analysis_objective(normalized)


def _looks_like_run_confirmation(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    if not normalized:
        return False
    confirmations = {
        "yes",
        "y",
        "start",
        "go",
        "continue",
        "run it",
        "do it",
        "sounds good",
        "looks good",
        "okay",
        "ok",
        "please start",
        "start it",
    }
    return normalized in confirmations


def _looks_like_off_topic_detour(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    return any(
        token in normalized
        for token in (
            "weather",
            "temperature outside",
            "is it raining",
            "what time is it",
            "tell me a joke",
            "do you like",
        )
    )


def _render_off_topic_redirect_response(
    *,
    session_state: dict[str, Any],
    has_data: bool,
    has_objective: bool,
) -> str:
    data_path = _clean_text(session_state.get("detected_data_path"))
    objective = _clean_text(session_state.get("detected_objective"))
    suggested_run_dir = _clean_text(session_state.get("suggested_run_dir")) or "artifacts/demo"
    if has_data and has_objective:
        return (
            "I’m here to help with the Relaytic workflow rather than general side questions. "
            f"I still have dataset `{data_path}` and objective `{objective}`. "
            f"If you want, say `yes`, `start`, or `go` and I’ll create the run in `{suggested_run_dir}`, "
            "or tell me what you want changed."
        )
    if has_data:
        return (
            "I’m here to help with the Relaytic workflow rather than general side questions. "
            f"I still have dataset `{data_path}` captured. "
            "Now tell me the goal, for example `analyze this first`, `give me the top 3 signals`, or `build a fraud model`."
        )
    if has_objective:
        return (
            "I’m here to help with the Relaytic workflow rather than general side questions. "
            f"I still have the objective `{objective}`. "
            "Now paste the dataset path you want Relaytic to use."
        )
    return (
        "I’m here to help with the Relaytic workflow rather than general side questions. "
        "Paste a dataset path, describe the goal, or do both in one message and I’ll keep going."
    )


def _looks_like_reset_request(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    return normalized in {"/reset", "reset", "start over", "clear this", "clear state"}


def _looks_like_state_request(message: str) -> bool:
    normalized = " ".join(str(message).strip().lower().split())
    return normalized in {"/state", "state", "what do you have", "what have you captured", "show state"}


def _paths_equivalent(left: Path, right: Path) -> bool:
    try:
        return left.resolve(strict=False) == right.resolve(strict=False)
    except OSError:
        return str(left.absolute()) == str(right.absolute())


def _contains_onboarding_or_mission_control_state(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    state_filenames = {
        "assist_session_state.json",
        "mission_control_state.json",
        "review_queue_state.json",
        "control_center_layout.json",
        "onboarding_status.json",
        "onboarding_chat_session_state.json",
        "install_experience_report.json",
        "launch_manifest.json",
        "demo_session_manifest.json",
        "ui_preferences.json",
    }
    if any((path / filename).exists() for filename in state_filenames):
        return True
    return (path / "reports" / "mission_control.html").exists()


def _next_available_onboarding_run_dir(*, preferred: Path, state_root: Path) -> Path:
    base_candidate = preferred.parent / f"{preferred.name}_run"
    candidate = base_candidate
    index = 2
    while _paths_equivalent(candidate, state_root) or candidate.exists():
        candidate = preferred.parent / f"{base_candidate.name}_{index}"
        index += 1
    return candidate


def _resolve_safe_onboarding_run_dir(
    *,
    suggested_run_dir: str | Path,
    state_root: Path,
) -> tuple[str, str | None]:
    preferred = Path(suggested_run_dir).expanduser()
    reason: str | None = None
    if _paths_equivalent(preferred, state_root):
        reason = "the current mission-control folder is already storing onboarding state"
    elif preferred.exists() and preferred.is_file():
        reason = "that path already exists as a file"
    elif _contains_onboarding_or_mission_control_state(preferred):
        reason = "that folder is already storing onboarding or mission-control state"
    elif preferred.exists() and preferred.is_dir():
        try:
            has_any_contents = any(preferred.iterdir())
        except OSError:
            has_any_contents = True
        if has_any_contents:
            reason = "that folder already contains existing artifacts"
    if reason is None:
        return str(preferred), None
    return str(_next_available_onboarding_run_dir(preferred=preferred, state_root=state_root)), reason


def _suggested_onboarding_run_dir(*, policy: dict[str, Any]) -> str:
    communication_cfg = dict(policy.get("communication", {}))
    configured = _clean_text(communication_cfg.get("adaptive_onboarding_default_run_dir"))
    return str(Path(configured).expanduser()) if configured else str(Path("artifacts") / "demo")


def _fresh_onboarding_chat_session_state(*, policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "relaytic.onboarding_chat_session_state.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready",
        "current_phase": "need_data",
        "detected_data_path": None,
        "data_path_exists": None,
        "detected_objective": None,
        "objective_family": None,
        "incumbent_path": None,
        "incumbent_path_exists": None,
        "suggested_run_dir": _suggested_onboarding_run_dir(policy=policy),
        "suggested_run_dir_reason": None,
        "ready_to_start_run": False,
        "created_run_dir": None,
        "last_analysis_report_path": None,
        "last_analysis_summary": None,
        "next_expected_input": "dataset path",
        "last_user_message": None,
        "last_system_question": None,
        "semantic_backend_status": "not_checked",
        "semantic_model": None,
        "llm_used_last_turn": False,
        "turn_count": 0,
        "notes": [],
        "summary": "Relaytic is waiting for the first useful onboarding input.",
    }


def _finalize_onboarding_session_state(session_state: dict[str, Any]) -> None:
    has_data = bool(_clean_text(session_state.get("detected_data_path"))) and bool(session_state.get("data_path_exists"))
    has_objective = bool(_clean_text(session_state.get("detected_objective")))
    objective_family = _clean_text(session_state.get("objective_family")) or "governed_run"
    if has_data and has_objective and objective_family == "analysis":
        session_state["current_phase"] = "analysis_ready"
        session_state["ready_to_start_run"] = False
        session_state["next_expected_input"] = "analysis request or model request"
        session_state["summary"] = "Relaytic has the data path and an analysis-first objective and can run a direct exploratory pass immediately."
    elif has_data and has_objective:
        session_state["current_phase"] = "confirm_start"
        session_state["ready_to_start_run"] = True
        session_state["next_expected_input"] = "confirmation"
        session_state["summary"] = "Relaytic has both the data path and the objective and is waiting for confirmation."
    elif has_data:
        session_state["current_phase"] = "need_objective"
        session_state["ready_to_start_run"] = False
        session_state["next_expected_input"] = "objective"
        session_state["summary"] = "Relaytic has a data path and is waiting for the objective."
    elif has_objective:
        session_state["current_phase"] = "need_data"
        session_state["ready_to_start_run"] = False
        session_state["next_expected_input"] = "dataset path"
        session_state["summary"] = "Relaytic has an objective and is waiting for the dataset path."
    else:
        session_state["current_phase"] = "need_data"
        session_state["ready_to_start_run"] = False
        session_state["next_expected_input"] = "dataset path or objective"
        session_state["summary"] = "Relaytic is waiting for the first useful onboarding input."


def _render_onboarding_state_response(*, session_state: dict[str, Any]) -> str:
    data_path = _clean_text(session_state.get("detected_data_path")) or "none yet"
    objective = _clean_text(session_state.get("detected_objective")) or "none yet"
    objective_family = _clean_text(session_state.get("objective_family")) or "none yet"
    next_expected = _clean_text(session_state.get("next_expected_input")) or "dataset path or objective"
    suggested_run_dir = _clean_text(session_state.get("suggested_run_dir")) or r"artifacts\demo"
    suggested_run_dir_reason = _clean_text(session_state.get("suggested_run_dir_reason"))
    analysis_summary = _clean_text(session_state.get("last_analysis_summary"))
    return (
        f"So far I have data path `{data_path}`, objective `{objective}`, and objective family `{objective_family}`. "
        f"The next thing I need is `{next_expected}`. "
        + (
            f"The last direct analysis summary is: {analysis_summary}. "
            if analysis_summary
            else ""
        )
        + (
            f"The default run folder was already in use because {suggested_run_dir_reason}, so I’ll create the governed run in `{suggested_run_dir}` unless you want a different one."
            if suggested_run_dir_reason
            else f"If we get to the governed run path, I’ll use run directory `{suggested_run_dir}` unless you want a different one."
        )
    )


def _read_onboarding_chat_session_state_from_payload(mission_control_payload: dict[str, Any]) -> dict[str, Any]:
    bundle = dict(mission_control_payload.get("surface_payload", {}).get("bundle", {}))
    existing = dict(bundle.get("onboarding_chat_session_state", {}))
    return existing if existing else {}


def _show_event_bus_surface(*, run_dir: str | Path, config_path: str | None) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    _ensure_runtime_present(root)
    policy = _load_mission_control_policy(run_dir=str(root), config_path=config_path)
    review = run_event_bus_review(run_dir=root, policy=policy)
    bundle = review.bundle.to_dict()
    dispatch = dict(bundle.get("hook_dispatch_report", {}))
    subscriptions = dict(bundle.get("event_subscription_registry", {}))
    schema = dict(bundle.get("event_schema", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "events": {
                "event_type_count": schema.get("event_type_count"),
                "subscription_count": subscriptions.get("subscription_count"),
                "dispatch_count": dispatch.get("dispatch_count"),
                "observed_event_count": dispatch.get("observed_event_count"),
                "source_of_truth_preserved": dispatch.get("source_of_truth_preserved"),
            },
            "bundle": bundle,
        },
        "human_output": review.review_markdown,
    }


def _show_permission_surface(*, run_dir: str | Path, config_path: str | None) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    _ensure_runtime_present(root)
    policy = _load_mission_control_policy(run_dir=str(root), config_path=config_path)
    review = run_permission_review(run_dir=root, policy=policy)
    bundle = review.bundle.to_dict()
    mode = dict(bundle.get("permission_mode", {}))
    approval = dict(bundle.get("approval_policy_report", {}))
    contract = dict(bundle.get("session_capability_contract", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "permissions": {
                "current_mode": mode.get("current_mode"),
                "mode_source": mode.get("mode_source"),
                "pending_approval_count": approval.get("pending_approval_count"),
                "approval_requested_count": approval.get("approval_requested_count"),
                "denied_count": approval.get("denied_count"),
                "allowed_action_count": contract.get("allowed_action_count"),
                "approval_gated_action_count": contract.get("approval_gated_action_count"),
                "blocked_action_count": contract.get("blocked_action_count"),
            },
            "bundle": bundle,
        },
        "human_output": review.review_markdown,
    }


def _check_permission_surface(
    *,
    run_dir: str | Path,
    action_id: str,
    config_path: str | None,
    mode: str | None,
    actor_type: str,
    actor_name: str | None,
) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    _ensure_runtime_present(root)
    policy = _load_mission_control_policy(run_dir=str(root), config_path=config_path)
    result = evaluate_permission_action(
        run_dir=root,
        action_id=action_id,
        policy=policy,
        mode_override=mode,
        actor_type=actor_type,
        actor_name=actor_name,
        source_surface="cli",
        source_command="relaytic permissions check",
    )
    bundle = result.bundle.to_dict()
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "decision": result.decision,
            "permissions": dict(bundle.get("permission_mode", {})),
            "approval_policy": dict(bundle.get("approval_policy_report", {})),
            "bundle": bundle,
        },
        "human_output": result.review_markdown,
    }


def _decide_permission_surface(
    *,
    run_dir: str | Path,
    request_id: str,
    decision: str,
    config_path: str | None,
    actor_type: str,
    actor_name: str | None,
) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    _ensure_runtime_present(root)
    policy = _load_mission_control_policy(run_dir=str(root), config_path=config_path)
    result = apply_permission_decision(
        run_dir=root,
        request_id=request_id,
        decision=decision,
        policy=policy,
        actor_type=actor_type,
        actor_name=actor_name,
        source_surface="cli",
        source_command="relaytic permissions decide",
    )
    bundle = result.bundle.to_dict()
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "decision": result.decision,
            "permissions": dict(bundle.get("permission_mode", {})),
            "approval_policy": dict(bundle.get("approval_policy_report", {})),
            "bundle": bundle,
        },
        "human_output": result.review_markdown,
    }


def _show_runtime_surface(*, run_dir: str | Path, limit: int = 20) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    _ensure_runtime_present(root)
    sync_materialization_runtime_artifacts(root)
    payload = build_runtime_surface(run_dir=root, event_limit=limit)
    return {
        "surface_payload": payload,
        "human_output": render_runtime_markdown(payload),
    }


def _show_runtime_events(*, run_dir: str | Path, limit: int = 20) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    _ensure_runtime_present(root)
    payload = build_runtime_events_surface(run_dir=root, limit=limit)
    return {
        "surface_payload": payload,
        "human_output": render_runtime_events_markdown(payload),
    }


def _show_runtime_reuse_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    _ensure_runtime_present(root)
    payload = build_materialization_surface(run_dir=root)
    return {
        "surface_payload": payload,
        "human_output": render_materialization_markdown(payload),
    }


def _show_mission_control_surface(
    *,
    run_dir: str | None,
    output_dir: str | None,
    config_path: str | None,
    expected_profile: str,
) -> dict[str, Any]:
    from relaytic.mission_control import write_mission_control_bundle

    state_root = _resolve_mission_control_root(run_dir=run_dir, output_dir=output_dir)
    policy = _load_mission_control_policy(run_dir=run_dir, config_path=config_path)
    review = run_mission_control_review(
        root_dir=state_root,
        run_dir=run_dir,
        expected_profile=expected_profile,
        policy=policy,
        browser_requested=False,
        browser_opened=False,
    )
    written = write_mission_control_bundle(
        state_root,
        bundle=review.bundle,
        html_report=review.html_report,
    )
    manifest_path = _refresh_mission_control_manifest(state_root)
    bundle = review.bundle.to_dict()
    state = dict(bundle.get("mission_control_state", {}))
    queue = dict(bundle.get("review_queue_state", {}))
    modes = dict(bundle.get("mode_overview", {}))
    capabilities = dict(bundle.get("capability_manifest", {}))
    affordances = dict(bundle.get("action_affordances", {}))
    navigator = dict(bundle.get("stage_navigator", {}))
    questions = dict(bundle.get("question_starters", {}))
    onboarding = dict(bundle.get("onboarding_status", {}))
    launch = dict(bundle.get("launch_manifest", {}))
    onboarding_session = dict(bundle.get("onboarding_chat_session_state", {}))
    branch_dag = dict(bundle.get("branch_dag", {}))
    confidence_map = dict(bundle.get("confidence_map", {}))
    change_attribution = dict(bundle.get("change_attribution_report", {}))
    trace_explorer = dict(bundle.get("trace_explorer_state", {}))
    branch_replay = dict(bundle.get("branch_replay_index", {}))
    approval_timeline = dict(bundle.get("approval_timeline", {}))
    background_jobs = dict(bundle.get("background_job_view", {}))
    permission_mode_card = dict(bundle.get("permission_mode_card", {}))
    release_health = dict(bundle.get("release_health_report", {}))
    demo_pack = dict(bundle.get("demo_pack_manifest", {}))
    demo_scorecard = dict(bundle.get("flagship_demo_scorecard", {}))
    human_factors = dict(bundle.get("human_factors_eval_report", {}))
    onboarding_success = dict(bundle.get("onboarding_success_report", {}))
    pulse = read_run_summary(run_dir).get("pulse", {}) if run_dir is not None else {}
    pulse = dict(pulse) if isinstance(pulse, dict) else {}
    summary_payload = read_run_summary(run_dir) if run_dir is not None else {}
    permissions = dict(summary_payload.get("permissions", {})) if isinstance(summary_payload, dict) else {}
    event_bus = dict(summary_payload.get("event_bus", {})) if isinstance(summary_payload, dict) else {}
    remote = dict(summary_payload.get("remote", {})) if isinstance(summary_payload, dict) else {}
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(run_dir) if run_dir is not None else None,
            "state_dir": str(state_root),
            "manifest_path": str(manifest_path),
            "paths": {key: str(value) for key, value in written.items()},
            "mission_control": {
                "current_stage": state.get("current_stage"),
                "recommended_action": state.get("recommended_action"),
                "review_required": state.get("review_required"),
                "next_actor": state.get("next_actor"),
                "card_count": state.get("card_count"),
                "capability_count": state.get("capability_count"),
                "action_count": state.get("action_count"),
                "question_count": state.get("question_count"),
                "review_queue_pending_count": queue.get("pending_count"),
                "intelligence_mode": modes.get("intelligence_effective_mode"),
                "autonomy_mode": modes.get("autonomy_mode"),
                "can_rerun_stage": navigator.get("can_rerun_stage"),
                "navigation_scope": navigator.get("navigation_scope"),
                "launch_ready": onboarding.get("launch_ready"),
                "doctor_status": onboarding.get("doctor_status"),
                "needs_data": onboarding.get("needs_data"),
                "live_chat_command": onboarding.get("live_chat_command"),
                "captured_data_path": onboarding_session.get("detected_data_path"),
                "captured_objective": onboarding_session.get("detected_objective"),
                "objective_family": onboarding_session.get("objective_family"),
                "next_expected_input": onboarding_session.get("next_expected_input"),
                "onboarding_semantic_status": onboarding_session.get("semantic_backend_status"),
                "last_analysis_summary": onboarding_session.get("last_analysis_summary"),
                "last_analysis_report_path": onboarding_session.get("last_analysis_report_path"),
                "html_report_path": launch.get("html_report_path"),
                "capability_manifest_status": capabilities.get("status"),
                "action_affordances_status": affordances.get("status"),
                "question_starters_status": questions.get("status"),
                "pulse_status": pulse.get("status"),
                "pulse_mode": pulse.get("mode"),
                "pulse_queued_action_count": pulse.get("queued_action_count"),
                "permission_mode": permissions.get("current_mode"),
                "pending_approval_count": permissions.get("pending_approval_count"),
                "remote_status": remote.get("status"),
                "remote_transport_kind": remote.get("transport_kind"),
                "remote_pending_approval_count": remote.get("pending_approval_count"),
                "remote_current_supervisor_type": remote.get("current_supervisor_type"),
                "event_subscription_count": event_bus.get("subscription_count"),
                "event_dispatch_count": event_bus.get("dispatch_count"),
                "workspace_id": dict(summary_payload.get("workspace", {})).get("workspace_id"),
                "workspace_label": dict(summary_payload.get("workspace", {})).get("workspace_label"),
                "overall_confidence": confidence_map.get("overall_confidence"),
                "review_need": confidence_map.get("review_need"),
                "unresolved_count": confidence_map.get("unresolved_count"),
                "branch_count": branch_dag.get("branch_count"),
                "active_branch_id": branch_dag.get("active_branch_id"),
                "trace_winning_action": trace_explorer.get("winning_action"),
                "trace_replay_count": branch_replay.get("replay_count"),
                "primary_change_driver": change_attribution.get("primary_driver"),
                "latest_approval_decision": approval_timeline.get("latest_decision"),
                "background_job_count": background_jobs.get("job_count"),
                "resumable_job_count": background_jobs.get("resumable_job_count"),
                "permission_mode_source": permission_mode_card.get("mode_source"),
                "release_health_status": release_health.get("status"),
                "safe_to_hand_out_publicly": release_health.get("safe_to_hand_out_publicly"),
                "demo_ready_count": demo_pack.get("ready_demo_count"),
                "demo_story_count": demo_pack.get("demo_count"),
                "current_demo_story": demo_scorecard.get("current_run_story"),
                "current_run_qualifies_demo": demo_scorecard.get("current_run_qualifies"),
                "first_run_success_ready": human_factors.get("first_run_success_ready"),
                "onboarding_ready_for_first_time_user": onboarding_success.get("ready_for_first_time_user"),
            },
            "bundle": bundle,
        },
        "human_output": review.review_markdown,
    }


def _launch_mission_control_surface(
    *,
    run_dir: str | None,
    output_dir: str | None,
    config_path: str | None,
    expected_profile: str,
    open_browser: bool,
) -> dict[str, Any]:
    from relaytic.mission_control import write_mission_control_artifact, write_mission_control_bundle

    state_root = _resolve_mission_control_root(run_dir=run_dir, output_dir=output_dir)
    policy = _load_mission_control_policy(run_dir=run_dir, config_path=config_path)
    review = run_mission_control_review(
        root_dir=state_root,
        run_dir=run_dir,
        expected_profile=expected_profile,
        policy=policy,
        browser_requested=open_browser,
        browser_opened=False,
    )
    written = write_mission_control_bundle(
        state_root,
        bundle=review.bundle,
        html_report=review.html_report,
    )
    report_path = written["mission_control_report"]
    browser_opened = False
    if open_browser:
        try:
            browser_opened = bool(webbrowser.open(report_path.resolve().as_uri()))
        except Exception:
            browser_opened = False
    bundle = review.bundle.to_dict()
    launch_payload = dict(bundle.get("launch_manifest", {}))
    launch_payload["browser_requested"] = open_browser
    launch_payload["browser_opened"] = browser_opened
    write_mission_control_artifact(state_root, key="launch_manifest", payload=launch_payload)
    bundle["launch_manifest"] = launch_payload
    manifest_path = _refresh_mission_control_manifest(state_root)
    state = dict(bundle.get("mission_control_state", {}))
    queue = dict(bundle.get("review_queue_state", {}))
    modes = dict(bundle.get("mode_overview", {}))
    capabilities = dict(bundle.get("capability_manifest", {}))
    affordances = dict(bundle.get("action_affordances", {}))
    navigator = dict(bundle.get("stage_navigator", {}))
    questions = dict(bundle.get("question_starters", {}))
    onboarding = dict(bundle.get("onboarding_status", {}))
    branch_dag = dict(bundle.get("branch_dag", {}))
    confidence_map = dict(bundle.get("confidence_map", {}))
    trace_explorer = dict(bundle.get("trace_explorer_state", {}))
    background_jobs = dict(bundle.get("background_job_view", {}))
    release_health = dict(bundle.get("release_health_report", {}))
    demo_scorecard = dict(bundle.get("flagship_demo_scorecard", {}))
    onboarding_success = dict(bundle.get("onboarding_success_report", {}))
    pulse = read_run_summary(run_dir).get("pulse", {}) if run_dir is not None else {}
    pulse = dict(pulse) if isinstance(pulse, dict) else {}
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(run_dir) if run_dir is not None else None,
            "state_dir": str(state_root),
            "manifest_path": str(manifest_path),
            "paths": {**{key: str(value) for key, value in written.items()}, "launch_manifest": str(state_root / "launch_manifest.json")},
            "mission_control": {
                "current_stage": state.get("current_stage"),
                "recommended_action": state.get("recommended_action"),
                "review_required": state.get("review_required"),
                "next_actor": state.get("next_actor"),
                "card_count": state.get("card_count"),
                "capability_count": state.get("capability_count"),
                "action_count": state.get("action_count"),
                "question_count": state.get("question_count"),
                "review_queue_pending_count": queue.get("pending_count"),
                "intelligence_mode": modes.get("intelligence_effective_mode"),
                "autonomy_mode": modes.get("autonomy_mode"),
                "can_rerun_stage": navigator.get("can_rerun_stage"),
                "navigation_scope": navigator.get("navigation_scope"),
                "launch_ready": onboarding.get("launch_ready"),
                "doctor_status": onboarding.get("doctor_status"),
                "needs_data": onboarding.get("needs_data"),
                "live_chat_command": onboarding.get("live_chat_command"),
                "html_report_path": launch_payload.get("html_report_path"),
                "browser_requested": launch_payload.get("browser_requested"),
                "browser_opened": launch_payload.get("browser_opened"),
                "capability_manifest_status": capabilities.get("status"),
                "action_affordances_status": affordances.get("status"),
                "question_starters_status": questions.get("status"),
                "pulse_status": pulse.get("status"),
                "pulse_mode": pulse.get("mode"),
                "pulse_queued_action_count": pulse.get("queued_action_count"),
                "overall_confidence": confidence_map.get("overall_confidence"),
                "branch_count": branch_dag.get("branch_count"),
                "trace_winning_action": trace_explorer.get("winning_action"),
                "background_job_count": background_jobs.get("job_count"),
                "release_health_status": release_health.get("status"),
                "current_demo_story": demo_scorecard.get("current_run_story"),
                "onboarding_ready_for_first_time_user": onboarding_success.get("ready_for_first_time_user"),
            },
            "bundle": bundle,
        },
        "human_output": review.review_markdown,
    }


def _resolve_mission_control_root(*, run_dir: str | None, output_dir: str | None) -> Path:
    if run_dir:
        return Path(run_dir)
    if output_dir:
        return Path(output_dir)
    return Path("artifacts") / "mission_control_onboarding"


def _load_mission_control_policy(*, run_dir: str | None, config_path: str | None) -> dict[str, Any]:
    if run_dir:
        resolved_path = Path(run_dir) / "policy_resolved.yaml"
        if resolved_path.exists():
            try:
                return load_policy(resolved_path).policy
            except Exception:
                pass
    try:
        return load_policy(config_path).policy
    except Exception:
        return {}


def _materialize_assist_surface(
    *,
    run_dir: str | Path,
    config_path: str | None,
    last_user_intent: str | None,
    last_requested_stage: str | None,
    last_action_kind: str | None,
    increment_turn_count: bool,
) -> dict[str, Any]:
    from relaytic.assist import write_assist_bundle
    from relaytic.intelligence import build_intelligence_controls_from_policy
    from relaytic.intelligence.backends import discover_backend

    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    existing_summary = read_run_summary(root)
    request = dict(existing_summary.get("request", {})) if isinstance(existing_summary, dict) else {}
    summary_materialized = _load_or_materialize_summary(
        run_dir=root,
        data_path=_resolve_run_data_path(root),
        request_source=str(request.get("source", "")).strip() or None,
        request_text=str(request.get("text_preview", "")).strip() or None,
    )
    backend_discovery_payload: dict[str, Any]
    try:
        backend_discovery = discover_backend(
            controls=build_intelligence_controls_from_policy(foundation_state["resolved"].policy),
            config_path=config_path,
        )
        backend_discovery_payload = backend_discovery.to_dict()
    except Exception as exc:
        backend_discovery_payload = {
            "status": "error",
            "notes": [str(exc)],
        }
    existing_assist = _read_json_bundle(root, bundle="assist")
    previous_state = dict(existing_assist.get("assist_session_state", {}))
    previous_turn_count = int(previous_state.get("turn_count", 0) or 0)
    bundle = build_assist_bundle(
        policy=foundation_state["resolved"].policy,
        run_summary=summary_materialized["summary"],
        backend_discovery=backend_discovery_payload,
        interoperability_inventory=build_interoperability_inventory(),
        last_user_intent=last_user_intent or _clean_text(previous_state.get("last_user_intent")),
        last_requested_stage=last_requested_stage or _clean_text(previous_state.get("last_requested_stage")),
        last_action_kind=last_action_kind or _clean_text(previous_state.get("last_action_kind")),
        turn_count=previous_turn_count + (1 if increment_turn_count else 0),
    )
    written = write_assist_bundle(root, bundle=bundle)
    manifest_path = _refresh_assist_manifest(
        root,
        policy_source=foundation_state["policy_path"],
    )
    return {
        "bundle": bundle.to_dict(),
        "written": {key: str(value) for key, value in written.items()},
        "manifest_path": manifest_path,
        "run_summary": summary_materialized["summary"],
    }


def _next_takeover_stage(*, run_dir: str | Path, run_summary: dict[str, Any]) -> str | None:
    root = Path(run_dir)
    for stage_name, required_path in (
        ("intake", root / "intake_record.json"),
        ("investigation", root / "dataset_profile.json"),
        ("memory", root / "memory_retrieval.json"),
        ("planning", root / "plan.json"),
        ("evidence", root / "audit_report.json"),
        ("intelligence", root / "semantic_debate_report.json"),
        ("research", root / "research_brief.json"),
        ("benchmark", root / "benchmark_parity_report.json"),
        ("decision", root / "decision_world_model.json"),
        ("completion", root / "completion_decision.json"),
        ("lifecycle", root / "champion_vs_candidate.json"),
        ("autonomy", root / "autonomy_loop_state.json"),
    ):
        if not required_path.exists():
            return stage_name
    next_action = _clean_text(dict(run_summary.get("next_step", {})).get("recommended_action"))
    if next_action in {
        "retrain",
        "retrain_candidate",
        "recalibrate",
        "recalibration_candidate",
        "continue_experimentation",
        "review_challenger",
        "memory_support_needed",
    }:
        return "autonomy"
    return None


def _run_assist_stage_pipeline(
    *,
    run_dir: str | Path,
    start_stage: str,
    config_path: str | None,
    data_path: str | None,
    overwrite: bool,
) -> list[str]:
    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    labels: dict[str, str] | None = None
    executed: list[str] = []
    resolved_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="primary",
    ) or _resolve_run_data_path(root)
    stage_order = [
        "foundation",
        "intake",
        "investigation",
        "memory",
        "planning",
        "evidence",
        "intelligence",
        "research",
        "benchmark",
        "decision",
        "completion",
        "lifecycle",
        "autonomy",
    ]
    if start_stage not in stage_order:
        raise ValueError(f"Unsupported assist stage `{start_stage}`.")
    for stage in stage_order[stage_order.index(start_stage) :]:
        if stage == "foundation":
            _init_run_foundation(
                run_dir=root,
                config_path=config_path,
                run_id=None,
                overwrite=overwrite,
                labels=labels,
            )
            executed.append(stage)
            continue
        if stage == "intake":
            intake_context = _assist_replay_intake_context(root=root)
            if not intake_context["message"]:
                raise ValueError("Relaytic assist cannot rerun intake because no prior intake message was found.")
            _run_intake_phase(
                run_dir=root,
                message=str(intake_context["message"]),
                actor_type=str(intake_context["actor_type"]),
                actor_name=intake_context["actor_name"],
                channel=str(intake_context["channel"]),
                config_path=config_path,
                run_id=None,
                data_path=resolved_data_path or intake_context["data_path"],
                sheet_name=intake_context["sheet_name"],
                header_row=intake_context["header_row"],
                data_start_row=intake_context["data_start_row"],
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            resolved_data_path = resolved_data_path or intake_context["data_path"]
            executed.append(stage)
            continue
        if stage == "investigation":
            if not resolved_data_path:
                raise ValueError("Relaytic assist requires a dataset path to rerun investigation.")
            _run_investigation_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=None,
                sheet_name=None,
                header_row=None,
                data_start_row=None,
                timestamp_column=None,
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "memory":
            _run_memory_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=None,
                labels=labels,
                search_roots=None,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "planning":
            if not resolved_data_path:
                raise ValueError("Relaytic assist requires a dataset path to rerun planning.")
            _run_planning_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=None,
                sheet_name=None,
                header_row=None,
                data_start_row=None,
                timestamp_column=None,
                overwrite=True,
                labels=labels,
                execute_route=True,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "evidence":
            if not resolved_data_path:
                raise ValueError("Relaytic assist requires a dataset path to rerun evidence.")
            _run_evidence_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=None,
                sheet_name=None,
                header_row=None,
                data_start_row=None,
                timestamp_column=None,
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "intelligence":
            _run_intelligence_phase(
                run_dir=root,
                config_path=config_path,
                run_id=None,
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "research":
            _run_research_phase(
                run_dir=root,
                config_path=config_path,
                run_id=None,
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "benchmark":
            incumbent_config = _resolve_existing_incumbent_config(root)
            _run_benchmark_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=None,
                overwrite=True,
                labels=labels,
                incumbent_path=incumbent_config.get("incumbent_path"),
                incumbent_kind=incumbent_config.get("incumbent_kind"),
                incumbent_name=incumbent_config.get("incumbent_name"),
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "decision":
            _run_decision_phase(
                run_dir=root,
                config_path=config_path,
                run_id=None,
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "completion":
            _run_completion_phase(
                run_dir=root,
                config_path=config_path,
                run_id=None,
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "lifecycle":
            _run_lifecycle_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=None,
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
        if stage == "autonomy":
            _run_autonomy_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=None,
                overwrite=True,
                labels=labels,
                runtime_surface="cli",
                runtime_command="relaytic assist turn",
            )
            executed.append(stage)
            continue
    return executed


def _assist_replay_intake_context(*, root: Path) -> dict[str, Any]:
    intake_bundle = _read_json_bundle(root, bundle="intake")
    intake_record = dict(intake_bundle.get("intake_record", {}))
    return {
        "message": _clean_text(intake_record.get("message")),
        "actor_type": _clean_text(intake_record.get("actor_type")) or "user",
        "actor_name": _clean_text(intake_record.get("actor_name")),
        "channel": _clean_text(intake_record.get("channel")) or "assist",
        "data_path": _clean_text(intake_record.get("dataset_path")) or _resolve_run_data_path(root),
        "sheet_name": _clean_text(intake_record.get("selected_sheet")),
        "header_row": intake_record.get("header_row"),
        "data_start_row": intake_record.get("data_start_row"),
    }


def _ensure_completion_present(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = _read_json_bundle(root, bundle="completion")
    if bundle and bool(stage_recompute_entry(root, stage="completion").get("reusable", False)):
        return bundle
    evidence_bundle = _read_json_bundle(root, bundle="evidence")
    if not evidence_bundle:
        return {}
    payload = _run_completion_phase(
        run_dir=root,
        config_path=None,
        run_id=None,
        overwrite=False,
        labels=None,
    )
    return dict(payload["surface_payload"].get("bundle", {}))


def _ensure_memory_present(run_dir: str | Path, data_path: str | None = None) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = _read_json_bundle(root, bundle="memory")
    if bundle:
        return bundle
    resolved_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="evaluation",
    ) or _resolve_run_data_path(root)
    if not _read_json_bundle(root, bundle="investigation") and not resolved_data_path:
        return {}
    payload = _run_memory_phase(
        run_dir=root,
        data_path=resolved_data_path,
        config_path=None,
        run_id=None,
        labels=None,
        search_roots=None,
    )
    return dict(payload["surface_payload"].get("bundle", {}))


def _ensure_intelligence_present(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = _read_json_bundle(root, bundle="intelligence")
    if bundle:
        return bundle
    evidence_bundle = _read_json_bundle(root, bundle="evidence")
    if not evidence_bundle:
        return {}
    payload = _run_intelligence_phase(
        run_dir=root,
        config_path=None,
        run_id=None,
        overwrite=False,
        labels=None,
    )
    return dict(payload["surface_payload"].get("bundle", {}))


def _ensure_research_present(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = _read_json_bundle(root, bundle="research")
    if bundle:
        return bundle
    evidence_bundle = _read_json_bundle(root, bundle="evidence")
    if not evidence_bundle:
        return {}
    payload = _run_research_phase(
        run_dir=root,
        config_path=None,
        run_id=None,
        overwrite=False,
        labels=None,
    )
    return dict(payload["surface_payload"].get("bundle", {}))


def _ensure_decision_present(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = _read_json_bundle(root, bundle="decision")
    if bundle:
        return bundle
    planning_bundle = _read_json_bundle(root, bundle="planning")
    if not planning_bundle:
        return {}
    payload = _run_decision_phase(
        run_dir=root,
        config_path=None,
        run_id=None,
        overwrite=False,
        labels=None,
    )
    return dict(payload["surface_payload"].get("bundle", {}))


def _ensure_runtime_present(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = _read_json_bundle(root, bundle="runtime")
    if bundle:
        return bundle
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=None,
        run_id=None,
        labels=None,
    )
    ensure_runtime_initialized(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        source_surface="cli",
        source_command="runtime_backfill",
        backfill_if_missing=True,
    )
    return _read_json_bundle(root, bundle="runtime")


def _ensure_lifecycle_present(run_dir: str | Path, data_path: str | None = None) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = _read_json_bundle(root, bundle="lifecycle")
    if bundle:
        return bundle
    completion_bundle = _ensure_completion_present(root)
    if not completion_bundle:
        return {}
    resolved_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="evaluation",
    ) or _resolve_run_data_path(root)
    payload = _run_lifecycle_phase(
        run_dir=root,
        data_path=resolved_data_path,
        config_path=None,
        run_id=None,
        overwrite=False,
        labels=None,
    )
    return dict(payload["surface_payload"].get("bundle", {}))


def _read_json_bundle(run_dir: str | Path, *, bundle: str) -> dict[str, Any]:
    if bundle == "mandate":
        from relaytic.mandate import read_mandate_bundle

        return read_mandate_bundle(run_dir)
    if bundle == "context":
        from relaytic.context import read_context_bundle

        return read_context_bundle(run_dir)
    if bundle == "intake":
        from relaytic.intake import read_intake_bundle

        return read_intake_bundle(run_dir)
    if bundle == "investigation":
        from relaytic.investigation import read_investigation_bundle

        return read_investigation_bundle(run_dir)
    if bundle == "planning":
        from relaytic.planning import read_planning_bundle

        return read_planning_bundle(run_dir)
    if bundle == "evidence":
        from relaytic.evidence import read_evidence_bundle

        return read_evidence_bundle(run_dir)
    if bundle == "memory":
        from relaytic.memory import read_memory_bundle

        return read_memory_bundle(run_dir)
    if bundle == "intelligence":
        from relaytic.intelligence import read_intelligence_bundle

        return read_intelligence_bundle(run_dir)
    if bundle == "research":
        from relaytic.research import read_research_bundle

        return read_research_bundle(run_dir)
    if bundle == "benchmark":
        from relaytic.benchmark import read_benchmark_bundle

        return read_benchmark_bundle(run_dir)
    if bundle == "decision":
        from relaytic.decision import read_decision_bundle

        return read_decision_bundle(run_dir)
    if bundle == "dojo":
        from relaytic.dojo import read_dojo_bundle

        return read_dojo_bundle(run_dir)
    if bundle == "pulse":
        from relaytic.pulse import read_pulse_bundle

        return read_pulse_bundle(run_dir)
    if bundle == "trace":
        from relaytic.tracing import read_trace_bundle

        return read_trace_bundle(run_dir)
    if bundle == "evals":
        from relaytic.evals import read_eval_bundle

        return read_eval_bundle(run_dir)
    if bundle == "search":
        from relaytic.search import read_search_bundle

        return read_search_bundle(run_dir)
    if bundle == "daemon":
        return read_daemon_bundle(run_dir)
    if bundle == "feedback":
        from relaytic.feedback import read_feedback_bundle

        return read_feedback_bundle(run_dir)
    if bundle == "profiles":
        from relaytic.profiles import read_profiles_bundle

        return read_profiles_bundle(run_dir)
    if bundle == "control":
        from relaytic.control import read_control_bundle

        return read_control_bundle(run_dir)
    if bundle == "runtime":
        from relaytic.runtime import read_runtime_bundle

        return read_runtime_bundle(run_dir)
    if bundle == "events":
        return read_event_bus_bundle(run_dir)
    if bundle == "permissions":
        from relaytic.permissions import read_permission_bundle

        return read_permission_bundle(run_dir)
    if bundle == "completion":
        from relaytic.completion import read_completion_bundle

        return read_completion_bundle(run_dir)
    if bundle == "lifecycle":
        from relaytic.lifecycle import read_lifecycle_bundle

        return read_lifecycle_bundle(run_dir)
    if bundle == "autonomy":
        from relaytic.autonomy import read_autonomy_bundle

        return read_autonomy_bundle(run_dir)
    if bundle == "assist":
        from relaytic.assist import read_assist_bundle

        return read_assist_bundle(run_dir)
    if bundle == "mission_control":
        from relaytic.mission_control import read_mission_control_bundle

        return read_mission_control_bundle(run_dir)
    if bundle == "handoff":
        return read_handoff_bundle(run_dir)
    if bundle == "learnings":
        root = Path(run_dir)
        state_dir = default_learnings_state_dir(run_dir=root)
        return {
            "learnings_state": read_learnings_state(state_dir),
            "lab_learnings_snapshot": read_learnings_snapshot(root),
        }
    raise ValueError(f"Unsupported bundle '{bundle}'.")


def _resolve_run_data_path(run_dir: str | Path) -> str | None:
    root = Path(run_dir)
    try:
        from relaytic.ingestion import resolve_staged_data_path

        staged_primary = resolve_staged_data_path(root, purpose="primary")
        if staged_primary:
            return staged_primary
    except Exception:
        pass
    existing_summary = read_run_summary(root)
    if isinstance(existing_summary, dict):
        data_path = str(dict(existing_summary.get("data", {})).get("data_path", "")).strip()
        if data_path:
            return data_path
    planning_bundle = _read_json_bundle(root, bundle="planning")
    plan = dict(planning_bundle.get("plan", {}))
    builder_handoff = dict(plan.get("builder_handoff", {}))
    for value in builder_handoff.get("data_references", []):
        text = str(value).strip()
        if text:
            return text
    return None


def _stage_run_data_copy(
    *,
    run_dir: str | Path,
    data_path: str | None,
    purpose: str,
    source_type: str = "auto",
    source_table: str | None = None,
    sql_query: str | None = None,
    stream_window_rows: int = 5000,
    stream_format: str = "auto",
    materialized_format: str = "auto",
    delimiter: str | None = None,
) -> str | None:
    if not data_path:
        return None
    from relaytic.ingestion import build_source_spec, materialize_structured_source

    root = Path(run_dir)
    source_spec = build_source_spec(
        source_path=data_path,
        source_type=source_type,
        source_table=source_table,
        sql_query=sql_query,
        stream_window_rows=stream_window_rows,
        stream_format=stream_format,
        materialized_format=materialized_format,
        delimiter=delimiter,
    )
    materialized = materialize_structured_source(
        spec=source_spec,
        run_dir=root,
        purpose=purpose,
        alias=Path(data_path).stem,
    )
    return materialized.staged_path


def _runtime_surface_from_channel(channel: str | None) -> str:
    text = str(channel or "").strip().lower()
    if "mcp" in text:
        return "mcp"
    return "cli"


def _source_option_payload(
    *,
    source_type: str = "auto",
    source_table: str | None = None,
    sql_query: str | None = None,
    stream_window_rows: int = 5000,
    stream_format: str = "auto",
    materialized_format: str = "auto",
    delimiter: str | None = None,
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_table": source_table,
        "sql_query": sql_query,
        "stream_window_rows": int(stream_window_rows),
        "stream_format": stream_format,
        "materialized_format": materialized_format,
        "delimiter": delimiter,
    }


def _runtime_stage_token(
    *,
    run_dir: Path,
    policy: dict[str, Any],
    stage: str,
    data_path: str | None,
    runtime_surface: str,
    runtime_command: str | None,
    input_artifacts: list[str] | None = None,
) -> dict[str, Any]:
    return record_runtime_stage_start(
        run_dir=run_dir,
        policy=policy,
        stage=stage,
        source_surface=runtime_surface,
        source_command=str(runtime_command or stage),
        data_path=data_path,
        input_artifacts=input_artifacts,
    )


def _init_run_foundation(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
) -> dict[str, Any]:
    from relaytic.context import (
        build_context_controls_from_policy,
        default_data_origin,
        default_domain_brief,
        default_task_brief,
        write_context_bundle,
    )
    from relaytic.mandate import (
        build_mandate_controls_from_policy,
        build_run_brief,
        build_work_preferences,
        default_lab_mandate,
        write_mandate_bundle,
    )

    root = Path(run_dir)
    foundation_paths = _foundation_output_paths(root)
    _ensure_paths_absent(
        [
            foundation_paths["lab_mandate"],
            foundation_paths["work_preferences"],
            foundation_paths["run_brief"],
            foundation_paths["data_origin"],
            foundation_paths["domain_brief"],
            foundation_paths["task_brief"],
            foundation_paths["manifest"],
        ],
        overwrite=overwrite,
    )
    resolved, policy_path = _ensure_policy_resolved(root, config_path=config_path, overwrite=overwrite)
    mandate_controls = build_mandate_controls_from_policy(resolved.policy)
    context_controls = build_context_controls_from_policy(resolved.policy)

    mandate_paths = write_mandate_bundle(
        root,
        lab_mandate=default_lab_mandate(mandate_controls),
        work_preferences=build_work_preferences(mandate_controls, policy=resolved.policy),
        run_brief=build_run_brief(mandate_controls, policy=resolved.policy),
    )
    context_paths = write_context_bundle(
        root,
        data_origin=default_data_origin(context_controls),
        domain_brief=default_domain_brief(context_controls),
        task_brief=default_task_brief(context_controls),
    )
    manifest_path = _refresh_foundation_manifest(
        root,
        run_id=run_id,
        policy_source=policy_path,
        labels=labels,
    )
    return {
        "status": "ok",
        "run_dir": str(root),
        "policy_resolved": str(policy_path),
        "mandate_paths": {key: str(value) for key, value in mandate_paths.items()},
        "context_paths": {key: str(value) for key, value in context_paths.items()},
        "manifest_path": str(manifest_path),
        "source_format": resolved.source_format,
    }


def _ensure_run_foundation_present(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    labels: dict[str, str] | None,
) -> dict[str, Any]:
    from relaytic.context import (
        build_context_controls_from_policy,
        default_data_origin,
        default_domain_brief,
        default_task_brief,
        write_context_bundle,
    )
    from relaytic.mandate import (
        build_mandate_controls_from_policy,
        build_run_brief,
        build_work_preferences,
        default_lab_mandate,
        write_mandate_bundle,
    )

    root = Path(run_dir)
    resolved, policy_path = _ensure_policy_resolved(root, config_path=config_path, overwrite=False)
    foundation_paths = _foundation_output_paths(root)
    if not all(
        foundation_paths[key].exists()
        for key in ("lab_mandate", "work_preferences", "run_brief")
    ):
        mandate_controls = build_mandate_controls_from_policy(resolved.policy)
        write_mandate_bundle(
            root,
            lab_mandate=default_lab_mandate(mandate_controls),
            work_preferences=build_work_preferences(mandate_controls, policy=resolved.policy),
            run_brief=build_run_brief(mandate_controls, policy=resolved.policy),
        )
    if not all(
        foundation_paths[key].exists()
        for key in ("data_origin", "domain_brief", "task_brief")
    ):
        context_controls = build_context_controls_from_policy(resolved.policy)
        write_context_bundle(
            root,
            data_origin=default_data_origin(context_controls),
            domain_brief=default_domain_brief(context_controls),
            task_brief=default_task_brief(context_controls),
        )
    manifest_path = _refresh_foundation_manifest(
        root,
        run_id=run_id,
        policy_source=policy_path,
        labels=labels,
    )
    return {
        "resolved": resolved,
        "policy_path": policy_path,
        "manifest_path": manifest_path,
    }


def _run_intake_phase(
    *,
    run_dir: str | Path,
    message: str,
    actor_type: str,
    actor_name: str | None,
    channel: str,
    config_path: str | None,
    run_id: str | None,
    data_path: str | None,
    sheet_name: str | None,
    header_row: int | None,
    data_start_row: int | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.context import write_context_bundle
    from relaytic.intake import write_intake_bundle
    from relaytic.mandate import write_mandate_bundle

    root = Path(run_dir)
    targets = _intake_output_paths(root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    staged_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="primary",
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="intake",
        data_path=staged_data_path,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=["lab_mandate.json", "work_preferences.json", "run_brief.json", "data_origin.json", "domain_brief.json", "task_brief.json"],
    )
    try:
        resolution = run_intake_interpretation(
            message=message,
            actor_type=actor_type,
            actor_name=actor_name,
            channel=channel,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            config_path=config_path,
            data_path=staged_data_path,
            sheet_name=sheet_name,
            header_row=header_row,
            data_start_row=data_start_row,
        )
        mandate_paths = write_mandate_bundle(
            root,
            lab_mandate=resolution.lab_mandate,
            work_preferences=resolution.work_preferences,
            run_brief=resolution.run_brief,
        )
        context_paths = write_context_bundle(
            root,
            data_origin=resolution.data_origin,
            domain_brief=resolution.domain_brief,
            task_brief=resolution.task_brief,
        )
        intake_paths = write_intake_bundle(root, bundle=resolution.intake_bundle)
        manifest_path = _refresh_intake_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in mandate_paths.values()), *(str(value) for value in context_paths.values()), *(str(value) for value in intake_paths.values()), str(manifest_path)],
            summary="Relaytic translated free-form intake into structured mandate, context, and intake artifacts.",
        )
        return {
            "status": "ok",
            "run_dir": str(root),
            "policy_resolved": str(foundation_state["policy_path"]),
            "mandate_paths": {key: str(value) for key, value in mandate_paths.items()},
            "context_paths": {key: str(value) for key, value in context_paths.items()},
            "intake_paths": {key: str(value) for key, value in intake_paths.items()},
            "manifest_path": str(manifest_path),
            "autonomy_mode": resolution.intake_bundle.autonomy_mode.to_dict(),
            "clarification_queue": resolution.intake_bundle.clarification_queue.to_dict(),
            "assumption_log": resolution.intake_bundle.assumption_log.to_dict(),
            "clarification_questions": resolution.intake_bundle.context_interpretation.clarification_questions,
            "assumptions": resolution.intake_bundle.context_interpretation.assumptions,
            "conflicts": resolution.intake_bundle.context_interpretation.conflicts,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _run_investigation_phase(
    *,
    run_dir: str | Path,
    data_path: str,
    config_path: str | None,
    run_id: str | None,
    sheet_name: str | None,
    header_row: int | None,
    data_start_row: int | None,
    timestamp_column: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.investigation import write_investigation_bundle

    root = Path(run_dir)
    targets = _investigation_output_paths(root)
    _ensure_paths_absent(
        [
            targets["dataset_profile"],
            targets["domain_memo"],
            targets["objective_hypotheses"],
            targets["focus_debate"],
            targets["focus_profile"],
            targets["optimization_profile"],
            targets["feature_strategy_profile"],
        ],
        overwrite=overwrite,
    )
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    staged_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="primary",
    ) or str(Path(data_path))
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="investigation",
        data_path=staged_data_path,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=["task_brief.json", "domain_brief.json", "run_brief.json", "data_origin.json"],
    )
    try:
        bundle = run_investigation(
            data_path=staged_data_path,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            config_path=config_path,
            sheet_name=sheet_name,
            header_row=header_row,
            data_start_row=data_start_row,
            timestamp_column=timestamp_column,
        )
        written = write_investigation_bundle(root, bundle=bundle)
        manifest_path = _refresh_investigation_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic profiled the dataset and resolved focus through Scout, Scientist, and Focus Council artifacts.",
        )
        focus_profile = bundle.focus_profile.to_dict()
        return {
            "status": "ok",
            "run_dir": str(root),
            "data_path": str(Path(data_path)),
            "policy_resolved": str(foundation_state["policy_path"]),
            "paths": {key: str(value) for key, value in written.items()},
            "manifest_path": str(manifest_path),
            "focus_profile": {
                "primary_objective": focus_profile.get("primary_objective"),
                "secondary_objectives": focus_profile.get("secondary_objectives"),
                "resolution_mode": focus_profile.get("resolution_mode"),
            },
            "optimization_profile": {
                "primary_metric": bundle.optimization_profile.primary_metric,
                "split_strategy_bias": bundle.optimization_profile.split_strategy_bias,
            },
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _run_planning_phase(
    *,
    run_dir: str | Path,
    data_path: str,
    config_path: str | None,
    run_id: str | None,
    sheet_name: str | None,
    header_row: int | None,
    data_start_row: int | None,
    timestamp_column: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    execute_route: bool,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.analytics import (
        read_architecture_routing_artifacts,
        read_task_contract_artifacts,
        sync_architecture_routing_artifacts,
        sync_task_contract_artifacts,
        sync_temporal_engine_artifacts,
    )
    from relaytic.planning import write_planning_bundle

    root = Path(run_dir)
    targets = _planning_output_paths(root)
    protected_paths = list(targets.values())
    if execute_route:
        protected_paths.extend(_planning_model_artifact_paths(root))
    _ensure_paths_absent(protected_paths, overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    staged_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="primary",
    ) or str(Path(data_path))
    investigation_state = _ensure_investigation_present(
        run_dir=root,
        data_path=staged_data_path,
        config_path=config_path,
        run_id=run_id,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        overwrite=overwrite,
        labels=labels,
    )
    _run_memory_phase(
        run_dir=root,
        data_path=staged_data_path,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        search_roots=None,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="planning",
        data_path=staged_data_path,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=["dataset_profile.json", "domain_memo.json", "focus_profile.json", "optimization_profile.json", "feature_strategy_profile.json", "route_prior_context.json"],
    )
    try:
        planning_bundle = run_planning(
            data_path=staged_data_path,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            investigation_bundle=investigation_state["bundle"],
            memory_bundle=_read_json_bundle(root, bundle="memory"),
            config_path=config_path,
            sheet_name=sheet_name,
            header_row=header_row,
            data_start_row=data_start_row,
        )
        training_result: dict[str, Any] | None = None
        if execute_route:
            execution = execute_planned_route(
                run_dir=root,
                data_path=staged_data_path,
                planning_bundle=planning_bundle,
                sheet_name=sheet_name,
                header_row=header_row,
                data_start_row=data_start_row,
            )
            planning_bundle = execution.planning_bundle
            training_result = execution.training_result
        written = write_planning_bundle(root, bundle=planning_bundle)
        task_contract_written = sync_task_contract_artifacts(
            root,
            data_path=staged_data_path,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            investigation_bundle=investigation_state["bundle"],
            planning_bundle=planning_bundle.to_dict(),
        )
        architecture_written = sync_architecture_routing_artifacts(
            root,
            investigation_bundle=investigation_state["bundle"],
            planning_bundle=planning_bundle.to_dict(),
            route_prior_context=dict(_read_json_bundle(root, bundle="memory").get("route_prior_context", {}) or {}),
            benchmark_bundle=_read_json_bundle(root, bundle="benchmark"),
        )
        temporal_written = sync_temporal_engine_artifacts(
            root,
            data_path=staged_data_path,
            investigation_bundle=investigation_state["bundle"],
            planning_bundle=planning_bundle.to_dict(),
            benchmark_bundle=_read_json_bundle(root, bundle="benchmark"),
            architecture_bundle=read_architecture_routing_artifacts(root),
            task_contract_bundle=read_task_contract_artifacts(root),
        )
        manifest_path = _refresh_planning_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
            training_result=training_result,
        )
        model_artifacts = []
        if training_result is not None:
            for key in ("model_params_path", "model_state_path"):
                value = training_result.get(key)
                if value:
                    model_artifacts.append(str(value))
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[
                *(str(value) for value in written.values()),
                *(str(value) for value in task_contract_written.values()),
                *(str(value) for value in architecture_written.values()),
                *(str(value) for value in temporal_written.values()),
                *model_artifacts,
                str(manifest_path),
            ],
            summary="Relaytic built the Strategist plan and, when requested, executed the first Builder route in the same run directory.",
        )
        payload = {
            "status": "ok",
            "run_dir": str(root),
            "data_path": staged_data_path,
            "policy_resolved": str(foundation_state["policy_path"]),
            "paths": {
                **{key: str(value) for key, value in written.items()},
                **{key: str(value) for key, value in task_contract_written.items()},
                **{key: str(value) for key, value in architecture_written.items()},
                **{key: str(value) for key, value in temporal_written.items()},
            },
            "manifest_path": str(manifest_path),
            "plan": {
                "selected_route_id": planning_bundle.plan.selected_route_id,
                "selected_route_title": planning_bundle.plan.selected_route_title,
                "target_column": planning_bundle.plan.target_column,
                "primary_metric": planning_bundle.plan.primary_metric,
                "split_strategy": planning_bundle.plan.split_strategy,
            },
            "builder_handoff": planning_bundle.plan.builder_handoff,
        }
        if training_result is not None:
            payload["training_result"] = {
                "selected_model_family": training_result.get("selected_model_family"),
                "best_validation_model_family": training_result.get("best_validation_model_family"),
                "checkpoint_id": training_result.get("checkpoint_id"),
                "model_params_path": training_result.get("model_params_path"),
                "model_state_path": training_result.get("model_state_path"),
                "run_dir": training_result.get("run_dir"),
                "selected_metrics": training_result.get("selected_metrics"),
            }
        return payload
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _run_evidence_phase(
    *,
    run_dir: str | Path,
    data_path: str,
    config_path: str | None,
    run_id: str | None,
    sheet_name: str | None,
    header_row: int | None,
    data_start_row: int | None,
    timestamp_column: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    planning_state: dict[str, Any] | None = None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.evidence import write_evidence_bundle

    root = Path(run_dir)
    staged_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="primary",
    ) or str(Path(data_path))
    targets = _evidence_output_paths(root)
    _ensure_paths_absent(
        [
            path
            for key, path in targets.items()
            if key
            in {
                "experiment_registry",
                "challenger_report",
                "ablation_report",
                "audit_report",
                "belief_update",
                "leaderboard",
                "technical_report",
                "decision_memo",
            }
        ],
        overwrite=overwrite,
    )
    selected_planning_state = planning_state
    if selected_planning_state is None:
        planning_bundle_existing = _read_json_bundle(root, bundle="planning")
        existing_plan = dict(planning_bundle_existing.get("plan", {}))
        if not overwrite and existing_plan and dict(existing_plan.get("execution_summary", {})):
            selected_planning_state = {
                "status": "ok",
                "run_dir": str(root),
                "data_path": staged_data_path,
                "plan": {
                    "selected_route_id": existing_plan.get("selected_route_id"),
                    "selected_route_title": existing_plan.get("selected_route_title"),
                    "target_column": existing_plan.get("target_column"),
                    "primary_metric": existing_plan.get("primary_metric"),
                    "split_strategy": existing_plan.get("split_strategy"),
                },
                "training_result": dict(existing_plan.get("execution_summary", {})),
            }
    if selected_planning_state is None:
        planning_state = _run_planning_phase(
            run_dir=root,
            data_path=staged_data_path,
            config_path=config_path,
            run_id=run_id,
            sheet_name=sheet_name,
            header_row=header_row,
            data_start_row=data_start_row,
            timestamp_column=timestamp_column,
            overwrite=overwrite,
            labels=labels,
            execute_route=True,
            runtime_surface=runtime_surface,
            runtime_command=runtime_command,
        )
    else:
        planning_state = selected_planning_state
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    _run_memory_phase(
        run_dir=root,
        data_path=staged_data_path,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        search_roots=None,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="evidence",
        data_path=staged_data_path,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=["plan.json", "memory_retrieval.json", "route_prior_context.json", "challenger_prior_suggestions.json", "model_params.json"],
    )
    try:
        evidence_result = run_evidence_review(
            run_dir=root,
            data_path=staged_data_path,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            intake_bundle=_read_json_bundle(root, bundle="intake"),
            investigation_bundle=_read_json_bundle(root, bundle="investigation"),
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            memory_bundle=_read_json_bundle(root, bundle="memory"),
            config_path=config_path,
            sheet_name=sheet_name,
            header_row=header_row,
            data_start_row=data_start_row,
        )
        written = write_evidence_bundle(
            root,
            bundle=evidence_result.bundle,
            leaderboard_rows=evidence_result.leaderboard_rows,
            technical_report_markdown=evidence_result.technical_report_markdown,
            decision_memo_markdown=evidence_result.decision_memo_markdown,
        )
        manifest_path = _refresh_evidence_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic challenged the current route, wrote audit artifacts, and updated the current belief state.",
        )
        materialize_run_summary(run_dir=root, data_path=staged_data_path)
        payload = {
            "status": "ok",
            "run_dir": str(root),
            "data_path": staged_data_path,
            "manifest_path": str(manifest_path),
            "paths": {key: str(value) for key, value in written.items()},
            "evidence": {
                "provisional_recommendation": evidence_result.bundle.audit_report.provisional_recommendation,
                "readiness_level": evidence_result.bundle.audit_report.readiness_level,
                "challenger_winner": evidence_result.bundle.challenger_report.winner,
                "recommended_action": evidence_result.bundle.belief_update.recommended_action,
            },
            "plan": planning_state.get("plan", {}),
            "training_result": planning_state.get("training_result", {}),
        }
        return {
            "surface_payload": payload,
            "human_output": evidence_result.decision_memo_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _run_memory_phase(
    *,
    run_dir: str | Path,
    data_path: str | None,
    config_path: str | None,
    run_id: str | None,
    labels: dict[str, str] | None,
    search_roots: list[str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.memory import write_memory_bundle

    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    resolved_data_path = data_path or _resolve_run_data_path(root)
    if resolved_data_path:
        _ensure_investigation_present(
            run_dir=root,
            data_path=resolved_data_path,
            config_path=config_path,
            run_id=run_id,
            sheet_name=None,
            header_row=None,
            data_start_row=None,
            timestamp_column=None,
            overwrite=False,
            labels=labels,
        )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="memory",
        data_path=resolved_data_path,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=["run_summary.json", "plan.json", "challenger_report.json", "completion_decision.json", "promotion_decision.json"],
    )
    try:
        memory_result = run_memory_retrieval(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            intake_bundle=_read_json_bundle(root, bundle="intake"),
            investigation_bundle=_read_json_bundle(root, bundle="investigation"),
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            evidence_bundle=_read_json_bundle(root, bundle="evidence"),
            completion_bundle=_read_json_bundle(root, bundle="completion"),
            lifecycle_bundle=_read_json_bundle(root, bundle="lifecycle"),
            autonomy_bundle=_read_json_bundle(root, bundle="autonomy"),
            search_roots=search_roots or None,
        )
        written = write_memory_bundle(root, bundle=memory_result.bundle)
        manifest_path = _refresh_memory_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic retrieved prior analogs, flushed reflection memory, and updated advisory memory artifacts.",
        )
        payload = {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "paths": {key: str(value) for key, value in written.items()},
            "memory": {
                "status": memory_result.bundle.memory_retrieval.status,
                "analog_count": memory_result.bundle.memory_retrieval.selected_analog_count,
                "route_prior_applied": memory_result.bundle.route_prior_context.status == "memory_influenced",
                "preferred_challenger_family": memory_result.bundle.challenger_prior_suggestions.preferred_challenger_family,
            },
            "bundle": memory_result.bundle.to_dict(),
        }
        return {
            "surface_payload": payload,
            "human_output": memory_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _run_intelligence_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.intelligence import write_intelligence_bundle

    root = Path(run_dir)
    targets = _intelligence_output_paths(root)
    if not overwrite and all(path.exists() for path in targets.values()):
        return _show_intelligence_surface(run_dir=root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    evidence_bundle = _read_json_bundle(root, bundle="evidence")
    if not evidence_bundle:
        raise ValueError(f"Slice 09 intelligence requires Slice 06 evidence artifacts in {root}.")
    _run_memory_phase(
        run_dir=root,
        data_path=_resolve_run_data_path(root),
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        search_roots=None,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="intelligence",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=["run_brief.json", "task_brief.json", "plan.json", "audit_report.json", "completion_decision.json"],
    )
    try:
        intelligence_result = run_intelligence_review(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            intake_bundle=_read_json_bundle(root, bundle="intake"),
            investigation_bundle=_read_json_bundle(root, bundle="investigation"),
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            evidence_bundle=evidence_bundle,
            memory_bundle=_read_json_bundle(root, bundle="memory"),
            completion_bundle=_read_json_bundle(root, bundle="completion"),
            lifecycle_bundle=_read_json_bundle(root, bundle="lifecycle"),
            config_path=config_path,
        )
        written = write_intelligence_bundle(root, bundle=intelligence_result.bundle)
        manifest_path = _refresh_intelligence_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic assembled rowless semantic context, grounded artifact evidence, and wrote bounded debate outputs.",
        )
        materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        debate = intelligence_result.bundle.semantic_debate_report
        mode = intelligence_result.bundle.intelligence_mode
        routing = intelligence_result.bundle.llm_routing_plan
        profile = intelligence_result.bundle.local_llm_profile
        proof = intelligence_result.bundle.semantic_proof_report
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "intelligence": {
                    "configured_mode": mode.configured_mode,
                    "effective_mode": mode.effective_mode,
                    "routed_mode": routing.selected_mode,
                    "recommended_mode": routing.recommended_mode,
                    "local_profile": profile.profile_name,
                    "backend_status": mode.backend_status,
                    "recommended_followup_action": debate.recommended_followup_action,
                    "confidence": debate.confidence,
                    "semantic_gain_detected": proof.measurable_gain_detected,
                },
                "bundle": intelligence_result.bundle.to_dict(),
            },
            "human_output": intelligence_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_intelligence_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="intelligence")
    if not bundle:
        raise ValueError(f"No Slice 09 intelligence artifacts found in {root}.")
    materialize_run_summary(run_dir=root)
    manifest_path = _refresh_intelligence_manifest(root)
    mode = dict(bundle.get("intelligence_mode", {}))
    routing = dict(bundle.get("llm_routing_plan", {}))
    profile = dict(bundle.get("local_llm_profile", {}))
    debate = dict(bundle.get("semantic_debate_report", {}))
    proof = dict(bundle.get("semantic_proof_report", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "intelligence": {
                "configured_mode": mode.get("configured_mode"),
                "effective_mode": mode.get("effective_mode"),
                "routed_mode": routing.get("selected_mode"),
                "recommended_mode": routing.get("recommended_mode"),
                "local_profile": profile.get("profile_name"),
                "backend_status": mode.get("backend_status"),
                "recommended_followup_action": debate.get("recommended_followup_action"),
                "confidence": debate.get("confidence"),
                "domain_archetype": dict(debate.get("domain_interpretation", {})).get("domain_archetype"),
                "modeling_bias": dict(debate.get("domain_interpretation", {})).get("modeling_bias"),
                "semantic_gain_detected": proof.get("measurable_gain_detected"),
            },
            "bundle": bundle,
        },
        "human_output": render_intelligence_review_markdown(bundle),
    }


def _run_research_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.research import write_research_bundle

    root = Path(run_dir)
    targets = _research_output_paths(root)
    if not overwrite and all(path.exists() for path in targets.values()):
        return _show_research_surface(run_dir=root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    evidence_bundle = _read_json_bundle(root, bundle="evidence")
    if not evidence_bundle:
        raise ValueError(f"Slice 09D research requires Slice 06 evidence artifacts in {root}.")
    _run_intelligence_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        overwrite=False,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="research",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "run_brief.json",
            "task_brief.json",
            "dataset_profile.json",
            "plan.json",
            "audit_report.json",
            "semantic_debate_report.json",
        ],
    )
    try:
        research_result = run_research_review(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            intake_bundle=_read_json_bundle(root, bundle="intake"),
            investigation_bundle=_read_json_bundle(root, bundle="investigation"),
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            evidence_bundle=evidence_bundle,
            memory_bundle=_read_json_bundle(root, bundle="memory"),
            intelligence_bundle=_read_json_bundle(root, bundle="intelligence"),
        )
        written = write_research_bundle(root, bundle=research_result.bundle)
        manifest_path = _refresh_research_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic built redacted research queries, gathered typed external references, and wrote explicit transfer and audit artifacts.",
        )
        materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        brief = research_result.bundle.research_brief
        inventory = research_result.bundle.research_source_inventory
        transfer = research_result.bundle.method_transfer_report
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "research": {
                    "status": inventory.status,
                    "source_count": int(inventory.source_counts.get("total_sources", 0) or 0),
                    "recommended_followup_action": brief.recommended_followup_action,
                    "accepted_transfer_count": len(transfer.accepted_candidates),
                    "benchmark_reference_count": research_result.bundle.benchmark_reference_report.reference_count,
                },
                "bundle": research_result.bundle.to_dict(),
            },
            "human_output": research_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_research_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="research")
    if not bundle:
        raise ValueError(f"No Slice 09D research artifacts found in {root}.")
    materialize_run_summary(run_dir=root)
    manifest_path = _refresh_research_manifest(root)
    inventory = dict(bundle.get("research_source_inventory", {}))
    brief = dict(bundle.get("research_brief", {}))
    transfer = dict(bundle.get("method_transfer_report", {}))
    benchmark = dict(bundle.get("benchmark_reference_report", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "research": {
                "status": inventory.get("status"),
                "source_count": int(dict(inventory.get("source_counts", {})).get("total_sources", 0) or 0),
                "recommended_followup_action": brief.get("recommended_followup_action"),
                "accepted_transfer_count": len(transfer.get("accepted_candidates", [])),
                "benchmark_reference_count": int(benchmark.get("reference_count", 0) or 0),
            },
            "bundle": bundle,
        },
        "human_output": render_research_review_markdown(bundle),
    }


def _run_benchmark_phase(
    *,
    run_dir: str | Path,
    data_path: str | None,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    incumbent_path: str | None = None,
    incumbent_kind: str | None = None,
    incumbent_name: str | None = None,
    trust_model_deserialization: bool = False,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.benchmark import write_benchmark_bundle
    from relaytic.analytics import read_task_contract_artifacts

    root = Path(run_dir)
    targets = _benchmark_output_paths(root)
    benchmark_stage = stage_recompute_entry(root, stage="benchmark")
    if not overwrite and bool(benchmark_stage.get("reusable", False)):
        return _show_benchmark_surface(run_dir=root)
    _ensure_paths_absent(
        list(targets.values()),
        overwrite=overwrite or str(benchmark_stage.get("status", "")).strip() != "fresh",
    )
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    planning_bundle = _read_json_bundle(root, bundle="planning")
    plan = dict(planning_bundle.get("plan", {}))
    if not plan or not dict(plan.get("execution_summary", {})):
        raise ValueError(f"Slice 11 benchmark requires executed planning artifacts in {root}.")
    resolved_data_path = data_path or _resolve_run_data_path(root)
    if not resolved_data_path:
        raise ValueError(f"Slice 11 benchmark requires a resolvable dataset path in {root}.")
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="benchmark",
        data_path=resolved_data_path,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "plan.json",
            "model_params.json",
            "task_brief.json",
            "run_brief.json",
        ],
    )
    try:
        benchmark_result = run_benchmark_review(
            run_dir=root,
            data_path=resolved_data_path,
            policy=foundation_state["resolved"].policy,
            planning_bundle=planning_bundle,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            incumbent_path=incumbent_path,
            incumbent_kind=incumbent_kind,
            incumbent_name=incumbent_name,
            trust_model_deserialization=trust_model_deserialization,
        )
        written = write_benchmark_bundle(root, bundle=benchmark_result.bundle)
        manifest_path = _refresh_benchmark_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic compared the selected route against same-contract strong reference approaches and recorded honest parity artifacts.",
        )
        materialize_run_summary(run_dir=root, data_path=resolved_data_path)
        sync_materialization_runtime_artifacts(root)
        parity = benchmark_result.bundle.benchmark_parity_report
        gap = benchmark_result.bundle.benchmark_gap_report
        incumbent = benchmark_result.bundle.incumbent_parity_report
        beat_target = benchmark_result.bundle.beat_target_contract
        paper_manifest = benchmark_result.bundle.paper_benchmark_manifest
        rerun_variance = benchmark_result.bundle.rerun_variance_report
        claims = benchmark_result.bundle.benchmark_claims_report
        benchmark_truth_audit = benchmark_result.bundle.benchmark_truth_audit
        benchmark_release_gate = benchmark_result.bundle.benchmark_release_gate
        dataset_leakage_audit = benchmark_result.bundle.dataset_leakage_audit
        temporal_benchmark_recovery_report = benchmark_result.bundle.temporal_benchmark_recovery_report
        benchmark_pack_partition = benchmark_result.bundle.benchmark_pack_partition
        holdout_claim_policy = benchmark_result.bundle.holdout_claim_policy
        benchmark_generalization_audit = benchmark_result.bundle.benchmark_generalization_audit
        shadow_manifest = benchmark_result.bundle.shadow_trial_manifest
        promotion = benchmark_result.bundle.promotion_readiness_report
        quarantine = benchmark_result.bundle.candidate_quarantine
        from relaytic.analytics import read_architecture_routing_artifacts, read_temporal_engine_artifacts

        task_contract_bundle = read_task_contract_artifacts(root)
        eval_bundle = _read_json_bundle(root, bundle="evals")
        temporal_bundle = read_temporal_engine_artifacts(root)
        architecture_bundle = read_architecture_routing_artifacts(root)
        operating_point_bundle = {
            key: json.loads((root / filename).read_text(encoding="utf-8"))
            for key, filename in {
                "calibration_strategy_report": "calibration_strategy_report.json",
                "operating_point_contract": "operating_point_contract.json",
                "threshold_search_report": "threshold_search_report.json",
                "decision_cost_profile": "decision_cost_profile.json",
                "review_budget_optimization_report": "review_budget_optimization_report.json",
                "abstention_policy_report": "abstention_policy_report.json",
            }.items()
            if (root / filename).exists()
        }
        bundle_payload = benchmark_result.bundle.to_dict()
        bundle_payload.update(eval_bundle)
        bundle_payload.update(task_contract_bundle)
        bundle_payload.update(temporal_bundle)
        bundle_payload.update(architecture_bundle)
        bundle_payload.update(operating_point_bundle)
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "benchmark": {
                    "parity_status": parity.parity_status,
                    "recommended_action": parity.recommended_action,
                    "comparison_metric": parity.comparison_metric,
                    "winning_family": parity.winning_family,
                    "reference_count": parity.reference_count,
                    "test_gap": gap.test_gap,
                    "near_parity": gap.near_parity,
                    "incumbent_present": parity.incumbent_present,
                    "incumbent_name": parity.incumbent_name,
                    "incumbent_parity_status": incumbent.parity_status,
                    "beat_target_state": beat_target.contract_state,
                    "relaytic_beats_incumbent": incumbent.relaytic_beats_incumbent,
                    "incumbent_stronger": incumbent.incumbent_stronger,
                    "paper_status": paper_manifest.status,
                    "claim_gate_status": benchmark_release_gate.status,
                    "safe_to_cite_publicly": benchmark_release_gate.safe_to_cite_publicly,
                    "demo_safe": benchmark_release_gate.demo_safe,
                    "blocked_reason_count": len(benchmark_release_gate.blocked_reason_codes),
                    "rerun_match_count": rerun_variance.matching_run_count,
                    "rerun_stability_band": rerun_variance.stability_band,
                    "competitiveness_claim": claims.competitiveness_claim,
                    "deployment_claim": claims.deployment_claim,
                    "below_reference": claims.below_reference,
                    "imported_candidate_count": shadow_manifest.candidate_count,
                    "promotion_ready_count": promotion.promotion_ready_count,
                    "candidate_available_count": promotion.candidate_available_count,
                    "quarantined_candidate_count": quarantine.quarantined_count,
                    "objective_alignment_status": task_contract_bundle.get("objective_alignment_report", {}).get("status"),
                    "truth_precheck_status": task_contract_bundle.get("benchmark_truth_precheck", {}).get("status"),
                    "safe_to_rank": task_contract_bundle.get("benchmark_truth_precheck", {}).get("safe_to_rank"),
                    "truth_audit_status": benchmark_truth_audit.status,
                    "leakage_status": dataset_leakage_audit.status,
                    "temporal_recovery_status": temporal_benchmark_recovery_report.recovery_state,
                    "pack_partition": benchmark_pack_partition.partition_name,
                    "claim_origin": holdout_claim_policy.claim_origin,
                    "paper_primary_claim_allowed": holdout_claim_policy.paper_primary_claim_allowed,
                    "benchmark_generalization_status": benchmark_generalization_audit.status,
                    "identity_branching_detected": benchmark_generalization_audit.identity_branching_detected,
                    "split_diagnostics_status": task_contract_bundle.get("split_diagnostics_report", {}).get("status"),
                    "temporal_fold_status": task_contract_bundle.get("temporal_fold_health", {}).get("status"),
                    "selected_threshold": operating_point_bundle.get("operating_point_contract", {}).get("selected_threshold"),
                    "selected_calibration_method": operating_point_bundle.get("calibration_strategy_report", {}).get("selected_method"),
                },
                "bundle": bundle_payload,
            },
            "human_output": benchmark_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_benchmark_surface(*, run_dir: str | Path) -> dict[str, Any]:
    from relaytic.analytics import read_task_contract_artifacts

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="benchmark")
    if not bundle:
        raise ValueError(f"No Slice 11 benchmark artifacts found in {root}.")
    sync_materialization_runtime_artifacts(root)
    _load_or_materialize_summary(run_dir=root)
    manifest_path = _refresh_benchmark_manifest(root)
    parity = dict(bundle.get("benchmark_parity_report", {}))
    gap = dict(bundle.get("benchmark_gap_report", {}))
    incumbent = dict(bundle.get("incumbent_parity_report", {}))
    beat_target = dict(bundle.get("beat_target_contract", {}))
    paper_manifest = dict(bundle.get("paper_benchmark_manifest", {}))
    rerun_variance = dict(bundle.get("rerun_variance_report", {}))
    claims = dict(bundle.get("benchmark_claims_report", {}))
    benchmark_truth_audit = dict(bundle.get("benchmark_truth_audit", {}))
    benchmark_release_gate = dict(bundle.get("benchmark_release_gate", {}))
    dataset_leakage_audit = dict(bundle.get("dataset_leakage_audit", {}))
    temporal_benchmark_recovery_report = dict(bundle.get("temporal_benchmark_recovery_report", {}))
    benchmark_pack_partition = dict(bundle.get("benchmark_pack_partition", {}))
    holdout_claim_policy = dict(bundle.get("holdout_claim_policy", {}))
    benchmark_generalization_audit = dict(bundle.get("benchmark_generalization_audit", {}))
    shadow_manifest = dict(bundle.get("shadow_trial_manifest", {}))
    promotion = dict(bundle.get("promotion_readiness_report", {}))
    quarantine = dict(bundle.get("candidate_quarantine", {}))
    from relaytic.analytics import read_architecture_routing_artifacts, read_temporal_engine_artifacts

    task_contract_bundle = read_task_contract_artifacts(root)
    eval_bundle = _read_json_bundle(root, bundle="evals")
    temporal_bundle = read_temporal_engine_artifacts(root)
    architecture_bundle = read_architecture_routing_artifacts(root)
    operating_point_bundle = {
        key: json.loads((root / filename).read_text(encoding="utf-8"))
        for key, filename in {
            "calibration_strategy_report": "calibration_strategy_report.json",
            "operating_point_contract": "operating_point_contract.json",
            "threshold_search_report": "threshold_search_report.json",
            "decision_cost_profile": "decision_cost_profile.json",
            "review_budget_optimization_report": "review_budget_optimization_report.json",
            "abstention_policy_report": "abstention_policy_report.json",
        }.items()
        if (root / filename).exists()
    }
    bundle_payload = dict(bundle)
    bundle_payload.update(eval_bundle)
    bundle_payload.update(task_contract_bundle)
    bundle_payload.update(temporal_bundle)
    bundle_payload.update(architecture_bundle)
    bundle_payload.update(operating_point_bundle)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "benchmark": {
                "parity_status": parity.get("parity_status"),
                "recommended_action": parity.get("recommended_action"),
                "comparison_metric": parity.get("comparison_metric"),
                "winning_family": parity.get("winning_family"),
                "reference_count": int(parity.get("reference_count", 0) or 0),
                "test_gap": gap.get("test_gap"),
                "near_parity": gap.get("near_parity"),
                "incumbent_present": parity.get("incumbent_present"),
                "incumbent_name": parity.get("incumbent_name"),
                "incumbent_parity_status": incumbent.get("parity_status"),
                "beat_target_state": beat_target.get("contract_state") or parity.get("beat_target_state"),
                "relaytic_beats_incumbent": incumbent.get("relaytic_beats_incumbent"),
                "incumbent_stronger": incumbent.get("incumbent_stronger"),
                "paper_status": paper_manifest.get("status"),
                "claim_gate_status": benchmark_release_gate.get("status"),
                "safe_to_cite_publicly": benchmark_release_gate.get("safe_to_cite_publicly"),
                "demo_safe": benchmark_release_gate.get("demo_safe"),
                "blocked_reason_count": len(benchmark_release_gate.get("blocked_reason_codes", []))
                if isinstance(benchmark_release_gate.get("blocked_reason_codes"), list)
                else 0,
                "rerun_match_count": int(rerun_variance.get("matching_run_count", 0) or 0),
                "rerun_stability_band": rerun_variance.get("stability_band"),
                "competitiveness_claim": claims.get("competitiveness_claim"),
                "deployment_claim": claims.get("deployment_claim"),
                "below_reference": claims.get("below_reference"),
                "imported_candidate_count": int(shadow_manifest.get("candidate_count", 0) or 0),
                "promotion_ready_count": int(promotion.get("promotion_ready_count", 0) or 0),
                "candidate_available_count": int(promotion.get("candidate_available_count", 0) or 0),
                "quarantined_candidate_count": int(quarantine.get("quarantined_count", 0) or 0),
                "objective_alignment_status": task_contract_bundle.get("objective_alignment_report", {}).get("status"),
                "truth_precheck_status": task_contract_bundle.get("benchmark_truth_precheck", {}).get("status"),
                "safe_to_rank": task_contract_bundle.get("benchmark_truth_precheck", {}).get("safe_to_rank"),
                "truth_audit_status": benchmark_truth_audit.get("status"),
                "leakage_status": dataset_leakage_audit.get("status"),
                "temporal_recovery_status": temporal_benchmark_recovery_report.get("recovery_state") or temporal_benchmark_recovery_report.get("status"),
                "pack_partition": benchmark_pack_partition.get("partition_name"),
                "claim_origin": holdout_claim_policy.get("claim_origin") or benchmark_pack_partition.get("claim_origin"),
                "paper_primary_claim_allowed": holdout_claim_policy.get("paper_primary_claim_allowed"),
                "benchmark_generalization_status": benchmark_generalization_audit.get("status"),
                "identity_branching_detected": benchmark_generalization_audit.get("identity_branching_detected"),
                "split_diagnostics_status": task_contract_bundle.get("split_diagnostics_report", {}).get("status"),
                "temporal_fold_status": task_contract_bundle.get("temporal_fold_health", {}).get("status"),
                "selected_threshold": operating_point_bundle.get("operating_point_contract", {}).get("selected_threshold"),
                "selected_calibration_method": operating_point_bundle.get("calibration_strategy_report", {}).get("selected_method"),
            },
            "bundle": bundle_payload,
        },
        "human_output": render_benchmark_review_markdown(bundle_payload),
    }


def _run_decision_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.decision import run_decision_review, write_decision_bundle

    root = Path(run_dir)
    targets = _decision_output_paths(root)
    if not overwrite and all(path.exists() for path in targets.values()):
        return _show_decision_surface(run_dir=root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    planning_bundle = _read_json_bundle(root, bundle="planning")
    plan = dict(planning_bundle.get("plan", {}))
    if not plan or not dict(plan.get("execution_summary", {})):
        raise ValueError(f"Slice 10A decision review requires executed planning artifacts in {root}.")
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="decision",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "benchmark_parity_report.json",
            "quality_contract.json",
            "quality_gate_report.json",
            "override_decision.json",
            "route_prior_context.json",
            "research_brief.json",
            "semantic_debate_report.json",
            "plan.json",
        ],
    )
    try:
        decision_result = run_decision_review(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            context_bundle=_read_json_bundle(root, bundle="context"),
            investigation_bundle=_read_json_bundle(root, bundle="investigation"),
            planning_bundle=planning_bundle,
            memory_bundle=_read_json_bundle(root, bundle="memory"),
            intelligence_bundle=_read_json_bundle(root, bundle="intelligence"),
            research_bundle=_read_json_bundle(root, bundle="research"),
            benchmark_bundle=_read_json_bundle(root, bundle="benchmark"),
            profiles_bundle=_read_json_bundle(root, bundle="profiles"),
            control_bundle=_read_json_bundle(root, bundle="control"),
            completion_bundle=_read_json_bundle(root, bundle="completion"),
            lifecycle_bundle=_read_json_bundle(root, bundle="lifecycle"),
            autonomy_bundle=_read_json_bundle(root, bundle="autonomy"),
            permission_bundle=_read_json_bundle(root, bundle="permissions"),
            daemon_bundle=_read_json_bundle(root, bundle="daemon"),
            result_contract_bundle=read_result_contract_artifacts(root),
            iteration_bundle=read_iteration_bundle(workspace_dir=default_workspace_dir(run_dir=root), run_dir=root),
        )
        written = write_decision_bundle(root, bundle=decision_result.bundle)
        manifest_path = _refresh_decision_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic modeled the decision environment, controller path, local data opportunities, and compiled executable challenger and feature proposals.",
        )
        materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "decision_lab": {
                    "action_regime": decision_result.bundle.decision_world_model.action_regime,
                    "threshold_posture": decision_result.bundle.decision_world_model.threshold_posture,
                    "under_specified": decision_result.bundle.decision_world_model.under_specified,
                    "selected_strategy": decision_result.selected_strategy,
                    "next_actor": decision_result.next_actor,
                    "selected_next_action": decision_result.selected_next_action,
                    "controller_selected_action": decision_result.bundle.controller_policy.selected_next_action,
                    "review_required": decision_result.bundle.controller_policy.review_required,
                    "changed_next_action": decision_result.changed_next_action,
                    "changed_controller_path": decision_result.changed_controller_path,
                    "join_candidate_count": decision_result.bundle.join_candidate_report.candidate_count,
                    "compiled_challenger_count": decision_result.bundle.method_compiler_report.compiled_challenger_count,
                    "compiled_feature_count": decision_result.bundle.method_compiler_report.compiled_feature_count,
                    "imported_candidate_count": decision_result.bundle.method_import_report.imported_family_count,
                    "shadow_only_import_count": decision_result.bundle.method_import_report.shadow_only_count,
                },
                "feasibility": {
                    "trajectory_status": decision_result.bundle.trajectory_constraint_report.trajectory_status,
                    "region_posture": decision_result.bundle.feasible_region_map.region_posture,
                    "risk_band": decision_result.bundle.extrapolation_risk_report.risk_band,
                    "recommended_direction": decision_result.bundle.decision_constraint_report.recommended_direction,
                    "deployability": decision_result.bundle.deployability_assessment.deployability,
                    "gate_open": decision_result.bundle.review_gate_state.gate_open,
                    "override_required": decision_result.bundle.constraint_override_request.override_required,
                },
                "bundle": decision_result.bundle.to_dict(),
            },
            "human_output": decision_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_decision_surface(*, run_dir: str | Path) -> dict[str, Any]:
    from relaytic.decision import render_decision_review_markdown

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="decision")
    if not bundle:
        raise ValueError(f"No Slice 10A decision artifacts found in {root}.")
    materialize_run_summary(run_dir=root)
    manifest_path = _refresh_decision_manifest(root)
    world = dict(bundle.get("decision_world_model", {}))
    controller = dict(bundle.get("controller_policy", {}))
    usefulness = dict(bundle.get("decision_usefulness_report", {}))
    constraints = dict(bundle.get("decision_constraint_report", {}))
    trajectory = dict(bundle.get("trajectory_constraint_report", {}))
    feasible_region = dict(bundle.get("feasible_region_map", {}))
    extrapolation = dict(bundle.get("extrapolation_risk_report", {}))
    deployability = dict(bundle.get("deployability_assessment", {}))
    review_gate = dict(bundle.get("review_gate_state", {}))
    override_request = dict(bundle.get("constraint_override_request", {}))
    value_report = dict(bundle.get("value_of_more_data_report", {}))
    join_report = dict(bundle.get("join_candidate_report", {}))
    compiler = dict(bundle.get("method_compiler_report", {}))
    method_import = dict(bundle.get("method_import_report", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "decision_lab": {
                "action_regime": world.get("action_regime"),
                "threshold_posture": world.get("threshold_posture"),
                "under_specified": world.get("under_specified"),
                "selected_strategy": value_report.get("selected_strategy"),
                "next_actor": controller.get("next_actor"),
                "selected_next_action": constraints.get("feasible_selected_action") or controller.get("selected_next_action"),
                "controller_selected_action": controller.get("selected_next_action"),
                "review_required": controller.get("review_required"),
                "changed_next_action": usefulness.get("changed_next_action"),
                "changed_controller_path": usefulness.get("changed_controller_path"),
                "join_candidate_count": int(join_report.get("candidate_count", 0) or 0),
                "compiled_challenger_count": int(compiler.get("compiled_challenger_count", 0) or 0),
                "compiled_feature_count": int(compiler.get("compiled_feature_count", 0) or 0),
                "imported_candidate_count": int(method_import.get("imported_family_count", 0) or 0),
                "shadow_only_import_count": int(method_import.get("shadow_only_count", 0) or 0),
            },
            "feasibility": {
                "trajectory_status": trajectory.get("trajectory_status"),
                "region_posture": feasible_region.get("region_posture"),
                "risk_band": extrapolation.get("risk_band"),
                "recommended_direction": constraints.get("recommended_direction"),
                "deployability": deployability.get("deployability"),
                "gate_open": review_gate.get("gate_open"),
                "override_required": override_request.get("override_required"),
            },
            "bundle": bundle,
        },
        "human_output": render_decision_review_markdown(bundle),
    }


def _run_dojo_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.dojo import write_dojo_bundle

    root = Path(run_dir)
    targets = _dojo_output_paths(root)
    if not overwrite and all(path.exists() for path in targets.values()):
        return _show_dojo_surface(run_dir=root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    planning_bundle = _read_json_bundle(root, bundle="planning")
    plan = dict(planning_bundle.get("plan", {}))
    if not plan or not dict(plan.get("execution_summary", {})):
        raise ValueError(f"Slice 12 dojo review requires executed planning artifacts in {root}.")
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="dojo",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "plan.json",
            "benchmark_parity_report.json",
            "beat_target_contract.json",
            "quality_gate_report.json",
            "control_injection_audit.json",
            "method_compiler_report.json",
        ],
    )
    try:
        dojo_result = run_dojo_review(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            planning_bundle=planning_bundle,
            research_bundle=_read_json_bundle(root, bundle="research"),
            benchmark_bundle=_read_json_bundle(root, bundle="benchmark"),
            decision_bundle=_read_json_bundle(root, bundle="decision"),
            profiles_bundle=_read_json_bundle(root, bundle="profiles"),
            control_bundle=_read_json_bundle(root, bundle="control"),
        )
        written = write_dojo_bundle(root, bundle=dojo_result.bundle)
        manifest_path = _refresh_dojo_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic evaluated quarantined self-improvement proposals against benchmark, quality, and skeptical-control gates before recording explicit promotions, rejections, and rollback-ready ledgers.",
        )
        materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        session = dojo_result.bundle.dojo_session
        results = dojo_result.bundle.dojo_results
        promotions = dojo_result.bundle.dojo_promotions
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "dojo": {
                    "status": session.status,
                    "benchmark_state": session.benchmark_state,
                    "quality_gate_status": session.quality_gate_status,
                    "control_security_state": session.control_security_state,
                    "active_promotion_count": session.active_promotion_count,
                    "rejected_count": results.rejected_count,
                    "quarantined_count": results.quarantined_count,
                    "rolled_back_count": len(promotions.rolled_back_promotions),
                },
                "bundle": dojo_result.bundle.to_dict(),
            },
            "human_output": dojo_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_dojo_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="dojo")
    if not bundle:
        raise ValueError(f"No Slice 12 dojo artifacts found in {root}.")
    materialize_run_summary(run_dir=root)
    manifest_path = _refresh_dojo_manifest(root)
    session = dict(bundle.get("dojo_session", {}))
    results = dict(bundle.get("dojo_results", {}))
    promotions = dict(bundle.get("dojo_promotions", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "dojo": {
                "status": session.get("status"),
                "benchmark_state": session.get("benchmark_state"),
                "quality_gate_status": session.get("quality_gate_status"),
                "control_security_state": session.get("control_security_state"),
                "active_promotion_count": int(session.get("active_promotion_count", 0) or 0),
                "rejected_count": int(results.get("rejected_count", 0) or 0),
                "quarantined_count": int(results.get("quarantined_count", 0) or 0),
                "rolled_back_count": len(promotions.get("rolled_back_promotions", [])),
            },
            "bundle": bundle,
        },
        "human_output": render_dojo_review_markdown(bundle),
    }


def _run_pulse_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.pulse import write_pulse_bundle

    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    effective_policy = foundation_state["resolved"].policy
    effective_policy_source: str | Path = foundation_state["policy_path"]
    if config_path:
        resolved_override = load_policy(config_path)
        effective_policy = resolved_override.policy
        effective_policy_source = config_path
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=effective_policy,
        stage="pulse",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "run_summary.json",
            "benchmark_parity_report.json",
            "research_source_inventory.json",
            "control_injection_audit.json",
            "memory_retrieval.json",
            "dojo_session.json",
        ],
    )
    try:
        pulse_result = run_pulse_review(
            run_dir=root,
            policy=effective_policy,
            trigger_kind="manual",
        )
        written = write_pulse_bundle(root, bundle=pulse_result.bundle)
        manifest_path = _refresh_pulse_manifest(
            root,
            run_id=run_id,
            policy_source=effective_policy_source,
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=effective_policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic pulse inspected local state, wrote explicit skip/recommend/action artifacts, and only performed bounded low-risk follow-up when policy allowed it.",
        )
        summary_bundle = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        run_report = pulse_result.bundle.pulse_run_report
        skip_report = pulse_result.bundle.pulse_skip_report
        recommendations = pulse_result.bundle.pulse_recommendations
        innovation = pulse_result.bundle.innovation_watch_report
        watchlist = pulse_result.bundle.challenge_watchlist
        compaction = pulse_result.bundle.memory_compaction_report
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "pulse": {
                    "status": run_report.status,
                    "mode": pulse_result.bundle.pulse_schedule.mode,
                    "skip_reason": skip_report.skip_reason,
                    "recommendation_count": run_report.recommendation_count,
                    "watchlist_count": run_report.watchlist_count,
                    "innovation_lead_count": run_report.innovation_lead_count,
                    "queued_action_count": len(recommendations.queued_actions),
                    "executed_action_count": len(run_report.executed_actions),
                    "memory_pinned_count": run_report.memory_pinned_count,
                    "redacted_innovation": not innovation.raw_rows_exported and not innovation.identifier_leak_detected,
                    "compaction_executed": compaction.executed,
                    "top_watch_kind": (watchlist.items[0].get("watch_kind") if watchlist.items else None),
                },
                "bundle": pulse_result.bundle.to_dict(),
                "run_summary": summary_bundle["summary"],
            },
            "human_output": pulse_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=effective_policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_pulse_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="pulse")
    if not bundle:
        raise ValueError(f"No Slice 12A pulse artifacts found in {root}.")
    materialize_run_summary(run_dir=root)
    manifest_path = _refresh_pulse_manifest(root)
    schedule = dict(bundle.get("pulse_schedule", {}))
    run_report = dict(bundle.get("pulse_run_report", {}))
    skip_report = dict(bundle.get("pulse_skip_report", {}))
    recommendations = dict(bundle.get("pulse_recommendations", {}))
    innovation = dict(bundle.get("innovation_watch_report", {}))
    watchlist = dict(bundle.get("challenge_watchlist", {}))
    compaction = dict(bundle.get("memory_compaction_report", {}))
    pinning = dict(bundle.get("memory_pinning_index", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "pulse": {
                "status": run_report.get("status"),
                "mode": schedule.get("mode"),
                "skip_reason": skip_report.get("skip_reason"),
                "due_now": schedule.get("due_now"),
                "throttled": schedule.get("throttled"),
                "recommendation_count": run_report.get("recommendation_count"),
                "watchlist_count": run_report.get("watchlist_count"),
                "innovation_lead_count": run_report.get("innovation_lead_count"),
                "queued_action_count": len(recommendations.get("queued_actions", []))
                if isinstance(recommendations.get("queued_actions"), list)
                else 0,
                "memory_pinned_count": pinning.get("pin_count"),
                "compaction_executed": compaction.get("executed"),
                "redacted_innovation": not bool(innovation.get("raw_rows_exported")) and not bool(innovation.get("identifier_leak_detected")),
            },
            "bundle": bundle,
        },
        "human_output": render_pulse_review_markdown(bundle),
    }


def _materialize_trace_bundle(*, run_dir: Path, config_path: str | None) -> tuple[dict[str, Any], dict[str, Any], str | Path]:
    from relaytic.tracing import run_trace_review, write_trace_bundle

    foundation_state = _ensure_run_foundation_present(
        run_dir=run_dir,
        config_path=config_path,
        run_id=None,
        labels=None,
    )
    effective_policy = foundation_state["resolved"].policy
    effective_policy_source: str | Path = foundation_state["policy_path"]
    if config_path:
        resolved_override = load_policy(config_path)
        effective_policy = resolved_override.policy
        effective_policy_source = config_path
    trace_result = run_trace_review(run_dir=run_dir, policy=effective_policy)
    written = write_trace_bundle(run_dir, bundle=trace_result.bundle)
    sync_materialization_runtime_artifacts(run_dir)
    return trace_result.bundle.to_dict(), written, effective_policy_source


def _show_trace_surface(*, run_dir: str | Path, config_path: str | None = None) -> dict[str, Any]:
    from relaytic.tracing import render_trace_review_markdown

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="trace")
    effective_policy_source: str | Path | None = None
    if (
        not bundle
        or not isinstance(bundle.get("trace_model"), dict)
        or not bundle.get("trace_model")
    ):
        bundle, _, effective_policy_source = _materialize_trace_bundle(run_dir=root, config_path=config_path)
    summary_materialized = _load_or_materialize_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    manifest_path = _refresh_trace_manifest(root, policy_source=effective_policy_source)
    trace_model = dict(bundle.get("trace_model", {}))
    adjudication = dict(bundle.get("adjudication_scorecard", {}))
    replay = dict(bundle.get("decision_replay_report", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(summary_materialized["report_path"]),
            "trace": {
                "status": trace_model.get("status"),
                "span_count": trace_model.get("span_count"),
                "claim_count": trace_model.get("claim_count"),
                "winning_claim_id": adjudication.get("winning_claim_id"),
                "winning_action": adjudication.get("winning_action"),
                "competing_claim_count": replay.get("competing_claim_count"),
                "direct_runtime_emission_detected": trace_model.get("direct_runtime_emission_detected"),
            },
            "bundle": bundle,
            "run_summary": summary_materialized["summary"],
        },
        "human_output": render_trace_review_markdown(bundle),
    }


def _replay_trace_surface(*, run_dir: str | Path, config_path: str | None = None) -> dict[str, Any]:
    from relaytic.tracing import render_trace_replay_markdown

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="trace")
    effective_policy_source: str | Path | None = None
    if (
        not bundle
        or not isinstance(bundle.get("decision_replay_report"), dict)
        or not bundle.get("decision_replay_report")
    ):
        bundle, _, effective_policy_source = _materialize_trace_bundle(run_dir=root, config_path=config_path)
    summary_materialized = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    manifest_path = _refresh_trace_manifest(root, policy_source=effective_policy_source)
    replay = dict(bundle.get("decision_replay_report", {}))
    adjudication = dict(bundle.get("adjudication_scorecard", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(summary_materialized["report_path"]),
            "trace": {
                "winning_claim_id": adjudication.get("winning_claim_id"),
                "winning_action": adjudication.get("winning_action"),
                "competing_claim_count": replay.get("competing_claim_count"),
                "timeline_count": len(replay.get("timeline", [])) if isinstance(replay.get("timeline"), list) else 0,
                "status": replay.get("status"),
            },
            "bundle": bundle,
            "run_summary": summary_materialized["summary"],
        },
        "human_output": render_trace_replay_markdown(bundle),
    }


def _run_evals_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.evals import run_agent_evals, write_eval_bundle

    root = Path(run_dir)
    targets = _evals_output_paths(root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    effective_policy = foundation_state["resolved"].policy
    effective_policy_source: str | Path = foundation_state["policy_path"]
    if config_path:
        resolved_override = load_policy(config_path)
        effective_policy = resolved_override.policy
        effective_policy_source = config_path
    trace_bundle = _read_json_bundle(root, bundle="trace")
    if not trace_bundle or not isinstance(trace_bundle.get("adjudication_scorecard"), dict) or not trace_bundle.get("adjudication_scorecard"):
        _materialize_trace_bundle(run_dir=root, config_path=config_path)
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=effective_policy,
        stage="evals",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "trace_model.json",
            "adjudication_scorecard.json",
            "decision_replay_report.json",
            "protocol_conformance_report.json",
            "run_summary.json",
        ],
    )
    try:
        eval_result = run_agent_evals(run_dir=root, policy=effective_policy)
        written = write_eval_bundle(root, bundle=eval_result.bundle)
        manifest_path = _refresh_evals_manifest(
            root,
            run_id=run_id,
            policy_source=effective_policy_source,
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=effective_policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic compared CLI and MCP host surfaces against the same trace truth, scored deterministic-debate proof cases, and recorded explicit security and red-team eval artifacts.",
        )
        summary_bundle = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        matrix = eval_result.bundle.agent_eval_matrix
        protocol = eval_result.bundle.protocol_conformance_report
        security = eval_result.bundle.security_eval_report
        red_team = eval_result.bundle.red_team_report
        trace_identity = eval_result.bundle.trace_identity_conformance
        surface_parity = eval_result.bundle.eval_surface_parity_report
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "evals": {
                    "status": matrix.status,
                    "passed_count": matrix.passed_count,
                    "failed_count": matrix.failed_count,
                    "not_applicable_count": matrix.not_applicable_count,
                    "protocol_status": protocol.status,
                    "protocol_mismatch_count": protocol.mismatch_count,
                    "security_status": security.status,
                    "security_open_finding_count": security.open_finding_count,
                    "red_team_status": red_team.status,
                    "red_team_finding_count": red_team.finding_count,
                    "trace_identity_status": trace_identity.status,
                    "trace_identity_mismatch_count": trace_identity.mismatch_count,
                    "surface_parity_status": surface_parity.status,
                    "surface_parity_mismatch_count": surface_parity.mismatch_count,
                },
                "bundle": eval_result.bundle.to_dict(),
                "run_summary": summary_bundle["summary"],
            },
            "human_output": eval_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=effective_policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_evals_surface(*, run_dir: str | Path, config_path: str | None = None) -> dict[str, Any]:
    from relaytic.evals import render_eval_review_markdown

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="evals")
    if not bundle or not isinstance(bundle.get("agent_eval_matrix"), dict) or not bundle.get("agent_eval_matrix"):
        payload = _run_evals_phase(
            run_dir=root,
            config_path=config_path,
            run_id=None,
            overwrite=True,
            labels=None,
        )
        return {
            "surface_payload": payload["surface_payload"],
            "human_output": payload["human_output"],
        }
    summary_materialized = _load_or_materialize_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    manifest_path = _refresh_evals_manifest(root)
    matrix = dict(bundle.get("agent_eval_matrix", {}))
    protocol = dict(bundle.get("protocol_conformance_report", {}))
    security = dict(bundle.get("security_eval_report", {}))
    red_team = dict(bundle.get("red_team_report", {}))
    trace_identity = dict(bundle.get("trace_identity_conformance", {}))
    surface_parity = dict(bundle.get("eval_surface_parity_report", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(summary_materialized["report_path"]),
            "evals": {
                "status": matrix.get("status"),
                "passed_count": matrix.get("passed_count"),
                "failed_count": matrix.get("failed_count"),
                "not_applicable_count": matrix.get("not_applicable_count"),
                "protocol_status": protocol.get("status"),
                "protocol_mismatch_count": protocol.get("mismatch_count"),
                "security_status": security.get("status"),
                "security_open_finding_count": security.get("open_finding_count"),
                "red_team_status": red_team.get("status"),
                "red_team_finding_count": red_team.get("finding_count"),
                "trace_identity_status": trace_identity.get("status"),
                "trace_identity_mismatch_count": trace_identity.get("mismatch_count"),
                "surface_parity_status": surface_parity.get("status"),
                "surface_parity_mismatch_count": surface_parity.get("mismatch_count"),
            },
            "bundle": bundle,
            "run_summary": summary_materialized["summary"],
        },
        "human_output": render_eval_review_markdown(bundle),
    }


def _run_dojo_rollback(
    *,
    run_dir: str | Path,
    proposal_id: str,
    reason: str | None,
    config_path: str | None,
    run_id: str | None,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.dojo import write_dojo_bundle

    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="dojo",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "dojo_session.json",
            "dojo_results.json",
            "dojo_promotions.json",
        ],
    )
    try:
        dojo_result = rollback_dojo_promotion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            proposal_id=proposal_id,
            reason=reason,
        )
        written = write_dojo_bundle(root, bundle=dojo_result.bundle)
        manifest_path = _refresh_dojo_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary=f"Relaytic rolled back dojo proposal `{proposal_id}` while preserving promotion and rollback provenance.",
        )
        materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        return _show_dojo_surface(run_dir=root)
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _run_feedback_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.feedback import write_feedback_bundle

    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="feedback",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "feedback_intake.json",
            "benchmark_parity_report.json",
            "promotion_decision.json",
            "autonomy_loop_state.json",
            "run_summary.json",
        ],
    )
    try:
        feedback_result = run_feedback_review(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            evidence_bundle=_read_json_bundle(root, bundle="evidence"),
            completion_bundle=_read_json_bundle(root, bundle="completion"),
            lifecycle_bundle=_read_json_bundle(root, bundle="lifecycle"),
            autonomy_bundle=_read_json_bundle(root, bundle="autonomy"),
            benchmark_bundle=_read_json_bundle(root, bundle="benchmark"),
            memory_bundle=_read_json_bundle(root, bundle="memory"),
        )
        written = write_feedback_bundle(root, bundle=feedback_result.bundle)
        manifest_path = _refresh_feedback_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic validated feedback and downstream outcomes, wrote explicit effect reports, and preserved rollback-ready casebook state.",
        )
        materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        effect = feedback_result.bundle.feedback_effect_report
        validation = feedback_result.bundle.feedback_validation
        route_updates = feedback_result.bundle.route_prior_updates
        decision_updates = feedback_result.bundle.decision_policy_update_suggestions
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "feedback": {
                    "accepted_count": validation.accepted_count,
                    "rejected_count": validation.rejected_count,
                    "reverted_count": validation.reverted_count,
                    "route_prior_update_count": len(route_updates.updates),
                    "decision_policy_suggestion_count": len(decision_updates.suggestions),
                    "primary_recommended_action": effect.primary_recommended_action,
                },
                "bundle": feedback_result.bundle.to_dict(),
            },
            "human_output": feedback_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_feedback_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="feedback")
    if not bundle:
        raise ValueError(f"No Slice 10 feedback artifacts found in {root}.")
    _load_or_materialize_summary(run_dir=root)
    manifest_path = _refresh_feedback_manifest(root)
    validation = dict(bundle.get("feedback_validation", {}))
    effect = dict(bundle.get("feedback_effect_report", {}))
    route_updates = dict(bundle.get("route_prior_updates", {}))
    decision_updates = dict(bundle.get("decision_policy_update_suggestions", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "feedback": {
                "accepted_count": int(validation.get("accepted_count", 0) or 0),
                "rejected_count": int(validation.get("rejected_count", 0) or 0),
                "reverted_count": int(validation.get("reverted_count", 0) or 0),
                "route_prior_update_count": len(route_updates.get("updates", [])),
                "decision_policy_suggestion_count": len(decision_updates.get("suggestions", [])),
                "primary_recommended_action": effect.get("primary_recommended_action"),
            },
            "bundle": bundle,
        },
        "human_output": render_feedback_review_markdown(bundle),
    }


def _run_profiles_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.profiles import write_profiles_bundle

    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="profiles",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "work_preferences.json",
            "lab_mandate.json",
            "task_brief.json",
            "focus_profile.json",
            "optimization_profile.json",
            "plan.json",
            "audit_report.json",
            "benchmark_parity_report.json",
            "loop_budget_report.json",
        ],
    )
    try:
        profiles_result = run_profiles_review(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            intake_bundle=_read_json_bundle(root, bundle="intake"),
            investigation_bundle=_read_json_bundle(root, bundle="investigation"),
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            evidence_bundle=_read_json_bundle(root, bundle="evidence"),
            benchmark_bundle=_read_json_bundle(root, bundle="benchmark"),
            completion_bundle=_read_json_bundle(root, bundle="completion"),
            lifecycle_bundle=_read_json_bundle(root, bundle="lifecycle"),
            autonomy_bundle=_read_json_bundle(root, bundle="autonomy"),
        )
        written = write_profiles_bundle(root, bundle=profiles_result.bundle)
        manifest_path = _refresh_profiles_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic materialized explicit quality and budget contracts, tracked configured versus consumed budget, and derived operator/lab posture without changing artifact truth.",
        )
        materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        quality_gate = profiles_result.bundle.quality_gate_report
        budget = profiles_result.bundle.budget_consumption_report
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "profiles": {
                    "quality_gate_status": quality_gate.gate_status,
                    "recommended_action": quality_gate.recommended_action,
                    "budget_health": budget.budget_health,
                    "observed_elapsed_minutes": budget.observed_elapsed_minutes,
                    "estimated_trials_consumed": budget.estimated_trials_consumed,
                    "remaining_trials": budget.remaining_trials,
                },
                "bundle": profiles_result.bundle.to_dict(),
            },
            "human_output": profiles_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_profiles_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="profiles")
    if not bundle:
        raise ValueError(f"No Slice 10B profile artifacts found in {root}.")
    materialize_run_summary(run_dir=root)
    manifest_path = _refresh_profiles_manifest(root)
    quality_gate = dict(bundle.get("quality_gate_report", {}))
    budget = dict(bundle.get("budget_consumption_report", {}))
    operator_profile = dict(bundle.get("operator_profile", {}))
    lab_profile = dict(bundle.get("lab_operating_profile", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "profiles": {
                "quality_gate_status": quality_gate.get("gate_status"),
                "recommended_action": quality_gate.get("recommended_action"),
                "budget_health": budget.get("budget_health"),
                "observed_elapsed_minutes": budget.get("observed_elapsed_minutes"),
                "estimated_trials_consumed": budget.get("estimated_trials_consumed"),
                "remaining_trials": budget.get("remaining_trials"),
                "operator_profile_name": operator_profile.get("profile_name"),
                "lab_profile_name": lab_profile.get("profile_name"),
            },
            "bundle": bundle,
        },
        "human_output": render_profiles_review_markdown(bundle),
    }


def _run_control_phase(
    *,
    run_dir: str | Path,
    message: str,
    action_kind: str,
    requested_stage: str | None,
    config_path: str | None,
    run_id: str | None,
    labels: dict[str, str] | None,
    actor_type: str = "user",
    actor_name: str | None = None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.control import write_control_bundle

    root = Path(run_dir)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    current_summary = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    stage_before = str(current_summary.get("stage_completed", "")).strip() or "unknown"
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="control",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "run_summary.json",
            "assist_mode.json",
            "assist_session_state.json",
            "feedback_casebook.json",
            "route_prior_updates.json",
            "benchmark_parity_report.json",
        ],
    )
    try:
        control_result = run_control_review(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            message=message,
            action_kind=action_kind,
            requested_stage=requested_stage,
            stage_before=stage_before,
            run_summary=current_summary,
            source_surface=runtime_surface,
            source_command=runtime_command,
            actor_type=actor_type,
            actor_name=actor_name,
        )
        written = write_control_bundle(root, bundle=control_result.bundle)
        manifest_path = _refresh_control_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic normalized one steering request, challenged material changes skeptically, preserved a replayable override decision, and refreshed causal steering memory.",
        )
        materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
        decision = control_result.bundle.override_decision
        challenge = control_result.bundle.control_challenge_report
        audit = control_result.bundle.control_injection_audit
        checkpoint = control_result.bundle.recovery_checkpoint
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "control": {
                    "decision": decision.decision,
                    "approved_action_kind": decision.approved_action_kind,
                    "approved_stage": decision.approved_stage,
                    "challenge_level": challenge.challenge_level,
                    "skepticism_level": challenge.skepticism_level,
                    "similar_harmful_override_count": challenge.similar_harmful_override_count,
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "suspicious_count": audit.suspicious_count,
                },
                "bundle": control_result.bundle.to_dict(),
            },
            "human_output": control_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_control_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="control")
    if not bundle:
        raise ValueError(f"No Slice 10C control artifacts found in {root}.")
    materialize_run_summary(run_dir=root)
    manifest_path = _refresh_control_manifest(root)
    decision = dict(bundle.get("override_decision", {}))
    challenge = dict(bundle.get("control_challenge_report", {}))
    audit = dict(bundle.get("control_injection_audit", {}))
    checkpoint = dict(bundle.get("recovery_checkpoint", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "control": {
                "decision": decision.get("decision"),
                "approved_action_kind": decision.get("approved_action_kind"),
                "approved_stage": decision.get("approved_stage"),
                "challenge_level": challenge.get("challenge_level"),
                "skepticism_level": challenge.get("skepticism_level"),
                "similar_harmful_override_count": challenge.get("similar_harmful_override_count"),
                "checkpoint_id": checkpoint.get("checkpoint_id"),
                "suspicious_count": audit.get("suspicious_count"),
            },
            "bundle": bundle,
        },
        "human_output": render_control_review_markdown(bundle),
    }


def _render_research_sources_markdown(inventory: dict[str, Any]) -> str:
    sources = list(inventory.get("sources", []))
    lines = [
        "# Relaytic Research Sources",
        "",
        f"- Source inventory status: `{inventory.get('status') or 'unknown'}`",
        f"- Source count: `{len(sources)}`",
    ]
    if sources:
        lines.extend(["", "## Sources"])
        for item in sources[:10]:
            title = str(item.get("title", "")).strip() or "Untitled source"
            provider = str(item.get("provider", "")).strip() or "unknown"
            source_type = str(item.get("source_type", "")).strip() or "unknown"
            year = str(item.get("year", "")).strip() or "n/a"
            lines.append(f"- `{provider}` `{source_type}` `{year}`: {title}")
    return "\n".join(lines).rstrip() + "\n"


def _show_evidence_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = read_evidence_bundle(root)
    if not bundle:
        raise ValueError(f"No Slice 06 evidence artifacts found in {root}.")
    summary_materialized = materialize_run_summary(run_dir=root)
    decision_memo_path = root / "reports" / "decision_memo.md"
    if decision_memo_path.exists():
        human_output = decision_memo_path.read_text(encoding="utf-8")
    else:
        human_output = summary_materialized["report_markdown"]
    manifest_path = _refresh_evidence_manifest(root)
    audit_report = dict(bundle.get("audit_report", {}))
    belief_update = dict(bundle.get("belief_update", {}))
    challenger_report = dict(bundle.get("challenger_report", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(decision_memo_path if decision_memo_path.exists() else summary_materialized["report_path"]),
            "evidence": {
                "provisional_recommendation": audit_report.get("provisional_recommendation"),
                "readiness_level": audit_report.get("readiness_level"),
                "challenger_winner": challenger_report.get("winner"),
                "recommended_action": belief_update.get("recommended_action"),
            },
            "bundle": bundle,
        },
        "human_output": human_output,
    }


def _run_completion_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.completion import write_completion_bundle

    root = Path(run_dir)
    targets = _completion_output_paths(root)
    completion_stage = stage_recompute_entry(root, stage="completion")
    if not overwrite and bool(completion_stage.get("reusable", False)):
        return _show_completion_status(run_dir=root)
    _ensure_paths_absent(
        list(targets.values()),
        overwrite=overwrite or str(completion_stage.get("status", "")).strip() != "fresh",
    )
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    evidence_bundle = _read_json_bundle(root, bundle="evidence")
    if not evidence_bundle:
        raise ValueError(f"Slice 07 completion requires Slice 06 evidence artifacts in {root}.")
    memory_bundle = _read_json_bundle(root, bundle="memory")
    if not memory_bundle:
        _run_memory_phase(
            run_dir=root,
            data_path=_resolve_run_data_path(root),
            config_path=config_path,
            run_id=run_id,
            labels=labels,
            search_roots=None,
            runtime_surface=runtime_surface,
            runtime_command=runtime_command,
        )
        memory_bundle = _read_json_bundle(root, bundle="memory")
    intelligence_bundle = _read_json_bundle(root, bundle="intelligence")
    if not intelligence_bundle:
        _run_intelligence_phase(
            run_dir=root,
            config_path=config_path,
            run_id=run_id,
            overwrite=overwrite,
            labels=labels,
            runtime_surface=runtime_surface,
            runtime_command=runtime_command,
        )
        intelligence_bundle = _read_json_bundle(root, bundle="intelligence")
    research_bundle = _read_json_bundle(root, bundle="research")
    if not research_bundle:
        _run_research_phase(
            run_dir=root,
            config_path=config_path,
            run_id=run_id,
            overwrite=overwrite,
            labels=labels,
            runtime_surface=runtime_surface,
            runtime_command=runtime_command,
        )
        research_bundle = _read_json_bundle(root, bundle="research")
    incumbent_config = _resolve_existing_incumbent_config(root)
    benchmark_bundle = _read_json_bundle(root, bundle="benchmark")
    if not benchmark_bundle:
        _run_benchmark_phase(
            run_dir=root,
            data_path=_resolve_run_data_path(root),
            config_path=config_path,
            run_id=run_id,
            overwrite=overwrite,
            labels=labels,
            incumbent_path=incumbent_config.get("incumbent_path"),
            incumbent_kind=incumbent_config.get("incumbent_kind"),
            incumbent_name=incumbent_config.get("incumbent_name"),
            runtime_surface=runtime_surface,
            runtime_command=runtime_command,
        )
        benchmark_bundle = _read_json_bundle(root, bundle="benchmark")
    profiles_bundle = _read_json_bundle(root, bundle="profiles")
    if not profiles_bundle:
        _run_profiles_phase(
            run_dir=root,
            config_path=config_path,
            run_id=run_id,
            labels=labels,
            runtime_surface=runtime_surface,
            runtime_command=runtime_command,
        )
    decision_bundle = _read_json_bundle(root, bundle="decision")
    if not decision_bundle:
        _run_decision_phase(
            run_dir=root,
            config_path=config_path,
            run_id=run_id,
            overwrite=overwrite,
            labels=labels,
            runtime_surface=runtime_surface,
            runtime_command=runtime_command,
        )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="completion",
        data_path=_resolve_run_data_path(root),
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "audit_report.json",
            "belief_update.json",
            "route_prior_context.json",
            "memory_retrieval.json",
            "research_brief.json",
            "method_transfer_report.json",
            "benchmark_parity_report.json",
            "benchmark_gap_report.json",
            "decision_world_model.json",
            "controller_policy.json",
            "value_of_more_data_report.json",
            "run_summary.json",
        ],
    )
    try:
        completion_result = run_completion_review(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            intake_bundle=_read_json_bundle(root, bundle="intake"),
            investigation_bundle=_read_json_bundle(root, bundle="investigation"),
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            evidence_bundle=evidence_bundle,
            memory_bundle=memory_bundle,
            research_bundle=research_bundle,
            benchmark_bundle=benchmark_bundle,
            intelligence_bundle=intelligence_bundle,
            config_path=config_path,
        )
        written = write_completion_bundle(root, bundle=completion_result.bundle)
        manifest_path = _refresh_completion_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic fused evidence, memory, and mandate state into an explicit governed completion decision.",
        )
        materialize_run_summary(run_dir=root)
        sync_materialization_runtime_artifacts(root)
        decision = completion_result.bundle.completion_decision
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "completion": {
                    "action": decision.action,
                    "confidence": decision.confidence,
                    "current_stage": decision.current_stage,
                    "blocking_layer": decision.blocking_layer,
                    "mandate_alignment": decision.mandate_alignment,
                    "complete_for_mode": decision.complete_for_mode,
                },
                "bundle": completion_result.bundle.to_dict(),
            },
            "human_output": completion_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_completion_status(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    completion_bundle = _ensure_completion_present(root)
    if not completion_bundle:
        raise ValueError(f"No Slice 07 completion artifacts found or materializable in {root}.")
    summary_materialized = materialize_run_summary(run_dir=root)
    sync_materialization_runtime_artifacts(root)
    manifest_path = _refresh_completion_manifest(root)
    human_output = render_completion_review_markdown(completion_bundle)
    decision = dict(completion_bundle.get("completion_decision", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(summary_materialized["report_path"]),
            "completion": {
                "action": decision.get("action"),
                "confidence": decision.get("confidence"),
                "current_stage": decision.get("current_stage"),
                "blocking_layer": decision.get("blocking_layer"),
                "mandate_alignment": decision.get("mandate_alignment"),
                "complete_for_mode": decision.get("complete_for_mode"),
            },
            "bundle": completion_bundle,
        },
        "human_output": human_output,
    }


def _run_lifecycle_phase(
    *,
    run_dir: str | Path,
    data_path: str | None,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.lifecycle import write_lifecycle_bundle

    root = Path(run_dir)
    targets = _lifecycle_output_paths(root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    completion_bundle = _ensure_completion_present(root)
    if not completion_bundle:
        raise ValueError(f"Slice 08 lifecycle requires Slice 07 completion artifacts in {root}.")
    resolved_data_path = data_path or _resolve_run_data_path(root)
    _run_memory_phase(
        run_dir=root,
        data_path=resolved_data_path,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
        search_roots=None,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="lifecycle",
        data_path=resolved_data_path,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=[
            "completion_decision.json",
            "memory_retrieval.json",
            "run_summary.json",
            "champion_vs_candidate.json",
        ],
    )
    try:
        lifecycle_result = run_lifecycle_review(
            run_dir=root,
            data_path=resolved_data_path,
            policy=foundation_state["resolved"].policy,
            mandate_bundle=_read_json_bundle(root, bundle="mandate"),
            context_bundle=_read_json_bundle(root, bundle="context"),
            investigation_bundle=_read_json_bundle(root, bundle="investigation"),
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            evidence_bundle=_read_json_bundle(root, bundle="evidence"),
            completion_bundle=completion_bundle,
            memory_bundle=_read_json_bundle(root, bundle="memory"),
            intelligence_bundle=_read_json_bundle(root, bundle="intelligence"),
            config_path=config_path,
        )
        written = write_lifecycle_bundle(root, bundle=lifecycle_result.bundle)
        manifest_path = _refresh_lifecycle_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic finalized lifecycle posture and recorded keep, recalibrate, retrain, promote, or rollback decisions.",
        )
        materialize_run_summary(run_dir=root, data_path=resolved_data_path)
        promotion = lifecycle_result.bundle.promotion_decision
        retrain = lifecycle_result.bundle.retrain_decision
        recalibration = lifecycle_result.bundle.recalibration_decision
        rollback = lifecycle_result.bundle.rollback_decision
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "lifecycle": {
                    "promotion_action": promotion.action,
                    "recalibration_action": recalibration.action,
                    "retrain_action": retrain.action,
                    "rollback_action": rollback.action,
                },
                "bundle": lifecycle_result.bundle.to_dict(),
            },
            "human_output": lifecycle_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_lifecycle_surface(*, run_dir: str | Path, data_path: str | None = None) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    lifecycle_bundle = _ensure_lifecycle_present(root, data_path=data_path)
    if not lifecycle_bundle:
        raise ValueError(f"No Slice 08 lifecycle artifacts found or materializable in {root}.")
    resolved_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="evaluation",
    ) or _resolve_run_data_path(root)
    summary_materialized = materialize_run_summary(run_dir=root, data_path=resolved_data_path)
    manifest_path = _refresh_lifecycle_manifest(root)
    promotion = dict(lifecycle_bundle.get("promotion_decision", {}))
    recalibration = dict(lifecycle_bundle.get("recalibration_decision", {}))
    retrain = dict(lifecycle_bundle.get("retrain_decision", {}))
    rollback = dict(lifecycle_bundle.get("rollback_decision", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_materialized["summary_path"]),
            "report_path": str(summary_materialized["report_path"]),
            "lifecycle": {
                "promotion_action": promotion.get("action"),
                "recalibration_action": recalibration.get("action"),
                "retrain_action": retrain.get("action"),
                "rollback_action": rollback.get("action"),
            },
            "bundle": lifecycle_bundle,
        },
        "human_output": render_lifecycle_review_markdown(lifecycle_bundle),
    }


def _run_autonomy_phase(
    *,
    run_dir: str | Path,
    data_path: str | None,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    runtime_surface: str = "cli",
    runtime_command: str | None = None,
) -> dict[str, Any]:
    from relaytic.autonomy import write_autonomy_bundle

    root = Path(run_dir)
    targets = _autonomy_output_paths(root)
    if not overwrite and all(path.exists() for path in targets.values()):
        return _show_autonomy_surface(run_dir=root)
    _ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    lifecycle_bundle = _read_json_bundle(root, bundle="lifecycle")
    if not lifecycle_bundle:
        raise ValueError(f"Slice 09C autonomy requires Slice 08 lifecycle artifacts in {root}.")
    resolved_data_path = data_path or _resolve_run_data_path(root)
    if not resolved_data_path:
        raise ValueError(f"Slice 09C autonomy requires a resolvable dataset path in {root}.")
    _run_intelligence_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        overwrite=False,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
    )
    _run_research_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        overwrite=False,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
    )
    _run_decision_phase(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        overwrite=False,
        labels=labels,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
    )
    runtime_token = _runtime_stage_token(
        run_dir=root,
        policy=foundation_state["resolved"].policy,
        stage="autonomy",
        data_path=resolved_data_path,
        runtime_surface=runtime_surface,
        runtime_command=runtime_command,
        input_artifacts=["plan.json", "completion_decision.json", "promotion_decision.json", "semantic_debate_report.json", "semantic_uncertainty_report.json", "research_brief.json", "method_transfer_report.json", "decision_world_model.json", "controller_policy.json", "compiled_challenger_templates.json"],
    )
    try:
        autonomy_result = run_autonomy_loop(
            run_dir=root,
            data_path=resolved_data_path,
            policy=foundation_state["resolved"].policy,
            planning_bundle=_read_json_bundle(root, bundle="planning"),
            evidence_bundle=_read_json_bundle(root, bundle="evidence"),
            completion_bundle=_read_json_bundle(root, bundle="completion"),
            lifecycle_bundle=lifecycle_bundle,
            research_bundle=_read_json_bundle(root, bundle="research"),
            intelligence_bundle=_read_json_bundle(root, bundle="intelligence"),
            decision_bundle=_read_json_bundle(root, bundle="decision"),
            benchmark_bundle=_read_json_bundle(root, bundle="benchmark"),
        )
        if autonomy_result.promotion_applied:
            _run_memory_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=run_id,
                labels=labels,
                search_roots=None,
                runtime_surface=runtime_surface,
                runtime_command=runtime_command,
            )
            _run_evidence_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=run_id,
                sheet_name=None,
                header_row=None,
                data_start_row=None,
                timestamp_column=None,
                overwrite=True,
                labels=labels,
                planning_state=None,
                runtime_surface=runtime_surface,
                runtime_command=runtime_command,
            )
            _run_intelligence_phase(
                run_dir=root,
                config_path=config_path,
                run_id=run_id,
                overwrite=True,
                labels=labels,
                runtime_surface=runtime_surface,
                runtime_command=runtime_command,
            )
            _run_completion_phase(
                run_dir=root,
                config_path=config_path,
                run_id=run_id,
                overwrite=True,
                labels=labels,
                runtime_surface=runtime_surface,
                runtime_command=runtime_command,
            )
            _run_lifecycle_phase(
                run_dir=root,
                data_path=resolved_data_path,
                config_path=config_path,
                run_id=run_id,
                overwrite=True,
                labels=labels,
                runtime_surface=runtime_surface,
                runtime_command=runtime_command,
            )
        written = write_autonomy_bundle(root, bundle=autonomy_result.bundle)
        manifest_path = _refresh_autonomy_manifest(
            root,
            run_id=run_id,
            policy_source=foundation_state["policy_path"],
            labels=labels,
        )
        record_runtime_stage_completion(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            output_artifacts=[*(str(value) for value in written.values()), str(manifest_path)],
            summary="Relaytic executed one bounded autonomous follow-up round and recorded branch outcomes and champion lineage.",
        )
        materialize_run_summary(run_dir=root, data_path=resolved_data_path)
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(root),
                "manifest_path": str(manifest_path),
                "paths": {key: str(value) for key, value in written.items()},
                "autonomy": {
                    "selected_action": autonomy_result.selected_action,
                    "promotion_applied": autonomy_result.promotion_applied,
                    "winning_branch_id": autonomy_result.winning_branch_id,
                },
                "bundle": autonomy_result.bundle.to_dict(),
            },
            "human_output": autonomy_result.review_markdown,
        }
    except Exception as exc:
        record_runtime_stage_failure(
            run_dir=root,
            policy=foundation_state["resolved"].policy,
            stage_token=runtime_token,
            error=exc,
        )
        raise


def _show_autonomy_surface(*, run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = _read_json_bundle(root, bundle="autonomy")
    if not bundle:
        raise ValueError(f"No Slice 09C autonomy artifacts found in {root}.")
    materialize_run_summary(run_dir=root)
    manifest_path = _refresh_autonomy_manifest(root)
    loop_state = dict(bundle.get("autonomy_loop_state", {}))
    matrix = dict(bundle.get("branch_outcome_matrix", {}))
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "autonomy": {
                "selected_action": loop_state.get("selected_action"),
                "promotion_applied": loop_state.get("promotion_applied"),
                "winning_branch_id": matrix.get("winning_branch_id"),
            },
            "bundle": bundle,
        },
        "human_output": render_autonomy_review_markdown(bundle),
    }


def _ensure_investigation_present(
    *,
    run_dir: str | Path,
    data_path: str,
    config_path: str | None,
    run_id: str | None,
    sheet_name: str | None,
    header_row: int | None,
    data_start_row: int | None,
    timestamp_column: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
) -> dict[str, Any]:
    root = Path(run_dir)
    staged_data_path = _stage_run_data_copy(
        run_dir=root,
        data_path=data_path,
        purpose="primary",
    ) or str(Path(data_path))
    targets = _investigation_output_paths(root)
    if not overwrite and all(path.exists() for path in targets.values()):
        return {"bundle": _read_json_bundle(root, bundle="investigation")}
    foundation_state = _ensure_run_foundation_present(
        run_dir=root,
        config_path=config_path,
        run_id=run_id,
        labels=labels,
    )
    bundle = run_investigation(
        data_path=staged_data_path,
        policy=foundation_state["resolved"].policy,
        mandate_bundle=_read_json_bundle(root, bundle="mandate"),
        context_bundle=_read_json_bundle(root, bundle="context"),
        config_path=config_path,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
    )
    from relaytic.investigation import write_investigation_bundle

    write_investigation_bundle(root, bundle=bundle)
    _refresh_investigation_manifest(
        root,
        run_id=run_id,
        policy_source=foundation_state["policy_path"],
        labels=labels,
    )
    return {"bundle": bundle.to_dict()}


def _init_mandate_foundation(args: argparse.Namespace) -> dict[str, Any]:
    from relaytic.mandate import (
        MandateControl,
        build_mandate_controls_from_policy,
        build_run_brief,
        build_work_preferences,
        default_lab_mandate,
        write_mandate_bundle,
    )

    root = Path(args.run_dir)
    targets = _foundation_output_paths(root)
    _ensure_paths_absent(
        [targets["lab_mandate"], targets["work_preferences"], targets["run_brief"]],
        overwrite=bool(args.overwrite),
    )
    resolved, policy_path = _ensure_policy_resolved(
        root,
        config_path=args.config,
        overwrite=bool(args.overwrite),
    )
    derived_controls = build_mandate_controls_from_policy(resolved.policy)
    controls = MandateControl(
        enabled=False if bool(args.disable_mandate) else derived_controls.enabled,
        influence_mode=args.influence_mode or derived_controls.influence_mode,
        allow_agent_challenges=derived_controls.allow_agent_challenges,
        require_disagreement_logging=derived_controls.require_disagreement_logging,
        allow_soft_preference_override_with_evidence=derived_controls.allow_soft_preference_override_with_evidence,
    )
    lab_mandate = default_lab_mandate(controls)
    if args.lab_value:
        lab_mandate = type(lab_mandate)(
            controls=controls,
            values=list(args.lab_value),
            hard_constraints=list(args.hard_constraint),
            soft_preferences=list(args.soft_preference),
            prohibited_actions=list(args.prohibited_action),
            notes=args.lab_notes,
        )
    else:
        lab_mandate = type(lab_mandate)(
            controls=controls,
            values=lab_mandate.values,
            hard_constraints=list(args.hard_constraint or lab_mandate.hard_constraints),
            soft_preferences=list(args.soft_preference or lab_mandate.soft_preferences),
            prohibited_actions=list(args.prohibited_action or lab_mandate.prohibited_actions),
            notes=args.lab_notes or lab_mandate.notes,
        )
    work_preferences = build_work_preferences(
        controls,
        policy=resolved.policy,
        execution_mode_preference=args.work_execution_mode,
        operation_mode_preference=args.work_operation_mode,
        preferred_report_style=args.report_style,
        preferred_effort_tier=args.effort_tier,
        notes=args.work_notes,
    )
    run_brief = build_run_brief(
        controls,
        policy=resolved.policy,
        objective=args.objective,
        target_column=args.target_column,
        deployment_target=args.deployment_target,
        success_criteria=list(args.success_criterion),
        binding_constraints=list(args.binding_constraint),
        notes=args.run_notes,
    )
    written = write_mandate_bundle(
        root,
        lab_mandate=lab_mandate,
        work_preferences=work_preferences,
        run_brief=run_brief,
    )
    manifest_path = _refresh_foundation_manifest(root, policy_source=policy_path)
    return {
        "status": "ok",
        "run_dir": str(root),
        "policy_resolved": str(policy_path),
        "paths": {key: str(value) for key, value in written.items()},
        "manifest_path": str(manifest_path),
    }


def _init_context_foundation(args: argparse.Namespace) -> dict[str, Any]:
    from relaytic.context import (
        build_context_controls_from_policy,
        default_data_origin,
        default_domain_brief,
        default_task_brief,
        write_context_bundle,
    )

    root = Path(args.run_dir)
    targets = _foundation_output_paths(root)
    _ensure_paths_absent(
        [targets["data_origin"], targets["domain_brief"], targets["task_brief"]],
        overwrite=bool(args.overwrite),
    )
    resolved, policy_path = _ensure_policy_resolved(
        root,
        config_path=args.config,
        overwrite=bool(args.overwrite),
    )
    controls = build_context_controls_from_policy(resolved.policy)
    data_origin = default_data_origin(
        controls,
        source_name=args.source_name,
        source_type=args.source_type,
        acquisition_notes=args.acquisition_notes,
        owner=args.owner,
        contains_pii=True if bool(args.contains_pii) else None,
        access_constraints=list(args.access_constraint),
        refresh_cadence=args.refresh_cadence,
    )
    domain_brief = default_domain_brief(
        controls,
        system_name=args.system_name,
        summary=args.domain_summary,
        target_meaning=args.target_meaning,
        known_caveats=list(args.known_caveat),
        suspicious_columns=list(args.suspicious_column),
        forbidden_features=list(args.forbidden_feature),
        binding_constraints=list(args.domain_binding_constraint),
        assumptions=list(args.domain_assumption),
    )
    task_brief = default_task_brief(
        controls,
        problem_statement=args.problem_statement,
        target_column=args.task_target_column,
        prediction_horizon=args.prediction_horizon,
        decision_type=args.decision_type,
        primary_stakeholder=args.primary_stakeholder,
        success_criteria=list(args.task_success_criterion),
        failure_costs=list(args.failure_cost),
        notes=args.task_notes,
    )
    written = write_context_bundle(
        root,
        data_origin=data_origin,
        domain_brief=domain_brief,
        task_brief=task_brief,
    )
    manifest_path = _refresh_foundation_manifest(root, policy_source=policy_path)
    return {
        "status": "ok",
        "run_dir": str(root),
        "policy_resolved": str(policy_path),
        "paths": {key: str(value) for key, value in written.items()},
        "manifest_path": str(manifest_path),
    }


def _ensure_policy_resolved(
    run_dir: Path,
    *,
    config_path: str | None,
    overwrite: bool,
) -> tuple[Any, Path]:
    import yaml
    from relaytic.policies.loader import ResolvedPolicy

    policy_path = run_dir / "policy_resolved.yaml"
    run_dir.mkdir(parents=True, exist_ok=True)
    if policy_path.exists() and not overwrite:
        payload = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
        return (
            ResolvedPolicy(
                schema_version=str(payload.get("schema_version", "")),
                resolved_at=str(payload.get("resolved_at", "")),
                source_path=str(payload.get("source_path", "")),
                source_format=str(payload.get("source_format", "canonical")),
                policy=dict(payload.get("policy", {})),
            ),
            policy_path,
        )
    resolved = load_policy(config_path)
    policy_path.write_text(
        yaml.safe_dump(resolved.to_dict(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return resolved, policy_path


def _foundation_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "policy_resolved": run_dir / "policy_resolved.yaml",
        "lab_mandate": run_dir / "lab_mandate.json",
        "work_preferences": run_dir / "work_preferences.json",
        "run_brief": run_dir / "run_brief.json",
        "data_origin": run_dir / "data_origin.json",
        "domain_brief": run_dir / "domain_brief.json",
        "task_brief": run_dir / "task_brief.json",
        "manifest": run_dir / "manifest.json",
    }


def _investigation_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "dataset_profile": run_dir / "dataset_profile.json",
        "domain_memo": run_dir / "domain_memo.json",
        "objective_hypotheses": run_dir / "objective_hypotheses.json",
        "focus_debate": run_dir / "focus_debate.json",
        "focus_profile": run_dir / "focus_profile.json",
        "optimization_profile": run_dir / "optimization_profile.json",
        "feature_strategy_profile": run_dir / "feature_strategy_profile.json",
    }


def _intake_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "intake_record": run_dir / "intake_record.json",
        "autonomy_mode": run_dir / "autonomy_mode.json",
        "clarification_queue": run_dir / "clarification_queue.json",
        "assumption_log": run_dir / "assumption_log.json",
        "context_interpretation": run_dir / "context_interpretation.json",
        "context_constraints": run_dir / "context_constraints.json",
        "semantic_mapping": run_dir / "semantic_mapping.json",
    }


def _planning_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "plan": run_dir / "plan.json",
        "alternatives": run_dir / "alternatives.json",
        "hypotheses": run_dir / "hypotheses.json",
        "experiment_priority_report": run_dir / "experiment_priority_report.json",
        "marginal_value_of_next_experiment": run_dir / "marginal_value_of_next_experiment.json",
    }


def _memory_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "memory_retrieval": run_dir / "memory_retrieval.json",
        "analog_run_candidates": run_dir / "analog_run_candidates.json",
        "route_prior_context": run_dir / "route_prior_context.json",
        "challenger_prior_suggestions": run_dir / "challenger_prior_suggestions.json",
        "reflection_memory": run_dir / "reflection_memory.json",
        "memory_flush_report": run_dir / "memory_flush_report.json",
    }


def _intelligence_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "intelligence_mode": run_dir / "intelligence_mode.json",
        "llm_routing_plan": run_dir / "llm_routing_plan.json",
        "local_llm_profile": run_dir / "local_llm_profile.json",
        "llm_backend_discovery": run_dir / "llm_backend_discovery.json",
        "llm_health_check": run_dir / "llm_health_check.json",
        "llm_upgrade_suggestions": run_dir / "llm_upgrade_suggestions.json",
        "semantic_task_request": run_dir / "semantic_task_request.json",
        "semantic_task_results": run_dir / "semantic_task_results.json",
        "intelligence_escalation": run_dir / "intelligence_escalation.json",
        "verifier_report": run_dir / "verifier_report.json",
        "context_assembly_report": run_dir / "context_assembly_report.json",
        "doc_grounding_report": run_dir / "doc_grounding_report.json",
        "semantic_access_audit": run_dir / "semantic_access_audit.json",
        "semantic_debate_report": run_dir / "semantic_debate_report.json",
        "semantic_counterposition_pack": run_dir / "semantic_counterposition_pack.json",
        "semantic_uncertainty_report": run_dir / "semantic_uncertainty_report.json",
        "semantic_proof_report": run_dir / "semantic_proof_report.json",
    }


def _research_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "research_query_plan": run_dir / "research_query_plan.json",
        "research_source_inventory": run_dir / "research_source_inventory.json",
        "research_brief": run_dir / "research_brief.json",
        "method_transfer_report": run_dir / "method_transfer_report.json",
        "benchmark_reference_report": run_dir / "benchmark_reference_report.json",
        "external_research_audit": run_dir / "external_research_audit.json",
    }


def _benchmark_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "reference_approach_matrix": run_dir / "reference_approach_matrix.json",
        "benchmark_gap_report": run_dir / "benchmark_gap_report.json",
        "benchmark_parity_report": run_dir / "benchmark_parity_report.json",
        "external_challenger_manifest": run_dir / "external_challenger_manifest.json",
        "external_challenger_evaluation": run_dir / "external_challenger_evaluation.json",
        "incumbent_parity_report": run_dir / "incumbent_parity_report.json",
        "beat_target_contract": run_dir / "beat_target_contract.json",
        "paper_benchmark_manifest": run_dir / "paper_benchmark_manifest.json",
        "paper_benchmark_table": run_dir / "paper_benchmark_table.json",
        "benchmark_ablation_matrix": run_dir / "benchmark_ablation_matrix.json",
        "rerun_variance_report": run_dir / "rerun_variance_report.json",
        "benchmark_claims_report": run_dir / "benchmark_claims_report.json",
        "shadow_trial_manifest": run_dir / "shadow_trial_manifest.json",
        "shadow_trial_scorecard": run_dir / "shadow_trial_scorecard.json",
        "candidate_quarantine": run_dir / "candidate_quarantine.json",
        "promotion_readiness_report": run_dir / "promotion_readiness_report.json",
        "benchmark_truth_audit": run_dir / "benchmark_truth_audit.json",
        "paper_claim_guard_report": run_dir / "paper_claim_guard_report.json",
        "benchmark_release_gate": run_dir / "benchmark_release_gate.json",
        "dataset_leakage_audit": run_dir / "dataset_leakage_audit.json",
        "temporal_benchmark_recovery_report": run_dir / "temporal_benchmark_recovery_report.json",
        "benchmark_pack_partition": run_dir / "benchmark_pack_partition.json",
        "holdout_claim_policy": run_dir / "holdout_claim_policy.json",
        "benchmark_generalization_audit": run_dir / "benchmark_generalization_audit.json",
    }


def _decision_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "decision_world_model": run_dir / "decision_world_model.json",
        "controller_policy": run_dir / "controller_policy.json",
        "handoff_controller_report": run_dir / "handoff_controller_report.json",
        "intervention_policy_report": run_dir / "intervention_policy_report.json",
        "decision_usefulness_report": run_dir / "decision_usefulness_report.json",
        "trajectory_constraint_report": run_dir / "trajectory_constraint_report.json",
        "feasible_region_map": run_dir / "feasible_region_map.json",
        "extrapolation_risk_report": run_dir / "extrapolation_risk_report.json",
        "decision_constraint_report": run_dir / "decision_constraint_report.json",
        "action_boundary_report": run_dir / "action_boundary_report.json",
        "deployability_assessment": run_dir / "deployability_assessment.json",
        "review_gate_state": run_dir / "review_gate_state.json",
        "constraint_override_request": run_dir / "constraint_override_request.json",
        "counterfactual_region_report": run_dir / "counterfactual_region_report.json",
        "value_of_more_data_report": run_dir / "value_of_more_data_report.json",
        "data_acquisition_plan": run_dir / "data_acquisition_plan.json",
        "source_graph": run_dir / "source_graph.json",
        "join_candidate_report": run_dir / "join_candidate_report.json",
        "method_compiler_report": run_dir / "method_compiler_report.json",
        "compiled_challenger_templates": run_dir / "compiled_challenger_templates.json",
        "compiled_feature_hypotheses": run_dir / "compiled_feature_hypotheses.json",
        "compiled_benchmark_protocol": run_dir / "compiled_benchmark_protocol.json",
        "method_import_report": run_dir / "method_import_report.json",
        "architecture_candidate_registry": run_dir / "architecture_candidate_registry.json",
    }


def _dojo_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "dojo_session": run_dir / "dojo_session.json",
        "dojo_hypotheses": run_dir / "dojo_hypotheses.json",
        "dojo_results": run_dir / "dojo_results.json",
        "dojo_promotions": run_dir / "dojo_promotions.json",
        "architecture_proposals": run_dir / "architecture_proposals.json",
    }


def _pulse_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "pulse_schedule": run_dir / "pulse_schedule.json",
        "pulse_run_report": run_dir / "pulse_run_report.json",
        "pulse_skip_report": run_dir / "pulse_skip_report.json",
        "pulse_recommendations": run_dir / "pulse_recommendations.json",
        "innovation_watch_report": run_dir / "innovation_watch_report.json",
        "challenge_watchlist": run_dir / "challenge_watchlist.json",
        "pulse_checkpoint": run_dir / "pulse_checkpoint.json",
        "memory_compaction_plan": run_dir / "memory_compaction_plan.json",
        "memory_compaction_report": run_dir / "memory_compaction_report.json",
        "memory_pinning_index": run_dir / "memory_pinning_index.json",
    }


def _trace_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "trace_model": run_dir / "trace_model.json",
        "specialist_trace_index": run_dir / "specialist_trace_index.json",
        "branch_trace_graph": run_dir / "branch_trace_graph.json",
        "adjudication_scorecard": run_dir / "adjudication_scorecard.json",
        "decision_replay_report": run_dir / "decision_replay_report.json",
        "trace_span_log": run_dir / "trace_span_log.jsonl",
        "tool_trace_log": run_dir / "tool_trace_log.jsonl",
        "intervention_trace_log": run_dir / "intervention_trace_log.jsonl",
        "claim_packet_log": run_dir / "claim_packet_log.jsonl",
    }


def _evals_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "agent_eval_matrix": run_dir / "agent_eval_matrix.json",
        "security_eval_report": run_dir / "security_eval_report.json",
        "red_team_report": run_dir / "red_team_report.json",
        "protocol_conformance_report": run_dir / "protocol_conformance_report.json",
        "host_surface_matrix": run_dir / "host_surface_matrix.json",
        "trace_identity_conformance": run_dir / "trace_identity_conformance.json",
        "eval_surface_parity_report": run_dir / "eval_surface_parity_report.json",
    }


def _search_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "hpo_budget_contract": run_dir / "hpo_budget_contract.json",
        "architecture_search_space": run_dir / "architecture_search_space.json",
        "trial_ledger": run_dir / "trial_ledger.jsonl",
        "early_stopping_report": run_dir / "early_stopping_report.json",
        "search_loop_scorecard": run_dir / "search_loop_scorecard.json",
        "warm_start_transfer_report": run_dir / "warm_start_transfer_report.json",
        "threshold_tuning_report": run_dir / "threshold_tuning_report.json",
        "search_controller_plan": run_dir / "search_controller_plan.json",
        "portfolio_search_trace": run_dir / "portfolio_search_trace.json",
        "hpo_campaign_report": run_dir / "hpo_campaign_report.json",
        "search_decision_ledger": run_dir / "search_decision_ledger.json",
        "execution_backend_profile": run_dir / "execution_backend_profile.json",
        "device_allocation": run_dir / "device_allocation.json",
        "distributed_run_plan": run_dir / "distributed_run_plan.json",
        "scheduler_job_map": run_dir / "scheduler_job_map.json",
        "checkpoint_state": run_dir / "checkpoint_state.json",
        "execution_strategy_report": run_dir / "execution_strategy_report.json",
        "search_value_report": run_dir / "search_value_report.json",
        "search_controller_eval_report": run_dir / "search_controller_eval_report.json",
    }


def _daemon_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "daemon_state": run_dir / "daemon_state.json",
        "background_job_registry": run_dir / "background_job_registry.json",
        "background_checkpoint": run_dir / "background_checkpoint.json",
        "resume_session_manifest": run_dir / "resume_session_manifest.json",
        "background_approval_queue": run_dir / "background_approval_queue.json",
        "memory_maintenance_queue": run_dir / "memory_maintenance_queue.json",
        "memory_maintenance_report": run_dir / "memory_maintenance_report.json",
        "search_resume_plan": run_dir / "search_resume_plan.json",
        "stale_job_report": run_dir / "stale_job_report.json",
    }


def _feedback_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "feedback_intake": run_dir / "feedback_intake.json",
        "feedback_validation": run_dir / "feedback_validation.json",
        "feedback_effect_report": run_dir / "feedback_effect_report.json",
        "feedback_casebook": run_dir / "feedback_casebook.json",
        "outcome_observation_report": run_dir / "outcome_observation_report.json",
        "decision_policy_update_suggestions": run_dir / "decision_policy_update_suggestions.json",
        "policy_update_suggestions": run_dir / "policy_update_suggestions.json",
        "route_prior_updates": run_dir / "route_prior_updates.json",
    }


def _profiles_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "quality_contract": run_dir / "quality_contract.json",
        "quality_gate_report": run_dir / "quality_gate_report.json",
        "budget_contract": run_dir / "budget_contract.json",
        "budget_consumption_report": run_dir / "budget_consumption_report.json",
        "operator_profile": run_dir / "operator_profile.json",
        "lab_operating_profile": run_dir / "lab_operating_profile.json",
    }


def _control_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "intervention_request": run_dir / "intervention_request.json",
        "intervention_contract": run_dir / "intervention_contract.json",
        "control_challenge_report": run_dir / "control_challenge_report.json",
        "override_decision": run_dir / "override_decision.json",
        "intervention_ledger": run_dir / "intervention_ledger.json",
        "recovery_checkpoint": run_dir / "recovery_checkpoint.json",
        "control_injection_audit": run_dir / "control_injection_audit.json",
        "causal_memory_index": run_dir / "causal_memory_index.json",
        "intervention_memory_log": run_dir / "intervention_memory_log.json",
        "outcome_memory_graph": run_dir / "outcome_memory_graph.json",
        "method_memory_index": run_dir / "method_memory_index.json",
    }


def _evidence_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "experiment_registry": run_dir / "experiment_registry.json",
        "challenger_report": run_dir / "challenger_report.json",
        "ablation_report": run_dir / "ablation_report.json",
        "audit_report": run_dir / "audit_report.json",
        "belief_update": run_dir / "belief_update.json",
        "leaderboard": run_dir / "leaderboard.csv",
        "technical_report": run_dir / "reports" / "technical_report.md",
        "decision_memo": run_dir / "reports" / "decision_memo.md",
    }


def _completion_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "completion_decision": run_dir / "completion_decision.json",
        "run_state": run_dir / "run_state.json",
        "stage_timeline": run_dir / "stage_timeline.json",
        "mandate_evidence_review": run_dir / "mandate_evidence_review.json",
        "blocking_analysis": run_dir / "blocking_analysis.json",
        "next_action_queue": run_dir / "next_action_queue.json",
    }


def _lifecycle_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "champion_vs_candidate": run_dir / "champion_vs_candidate.json",
        "recalibration_decision": run_dir / "recalibration_decision.json",
        "retrain_decision": run_dir / "retrain_decision.json",
        "promotion_decision": run_dir / "promotion_decision.json",
        "rollback_decision": run_dir / "rollback_decision.json",
    }


def _autonomy_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "autonomy_loop_state": run_dir / "autonomy_loop_state.json",
        "autonomy_round_report": run_dir / "autonomy_round_report.json",
        "challenger_queue": run_dir / "challenger_queue.json",
        "branch_outcome_matrix": run_dir / "branch_outcome_matrix.json",
        "retrain_run_request": run_dir / "retrain_run_request.json",
        "recalibration_run_request": run_dir / "recalibration_run_request.json",
        "champion_lineage": run_dir / "champion_lineage.json",
        "loop_budget_report": run_dir / "loop_budget_report.json",
    }


def _assist_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "assist_mode": run_dir / "assist_mode.json",
        "assist_session_state": run_dir / "assist_session_state.json",
        "assistant_connection_guide": run_dir / "assistant_connection_guide.json",
        "assist_turn_log": run_dir / "assist_turn_log.jsonl",
    }


def _mission_control_output_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "mission_control_state": run_dir / "mission_control_state.json",
        "review_queue_state": run_dir / "review_queue_state.json",
        "control_center_layout": run_dir / "control_center_layout.json",
        "onboarding_status": run_dir / "onboarding_status.json",
        "install_experience_report": run_dir / "install_experience_report.json",
        "launch_manifest": run_dir / "launch_manifest.json",
        "demo_session_manifest": run_dir / "demo_session_manifest.json",
        "ui_preferences": run_dir / "ui_preferences.json",
        "mission_control_report": run_dir / "reports" / "mission_control.html",
    }


def _resolve_existing_incumbent_config(run_dir: Path) -> dict[str, str | None]:
    bundle = _read_json_bundle(run_dir, bundle="benchmark")
    if not bundle:
        return {}
    manifest = dict(bundle.get("external_challenger_manifest", {}))
    source_path = str(manifest.get("source_path", "")).strip()
    if not source_path or not bool(manifest.get("executable_locally")):
        return {}
    return {
        "incumbent_path": source_path,
        "incumbent_kind": str(manifest.get("incumbent_kind", "")).strip() or None,
        "incumbent_name": str(manifest.get("incumbent_name", "")).strip() or None,
    }


def _access_surface_output_paths(run_dir: Path) -> dict[str, Path]:
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    return {
        "run_summary": run_dir / "run_summary.json",
        "summary_report": run_dir / "reports" / "summary.md",
        "run_handoff": run_dir / "run_handoff.json",
        "next_run_options": run_dir / "next_run_options.json",
        "next_run_focus": run_dir / "next_run_focus.json",
        "user_result_report": run_dir / "reports" / "user_result_report.md",
        "agent_result_report": run_dir / "reports" / "agent_result_report.md",
        "lab_learnings_snapshot": run_dir / "lab_learnings_snapshot.json",
        "workspace_state": workspace_dir / "workspace_state.json",
        "workspace_lineage": workspace_dir / "workspace_lineage.json",
        "workspace_focus_history": workspace_dir / "workspace_focus_history.json",
        "workspace_memory_policy": workspace_dir / "workspace_memory_policy.json",
        "result_contract": run_dir / "result_contract.json",
        "confidence_posture": run_dir / "confidence_posture.json",
        "belief_revision_triggers": run_dir / "belief_revision_triggers.json",
        "next_run_plan": workspace_dir / "next_run_plan.json",
        "focus_decision_record": run_dir / "focus_decision_record.json",
        "data_expansion_candidates": run_dir / "data_expansion_candidates.json",
        "hpo_budget_contract": run_dir / "hpo_budget_contract.json",
        "architecture_search_space": run_dir / "architecture_search_space.json",
        "trial_ledger": run_dir / "trial_ledger.jsonl",
        "early_stopping_report": run_dir / "early_stopping_report.json",
        "search_loop_scorecard": run_dir / "search_loop_scorecard.json",
        "warm_start_transfer_report": run_dir / "warm_start_transfer_report.json",
        "threshold_tuning_report": run_dir / "threshold_tuning_report.json",
        "search_controller_plan": run_dir / "search_controller_plan.json",
        "portfolio_search_trace": run_dir / "portfolio_search_trace.json",
        "hpo_campaign_report": run_dir / "hpo_campaign_report.json",
        "search_decision_ledger": run_dir / "search_decision_ledger.json",
        "execution_backend_profile": run_dir / "execution_backend_profile.json",
        "device_allocation": run_dir / "device_allocation.json",
        "distributed_run_plan": run_dir / "distributed_run_plan.json",
        "scheduler_job_map": run_dir / "scheduler_job_map.json",
        "checkpoint_state": run_dir / "checkpoint_state.json",
        "execution_strategy_report": run_dir / "execution_strategy_report.json",
        "search_value_report": run_dir / "search_value_report.json",
        "search_controller_eval_report": run_dir / "search_controller_eval_report.json",
    }


def _planning_model_artifact_paths(run_dir: Path) -> list[Path]:
    candidates: list[Path] = [
        run_dir / "model_params.json",
        run_dir / "model_state.json",
        run_dir / "normalization_state.json",
        run_dir / "checkpoints",
    ]
    candidates.extend(sorted(run_dir.glob("*_state.json")))
    checkpoint_dir = run_dir / "checkpoints"
    if checkpoint_dir.exists():
        candidates.extend(sorted(checkpoint_dir.glob("ckpt_*.json")))
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = Path(path)
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(resolved)
    return deduped


def _ensure_paths_absent(paths: list[Path], *, overwrite: bool) -> None:
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        deduped.append(path)
    if overwrite:
        for path in deduped:
            if not path.exists():
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        return
    existing = [str(path) for path in deduped if path.exists()]
    if existing:
        raise ValueError(
            "Refusing to overwrite existing artifacts without --overwrite: "
            + ", ".join(existing)
        )


def _refresh_foundation_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = [
        artifact_entry("policy_resolved.yaml", run_dir=root, kind="policy", required=True),
        artifact_entry("lab_mandate.json", run_dir=root, required=True),
        artifact_entry("work_preferences.json", run_dir=root, required=True),
        artifact_entry("run_brief.json", run_dir=root, required=True),
        artifact_entry("data_origin.json", run_dir=root, required=True),
        artifact_entry("domain_brief.json", run_dir=root, required=True),
        artifact_entry("task_brief.json", run_dir=root, required=True),
    ]
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=entries,
    )


def _refresh_intake_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = [
        artifact_entry("policy_resolved.yaml", run_dir=root, kind="policy", required=True),
        artifact_entry("lab_mandate.json", run_dir=root, required=True),
        artifact_entry("work_preferences.json", run_dir=root, required=True),
        artifact_entry("run_brief.json", run_dir=root, required=True),
        artifact_entry("data_origin.json", run_dir=root, required=True),
        artifact_entry("domain_brief.json", run_dir=root, required=True),
        artifact_entry("task_brief.json", run_dir=root, required=True),
        artifact_entry("intake_record.json", run_dir=root, required=True),
        artifact_entry("autonomy_mode.json", run_dir=root, required=True),
        artifact_entry("clarification_queue.json", run_dir=root, required=True),
        artifact_entry("assumption_log.json", run_dir=root, required=True),
        artifact_entry("context_interpretation.json", run_dir=root, required=True),
        artifact_entry("context_constraints.json", run_dir=root, required=True),
        artifact_entry("semantic_mapping.json", run_dir=root, required=True),
    ]
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=entries,
    )


def _refresh_investigation_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = [
        artifact_entry("policy_resolved.yaml", run_dir=root, kind="policy", required=True),
        artifact_entry("lab_mandate.json", run_dir=root, required=True),
        artifact_entry("work_preferences.json", run_dir=root, required=True),
        artifact_entry("run_brief.json", run_dir=root, required=True),
        artifact_entry("data_origin.json", run_dir=root, required=True),
        artifact_entry("domain_brief.json", run_dir=root, required=True),
        artifact_entry("task_brief.json", run_dir=root, required=True),
        artifact_entry("intake_record.json", run_dir=root, required=(root / "intake_record.json").exists()),
        artifact_entry("autonomy_mode.json", run_dir=root, required=(root / "autonomy_mode.json").exists()),
        artifact_entry(
            "clarification_queue.json",
            run_dir=root,
            required=(root / "clarification_queue.json").exists(),
        ),
        artifact_entry("assumption_log.json", run_dir=root, required=(root / "assumption_log.json").exists()),
        artifact_entry(
            "context_interpretation.json",
            run_dir=root,
            required=(root / "context_interpretation.json").exists(),
        ),
        artifact_entry(
            "context_constraints.json",
            run_dir=root,
            required=(root / "context_constraints.json").exists(),
        ),
        artifact_entry("semantic_mapping.json", run_dir=root, required=(root / "semantic_mapping.json").exists()),
        artifact_entry("dataset_profile.json", run_dir=root, required=True),
        artifact_entry("domain_memo.json", run_dir=root, required=True),
        artifact_entry("objective_hypotheses.json", run_dir=root, required=True),
        artifact_entry("focus_debate.json", run_dir=root, required=True),
        artifact_entry("focus_profile.json", run_dir=root, required=True),
        artifact_entry("optimization_profile.json", run_dir=root, required=True),
        artifact_entry("feature_strategy_profile.json", run_dir=root, required=True),
    ]
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=entries,
    )


def _refresh_memory_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_investigation_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _memory_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="memory", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_planning_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
    training_result: dict[str, Any] | None = None,
) -> Path:
    root = Path(run_dir)
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = [
        artifact_entry("policy_resolved.yaml", run_dir=root, kind="policy", required=True),
        artifact_entry("lab_mandate.json", run_dir=root, required=True),
        artifact_entry("work_preferences.json", run_dir=root, required=True),
        artifact_entry("run_brief.json", run_dir=root, required=True),
        artifact_entry("data_origin.json", run_dir=root, required=True),
        artifact_entry("domain_brief.json", run_dir=root, required=True),
        artifact_entry("task_brief.json", run_dir=root, required=True),
    ]

    for filename in [
        "intake_record.json",
        "autonomy_mode.json",
        "clarification_queue.json",
        "assumption_log.json",
        "context_interpretation.json",
        "context_constraints.json",
        "semantic_mapping.json",
    ]:
        path = root / filename
        if path.exists():
            entries.append(artifact_entry(filename, run_dir=root, required=True))

    for filename in [
        "dataset_profile.json",
        "domain_memo.json",
        "objective_hypotheses.json",
        "focus_debate.json",
        "focus_profile.json",
        "optimization_profile.json",
        "feature_strategy_profile.json",
    ]:
        path = root / filename
        if path.exists():
            entries.append(artifact_entry(filename, run_dir=root, required=True))

    for path in _memory_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="memory", required=True))

    for filename in [
        "plan.json",
        "alternatives.json",
        "hypotheses.json",
        "experiment_priority_report.json",
        "marginal_value_of_next_experiment.json",
    ]:
        path = root / filename
        if path.exists():
            entries.append(artifact_entry(filename, run_dir=root, required=True))

    model_required = training_result is not None
    state_candidates = sorted(
        path
        for path in root.glob("*_state.json")
        if path.name != "normalization_state.json"
    )
    explicit_state_path = None
    if training_result is not None:
        raw_state_path = str(training_result.get("model_state_path", "")).strip()
        if raw_state_path:
            explicit_state_path = Path(raw_state_path)

    if (root / "model_params.json").exists() or model_required:
        entries.append(
            artifact_entry(
                "model_params.json",
                run_dir=root,
                kind="model",
                required=model_required or (root / "model_params.json").exists(),
            )
        )
    if (root / "normalization_state.json").exists():
        entries.append(
            artifact_entry(
                "normalization_state.json",
                run_dir=root,
                kind="preprocessing",
                required=True,
            )
        )
    if explicit_state_path is not None:
        entries.append(artifact_entry(explicit_state_path, run_dir=root, kind="model", required=True))
    elif state_candidates:
        entries.extend(
            artifact_entry(path, run_dir=root, kind="model", required=True)
            for path in state_candidates
        )

    checkpoint_dir = root / "checkpoints"
    if checkpoint_dir.exists():
        entries.append(artifact_entry("checkpoints", run_dir=root, kind="checkpoint", required=True))
        entries.extend(
            artifact_entry(path, run_dir=root, kind="checkpoint", required=True)
            for path in sorted(checkpoint_dir.glob("ckpt_*.json"))
        )

    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)

    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_evidence_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_planning_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
        training_result=None,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    if (root / "experiments").exists():
        entries.append(artifact_entry("experiments", run_dir=root, kind="experiment", required=True))
    for filename, kind in [
        ("experiment_registry.json", "registry"),
        ("challenger_report.json", "report"),
        ("ablation_report.json", "report"),
        ("audit_report.json", "report"),
        ("belief_update.json", "report"),
        ("leaderboard.csv", "report"),
        ("reports/technical_report.md", "report"),
        ("reports/decision_memo.md", "report"),
    ]:
        path = root / filename
        if path.exists():
            entries.append(artifact_entry(filename, run_dir=root, kind=kind, required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_completion_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_decision_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for filename in [
        "completion_decision.json",
        "run_state.json",
        "stage_timeline.json",
        "mandate_evidence_review.json",
        "blocking_analysis.json",
        "next_action_queue.json",
    ]:
        path = root / filename
        if path.exists():
            entries.append(artifact_entry(filename, run_dir=root, kind="status", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_decision_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_profiles_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _decision_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="decision", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_profiles_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_benchmark_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _profiles_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="profile", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_lifecycle_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_completion_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for filename in [
        "champion_vs_candidate.json",
        "recalibration_decision.json",
        "retrain_decision.json",
        "promotion_decision.json",
        "rollback_decision.json",
    ]:
        path = root / filename
        if path.exists():
            entries.append(artifact_entry(filename, run_dir=root, kind="lifecycle", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_intelligence_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_evidence_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _intelligence_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="intelligence", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_research_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_intelligence_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _research_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="research", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_benchmark_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_research_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _benchmark_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="benchmark", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_feedback_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_autonomy_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _feedback_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="feedback", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_autonomy_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_decision_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    _refresh_lifecycle_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _autonomy_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="autonomy", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_access_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
    training_result: dict[str, Any] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_feedback_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    surface_paths = _access_surface_output_paths(root)
    if surface_paths["run_summary"].exists():
        entries.append(
            artifact_entry(
                "run_summary.json",
                run_dir=root,
                kind="summary",
                required=True,
            )
        )
    if surface_paths["summary_report"].exists():
        entries.append(
            artifact_entry(
                "reports/summary.md",
                run_dir=root,
                kind="report",
                required=True,
            )
        )
    for key in ("run_handoff", "next_run_options", "next_run_focus", "lab_learnings_snapshot"):
        path = surface_paths[key]
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="handoff" if "handoff" in key or "next_run" in key else "memory", required=False))
    for key in ("workspace_state", "workspace_lineage", "workspace_focus_history", "workspace_memory_policy", "next_run_plan"):
        path = surface_paths[key]
        if path.exists():
            display = str(path.relative_to(root.parent)).replace("\\", "/")
            entries.append(artifact_entry(display, run_dir=root, kind="workspace", required=False))
    for key in ("result_contract", "confidence_posture", "belief_revision_triggers", "focus_decision_record", "data_expansion_candidates"):
        path = surface_paths[key]
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="workspace", required=False))
    for key in ("user_result_report", "agent_result_report"):
        path = surface_paths[key]
        if path.exists():
            entries.append(artifact_entry(str(path.relative_to(root)).replace("\\", "/"), run_dir=root, kind="report", required=False))
    learnings_dir = default_learnings_state_dir(run_dir=root)
    for filename in ("learnings_state.json", "learnings.md"):
        path = learnings_dir / filename
        if path.exists():
            display = str(path.relative_to(root.parent)).replace("\\", "/")
            entries.append(artifact_entry(display, run_dir=root, kind="memory", required=False))
    for path in _control_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="control", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_assist_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_access_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for key, path in _assist_output_paths(root).items():
        if path.exists():
            entries.append(
                artifact_entry(
                    path.name,
                    run_dir=root,
                    kind="assist",
                    required=key != "assist_turn_log",
                )
            )
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_control_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_assist_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _control_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="control", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id"),
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_mission_control_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    if (root / "run_summary.json").exists():
        _refresh_control_manifest(
            root,
            run_id=run_id,
            policy_source=policy_source,
            labels=labels,
        )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for key, path in _mission_control_output_paths(root).items():
        if not path.exists():
            continue
        relative_path = path.relative_to(root)
        entries.append(
            artifact_entry(
                relative_path.as_posix(),
                run_dir=root,
                kind="mission_control",
                required=key != "mission_control_report",
            )
        )
    for path in _dojo_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="dojo", required=True))
    for path in _pulse_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="pulse", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id") or root.name,
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_dojo_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_mission_control_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _dojo_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="dojo", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id") or root.name,
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_pulse_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_dojo_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _pulse_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="pulse", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id") or root.name,
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_trace_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_pulse_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _trace_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="trace", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id") or root.name,
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_evals_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_trace_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _evals_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="evals", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id") or root.name,
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_search_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_evals_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _search_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="search", required=True))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id") or root.name,
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _refresh_daemon_manifest(
    run_dir: str | Path,
    *,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
) -> Path:
    root = Path(run_dir)
    _refresh_search_manifest(
        root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
    )
    existing = _read_existing_manifest_metadata(root)
    merged_labels = dict(existing.get("labels", {}))
    merged_labels.update(labels or {})
    entries = []
    for item in existing.get("entries", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        entries.append(
            artifact_entry(
                path,
                run_dir=root,
                kind=str(item.get("kind", "artifact") or "artifact"),
                required=bool(item.get("required", False)),
            )
        )
    for path in _daemon_output_paths(root).values():
        if path.exists():
            entries.append(artifact_entry(path.name, run_dir=root, kind="daemon", required=True))
    log_path = root / "background_job_log.jsonl"
    if log_path.exists():
        entries.append(artifact_entry(log_path.name, run_dir=root, kind="daemon", required=False))
    deduped_entries: list[Any] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped_entries.append(entry)
    return write_manifest(
        run_dir=root,
        run_id=run_id or existing.get("run_id") or root.name,
        policy_source=policy_source or existing.get("policy_source"),
        labels=merged_labels,
        entries=deduped_entries,
    )


def _read_existing_manifest_metadata(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_json_object(raw: str, *, arg_name: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid {arg_name} value: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{arg_name} must decode to a JSON object.")
    return parsed


def _parse_json_array(raw: str, *, arg_name: str) -> list[Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid {arg_name} value: {exc}") from exc
    if not isinstance(parsed, list):
        raise ValueError(f"{arg_name} must decode to a JSON array.")
    return parsed


def _parse_task_override_command(user_message: str) -> str | None:
    stripped = user_message.strip()
    if not stripped.lower().startswith("task "):
        return None
    return stripped[5:].strip()


def _parse_threshold_override_command(user_message: str) -> str | None:
    stripped = user_message.strip()
    if not stripped.lower().startswith("threshold "):
        return None
    return stripped[10:].strip()


def _drop_none_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _run_agent_session(
    *,
    agent: str,
    base_context: dict[str, Any],
    config_path: str | None,
    show_json: bool,
    max_turns: int,
) -> int:
    if max_turns < 0:
        print("max-turns must be >= 0")
        return 2

    print(f"agent> Welcome to Relaytic ({agent} session).")
    if agent == "analyst":
        default_dataset_path = _resolve_default_public_dataset_path()
        print(
            "agent> I can chat, inspect structured data, run Agent 1 analysis, "
            "save reports, and interpret the results."
        )
        print(
            "agent> Runtime mode: local LLM by default. Optional API mode: set "
            "RELAYTIC_PROVIDER=openai, RELAYTIC_API_CALLS_ALLOWED=true, "
            "RELAYTIC_REQUIRE_LOCAL_MODELS=false, RELAYTIC_OFFLINE_MODE=false, "
            "RELAYTIC_API_KEY=<key>."
        )
        print(
            "agent> Useful commands: /help, /context, /reset, /exit. "
            "At target selection use: list, list <filter>, all, or comma-separated names."
        )
        print(
            "agent> Task override: use `task regression`, `task binary_classification`, "
            "`task fraud_detection`, or `task auto` to clear it."
        )
        print(
            "agent> Threshold override: use `threshold favor_recall`, `threshold favor_precision`, "
            "`threshold favor_f1`, `threshold favor_pr_auc`, `threshold 0.35`, or `threshold auto`."
        )
        print(
            "agent> Hypothesis syntax: "
            "`hypothesis corr target:pred1,pred2; target2:pred3` and "
            "`hypothesis feature target:signal->rate_change; signal2->square`."
        )
        if default_dataset_path is not None:
            print(
                "agent> Dataset choice: paste a structured dataset path such as CSV/Parquet/JSONL/Excel or type `default` "
                "to run the built-in test dataset: "
                f"`{_path_for_display(default_dataset_path)}`."
            )
        else:
            print(
                "agent> Dataset choice: paste a structured dataset path such as CSV/Parquet/JSONL/Excel. "
                "(`default` is unavailable because no public test dataset was found.)"
            )
    else:
        default_dataset_path = _resolve_default_public_dataset_path()
        print(
            "agent> I can chat, load structured data, run direct modeler workflows, "
            "and explain the training outcome."
        )
        print(
            "agent> Useful commands: /help, /context, /reset, /exit. "
            "Use `list` after loading data to inspect available signals."
        )
        print(
            "agent> Task override: use `task regression`, `task binary_classification`, "
            "`task fraud_detection`, or `task auto` to clear it."
        )
        print(
            "agent> Direct build syntax: "
            "`build model linear_ridge with inputs A,B,C and target D` "
            "or `build model logistic_regression with inputs A,B and target class_label`."
        )
        print(
            "agent> Current executable models: `auto`, `linear_ridge`, "
            "`logistic_regression`, `lagged_logistic_regression`, `bagged_tree_classifier`, "
            "`boosted_tree_classifier`, `lagged_linear`, `lagged_tree_classifier`, "
            "`lagged_tree_ensemble`, `bagged_tree_ensemble`, `boosted_tree_ensemble` "
            "(aliases include `ridge`, `linear`, `logistic`, `logit`, `classifier`, "
            "`lagged_logistic`, `temporal_classifier`, `tree_classifier`, "
            "`gradient_boosting_classifier`, `lagged`, `temporal_linear`, `arx`, "
            "`temporal_tree_classifier`, `lagged_tree`, "
            "`lag_window_tree`, `temporal_tree`, `tree`, `tree_ensemble`, "
            "`extra_trees`, `gradient_boosting`, `hist_gradient_boosting`)."
        )
        print(
            "agent> During training I will print staged progress, compare candidates on "
            "validation/test, adapt model family/features/lags/thresholds when safe, "
            "suggest next data trajectories if the loop stalls, propose an inference command for the selected model, "
            "and then give an LLM interpretation grounded in those metrics."
        )
        print(
            "agent> Handoff syntax: "
            "`use handoff path\\\\to\\\\structured_report.json` "
            "to load an Agent 1 structured report and then confirm/override target, inputs, and model."
        )
        if default_dataset_path is not None:
            print(
                "agent> Dataset choice: paste a structured dataset path such as CSV/Parquet/JSONL/Excel, type `default`, "
                "or give a direct build request first and then provide the dataset."
            )
        else:
            print(
                "agent> Dataset choice: paste a structured dataset path such as CSV/Parquet/JSONL/Excel, "
                "or give a direct build request first and then provide the dataset."
            )
    session_messages: list[dict[str, str]] = []
    session_context = dict(base_context)
    if agent == "analyst":
        session_context.setdefault("workflow_stage", "awaiting_dataset_path")
    else:
        session_context.setdefault("workflow_stage", "awaiting_modeler_request_or_dataset")
    registry: Any | None = None

    def _get_registry() -> Any:
        nonlocal registry
        if registry is None:
            registry = build_default_registry()
        return registry

    turns = 0

    while True:
        try:
            raw_user = input("you> ")
        except EOFError:
            print("\nSession ended.")
            return 0
        except KeyboardInterrupt:
            print("\nSession interrupted.")
            return 0

        user_message = raw_user.strip()
        if not user_message:
            continue

        command = user_message.lower()
        if command in {"/exit", "/quit"}:
            print("Session ended.")
            return 0
        if command == "/help":
            if agent == "analyst":
                default_dataset_path = _resolve_default_public_dataset_path()
                print(
                    "agent> Commands: /help, /context, /reset, /exit. "
                    "For data analysis paste a .csv/.xlsx path."
                )
                print(
                    "agent> During target selection: type list, list <filter>, "
                    "all, numeric index, or comma-separated signal names."
                )
                print(
                    "agent> Task override: `task regression`, `task binary_classification`, "
                    "`task fraud_detection`, or `task auto`."
                )
                print(
                    "agent> Threshold override: `threshold favor_recall`, `threshold favor_precision`, "
                    "`threshold favor_f1`, `threshold favor_pr_auc`, numeric `threshold 0.35`, or `threshold auto`."
                )
                print(
                    "agent> You can also add hypotheses: "
                    "`hypothesis corr target:pred1,pred2` or "
                    "`hypothesis feature target:signal->rate_change`."
                )
                print(
                    "agent> Local runtime setup: "
                    "`relaytic setup-local-llm --provider llama_cpp --install-provider` "
                    "(Windows) or `relaytic setup-local-llm --provider llama_cpp` (macOS/Linux)."
                )
                print(
                    "agent> API mode (optional): set RELAYTIC_PROVIDER=openai, "
                    "RELAYTIC_API_CALLS_ALLOWED=true, RELAYTIC_REQUIRE_LOCAL_MODELS=false, "
                    "RELAYTIC_OFFLINE_MODE=false, RELAYTIC_API_KEY=<key>, then restart or /reset."
                )
                if default_dataset_path is not None:
                    print(
                        "agent> Type `default` to analyze the built-in public test dataset."
                    )
            else:
                default_dataset_path = _resolve_default_public_dataset_path()
                print("agent> Commands: /help, /context, /reset, /exit.")
                print(
                    "agent> Load a dataset by pasting a structured dataset path such as CSV/Parquet/JSONL/Excel, "
                    "or type `default` to use the built-in public test dataset."
                    if default_dataset_path is not None
                    else "agent> Load a dataset by pasting a structured dataset path such as CSV/Parquet/JSONL/Excel."
                )
                print(
                    "agent> Direct build syntax: "
                    "`build model linear_ridge with inputs A,B,C and target D` "
                    "or `build model logistic_regression with inputs A,B and target class_label`."
                )
                print(
                    "agent> Current executable models: `auto`, `linear_ridge`, "
                    "`logistic_regression`, `lagged_logistic_regression`, `bagged_tree_classifier`, "
                    "`boosted_tree_classifier`, `lagged_linear`, `lagged_tree_classifier`, "
                    "`lagged_tree_ensemble`, `bagged_tree_ensemble`, `boosted_tree_ensemble` "
                    "(aliases include `ridge`, `linear`, `logistic`, `logit`, `classifier`, "
                    "`lagged_logistic`, `temporal_classifier`, `tree_classifier`, "
                    "`gradient_boosting_classifier`, `lagged`, `temporal_linear`, `arx`, `lagged_tree`, "
                    "`lag_window_tree`, `temporal_tree`, `tree`, `tree_ensemble`, "
                    "`extra_trees`, `gradient_boosting`, `hist_gradient_boosting`)."
                )
                print(
                    "agent> You can also load an Agent 1 handoff via: "
                    "`use handoff path\\\\to\\\\structured_report.json`."
                )
                print(
                    "agent> Adaptive retry loop: when quality is weak, I can switch model family, "
                    "expand the feature set, widen lag windows, retune binary thresholds when safe, "
                    "and print concrete experiment recommendations if retries stall."
                )
                print(
                    "agent> After a successful run I will also propose ready-to-run "
                    "`run-inference` commands for new data using the selected checkpoint."
                )
                print(
                    "agent> Task override: `task regression`, `task binary_classification`, "
                    "`task fraud_detection`, or `task auto`."
                )
            continue
        if command == "/context":
            snapshot = dict(session_context)
            snapshot["session_messages"] = session_messages
            print(dumps_json(snapshot, indent=2))
            continue
        if command == "/reset":
            session_context = dict(base_context)
            if agent == "analyst":
                session_context["workflow_stage"] = "awaiting_dataset_path"
            else:
                session_context["workflow_stage"] = "awaiting_modeler_request_or_dataset"
            session_messages = []
            print("Session state reset.")
            continue
        task_override_command = _parse_task_override_command(user_message)
        if task_override_command is not None:
            normalized_task = normalize_task_type_hint(task_override_command)
            if normalized_task is None:
                supported = ", ".join(
                    item for item in _supported_task_types() if item != "auto"
                )
                print(
                    "agent> Unsupported task override. "
                    f"Use one of: {supported}, or `task auto`."
                )
                continue
            if normalized_task == "auto":
                session_context.pop("task_type_override", None)
                print("agent> Task override cleared. I will auto-detect the task again.")
                continue
            session_context["task_type_override"] = normalized_task
            print(
                f"agent> Task override set to `{normalized_task}`. "
                "I will use that for the next analysis/modeling step."
            )
            continue
        threshold_override_command = _parse_threshold_override_command(user_message)
        if threshold_override_command is not None:
            if agent != "modeler":
                print(
                    "agent> Threshold overrides apply to Agent 2 modeling. "
                    "Start or continue a modeler session to use them."
                )
                continue
            threshold_override = _normalize_threshold_override(threshold_override_command)
            if threshold_override is None:
                print(
                    "agent> Unsupported threshold override. Use `threshold auto`, "
                    "`threshold favor_recall`, `threshold favor_precision`, `threshold favor_f1`, "
                    "`threshold favor_pr_auc`, or `threshold 0.35`."
                )
                continue
            if threshold_override == "auto":
                session_context.pop("threshold_policy_override", None)
                print(
                    "agent> Threshold override cleared. "
                    "I will use validation-tuned automatic threshold selection again."
                )
                continue
            session_context["threshold_policy_override"] = threshold_override
            print(
                "agent> Threshold override set to "
                f"`{_format_threshold_override(threshold_override)}`. "
                "I will use that for the next modeling step."
            )
            continue

        if agent == "analyst":
            def _chat_reply_only(detour_user_message: str) -> str:
                return _llm_chat_detour(
                    agent=agent,
                    user_message=detour_user_message,
                    session_context=session_context,
                    session_messages=session_messages,
                    config_path=config_path,
                )

            def _chat_reply_internal(detour_user_message: str) -> str:
                return _llm_chat_detour(
                    agent=agent,
                    user_message=detour_user_message,
                    session_context=session_context,
                    session_messages=session_messages,
                    config_path=config_path,
                    record_in_history=False,
                )

            def _chat_detour_with_reprompt(detour_user_message: str, reminder: str) -> None:
                reply = _chat_reply_only(detour_user_message)
                if reply:
                    print(f"agent> {reply}")
                print(f"agent> {reminder}")

            def _modeler_chat_reply_internal(detour_user_message: str) -> str:
                return _llm_chat_detour(
                    agent="modeler",
                    user_message=detour_user_message,
                    session_context=session_context,
                    session_messages=session_messages,
                    config_path=config_path,
                    record_in_history=False,
                )

            try:
                autopilot = _run_analyst_autopilot_turn(
                    user_message=user_message,
                    registry=_get_registry(),
                    session_context=session_context,
                    chat_detour=_chat_detour_with_reprompt,
                    chat_reply_only=_chat_reply_internal,
                    modeler_chat_reply_only=_modeler_chat_reply_internal,
                )
            except Exception as exc:
                response = _runtime_error_fallback_message(
                    agent=agent,
                    user_message=user_message,
                    error=exc,
                )
                print(f"agent> {response}")
                session_messages.append({"role": "user", "content": user_message})
                session_messages.append({"role": "assistant", "content": response})
                session_messages = session_messages[-20:]
                session_context["last_event"] = _compact_event_for_context(
                    {"status": "respond", "message": response, "error": "runtime_error"}
                )
                turns += 1
                if max_turns > 0 and turns >= max_turns:
                    print(f"Reached max turns ({max_turns}). Session ended.")
                    return 0
                continue
            if autopilot is not None:
                response = autopilot["response"]
                summary_event = autopilot["event"]
                if summary_event.get("error"):
                    print(f"agent> {response}")
                    session_context["workflow_stage"] = "awaiting_dataset_path"
                session_messages.append({"role": "user", "content": user_message})
                session_messages.append({"role": "assistant", "content": response})
                session_messages = session_messages[-20:]
                session_context["last_event"] = _compact_event_for_context(summary_event)
                if not summary_event.get("error"):
                    tool_output = summary_event.get("tool_output")
                    next_stage = "analysis_completed"
                    if isinstance(tool_output, dict):
                        stage_from_tool = tool_output.get("workflow_stage")
                        if isinstance(stage_from_tool, str) and stage_from_tool.strip():
                            next_stage = stage_from_tool
                        report_path = tool_output.get("report_path")
                        if isinstance(report_path, str) and report_path.strip():
                            session_context["last_report_path"] = report_path
                        handoff_path = tool_output.get("handoff_json_path")
                        if isinstance(handoff_path, str) and handoff_path.strip():
                            session_context["last_handoff_path"] = handoff_path
                    session_context["workflow_stage"] = next_stage
                turns += 1
                if max_turns > 0 and turns >= max_turns:
                    print(f"Reached max turns ({max_turns}). Session ended.")
                    return 0
                continue

        if agent == "modeler":
            def _modeler_chat_reply_internal(detour_user_message: str) -> str:
                return _llm_chat_detour(
                    agent=agent,
                    user_message=detour_user_message,
                    session_context=session_context,
                    session_messages=session_messages,
                    config_path=config_path,
                    record_in_history=False,
                )

            try:
                autopilot = _run_modeler_autopilot_turn(
                    user_message=user_message,
                    registry=_get_registry(),
                    session_context=session_context,
                    chat_reply_only=_modeler_chat_reply_internal,
                )
            except Exception as exc:
                response = _runtime_error_fallback_message(
                    agent=agent,
                    user_message=user_message,
                    error=exc,
                )
                print(f"agent> {response}")
                session_messages.append({"role": "user", "content": user_message})
                session_messages.append({"role": "assistant", "content": response})
                session_messages = session_messages[-20:]
                session_context["last_event"] = _compact_event_for_context(
                    {"status": "respond", "message": response, "error": "runtime_error"}
                )
                turns += 1
                if max_turns > 0 and turns >= max_turns:
                    print(f"Reached max turns ({max_turns}). Session ended.")
                    return 0
                continue
            if autopilot is not None:
                response = autopilot["response"]
                summary_event = autopilot["event"]
                session_messages.append({"role": "user", "content": user_message})
                session_messages.append({"role": "assistant", "content": response})
                session_messages = session_messages[-20:]
                session_context["last_event"] = _compact_event_for_context(summary_event)
                turns += 1
                if max_turns > 0 and turns >= max_turns:
                    print(f"Reached max turns ({max_turns}). Session ended.")
                    return 0
                continue

        turn_context = dict(session_context)
        turn_context["session_messages"] = list(session_messages)
        turn_context["recent_user_prompts"] = _recent_user_prompts(
            session_messages=session_messages,
            limit=5,
        )
        try:
            result = _invoke_agent_once_with_recovery(
                agent=agent,
                user_message=user_message,
                context=turn_context,
                config_path=config_path,
            )
        except Exception as exc:
            response = _runtime_error_fallback_message(
                agent=agent,
                user_message=user_message,
                error=exc,
            )
            print(f"agent> {response}")
            session_messages.append({"role": "user", "content": user_message})
            session_messages.append({"role": "assistant", "content": response})
            session_messages = session_messages[-20:]
            session_context["last_event"] = _compact_event_for_context(
                {"status": "respond", "message": response, "error": "runtime_error"}
            )
            turns += 1
            if max_turns > 0 and turns >= max_turns:
                print(f"Reached max turns ({max_turns}). Session ended.")
                return 0
            continue

        event = result.get("event", {})
        response = str(event.get("message", "")).strip() or "[empty response]"
        response = _rewrite_unhelpful_response(
            agent=agent,
            user_message=user_message,
            response=response,
            chat_detour=(
                _chat_reply_only
                if agent == "analyst"
                else None
            ),
        )
        stage_reminder = _analyst_stage_reprompt_message(
            agent=agent,
            session_context=session_context,
            user_message=user_message,
        )
        print(f"agent> {response}")
        if stage_reminder:
            print(f"agent> {stage_reminder}")
            response = f"{response}\n{stage_reminder}"
        if show_json:
            print(dumps_json(result, indent=2))

        session_messages.append({"role": "user", "content": user_message})
        session_messages.append({"role": "assistant", "content": response})
        session_messages = session_messages[-20:]
        session_context["last_event"] = _compact_event_for_context(event)

        turns += 1
        if max_turns > 0 and turns >= max_turns:
            print(f"Reached max turns ({max_turns}). Session ended.")
            return 0


def _analyst_stage_reprompt_message(
    *,
    agent: str,
    session_context: dict[str, Any],
    user_message: str,
) -> str:
    stage = str(session_context.get("workflow_stage", "")).strip().lower()
    lowered = user_message.strip().lower()
    if agent == "analyst":
        if stage != "awaiting_dataset_path":
            return ""
        if lowered == "default":
            return ""
        if _extract_first_data_path(user_message) is not None:
            return ""
        return (
            "To continue, paste a structured dataset path such as CSV/Parquet/JSONL/Excel or type `default` "
            "to run the built-in test dataset."
        )
    if agent == "modeler":
        if stage == "awaiting_modeler_dataset_path":
            if lowered == "default":
                return ""
            if _extract_first_data_path(user_message) is not None:
                return ""
            return (
                "To continue, paste a structured dataset path such as CSV/Parquet/JSONL/Excel or type `default` "
                "so I can load data for the pending model request."
            )
        if stage == "modeler_dataset_ready":
            return (
                "To continue, type `list` to inspect signals or "
                "`build model linear_ridge with inputs A,B and target C`."
            )
    return ""


def _run_analyst_autopilot_turn(
    *,
    user_message: str,
    registry: Any,
    session_context: dict[str, Any],
    chat_detour: Callable[[str, str], None] | None = None,
    chat_reply_only: Callable[[str], str] | None = None,
    modeler_chat_reply_only: Callable[[str], str] | None = None,
) -> dict[str, Any] | None:
    detected: Path | None = None
    if user_message.strip().lower() == "default":
        detected = _resolve_default_public_dataset_path()
        if detected is None:
            response = (
                "Default dataset is not available. "
                "Please paste a structured dataset path from your machine."
            )
            return {
                "response": response,
                "event": {
                    "status": "respond",
                    "message": response,
                    "error": "default_dataset_missing",
                },
            }
    else:
        detected = _extract_first_data_path(user_message)
    if detected is None:
        return None

    data_path = str(detected.resolve())
    if not detected.exists():
        response = f"Detected data path but file does not exist: {data_path}"
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "missing_path"},
        }

    print(f"agent> Detected data file: {_path_for_display(Path(data_path))}")
    preflight_args: dict[str, Any] = {"path": data_path}
    preflight = _execute_registry_tool(registry, "prepare_ingestion_step", preflight_args)
    print(f"agent> Ingestion check: {preflight.get('message', '')}")

    if preflight.get("status") == "needs_user_input":
        options = preflight.get("options") or preflight.get("available_sheets") or []
        selected_sheet = _prompt_sheet_selection(options, chat_detour=chat_detour)
        if selected_sheet is None:
            response = "Sheet selection aborted. Please provide a valid sheet."
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "sheet_selection_aborted"},
            }
        preflight_args["sheet_name"] = selected_sheet
        preflight = _execute_registry_tool(registry, "prepare_ingestion_step", preflight_args)
        print(f"agent> Ingestion check: {preflight.get('message', '')}")

    if preflight.get("status") != "ok":
        response = preflight.get("message") or "Ingestion failed."
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "ingestion_error"},
        }

    selected_sheet = preflight.get("selected_sheet")
    header_row = preflight.get("header_row")
    data_start_row = preflight.get("data_start_row")

    inferred_header_row = preflight.get("header_row")
    wide_table = int(preflight.get("column_count") or 0) >= 50
    force_header_check = (
        isinstance(inferred_header_row, int) and inferred_header_row > 0 and wide_table
    )
    if bool(preflight.get("needs_user_confirmation")) or force_header_check:
        confidence = preflight.get("header_confidence")
        if bool(preflight.get("needs_user_confirmation")):
            print(
                "agent> Header detection confidence is low "
                f"({confidence if confidence is not None else 'n/a'})."
            )
        if force_header_check and not bool(preflight.get("needs_user_confirmation")):
            print(
                "agent> Wide table with non-zero header row detected; "
                "please confirm inferred rows before analysis."
            )
        _print_header_preview(preflight)
        resolved_header_row = int(header_row) if isinstance(header_row, int) else 0
        resolved_data_start = (
            int(data_start_row)
            if isinstance(data_start_row, int)
            else max(resolved_header_row + 1, 1)
        )
        header_row, data_start_row = _prompt_header_confirmation(
            header_row=resolved_header_row,
            data_start_row=resolved_data_start,
            chat_detour=chat_detour,
        )

        preflight_args["header_row"] = int(header_row)
        preflight_args["data_start_row"] = int(data_start_row)
        preflight = _execute_registry_tool(registry, "prepare_ingestion_step", preflight_args)
        print(f"agent> Ingestion check: {preflight.get('message', '')}")
        _print_header_preview(preflight)
        if preflight.get("status") != "ok":
            response = preflight.get("message") or "Ingestion confirmation failed."
            return {
                "response": response,
                "event": {
                    "status": "respond",
                    "message": response,
                    "error": "ingestion_confirmation_error",
                },
            }

    _print_analysis_dataset_overview(preflight=preflight)
    print(
        "agent> Preparing Agent 1 analysis. "
        "I will ask about target scope, sample budget, data cleaning, and lag assumptions."
    )
    analysis_args: dict[str, Any] = {
        "data_path": data_path,
        "save_report": True,
        "save_artifacts": True,
        "enable_strategy_search": True,
        "strategy_search_candidates": 4,
        "include_feature_engineering": True,
        "top_k_predictors": 10,
        "feature_scan_predictors": 10,
        "max_feature_opportunities": 20,
        "confidence_top_k": 10,
        "bootstrap_rounds": 40,
        "stability_windows": 4,
    }
    task_type_override = str(session_context.get("task_type_override", "")).strip() or None
    if task_type_override:
        analysis_args["task_type_hint"] = task_type_override
        print(f"agent> Task override: forcing task profile `{task_type_override}` during analysis.")
    hypothesis_state: dict[str, list[dict[str, Any]]] = {
        "user_hypotheses": [],
        "feature_hypotheses": [],
    }
    row_count = int(preflight.get("row_count") or 0)
    signal_inventory_available = (
        "numeric_signal_columns" in preflight or "signal_columns" in preflight
    )
    numeric_signals_raw = preflight.get("numeric_signal_columns")
    if isinstance(numeric_signals_raw, list) and numeric_signals_raw:
        numeric_signals = [str(item) for item in numeric_signals_raw]
    else:
        fallback_signals = preflight.get("signal_columns")
        numeric_signals = [str(item) for item in fallback_signals] if isinstance(fallback_signals, list) else []

    if not numeric_signals and signal_inventory_available:
        response = "No numeric signals were detected after ingestion. Please load a dataset with usable numeric columns."
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "no_numeric_signals"},
        }
    if numeric_signals:
        suggested_targets = _suggest_default_analysis_targets(
            available_signals=numeric_signals,
            default_count=5,
        )
        if len(numeric_signals) == 1:
            only_target = numeric_signals[0]
            analysis_args["target_signals"] = [only_target]
            print(
                "agent> Only one numeric signal is available, "
                f"so I will analyze `{only_target}` as the target."
            )
        else:
            print(
                "agent> Dataset scope: "
                f"{len(numeric_signals)} numeric signals are available for target selection."
            )
            if len(numeric_signals) > 40:
                print(
                    "agent> Full all-signal correlation can take a long time on this dataset."
                )
            if suggested_targets:
                print(
                    "agent> Suggested target set: "
                    + ", ".join(f"`{item}`" for item in suggested_targets[:5])
                    + "."
                )
            print(_target_selection_prompt_text(default_targets=suggested_targets))
            selected_targets = _prompt_target_selection(
                available_signals=numeric_signals,
                default_count=5,
                default_targets=suggested_targets,
                hypothesis_state=hypothesis_state,
                chat_detour=chat_detour,
            )
            if selected_targets is not None:
                analysis_args["target_signals"] = selected_targets
                print(f"agent> Using focused targets: {selected_targets}")
                print(
                    "agent> Focused target mode enabled with full analysis "
                    "(multi-technique correlations + feature engineering)."
                )
            else:
                print("agent> Running full all-signal analysis as requested.")
    else:
        print(
            "agent> Signal inventory was not exposed by ingestion preflight, "
            "so I will proceed with the tool defaults for target discovery."
        )

    sample_plan = _prompt_sample_budget(row_count=row_count, chat_detour=chat_detour)
    analysis_args.update(sample_plan)

    data_issue_plan = _prompt_data_issue_handling(preflight=preflight, chat_detour=chat_detour)
    analysis_args.update(data_issue_plan)

    if len(numeric_signals) > 40 and analysis_args.get("target_signals") is None:
        print(
            "agent> High-dimensional full run confirmed. "
            "This can take longer, but all numeric targets will be evaluated."
        )

    inline_hypotheses = _parse_inline_hypothesis_command(
        user_message=user_message,
        available_signals=numeric_signals,
    )
    if inline_hypotheses["user_hypotheses"] or inline_hypotheses["feature_hypotheses"]:
        _merge_hypothesis_state(hypothesis_state, inline_hypotheses)
        print(
            "agent> Parsed inline hypotheses from your request: "
            f"correlation={len(inline_hypotheses['user_hypotheses'])}, "
            f"feature={len(inline_hypotheses['feature_hypotheses'])}."
        )

    if hypothesis_state["user_hypotheses"] or hypothesis_state["feature_hypotheses"]:
        analysis_args["user_hypotheses"] = hypothesis_state["user_hypotheses"]
        analysis_args["feature_hypotheses"] = hypothesis_state["feature_hypotheses"]
        print(
            "agent> User hypotheses will be investigated additionally: "
            f"correlation={len(hypothesis_state['user_hypotheses'])}, "
            f"feature={len(hypothesis_state['feature_hypotheses'])}."
        )

    timestamp_hint = str(preflight.get("timestamp_column_hint") or "").strip()
    estimated_sample_period = _safe_float_or_none(preflight.get("estimated_sample_period_seconds"))
    if timestamp_hint:
        lag_plan = _prompt_lag_preferences(
            timestamp_column_hint=timestamp_hint,
            estimated_sample_period_seconds=estimated_sample_period,
            chat_detour=chat_detour,
        )
        analysis_args["timestamp_column"] = timestamp_hint
        analysis_args["max_lag"] = int(lag_plan["max_lag"])
        print(
            "agent> Lag plan: "
            f"enabled={lag_plan['enabled']}, "
            f"dimension={lag_plan['dimension']}, "
            f"max_lag_samples={lag_plan['max_lag']}."
        )

    if selected_sheet:
        analysis_args["sheet_name"] = str(selected_sheet)
    if header_row is not None:
        analysis_args["header_row"] = int(header_row)
    if data_start_row is not None:
        analysis_args["data_start_row"] = int(data_start_row)

    print("agent> Running Agent 1 analysis now.")
    analysis = _execute_registry_tool(registry, "run_agent1_analysis", analysis_args)
    summary = (
        "Analysis complete: "
        f"data_mode={analysis.get('data_mode', 'unknown')}, "
        f"targets={analysis.get('target_count', 'n/a')}, "
        f"candidates={analysis.get('candidate_count', 'n/a')}."
    )
    report_path = str(analysis.get("report_path", "n/a"))
    report_line = f"Report saved: {report_path}"
    print(f"agent> {summary}")
    print(f"agent> {report_line}")
    _print_task_profile_summary(analysis.get("task_profiles"), context_label="analysis")
    artifact_paths = analysis.get("artifact_paths") if isinstance(analysis.get("artifact_paths"), dict) else {}
    handoff_json_path = str(artifact_paths.get("json_path", "")).strip()
    if handoff_json_path:
        print(f"agent> Structured handoff saved: {handoff_json_path}")
    top3_correlations = _extract_top3_correlations_global(analysis)
    if chat_reply_only is not None:
        interpretation = _generate_analysis_interpretation(
            analysis=analysis,
            chat_reply_only=chat_reply_only,
        )
        if interpretation:
            print("agent> LLM interpretation:")
            for line in interpretation.splitlines():
                text = line.strip()
                if text:
                    print(f"agent> {text}")
            if top3_correlations and not _interpretation_mentions_top3(
                interpretation=interpretation,
                top3=top3_correlations,
            ):
                print(f"agent> {_format_top3_correlations_line(top3_correlations)}")
        elif top3_correlations:
            print(
                "agent> LLM interpretation unavailable for this turn. "
                "Showing deterministic correlation summary."
            )
            print(f"agent> {_format_top3_correlations_line(top3_correlations)}")

    modeler_result: dict[str, Any] | None = None
    workflow_stage = "analysis_completed"
    if handoff_json_path:
        start_modeling = _prompt_start_modeling_after_analysis(chat_detour=chat_detour)
        if start_modeling:
            print("agent> Starting Agent 2 handoff-driven modeling.")
            modeler_result = _start_modeler_from_handoff_path(
                handoff_path=Path(handoff_json_path),
                registry=registry,
                session_context=session_context,
                chat_reply_only=modeler_chat_reply_only,
            )
            modeler_event = modeler_result.get("event") if isinstance(modeler_result, dict) else {}
            if isinstance(modeler_event, dict) and not modeler_event.get("error"):
                workflow_stage = "model_training_completed"

    response = f"{summary} {report_line}"
    event = {
        "status": "respond",
        "message": response,
        "tool_output": {
            "data_mode": analysis.get("data_mode"),
            "target_count": analysis.get("target_count"),
            "candidate_count": analysis.get("candidate_count"),
            "task_profiles": analysis.get("task_profiles"),
            "report_path": report_path,
            "handoff_json_path": handoff_json_path,
            "workflow_stage": workflow_stage,
            "modeler_started": bool(modeler_result is not None),
        },
    }
    return {"response": response, "event": event}


def _prompt_start_modeling_after_analysis(
    *,
    chat_detour: Callable[[str, str], None] | None = None,
) -> bool:
    while True:
        print("agent> Start Agent 2 modeling now from this handoff? [y/N]")
        answer = input("you> ").strip().lower()
        if answer in {"", "n", "no"}:
            return False
        if answer in {"y", "yes"}:
            return True
        if _looks_like_small_talk(answer):
            if chat_detour is not None:
                chat_detour(
                    answer,
                    "To continue, reply Y to start Agent 2 now, or N to stay in the analyst session.",
                )
            else:
                print("agent> Reply Y to start Agent 2 now, or N to stay in the analyst session.")
            continue
        print("agent> Please answer Y or N.")


def _start_modeler_from_handoff_path(
    *,
    handoff_path: Path,
    registry: Any,
    session_context: dict[str, Any],
    chat_reply_only: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    handoff = _load_modeler_handoff_payload(handoff_path)
    if isinstance(handoff.get("error"), str):
        response = str(handoff["error"])
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "handoff_load_error"},
        }

    data_path = str(handoff.get("data_path", "")).strip()
    if not data_path:
        response = (
            "The handoff file does not contain a usable `data_path`. "
            "You can still start the modeler session manually and provide a dataset."
        )
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "handoff_missing_data_path"},
        }

    dataset_result = _prepare_modeler_dataset_for_session(
        path=data_path,
        registry=registry,
        session_context=session_context,
    )
    if dataset_result.get("error"):
        response = str(dataset_result["error"])
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "modeler_dataset_error"},
        }

    dataset = _modeler_loaded_dataset(session_context)
    if dataset is None:
        response = "Modeler dataset state could not be initialized."
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "modeler_state_error"},
        }

    build_request = _modeler_request_from_handoff(
        payload=handoff["payload"],
        handoff=handoff["handoff"],
        available_signals=list(dataset.get("signal_columns", [])),
    )
    if build_request is None:
        response = (
            "I could not derive a usable modeling request from that handoff. "
            "Start the modeler session manually if you want to override everything."
        )
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "handoff_parse_error"},
        }

    session_context["active_handoff"] = handoff["handoff"]
    handoff_info = handoff["handoff"]
    print(
        "agent> Handoff contract: "
        f"data_mode=`{handoff_info.get('dataset_profile', {}).get('data_mode', 'n/a')}`, "
        f"task=`{handoff_info.get('task_type', 'n/a')}`, "
        f"split=`{handoff_info.get('split_strategy', 'n/a')}`, "
        f"acceptance={handoff_info.get('acceptance_criteria', {})}."
    )
    print(
        "agent> Handoff suggestion: "
        f"target=`{build_request['target_raw']}`, "
        f"inputs={build_request['feature_raw']}, "
        f"recommended_model=`{build_request['requested_model_family']}`."
    )
    build_request = _prompt_modeler_overrides(
        request=build_request,
        available_signals=list(dataset.get("signal_columns", [])),
    )
    return _execute_modeler_build_request(
        build_request=build_request,
        registry=registry,
        session_context=session_context,
        chat_reply_only=chat_reply_only,
    )


def _run_modeler_autopilot_turn(
    *,
    user_message: str,
    registry: Any,
    session_context: dict[str, Any],
    chat_reply_only: Callable[[str], str] | None = None,
) -> dict[str, Any] | None:
    stripped = user_message.strip()
    lowered = stripped.lower()
    stage = str(session_context.get("workflow_stage", "")).strip().lower()

    if stage == "awaiting_inference_decision":
        return _handle_modeler_inference_decision_turn(
            user_message=user_message,
            session_context=session_context,
            chat_reply_only=chat_reply_only,
        )

    if stage == "awaiting_inference_data_path":
        return _handle_modeler_inference_data_path_turn(
            user_message=user_message,
            session_context=session_context,
            chat_reply_only=chat_reply_only,
        )

    if lowered.startswith(("use handoff", "load handoff")):
        handoff_path = _extract_first_json_path(user_message)
        if handoff_path is None:
            response = (
                "I did not detect a handoff JSON path. "
                "Use: `use handoff path\\to\\structured_report.json`."
            )
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "handoff_path_missing"},
            }
        handoff = _load_modeler_handoff_payload(handoff_path)
        if isinstance(handoff.get("error"), str):
            response = str(handoff["error"])
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "handoff_load_error"},
            }

        data_path = str(handoff.get("data_path", "")).strip()
        if not data_path:
            response = (
                "The handoff file does not contain a usable `data_path`. "
                "Provide a dataset path directly or generate a newer Agent 1 structured report."
            )
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "handoff_missing_data_path"},
            }

        dataset_result = _prepare_modeler_dataset_for_session(
            path=data_path,
            registry=registry,
            session_context=session_context,
        )
        if dataset_result.get("error"):
            response = str(dataset_result["error"])
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "modeler_dataset_error"},
            }

        dataset = _modeler_loaded_dataset(session_context)
        if dataset is None:
            response = "Modeler dataset state could not be initialized."
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "modeler_state_error"},
            }

        build_request = _modeler_request_from_handoff(
            payload=handoff["payload"],
            handoff=handoff["handoff"],
            available_signals=list(dataset.get("signal_columns", [])),
        )
        if build_request is None:
            response = (
                "I could not derive a usable modeling request from that handoff. "
                "Please specify target, inputs, and model directly."
            )
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "handoff_parse_error"},
            }

        session_context["active_handoff"] = handoff["handoff"]
        handoff_info = handoff["handoff"]
        print(
            "agent> Handoff contract: "
            f"data_mode=`{handoff_info.get('dataset_profile', {}).get('data_mode', 'n/a')}`, "
            f"task=`{handoff_info.get('task_type', 'n/a')}`, "
            f"split=`{handoff_info.get('split_strategy', 'n/a')}`, "
            f"acceptance={handoff_info.get('acceptance_criteria', {})}."
        )
        print(
            "agent> Handoff suggestion: "
            f"target=`{build_request['target_raw']}`, "
            f"inputs={build_request['feature_raw']}, "
            f"recommended_model=`{build_request['requested_model_family']}`."
        )
        build_request = _prompt_modeler_overrides(
            request=build_request,
            available_signals=list(dataset.get("signal_columns", [])),
        )
        return _execute_modeler_build_request(
            build_request=build_request,
            registry=registry,
            session_context=session_context,
            chat_reply_only=chat_reply_only,
        )

    parsed_request = _parse_modeler_build_request(user_message)
    if parsed_request is not None:
        requested_data_path = str(parsed_request.get("data_path", "")).strip()
        if requested_data_path:
            dataset_result = _prepare_modeler_dataset_for_session(
                path=requested_data_path,
                registry=registry,
                session_context=session_context,
            )
            if dataset_result.get("error"):
                response = str(dataset_result["error"])
                return {
                    "response": response,
                    "event": {
                        "status": "respond",
                        "message": response,
                        "error": "modeler_dataset_error",
                    },
                }

        if _modeler_loaded_dataset(session_context) is None:
            session_context["pending_model_request"] = parsed_request
            session_context["workflow_stage"] = "awaiting_modeler_dataset_path"
            response = (
                "I parsed your model request. To continue, paste a structured dataset path "
                "or type `default` so I can load the training dataset first."
            )
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response},
            }
        return _execute_modeler_build_request(
            build_request=parsed_request,
            registry=registry,
            session_context=session_context,
            chat_reply_only=chat_reply_only,
        )

    if lowered.startswith("list"):
        dataset = _modeler_loaded_dataset(session_context)
        if dataset is None:
            response = (
                "Load a dataset first, then I can show available signal names. "
                "Paste a structured dataset path such as CSV/Parquet/JSONL/Excel or type `default`."
            )
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response},
            }
        query = stripped[4:].strip()
        _print_signal_names(list(dataset.get("signal_columns", [])), query=query)
        response = "Signal list displayed."
        return {
            "response": response,
            "event": {"status": "respond", "message": response},
        }

    detected: Path | None = None
    if lowered == "default":
        detected = _resolve_default_public_dataset_path()
        if detected is None:
            response = (
                "Default dataset is not available. "
                "Please paste a structured dataset path from your machine."
            )
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "default_dataset_missing"},
            }
    else:
        detected = _extract_first_data_path(user_message)

    if detected is None:
        return None

    dataset_result = _prepare_modeler_dataset_for_session(
        path=str(detected),
        registry=registry,
        session_context=session_context,
    )
    if dataset_result.get("error"):
        response = str(dataset_result["error"])
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "modeler_dataset_error"},
        }

    pending_request = session_context.pop("pending_model_request", None)
    if isinstance(pending_request, dict):
        print("agent> Continuing with your pending model request.")
        return _execute_modeler_build_request(
            build_request=pending_request,
            registry=registry,
            session_context=session_context,
            chat_reply_only=chat_reply_only,
        )

    response = (
        "Dataset ready. Type `list` to inspect signals, "
        "or `build model linear_ridge with inputs A,B and target C` to train."
    )
    print(f"agent> {response}")
    return {
        "response": response,
        "event": {
            "status": "respond",
            "message": response,
            "tool_output": {
                "data_path": str((detected if lowered != 'default' else _resolve_default_public_dataset_path()) or detected),
                "signal_count": len((_modeler_loaded_dataset(session_context) or {}).get("signal_columns", [])),
            },
        },
    }


def _prepare_modeler_dataset_for_session(
    *,
    path: str,
    registry: Any,
    session_context: dict[str, Any],
) -> dict[str, Any]:
    data_path = str(Path(path).expanduser())
    detected = Path(data_path)
    if not detected.exists():
        response = f"Detected data path but file does not exist: {data_path}"
        print(f"agent> {response}")
        return {"error": response}

    print(f"agent> Detected data file: {_path_for_display(detected)}")
    preflight_args: dict[str, Any] = {"path": data_path}
    preflight = _execute_registry_tool(registry, "prepare_ingestion_step", preflight_args)
    print(f"agent> Ingestion check: {preflight.get('message', '')}")

    if preflight.get("status") == "needs_user_input":
        options = preflight.get("options") or preflight.get("available_sheets") or []
        selected_sheet = _prompt_sheet_selection(options)
        if selected_sheet is None:
            return {"error": "Sheet selection aborted. Please provide a valid sheet."}
        preflight_args["sheet_name"] = selected_sheet
        preflight = _execute_registry_tool(registry, "prepare_ingestion_step", preflight_args)
        print(f"agent> Ingestion check: {preflight.get('message', '')}")

    if preflight.get("status") != "ok":
        return {"error": preflight.get("message") or "Ingestion failed."}

    selected_sheet = preflight.get("selected_sheet")
    header_row = preflight.get("header_row")
    data_start_row = preflight.get("data_start_row")
    inferred_header_row = preflight.get("header_row")
    wide_table = int(preflight.get("column_count") or 0) >= 50
    force_header_check = isinstance(inferred_header_row, int) and inferred_header_row > 0 and wide_table
    if bool(preflight.get("needs_user_confirmation")) or force_header_check:
        if bool(preflight.get("needs_user_confirmation")):
            print(
                "agent> Header detection confidence is low "
                f"({preflight.get('header_confidence', 'n/a')})."
            )
        if force_header_check and not bool(preflight.get("needs_user_confirmation")):
            print(
                "agent> Wide table with non-zero header row detected; "
                "please confirm inferred rows before modeling."
            )
        _print_header_preview(preflight)
        resolved_header_row = int(header_row) if isinstance(header_row, int) else 0
        resolved_data_start = (
            int(data_start_row)
            if isinstance(data_start_row, int)
            else max(resolved_header_row + 1, 1)
        )
        header_row, data_start_row = _prompt_header_confirmation(
            header_row=resolved_header_row,
            data_start_row=resolved_data_start,
        )
        preflight_args["header_row"] = int(header_row)
        preflight_args["data_start_row"] = int(data_start_row)
        preflight = _execute_registry_tool(registry, "prepare_ingestion_step", preflight_args)
        print(f"agent> Ingestion check: {preflight.get('message', '')}")
        _print_header_preview(preflight)
        if preflight.get("status") != "ok":
            return {"error": preflight.get("message") or "Ingestion confirmation failed."}

    dataset = {
        "data_path": data_path,
        "sheet_name": selected_sheet,
        "header_row": header_row,
        "data_start_row": data_start_row,
        "timestamp_column_hint": str(preflight.get("timestamp_column_hint") or "").strip() or None,
        "signal_columns": [str(item) for item in (preflight.get("signal_columns") or [])],
        "numeric_signal_columns": [
            str(item) for item in (preflight.get("numeric_signal_columns") or [])
        ],
        "row_count": int(preflight.get("row_count") or 0),
    }
    session_context["modeler_dataset"] = dataset
    session_context["workflow_stage"] = "modeler_dataset_ready"
    print(
        "agent> Dataset ready: "
        f"rows={dataset['row_count']}, "
        f"signals={len(dataset['signal_columns'])}, "
        f"numeric_signals={len(dataset['numeric_signal_columns'])}."
    )
    return {"dataset": dataset}


def _modeler_loaded_dataset(session_context: dict[str, Any]) -> dict[str, Any] | None:
    dataset = session_context.get("modeler_dataset")
    return dataset if isinstance(dataset, dict) else None


def _parse_modeler_build_request(user_message: str) -> dict[str, Any] | None:
    text = user_message.strip()
    pattern = re.compile(
        r"^\s*(?:build|train)(?:\s+me)?\s+model\s+(?P<model>[A-Za-z0-9_\-]+)\s+"
        r"with\s+(?:inputs|inouts|features|predictors)\s+(?P<inputs>.+?)\s+"
        r"and\s+target\s+(?P<target>.+?)"
        r"(?:\s+(?:using|from|on)(?:\s+data)?\s+.+)?\s*$",
        flags=re.IGNORECASE,
    )
    match = pattern.match(text)
    if not match:
        return None
    inputs_raw = match.group("inputs").strip()
    target_raw = _strip_wrapping_quotes(match.group("target").strip())
    feature_raw = _split_modeler_input_tokens(inputs_raw)
    if not feature_raw or not target_raw:
        return None
    data_path = _extract_first_data_path(user_message)
    requested_model_family = match.group("model").strip()
    normalized_model = _normalize_modeler_model_family(requested_model_family)
    return {
        "requested_model_family": requested_model_family,
        "feature_raw": feature_raw,
        "target_raw": target_raw,
        "data_path": str(data_path) if data_path is not None else "",
        "acceptance_criteria": {},
        "loop_policy": {
            "enabled": True,
            "max_attempts": 3,
            "allow_architecture_switch": True,
            "allow_feature_set_expansion": True,
            "allow_lag_horizon_expansion": True,
            "allow_threshold_policy_tuning": True,
            "suggest_more_data_when_stalled": True,
        },
        "user_locked_model_family": normalized_model not in {None, "auto"},
        "source": "direct",
    }


def _split_modeler_input_tokens(raw: str) -> list[str]:
    text = raw.strip()
    if not text:
        return []
    if "," in text or "|" in text:
        parts = [item.strip() for item in re.split(r"[,|]", text) if item.strip()]
    else:
        parts = [item.strip() for item in text.split() if item.strip()]
    return [_strip_wrapping_quotes(item) for item in parts if _strip_wrapping_quotes(item)]


def _strip_wrapping_quotes(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        return text[1:-1].strip()
    return text


def _execute_modeler_build_request(
    *,
    build_request: dict[str, Any],
    registry: Any,
    session_context: dict[str, Any],
    chat_reply_only: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    dataset = _modeler_loaded_dataset(session_context)
    if dataset is None:
        response = "No dataset is loaded. Paste a structured dataset path such as CSV/Parquet/JSONL/Excel or type `default` first."
        print(f"agent> {response}")
        session_context["workflow_stage"] = "awaiting_modeler_dataset_path"
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "dataset_missing"},
        }

    numeric_signals = list(dataset.get("numeric_signal_columns", []))
    if not numeric_signals:
        response = (
            "The loaded dataset does not expose usable numeric signals for training. "
            "Please load another dataset or adjust the header selection."
        )
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "no_numeric_signals"},
        }

    target = _resolve_signal_name(str(build_request.get("target_raw", "")).strip(), numeric_signals)
    if target is None:
        response = (
            "I could not resolve the requested target signal in the loaded dataset. "
            "Type `list` to inspect signal names and retry."
        )
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "target_unresolved"},
        }

    raw_features = [str(item).strip() for item in build_request.get("feature_raw", [])]
    features: list[str] = []
    unknown_features: list[str] = []
    seen: set[str] = set()
    for raw in raw_features:
        resolved = _resolve_signal_name(raw, numeric_signals)
        if resolved is None:
            unknown_features.append(raw)
            continue
        if resolved == target or resolved in seen:
            continue
        features.append(resolved)
        seen.add(resolved)
    if unknown_features:
        print(f"agent> Ignoring unknown input signals: {unknown_features}")
    if not features:
        response = (
            "I did not resolve any usable numeric input signals after validation. "
            "Type `list` to inspect signal names and retry."
        )
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "features_unresolved"},
        }
    current_features = list(features)

    requested_model = str(build_request.get("requested_model_family", "")).strip() or "linear_ridge"
    resolved_model = _normalize_modeler_model_family(requested_model)
    if resolved_model is None:
        response = (
            f"Requested model `{requested_model}` is not implemented yet. "
            "Currently available: `auto`, `linear_ridge` "
            "(aliases: `ridge`, `linear`, `incremental_linear_surrogate`), "
            "`logistic_regression` (aliases: `logistic`, `logit`, `linear_classifier`, `classifier`), "
            "`lagged_logistic_regression` (aliases: `lagged_logistic`, `lagged_logit`, `temporal_classifier`), "
            "`lagged_linear` (aliases: `lagged`, `temporal_linear`, `arx`), "
            "`lagged_tree_classifier` (aliases: `temporal_tree_classifier`, `lag_window_tree_classifier`), "
            "`lagged_tree_ensemble` (aliases: `lagged_tree`, `lag_window_tree`, `temporal_tree`), and "
            "`bagged_tree_ensemble` (aliases: `tree`, `tree_ensemble`, `extra_trees`), "
            "`boosted_tree_ensemble` (aliases: `gradient_boosting`, `hist_gradient_boosting`), "
            "`bagged_tree_classifier` (aliases: `tree_classifier`, `classifier_tree`, `fraud_tree`), "
            "and `boosted_tree_classifier` (aliases: `gradient_boosting_classifier`, `hist_gradient_boosting_classifier`)."
        )
        print(f"agent> {response}")
        session_context["workflow_stage"] = "modeler_dataset_ready"
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "model_not_implemented"},
        }

    requested_normalize = bool(build_request.get("normalize", True))
    missing_data_strategy = str(build_request.get("missing_data_strategy", "fill_median")).strip() or "fill_median"
    fill_constant_value = build_request.get("fill_constant_value")
    compare_against_baseline = bool(build_request.get("compare_against_baseline", True))
    lag_horizon_samples = build_request.get("lag_horizon_samples")
    current_lag_horizon = _coerce_optional_int(lag_horizon_samples)
    task_type_hint = str(
        build_request.get("task_type_hint")
        or session_context.get("task_type_override")
        or ""
    ).strip() or None
    threshold_override = build_request.get("threshold_policy")
    if threshold_override in {None, ""}:
        threshold_override = session_context.get("threshold_policy_override")
    threshold_policy, explicit_decision_threshold = _resolve_threshold_training_controls(
        threshold_override
    )
    timestamp_column = str(
        build_request.get("timestamp_column")
        or dataset.get("timestamp_column_hint")
        or ""
    ).strip() or None
    raw_acceptance_criteria = build_request.get("acceptance_criteria")
    acceptance_criteria = _safe_acceptance_criteria(
        raw_acceptance_criteria,
        task_type_hint=task_type_hint,
    )
    loop_policy = _safe_loop_policy(build_request.get("loop_policy"))
    user_locked_model_family = bool(build_request.get("user_locked_model_family", False))
    raw_search_order = [str(item).strip() for item in build_request.get("model_search_order", []) if str(item).strip()]

    print(
        "agent> Training request: "
        f"model=`{resolved_model}`, target=`{target}`, inputs={current_features}."
    )
    if build_request.get("source") == "handoff" and raw_search_order:
        print(
            "agent> Handoff prior: "
            f"search_order={raw_search_order}, normalize={requested_normalize}, "
            f"missing_data={missing_data_strategy}."
        )
    if task_type_hint:
        print(f"agent> Task override: forcing task profile `{task_type_hint}` before training.")
    if timestamp_column:
        print(f"agent> Timestamp context: using `{timestamp_column}` for data-mode-aware splitting.")
    if threshold_policy is not None or explicit_decision_threshold is not None:
        print(
            "agent> Threshold policy: "
            f"{_format_threshold_override(explicit_decision_threshold if explicit_decision_threshold is not None else threshold_policy)}."
        )

    attempt = 1
    max_attempts = int(loop_policy.get("max_attempts", 2))
    allow_loop = bool(loop_policy.get("enabled", True))
    allow_architecture_switch = bool(loop_policy.get("allow_architecture_switch", True))
    allow_feature_set_expansion = bool(loop_policy.get("allow_feature_set_expansion", True))
    allow_lag_horizon_expansion = bool(loop_policy.get("allow_lag_horizon_expansion", True))
    allow_threshold_policy_tuning = bool(loop_policy.get("allow_threshold_policy_tuning", True))
    suggest_more_data_when_stalled = bool(loop_policy.get("suggest_more_data_when_stalled", True))
    current_requested_model = resolved_model
    tried_models: set[str] = set()
    tried_configurations: set[str] = set()
    last_training: dict[str, Any] | None = None
    best_training: dict[str, Any] | None = None
    last_loop_eval: dict[str, Any] | None = None

    while True:
        tried_models.add(current_requested_model)
        tried_configurations.add(
            _training_configuration_signature(
                model_family=current_requested_model,
                feature_columns=current_features,
                lag_horizon_samples=current_lag_horizon,
                threshold_policy=threshold_policy,
                decision_threshold=explicit_decision_threshold,
            )
        )
        print(
            f"agent> Attempt {attempt}/{max_attempts}: requested candidate family `{current_requested_model}`."
        )
        print("agent> Step 1/3: building split-safe train/validation/test partitions.")
        print("agent> Step 2/3: fitting train-only preprocessing (missing-data handling and optional normalization).")
        print(
            "agent> Step 3/3: training the task-appropriate baseline and available comparators, "
            "then selecting the requested/best candidate."
        )
        tool_args = _modeler_training_tool_args(
            dataset=dataset,
            target=target,
            features=current_features,
            requested_model_family=current_requested_model,
            timestamp_column=timestamp_column,
            requested_normalize=requested_normalize,
            missing_data_strategy=missing_data_strategy,
            fill_constant_value=fill_constant_value,
            compare_against_baseline=compare_against_baseline,
            lag_horizon_samples=current_lag_horizon,
            threshold_policy=threshold_policy,
            decision_threshold=explicit_decision_threshold,
            task_type_hint=task_type_hint,
            checkpoint_tag=f"modeler_session_attempt_{attempt}",
        )
        try:
            training = _execute_registry_tool(registry, "train_surrogate_candidates", tool_args)
        except Exception as exc:
            response = str(exc).strip() or _runtime_error_fallback_message(
                agent="modeler",
                user_message=f"train {current_requested_model}",
                error=exc,
            )
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "training_runtime_error"},
            }
        if str(training.get("status", "")).lower() != "ok":
            response = str(training.get("message") or "Model training failed.")
            print(f"agent> {response}")
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "error": "training_failed"},
            }

        last_training = training
        best_training = _select_better_training_result(
            incumbent=best_training,
            candidate=training,
        )
        _print_modeler_training_summary(training=training)
        training_task_profile = (
            training.get("task_profile") if isinstance(training.get("task_profile"), dict) else {}
        )
        effective_task_type = str(
            training_task_profile.get("task_type") or task_type_hint or ""
        ).strip() or None
        acceptance_criteria = _safe_acceptance_criteria(
            raw_acceptance_criteria,
            task_type_hint=effective_task_type,
        )
        metrics_payload = _build_model_loop_metrics(training)
        try:
            loop_eval = _execute_registry_tool(
                registry,
                "evaluate_training_iteration",
                {
                    "metrics": metrics_payload,
                    "acceptance_criteria": acceptance_criteria,
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "task_type_hint": effective_task_type,
                    "data_mode": training.get("data_mode"),
                    "feature_columns": current_features,
                    "target_column": target,
                    "lag_horizon_samples": current_lag_horizon or training.get("lag_horizon_samples"),
                },
            )
        except Exception:
            loop_eval = {
                "should_continue": False,
                "attempt": attempt,
                "max_attempts": max_attempts,
                "unmet_criteria": [],
                "recommendations": [],
                "summary": "Acceptance loop evaluation failed; keeping the current measured result.",
            }
        last_loop_eval = loop_eval if isinstance(loop_eval, dict) else {}
        if last_loop_eval:
            summary_line = str(last_loop_eval.get("summary", "")).strip()
            if summary_line:
                print(f"agent> Acceptance check: {summary_line}")
            unmet = last_loop_eval.get("unmet_criteria")
            if isinstance(unmet, list) and unmet:
                print(f"agent> Unmet criteria: {', '.join(str(item) for item in unmet)}.")
            recommendations = last_loop_eval.get("recommendations")
            if isinstance(recommendations, list):
                for rec in recommendations[:3]:
                    text = str(rec).strip()
                    if text:
                        print(f"agent> Loop recommendation: {text}")

        should_continue = bool((last_loop_eval or {}).get("should_continue", False))
        if not allow_loop:
            should_continue = False
        if user_locked_model_family and current_requested_model != "auto":
            if should_continue and allow_architecture_switch:
                print(
                    "agent> Architecture auto-switch is disabled because this model family was explicitly chosen by the user."
                )
            allow_architecture_switch = False
        if not should_continue:
            _print_stalled_experiment_recommendations(
                loop_evaluation=last_loop_eval,
                enabled=suggest_more_data_when_stalled,
            )
            break

        retry_plan = _choose_model_retry_plan(
            training=training,
            current_model_family=current_requested_model,
            model_search_order=raw_search_order,
            tried_models=tried_models,
            current_feature_columns=current_features,
            available_signals=list(dataset.get("numeric_signal_columns", [])),
            target_signal=target,
            timestamp_column=timestamp_column,
            current_lag_horizon=current_lag_horizon,
            threshold_policy=threshold_policy,
            decision_threshold=explicit_decision_threshold,
            loop_evaluation=last_loop_eval,
            allow_architecture_switch=allow_architecture_switch,
            allow_feature_set_expansion=allow_feature_set_expansion,
            allow_lag_horizon_expansion=allow_lag_horizon_expansion,
            allow_threshold_policy_tuning=allow_threshold_policy_tuning,
            tried_configurations=tried_configurations,
        )
        if retry_plan is None:
            print(
                "agent> No additional safe adaptive retry is available from the current comparison set and search space."
            )
            _print_stalled_experiment_recommendations(
                loop_evaluation=last_loop_eval,
                enabled=suggest_more_data_when_stalled,
            )
            break
        attempt += 1
        if attempt > max_attempts:
            break
        current_requested_model = str(retry_plan.get("model_family", current_requested_model))
        current_features = list(retry_plan.get("feature_columns", current_features))
        current_lag_horizon = _coerce_optional_int(retry_plan.get("lag_horizon_samples"))
        threshold_policy = (
            str(retry_plan["threshold_policy"]).strip()
            if retry_plan.get("threshold_policy") is not None
            else None
        )
        explicit_decision_threshold = (
            float(retry_plan["decision_threshold"])
            if retry_plan.get("decision_threshold") is not None
            else None
        )
        print(
            "agent> Continuing bounded optimization loop with "
            f"`{current_requested_model}` and {_describe_retry_plan(retry_plan)}."
        )

    if last_training is None:
        response = "Model training did not produce a usable result."
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "training_unavailable"},
        }

    training = best_training or last_training
    selected_metrics_bundle = (
        training.get("selected_metrics") if isinstance(training.get("selected_metrics"), dict) else {}
    )
    test_metrics = (
        selected_metrics_bundle.get("test")
        if isinstance(selected_metrics_bundle.get("test"), dict)
        else {}
    )
    comparison = training.get("comparison") if isinstance(training.get("comparison"), list) else []
    final_feature_columns = [
        str(item)
        for item in (training.get("feature_columns") if isinstance(training.get("feature_columns"), list) else current_features)
        if str(item)
    ]
    summary = (
        "Model build complete: "
        f"requested_model={resolved_model}, "
        f"final_attempt_model={current_requested_model}, "
        f"selected_model={training.get('selected_model_family', 'n/a')}, "
        f"best_validation_model={training.get('best_validation_model_family', 'n/a')}, "
        f"target={target}, "
        f"inputs={len(final_feature_columns)}, "
        f"rows_used={training.get('rows_used', 'n/a')}, "
        f"{_format_model_outcome_summary(test_metrics, training.get('task_profile'))}."
    )
    checkpoint_line = f"Checkpoint saved: {training.get('checkpoint_id', 'n/a')}"
    run_dir_line = f"Artifacts: {training.get('run_dir', 'n/a')}"
    print(f"agent> {summary}")
    print(f"agent> {checkpoint_line}")
    print(f"agent> {run_dir_line}")
    inference_suggestions = _build_inference_suggestions(
        checkpoint_id=str(training.get("checkpoint_id", "")).strip(),
        run_dir=str(training.get("run_dir", "")).strip(),
        dataset_path=str(dataset.get("data_path", "")).strip(),
    )
    for line in inference_suggestions.get("lines", []):
        print(f"agent> {line}")
    if chat_reply_only is not None:
        try:
            interpretation = _generate_modeling_interpretation(
                training=training,
                target_signal=target,
                requested_model_family=current_requested_model,
                chat_reply_only=chat_reply_only,
            )
        except Exception:
            interpretation = ""
        if interpretation:
            print("agent> LLM interpretation:")
            for line in interpretation.splitlines():
                text = line.strip()
                if text:
                    print(f"agent> {text}")
        else:
            print(
                "agent> LLM interpretation unavailable for this turn. "
                "Using the deterministic model summary above."
            )
    inference_prompt = (
        "Run inference now with this selected model on data you provide? "
        "Reply `yes` to continue or `no` to skip."
    )
    print(f"agent> {inference_prompt}")
    session_context["workflow_stage"] = "awaiting_inference_decision"
    session_context["last_model_request"] = {
        "target_signal": target,
        "feature_signals": final_feature_columns,
        "requested_model_family": requested_model,
        "final_attempt_model_family": current_requested_model,
        "resolved_model_family": training.get("selected_model_family", current_requested_model),
        "task_profile": training.get("task_profile"),
        "checkpoint_id": training.get("checkpoint_id"),
        "run_dir": training.get("run_dir"),
        "lag_horizon_samples": int(training.get("lag_horizon_samples") or 0),
        "threshold_policy": threshold_policy if threshold_policy is not None else explicit_decision_threshold,
        "acceptance_check": last_loop_eval or {},
        "inference_suggestions": inference_suggestions,
    }
    response = f"{summary} {checkpoint_line} {inference_prompt}"
    return {
        "response": response,
        "event": {
            "status": "respond",
            "message": response,
            "tool_output": {
                "target_signal": target,
                "feature_signals": final_feature_columns,
                "resolved_model_family": training.get("selected_model_family", current_requested_model),
                "checkpoint_id": training.get("checkpoint_id"),
                "run_dir": training.get("run_dir"),
                "metrics": test_metrics,
                "comparison": comparison,
                "task_profile": training.get("task_profile"),
                "acceptance_check": last_loop_eval or {},
                "inference_suggestions": inference_suggestions,
                "workflow_stage": "awaiting_inference_decision",
            },
        },
    }


def _normalize_modeler_model_family(requested_model: str) -> str | None:
    return normalize_candidate_model_family(requested_model)


def _handle_modeler_inference_decision_turn(
    *,
    user_message: str,
    session_context: dict[str, Any],
    chat_reply_only: Callable[[str], str] | None,
) -> dict[str, Any]:
    lowered = user_message.strip().lower()
    if lowered in {"y", "yes", "sure", "ok", "okay", "run"}:
        session_context["workflow_stage"] = "awaiting_inference_data_path"
        response = (
            "Great. Paste a structured dataset path for inference now. "
            "You can also type `same` to reuse the currently loaded dataset, or `skip`."
        )
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "tool_output": {"workflow_stage": "awaiting_inference_data_path"}},
        }
    if lowered in {"n", "no", "skip", "later", "not now"}:
        session_context["workflow_stage"] = "model_training_completed"
        response = "Inference skipped. You can run it later with the proposed `run-inference` command."
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "tool_output": {"workflow_stage": "model_training_completed"}},
        }
    direct_path = _resolve_modeler_inference_data_path(
        user_message=user_message,
        session_context=session_context,
    )
    if direct_path is not None:
        return _run_modeler_inference_now(
            inference_data_path=direct_path,
            session_context=session_context,
        )

    if _looks_like_small_talk(lowered) and chat_reply_only is not None:
        chat = chat_reply_only(user_message).strip()
        reminder = "To continue, reply `yes` to run inference now or `no` to skip."
        response = f"{chat}\n{reminder}" if chat else reminder
        print(f"agent> {chat}" if chat else f"agent> {reminder}")
        if chat:
            print(f"agent> {reminder}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "tool_output": {"workflow_stage": "awaiting_inference_decision"}},
        }
    response = "Please reply `yes` to run inference now, `no` to skip, or paste an inference dataset path."
    print(f"agent> {response}")
    return {
        "response": response,
        "event": {"status": "respond", "message": response, "tool_output": {"workflow_stage": "awaiting_inference_decision"}},
    }


def _handle_modeler_inference_data_path_turn(
    *,
    user_message: str,
    session_context: dict[str, Any],
    chat_reply_only: Callable[[str], str] | None,
) -> dict[str, Any]:
    lowered = user_message.strip().lower()
    if lowered in {"skip", "n", "no", "cancel"}:
        session_context["workflow_stage"] = "model_training_completed"
        response = "Inference skipped. You can run it later with the suggested `run-inference` command."
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "tool_output": {"workflow_stage": "model_training_completed"}},
        }
    direct_path = _resolve_modeler_inference_data_path(
        user_message=user_message,
        session_context=session_context,
    )
    if direct_path is None:
        reminder = (
            "Paste a valid structured dataset path for inference, type `same` to reuse the current dataset, or `skip`."
        )
        if _looks_like_small_talk(lowered) and chat_reply_only is not None:
            chat = chat_reply_only(user_message).strip()
            if chat:
                print(f"agent> {chat}")
                print(f"agent> {reminder}")
                response = f"{chat}\n{reminder}"
            else:
                print(f"agent> {reminder}")
                response = reminder
            return {
                "response": response,
                "event": {"status": "respond", "message": response, "tool_output": {"workflow_stage": "awaiting_inference_data_path"}},
            }
        print(f"agent> {reminder}")
        return {
            "response": reminder,
            "event": {"status": "respond", "message": reminder, "tool_output": {"workflow_stage": "awaiting_inference_data_path"}},
        }
    return _run_modeler_inference_now(
        inference_data_path=direct_path,
        session_context=session_context,
    )


def _resolve_modeler_inference_data_path(
    *,
    user_message: str,
    session_context: dict[str, Any],
) -> Path | None:
    text = user_message.strip()
    lowered = text.lower()
    if lowered == "same":
        dataset = _modeler_loaded_dataset(session_context)
        if dataset and str(dataset.get("data_path", "")).strip():
            return Path(str(dataset["data_path"])).expanduser()
        return None
    if lowered == "default":
        return _resolve_default_public_dataset_path()

    detected = _extract_first_data_path(user_message)
    if detected is not None:
        return detected

    stripped = text.strip().strip("\"'")
    if not stripped:
        return None
    direct = Path(stripped).expanduser()
    return direct if direct.exists() else None


def _run_modeler_inference_now(
    *,
    inference_data_path: Path,
    session_context: dict[str, Any],
) -> dict[str, Any]:
    last_request = (
        session_context.get("last_model_request")
        if isinstance(session_context.get("last_model_request"), dict)
        else {}
    )
    checkpoint_id = str(last_request.get("checkpoint_id", "")).strip()
    run_dir = str(last_request.get("run_dir", "")).strip()
    if not checkpoint_id and not run_dir:
        response = "No saved model reference is available for inference. Train a model first."
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "inference_reference_missing"},
        }

    if not inference_data_path.exists():
        response = f"Inference data path does not exist: {_path_for_display(inference_data_path)}"
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "inference_data_missing"},
        }

    print(f"agent> Running inference on: {_path_for_display(inference_data_path)}")
    try:
        payload = run_inference_from_artifacts(
            data_path=str(inference_data_path),
            checkpoint_id=checkpoint_id or None,
            run_dir=run_dir or None,
        )
    except Exception as exc:
        response = (
            "Inference failed: "
            f"{str(exc).strip() or 'unknown runtime error'}"
        )
        print(f"agent> {response}")
        return {
            "response": response,
            "event": {"status": "respond", "message": response, "error": "inference_runtime_error"},
        }

    metrics = (
        payload.get("evaluation", {}).get("metrics")
        if isinstance(payload.get("evaluation"), dict)
        else {}
    )
    summary = (
        "Inference complete: "
        f"rows_scored={payload.get('prediction_count', 'n/a')}, "
        f"dropped_rows={payload.get('dropped_rows_missing_features', 'n/a')}."
    )
    report_line = f"Inference report: {payload.get('report_path', 'n/a')}"
    preds_line = f"Predictions: {payload.get('predictions_path', 'n/a')}"
    print(f"agent> {summary}")
    print(f"agent> {report_line}")
    print(f"agent> {preds_line}")
    if isinstance(metrics, dict) and metrics:
        metric_keys = ("r2", "mae", "f1", "accuracy", "recall", "pr_auc")
        metric_parts = [
            f"{key}={_fmt_metric(metrics.get(key))}"
            for key in metric_keys
            if key in metrics
        ]
        if metric_parts:
            print("agent> Inference eval: " + ", ".join(metric_parts) + ".")
    recommendations = payload.get("recommendations")
    if isinstance(recommendations, list):
        for item in recommendations[:2]:
            text = str(item).strip()
            if text:
                print(f"agent> Inference suggestion: {text}")

    session_context["last_inference_result"] = payload
    session_context["workflow_stage"] = "model_training_completed"
    response = f"{summary} {report_line}"
    return {
        "response": response,
        "event": {
            "status": "respond",
            "message": response,
            "tool_output": {
                "workflow_stage": "model_training_completed",
                "inference_report_path": payload.get("report_path"),
                "predictions_path": payload.get("predictions_path"),
                "inference_metrics": metrics,
            },
        },
    }


def _fmt_metric(value: Any) -> str:
    parsed = _float_value_or_none(value)
    if parsed is None:
        return "n/a"
    return f"{parsed:.4f}"


def _print_task_profile_summary(raw_task_profiles: Any, *, context_label: str) -> None:
    if not isinstance(raw_task_profiles, list):
        return
    printed = 0
    for item in raw_task_profiles:
        if not isinstance(item, dict):
            continue
        target_signal = str(item.get("target_signal", "")).strip() or "unknown"
        task_type = str(item.get("task_type", "")).strip() or "n/a"
        split_strategy = str(item.get("recommended_split_strategy", "")).strip() or "n/a"
        rationale = str(item.get("rationale", "")).strip()
        line = (
            f"agent> Detected task profile ({context_label}): "
            f"target=`{target_signal}`, task_type=`{task_type}`, recommended_split=`{split_strategy}`."
        )
        print(line)
        if rationale:
            print(f"agent> Task rationale: {rationale}")
        printed += 1
        if printed >= 3:
            break


def _modeler_training_tool_args(
    *,
    dataset: dict[str, Any],
    target: str,
    features: list[str],
    requested_model_family: str,
    timestamp_column: str | None,
    requested_normalize: bool,
    missing_data_strategy: str,
    fill_constant_value: Any,
    compare_against_baseline: bool,
    lag_horizon_samples: Any,
    threshold_policy: Any,
    decision_threshold: Any,
    task_type_hint: str | None,
    checkpoint_tag: str,
) -> dict[str, Any]:
    return {
        "data_path": str(dataset.get("data_path", "")),
        "target_column": target,
        "feature_columns": features,
        "requested_model_family": requested_model_family,
        "sheet_name": dataset.get("sheet_name"),
        "timestamp_column": timestamp_column,
        "checkpoint_tag": checkpoint_tag,
        "normalize": requested_normalize,
        "missing_data_strategy": missing_data_strategy,
        "fill_constant_value": fill_constant_value,
        "compare_against_baseline": compare_against_baseline,
        "lag_horizon_samples": lag_horizon_samples,
        "threshold_policy": threshold_policy,
        "decision_threshold": decision_threshold,
        "task_type_hint": task_type_hint,
    }


def _print_modeler_training_summary(*, training: dict[str, Any]) -> None:
    split_info = training.get("split") if isinstance(training.get("split"), dict) else {}
    preprocessing = training.get("preprocessing") if isinstance(training.get("preprocessing"), dict) else {}
    comparison = training.get("comparison") if isinstance(training.get("comparison"), list) else []
    professional_analysis = (
        training.get("professional_analysis")
        if isinstance(training.get("professional_analysis"), dict)
        else {}
    )
    task_profile = training.get("task_profile") if isinstance(training.get("task_profile"), dict) else {}
    hyperparameters = (
        training.get("selected_hyperparameters")
        if isinstance(training.get("selected_hyperparameters"), dict)
        else {}
    )
    if task_profile:
        minority = _safe_float_or_none(task_profile.get("minority_class_fraction"))
        task_line = (
            "agent> Task profile: "
            f"type={task_profile.get('task_type', 'n/a')}, "
            f"family={task_profile.get('task_family', 'n/a')}, "
            f"recommended_split={task_profile.get('recommended_split_strategy', 'n/a')}"
        )
        if minority is not None:
            task_line += f", minority_fraction={minority:.3%}"
        task_line += "."
        print(task_line)
        if _task_is_classification(str(task_profile.get("task_type", "")).strip()):
            print(
                "agent> Binary classification thresholding is validation-tuned by default. "
                "Use `threshold ...` before the next run if you want to favor recall, precision, F1, PR-AUC, or set an explicit cutoff."
            )
    print(
        "agent> Split-safe pipeline: "
        f"strategy={split_info.get('strategy', 'n/a')}, "
        f"train={split_info.get('train_size', 'n/a')}, "
        f"val={split_info.get('validation_size', 'n/a')}, "
        f"test={split_info.get('test_size', 'n/a')}."
    )
    print(
        "agent> Preprocessing policy: "
        f"requested={preprocessing.get('missing_data_strategy_requested', 'n/a')}, "
        f"effective={preprocessing.get('missing_data_strategy_effective', 'n/a')}, "
        f"normalization={((training.get('normalization') or {}).get('method', 'none'))}."
    )
    if int(training.get("lag_horizon_samples") or 0) > 0:
        print(
            "agent> Temporal feature plan: "
            f"lag_horizon_samples={int(training.get('lag_horizon_samples') or 0)}."
        )
    if hyperparameters:
        print(
            "agent> Selected hyperparameters: "
            f"{dumps_json(hyperparameters, ensure_ascii=False)}."
        )
    for item in comparison:
        if not isinstance(item, dict):
            continue
        val_metrics = item.get("validation_metrics") if isinstance(item.get("validation_metrics"), dict) else {}
        test_metrics = item.get("test_metrics") if isinstance(item.get("test_metrics"), dict) else {}
        print(
            "agent> Candidate "
            f"`{item.get('model_family', 'n/a')}`: "
            f"{_format_candidate_metric_summary(val_metrics, test_metrics)}."
        )
    if professional_analysis:
        summary = str(professional_analysis.get("summary", "")).strip()
        if summary:
            print(f"agent> Professional analysis: {summary}")
        diagnostics = professional_analysis.get("diagnostics")
        if isinstance(diagnostics, list):
            for item in diagnostics[:3]:
                text = str(item).strip()
                if text:
                    print(f"agent> Diagnostic: {text}")
        risk_flags = professional_analysis.get("risk_flags")
        if isinstance(risk_flags, list) and risk_flags:
            print(
                "agent> Risk flags: "
                + ", ".join(str(item).strip() for item in risk_flags if str(item).strip())
                + "."
            )
        suggestions = professional_analysis.get("suggestions")
        if isinstance(suggestions, list):
            for item in suggestions[:3]:
                text = str(item).strip()
                if text:
                    print(f"agent> Suggestion: {text}")


def _build_inference_suggestions(
    *,
    checkpoint_id: str,
    run_dir: str,
    dataset_path: str,
) -> dict[str, Any]:
    lines: list[str] = []
    if not checkpoint_id and not run_dir:
        return {"lines": lines}

    lines.append(
        "Next step: run inference with the selected model on new data you provide."
    )
    if checkpoint_id:
        lines.append(
            "Inference command (checkpoint): "
            f"`relaytic run-inference --checkpoint-id {checkpoint_id} --data-path <new_data.csv>`"
        )
    if run_dir:
        lines.append(
            "Inference command (run dir): "
            f"`relaytic run-inference --run-dir \"{run_dir}\" --data-path <new_data.csv>`"
        )
    if checkpoint_id and dataset_path:
        try:
            dataset_display = _path_for_display(Path(dataset_path))
        except Exception:
            dataset_display = dataset_path
        lines.append(
            "Quick smoke test on current dataset: "
            f"`relaytic run-inference --checkpoint-id {checkpoint_id} --data-path \"{dataset_display}\"`"
        )
    return {
        "checkpoint_id": checkpoint_id,
        "run_dir": run_dir,
        "dataset_path": dataset_path,
        "lines": lines,
    }


def _default_acceptance_criteria(*, task_type_hint: str | None = None) -> dict[str, float]:
    normalized = normalize_task_type_hint(task_type_hint) or str(task_type_hint or "").strip()
    if normalized in {"fraud_detection", "anomaly_detection"}:
        return {"recall": 0.70, "pr_auc": 0.35}
    if normalized in {"binary_classification", "multiclass_classification"}:
        return {"f1": 0.75, "accuracy": 0.75}
    return {"r2": 0.70}


def _task_is_classification(task_type_hint: str | None) -> bool:
    normalized = normalize_task_type_hint(task_type_hint) or str(task_type_hint or "").strip()
    return normalized in {
        "binary_classification",
        "multiclass_classification",
        "fraud_detection",
        "anomaly_detection",
    }


def _format_model_outcome_summary(test_metrics: dict[str, Any], task_profile: Any) -> str:
    task_type = ""
    if isinstance(task_profile, dict):
        task_type = str(task_profile.get("task_type", "")).strip()
    if _task_is_classification(task_type):
        parts = [
            f"test_f1={_fmt_metric(test_metrics.get('f1'))}",
            f"test_accuracy={_fmt_metric(test_metrics.get('accuracy'))}",
            f"test_precision={_fmt_metric(test_metrics.get('precision'))}",
            f"test_recall={_fmt_metric(test_metrics.get('recall'))}",
        ]
        if "pr_auc" in test_metrics:
            parts.append(f"test_pr_auc={_fmt_metric(test_metrics.get('pr_auc'))}")
        elif "log_loss" in test_metrics:
            parts.append(f"test_log_loss={_fmt_metric(test_metrics.get('log_loss'))}")
        if "roc_auc" in test_metrics:
            parts.append(f"test_roc_auc={_fmt_metric(test_metrics.get('roc_auc'))}")
        return ", ".join(parts)
    return (
        f"test_r2={_fmt_metric(test_metrics.get('r2'))}, "
        f"test_mae={_fmt_metric(test_metrics.get('mae'))}"
    )


def _format_candidate_metric_summary(
    validation_metrics: dict[str, Any],
    test_metrics: dict[str, Any],
) -> str:
    classification_like = any(
        key in validation_metrics or key in test_metrics
        for key in ("accuracy", "precision", "recall", "f1", "pr_auc", "roc_auc", "log_loss")
    )
    if classification_like:
        parts = [
            f"val_f1={_fmt_metric(validation_metrics.get('f1'))}",
            f"val_accuracy={_fmt_metric(validation_metrics.get('accuracy'))}",
            f"test_f1={_fmt_metric(test_metrics.get('f1'))}",
            f"test_accuracy={_fmt_metric(test_metrics.get('accuracy'))}",
        ]
        if "pr_auc" in validation_metrics or "pr_auc" in test_metrics:
            parts.append(f"val_pr_auc={_fmt_metric(validation_metrics.get('pr_auc'))}")
            parts.append(f"test_pr_auc={_fmt_metric(test_metrics.get('pr_auc'))}")
        elif "log_loss" in validation_metrics or "log_loss" in test_metrics:
            parts.append(f"val_log_loss={_fmt_metric(validation_metrics.get('log_loss'))}")
            parts.append(f"test_log_loss={_fmt_metric(test_metrics.get('log_loss'))}")
        if "recall" in validation_metrics or "recall" in test_metrics:
            parts.append(f"val_recall={_fmt_metric(validation_metrics.get('recall'))}")
            parts.append(f"test_recall={_fmt_metric(test_metrics.get('recall'))}")
        return ", ".join(parts)
    return (
        f"val_r2={_fmt_metric(validation_metrics.get('r2'))}, "
        f"val_mae={_fmt_metric(validation_metrics.get('mae'))}, "
        f"test_r2={_fmt_metric(test_metrics.get('r2'))}, "
        f"test_mae={_fmt_metric(test_metrics.get('mae'))}"
    )


def _select_better_training_result(
    *,
    incumbent: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if incumbent is None:
        return candidate
    incumbent_rank = _training_result_rank(incumbent)
    candidate_rank = _training_result_rank(candidate)
    return candidate if candidate_rank < incumbent_rank else incumbent


def _training_result_rank(training: dict[str, Any]) -> tuple[float, ...]:
    task_profile = training.get("task_profile") if isinstance(training.get("task_profile"), dict) else {}
    task_type = str(task_profile.get("task_type", "")).strip()
    selected = training.get("selected_metrics") if isinstance(training.get("selected_metrics"), dict) else {}
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    if not validation:
        validation = selected.get("test") if isinstance(selected.get("test"), dict) else {}
    if _task_is_classification(task_type):
        if task_type in {"fraud_detection", "anomaly_detection"}:
            return (
                -float(validation.get("pr_auc", 0.0)),
                -float(validation.get("recall", 0.0)),
                -float(validation.get("f1", 0.0)),
                float(validation.get("log_loss", float("inf"))),
            )
        return (
            -float(validation.get("f1", 0.0)),
            -float(validation.get("accuracy", 0.0)),
            -float(validation.get("precision", 0.0)),
            -float(validation.get("recall", 0.0)),
            float(validation.get("log_loss", float("inf"))),
        )
    return (
        -float(validation.get("r2", float("-inf"))),
        float(validation.get("mae", float("inf"))),
        float(validation.get("rmse", float("inf"))),
    )


def _normalize_threshold_override(raw: str) -> str | float | None:
    text = str(raw).strip()
    if not text:
        return None
    lowered = text.lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "auto": "auto",
        "favor_recall": "favor_recall",
        "favor_precision": "favor_precision",
        "favor_f1": "favor_f1",
        "favor_pr_auc": "favor_pr_auc",
        "favor_prauc": "favor_pr_auc",
    }
    if lowered in aliases:
        return aliases[lowered]
    try:
        numeric = float(text)
    except (TypeError, ValueError):
        return None
    if 0.0 < numeric < 1.0:
        return float(numeric)
    return None


def _format_threshold_override(value: str | float | None) -> str:
    if value is None:
        return "auto"
    if isinstance(value, (int, float)):
        return f"explicit threshold {float(value):.2f}"
    return str(value)


def _resolve_threshold_training_controls(
    raw: Any,
) -> tuple[str | None, float | None]:
    if raw is None:
        return None, None
    if isinstance(raw, (int, float)):
        numeric = float(raw)
        if 0.0 < numeric < 1.0:
            return None, numeric
        return None, None
    normalized = _normalize_threshold_override(str(raw))
    if isinstance(normalized, float):
        return None, normalized
    if normalized == "auto":
        return None, None
    if isinstance(normalized, str):
        return normalized, None
    return None, None


def _coerce_optional_int(raw: Any) -> int | None:
    if raw is None:
        return None
    try:
        parsed = int(raw)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _training_configuration_signature(
    *,
    model_family: str,
    feature_columns: list[str],
    lag_horizon_samples: int | None,
    threshold_policy: str | None,
    decision_threshold: float | None,
) -> str:
    feature_key = ",".join(sorted(str(item) for item in feature_columns))
    threshold_key = (
        f"threshold={float(decision_threshold):.4f}"
        if decision_threshold is not None
        else f"policy={str(threshold_policy or 'auto')}"
    )
    return (
        f"{model_family}|features={feature_key}|lag={int(lag_horizon_samples or 0)}|{threshold_key}"
    )


def _choose_model_retry_plan(
    *,
    training: dict[str, Any],
    current_model_family: str,
    model_search_order: list[str],
    tried_models: set[str],
    current_feature_columns: list[str],
    available_signals: list[str],
    target_signal: str,
    timestamp_column: str | None,
    current_lag_horizon: int | None,
    threshold_policy: str | None,
    decision_threshold: float | None,
    loop_evaluation: dict[str, Any],
    allow_architecture_switch: bool,
    allow_feature_set_expansion: bool,
    allow_lag_horizon_expansion: bool,
    allow_threshold_policy_tuning: bool,
    tried_configurations: set[str],
) -> dict[str, Any] | None:
    unmet = [
        str(item).strip().lower()
        for item in (loop_evaluation.get("unmet_criteria") if isinstance(loop_evaluation, dict) else [])
        if str(item).strip()
    ]
    task_profile = training.get("task_profile") if isinstance(training.get("task_profile"), dict) else {}
    task_type = str(task_profile.get("task_type", "")).strip()
    normalized_current = _normalize_modeler_model_family(current_model_family) or current_model_family

    def _candidate_plan(
        *,
        model_family: str | None = None,
        feature_columns: list[str] | None = None,
        lag_horizon_samples: int | None = None,
        threshold_policy_value: str | None = threshold_policy,
        decision_threshold_value: float | None = decision_threshold,
        note: str,
    ) -> dict[str, Any] | None:
        plan = {
            "model_family": model_family or normalized_current,
            "feature_columns": list(feature_columns or current_feature_columns),
            "lag_horizon_samples": lag_horizon_samples,
            "threshold_policy": threshold_policy_value,
            "decision_threshold": decision_threshold_value,
            "note": note,
        }
        signature = _training_configuration_signature(
            model_family=str(plan["model_family"]),
            feature_columns=list(plan["feature_columns"]),
            lag_horizon_samples=_coerce_optional_int(plan["lag_horizon_samples"]),
            threshold_policy=(
                str(plan["threshold_policy"]).strip()
                if plan["threshold_policy"] is not None
                else None
            ),
            decision_threshold=(
                float(plan["decision_threshold"])
                if plan["decision_threshold"] is not None
                else None
            ),
        )
        if signature in tried_configurations:
            return None
        return plan

    if _task_is_classification(task_type) and allow_threshold_policy_tuning:
        if "recall" in unmet and threshold_policy != "favor_recall":
            plan = _candidate_plan(
                threshold_policy_value="favor_recall",
                decision_threshold_value=None,
                note="raising minority-class sensitivity via `favor_recall` threshold policy",
            )
            if plan is not None:
                return plan
        if "precision" in unmet and threshold_policy != "favor_precision":
            plan = _candidate_plan(
                threshold_policy_value="favor_precision",
                decision_threshold_value=None,
                note="tightening positive decisions via `favor_precision` threshold policy",
            )
            if plan is not None:
                return plan
        if "f1" in unmet and threshold_policy != "favor_f1":
            plan = _candidate_plan(
                threshold_policy_value="favor_f1",
                decision_threshold_value=None,
                note="retuning the binary decision threshold for F1 balance",
            )
            if plan is not None:
                return plan
        if "pr_auc" in unmet and threshold_policy != "favor_pr_auc":
            plan = _candidate_plan(
                threshold_policy_value="favor_pr_auc",
                decision_threshold_value=None,
                note="retuning the binary decision threshold to favor precision-recall separation",
            )
            if plan is not None:
                return plan

    if allow_architecture_switch:
        next_model = _choose_model_retry_candidate(
            training=training,
            current_model_family=current_model_family,
            model_search_order=model_search_order,
            tried_models=tried_models,
        )
        if next_model is not None:
            plan = _candidate_plan(
                model_family=next_model,
                note=f"switching candidate family to `{next_model}`",
            )
            if plan is not None:
                return plan

    if allow_feature_set_expansion:
        extras = [
            str(item)
            for item in available_signals
            if (
                str(item)
                and str(item) != target_signal
                and str(item) not in current_feature_columns
                and str(item) != str(timestamp_column or "").strip()
            )
        ]
        if extras:
            addition = extras[: min(2, len(extras))]
            expanded_features = list(current_feature_columns) + addition
            plan = _candidate_plan(
                feature_columns=expanded_features,
                note=f"expanding the feature set with {addition}",
            )
            if plan is not None:
                return plan

    if allow_lag_horizon_expansion:
        data_mode = str(training.get("data_mode", "")).strip()
        target_model = normalized_current
        if data_mode == "time_series" and target_model in {
            "auto",
            "lagged_linear",
            "lagged_logistic_regression",
            "lagged_tree_ensemble",
            "lagged_tree_classifier",
        }:
            current_lag = int(current_lag_horizon or training.get("lag_horizon_samples") or 0)
            next_lag = current_lag + 1 if current_lag > 0 else 2
            if next_lag <= 12:
                if target_model in {"lagged_linear", "lagged_logistic_regression", "lagged_tree_ensemble", "lagged_tree_classifier"}:
                    lagged_model = target_model
                elif _task_is_classification(task_type):
                    lagged_model = "lagged_logistic_regression"
                else:
                    lagged_model = "lagged_linear"
                plan = _candidate_plan(
                    model_family=lagged_model,
                    lag_horizon_samples=next_lag,
                    note=f"widening the lag window to {next_lag} samples",
                )
                if plan is not None:
                    return plan

    return None


def _describe_retry_plan(plan: dict[str, Any]) -> str:
    note = str(plan.get("note", "")).strip()
    feature_columns = [str(item) for item in (plan.get("feature_columns") or []) if str(item)]
    extras = []
    if feature_columns:
        extras.append(f"inputs={feature_columns}")
    lag_value = _coerce_optional_int(plan.get("lag_horizon_samples"))
    if lag_value is not None:
        extras.append(f"lag_horizon={lag_value}")
    threshold_display = None
    if plan.get("decision_threshold") is not None:
        threshold_display = _format_threshold_override(float(plan["decision_threshold"]))
    elif plan.get("threshold_policy") is not None:
        threshold_display = _format_threshold_override(str(plan["threshold_policy"]))
    if threshold_display is not None:
        extras.append(f"threshold={threshold_display}")
    if note and extras:
        return f"{note} ({', '.join(extras)})"
    if note:
        return note
    if extras:
        return ", ".join(extras)
    return "the next safe retry plan"


def _print_stalled_experiment_recommendations(
    *,
    loop_evaluation: dict[str, Any],
    enabled: bool,
) -> None:
    if not enabled or not isinstance(loop_evaluation, dict):
        return
    suggestions = loop_evaluation.get("trajectory_recommendations")
    if not isinstance(suggestions, list):
        return
    printed = 0
    for item in suggestions:
        text = str(item).strip()
        if not text:
            continue
        print(f"agent> Experiment recommendation: {text}")
        printed += 1
        if printed >= 3:
            break


def _safe_acceptance_criteria(raw: Any, *, task_type_hint: str | None = None) -> dict[str, float]:
    default = _default_acceptance_criteria(task_type_hint=task_type_hint)
    if not isinstance(raw, dict):
        return default
    criteria: dict[str, float] = {}
    for key, value in raw.items():
        name = str(key).strip()
        if not name:
            continue
        try:
            criteria[name] = float(value)
        except (TypeError, ValueError):
            continue
    if not criteria:
        return default
    if _task_is_classification(task_type_hint) and not any(
        key in criteria for key in ("accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc")
    ):
        return default
    return criteria


def _safe_loop_policy(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {
            "enabled": True,
            "max_attempts": 3,
            "allow_architecture_switch": True,
            "allow_feature_set_expansion": True,
            "allow_lag_horizon_expansion": True,
            "allow_threshold_policy_tuning": True,
            "suggest_more_data_when_stalled": True,
        }
    enabled = bool(raw.get("enabled", True))
    try:
        max_attempts = max(1, int(raw.get("max_attempts", 3)))
    except (TypeError, ValueError):
        max_attempts = 3
    allow_architecture_switch = bool(raw.get("allow_architecture_switch", True))
    allow_feature_set_expansion = bool(raw.get("allow_feature_set_expansion", True))
    allow_lag_horizon_expansion = bool(raw.get("allow_lag_horizon_expansion", True))
    allow_threshold_policy_tuning = bool(raw.get("allow_threshold_policy_tuning", True))
    suggest_more_data_when_stalled = bool(raw.get("suggest_more_data_when_stalled", True))
    return {
        "enabled": enabled,
        "max_attempts": max_attempts,
        "allow_architecture_switch": allow_architecture_switch,
        "allow_feature_set_expansion": allow_feature_set_expansion,
        "allow_lag_horizon_expansion": allow_lag_horizon_expansion,
        "allow_threshold_policy_tuning": allow_threshold_policy_tuning,
        "suggest_more_data_when_stalled": suggest_more_data_when_stalled,
    }


def _build_model_loop_metrics(training: dict[str, Any]) -> dict[str, float]:
    selected = training.get("selected_metrics") if isinstance(training.get("selected_metrics"), dict) else {}
    train_metrics = selected.get("train") if isinstance(selected.get("train"), dict) else {}
    val_metrics = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    test_metrics = selected.get("test") if isinstance(selected.get("test"), dict) else {}
    metrics: dict[str, float] = {}
    for key, value in test_metrics.items():
        try:
            metrics[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    for source, prefix in ((train_metrics, "train_"), (val_metrics, "val_")):
        for key, value in source.items():
            try:
                metrics[f"{prefix}{key}"] = float(value)
            except (TypeError, ValueError):
                continue
    try:
        metrics["n_samples"] = float(training.get("rows_used", 0))
    except (TypeError, ValueError):
        metrics["n_samples"] = 0.0
    return metrics


def _choose_model_retry_candidate(
    *,
    training: dict[str, Any],
    current_model_family: str,
    model_search_order: list[str],
    tried_models: set[str],
) -> str | None:
    normalized_order: list[str] = []
    for item in model_search_order:
        normalized = _normalize_modeler_model_family(str(item))
        if normalized is not None and normalized not in normalized_order:
            normalized_order.append(normalized)
    best_validation = _normalize_modeler_model_family(
        str(training.get("best_validation_model_family", "")).strip()
    )
    if best_validation is not None and best_validation not in normalized_order:
        normalized_order.append(best_validation)
    comparison = training.get("comparison") if isinstance(training.get("comparison"), list) else []
    for item in comparison:
        if not isinstance(item, dict):
            continue
        candidate = _normalize_modeler_model_family(str(item.get("model_family", "")).strip())
        if candidate is not None and candidate not in normalized_order:
            normalized_order.append(candidate)

    current_normalized = _normalize_modeler_model_family(current_model_family) or current_model_family
    for candidate in normalized_order:
        if candidate == current_normalized:
            continue
        if candidate in tried_models:
            continue
        return candidate
    return None


def _extract_first_json_path(user_message: str) -> Path | None:
    quoted = re.findall(r"[\"']([^\"']+\.json)[\"']", user_message, flags=re.IGNORECASE)
    candidates: list[str] = list(quoted)
    absolute_windows = re.findall(
        r"([A-Za-z]:\\[^\n]+?\.json)",
        user_message,
        flags=re.IGNORECASE,
    )
    candidates.extend(absolute_windows)
    plain = re.findall(r"([^\s\"']+\.json)", user_message, flags=re.IGNORECASE)
    candidates.extend(plain)
    for raw in candidates:
        cleaned = raw.strip().rstrip(".,;:)")
        if not cleaned:
            continue
        path = Path(cleaned).expanduser()
        if path.exists():
            return path
    for raw in candidates:
        cleaned = raw.strip().rstrip(".,;:)")
        if cleaned:
            return Path(cleaned).expanduser()
    return None


def _load_modeler_handoff_payload(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"error": f"Handoff file does not exist: {path}"}
    except json.JSONDecodeError as exc:
        return {"error": f"Handoff file is not valid JSON: {exc}"}
    if not isinstance(payload, dict):
        return {"error": "Handoff JSON must be an object."}
    handoff = build_agent2_handoff_from_report_payload(payload)
    if handoff is None:
        return {
            "error": (
                "I could not derive a valid Agent 2 handoff from that report. "
                "Ensure it is an Agent 1 structured report with target and predictor recommendations."
            )
        }
    dataset_profile = handoff.dataset_profile if isinstance(handoff.dataset_profile, dict) else {}
    return {
        "payload": payload,
        "handoff": handoff.to_dict(),
        "data_path": dataset_profile.get("data_path", "") or payload.get("data_path", ""),
    }


def _modeler_request_from_handoff(
    *,
    payload: dict[str, Any],
    handoff: dict[str, Any],
    available_signals: list[str],
) -> dict[str, Any] | None:
    target_raw = str(handoff.get("target_signal", "")).strip()
    if not target_raw:
        return None

    feature_raw = [
        str(item).strip()
        for item in handoff.get("feature_signals", [])
        if str(item).strip()
    ]
    if not feature_raw and available_signals:
        fallback = [name for name in available_signals if name != target_raw]
        feature_raw = fallback[: min(3, len(fallback))]

    if not feature_raw:
        return None

    preprocessing = payload.get("preprocessing") if isinstance(payload.get("preprocessing"), dict) else {}
    missing_plan = (
        preprocessing.get("missing_data_plan")
        if isinstance(preprocessing.get("missing_data_plan"), dict)
        else {}
    )
    return {
        "requested_model_family": str(handoff.get("recommended_model_family", "linear_ridge")).strip() or "linear_ridge",
        "feature_raw": feature_raw,
        "target_raw": target_raw,
        "data_path": str(payload.get("data_path", "")).strip(),
        "timestamp_column": str(handoff.get("dataset_profile", {}).get("timestamp_column", "")).strip() or None,
        "task_type_hint": str(handoff.get("task_type", "")).strip() or None,
        "normalize": bool(handoff.get("normalization", {}).get("enabled", True)),
        "missing_data_strategy": str(missing_plan.get("strategy", "keep")).strip() or "keep",
        "fill_constant_value": missing_plan.get("fill_constant_value"),
        "compare_against_baseline": True,
        "lag_horizon_samples": int(handoff.get("lag_horizon_samples", 0) or 0) or None,
        "acceptance_criteria": (
            dict(handoff.get("acceptance_criteria"))
            if isinstance(handoff.get("acceptance_criteria"), dict)
            else _default_acceptance_criteria(
                task_type_hint=str(handoff.get("task_type", "")).strip() or None
            )
        ),
        "loop_policy": (
            dict(handoff.get("loop_policy"))
            if isinstance(handoff.get("loop_policy"), dict)
            else {
                "enabled": True,
                "max_attempts": 3,
                "allow_architecture_switch": True,
                "allow_feature_set_expansion": True,
                "allow_lag_horizon_expansion": True,
                "allow_threshold_policy_tuning": True,
                "suggest_more_data_when_stalled": True,
            }
        ),
        "user_locked_model_family": False,
        "model_search_order": [
            str(item).strip()
            for item in handoff.get("model_search_order", [])
            if str(item).strip()
        ],
        "source": "handoff",
    }


def _prompt_modeler_overrides(
    *,
    request: dict[str, Any],
    available_signals: list[str],
) -> dict[str, Any]:
    target_raw = _prompt_modeler_target_override(
        default_target=str(request.get("target_raw", "")).strip(),
        available_signals=available_signals,
    )
    feature_raw = _prompt_modeler_feature_override(
        default_features=[str(item) for item in request.get("feature_raw", [])],
        target_signal=target_raw,
        available_signals=available_signals,
    )
    requested_model_family, user_locked_model_family = _prompt_modeler_model_override(
        default_model=str(request.get("requested_model_family", "linear_ridge")).strip(),
    )
    return {
        **request,
        "target_raw": target_raw,
        "feature_raw": feature_raw,
        "requested_model_family": requested_model_family,
        "user_locked_model_family": user_locked_model_family,
    }


def _prompt_modeler_target_override(
    *,
    default_target: str,
    available_signals: list[str],
) -> str:
    while True:
        print(
            "agent> Press Enter to use the recommended target "
            f"`{default_target}`, type `list` to show signals, or enter a target name/index."
        )
        answer = input("you> ").strip()
        lowered = answer.lower()
        if not answer:
            return default_target
        if lowered.startswith("list"):
            _print_signal_names(available_signals, query=answer[4:].strip())
            continue
        resolved = _resolve_signal_name(answer, available_signals)
        if resolved is not None:
            return resolved
        print("agent> I did not resolve that target. Type `list` to inspect signal names.")


def _prompt_modeler_feature_override(
    *,
    default_features: list[str],
    target_signal: str,
    available_signals: list[str],
) -> list[str]:
    default_display = ",".join(default_features)
    while True:
        print(
            "agent> Press Enter to use the recommended inputs "
            f"`{default_display}`, type `list` to show signals, or enter comma-separated inputs."
        )
        answer = input("you> ").strip()
        lowered = answer.lower()
        if not answer:
            return [item for item in default_features if item != target_signal]
        if lowered.startswith("list"):
            _print_signal_names(available_signals, query=answer[4:].strip())
            continue
        requested = _split_modeler_input_tokens(answer)
        resolved: list[str] = []
        unknown: list[str] = []
        seen: set[str] = set()
        for raw in requested:
            match = _resolve_signal_name(raw, available_signals)
            if match is None:
                unknown.append(raw)
                continue
            if match == target_signal or match in seen:
                continue
            resolved.append(match)
            seen.add(match)
        if unknown:
            print(f"agent> Ignoring unknown inputs: {unknown}")
        if resolved:
            return resolved
        print("agent> I did not resolve any usable inputs. Type `list` to inspect signal names.")


def _prompt_modeler_model_override(*, default_model: str) -> tuple[str, bool]:
    available = (
        "auto, linear_ridge (aliases: ridge, linear, incremental_linear_surrogate), "
        "logistic_regression (aliases: logistic, logit, linear_classifier, classifier), "
        "lagged_logistic_regression (aliases: lagged_logistic, lagged_logit, temporal_classifier), "
        "lagged_linear (aliases: lagged, temporal_linear, arx), "
        "lagged_tree_classifier (aliases: temporal_tree_classifier, lag_window_tree_classifier), "
        "lagged_tree_ensemble (aliases: lagged_tree, lag_window_tree, temporal_tree), "
        "bagged_tree_ensemble (aliases: tree, tree_ensemble, extra_trees), "
        "boosted_tree_ensemble (aliases: gradient_boosting, hist_gradient_boosting), "
        "bagged_tree_classifier (aliases: tree_classifier, classifier_tree, fraud_tree), "
        "boosted_tree_classifier (aliases: gradient_boosting_classifier, hist_gradient_boosting_classifier)"
    )
    recommended_supported = _normalize_modeler_model_family(default_model)
    while True:
        default_text = default_model or "linear_ridge"
        if recommended_supported is None:
            print(
                "agent> The recommended model "
                f"`{default_text}` is not implemented yet. "
                "Press Enter to use `auto`, or type an available model."
            )
        else:
            print(
                "agent> Press Enter to use the recommended model "
                f"`{default_text}`, or type an available model."
            )
        print(f"agent> Currently implemented: {available}.")
        answer = input("you> ").strip()
        if not answer:
            return recommended_supported or "auto", False
        if _normalize_modeler_model_family(answer) is not None:
            return answer, True
        print("agent> That model is not implemented yet. Please choose an available model.")


def _generate_analysis_interpretation(
    *,
    analysis: dict[str, Any],
    chat_reply_only: Callable[[str], str],
) -> str:
    primary_prompt = _build_analysis_interpretation_prompt(analysis)
    primary = _safe_chat_reply(chat_reply_only=chat_reply_only, prompt=primary_prompt)
    if primary and not _looks_like_llm_failure_message(primary):
        return primary

    compact_prompt = _build_compact_analysis_interpretation_prompt(analysis)
    compact = _safe_chat_reply(chat_reply_only=chat_reply_only, prompt=compact_prompt)
    if compact and not _looks_like_llm_failure_message(compact):
        return compact
    return ""


def _generate_modeling_interpretation(
    *,
    training: dict[str, Any],
    target_signal: str,
    requested_model_family: str,
    chat_reply_only: Callable[[str], str],
) -> str:
    prompt = _build_modeling_interpretation_prompt(
        training=training,
        target_signal=target_signal,
        requested_model_family=requested_model_family,
    )
    primary = _safe_chat_reply(chat_reply_only=chat_reply_only, prompt=prompt)
    if primary and not _looks_like_llm_failure_message(primary):
        return primary
    compact = (
        "Interpret this model training result in 4 concise bullets: "
        "1) whether the selected model is scientifically credible, "
        "2) whether the requested model agreed with the best validation result, "
        "3) main risks, "
        "4) what to try next.\n"
        f"SUMMARY={dumps_json(_compact_modeling_summary(training, target_signal, requested_model_family), ensure_ascii=False)}"
    )
    secondary = _safe_chat_reply(chat_reply_only=chat_reply_only, prompt=compact)
    if secondary and not _looks_like_llm_failure_message(secondary):
        return secondary
    return ""


def _safe_chat_reply(*, chat_reply_only: Callable[[str], str], prompt: str) -> str:
    try:
        return chat_reply_only(prompt).strip()
    except Exception:
        return ""


def _build_modeling_interpretation_prompt(
    *,
    training: dict[str, Any],
    target_signal: str,
    requested_model_family: str,
) -> str:
    return (
        "Interpret this Agent 2 model training result for a lab engineer. "
        "Use 5-7 concise bullets. Cover: "
        "overall result quality, whether the requested model matched the best validation model, "
        "what the train/validation/test split implies, main risks, and immediate next actions. "
        "Do not invent values.\n"
        f"RESULTS_JSON={dumps_json(_compact_modeling_summary(training, target_signal, requested_model_family), ensure_ascii=False)}"
    )


def _compact_modeling_summary(
    training: dict[str, Any],
    target_signal: str,
    requested_model_family: str,
) -> dict[str, Any]:
    comparison_out: list[dict[str, Any]] = []
    comparison = training.get("comparison") if isinstance(training.get("comparison"), list) else []
    for item in comparison[:4]:
        if not isinstance(item, dict):
            continue
        comparison_out.append(
            {
                "model_family": item.get("model_family"),
                "validation_metrics": item.get("validation_metrics"),
                "test_metrics": item.get("test_metrics"),
            }
        )
    return {
        "target_signal": target_signal,
        "requested_model_family": requested_model_family,
        "selected_model_family": training.get("selected_model_family"),
        "best_validation_model_family": training.get("best_validation_model_family"),
        "selected_hyperparameters": training.get("selected_hyperparameters"),
        "model_params_path": training.get("model_params_path"),
        "lag_horizon_samples": training.get("lag_horizon_samples"),
        "split": training.get("split"),
        "preprocessing": training.get("preprocessing"),
        "normalization": training.get("normalization"),
        "selected_metrics": training.get("selected_metrics"),
        "comparison": comparison_out,
    }


def _build_analysis_interpretation_prompt(analysis: dict[str, Any]) -> str:
    quality = analysis.get("quality") if isinstance(analysis.get("quality"), dict) else {}
    ranking = analysis.get("ranking") if isinstance(analysis.get("ranking"), list) else []
    correlations = analysis.get("correlations")
    target_analyses = []
    if isinstance(correlations, dict):
        maybe_targets = correlations.get("target_analyses")
        if isinstance(maybe_targets, list):
            target_analyses = maybe_targets

    top_ranked: list[dict[str, Any]] = []
    for item in ranking[:3]:
        if not isinstance(item, dict):
            continue
        top_ranked.append(
            {
                "target_signal": item.get("target_signal"),
                "adjusted_score": item.get("adjusted_score"),
                "feasible": item.get("feasible"),
                "rationale": item.get("rationale"),
            }
        )

    top_predictors = _extract_top3_correlations_global(analysis)

    warnings = quality.get("warnings") if isinstance(quality, dict) else []
    if not isinstance(warnings, list):
        warnings = []

    summary = {
        "data_mode": analysis.get("data_mode"),
        "target_count": analysis.get("target_count"),
        "candidate_count": analysis.get("candidate_count"),
        "quality": {
            "rows": quality.get("rows"),
            "columns": quality.get("columns"),
            "completeness_score": quality.get("completeness_score"),
            "warnings": [str(item) for item in warnings[:6]],
        },
        "top_ranked_signals": top_ranked,
        "top_3_correlated_predictors": top_predictors,
    }

    return (
        "Interpret these Agent 1 results for a lab engineer. "
        "Give a concise scientific readout in 5-8 bullets: "
        "overall assessment, strongest evidence, risks/uncertainties, and immediate next actions. "
        "Mandatory: include one bullet that starts with `Top 3 correlated predictors:` and list "
        "the predictor_signal, target_signal, best_method, and best_abs_score from "
        "`top_3_correlated_predictors`. "
        "Do not invent values.\n"
        f"RESULTS_JSON={dumps_json(summary, ensure_ascii=False)}"
    )


def _build_compact_analysis_interpretation_prompt(analysis: dict[str, Any]) -> str:
    quality = analysis.get("quality") if isinstance(analysis.get("quality"), dict) else {}
    top3 = _extract_top3_correlations_global(analysis)
    rows = quality.get("rows", "n/a")
    completeness = quality.get("completeness_score", "n/a")
    warnings = quality.get("warnings") if isinstance(quality.get("warnings"), list) else []
    top3_line = _format_top3_correlations_line(top3) if top3 else "Top 3 correlated predictors: n/a"
    return (
        "You are Agent 1's scientific narrator. Use concise plain text.\n"
        "Summarize in 4 numbered points:\n"
        "1) data quality,\n"
        "2) strongest evidence,\n"
        "3) key risks,\n"
        "4) immediate next actions.\n"
        "Mandatory: include one bullet that starts with `Top 3 correlated predictors:` exactly.\n"
        f"rows={rows}\n"
        f"completeness_score={completeness}\n"
        f"warnings={warnings[:5]}\n"
        f"{top3_line}\n"
    )


def _extract_top3_correlations_global(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    correlations = analysis.get("correlations")
    target_analyses: list[dict[str, Any]] = []
    if isinstance(correlations, dict):
        maybe_targets = correlations.get("target_analyses")
        if isinstance(maybe_targets, list):
            target_analyses = [row for row in maybe_targets if isinstance(row, dict)]

    flattened: list[dict[str, Any]] = []
    for target in target_analyses:
        target_signal = str(target.get("target_signal", "")).strip()
        predictor_rows = target.get("predictor_results")
        if not isinstance(predictor_rows, list):
            continue
        for row in predictor_rows:
            if not isinstance(row, dict):
                continue
            score = _float_value_or_none(row.get("best_abs_score"))
            predictor_signal = str(row.get("predictor_signal", "")).strip()
            best_method = str(row.get("best_method", "")).strip()
            if not predictor_signal or score is None:
                continue
            flattened.append(
                {
                    "target_signal": target_signal,
                    "predictor_signal": predictor_signal,
                    "best_method": best_method or "n/a",
                    "best_abs_score": float(score),
                    "sample_count": row.get("sample_count"),
                }
            )

    flattened.sort(
        key=lambda item: float(item.get("best_abs_score", 0.0)),
        reverse=True,
    )
    return flattened[:3]


def _format_top3_correlations_line(top3: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in top3:
        predictor = str(row.get("predictor_signal", "n/a"))
        target = str(row.get("target_signal", "n/a"))
        method = str(row.get("best_method", "n/a"))
        score = _float_value_or_none(row.get("best_abs_score"))
        score_text = f"{score:.3f}" if score is not None else "n/a"
        parts.append(f"{predictor}->{target} ({method}, abs={score_text})")
    return "Top 3 correlated predictors: " + "; ".join(parts)


def _interpretation_mentions_top3(*, interpretation: str, top3: list[dict[str, Any]]) -> bool:
    lowered = interpretation.lower()
    return all(
        str(row.get("predictor_signal", "")).strip().lower() in lowered
        for row in top3
        if str(row.get("predictor_signal", "")).strip()
    )


def _execute_registry_tool(registry: Any, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = registry.execute(tool_name, _drop_none_fields(arguments))
    output = result.output
    if not isinstance(output, dict):
        return {"status": "error", "message": f"Tool '{tool_name}' returned non-object output."}
    return output


def _prompt_sheet_selection(
    options: list[str],
    *,
    chat_detour: Callable[[str, str], None] | None = None,
) -> str | None:
    if not options:
        return None
    _print_sheet_options(options)
    lowered_to_name = {str(name).lower(): str(name) for name in options}
    while True:
        selection = input("you> ").strip()
        lowered = selection.lower()
        if lowered in {"cancel", "abort"}:
            return None
        if lowered in {"list", "show", "help", "?"}:
            _print_sheet_options(options)
            continue
        if _looks_like_small_talk(selection):
            if chat_detour is not None:
                chat_detour(
                    selection,
                    "To continue, please enter a sheet number/name, type 'list', or 'cancel'.",
                )
            else:
                print(
                    "agent> I can chat, and we are selecting an Excel sheet now. "
                    "Please enter a sheet number/name, type 'list' to show sheets again, "
                    "or 'cancel' to abort."
                )
            continue
        if selection.isdigit():
            index = int(selection)
            if 1 <= index <= len(options):
                return str(options[index - 1])
        resolved = lowered_to_name.get(lowered)
        if resolved is not None:
            return resolved
        print(
            "agent> Invalid selection. Enter a sheet number/name, "
            "type 'list' to show sheets, or 'cancel' to abort."
        )


def _print_sheet_options(options: list[str]) -> None:
    print("agent> Multiple sheets detected. Please choose one:")
    for idx, name in enumerate(options, start=1):
        print(f"agent>   {idx}. {name}")


def _prompt_header_confirmation(
    *,
    header_row: int,
    data_start_row: int,
    chat_detour: Callable[[str, str], None] | None = None,
) -> tuple[int, int]:
    while True:
        print(
            "agent> Use inferred rows "
            f"header={header_row}, data_start={data_start_row}? [Y/n or custom 'h,d']"
        )
        answer = input("you> ").strip()
        lowered = answer.lower()
        parsed_override = _parse_header_override(answer)
        if parsed_override is not None:
            return parsed_override
        if lowered in {"", "y", "yes"}:
            return header_row, data_start_row
        if lowered in {"n", "no"}:
            return _prompt_header_override(
                default_header_row=header_row,
                default_data_start_row=data_start_row,
                chat_detour=chat_detour,
            )
        if _looks_like_small_talk(answer):
            if chat_detour is not None:
                chat_detour(
                    answer,
                    "To continue, reply with Y/Enter to keep inferred rows, N to change, or 'h,d'.",
                )
            else:
                print(
                    "agent> I can chat, and we are confirming inferred rows now. "
                    "Reply with Y/Enter to keep inferred rows, N to change, "
                    "or 'h,d' (for example 2,3)."
                )
            continue
        print(
            "agent> I did not parse that. Reply Y/Enter to keep inferred rows, "
            "N to change, or 'h,d' (for example 2,3)."
        )


def _prompt_header_override(
    *,
    default_header_row: int,
    default_data_start_row: int,
    chat_detour: Callable[[str, str], None] | None = None,
) -> tuple[int, int]:
    while True:
        print("agent> Enter header_row,data_start_row (e.g. 2,3). Press Enter to keep inferred.")
        second = input("you> ").strip()
        lowered = second.lower()
        if not second or lowered in {"y", "yes", "keep"}:
            return default_header_row, default_data_start_row
        parsed_second = _parse_header_override(second)
        if parsed_second is not None:
            return parsed_second
        if _looks_like_small_talk(second):
            if chat_detour is not None:
                chat_detour(
                    second,
                    "To continue, please enter 'header_row,data_start_row' or press Enter to keep inferred rows.",
                )
            else:
                print(
                    "agent> I can chat, and we are choosing explicit row numbers now. "
                    "Please enter 'header_row,data_start_row' (for example 2,3), "
                    "or press Enter to keep inferred rows."
                )
            continue
        print(
            "agent> Invalid format. Use 'header_row,data_start_row' with "
            "data_start_row greater than header_row."
        )


def _parse_header_override(raw: str) -> tuple[int, int] | None:
    text = raw.strip()
    if not text:
        return None
    match = re.match(r"^\s*(\d+)\s*,\s*(\d+)\s*$", text)
    if not match:
        return None
    header_row = int(match.group(1))
    data_start_row = int(match.group(2))
    if data_start_row <= header_row:
        return None
    return header_row, data_start_row


def _extract_first_data_path(user_message: str) -> Path | None:
    quoted = re.findall(r"[\"']([^\"']+\.(?:csv|xlsx|xls))[\"']", user_message, flags=re.IGNORECASE)
    candidates: list[str] = list(quoted)

    absolute_windows = re.findall(
        r"([A-Za-z]:\\[^\n]+?\.(?:csv|xlsx|xls))",
        user_message,
        flags=re.IGNORECASE,
    )
    candidates.extend(absolute_windows)

    plain = re.findall(r"([^\s\"']+\.(?:csv|xlsx|xls))", user_message, flags=re.IGNORECASE)
    candidates.extend(plain)

    for raw in candidates:
        cleaned = raw.strip().rstrip(".,;:)")
        if not cleaned:
            continue
        path = Path(cleaned).expanduser()
        if path.exists():
            return path
    for raw in candidates:
        cleaned = raw.strip().rstrip(".,;:)")
        if not cleaned:
            continue
        return Path(cleaned).expanduser()
    return None


def _resolve_default_public_dataset_path() -> Path | None:
    candidates: list[Path] = []
    candidates.append(Path("data/public/public_testbench_dataset_20k_minmax.csv"))
    candidates.append(Path("data/public/public_testbench_dataset_20k_minmax.xlsx"))
    repo_root_guess = Path(__file__).resolve().parents[3]
    candidates.append(
        repo_root_guess / "data" / "public" / "public_testbench_dataset_20k_minmax.csv"
    )
    candidates.append(
        repo_root_guess / "data" / "public" / "public_testbench_dataset_20k_minmax.xlsx"
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def _path_for_display(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(resolved)


def _compact_event_for_context(event: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "status": event.get("status"),
        "message": _truncate_text(str(event.get("message", "")), 500),
        "error": _truncate_text(str(event.get("error", "")), 300),
    }
    action = event.get("action")
    if isinstance(action, dict):
        compact["action"] = {
            "action": action.get("action"),
            "tool_name": action.get("tool_name"),
        }
    tool_output = event.get("tool_output")
    if isinstance(tool_output, dict):
        compact["tool_output"] = {
            "data_mode": tool_output.get("data_mode"),
            "target_count": tool_output.get("target_count"),
            "candidate_count": tool_output.get("candidate_count"),
            "report_path": tool_output.get("report_path"),
        }
    return compact


def _truncate_text(value: str, max_len: int) -> str:
    if len(value) <= max_len:
        return value
    return value[: max_len - 3] + "..."


def _parse_target_selection(
    *,
    target_answer: str,
    available_signals: list[str],
    default_count: int,
) -> list[str]:
    if not target_answer.strip():
        return list(available_signals[:default_count])
    requested = [item.strip() for item in target_answer.split(",") if item.strip()]
    selected = [item for item in requested if item in available_signals]
    if selected:
        return selected
    return list(available_signals[:default_count])


def _suggest_default_analysis_targets(
    *,
    available_signals: list[str],
    default_count: int,
) -> list[str]:
    if not available_signals:
        return []
    label_keywords = (
        "target",
        "label",
        "class",
        "fraud",
        "anomaly",
        "flag",
        "outcome",
        "status",
        "result",
    )
    hinted = [
        signal
        for signal in available_signals
        if any(token in signal.lower() for token in label_keywords)
    ]
    if hinted:
        return hinted[: min(3, len(hinted))]
    if len(available_signals) <= 8:
        return list(available_signals)
    return list(available_signals[: max(1, min(default_count, len(available_signals)))])


def _target_selection_prompt_text(*, default_targets: list[str]) -> str:
    preview = ", ".join(f"`{item}`" for item in default_targets[:5])
    if not preview:
        preview = "`n/a`"
    return (
        "agent> Enter comma-separated target signals to focus, "
        "'all' for full run, 'list' to show signal names, "
        "or `hypothesis ...` to add hypotheses; "
        f"or press Enter to use the suggested target set ({preview})."
    )


def _print_analysis_dataset_overview(*, preflight: dict[str, Any]) -> None:
    row_count = int(preflight.get("row_count") or 0)
    column_count = int(preflight.get("column_count") or 0)
    numeric_signals = [str(item) for item in (preflight.get("numeric_signal_columns") or [])]
    timestamp_hint = str(preflight.get("timestamp_column_hint") or "").strip()
    line = (
        "agent> Dataset overview: "
        f"rows={row_count}, columns={column_count}, numeric_signals={len(numeric_signals)}"
    )
    if timestamp_hint:
        line += f", timestamp_hint=`{timestamp_hint}`"
    line += "."
    print(line)


def _prompt_target_selection(
    *,
    available_signals: list[str],
    default_count: int,
    default_targets: list[str] | None = None,
    hypothesis_state: dict[str, list[dict[str, Any]]] | None = None,
    chat_detour: Callable[[str, str], None] | None = None,
) -> list[str] | None:
    resolved_defaults = [
        item for item in (default_targets or []) if item in available_signals
    ] or _suggest_default_analysis_targets(
        available_signals=available_signals,
        default_count=default_count,
    )
    while True:
        answer = input("you> ").strip()
        lowered = answer.lower()
        if lowered in {"y", "yes", "default"}:
            return list(resolved_defaults)
        if lowered == "all":
            return None
        if lowered.startswith("hypothesis"):
            parsed = _parse_inline_hypothesis_command(
                user_message=answer,
                available_signals=available_signals,
            )
            if parsed["user_hypotheses"] or parsed["feature_hypotheses"]:
                if hypothesis_state is not None:
                    _merge_hypothesis_state(hypothesis_state, parsed)
                print(
                    "agent> Hypotheses noted. "
                    f"correlation={len(parsed['user_hypotheses'])}, "
                    f"feature={len(parsed['feature_hypotheses'])}. "
                    "Now continue with target selection."
                )
                print(_target_selection_prompt_text(default_targets=resolved_defaults))
                continue
            print(
                "agent> Hypothesis format not recognized. "
                "Use: `hypothesis corr target:pred1,pred2; target2:pred3` or "
                "`hypothesis feature target:signal->rate_change; signal2->square`."
            )
            continue
        if lowered.startswith("list"):
            query = answer[4:].strip()
            _print_signal_names(available_signals, query=query)
            print(_target_selection_prompt_text(default_targets=resolved_defaults))
            continue
        selected, unknown = _parse_target_selection_with_unknowns(
            target_answer=answer,
            available_signals=available_signals,
            default_targets=resolved_defaults,
        )
        if unknown and not selected:
            if _looks_like_small_talk(answer):
                if chat_detour is not None:
                    chat_detour(
                        answer,
                        "To continue, type 'list' to show names, 'all' for full run, or provide target signals.",
                    )
                else:
                    print(
                        "agent> I am good and ready to continue. "
                        "We are currently selecting target signals. "
                        "If useful, add hypotheses via `hypothesis ...`. "
                        "Type 'list' to show names, 'all' for full run, "
                        "or press Enter for the suggested targets."
                    )
                continue
            print(
                "agent> No matching signal names found. "
                "Type 'list' to display available names."
            )
            continue
        if unknown:
            print(f"agent> Ignoring unknown signals: {unknown}")
        return selected


def _parse_target_selection_with_unknowns(
    *,
    target_answer: str,
    available_signals: list[str],
    default_targets: list[str],
) -> tuple[list[str], list[str]]:
    if not target_answer.strip():
        return list(default_targets), []

    requested = [item.strip() for item in target_answer.split(",") if item.strip()]
    available_lookup = {name.lower(): name for name in available_signals}
    selected: list[str] = []
    unknown: list[str] = []
    for item in requested:
        resolved: str | None = None
        if item.isdigit():
            idx = int(item)
            if 1 <= idx <= len(available_signals):
                resolved = available_signals[idx - 1]
        if resolved is None:
            resolved = available_lookup.get(item.lower())
        if resolved is None:
            fuzzy = [name for name in available_signals if item.lower() in name.lower()]
            if len(fuzzy) == 1:
                resolved = fuzzy[0]
        if resolved:
            selected.append(resolved)
        else:
            unknown.append(item)

    deduped: list[str] = []
    seen: set[str] = set()
    for name in selected:
        if name not in seen:
            deduped.append(name)
            seen.add(name)

    return deduped, unknown


def _parse_inline_hypothesis_command(
    *,
    user_message: str,
    available_signals: list[str],
) -> dict[str, list[dict[str, Any]]]:
    parsed: dict[str, list[dict[str, Any]]] = {
        "user_hypotheses": [],
        "feature_hypotheses": [],
    }
    text = user_message.strip()
    lowered = text.lower()
    if "hypothesis" not in lowered:
        return parsed

    payload = text
    if lowered.startswith("hypothesis"):
        payload = text[len("hypothesis") :].strip()
    if not payload:
        return parsed

    segments = [part.strip() for part in payload.split(";") if part.strip()]
    for segment in segments:
        seg_lower = segment.lower()
        if seg_lower.startswith("corr"):
            seg_body = segment[4:].strip()
            corr = _parse_correlation_hypothesis_segment(
                segment=seg_body,
                available_signals=available_signals,
            )
            if corr:
                parsed["user_hypotheses"].append(corr)
            continue
        if seg_lower.startswith("feature"):
            seg_body = segment[7:].strip()
            features = _parse_feature_hypothesis_segment(
                segment=seg_body,
                available_signals=available_signals,
            )
            parsed["feature_hypotheses"].extend(features)
            continue
        corr = _parse_correlation_hypothesis_segment(
            segment=segment,
            available_signals=available_signals,
        )
        if corr:
            parsed["user_hypotheses"].append(corr)
            continue
        features = _parse_feature_hypothesis_segment(
            segment=segment,
            available_signals=available_signals,
        )
        parsed["feature_hypotheses"].extend(features)
    return parsed


def _parse_correlation_hypothesis_segment(
    *,
    segment: str,
    available_signals: list[str],
) -> dict[str, Any] | None:
    if ":" not in segment:
        return None
    left, right = segment.split(":", 1)
    target = _resolve_signal_name(left.strip(), available_signals)
    if target is None:
        return None
    raw_predictors = [item.strip() for item in re.split(r"[,\|]", right) if item.strip()]
    predictors: list[str] = []
    seen: set[str] = set()
    for raw in raw_predictors:
        resolved = _resolve_signal_name(raw, available_signals)
        if resolved is None or resolved == target or resolved in seen:
            continue
        predictors.append(resolved)
        seen.add(resolved)
    if not predictors:
        return None
    return {
        "target_signal": target,
        "predictor_signals": predictors,
        "user_reason": "user hypothesis",
    }


def _parse_feature_hypothesis_segment(
    *,
    segment: str,
    available_signals: list[str],
) -> list[dict[str, Any]]:
    if "->" not in segment:
        return []
    target_signal = ""
    payload = segment.strip()
    if ":" in payload and payload.index(":") < payload.index("->"):
        left, right = payload.split(":", 1)
        resolved_target = _resolve_signal_name(left.strip(), available_signals)
        if resolved_target is None:
            return []
        target_signal = resolved_target
        payload = right.strip()
    if "->" not in payload:
        return []
    base_raw, transform_raw = payload.split("->", 1)
    base_signal = _resolve_signal_name(base_raw.strip(), available_signals)
    if base_signal is None:
        return []
    transforms = [
        token.strip().lower()
        for token in re.split(r"[,\|]", transform_raw)
        if token.strip()
    ]
    allowed = {
        "rate_change",
        "delta",
        "pct_change",
        "signed_log",
        "square",
        "sqrt_abs",
        "inverse",
        "lag1",
        "lag2",
        "lag3",
    }
    rows: list[dict[str, Any]] = []
    for transformation in transforms:
        if transformation not in allowed:
            continue
        rows.append(
            {
                "target_signal": target_signal,
                "base_signal": base_signal,
                "transformation": transformation,
                "user_reason": "user hypothesis",
            }
        )
    return rows


def _resolve_signal_name(raw: str, available_signals: list[str]) -> str | None:
    token = raw.strip()
    if not token:
        return None
    if token.isdigit():
        idx = int(token)
        if 1 <= idx <= len(available_signals):
            return available_signals[idx - 1]
    lookup = {name.lower(): name for name in available_signals}
    exact = lookup.get(token.lower())
    if exact:
        return exact
    fuzzy = [name for name in available_signals if token.lower() in name.lower()]
    if len(fuzzy) == 1:
        return fuzzy[0]
    return None


def _merge_hypothesis_state(
    state: dict[str, list[dict[str, Any]]],
    update: dict[str, list[dict[str, Any]]],
) -> None:
    corr_seen = {
        (
            str(item.get("target_signal", "")),
            tuple(str(v) for v in item.get("predictor_signals", [])),
        )
        for item in state.get("user_hypotheses", [])
    }
    for item in update.get("user_hypotheses", []):
        key = (
            str(item.get("target_signal", "")),
            tuple(str(v) for v in item.get("predictor_signals", [])),
        )
        if key in corr_seen:
            continue
        state.setdefault("user_hypotheses", []).append(item)
        corr_seen.add(key)

    feat_seen = {
        (
            str(item.get("target_signal", "")),
            str(item.get("base_signal", "")),
            str(item.get("transformation", "")),
        )
        for item in state.get("feature_hypotheses", [])
    }
    for item in update.get("feature_hypotheses", []):
        key = (
            str(item.get("target_signal", "")),
            str(item.get("base_signal", "")),
            str(item.get("transformation", "")),
        )
        if key in feat_seen:
            continue
        state.setdefault("feature_hypotheses", []).append(item)
        feat_seen.add(key)


def _prompt_lag_preferences(
    *,
    timestamp_column_hint: str,
    estimated_sample_period_seconds: float | None,
    chat_detour: Callable[[str, str], None] | None = None,
) -> dict[str, Any]:
    print(f"agent> Detected timestamp column hint: `{timestamp_column_hint}`.")
    while True:
        print("agent> Do you expect time-based lag effects? [Y/n]")
        answer = input("you> ").strip().lower()
        if answer in {"", "y", "yes"}:
            break
        if answer in {"n", "no"}:
            return {"enabled": False, "dimension": "none", "max_lag": 0}
        if _looks_like_small_talk(answer):
            if chat_detour is not None:
                chat_detour(
                    answer,
                    "To continue, reply Y/Enter to investigate lags, or N to skip lag search.",
                )
            else:
                print(
                    "agent> I can chat, and we are deciding lag analysis scope now. "
                    "Reply Y/Enter to investigate lags, or N to skip lag search."
                )
            continue
        print("agent> Please answer Y/Enter or N.")

    while True:
        print("agent> Lag dimension? Enter `samples` or `seconds` [samples].")
        dimension = input("you> ").strip().lower()
        if dimension in {"", "samples", "sample"}:
            max_lag_samples = _prompt_positive_int(
                prompt=(
                    "agent> Enter maximum lag in samples (positive integer). "
                    "Press Enter for default 8."
                ),
                default_value=8,
                chat_detour=chat_detour,
            )
            return {"enabled": True, "dimension": "samples", "max_lag": max_lag_samples}
        if dimension in {"seconds", "second", "sec", "s"}:
            lag_seconds = _prompt_positive_float(
                prompt=(
                    "agent> Enter maximum lag window in seconds (positive number, for example 2.5)."
                ),
                default_value=None,
                chat_detour=chat_detour,
            )
            default_period = estimated_sample_period_seconds
            if default_period is not None:
                period_prompt = (
                    "agent> Enter sample period in seconds. "
                    f"Press Enter to use estimated {default_period:.6f}s."
                )
            else:
                period_prompt = (
                    "agent> Enter sample period in seconds "
                    "(required to convert seconds to lag samples)."
                )
            sample_period = _prompt_positive_float(
                prompt=period_prompt,
                default_value=default_period,
                chat_detour=chat_detour,
            )
            max_lag_samples = max(1, int(round(lag_seconds / sample_period)))
            return {"enabled": True, "dimension": "seconds", "max_lag": max_lag_samples}
        if _looks_like_small_talk(dimension):
            if chat_detour is not None:
                chat_detour(
                    dimension,
                    "To continue, choose lag dimension: `samples` or `seconds`.",
                )
            else:
                print(
                    "agent> We need a lag dimension choice to continue. "
                    "Use `samples` or `seconds`."
                )
            continue
        print("agent> Invalid lag dimension. Use `samples` or `seconds`.")


def _prompt_sample_budget(
    *,
    row_count: int,
    chat_detour: Callable[[str, str], None] | None = None,
) -> dict[str, Any]:
    if row_count <= 0:
        return {"max_samples": None, "sample_selection": "uniform"}
    if row_count < 500:
        return {"max_samples": None, "sample_selection": "uniform"}
    print(f"agent> Dataset contains {row_count} rows.")
    while True:
        print("agent> Analyze all rows? [Y/n]")
        answer = input("you> ").strip().lower()
        if answer in {"", "y", "yes"}:
            return {"max_samples": None, "sample_selection": "uniform"}
        if answer in {"n", "no"}:
            break
        if _looks_like_small_talk(answer):
            if chat_detour is not None:
                chat_detour(
                    answer,
                    "To continue, reply Y/Enter for all rows, or N to set a subset.",
                )
            else:
                print(
                    "agent> We are choosing analysis sample count. "
                    "Reply Y/Enter for all rows, or N to set a subset."
                )
            continue
        print("agent> Please answer Y/Enter or N.")

    count = _prompt_positive_int(
        prompt=(
            "agent> Enter number of rows to analyze "
            f"(1..{row_count})."
        ),
        default_value=min(row_count, 2000),
        chat_detour=chat_detour,
    )
    count = max(1, min(count, row_count))
    while True:
        print("agent> Sampling mode? Enter `uniform`, `head`, or `tail` [uniform].")
        mode = input("you> ").strip().lower()
        if mode in {"", "uniform"}:
            return {"max_samples": count, "sample_selection": "uniform"}
        if mode in {"head", "tail"}:
            return {"max_samples": count, "sample_selection": mode}
        if _looks_like_small_talk(mode):
            if chat_detour is not None:
                chat_detour(
                    mode,
                    "To continue, choose sampling mode: uniform, head, or tail.",
                )
            else:
                print("agent> Sampling mode controls subset selection order. Use uniform/head/tail.")
            continue
        print("agent> Invalid mode. Use uniform, head, or tail.")


def _prompt_data_issue_handling(
    *,
    preflight: dict[str, Any],
    chat_detour: Callable[[str, str], None] | None = None,
) -> dict[str, Any]:
    plan: dict[str, Any] = {
        "missing_data_strategy": "keep",
        "fill_constant_value": None,
        "row_coverage_strategy": "keep",
        "sparse_row_min_fraction": 0.8,
        "row_range_start": None,
        "row_range_end": None,
    }
    missing_fraction = _safe_float_or_none(preflight.get("missing_overall_fraction")) or 0.0
    missing_cols_count = int(preflight.get("columns_with_missing_count") or 0)
    missing_cols = [str(item) for item in (preflight.get("columns_with_missing") or [])]
    if missing_fraction > 0.0:
        preview = ", ".join(missing_cols[:8]) if missing_cols else "n/a"
        print(
            "agent> Missing-data detected: "
            f"overall_fraction={missing_fraction:.3f}, "
            f"columns_with_missing={missing_cols_count} "
            f"(examples: {preview})."
        )
        print(
            "agent> Leakage note: if missing-value statistics are fit on full data before "
            "train/validation/test split, evaluation can be optimistic."
        )
        print(
            "agent> Split-safe rule for modeling: split first, fit missing-data handling on "
            "train only, then apply the same transform to validation/test."
        )
        print(
            "agent> Choose missing-data handling: "
            "`keep`, `drop_rows`, `fill_median`, `fill_constant` [keep]."
        )
        while True:
            answer = input("you> ").strip().lower()
            if answer in {"", "keep"}:
                break
            if answer in {"drop_rows", "fill_median", "fill_constant"}:
                plan["missing_data_strategy"] = answer
                if answer == "fill_constant":
                    value = _prompt_numeric_value(
                        prompt=(
                            "agent> Enter fill constant (numeric). "
                            "Use negative values if needed."
                        ),
                        default_value=0.0,
                        chat_detour=chat_detour,
                    )
                    plan["fill_constant_value"] = float(value)
                    print(
                        "agent> Leakage note: fill_constant is usually low leakage risk only "
                        "if the constant is fixed a priori."
                    )
                elif answer == "fill_median":
                    print(
                        "agent> Leakage warning: fill_median computed on full data is "
                        "data leakage for downstream train/test evaluation."
                    )
                elif answer == "drop_rows":
                    print(
                        "agent> Caution: drop_rows avoids statistic leakage, but can still bias "
                        "split distributions if done globally before splitting."
                    )
                break
            if _looks_like_small_talk(answer):
                if chat_detour is not None:
                    chat_detour(
                        answer,
                        "To continue, choose missing-data handling: keep, drop_rows, fill_median, or fill_constant.",
                    )
                else:
                    print(
                        "agent> This choice controls NaN handling before correlation. "
                        "Use keep/drop_rows/fill_median/fill_constant."
                    )
                continue
            print("agent> Invalid choice. Use keep, drop_rows, fill_median, or fill_constant.")

    mismatch = bool(preflight.get("potential_length_mismatch"))
    if mismatch:
        row_min = _safe_float_or_none(preflight.get("row_non_null_fraction_min")) or 0.0
        row_med = _safe_float_or_none(preflight.get("row_non_null_fraction_median")) or 0.0
        row_max = _safe_float_or_none(preflight.get("row_non_null_fraction_max")) or 0.0
        print(
            "agent> Uneven row coverage detected (possible different signal lengths): "
            f"min/median/max non-null fraction = {row_min:.3f}/{row_med:.3f}/{row_max:.3f}."
        )
        print(
            "agent> Choose row-coverage handling: "
            "`keep`, `drop_sparse_rows`, `trim_dense_window`, `manual_range` [keep]."
        )
        while True:
            answer = input("you> ").strip().lower()
            if answer in {"", "keep"}:
                break
            if answer in {"drop_sparse_rows", "trim_dense_window"}:
                plan["row_coverage_strategy"] = answer
                threshold = _prompt_fraction(
                    prompt=(
                        "agent> Enter non-null fraction threshold between 0 and 1 "
                        "(default 0.8)."
                    ),
                    default_value=0.8,
                    chat_detour=chat_detour,
                )
                plan["sparse_row_min_fraction"] = threshold
                break
            if answer == "manual_range":
                plan["row_coverage_strategy"] = "manual_range"
                start, end = _prompt_manual_row_range(chat_detour=chat_detour)
                plan["row_range_start"] = start
                plan["row_range_end"] = end
                break
            if _looks_like_small_talk(answer):
                if chat_detour is not None:
                    chat_detour(
                        answer,
                        "To continue, choose row-coverage handling: keep, drop_sparse_rows, trim_dense_window, or manual_range.",
                    )
                else:
                    print(
                        "agent> This choice controls how to align uneven row coverage. "
                        "Use keep/drop_sparse_rows/trim_dense_window/manual_range."
                    )
                continue
            print(
                "agent> Invalid choice. Use keep, drop_sparse_rows, "
                "trim_dense_window, or manual_range."
            )
    return plan


def _prompt_positive_int(
    *,
    prompt: str,
    default_value: int | None,
    chat_detour: Callable[[str, str], None] | None = None,
) -> int:
    while True:
        print(prompt)
        raw = input("you> ").strip()
        if not raw and default_value is not None:
            return int(default_value)
        try:
            value = int(raw)
        except ValueError:
            if _looks_like_small_talk(raw):
                if chat_detour is not None:
                    chat_detour(raw, "To continue, provide a positive integer value.")
                else:
                    print("agent> Please provide a positive integer value.")
            else:
                print("agent> Invalid number. Please provide a positive integer.")
            continue
        if value > 0:
            return value
        print("agent> Value must be > 0.")


def _prompt_positive_float(
    *,
    prompt: str,
    default_value: float | None,
    chat_detour: Callable[[str, str], None] | None = None,
) -> float:
    while True:
        print(prompt)
        raw = input("you> ").strip()
        if not raw and default_value is not None:
            return float(default_value)
        try:
            value = float(raw)
        except ValueError:
            if _looks_like_small_talk(raw):
                if chat_detour is not None:
                    chat_detour(raw, "To continue, provide a positive numeric value.")
                else:
                    print("agent> Please provide a positive numeric value.")
            else:
                print("agent> Invalid number. Please provide a positive numeric value.")
            continue
        if value > 0.0:
            return value
        print("agent> Value must be > 0.")


def _prompt_fraction(
    *,
    prompt: str,
    default_value: float,
    chat_detour: Callable[[str, str], None] | None = None,
) -> float:
    while True:
        print(prompt)
        raw = input("you> ").strip()
        if not raw:
            return float(default_value)
        try:
            value = float(raw)
        except ValueError:
            if _looks_like_small_talk(raw):
                if chat_detour is not None:
                    chat_detour(raw, "To continue, provide a number between 0 and 1.")
                else:
                    print("agent> Please provide a number between 0 and 1.")
            else:
                print("agent> Invalid value. Please provide a number between 0 and 1.")
            continue
        if 0.0 < value <= 1.0:
            return value
        print("agent> Threshold must be in (0, 1].")


def _prompt_numeric_value(
    *,
    prompt: str,
    default_value: float,
    chat_detour: Callable[[str, str], None] | None = None,
) -> float:
    while True:
        print(prompt)
        raw = input("you> ").strip()
        if not raw:
            return float(default_value)
        try:
            return float(raw)
        except ValueError:
            if _looks_like_small_talk(raw):
                if chat_detour is not None:
                    chat_detour(raw, "To continue, provide a numeric value.")
                else:
                    print("agent> Please provide a numeric value.")
            else:
                print("agent> Invalid value. Please provide a numeric value.")


def _prompt_manual_row_range(
    *,
    chat_detour: Callable[[str, str], None] | None = None,
) -> tuple[int, int]:
    while True:
        print("agent> Enter manual row range as `start,end` (0-based, inclusive).")
        raw = input("you> ").strip()
        parsed = _parse_row_range(raw)
        if parsed is not None:
            return parsed
        if _looks_like_small_talk(raw):
            if chat_detour is not None:
                chat_detour(raw, "To continue, provide a numeric row range like `100,2500`.")
            else:
                print("agent> Use numeric row range like `100,2500`.")
            continue
        print("agent> Invalid range. Use `start,end` with end >= start.")


def _parse_row_range(raw: str) -> tuple[int, int] | None:
    text = raw.strip()
    match = re.match(r"^\s*(\d+)\s*,\s*(\d+)\s*$", text)
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2))
    if end < start:
        return None
    return start, end


def _safe_float_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed <= 0:
        return None
    return parsed


def _float_value_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed


def _print_signal_names(signals: list[str], *, query: str) -> None:
    q = query.strip().lower()
    if q:
        generic = {"signals", "signal", "signal names", "the signal names", "names"}
        if q in generic:
            q = ""
    filtered = [name for name in signals if q in name.lower()] if q else list(signals)
    if not filtered:
        print("agent> No signal names match that filter.")
        return
    print(f"agent> Available signals ({len(filtered)}):")
    for idx, name in enumerate(filtered, start=1):
        print(f"agent>   {idx}. {name}")


def _print_header_preview(preflight: dict[str, Any]) -> None:
    columns = [str(item) for item in (preflight.get("signal_columns") or [])]
    if not columns:
        return
    header_row = preflight.get("header_row")
    candidate_rows = preflight.get("candidate_header_rows") or []
    print(
        "agent> Inferred header preview "
        f"(header_row={header_row}, candidates={candidate_rows}):"
    )
    for idx, name in enumerate(columns, start=1):
        print(f"agent>   {idx}. {name}")


def _llm_chat_detour(
    *,
    agent: str,
    user_message: str,
    session_context: dict[str, Any],
    session_messages: list[dict[str, str]],
    config_path: str | None,
    record_in_history: bool = True,
) -> str:
    turn_context = dict(session_context)
    turn_context["session_messages"] = list(session_messages)
    turn_context["recent_user_prompts"] = _recent_user_prompts(
        session_messages=session_messages,
        limit=5,
    )
    turn_context["chat_only"] = True
    try:
        result = _invoke_agent_once_with_recovery(
            agent=agent,
            user_message=user_message,
            context=turn_context,
            config_path=config_path,
        )
        event = result.get("event", {})
        response = str(event.get("message", "")).strip()
        if not response:
            response = "[empty response]"
        if record_in_history:
            session_messages.append({"role": "user", "content": user_message})
            session_messages.append({"role": "assistant", "content": response})
            session_messages[:] = session_messages[-20:]
            session_context["last_event"] = _compact_event_for_context(event)
        return response
    except Exception as exc:
        response = _runtime_error_fallback_message(
            agent=agent,
            user_message=user_message,
            error=exc,
        )
        if record_in_history:
            session_messages.append({"role": "user", "content": user_message})
            session_messages.append({"role": "assistant", "content": response})
            session_messages[:] = session_messages[-20:]
            session_context["last_event"] = _compact_event_for_context(
                {"status": "respond", "message": response, "error": "runtime_error"}
            )
        return response


def _rewrite_unhelpful_response(
    *,
    agent: str,
    user_message: str,
    response: str,
    chat_detour: Callable[[str], str] | None = None,
) -> str:
    if agent != "analyst":
        return response
    lowered = response.lower()
    fallback_markers = (
        "repeated tool argument errors",
        "turn limit before a stable answer",
        "too many invalid actions",
    )
    if any(marker in lowered for marker in fallback_markers):
        no_data_path = _extract_first_data_path(user_message) is None
        if no_data_path and chat_detour is not None:
            detour = chat_detour(user_message).strip()
            if detour:
                return detour
        if _is_casual_chat_message(user_message):
            return "I hit a tool-loop issue, but I can still chat. Ask again and I will answer directly."
        if no_data_path:
            return (
                "I hit a tool-loop issue on that request. "
                "If you want analysis, paste a .csv/.xlsx path. "
                "If you want a conceptual answer, ask directly and I will respond."
            )
    return response


def _is_simple_greeting(text: str) -> bool:
    normalized = text.strip().lower()
    return normalized in {"hi", "hello", "hey", "yo", "good morning", "good evening"}


def _is_casual_chat_message(text: str) -> bool:
    normalized = text.strip().lower()
    if not normalized:
        return False
    if _is_simple_greeting(normalized):
        return True
    phrases = {
        "how are you",
        "who are you",
        "what can you do",
        "what?",
        "thanks",
        "thank you",
    }
    if any(phrase in normalized for phrase in phrases):
        return True
    if normalized.endswith("?") and _extract_first_data_path(normalized) is None:
        return True
    return False


def _casual_chat_response(user_message: str) -> str:
    normalized = user_message.strip().lower()
    if "how are you" in normalized:
        return (
            "I am ready to help. I can chat and run analysis locally. "
            "Paste a .csv/.xlsx path when you want to start."
        )
    if "who are you" in normalized or "what can you do" in normalized:
        return (
            "I am your local Relaytic analyst. I can ingest structured snapshots such as CSV, Parquet, JSONL, and Excel, validate headers/sheets, "
            "run quality checks, stationarity checks, correlation analysis, and generate reports."
        )
    return (
        "Hi. I can chat and help with analysis. "
        "To start dataset analysis, paste a .csv/.xlsx path. "
        "You can also ask what checks I run before correlation."
    )


def _runtime_error_fallback_message(*, agent: str, user_message: str, error: Exception) -> str:
    if _is_provider_connection_error(error):
        if agent == "analyst":
            return (
                "Local LLM runtime is not reachable at the configured endpoint. "
                "Start it with `relaytic setup-local-llm` (or launch your local provider), "
                "then retry. I can still run deterministic ingestion/analysis if you paste a "
                ".csv/.xlsx path."
            )
        return (
            "Local LLM runtime is not reachable at the configured endpoint. "
            "Start it with `relaytic setup-local-llm` (or launch your local provider) and retry."
        )
    if agent == "analyst":
        return (
            "I hit an internal runtime error in this step. "
            "The session is still active; you can retry, change inputs, or use /reset."
        )
    return "I hit an internal runtime error. Please retry."


def _looks_like_llm_failure_message(message: str) -> bool:
    lowered = message.lower()
    return (
        "local llm runtime is not reachable" in lowered
        or ("provider connection error" in lowered and "http" in lowered)
        or "i hit an internal runtime error. please retry." in lowered
        or "i hit an internal runtime error" in lowered
        or "i hit an internal runtime error in this step" in lowered
        or "session is still active; you can retry" in lowered
    )


def _invoke_agent_once_with_recovery(
    *,
    agent: str,
    user_message: str,
    context: dict[str, Any],
    config_path: str | None,
) -> dict[str, Any]:
    try:
        return run_local_agent_once(
            agent=agent,
            user_message=user_message,
            context=context,
            config_path=config_path,
        )
    except Exception as exc:
        if not _is_provider_connection_error(exc):
            raise
        # Best effort: start/check local runtime, then retry exactly once.
        try:
            setup_local_llm(
                config_path=config_path,
                provider=None,
                profile_name=None,
                model=None,
                endpoint=None,
                install_provider=False,
                start_runtime=True,
                pull_model=False,
                download_model=False,
                llama_model_path=None,
                llama_model_url=None,
                timeout_seconds=30,
            )
        except Exception:
            pass
        return run_local_agent_once(
            agent=agent,
            user_message=user_message,
            context=context,
            config_path=config_path,
        )


def _is_provider_connection_error(error: Exception) -> bool:
    lowered = str(error).lower()
    markers = (
        "provider connection error",
        "provider request timed out",
        "connection refused",
        "winerror 10061",
        "winerror 10060",
        "failed to establish a new connection",
        "timed out",
        "timeout",
    )
    return any(marker in lowered for marker in markers)


def _recent_user_prompts(*, session_messages: list[dict[str, str]], limit: int) -> list[str]:
    collected: list[str] = []
    for item in reversed(session_messages):
        if str(item.get("role", "")).strip().lower() != "user":
            continue
        text = str(item.get("content", "")).strip()
        if not text:
            continue
        collected.append(text)
        if len(collected) >= max(1, int(limit)):
            break
    collected.reverse()
    return collected


def _looks_like_small_talk(text: str) -> bool:
    normalized = text.strip().lower()
    if not normalized:
        return False
    if _is_simple_greeting(normalized):
        return True
    phrases = {
        "how are you",
        "who are you",
        "what can you do",
        "thank you",
        "thanks",
    }
    if any(phrase in normalized for phrase in phrases):
        return True
    if normalized.endswith("?") and not normalized.startswith("sig_"):
        return True
    return False


if __name__ == "__main__":
    sys.exit(main())


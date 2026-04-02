from __future__ import annotations

import json
from pathlib import Path

from relaytic.release_safety import run_release_safety_scan


def test_release_safety_scan_flags_machine_path_leak(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle_machine_path"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "README.md").write_text(
        "Bundle contents\n\nPath leak: C:\\Users\\someone\\secrets\\demo.txt\n",
        encoding="utf-8",
    )

    result = run_release_safety_scan(
        target_path=bundle_dir,
        state_dir=tmp_path / "state_machine_path",
    )
    bundle = result.bundle.to_dict()

    assert bundle["release_safety_scan"]["status"] == "error"
    assert bundle["sensitive_string_audit"]["finding_count"] >= 1
    assert any(item["rule_id"] == "windows_user_path" for item in bundle["sensitive_string_audit"]["findings"])


def test_release_safety_scan_flags_source_map_file(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle_source_map"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "app.js").write_text("console.log('ok');\n", encoding="utf-8")
    (bundle_dir / "app.js.map").write_text('{"version":3,"sources":["app.ts"]}', encoding="utf-8")

    result = run_release_safety_scan(
        target_path=bundle_dir,
        state_dir=tmp_path / "state_source_map",
    )
    bundle = result.bundle.to_dict()

    assert bundle["release_safety_scan"]["status"] == "error"
    assert bundle["source_map_audit"]["finding_count"] == 1
    assert bundle["source_map_audit"]["findings"][0]["path"] == "app.js.map"


def test_release_safety_scan_attests_clean_bundle_and_includes_host_bundle_and_docs(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle_clean"
    (bundle_dir / ".claude" / "agents").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "docs").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "README.md").write_text("Relaytic release bundle\n", encoding="utf-8")
    (bundle_dir / ".claude" / "agents" / "relaytic.md").write_text("Agent host bundle\n", encoding="utf-8")
    (bundle_dir / "docs" / "guide.md").write_text("User guide\n", encoding="utf-8")

    state_dir = tmp_path / "state_clean"
    result = run_release_safety_scan(target_path=bundle_dir, state_dir=state_dir)
    bundle = result.bundle.to_dict()

    assert bundle["release_safety_scan"]["status"] == "ok"
    assert bundle["release_safety_scan"]["safe_to_ship"] is True
    assert bundle["distribution_manifest"]["host_bundle_paths"] == [".claude/agents/relaytic.md"]
    assert "docs/guide.md" in bundle["distribution_manifest"]["docs_paths"]
    assert (state_dir / "artifact_attestation.json").exists()


def test_release_safety_scan_flags_internal_specs_in_distribution_bundle(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle_drift"
    (bundle_dir / "docs" / "specs").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "docs" / "specs" / "workspace_lifecycle.md").write_text("internal spec\n", encoding="utf-8")

    result = run_release_safety_scan(
        target_path=bundle_dir,
        state_dir=tmp_path / "state_drift",
    )
    bundle = result.bundle.to_dict()

    assert bundle["release_safety_scan"]["status"] == "error"
    assert bundle["packaging_regression_report"]["finding_count"] >= 1
    assert any(item["rule_id"] == "product_spec_internal" for item in bundle["packaging_regression_report"]["findings"])

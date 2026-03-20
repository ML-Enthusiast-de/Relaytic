from pathlib import Path

import yaml

from relaytic.policies import load_policy, write_resolved_policy


def test_load_policy_wraps_explicit_config(tmp_path: Path) -> None:
    config = tmp_path / "policy.yaml"
    config.write_text("project:\n  name: relaytic-test\nprivacy:\n  local_only: true\n", encoding="utf-8")

    resolved = load_policy(config)

    assert resolved.schema_version == "relaytic.policy.v1"
    assert resolved.source_format == "legacy_top_level"
    assert resolved.policy["mandate"]["enabled"] is True
    assert resolved.policy["context"]["require_provenance"] is True
    assert resolved.source_path.endswith("policy.yaml")


def test_write_resolved_policy_writes_yaml(tmp_path: Path) -> None:
    config = tmp_path / "policy.yaml"
    config.write_text("project:\n  name: relaytic-test\n", encoding="utf-8")
    output = tmp_path / "artifacts" / "policy_resolved.yaml"

    path = write_resolved_policy(output, path=config)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert path == output
    assert payload["schema_version"] == "relaytic.policy.v1"
    assert payload["policy"]["optimization"]["objective"] == "best_robust_pareto_front"
    assert payload["source_format"] == "legacy_top_level"


def test_load_policy_raises_for_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"
    try:
        load_policy(missing)
    except FileNotFoundError:
        return
    raise AssertionError("Expected FileNotFoundError for missing policy file.")


def test_load_policy_accepts_canonical_policy_shape(tmp_path: Path) -> None:
    config = tmp_path / "canonical.yaml"
    config.write_text(
        "policy:\n  mandate:\n    enabled: false\n  context:\n    enabled: true\n",
        encoding="utf-8",
    )

    resolved = load_policy(config)

    assert resolved.source_format == "canonical"
    assert resolved.policy["mandate"]["enabled"] is False


def test_load_policy_maps_top_level_autonomy_and_intelligence_controls(tmp_path: Path) -> None:
    config = tmp_path / "legacy_extended.yaml"
    config.write_text(
        "\n".join(
            [
                "autonomy:",
                "  execution_mode: autonomous",
                "  allow_auto_run: true",
                "  max_followup_rounds: 2",
                "  max_branches_per_round: 3",
                "intelligence:",
                "  enabled: true",
                "  intelligence_mode: advisory_local_llm",
                "  allow_frontier_llm: false",
            ]
        ),
        encoding="utf-8",
    )

    resolved = load_policy(config)

    assert resolved.source_format == "legacy_top_level"
    assert resolved.policy["autonomy"]["execution_mode"] == "autonomous"
    assert resolved.policy["autonomy"]["max_followup_rounds"] == 2
    assert resolved.policy["autonomy"]["max_branches_per_round"] == 3
    assert resolved.policy["intelligence"]["enabled"] is True
    assert resolved.policy["intelligence"]["intelligence_mode"] == "advisory_local_llm"

import json

from relaytic.integrations import (
    build_integration_inventory,
    build_integration_self_check_report,
    render_integration_inventory_markdown,
)
from relaytic.ui.cli import main


def test_build_integration_inventory_exposes_stable_shape() -> None:
    payload = build_integration_inventory()

    assert payload["integration_count"] >= 8
    assert payload["installed_count"] >= 0
    assert isinstance(payload["installed_keys"], list)
    assert any(item["key"] == "scikit_learn" for item in payload["integrations"])
    assert any(item["key"] == "pandera" for item in payload["integrations"])
    assert any(item["wired_surfaces"] for item in payload["integrations"] if item["key"] == "pandera")


def test_render_integration_inventory_markdown_includes_relaytic_guidance() -> None:
    payload = build_integration_inventory()
    rendered = render_integration_inventory_markdown(payload["integrations"])

    assert "# Relaytic Optional Integrations" in rendered
    assert "explicit adapters" in rendered
    assert "scikit-learn" in rendered


def test_cli_integrations_show_supports_json_output(capsys) -> None:
    assert main(["integrations", "show", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["integration_count"] >= 8
    assert any(item["key"] == "scikit_learn" for item in payload["integrations"])


def test_build_integration_self_check_report_exposes_stable_shape() -> None:
    payload = build_integration_self_check_report()

    assert payload["check_count"] >= 5
    assert payload["compatible_count"] >= 0
    assert any(item["integration"] == "scikit_learn" for item in payload["checks"])


def test_cli_integrations_self_check_supports_json_output(capsys) -> None:
    assert main(["integrations", "self-check", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["check_count"] >= 5
    assert any(item["integration"] == "scikit_learn" for item in payload["checks"])

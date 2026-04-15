import os
import sys
from pathlib import Path

import pytest


pytest_plugins = ["tests.push_smoke_fixtures"]


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

for module_name in list(sys.modules):
    if module_name == "corr2surrogate" or module_name.startswith("corr2surrogate."):
        sys.modules.pop(module_name, None)

os.environ.setdefault("RELAYTIC_SEARCH_BUDGET_PROFILE", "test")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        nodeid = item.nodeid.replace("\\", "/")
        if "tests/test_push_smoke.py" in nodeid:
            item.add_marker(pytest.mark.smoke)
            item.add_marker(pytest.mark.prepush)
        elif "tests/test_push_prepush.py" in nodeid:
            item.add_marker(pytest.mark.prepush)
        elif any(
            token in nodeid
            for token in (
                "tests/test_architecture_routing.py",
                "tests/test_assist_agents.py",
                "tests/test_hpo_loop.py",
                "tests/test_operating_points.py",
                "tests/test_model_training_candidates.py",
                "tests/test_planning_agents.py",
                "tests/test_search_agents.py",
                "tests/test_temporal_engine.py",
                "tests/test_cli_slice15h.py",
                "tests/test_cli_slice15i.py",
                "tests/test_cli_slice15j.py",
                "tests/test_cli_slice15k.py",
                "tests/test_cli_slice15l.py",
            )
        ):
            item.add_marker(pytest.mark.prepush)

        if any(
            token in nodeid
            for token in (
                "tests/test_external_agent_readiness.py",
                "tests/test_interoperability_mcp.py",
                "tests/test_cli_slice12b.py",
                "tests/test_cli_slice13.py",
                "tests/test_cli_slice13c.py",
                "tests/test_paper_benchmark_pack.py",
                "tests/test_temporal_benchmark_pack.py",
            )
        ):
            item.add_marker(pytest.mark.slow)

        if any(
            token in nodeid
            for token in (
                "tests/test_domain_datasets.py",
                "tests/test_paper_benchmark_pack.py",
                "tests/test_temporal_benchmark_pack.py",
            )
        ):
            item.add_marker(pytest.mark.network)

        if "tests/test_interoperability_mcp.py" in nodeid:
            item.add_marker(pytest.mark.mcp)

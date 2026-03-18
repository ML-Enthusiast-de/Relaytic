"""Optional third-party integration inventory for Relaytic."""

from .imbalanced_learn_adapter import (
    run_resampled_logistic_challenger,
    self_check_imbalanced_learn,
)
from .pandera_adapter import self_check_pandera, validate_frame_contract
from .pyod_adapter import run_pyod_anomaly_challenger, self_check_pyod
from .registry import (
    OptionalIntegration,
    build_integration_inventory,
    build_integration_self_check_report,
    collect_optional_integrations,
    render_integration_inventory_markdown,
    render_integration_self_check_markdown,
)
from .sklearn_adapter import self_check_sklearn
from .statsmodels_adapter import (
    compute_regression_residual_diagnostics,
    self_check_statsmodels,
)

__all__ = [
    "OptionalIntegration",
    "build_integration_inventory",
    "build_integration_self_check_report",
    "collect_optional_integrations",
    "render_integration_inventory_markdown",
    "render_integration_self_check_markdown",
    "validate_frame_contract",
    "compute_regression_residual_diagnostics",
    "run_resampled_logistic_challenger",
    "run_pyod_anomaly_challenger",
    "self_check_sklearn",
    "self_check_pandera",
    "self_check_statsmodels",
    "self_check_imbalanced_learn",
    "self_check_pyod",
]

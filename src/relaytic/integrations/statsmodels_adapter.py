"""statsmodels-backed residual diagnostics for evidence audit."""

from __future__ import annotations

from typing import Any

import numpy as np

from .runtime import base_integration_result, import_optional_module


def compute_regression_residual_diagnostics(
    *,
    y_true: list[float] | np.ndarray,
    y_pred: list[float] | np.ndarray,
    surface: str = "evidence.audit",
) -> dict[str, Any]:
    """Compute lightweight residual diagnostics through statsmodels if available."""
    stattools = import_optional_module("statsmodels.stats.stattools")
    if stattools is None:
        return base_integration_result(
            integration="statsmodels",
            package_name="statsmodels",
            surface=surface,
            status="not_installed",
            compatible=False,
            notes=["statsmodels is not installed locally; residual diagnostics were skipped."],
        )
    jarque_bera = getattr(stattools, "jarque_bera", None)
    durbin_watson = getattr(stattools, "durbin_watson", None)
    if jarque_bera is None or durbin_watson is None:
        return base_integration_result(
            integration="statsmodels",
            package_name="statsmodels",
            surface=surface,
            status="incompatible",
            compatible=False,
            notes=["statsmodels is installed but the expected residual-diagnostics API is unavailable."],
        )
    truth = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    if truth.size != pred.size or truth.size < 8:
        return base_integration_result(
            integration="statsmodels",
            package_name="statsmodels",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["Residual diagnostics need at least 8 aligned rows."],
            details={"row_count": int(min(truth.size, pred.size))},
        )
    residuals = truth - pred
    try:
        jb_output = jarque_bera(residuals)
        jb_stat = float(jb_output[0])
        jb_pvalue = float(jb_output[1])
        dw_stat = float(durbin_watson(residuals))
    except Exception as exc:
        return base_integration_result(
            integration="statsmodels",
            package_name="statsmodels",
            surface=surface,
            status="error",
            compatible=False,
            notes=[f"statsmodels diagnostics failed: {exc}"],
        )
    findings: list[dict[str, Any]] = []
    if jb_pvalue < 0.05:
        findings.append(
            {
                "severity": "medium",
                "title": "Residual normality is weak.",
                "detail": f"Jarque-Bera p-value is {jb_pvalue:.4f}; residuals are unlikely to be Gaussian.",
                "source": "statsmodels",
            }
        )
    if abs(dw_stat - 2.0) >= 0.6:
        findings.append(
            {
                "severity": "medium",
                "title": "Residual autocorrelation is visible.",
                "detail": f"Durbin-Watson statistic is {dw_stat:.3f}, far from the no-autocorrelation center of 2.0.",
                "source": "statsmodels",
            }
        )
    return base_integration_result(
        integration="statsmodels",
        package_name="statsmodels",
        surface=surface,
        status="ok",
        compatible=True,
        notes=["statsmodels residual diagnostics completed successfully."],
        details={
            "row_count": int(truth.size),
            "jarque_bera_stat": jb_stat,
            "jarque_bera_pvalue": jb_pvalue,
            "durbin_watson": dw_stat,
            "findings": findings,
        },
    )


def self_check_statsmodels() -> dict[str, Any]:
    """Run a tiny compatibility check against statsmodels residual diagnostics."""
    y_true = [0.1, 0.4, 0.3, 0.7, 0.9, 1.1, 1.2, 1.4, 1.5, 1.8]
    y_pred = [0.1, 0.35, 0.28, 0.65, 0.95, 1.05, 1.18, 1.36, 1.48, 1.82]
    return compute_regression_residual_diagnostics(
        y_true=y_true,
        y_pred=y_pred,
        surface="integrations.self_check",
    )

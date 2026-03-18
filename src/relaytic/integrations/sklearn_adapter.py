"""Minimal scikit-learn compatibility self-checks."""

from __future__ import annotations

from .runtime import base_integration_result, import_optional_module


def self_check_sklearn() -> dict[str, object]:
    """Run a tiny compatibility check against stable sklearn surfaces."""
    datasets = import_optional_module("sklearn.datasets")
    if datasets is None:
        return base_integration_result(
            integration="scikit_learn",
            package_name="scikit-learn",
            surface="integrations.self_check",
            status="not_installed",
            compatible=False,
            notes=["scikit-learn is not installed locally."],
        )
    load_diabetes = getattr(datasets, "load_diabetes", None)
    if load_diabetes is None:
        return base_integration_result(
            integration="scikit_learn",
            package_name="scikit-learn",
            surface="integrations.self_check",
            status="incompatible",
            compatible=False,
            notes=["`sklearn.datasets.load_diabetes` is unavailable."],
        )
    try:
        bundle = load_diabetes(as_frame=True)
        frame = getattr(bundle, "frame", None)
        row_count = int(len(frame)) if frame is not None else 0
    except Exception as exc:
        return base_integration_result(
            integration="scikit_learn",
            package_name="scikit-learn",
            surface="integrations.self_check",
            status="error",
            compatible=False,
            notes=[f"scikit-learn self-check failed: {exc}"],
        )
    return base_integration_result(
        integration="scikit_learn",
        package_name="scikit-learn",
        surface="integrations.self_check",
        status="ok",
        compatible=True,
        notes=["Public bundled dataset API is available."],
        details={"dataset": "load_diabetes", "row_count": row_count},
    )

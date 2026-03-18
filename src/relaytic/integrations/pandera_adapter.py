"""Pandera-backed validation helpers for intake and schema checks."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .runtime import base_integration_result, import_optional_module


def validate_frame_contract(
    *,
    frame: pd.DataFrame,
    required_columns: list[str] | None = None,
    target_column: str | None = None,
    surface: str = "intake",
) -> dict[str, Any]:
    """Validate a lightweight dataframe contract through Pandera if available."""
    pandera = import_optional_module("pandera.pandas")
    if pandera is None:
        pandera = import_optional_module("pandera")
    if pandera is None:
        return base_integration_result(
            integration="pandera",
            package_name="pandera",
            surface=surface,
            status="not_installed",
            compatible=False,
            notes=["Pandera is not installed locally; schema validation was skipped."],
        )
    schema_cls = getattr(pandera, "DataFrameSchema", None)
    check_cls = getattr(pandera, "Check", None)
    if schema_cls is None or check_cls is None:
        return base_integration_result(
            integration="pandera",
            package_name="pandera",
            surface=surface,
            status="incompatible",
            compatible=False,
            notes=["Pandera is installed but the expected DataFrameSchema/Check API is unavailable."],
        )

    required = [str(item) for item in (required_columns or []) if str(item).strip()]
    target = str(target_column or "").strip() or None
    checks = [
        check_cls(
            lambda df: len([str(column) for column in df.columns]) == len({str(column) for column in df.columns}),
            element_wise=False,
            error="duplicate_columns",
        )
    ]
    if required:
        checks.append(
            check_cls(
                lambda df, req=tuple(required): all(column in df.columns for column in req),
                element_wise=False,
                error="missing_required_columns",
            )
        )
    if target:
        checks.append(
            check_cls(
                lambda df, expected=target: expected in df.columns,
                element_wise=False,
                error=f"missing_target_column::{target}",
            )
        )
        checks.append(
            check_cls(
                lambda df, expected=target: (expected not in df.columns) or bool(df[expected].notna().any()),
                element_wise=False,
                error=f"empty_target_column::{target}",
            )
        )

    try:
        schema = schema_cls(checks=checks)
        schema.validate(frame.head(min(256, len(frame))), lazy=True)
    except Exception as exc:
        detail_text = str(exc).strip() or exc.__class__.__name__
        return base_integration_result(
            integration="pandera",
            package_name="pandera",
            surface=surface,
            status="validation_failed",
            compatible=True,
            notes=[detail_text],
            details={"required_columns": required, "target_column": target},
        )

    return base_integration_result(
        integration="pandera",
        package_name="pandera",
        surface=surface,
        status="ok",
        compatible=True,
        notes=["Pandera validated the dataframe contract successfully."],
        details={
            "required_columns": required,
            "target_column": target,
            "checked_rows": int(min(256, len(frame))),
        },
    )


def self_check_pandera() -> dict[str, Any]:
    """Run a tiny self-check against Pandera's high-level API."""
    frame = pd.DataFrame({"signal": [1.0, 2.0, 3.0], "target": [0, 1, 0]})
    return validate_frame_contract(
        frame=frame,
        required_columns=["signal", "target"],
        target_column="target",
        surface="integrations.self_check",
    )

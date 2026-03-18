"""Optional integration inventory for mature OSS capabilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib import metadata, util
from typing import Any

from .runtime import base_integration_result


@dataclass(frozen=True)
class OptionalIntegration:
    """Describes one optional third-party capability Relaytic can adopt."""

    key: str
    display_name: str
    package_name: str
    import_name: str
    category: str
    status: str
    version: str | None
    intended_uses: tuple[str, ...]
    agent_touchpoints: tuple[str, ...]
    wired_surfaces: tuple[str, ...]
    docs_url: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["intended_uses"] = list(self.intended_uses)
        payload["agent_touchpoints"] = list(self.agent_touchpoints)
        payload["wired_surfaces"] = list(self.wired_surfaces)
        return payload


_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "key": "scikit_learn",
        "display_name": "scikit-learn",
        "package_name": "scikit-learn",
        "import_name": "sklearn",
        "category": "baselines_and_datasets",
        "intended_uses": (
            "reference baselines",
            "public dataset fixtures",
            "preprocessing and calibration primitives",
            "metric parity checks",
        ),
        "agent_touchpoints": ("planning", "evidence", "benchmarks", "tests"),
        "wired_surfaces": ("tests.public_datasets", "integrations.self_check"),
        "docs_url": "https://scikit-learn.org/stable/",
        "notes": (
            "Use for datasets, mature ML primitives, and benchmark parity. Do not let it replace "
            "Relaytic's orchestration, judgment, or artifact contract."
        ),
    },
    {
        "key": "imbalanced_learn",
        "display_name": "imbalanced-learn",
        "package_name": "imbalanced-learn",
        "import_name": "imblearn",
        "category": "rare_event_modeling",
        "intended_uses": (
            "resampling challengers",
            "class imbalance experiments",
            "rare-event calibration comparisons",
        ),
        "agent_touchpoints": ("planning", "evidence", "lifecycle"),
        "wired_surfaces": ("evidence.challenger", "integrations.self_check"),
        "docs_url": "https://imbalanced-learn.org/stable/",
        "notes": "Best used as an optional challenger or ablation tool for fraud and anomaly routes.",
    },
    {
        "key": "statsmodels",
        "display_name": "statsmodels",
        "package_name": "statsmodels",
        "import_name": "statsmodels",
        "category": "diagnostics_and_classical_models",
        "intended_uses": (
            "residual diagnostics",
            "classical statistical baselines",
            "uncertainty and calibration checks",
            "time-series diagnostics",
        ),
        "agent_touchpoints": ("investigation", "evidence", "lifecycle"),
        "wired_surfaces": ("evidence.audit", "integrations.self_check"),
        "docs_url": "https://www.statsmodels.org/stable/",
        "notes": "Strong fit for diagnostics and sanity-check baselines where interpretability matters.",
    },
    {
        "key": "pandera",
        "display_name": "Pandera",
        "package_name": "pandera",
        "import_name": "pandera",
        "category": "schema_validation",
        "intended_uses": (
            "dataframe schema validation",
            "artifact input guards",
            "operator and agent payload validation",
        ),
        "agent_touchpoints": ("intake", "foundation", "execution"),
        "wired_surfaces": ("intake", "integrations.self_check"),
        "docs_url": "https://pandera.readthedocs.io/en/stable/",
        "notes": "Good for hardening contracts without building a custom schema DSL.",
    },
    {
        "key": "pyod",
        "display_name": "PyOD",
        "package_name": "pyod",
        "import_name": "pyod",
        "category": "anomaly_detection",
        "intended_uses": (
            "anomaly challengers",
            "outlier baselines",
            "rare-event route comparisons",
        ),
        "agent_touchpoints": ("planning", "evidence", "benchmarks"),
        "wired_surfaces": ("evidence.challenger", "integrations.self_check"),
        "docs_url": "https://pyod.readthedocs.io/en/latest/",
        "notes": "Useful when anomaly detection needs stronger breadth than a hand-rolled challenger set.",
    },
    {
        "key": "featuretools",
        "display_name": "Featuretools",
        "package_name": "featuretools",
        "import_name": "featuretools",
        "category": "feature_engineering",
        "intended_uses": (
            "relational feature synthesis",
            "aggregated history features",
            "entity-centric candidate features",
        ),
        "agent_touchpoints": ("investigation", "planning"),
        "wired_surfaces": (),
        "docs_url": "https://docs.featuretools.com/en/stable/",
        "notes": "Best adopted through explicit feature provenance so generated features stay auditable.",
    },
    {
        "key": "tsfresh",
        "display_name": "tsfresh",
        "package_name": "tsfresh",
        "import_name": "tsfresh",
        "category": "time_series_features",
        "intended_uses": (
            "time-series feature extraction",
            "lag-window summarization",
            "sensor-pattern challengers",
        ),
        "agent_touchpoints": ("investigation", "planning", "benchmarks"),
        "wired_surfaces": (),
        "docs_url": "https://tsfresh.readthedocs.io/en/stable/",
        "notes": "A targeted accelerator for time-series feature breadth, not a replacement for route judgment.",
    },
    {
        "key": "sktime",
        "display_name": "sktime",
        "package_name": "sktime",
        "import_name": "sktime",
        "category": "time_series_routes",
        "intended_uses": (
            "forecasting baselines",
            "time-series classification baselines",
            "reference route parity",
        ),
        "agent_touchpoints": ("planning", "evidence", "benchmarks"),
        "wired_surfaces": (),
        "docs_url": "https://www.sktime.net/en/stable/",
        "notes": "Strong candidate for the later forecasting and panel-data benchmark track.",
    },
    {
        "key": "river",
        "display_name": "River",
        "package_name": "river",
        "import_name": "river",
        "category": "streaming_and_drift",
        "intended_uses": (
            "online learning baselines",
            "stream drift detection",
            "incremental anomaly monitoring",
        ),
        "agent_touchpoints": ("lifecycle", "monitoring", "memory"),
        "wired_surfaces": (),
        "docs_url": "https://riverml.xyz/latest/",
        "notes": "Best reserved for streaming slices where incremental updates become a first-class concern.",
    },
    {
        "key": "shap",
        "display_name": "SHAP",
        "package_name": "shap",
        "import_name": "shap",
        "category": "explainability",
        "intended_uses": (
            "post-hoc explanations",
            "challenger diagnosis",
            "operator-facing attribution views",
        ),
        "agent_touchpoints": ("evidence", "completion", "reporting"),
        "wired_surfaces": (),
        "docs_url": "https://shap.readthedocs.io/en/latest/",
        "notes": "Use selectively. Explanations should enrich evidence artifacts, not become the decision source of truth.",
    },
    {
        "key": "evidently",
        "display_name": "Evidently",
        "package_name": "evidently",
        "import_name": "evidently",
        "category": "monitoring_and_reports",
        "intended_uses": (
            "drift reports",
            "data quality monitoring",
            "dashboard-oriented audit views",
        ),
        "agent_touchpoints": ("lifecycle", "reporting"),
        "wired_surfaces": (),
        "docs_url": "https://docs.evidentlyai.com/",
        "notes": "Useful for richer report surfaces, but Relaytic should keep canonical judgments in its own artifacts.",
    },
)


def collect_optional_integrations() -> list[OptionalIntegration]:
    """Return the current optional integration inventory with local availability."""
    items: list[OptionalIntegration] = []
    for item in _CATALOG:
        import_name = str(item["import_name"])
        package_name = str(item["package_name"])
        installed = util.find_spec(import_name) is not None
        version: str | None = None
        if installed:
            try:
                version = metadata.version(package_name)
            except metadata.PackageNotFoundError:
                version = None
        items.append(
            OptionalIntegration(
                key=str(item["key"]),
                display_name=str(item["display_name"]),
                package_name=package_name,
                import_name=import_name,
                category=str(item["category"]),
                status="installed" if installed else "not_installed",
                version=version,
                intended_uses=tuple(item["intended_uses"]),
                agent_touchpoints=tuple(item["agent_touchpoints"]),
                wired_surfaces=tuple(item.get("wired_surfaces", ())),
                docs_url=str(item["docs_url"]),
                notes=str(item["notes"]),
            )
        )
    return items


def build_integration_inventory() -> dict[str, Any]:
    """Build a stable machine-readable integration summary."""
    integrations = collect_optional_integrations()
    installed = [item for item in integrations if item.status == "installed"]
    return {
        "integration_count": len(integrations),
        "installed_count": len(installed),
        "installed_keys": [item.key for item in installed],
        "integrations": [item.to_dict() for item in integrations],
    }


def render_integration_inventory_markdown(items: list[OptionalIntegration] | list[dict[str, Any]]) -> str:
    """Render a concise human-readable inventory."""
    normalized: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, OptionalIntegration):
            normalized.append(item.to_dict())
        else:
            normalized.append(dict(item))

    installed_count = sum(1 for item in normalized if str(item.get("status")) == "installed")
    lines = [
        "# Relaytic Optional Integrations",
        "",
        (
            f"Installed locally: `{installed_count}` of `{len(normalized)}`. "
            "These libraries are accelerators for baselines, diagnostics, validation, and feature breadth."
        ),
        "",
        "Relaytic should reuse them through explicit adapters and keep final judgment, provenance, and policy enforcement in native artifacts.",
        "",
    ]
    for item in normalized:
        version = str(item.get("version") or "n/a")
        uses = ", ".join(str(part) for part in item.get("intended_uses", []))
        touchpoints = ", ".join(str(part) for part in item.get("agent_touchpoints", []))
        wiring = ", ".join(str(part) for part in item.get("wired_surfaces", [])) or "not yet wired"
        lines.extend(
            [
                f"- `{item.get('display_name')}`: status=`{item.get('status')}`, version=`{version}`, category=`{item.get('category')}`.",
                f"  Uses: {uses}.",
                f"  Touchpoints: {touchpoints}.",
                f"  Wired: {wiring}.",
            ]
        )
    return "\n".join(lines) + "\n"


def build_integration_self_check_report() -> dict[str, Any]:
    """Run compatibility self-checks for wired optional integrations."""
    from .imbalanced_learn_adapter import self_check_imbalanced_learn
    from .pandera_adapter import self_check_pandera
    from .pyod_adapter import self_check_pyod
    from .sklearn_adapter import self_check_sklearn
    from .statsmodels_adapter import self_check_statsmodels

    checks = [
        _safe_self_check("scikit_learn", "scikit-learn", self_check_sklearn),
        _safe_self_check("pandera", "pandera", self_check_pandera),
        _safe_self_check("statsmodels", "statsmodels", self_check_statsmodels),
        _safe_self_check("imbalanced_learn", "imbalanced-learn", self_check_imbalanced_learn),
        _safe_self_check("pyod", "pyod", self_check_pyod),
    ]
    ok_count = sum(1 for item in checks if str(item.get("status", "")).strip() == "ok")
    compatible_count = sum(1 for item in checks if bool(item.get("compatible")))
    return {
        "check_count": len(checks),
        "ok_count": ok_count,
        "compatible_count": compatible_count,
        "checks": checks,
    }


def _safe_self_check(
    integration: str,
    package_name: str,
    check_fn: Any,
) -> dict[str, Any]:
    try:
        result = check_fn()
    except Exception as exc:
        return base_integration_result(
            integration=integration,
            package_name=package_name,
            surface="integrations.self_check",
            status="error",
            compatible=False,
            notes=[f"Integration self-check raised unexpectedly: {exc}"],
        )
    if isinstance(result, dict):
        return result
    return base_integration_result(
        integration=integration,
        package_name=package_name,
        surface="integrations.self_check",
        status="error",
        compatible=False,
        notes=["Integration self-check returned a non-dict payload."],
    )


def render_integration_self_check_markdown(report: dict[str, Any]) -> str:
    """Render a concise human-readable integration self-check report."""
    lines = [
        "# Relaytic Integration Self-Check",
        "",
        f"- Checks: `{report.get('check_count', 0)}`",
        f"- Compatible: `{report.get('compatible_count', 0)}`",
        f"- Passing: `{report.get('ok_count', 0)}`",
        "",
    ]
    for item in report.get("checks", []):
        notes = "; ".join(str(note) for note in item.get("notes", [])) or "no notes"
        lines.append(
            f"- `{item.get('integration')}`: status=`{item.get('status')}`, compatible=`{item.get('compatible')}`, version=`{item.get('version') or 'n/a'}`. {notes}"
        )
    return "\n".join(lines) + "\n"

from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd

import relaytic.integrations.sklearn_adapter as sklearn_adapter
from relaytic.integrations.imbalanced_learn_adapter import run_resampled_logistic_challenger
from relaytic.integrations.pandera_adapter import validate_frame_contract
from relaytic.integrations.pyod_adapter import run_pyod_anomaly_challenger
from relaytic.integrations.registry import build_integration_self_check_report
from relaytic.integrations.statsmodels_adapter import compute_regression_residual_diagnostics


def test_validate_frame_contract_returns_not_installed_when_pandera_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("relaytic.integrations.pandera_adapter.import_optional_module", lambda name: None)

    result = validate_frame_contract(
        frame=pd.DataFrame({"feature": [1.0, 2.0], "target": [0, 1]}),
        required_columns=["feature", "target"],
        target_column="target",
    )

    assert result["integration"] == "pandera"
    assert result["status"] == "not_installed"
    assert result["compatible"] is False


def test_statsmodels_adapter_returns_incompatible_when_expected_api_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        "relaytic.integrations.statsmodels_adapter.import_optional_module",
        lambda name: SimpleNamespace(),
    )

    result = compute_regression_residual_diagnostics(
        y_true=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
        y_pred=[0.1, 0.2, 0.29, 0.38, 0.52, 0.61, 0.71, 0.79],
    )

    assert result["integration"] == "statsmodels"
    assert result["status"] == "incompatible"
    assert result["compatible"] is False


def test_resampled_logistic_challenger_skips_cleanly_on_too_few_rows(monkeypatch) -> None:
    monkeypatch.setattr(
        "relaytic.integrations.imbalanced_learn_adapter.import_optional_module",
        lambda name: SimpleNamespace(
            RandomOverSampler=type("RandomOverSampler", (), {}),
            LogisticRegression=type("LogisticRegression", (), {}),
        )
        if name == "imblearn.over_sampling"
        else SimpleNamespace(LogisticRegression=type("LogisticRegression", (), {})),
    )

    frame = pd.DataFrame(
        {
            "amount_norm": [0.1, 0.2, 0.15, 0.82, 0.88, 0.9],
            "device_risk": [0.2, 0.15, 0.18, 0.91, 0.93, 0.95],
            "fraud_flag": [0, 0, 0, 1, 1, 1],
        }
    )

    result = run_resampled_logistic_challenger(
        frame=frame,
        feature_columns=["amount_norm", "device_risk"],
        target_column="fraud_flag",
        task_type="fraud_detection",
    )

    assert result["integration"] == "imbalanced_learn"
    assert result["status"] == "skipped"
    assert result["compatible"] is True


def test_pyod_challenger_skips_cleanly_on_too_few_rows(monkeypatch) -> None:
    monkeypatch.setenv("RELAYTIC_ALLOW_UNSTABLE_PYOD", "1")
    monkeypatch.setattr(
        "relaytic.integrations.pyod_adapter.import_optional_module",
        lambda name: SimpleNamespace(IForest=type("IForest", (), {})),
    )

    frame = pd.DataFrame(
        {
            "signal_a": [0.1, 0.15, 0.18, 0.82, 0.88, 0.9],
            "signal_b": [1.1, 1.2, 1.15, 2.9, 3.0, 3.1],
            "fault_flag": [0, 0, 0, 1, 1, 1],
        }
    )

    result = run_pyod_anomaly_challenger(
        frame=frame,
        feature_columns=["signal_a", "signal_b"],
        target_column="fault_flag",
        task_type="anomaly_detection",
    )

    assert result["integration"] == "pyod"
    assert result["status"] == "skipped"
    assert result["compatible"] is True


def test_pyod_challenger_is_guarded_on_windows_by_default(monkeypatch) -> None:
    monkeypatch.delenv("RELAYTIC_ALLOW_UNSTABLE_PYOD", raising=False)
    monkeypatch.setattr("relaytic.integrations.pyod_adapter.platform.system", lambda: "Windows")

    result = run_pyod_anomaly_challenger(
        frame=pd.DataFrame({"signal_a": [0.1] * 12, "signal_b": [1.0] * 12, "fault_flag": [0] * 12}),
        feature_columns=["signal_a", "signal_b"],
        target_column="fault_flag",
        task_type="anomaly_detection",
    )

    assert result["integration"] == "pyod"
    assert result["status"] == "guarded"
    assert result["compatible"] is False


def test_resampled_logistic_challenger_handles_all_nan_numeric_feature_without_runtime_warning(monkeypatch) -> None:
    class _FakeRandomOverSampler:
        def __init__(self, random_state: int = 0) -> None:
            self.random_state = random_state

        def fit_resample(self, X, y):
            return X, y

    class _FakeLogisticRegression:
        def __init__(self, max_iter: int = 400, solver: str = "liblinear") -> None:
            self.max_iter = max_iter
            self.solver = solver
            self.classes_ = np.asarray(["0", "1"])

        def fit(self, X, y):
            self.classes_ = np.asarray(sorted({str(item) for item in y}))
            return self

        def predict_proba(self, X):
            positive = np.clip(np.asarray(X[:, 1], dtype=float), 0.05, 0.95)
            return np.column_stack([1.0 - positive, positive])

    monkeypatch.setattr(
        "relaytic.integrations.imbalanced_learn_adapter.import_optional_module",
        lambda name: SimpleNamespace(RandomOverSampler=_FakeRandomOverSampler)
        if name == "imblearn.over_sampling"
        else SimpleNamespace(LogisticRegression=_FakeLogisticRegression),
    )

    frame = pd.DataFrame(
        {
            "amount_norm": [float("nan")] * 40,
            "device_risk": [0.05 + (index / 50.0) for index in range(40)],
            "fraud_flag": [0] * 30 + [1] * 10,
        }
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        result = run_resampled_logistic_challenger(
            frame=frame,
            feature_columns=["amount_norm", "device_risk"],
            target_column="fraud_flag",
            task_type="fraud_detection",
        )

    assert result["status"] == "ok"
    assert result["details"]["model_family"] == "imblearn_resampled_logistic"


def test_pyod_challenger_handles_all_nan_numeric_feature_without_runtime_warning(monkeypatch) -> None:
    class _FakeIForest:
        def __init__(self, contamination: float) -> None:
            self.contamination = contamination

        def fit(self, X):
            return self

        def decision_function(self, X):
            return np.linspace(0.1, 0.9, X.shape[0], dtype=float)

    monkeypatch.setenv("RELAYTIC_ALLOW_UNSTABLE_PYOD", "1")
    monkeypatch.setattr(
        "relaytic.integrations.pyod_adapter.import_optional_module",
        lambda name: SimpleNamespace(IForest=_FakeIForest),
    )

    frame = pd.DataFrame(
        {
            "signal_a": [float("nan")] * 40,
            "signal_b": [1.0 + (index / 20.0) for index in range(40)],
            "fault_flag": [0] * 30 + [1] * 10,
        }
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        result = run_pyod_anomaly_challenger(
            frame=frame,
            feature_columns=["signal_a", "signal_b"],
            target_column="fault_flag",
            task_type="anomaly_detection",
        )

    assert result["status"] == "ok"
    assert result["details"]["model_family"] == "pyod_iforest_anomaly"


def test_integration_self_check_report_degrades_gracefully_when_one_check_raises(monkeypatch) -> None:
    def _boom() -> dict[str, object]:
        raise RuntimeError("forced self-check failure")

    monkeypatch.setattr(sklearn_adapter, "self_check_sklearn", _boom)

    report = build_integration_self_check_report()

    assert report["check_count"] >= 5
    assert any(item["integration"] == "scikit_learn" and item["status"] == "error" for item in report["checks"])

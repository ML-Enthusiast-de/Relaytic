import csv
import json
import pickle
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.analytics.task_detection import assess_task_profile, is_classification_task
from relaytic.ingestion import load_tabular_data
from relaytic.modeling.feature_pipeline import prepare_split_safe_feature_frames
from relaytic.modeling.normalization import MinMaxNormalizer
from relaytic.modeling.splitters import build_train_validation_test_split
from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


class MemorizedClassifier:
    def fit(self, features: np.ndarray, labels: np.ndarray) -> "MemorizedClassifier":
        self.classes_ = sorted({str(item) for item in labels})
        self._lookup = {tuple(float(value) for value in row): str(label) for row, label in zip(features, labels)}
        return self

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        class_to_index = {label: index for index, label in enumerate(self.classes_)}
        probabilities = np.full((features.shape[0], len(self.classes_)), 1.0 / max(1, len(self.classes_)), dtype=float)
        for row_index, row in enumerate(features):
            label = self._lookup.get(tuple(float(value) for value in row))
            if label is None:
                continue
            probabilities[row_index, :] = 0.0
            probabilities[row_index, class_to_index[label]] = 1.0
        return probabilities


def test_cli_benchmark_run_supports_imported_incumbents_and_honest_parity(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "incumbent_parity"
    data_path = write_public_breast_cancer_dataset(tmp_path / "breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the provided features and benchmark against strong references.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    target_column = str(plan["target_column"])
    feature_columns = [str(item) for item in plan.get("feature_columns", [])]

    model_path = _write_memorized_incumbent_model(
        path=tmp_path / "memorized_incumbent.pkl",
        data_path=data_path,
        plan=plan,
    )
    ruleset_path = _write_weak_scorecard(
        path=tmp_path / "legacy_scorecard.json",
        feature_columns=feature_columns,
    )
    predictions_path = _write_test_only_predictions(
        path=tmp_path / "vendor_predictions.csv",
        data_path=data_path,
        target_column=target_column,
        plan=plan,
    )

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--incumbent-path",
            str(ruleset_path),
            "--incumbent-kind",
            "ruleset",
            "--incumbent-name",
            "legacy_scorecard",
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    weak_payload = json.loads(capsys.readouterr().out)
    assert weak_payload["bundle"]["external_challenger_evaluation"]["evaluation_mode"] == "ruleset_execution"
    assert weak_payload["bundle"]["incumbent_parity_report"]["parity_status"] == "beats_incumbent"
    assert weak_payload["bundle"]["beat_target_contract"]["contract_state"] == "met"

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--incumbent-path",
            str(model_path),
            "--incumbent-kind",
            "model",
            "--incumbent-name",
            "memorized_incumbent",
            "--trust-incumbent-model",
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    strong_payload = json.loads(capsys.readouterr().out)
    assert strong_payload["bundle"]["external_challenger_evaluation"]["evaluation_mode"] == "local_model_execution"
    assert strong_payload["bundle"]["incumbent_parity_report"]["parity_status"] == "below_incumbent"
    assert strong_payload["bundle"]["beat_target_contract"]["contract_state"] == "unmet"
    assert strong_payload["benchmark"]["incumbent_stronger"] is True

    assert main(["benchmark", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["benchmark"]["incumbent_name"] == "memorized_incumbent"
    assert show_payload["benchmark"]["beat_target_state"] == "unmet"
    assert show_payload["benchmark"]["incumbent_parity_status"] == "below_incumbent"

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--incumbent-path",
            str(predictions_path),
            "--incumbent-kind",
            "predictions",
            "--incumbent-name",
            "vendor_predictions",
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    prediction_payload = json.loads(capsys.readouterr().out)
    assert prediction_payload["bundle"]["external_challenger_evaluation"]["evaluation_mode"] == "prediction_replay"
    assert prediction_payload["bundle"]["external_challenger_evaluation"]["reduced_claim"] is True
    assert prediction_payload["bundle"]["incumbent_parity_report"]["parity_status"] == "reduced_claim"
    assert prediction_payload["bundle"]["beat_target_contract"]["contract_state"] == "reduced_claim"

    for filename in (
        "reference_approach_matrix.json",
        "benchmark_gap_report.json",
        "benchmark_parity_report.json",
        "external_challenger_manifest.json",
        "external_challenger_evaluation.json",
        "incumbent_parity_report.json",
        "beat_target_contract.json",
    ):
        assert (run_dir / filename).exists(), filename


def test_cli_autonomy_consumes_unmet_beat_target_contract(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "incumbent_autonomy"
    data_path = write_public_breast_cancer_dataset(tmp_path / "breast_cancer_autonomy.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the provided features and benchmark against strong references.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    model_path = _write_memorized_incumbent_model(
        path=tmp_path / "strong_incumbent.pkl",
        data_path=data_path,
        plan=plan,
    )

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--incumbent-path",
            str(model_path),
            "--incumbent-kind",
            "model",
            "--incumbent-name",
            "strong_incumbent",
            "--trust-incumbent-model",
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    benchmark_payload = json.loads(capsys.readouterr().out)
    assert benchmark_payload["bundle"]["beat_target_contract"]["contract_state"] == "unmet"
    for filename in ("retrain_decision.json", "recalibration_decision.json"):
        path = run_dir / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["action"] = "hold"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert main(
        [
            "autonomy",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    autonomy_payload = json.loads(capsys.readouterr().out)
    assert autonomy_payload["status"] == "ok"
    assert autonomy_payload["autonomy"]["selected_action"] == "expand_challenger_portfolio"
    assert autonomy_payload["bundle"]["autonomy_loop_state"]["selected_action"] == "expand_challenger_portfolio"


def test_cli_benchmark_blocks_executable_incumbent_models_by_default(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "incumbent_blocked"
    data_path = write_public_breast_cancer_dataset(tmp_path / "blocked_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the provided features and benchmark against strong references.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    model_path = _write_memorized_incumbent_model(
        path=tmp_path / "blocked_incumbent.pkl",
        data_path=data_path,
        plan=plan,
    )

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--incumbent-path",
            str(model_path),
            "--incumbent-kind",
            "model",
            "--incumbent-name",
            "blocked_incumbent",
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    blocked_payload = json.loads(capsys.readouterr().out)
    evaluation = blocked_payload["bundle"]["external_challenger_evaluation"]
    assert evaluation["status"] == "blocked"
    assert "unsafe_model_deserialization_blocked" in evaluation["reason_codes"]
    assert "blocked by default" in evaluation["summary"]


def _write_memorized_incumbent_model(
    *,
    path: Path,
    data_path: Path,
    plan: dict[str, object],
) -> Path:
    frame = load_tabular_data(str(data_path)).frame.copy()
    feature_columns = [str(item) for item in plan.get("feature_columns", [])]
    target_column = str(plan["target_column"])
    builder_handoff = dict(plan.get("builder_handoff") or {})
    task_profile = assess_task_profile(
        frame=frame,
        target_column=target_column,
        data_mode=str(plan.get("data_mode") or "steady_state"),
        task_type_hint=str(plan.get("task_type") or ""),
    )
    split = build_train_validation_test_split(
        n_rows=len(frame),
        data_mode=str(plan.get("data_mode") or task_profile.data_mode),
        task_type=task_profile.task_type,
        stratify_labels=frame[target_column] if is_classification_task(task_profile.task_type) else None,
    )
    split_frames = {
        "train": frame.iloc[split.train_indices].reset_index(drop=True),
        "validation": frame.iloc[split.validation_indices].reset_index(drop=True),
        "test": frame.iloc[split.test_indices].reset_index(drop=True),
    }
    prepared = prepare_split_safe_feature_frames(
        split_frames=split_frames,
        raw_feature_columns=feature_columns,
        target_column=target_column,
        missing_data_strategy=str(builder_handoff.get("missing_data_strategy", "fill_median")),
        fill_constant_value=None,
        task_type=task_profile.task_type,
    )
    prepared_frames = dict(prepared.get("frames", {}))
    model_feature_columns = [str(item) for item in prepared.get("model_feature_columns", [])]
    if bool(builder_handoff.get("normalize", True)):
        normalizer = MinMaxNormalizer()
        normalizer.fit(prepared_frames["train"], feature_columns=model_feature_columns)
        prepared_frames = {
            name: normalizer.transform_features(part)
            for name, part in prepared_frames.items()
        }
    all_features = np.vstack(
        [
            prepared_frames["train"][model_feature_columns].to_numpy(dtype=float),
            prepared_frames["validation"][model_feature_columns].to_numpy(dtype=float),
            prepared_frames["test"][model_feature_columns].to_numpy(dtype=float),
        ]
    )
    all_labels = np.concatenate(
        [
            prepared_frames["train"][target_column].astype(str).to_numpy(dtype=object),
            prepared_frames["validation"][target_column].astype(str).to_numpy(dtype=object),
            prepared_frames["test"][target_column].astype(str).to_numpy(dtype=object),
        ]
    )
    estimator = MemorizedClassifier().fit(
        all_features,
        all_labels,
    )
    with path.open("wb") as handle:
        pickle.dump({"estimator": estimator, "feature_columns": model_feature_columns}, handle)
    return path


def _write_weak_scorecard(*, path: Path, feature_columns: list[str]) -> Path:
    weights = {column: 0.0 for column in feature_columns[: min(5, len(feature_columns))]}
    payload = {
        "kind": "linear_scorecard",
        "weights": weights,
        "intercept": -50.0,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _write_test_only_predictions(
    *,
    path: Path,
    data_path: Path,
    target_column: str,
    plan: dict[str, object],
) -> Path:
    frame = load_tabular_data(str(data_path)).frame.copy()
    task_profile = assess_task_profile(
        frame=frame,
        target_column=target_column,
        data_mode=str(plan.get("data_mode") or "steady_state"),
        task_type_hint=str(plan.get("task_type") or ""),
    )
    split = build_train_validation_test_split(
        n_rows=len(frame),
        data_mode=str(plan.get("data_mode") or task_profile.data_mode),
        task_type=task_profile.task_type,
        stratify_labels=frame[target_column] if is_classification_task(task_profile.task_type) else None,
    )
    test_labels = frame.iloc[split.test_indices][target_column].astype(str).tolist()
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["prediction"])
        for label in test_labels:
            writer.writerow([label])
    return path

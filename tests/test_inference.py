from pathlib import Path

from relaytic.modeling.inference import run_inference_from_artifacts
from relaytic.orchestration.default_tools import build_default_registry


def test_inference_from_checkpoint_supports_regression_and_shift_diagnostics(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    train_path = tmp_path / "train_regression.csv"
    rows = ["x1,x2,y"]
    for idx in range(140):
        x1 = -1.0 + (2.0 * idx / 139.0)
        x2 = (idx % 6) / 5.0
        y = 1.7 * x1 + 0.3 * x2 + 0.15
        rows.append(f"{x1:.5f},{x2:.5f},{y:.5f}")
    train_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    trained = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(train_path),
            "target_column": "y",
            "feature_columns": ["x1", "x2"],
            "requested_model_family": "linear_ridge",
            "run_id": "inference_regression_train",
        },
    ).output

    infer_path = tmp_path / "infer_regression.csv"
    infer_rows = ["x1,x2,y"]
    for idx in range(36):
        x1 = 2.0 + (0.6 * idx / 35.0) if idx % 3 == 0 else (-0.8 + 1.6 * idx / 35.0)
        x2 = (idx % 4) / 3.0
        y = 1.7 * x1 + 0.3 * x2 + 0.15
        infer_rows.append(f"{x1:.5f},{x2:.5f},{y:.5f}")
    infer_path.write_text("\n".join(infer_rows), encoding="utf-8")

    payload = run_inference_from_artifacts(
        checkpoint_id=str(trained["checkpoint_id"]),
        data_path=str(infer_path),
    )
    assert payload["status"] == "ok"
    assert payload["prediction_count"] > 0
    assert payload["evaluation"]["available"] is True
    assert "r2" in payload["evaluation"]["metrics"]
    assert payload["uncertainty"]["status"] == "ok"
    assert payload["predictions_preview"][0]["prediction_lower_90"] <= payload["predictions_preview"][0]["prediction_upper_90"]
    assert payload["ood_summary"]["overall_ood_fraction"] > 0.0
    assert Path(payload["report_path"]).is_file()
    assert Path(payload["predictions_path"]).is_file()


def test_inference_from_run_dir_supports_classification_threshold_override(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    train_path = tmp_path / "train_classification.csv"
    rows = ["feature_a,feature_b,class_label"]
    for idx in range(120):
        a = idx / 119.0
        b = 1 if idx % 5 == 0 else 0
        label = 1 if (a > 0.6 or b == 1) else 0
        rows.append(f"{a:.5f},{b},{label}")
    train_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    trained = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(train_path),
            "target_column": "class_label",
            "feature_columns": ["feature_a", "feature_b"],
            "requested_model_family": "logistic_regression",
            "run_id": "inference_classification_train",
        },
    ).output

    infer_path = tmp_path / "infer_classification.csv"
    infer_rows = ["feature_a,feature_b,class_label"]
    for idx in range(60):
        a = idx / 59.0
        b = 1 if idx % 4 == 0 else 0
        label = 1 if (a > 0.58 or b == 1) else 0
        infer_rows.append(f"{a:.5f},{b},{label}")
    infer_path.write_text("\n".join(infer_rows), encoding="utf-8")

    payload = run_inference_from_artifacts(
        run_dir=str(trained["run_dir"]),
        data_path=str(infer_path),
        decision_threshold=0.35,
    )
    assert payload["status"] == "ok"
    assert payload["prediction_count"] > 0
    assert payload["decision_threshold_used"] == 0.35
    assert payload["evaluation"]["available"] is True
    assert "f1" in payload["evaluation"]["metrics"]
    assert payload["uncertainty"]["status"] == "ok"
    assert "low_confidence_fraction" in payload["uncertainty"]
    assert payload["predictions_preview"]


def test_inference_from_run_dir_supports_string_class_labels_and_bool_like_features(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    train_path = tmp_path / "train_string_classification.csv"
    rows = ["balance,duration,housing,loan,contact,term_deposit_flag"]
    for idx in range(180):
        balance = 500 + idx * 7
        duration = 60 + (idx % 40) * 9
        housing = "yes" if idx % 3 else "no"
        loan = "yes" if idx % 7 == 0 else "no"
        contact = "cellular" if idx % 4 else "telephone"
        label = "yes" if (duration > 240 or (housing == "no" and contact == "cellular")) else "no"
        rows.append(f"{balance},{duration},{housing},{loan},{contact},{label}")
    train_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    trained = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(train_path),
            "target_column": "term_deposit_flag",
            "feature_columns": ["balance", "duration", "housing", "loan", "contact"],
            "requested_model_family": "boosted_tree_classifier",
            "run_id": "inference_string_classification_train",
        },
    ).output

    infer_path = tmp_path / "infer_string_classification.csv"
    infer_rows = ["balance,duration,housing,loan,contact,term_deposit_flag"]
    for idx in range(80):
        balance = 700 + idx * 5
        duration = 80 + (idx % 35) * 11
        housing = "yes" if idx % 5 else "no"
        loan = "yes" if idx % 6 == 0 else "no"
        contact = "cellular" if idx % 3 else "telephone"
        label = "yes" if (duration > 250 or (housing == "no" and contact == "cellular")) else "no"
        infer_rows.append(f"{balance},{duration},{housing},{loan},{contact},{label}")
    infer_path.write_text("\n".join(infer_rows), encoding="utf-8")

    payload = run_inference_from_artifacts(
        run_dir=str(trained["run_dir"]),
        data_path=str(infer_path),
    )

    assert payload["status"] == "ok"
    assert payload["prediction_count"] > 0
    assert payload["evaluation"]["available"] is True
    assert "f1" in payload["evaluation"]["metrics"]
    assert payload["predictions_preview"]


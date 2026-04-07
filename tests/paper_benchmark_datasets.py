"""Paper-grade benchmark dataset catalog for optional Relaytic evaluation packs."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Callable

from tests.domain_datasets import (
    write_uci_ai4i_machine_failure_dataset,
    write_uci_bank_marketing_dataset,
    write_uci_concrete_strength_dataset,
    write_uci_credit_default_dataset,
    write_uci_dermatology_dataset,
    write_uci_dry_bean_dataset,
    write_uci_energy_efficiency_heating_dataset,
    write_uci_iranian_churn_dataset,
    write_uci_statlog_german_credit_dataset,
)
from tests.public_datasets import (
    write_public_breast_cancer_dataset,
    write_public_diabetes_dataset,
    write_public_wine_dataset,
)

DatasetWriter = Callable[[Path], Path]


@dataclass(frozen=True)
class PaperBenchmarkDatasetSpec:
    dataset_key: str
    family: str
    display_name: str
    source_name: str
    source_url: str
    writer: DatasetWriter
    target_column: str
    expected_task_types: tuple[str, ...]
    expected_rows: int
    objective_text: str
    benchmark_text: str
    why_chosen: tuple[str, ...]

    @property
    def pytest_id(self) -> str:
        return f"{self.family}:{self.dataset_key}"


PAPER_BENCHMARK_DATASETS: tuple[PaperBenchmarkDatasetSpec, ...] = (
    PaperBenchmarkDatasetSpec(
        dataset_key="sklearn_diabetes",
        family="regression",
        display_name="Diabetes",
        source_name="scikit-learn load_diabetes",
        source_url="https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html",
        writer=write_public_diabetes_dataset,
        target_column="disease_progression",
        expected_task_types=("regression",),
        expected_rows=442,
        objective_text="Predict disease_progression from the physiological measurement columns. Do everything on your own.",
        benchmark_text="Predict disease_progression from the physiological measurement columns, benchmark against strong references, and explain the route choice.",
        why_chosen=(
            "Classic small regression benchmark that keeps local runs fast and reproducible.",
            "Widely recognized by ML readers, so it works well as a sanity-check dataset in papers.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_concrete_strength",
        family="regression",
        display_name="Concrete Compressive Strength",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength",
        writer=write_uci_concrete_strength_dataset,
        target_column="concrete_strength",
        expected_task_types=("regression",),
        expected_rows=1030,
        objective_text="Predict concrete_strength from the process and material mix columns. Do everything on your own.",
        benchmark_text="Predict concrete_strength from the process and material mix columns, benchmark against strong references, and explain the winning route.",
        why_chosen=(
            "Nonlinear engineering regression benchmark that is common in tabular-method papers.",
            "Clean, medium-sized, and easy to cite from the primary UCI source.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_energy_efficiency",
        family="regression",
        display_name="Energy Efficiency (Heating Load)",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/242/energy+efficiency",
        writer=write_uci_energy_efficiency_heating_dataset,
        target_column="heating_load",
        expected_task_types=("regression",),
        expected_rows=768,
        objective_text="Predict heating_load from the building design columns. Do everything on your own.",
        benchmark_text="Predict heating_load from the building design columns, benchmark against strong references, and explain the selected route.",
        why_chosen=(
            "Popular structured regression benchmark with strong signal and a different domain than concrete or diabetes.",
            "Good paper complement because it is small enough for repeated runs but not toy-like.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="sklearn_breast_cancer",
        family="binary_classification",
        display_name="Breast Cancer Wisconsin Diagnostic",
        source_name="scikit-learn load_breast_cancer",
        source_url="https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html",
        writer=write_public_breast_cancer_dataset,
        target_column="diagnosis_flag",
        expected_task_types=("binary_classification",),
        expected_rows=569,
        objective_text="Classify diagnosis_flag from the measurement columns. Do everything on your own.",
        benchmark_text="Classify diagnosis_flag from the measurement columns, benchmark against strong references, and explain the route choice.",
        why_chosen=(
            "Canonical medical binary benchmark already familiar to many reviewers and engineers.",
            "Excellent low-friction baseline for verifying the full Relaytic loop before harder domains.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_bank_marketing",
        family="binary_classification",
        display_name="Bank Marketing",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/222/bank+marketing",
        writer=partial(write_uci_bank_marketing_dataset, max_rows=6000),
        target_column="term_deposit_flag",
        expected_task_types=("binary_classification",),
        expected_rows=6000,
        objective_text="Predict term_deposit_flag from the banking campaign and account columns. Do everything on your own.",
        benchmark_text="Predict term_deposit_flag from the banking campaign and account columns, benchmark against strong references, and explain the winning route.",
        why_chosen=(
            "Mixed-type tabular classification benchmark with real business semantics and moderate class imbalance.",
            "Stronger paper story than tiny toy datasets because it stresses preprocessing and route choice.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_statlog_german_credit",
        family="binary_classification",
        display_name="Statlog (German Credit Data)",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
        writer=write_uci_statlog_german_credit_dataset,
        target_column="credit_risk_flag",
        expected_task_types=("binary_classification",),
        expected_rows=1000,
        objective_text="Predict credit_risk_flag from the credit application columns. Do everything on your own.",
        benchmark_text="Predict credit_risk_flag from the credit application columns, benchmark against strong references, and explain the winning route.",
        why_chosen=(
            "Classic credit-risk benchmark that still appears in structured-data evaluations.",
            "Useful for papers because it mixes categorical and numeric inputs in a small but non-trivial setting.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="sklearn_wine",
        family="multiclass_classification",
        display_name="Wine",
        source_name="scikit-learn load_wine",
        source_url="https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_wine.html",
        writer=write_public_wine_dataset,
        target_column="wine_class",
        expected_task_types=("multiclass_classification",),
        expected_rows=178,
        objective_text="Classify wine_class from the chemistry columns. Do everything on your own.",
        benchmark_text="Classify wine_class from the chemistry columns, benchmark against strong references, and explain the selected route.",
        why_chosen=(
            "Canonical multiclass smoke benchmark that keeps the pack grounded and fast.",
            "Useful as a stable paper sanity check before larger multiclass datasets.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_dry_bean",
        family="multiclass_classification",
        display_name="Dry Bean",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/602/dry+bean+dataset",
        writer=partial(write_uci_dry_bean_dataset, max_rows=4000),
        target_column="bean_class",
        expected_task_types=("multiclass_classification",),
        expected_rows=4000,
        objective_text="Classify bean_class from the morphology columns. Do everything on your own.",
        benchmark_text="Classify bean_class from the morphology columns, benchmark against strong references, and explain the selected route.",
        why_chosen=(
            "Modern multiclass tabular benchmark with seven classes and enough scale to expose weak routing choices.",
            "Good paper dataset because it is public, citable, and meaningfully harder than Wine.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_dermatology",
        family="multiclass_classification",
        display_name="Dermatology",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/33/dermatology",
        writer=write_uci_dermatology_dataset,
        target_column="dermatology_class",
        expected_task_types=("multiclass_classification",),
        expected_rows=366,
        objective_text="Classify dermatology_class from the clinical columns. Do everything on your own.",
        benchmark_text="Classify dermatology_class from the clinical columns, benchmark against strong references, and explain the selected route.",
        why_chosen=(
            "Medical multiclass benchmark with heterogeneous features and a compact footprint.",
            "Adds a clinically flavored multiclass task without making the pack too slow.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_credit_default",
        family="rare_event",
        display_name="Default of Credit Card Clients",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients",
        writer=partial(write_uci_credit_default_dataset, max_rows=5000),
        target_column="default_flag",
        expected_task_types=("binary_classification", "fraud_detection", "anomaly_detection"),
        expected_rows=5000,
        objective_text="Predict default_flag from the credit history and billing columns. Do everything on your own.",
        benchmark_text="Predict default_flag from the credit history and billing columns, benchmark against strong references, and explain the risk-sensitive route choice.",
        why_chosen=(
            "Paper-friendly proxy for fraud-like financial risk detection with meaningful class imbalance.",
            "Strong fit for Relaytic because it exercises rare-event handling without relying on login-gated sources.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_iranian_churn",
        family="rare_event",
        display_name="Iranian Churn",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset",
        writer=partial(write_uci_iranian_churn_dataset, max_rows=2500),
        target_column="churn_flag",
        expected_task_types=("binary_classification", "fraud_detection", "anomaly_detection"),
        expected_rows=2500,
        objective_text="Predict churn_flag from the telecom behavior columns. Do everything on your own.",
        benchmark_text="Predict churn_flag from the telecom behavior columns, benchmark against strong references, and explain the retention-risk route choice.",
        why_chosen=(
            "Operational rare-event classification benchmark that is closer to everyday business decisioning than pure fraud datasets.",
            "Useful in papers because it shows Relaytic on mixed business signals with skewed outcomes.",
        ),
    ),
    PaperBenchmarkDatasetSpec(
        dataset_key="uci_ai4i_machine_failure",
        family="rare_event",
        display_name="AI4I 2020 Predictive Maintenance",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset",
        writer=partial(write_uci_ai4i_machine_failure_dataset, max_rows=3000),
        target_column="machine_failure",
        expected_task_types=("binary_classification", "fraud_detection", "anomaly_detection"),
        expected_rows=3000,
        objective_text="Predict machine_failure from the maintenance sensor columns. Do everything on your own.",
        benchmark_text="Predict machine_failure from the maintenance sensor columns, benchmark against strong references, and explain the failure-detection route choice.",
        why_chosen=(
            "Industrial rare-event benchmark with clear operational semantics and low positive prevalence.",
            "Good paper counterweight to the finance-focused default dataset.",
        ),
    ),
)


REPRESENTATIVE_PAPER_BENCHMARK_EVAL_DATASETS: tuple[PaperBenchmarkDatasetSpec, ...] = (
    next(spec for spec in PAPER_BENCHMARK_DATASETS if spec.dataset_key == "uci_energy_efficiency"),
    next(spec for spec in PAPER_BENCHMARK_DATASETS if spec.dataset_key == "uci_bank_marketing"),
    next(spec for spec in PAPER_BENCHMARK_DATASETS if spec.dataset_key == "uci_dry_bean"),
    next(spec for spec in PAPER_BENCHMARK_DATASETS if spec.dataset_key == "uci_credit_default"),
)

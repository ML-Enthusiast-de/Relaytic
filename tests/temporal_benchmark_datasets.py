"""Temporal benchmark dataset catalog for optional Relaytic evaluation packs."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Callable

from tests.domain_datasets import (
    write_uci_appliances_energy_prediction_dataset,
    write_uci_beijing_pm25_dataset,
    write_uci_household_power_consumption_dataset,
    write_uci_occupancy_detection_dataset,
    write_uci_room_occupancy_estimation_dataset,
)

DatasetWriter = Callable[[Path], Path]


@dataclass(frozen=True)
class TemporalBenchmarkDatasetSpec:
    dataset_key: str
    family: str
    display_name: str
    source_name: str
    source_url: str
    writer: DatasetWriter
    target_column: str
    timestamp_column: str
    expected_task_types: tuple[str, ...]
    expected_rows: int
    objective_text: str
    benchmark_text: str
    why_chosen: tuple[str, ...]

    @property
    def pytest_id(self) -> str:
        return f"{self.family}:{self.dataset_key}"


TEMPORAL_BENCHMARK_DATASETS: tuple[TemporalBenchmarkDatasetSpec, ...] = (
    TemporalBenchmarkDatasetSpec(
        dataset_key="uci_appliances_energy_prediction",
        family="temporal_regression",
        display_name="Appliances Energy Prediction",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction",
        writer=partial(write_uci_appliances_energy_prediction_dataset, max_rows=4000),
        target_column="appliances_energy",
        timestamp_column="timestamp",
        expected_task_types=("regression",),
        expected_rows=4000,
        objective_text="Predict appliances_energy from the sensor and weather columns over time. Do everything on your own.",
        benchmark_text="Predict appliances_energy from the sensor and weather columns over time, benchmark against strong references, and explain the time-aware route choice.",
        why_chosen=(
            "Public timestamped sensor dataset with clear temporal structure and a common regression framing.",
            "Good first temporal benchmark because lagged tabular routes should already be competitive before sequence models enter the stack.",
        ),
    ),
    TemporalBenchmarkDatasetSpec(
        dataset_key="uci_beijing_pm25",
        family="temporal_regression",
        display_name="Beijing PM2.5",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/381/beijing+pm2+5+data",
        writer=partial(write_uci_beijing_pm25_dataset, max_rows=6000),
        target_column="pm25",
        timestamp_column="timestamp",
        expected_task_types=("regression",),
        expected_rows=6000,
        objective_text="Predict pm25 from the weather and directional signal columns over time. Do everything on your own.",
        benchmark_text="Predict pm25 from the weather and directional signal columns over time, benchmark against strong references, and explain the time-aware route choice.",
        why_chosen=(
            "Widely used environmental time-series benchmark with real missingness and sensor/weather interactions.",
            "Useful paper dataset because it exposes whether Relaytic can preserve temporal semantics on a noisy public forecasting-style problem.",
        ),
    ),
    TemporalBenchmarkDatasetSpec(
        dataset_key="uci_household_power_consumption",
        family="temporal_regression",
        display_name="Individual Household Electric Power Consumption",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption",
        writer=partial(write_uci_household_power_consumption_dataset, max_rows=6000),
        target_column="household_power_target",
        timestamp_column="timestamp",
        expected_task_types=("regression",),
        expected_rows=6000,
        objective_text="Predict household_power_target from the electrical measurement columns over time. Do everything on your own.",
        benchmark_text="Predict household_power_target from the electrical measurement columns over time, benchmark against strong references, and explain the selected time-aware route.",
        why_chosen=(
            "Classic energy-monitoring dataset that is larger and more realistic than toy temporal regressions.",
            "Good benchmark for papers because it stresses timestamp parsing, missing-value handling, and lag usefulness.",
        ),
    ),
    TemporalBenchmarkDatasetSpec(
        dataset_key="uci_occupancy_detection",
        family="temporal_binary_classification",
        display_name="Occupancy Detection",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/357/occupancy+detection",
        writer=partial(write_uci_occupancy_detection_dataset, max_rows=5000),
        target_column="occupancy_flag",
        timestamp_column="timestamp",
        expected_task_types=("binary_classification",),
        expected_rows=5000,
        objective_text="Classify occupancy_flag from the room sensor columns over time. Do everything on your own.",
        benchmark_text="Classify occupancy_flag from the room sensor columns over time, benchmark against strong references, and explain the temporal classifier route.",
        why_chosen=(
            "Public room-sensor dataset with explicit timestamps and a clean binary decision problem.",
            "Useful for testing where lagged classifiers or future sequence models might outperform static tabular baselines.",
        ),
    ),
    TemporalBenchmarkDatasetSpec(
        dataset_key="uci_room_occupancy_estimation",
        family="temporal_multiclass_classification",
        display_name="Room Occupancy Estimation",
        source_name="UCI Machine Learning Repository",
        source_url="https://archive.ics.uci.edu/dataset/864/room+occupancy+estimation",
        writer=partial(write_uci_room_occupancy_estimation_dataset, max_rows=5000),
        target_column="room_occupancy_count",
        timestamp_column="timestamp",
        expected_task_types=("multiclass_classification",),
        expected_rows=5000,
        objective_text="Classify room_occupancy_count from the room sensor columns over time. Do everything on your own.",
        benchmark_text="Classify room_occupancy_count from the room sensor columns over time, benchmark against strong references, and explain the temporal multiclass route.",
        why_chosen=(
            "Temporal multiclass occupancy dataset that is more demanding than simple binary room-presence detection.",
            "Useful for papers because it creates a bridge between timestamped tabular classification and future sequence-native modeling work.",
        ),
    ),
)


REPRESENTATIVE_TEMPORAL_BENCHMARK_EVAL_DATASETS: tuple[TemporalBenchmarkDatasetSpec, ...] = (
    next(spec for spec in TEMPORAL_BENCHMARK_DATASETS if spec.dataset_key == "uci_appliances_energy_prediction"),
    next(spec for spec in TEMPORAL_BENCHMARK_DATASETS if spec.dataset_key == "uci_occupancy_detection"),
    next(spec for spec in TEMPORAL_BENCHMARK_DATASETS if spec.dataset_key == "uci_room_occupancy_estimation"),
)

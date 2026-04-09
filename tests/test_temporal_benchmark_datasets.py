import os
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("ucimlrepo")

from tests.temporal_benchmark_datasets import TEMPORAL_BENCHMARK_DATASETS


pytestmark = pytest.mark.skipif(
    os.environ.get("RELAYTIC_ENABLE_NETWORK_DATASETS", "").strip() != "1",
    reason="Set RELAYTIC_ENABLE_NETWORK_DATASETS=1 to run temporal network-backed dataset writer tests.",
)


@pytest.mark.parametrize("spec", TEMPORAL_BENCHMARK_DATASETS, ids=lambda spec: spec.pytest_id)
def test_temporal_benchmark_dataset_writers_materialize_expected_contract(
    tmp_path: Path,
    spec,
) -> None:
    data_path = spec.writer(tmp_path / f"{spec.dataset_key}.csv")
    frame = pd.read_csv(data_path)

    assert data_path.exists()
    assert spec.target_column in frame.columns
    assert spec.timestamp_column in frame.columns
    assert len(frame) == spec.expected_rows
    assert frame[spec.timestamp_column].notna().all()

from pathlib import Path

import pandas as pd

from tests.domain_datasets import _sample_frame, write_uci_bank_marketing_dataset


def test_sample_frame_stratified_sampling_hits_requested_row_count() -> None:
    frame = pd.DataFrame(
        {
            "feature": list(range(100)),
            "target": ["majority"] * 83 + ["minority"] * 17,
        }
    )

    sampled = _sample_frame(frame, target_column="target", max_rows=40, stratify=True)

    assert len(sampled) == 40
    assert set(sampled["target"].unique()) == {"majority", "minority"}


def test_write_uci_bank_marketing_dataset_honors_requested_max_rows(tmp_path: Path) -> None:
    path = write_uci_bank_marketing_dataset(tmp_path / "uci_bank_marketing.csv", max_rows=6000)
    frame = pd.read_csv(path)

    assert len(frame) == 6000

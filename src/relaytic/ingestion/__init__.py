"""Ingestion modules."""

from .csv_loader import (
    HeaderInference,
    IngestionError,
    IngestionResult,
    SheetSelectionRequiredError,
    UnsupportedFormatError,
    list_excel_sheets,
    load_tabular_data,
)
from .staging import (
    DATA_COPY_MANIFEST_FILENAME,
    read_data_copy_manifest,
    resolve_staged_data_path,
    stage_dataset_copy,
    stage_materialized_frame,
)
from .sources import (
    MaterializedSource,
    SourceInspection,
    SourceMaterializationError,
    SourceSpec,
    build_source_spec,
    inspect_structured_source,
    materialize_structured_source,
)

__all__ = [
    "HeaderInference",
    "IngestionError",
    "IngestionResult",
    "SheetSelectionRequiredError",
    "UnsupportedFormatError",
    "list_excel_sheets",
    "load_tabular_data",
    "DATA_COPY_MANIFEST_FILENAME",
    "read_data_copy_manifest",
    "resolve_staged_data_path",
    "stage_dataset_copy",
    "stage_materialized_frame",
    "MaterializedSource",
    "SourceInspection",
    "SourceMaterializationError",
    "SourceSpec",
    "build_source_spec",
    "inspect_structured_source",
    "materialize_structured_source",
]

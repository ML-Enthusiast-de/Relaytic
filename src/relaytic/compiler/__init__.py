"""Slice 10A method compiler package."""

from .agents import build_compiler_outputs
from .models import (
    ARCHITECTURE_CANDIDATE_REGISTRY_SCHEMA_VERSION,
    COMPILER_CONTROLS_SCHEMA_VERSION,
    COMPILED_BENCHMARK_PROTOCOL_SCHEMA_VERSION,
    COMPILED_CHALLENGER_TEMPLATES_SCHEMA_VERSION,
    COMPILED_FEATURE_HYPOTHESES_SCHEMA_VERSION,
    METHOD_IMPORT_REPORT_SCHEMA_VERSION,
    ArchitectureCandidateRegistry,
    METHOD_COMPILER_REPORT_SCHEMA_VERSION,
    CompiledBenchmarkProtocol,
    CompiledChallengerTemplates,
    CompiledFeatureHypotheses,
    CompilerControls,
    CompilerTrace,
    MethodImportReport,
    MethodCompilerReport,
    build_compiler_controls_from_policy,
)
from .storage import COMPILER_FILENAMES, read_compiler_bundle, write_compiler_bundle

__all__ = [
    "ARCHITECTURE_CANDIDATE_REGISTRY_SCHEMA_VERSION",
    "COMPILER_CONTROLS_SCHEMA_VERSION",
    "COMPILER_FILENAMES",
    "COMPILED_BENCHMARK_PROTOCOL_SCHEMA_VERSION",
    "COMPILED_CHALLENGER_TEMPLATES_SCHEMA_VERSION",
    "COMPILED_FEATURE_HYPOTHESES_SCHEMA_VERSION",
    "METHOD_IMPORT_REPORT_SCHEMA_VERSION",
    "ArchitectureCandidateRegistry",
    "METHOD_COMPILER_REPORT_SCHEMA_VERSION",
    "CompiledBenchmarkProtocol",
    "CompiledChallengerTemplates",
    "CompiledFeatureHypotheses",
    "CompilerControls",
    "CompilerTrace",
    "MethodImportReport",
    "MethodCompilerReport",
    "build_compiler_controls_from_policy",
    "build_compiler_outputs",
    "read_compiler_bundle",
    "write_compiler_bundle",
]

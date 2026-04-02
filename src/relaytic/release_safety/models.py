"""Typed artifact models for Slice 13A release safety."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


RELEASE_SAFETY_CONTROLS_SCHEMA_VERSION = "relaytic.release_safety_controls.v1"
RELEASE_SAFETY_SCAN_SCHEMA_VERSION = "relaytic.release_safety_scan.v1"
DISTRIBUTION_MANIFEST_SCHEMA_VERSION = "relaytic.distribution_manifest.v1"
ARTIFACT_INVENTORY_SCHEMA_VERSION = "relaytic.artifact_inventory.v1"
ARTIFACT_ATTESTATION_SCHEMA_VERSION = "relaytic.artifact_attestation.v1"
SOURCE_MAP_AUDIT_SCHEMA_VERSION = "relaytic.source_map_audit.v1"
SENSITIVE_STRING_AUDIT_SCHEMA_VERSION = "relaytic.sensitive_string_audit.v1"
RELEASE_BUNDLE_REPORT_SCHEMA_VERSION = "relaytic.release_bundle_report.v1"
PACKAGING_REGRESSION_REPORT_SCHEMA_VERSION = "relaytic.packaging_regression_report.v1"


@dataclass(frozen=True)
class ReleaseSafetyControls:
    schema_version: str = RELEASE_SAFETY_CONTROLS_SCHEMA_VERSION
    oversized_file_threshold_bytes: int = 5_000_000
    preview_finding_limit: int = 20
    scan_hidden_internal_urls: bool = True
    scan_source_mapping_comments: bool = True
    workspace_mode_tracks_attestation_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseSafetyFinding:
    path: str
    rule_id: str
    severity: str
    reason: str
    line_number: int | None = None
    excerpt: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseSafetyTrace:
    agent: str
    scan_mode: str
    target_label: str
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseSafetyScanArtifact:
    schema_version: str
    generated_at: str
    controls: ReleaseSafetyControls
    status: str
    target_path: str | None
    state_dir: str
    scan_mode: str
    ship_readiness: str
    safe_to_ship: bool
    scanned_file_count: int
    finding_count: int
    failed_check_count: int
    findings_by_rule: dict[str, int]
    host_bundle_count: int
    docs_file_count: int
    summary: str
    recommendation: str
    trace: ReleaseSafetyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DistributionManifestArtifact:
    schema_version: str
    generated_at: str
    status: str
    scan_mode: str
    target_path: str | None
    included_roots: list[str]
    workspace_only: bool
    host_bundle_paths: list[str]
    docs_paths: list[str]
    total_file_count: int
    total_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArtifactInventoryArtifact:
    schema_version: str
    generated_at: str
    status: str
    total_file_count: int
    total_bytes: int
    host_bundle_count: int
    docs_file_count: int
    extension_counts: dict[str, int]
    files: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArtifactAttestationArtifact:
    schema_version: str
    generated_at: str
    status: str
    scan_mode: str
    target_path: str | None
    workspace_only: bool
    safe_to_ship: bool
    checks_run: list[dict[str, Any]]
    failed_checks: list[str]
    scanned_file_count: int
    manifest_file_count: int
    attested_paths_preview: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceMapAuditArtifact:
    schema_version: str
    generated_at: str
    status: str
    finding_count: int
    findings: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SensitiveStringAuditArtifact:
    schema_version: str
    generated_at: str
    status: str
    finding_count: int
    findings: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PackagingRegressionReportArtifact:
    schema_version: str
    generated_at: str
    status: str
    finding_count: int
    oversized_payload_count: int
    disallowed_internal_count: int
    findings: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseBundleReportArtifact:
    schema_version: str
    generated_at: str
    status: str
    ship_readiness: str
    safe_to_ship: bool
    findings_preview: list[dict[str, Any]]
    required_actions: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseSafetyBundle:
    release_safety_scan: ReleaseSafetyScanArtifact
    distribution_manifest: DistributionManifestArtifact
    artifact_inventory: ArtifactInventoryArtifact
    artifact_attestation: ArtifactAttestationArtifact
    source_map_audit: SourceMapAuditArtifact
    sensitive_string_audit: SensitiveStringAuditArtifact
    release_bundle_report: ReleaseBundleReportArtifact
    packaging_regression_report: PackagingRegressionReportArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "release_safety_scan": self.release_safety_scan.to_dict(),
            "distribution_manifest": self.distribution_manifest.to_dict(),
            "artifact_inventory": self.artifact_inventory.to_dict(),
            "artifact_attestation": self.artifact_attestation.to_dict(),
            "source_map_audit": self.source_map_audit.to_dict(),
            "sensitive_string_audit": self.sensitive_string_audit.to_dict(),
            "release_bundle_report": self.release_bundle_report.to_dict(),
            "packaging_regression_report": self.packaging_regression_report.to_dict(),
        }

import json
from pathlib import Path

from relaytic.artifacts import artifact_entry, build_manifest, write_manifest


def test_artifact_entry_tracks_relative_paths_and_size(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_alpha"
    run_dir.mkdir()
    report = run_dir / "reports" / "summary.md"
    report.parent.mkdir()
    report.write_text("hello", encoding="utf-8")

    entry = artifact_entry(report, run_dir=run_dir, kind="report", required=True)

    assert entry.path == str(Path("reports") / "summary.md")
    assert entry.kind == "report"
    assert entry.required is True
    assert entry.exists is True
    assert entry.size_bytes == 5


def test_build_manifest_adds_manifest_entry(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_beta"
    run_dir.mkdir()

    manifest = build_manifest(run_dir=run_dir, run_id="beta")
    payload = manifest.to_dict()

    assert payload["product"] == "Relaytic"
    assert payload["run_id"] == "beta"
    assert any(item["path"] == "manifest.json" for item in payload["entries"])


def test_write_manifest_writes_expected_json(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_gamma"
    policy = run_dir / "policy_resolved.yaml"
    run_dir.mkdir()
    policy.write_text("policy:\n  mode: local\n", encoding="utf-8")

    path = write_manifest(
        run_dir=run_dir,
        run_id="gamma",
        policy_source=policy,
        labels={"stage": "slice01"},
        entries=[artifact_entry("policy_resolved.yaml", run_dir=run_dir, required=True)],
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "gamma"
    assert payload["policy_source"].endswith("policy_resolved.yaml")
    assert payload["labels"] == {"stage": "slice01"}
    assert any(item["path"] == "policy_resolved.yaml" for item in payload["entries"])
    assert any(item["path"] == "manifest.json" and item["exists"] is True for item in payload["entries"])

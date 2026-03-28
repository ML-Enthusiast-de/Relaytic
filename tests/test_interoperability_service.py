from pathlib import Path

from relaytic.interoperability import service


def test_relaytic_run_normalizes_human_actor_alias(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, str] = {}

    class _FakeCLI:
        def _run_access_flow(self, **kwargs):
            captured["actor_type"] = str(kwargs["actor_type"])
            captured["run_dir"] = str(kwargs["run_dir"])
            return {"surface_payload": {"status": "ok", "run_dir": str(kwargs["run_dir"])}, "human_output": "ok"}

    monkeypatch.setattr(service, "_cli", lambda: _FakeCLI())

    result = service.relaytic_run(
        data_path=str(tmp_path / "dataset.csv"),
        run_dir=str(tmp_path / "interop_run"),
        text="Build a fraud model.",
        actor_type="human",
    )

    assert captured["actor_type"] == "operator"
    assert captured["run_dir"] == str(tmp_path / "interop_run")
    assert result["surface_payload"]["status"] == "ok"

from pathlib import Path

from relaytic.core.config import load_config


def test_load_config_supports_explicit_path(tmp_path: Path) -> None:
    cfg = tmp_path / "relaytic.yaml"
    cfg.write_text("project:\n  name: test\n", encoding="utf-8")
    loaded = load_config(cfg)
    assert loaded["project"]["name"] == "test"


def test_load_config_uses_relaytic_env_path(monkeypatch, tmp_path: Path) -> None:
    cfg = tmp_path / "relaytic.yaml"
    cfg.write_text("project:\n  name: relaytic-env\n", encoding="utf-8")
    monkeypatch.setenv("RELAYTIC_CONFIG_PATH", str(cfg))
    loaded = load_config()
    assert loaded["project"]["name"] == "relaytic-env"


def test_load_config_explicit_path_beats_env(monkeypatch, tmp_path: Path) -> None:
    env_cfg = tmp_path / "env.yaml"
    env_cfg.write_text("project:\n  name: env\n", encoding="utf-8")
    explicit_cfg = tmp_path / "explicit.yaml"
    explicit_cfg.write_text("project:\n  name: explicit\n", encoding="utf-8")
    monkeypatch.setenv("RELAYTIC_CONFIG_PATH", str(env_cfg))
    loaded = load_config(explicit_cfg)
    assert loaded["project"]["name"] == "explicit"


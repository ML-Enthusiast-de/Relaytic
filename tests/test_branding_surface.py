import importlib
import importlib.util
from pathlib import Path


def _load_local_cli_shim():
    project_root = Path(__file__).resolve().parents[1]
    shim_path = project_root / "src" / "corr2surrogate" / "ui" / "cli.py"
    spec = importlib.util.spec_from_file_location("local_corr2surrogate_ui_cli", shim_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_relaytic_cli_parser_uses_public_name() -> None:
    cli = importlib.import_module("relaytic.ui.cli")
    parser = cli.build_parser()
    assert parser.prog == "relaytic"


def test_legacy_package_import_shim_resolves_new_cli() -> None:
    cli = _load_local_cli_shim()
    parser = cli.build_parser()
    assert parser.prog == "relaytic"

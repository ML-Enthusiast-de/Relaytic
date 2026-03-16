import importlib


def test_relaytic_cli_parser_uses_public_name() -> None:
    cli = importlib.import_module("relaytic.ui.cli")
    parser = cli.build_parser()
    assert parser.prog == "relaytic"


def test_legacy_package_import_shim_resolves_new_cli() -> None:
    cli = importlib.import_module("corr2surrogate.ui.cli")
    parser = cli.build_parser()
    assert parser.prog == "relaytic"

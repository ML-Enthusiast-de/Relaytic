"""Compatibility CLI shim forwarding to Relaytic."""

from relaytic.ui.cli import *  # noqa: F401,F403


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

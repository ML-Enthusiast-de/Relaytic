"""Compatibility git-guard shim forwarding to Relaytic."""

from relaytic.security.git_guard import *  # noqa: F401,F403


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

"""Compatibility shim for legacy imports.

New code should import from ``relaytic``.
"""

from __future__ import annotations

import importlib

_relaytic = importlib.import_module("relaytic")

__all__ = getattr(_relaytic, "__all__", [])
__doc__ = _relaytic.__doc__
__path__ = _relaytic.__path__

for _name in dir(_relaytic):
    if _name.startswith("__") and _name not in {"__version__"}:
        continue
    globals()[_name] = getattr(_relaytic, _name)
